import importlib.util
import json
from pathlib import Path
import sys
import threading
import tempfile
import unittest
from copy import deepcopy
from http.server import BaseHTTPRequestHandler, HTTPServer
from unittest.mock import patch

import torch
from transformers import BatchEncoding, GenerationConfig

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('dart_plugin', ROOT / '__init__.py', submodule_search_locations=[str(ROOT)])
plugin = importlib.util.module_from_spec(spec)
sys.modules['dart_plugin'] = plugin
spec.loader.exec_module(plugin)

from dart_plugin.py.dart.model import DartModel
from dart_plugin.py.dart.tags import encode_tags, remove_tags, keep_tags, split_tags
from dart_plugin.py.dart.assistant import request_scene, format_scene, parse_scene, scene_request
from dart_plugin.py.dart.local_assistant import select_model
from dart_plugin.py.dart.moss import compile_layout, read_layout
from dart_plugin.py.dart.tokenizer.tokenizer_v2 import DartTokenizerV2
from dart_plugin.py.dart.defs.token_v2 import SPECIAL_TAGS_V2
from dart_plugin.py.dart.tokenizer.load import load_tag_tokenizer


class Tokenizer:
    all_special_ids = [0, 1, 2]
    sequences = {'': [], 'red hair': [10, 11], 'hair': [11], '<|eos|>': [1], 'unknown': [2]}

    def __call__(self, text, **kwargs):
        ids = self.sequences.get(text, [12])
        if kwargs.get('return_tensors'):
            return BatchEncoding({'input_ids': torch.tensor([ids]), 'attention_mask': torch.ones(1, len(ids), dtype=torch.long)})
        return {'input_ids': ids}


class TagTests(unittest.TestCase):
    def test_loads_actual_wordlevel_ids_without_remote_subclass(self):
        from tokenizers import Tokenizer as Backend, models, pre_tokenizers
        vocabulary = {'<|bos|>': 0, '<|eos|>': 1, '<|unk|>': 2, '<|pad|>': 3,
                      '1girl': 4, 'solo': 5, 'red hair': 6}
        backend = Backend(models.WordLevel(vocabulary, unk_token='<|unk|>'))
        backend.pre_tokenizer = pre_tokenizers.Split(pattern=__import__('tokenizers').Regex(r',\s*'), behavior='removed')
        with tempfile.TemporaryDirectory() as directory:
            backend.save(str(Path(directory) / 'tokenizer.json'))
            tokenizer = load_tag_tokenizer(directory, ['<|bos|>', '<|eos|>'])
            self.assertEqual(tokenizer('1girl, solo, red hair', add_special_tokens=False)['input_ids'], [4, 5, 6])
            self.assertEqual(encode_tags(tokenizer, 'red hair, <|eos|>, unknown'), [[6]])

    def test_multi_token_ban_is_one_sequence(self):
        self.assertEqual(encode_tags(Tokenizer(), 'red hair, <|eos|>, unknown'), [[10, 11]])

    def test_removal_does_not_delete_shared_token_elsewhere(self):
        self.assertEqual(remove_tags(Tokenizer(), [0, 10, 11, 12, 11, 1], 'red hair'), [0, 12, 11, 1])

    def test_control_tokens_survive_removal(self):
        self.assertEqual(remove_tags(Tokenizer(), [0, 12, 1], '<|eos|>'), [0, 12, 1])

    def test_weight_groups_remain_whole(self):
        self.assertEqual(split_tags('(blue eyes, red hair:1.2), solo'), ['(blue eyes, red hair:1.2)', 'solo'])
        self.assertEqual(keep_tags('solo', '(blue eyes, red hair:1.2), <lora:style:0.8>'),
                         'solo, (blue eyes, red hair:1.2), <lora:style:0.8>')

    def test_keep_deduplicates(self):
        self.assertEqual(keep_tags('solo', 'Solo, red hair, red hair'), 'solo, red hair')


class GeometryTests(unittest.TestCase):
    def test_gallery_connections_and_cycles(self):
        for path in (ROOT / 'workflows' / 'next').glob('*.json'):
            with self.subTest(workflow=path.name):
                workflow = json.loads(path.read_text(encoding='utf-8'))
                nodes = {node['id']: node for node in workflow['nodes']}
                self.assertEqual(len(nodes), len(workflow['nodes']))
                links = {link[0]: link for link in workflow['links']}
                self.assertEqual(len(links), len(workflow['links']))
                for link_id, source, output, target, input_index, _ in links.values():
                    self.assertIn(link_id, nodes[source]['outputs'][output]['links'])
                    self.assertEqual(nodes[target]['inputs'][input_index]['link'], link_id)
                visited, active = set(), set()

                def visit(node_id):
                    self.assertNotIn(node_id, active, 'Workflow contains a cycle')
                    if node_id in visited:
                        return
                    active.add(node_id)
                    for slot in nodes[node_id].get('inputs', []):
                        if slot.get('link') is not None:
                            visit(links[slot['link']][1])
                    active.remove(node_id)
                    visited.add(node_id)

                for node_id in nodes:
                    visit(node_id)

    def test_aspect_boundaries(self):
        node = plugin.NODE_CLASS_MAPPINGS['DanbooruTagsTransformerGetAspectRatio']()
        for width, height, expected in [(1024, 1024, 'square'), (9, 8, 'square'), (8, 9, 'square'), (2, 1, 'ultra_wide'), (1, 2, 'ultra_tall'), (3, 2, 'wide'), (2, 3, 'tall')]:
            with self.subTest(size=(width, height)):
                self.assertEqual(node.get_aspect_ratio(width, height), (expected,))

    def test_v3_template_order_and_no_v2_identity(self):
        node = plugin.NODE_CLASS_MAPPINGS['DanbooruTagsTransformerComposePromptV3']()
        prompt = node.compose('general', 'too_wide', 'medium', 'original', '', 'solo')[0]
        self.assertTrue(prompt.startswith('<|bos|><|rating:general|><|aspect_ratio:too_wide|><|length:medium|><copyright>'))
        self.assertNotIn('identity', prompt)
        self.assertTrue(prompt.endswith('<general>solo<|input_end|>'))

    def test_old_workflow_node_names_and_required_inputs(self):
        for path in (ROOT / 'workflows').glob('*.json'):
            workflow = json.loads(path.read_text(encoding='utf-8'))
            for node in workflow.get('nodes', []):
                name = node['type']
                if name.startswith('DanbooruTagsTransformer'):
                    self.assertIn(name, plugin.NODE_CLASS_MAPPINGS, path.name)
        loader = plugin.NODE_CLASS_MAPPINGS['DanbooruTagsTransformerLoader']
        self.assertEqual(list(loader.INPUT_TYPES()['required']), ['model'])


class ModelTests(unittest.TestCase):
    def setUp(self):
        class Model:
            def __init__(self):
                self.generation_config = GenerationConfig(temperature=1.0, num_beams=1)
                self.calls = []

            def generate(self, **kwargs):
                self.calls.append(deepcopy(kwargs))
                return torch.randint(3, 30, (1, 8))

        self.wrapper = DartModel.__new__(DartModel)
        self.wrapper.model = Model()
        self.wrapper.device = torch.device('cpu')
        self.tokenizer = type('Wrapped', (), {'tokenizer': Tokenizer()})()

    def test_config_does_not_leak_between_runs(self):
        self.wrapper.generate(self.tokenizer, 'red hair', 4, {'temperature': 0.3, 'num_beams': 2})
        self.wrapper.generate(self.tokenizer, 'red hair', 4)
        calls = self.wrapper.model.calls
        self.assertEqual(calls[0]['generation_config'].temperature, 0.3)
        self.assertEqual(calls[1]['generation_config'].temperature, 1.0)
        self.assertEqual(calls[1]['generation_config'].num_beams, 1)
        self.assertEqual(self.wrapper.model.generation_config.max_new_tokens, None)

    def test_zero_temperature_and_repeatable_seed_restore_rng(self):
        before = torch.random.get_rng_state().clone()
        first = self.wrapper.generate(self.tokenizer, 'red hair', 7, {'temperature': 0})
        self.assertTrue(torch.equal(before, torch.random.get_rng_state()))
        second = self.wrapper.generate(self.tokenizer, 'red hair', 7, {'temperature': 0})
        self.assertTrue(torch.equal(first, second))
        self.assertFalse(self.wrapper.model.calls[0]['generation_config'].do_sample)

    def test_invalid_token_range_is_actionable(self):
        with self.assertRaisesRegex(ValueError, 'Minimum'):
            self.wrapper.generate(self.tokenizer, 'red hair', 0, {'min_new_tokens': 20, 'max_new_tokens': 10})

    def test_bans_are_passed_as_sequences(self):
        self.wrapper.generate(self.tokenizer, 'red hair', 0, ban_tags='red hair')
        self.assertEqual(self.wrapper.model.calls[0]['generation_config'].bad_words_ids, [[10, 11]])


class DecodeTests(unittest.TestCase):
    def test_truncated_v2_general_section_survives(self):
        class Vocabulary:
            vocab = {token: index for index, token in enumerate(SPECIAL_TAGS_V2 + ['original', 'solo'])}

            def convert_tokens_to_ids(self, tokens):
                if isinstance(tokens, str):
                    return self.vocab.get(tokens, -1)
                return [self.vocab.get(token, -1) for token in tokens]

            def decode(self, ids, **kwargs):
                return next(key for key, value in self.vocab.items() if value == int(ids[0]))

        wrapped = DartTokenizerV2.__new__(DartTokenizerV2)
        wrapped.tokenizer = Vocabulary()
        wrapped.special_tags = SPECIAL_TAGS_V2
        wrapped.token_id_table = {}
        sequence = wrapped.tokenizer.convert_tokens_to_ids(['<copyright>', 'original', '</copyright>', '<character>', '</character>', '<general>', 'solo'])
        self.assertIn('solo', wrapped.decode_by_animagine(sequence))
        self.assertEqual(len(wrapped.split_parts(sequence[:1])), 5)


SCENE = {'tags': ['1girl', 'red hair', 'extra people', 'red hair'],
         'description': 'A red-haired woman waits by a rainy cafe window.',
         'copyright': 'original', 'character': '', 'added_details': []}


class MossTests(unittest.TestCase):
    def setUp(self):
        self.draft = {'summary': {'meta': ['poster'], 'canvas': 'single', 'caption': 'A mountain poster.'},
                      'items': [{'label': 'text', 'caption': 'A title', 'text': 'EXPLORE\n探索',
                                 'bbox': [128, 96, 896, 224]}]}

    def test_official_example_coordinates_and_unicode_roundtrip(self):
        layout = compile_layout(self.draft, 1024, 1024, draft=True)
        self.assertEqual(layout['items'][0]['bbox'], [-416, -384, -288, 384])
        self.assertEqual(read_layout(json.dumps(layout, ensure_ascii=False), 1024, 1024), layout)
        self.assertEqual(layout['items'][0]['text'], 'EXPLORE\n探索')

    def test_rectangular_canvas_uses_correct_axis_and_center(self):
        self.draft['items'][0]['bbox'] = [0, 0, 1536, 1024]
        layout = compile_layout(self.draft, 1536, 1024, draft=True)
        self.assertEqual(layout['items'][0]['bbox'], [-512, -768, 512, 768])

    def test_invalid_boxes_and_canvas_fail_actionably(self):
        for box in ([0, 0, 2000, 20], [30, 0, 10, 20], [0, 0, float('nan'), 20], [0, 0, True, 20]):
            with self.subTest(box=box), self.assertRaisesRegex(ValueError, 'bbox'):
                self.draft['items'][0]['bbox'] = box
                compile_layout(self.draft, 1024, 1024, draft=True)
        with self.assertRaisesRegex(ValueError, 'multiples of 16'):
            compile_layout(self.draft, 1025, 1024, draft=True)

    def test_override_bypasses_inference_and_keeps_valid_json(self):
        layout = compile_layout(self.draft, 1024, 1024, draft=True)
        node = plugin.NODE_CLASS_MAPPINGS['DanbooruTagsTransformerDescribeImage']()
        with patch('dart_plugin.py.nodes.assistant.describe_local') as local:
            result = node.describe('', 'MOSS JSON layout', 'Concept', '', '', 0,
                                   layout_json=json.dumps(layout), keep_tags='must not corrupt JSON')
        local.assert_not_called()
        self.assertEqual(json.loads(result['result'][0]), layout)
        self.assertIn('\n  "summary":', result['result'][0])
        self.assertFalse(result['result'][0].startswith('```'))
        self.assertEqual(result['ui']['moss_json'], [True])
        self.assertEqual(len(result['result']), 8)

    def test_generated_layout_is_compiled_and_custom_instructions_reach_request(self):
        system, _ = scene_request('A poster', 'Concept', '', '', target='MOSS JSON layout',
                                  canvas_width=1536, canvas_height=1024)
        self.assertIn('1536x1024', system)
        self.assertIn('TOP-LEFT pixel xyxy', system)
        node = plugin.NODE_CLASS_MAPPINGS['DanbooruTagsTransformerDescribeImage']()
        with patch('dart_plugin.py.nodes.assistant.describe_local', return_value={**SCENE, 'layout_draft': self.draft}):
            result = node.describe('A poster', 'MOSS JSON layout', 'Concept', '', '', 0)
        self.assertEqual(json.loads(result['result'][0])['bbox_format'], 'yxyx')
        self.assertIn('moss_layout', json.loads(result['result'][5]))

    def test_invalid_generated_layout_gets_one_bounded_repair(self):
        node = plugin.NODE_CLASS_MAPPINGS['DanbooruTagsTransformerDescribeImage']()
        with patch('dart_plugin.py.nodes.assistant.describe_local', side_effect=[
            SCENE, {**SCENE, 'layout_draft': self.draft}
        ]) as local:
            result = node.describe('A poster', 'MOSS JSON layout', 'Preserve', '', '', 0,
                                   custom_instructions='Keep the title above the mountain.')
        self.assertEqual(local.call_count, 2)
        self.assertIn('Keep the title above the mountain.', local.call_args.kwargs['custom_instructions'])
        self.assertTrue(json.loads(result['result'][5])['layout_repaired'])
        with patch('dart_plugin.py.nodes.assistant.describe_local', return_value=SCENE) as local:
            with self.assertRaises(ValueError):
                node.describe('A poster', 'MOSS JSON layout', 'Preserve', '', '', 0)
        self.assertEqual(local.call_count, 2)


class AssistantTests(unittest.TestCase):
    def test_short_detailed_response_gets_one_revision_but_preserve_does_not(self):
        node = plugin.NODE_CLASS_MAPPINGS['DanbooruTagsTransformerDescribeImage']()
        longer = {**SCENE, 'description': ' '.join(['visual detail'] * 100)}
        with patch('dart_plugin.py.nodes.assistant.describe_local', side_effect=[SCENE, longer]) as query:
            output = node.describe('cafe', 'MOSS prose', 'Expand', '', '', 0, prompt_length='Detailed')
        self.assertEqual(query.call_count, 2)
        self.assertEqual(output['result'][0], longer['description'])
        with patch('dart_plugin.py.nodes.assistant.describe_local', return_value=SCENE) as query:
            node.describe('cafe', 'MOSS prose', 'Preserve', '', '', 0, prompt_length='Extensive')
        self.assertEqual(query.call_count, 1)

    def test_length_language_and_budget_reach_both_backends(self):
        node = plugin.NODE_CLASS_MAPPINGS['DanbooruTagsTransformerDescribeImage']()
        for backend, name in [('Local model', 'describe_local'), ('Chat server', 'request_scene')]:
            with self.subTest(backend=backend), patch('dart_plugin.py.nodes.assistant.' + name, return_value=SCENE) as query:
                node.describe('cafe', 'MOSS prose', 'Expand', 'http://localhost/v1', 'qwen', 0,
                              backend=backend, prompt_length='Extensive', max_tokens=8192,
                              language_style='Direct / explicit')
                self.assertEqual(query.call_args.kwargs['max_tokens'], 8192)
                self.assertEqual(query.call_args.kwargs['prompt_length'], 'Extensive')
                self.assertEqual(query.call_args.kwargs['language_style'], 'Direct / explicit')

    def test_length_guidance_preserves_fidelity_and_language_is_opt_in(self):
        default, _ = scene_request('cafe', 'Preserve', '', '')
        detailed, payload = scene_request('cafe', 'Preserve', '', '', prompt_length='Extensive',
                                         language_style='Direct / explicit', max_tokens=8192)
        self.assertIn('400–650', detailed)
        self.assertIn('fidelity', detailed)
        self.assertIn('avoid euphemisms', detailed)
        self.assertNotIn('avoid euphemisms', default)
        self.assertEqual(payload['prompt_length'], 'Extensive')
        with self.assertRaisesRegex(ValueError, 'token limit'):
            scene_request('cafe', 'Preserve', '', '', max_tokens=1)

    def test_local_generation_uses_selected_budget(self):
        from types import SimpleNamespace
        from unittest.mock import Mock
        from dart_plugin.py.dart.local_assistant import describe_local
        execute = Mock(return_value=SimpleNamespace(args=(json.dumps(SCENE),)))
        module = SimpleNamespace(TextGenerate=SimpleNamespace(execute=execute))
        with patch.dict(sys.modules, {'comfy_extras.nodes_textgen': module}):
            describe_local('cafe', 'Concept', '', '', 0, clip='model', max_tokens=8192,
                           prompt_length='Detailed', language_style='Direct / explicit')
        self.assertEqual(execute.call_args.kwargs['max_length'], 8192)
        self.assertIn('200–350', execute.call_args.kwargs['system_prompt'])

    def test_keywords_only_concept_and_custom_instructions_reach_local_model(self):
        node = plugin.NODE_CLASS_MAPPINGS['DanbooruTagsTransformerDescribeImage']()
        instructions = 'Create a photograph. Do not use realistic or photorealistic. Only output the prompt.'
        with patch('dart_plugin.py.nodes.assistant.describe_local', return_value=SCENE) as local:
            result = node.describe('', 'Natural language', 'Concept', '', '', 42,
                                   source_tags='red coat, rain, cafe', custom_instructions=instructions)
        self.assertEqual(local.call_args.kwargs['source_tags'], 'red coat, rain, cafe')
        self.assertEqual(local.call_args.kwargs['custom_instructions'], instructions)
        self.assertEqual(local.call_args.kwargs['target'], 'Natural language')
        self.assertEqual(result['result'][0], SCENE['description'])

    def test_custom_only_output_instruction_keeps_internal_json_contract(self):
        system, payload = scene_request('', 'Concept', '', '', 'cafe, red coat',
                                        'Only output a photographic prompt.', 'Natural language')
        self.assertIn('JSON schema', system)
        self.assertIn('Concept mode', system)
        self.assertEqual(payload['description'], '')
        self.assertEqual(payload['source_tags'], 'cafe, red coat')
        self.assertEqual(payload['output_target'], 'Natural language')
        with self.assertRaisesRegex(ValueError, 'description or connect source tags'):
            scene_request(' ', 'Concept', '', '', '', 'Only output a prompt.')

    def test_common_tag_aliases_and_subject_counts(self):
        scene = {**SCENE, 'tags': ['woman', 'rainy', 'looking out the window']}
        prompt, general = format_scene(scene, 'DART tags')
        self.assertEqual(general, '1girl, rain, looking out window')
        self.assertNotIn('rain', format_scene(scene, 'DART tags', avoid='rainy')[1].split(', '))
        scene['tags'] = ['2girls', 'woman', 'man']
        self.assertEqual(format_scene(scene, 'DART tags')[1], '2girls, 1boy')

    def test_default_node_runs_local_and_returns_visible_preview(self):
        node = plugin.NODE_CLASS_MAPPINGS['DanbooruTagsTransformerDescribeImage']()
        with patch('dart_plugin.py.nodes.assistant.describe_local', return_value=SCENE) as local, \
                patch('dart_plugin.py.nodes.assistant.request_scene') as remote:
            result = node.describe('rainy cafe', 'Anima hybrid', 'Preserve', 'http://localhost:1234/v1', '', 7)
        local.assert_called_once()
        remote.assert_not_called()
        self.assertTrue(node.OUTPUT_NODE)
        self.assertEqual(result['ui']['text'][0], result['result'][0])

    def test_existing_explicit_server_workflows_still_use_server(self):
        node = plugin.NODE_CLASS_MAPPINGS['DanbooruTagsTransformerDescribeImage']()
        with patch('dart_plugin.py.nodes.assistant.request_scene', return_value=SCENE) as remote:
            result = node.describe('rainy cafe', 'DART tags', 'Preserve', 'http://localhost:1234/v1', 'existing-model', 7)
        remote.assert_called_once()
        self.assertEqual(len(result['result']), 8)

    def test_automatic_model_prefers_small_general_model(self):
        names = ['qwen3.5_9b_flux3_prompt_upsampler_int8.safetensors', 'qwen3-vl-4b-heretic_int8.safetensors',
                 'qwen3vl_8b_int8_convrot.safetensors', 'qwen3vl_4b_int8_convrot.safetensors']
        self.assertEqual(select_model(names), 'qwen3vl_4b_int8_convrot.safetensors')
        with self.assertRaisesRegex(ValueError, 'No local assistant model'):
            select_model([])

    def test_reasoning_fence_and_empty_copyright_are_normalized(self):
        scene = parse_scene('<think>reasoning</think>\n```json\n' + json.dumps({**SCENE, 'copyright': ''}) + '\n```')
        self.assertEqual(scene['copyright'], 'original')

    def test_targets_preserve_literal_weights_and_exclude_exact_tags(self):
        for target in ('DART tags', 'Anima hybrid', 'MOSS prose'):
            prompt, general = format_scene(SCENE, target, '(red coat:1.3)', 'extra people')
            self.assertIn('(red coat:1.3)', prompt)
            self.assertNotIn('extra people', general)
        self.assertIn(SCENE['description'], format_scene(SCENE, 'MOSS prose')[0])

    def test_bad_schema_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'list of strings'):
            format_scene({**SCENE, 'tags': '1girl'}, 'DART tags')

    def test_request_to_real_loopback_http_server(self):
        received = []

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                received.append((self.path, json.loads(self.rfile.read(int(self.headers['Content-Length'])))))
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'choices': [{'message': {'content': '```json\n' + json.dumps(SCENE) + '\n```'}}]}).encode())

            def log_message(self, *args):
                pass

        server = HTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            endpoint = f'http://127.0.0.1:{server.server_port}/v1'
            result = request_scene('rainy cafe', endpoint, 'test-model', 'Concept', '', '', 5,
                                   source_tags='red coat, rain', custom_instructions='Write a film photograph.',
                                   target='Natural language')
            self.assertEqual(result['source_description'], 'rainy cafe')
            self.assertEqual(received[0][0], '/v1/chat/completions')
            self.assertEqual(received[0][1]['model'], 'test-model')
            self.assertIn('rainy cafe', received[0][1]['messages'][1]['content'])
            payload = json.loads(received[0][1]['messages'][1]['content'])
            self.assertEqual(payload['source_tags'], 'red coat, rain')
            self.assertEqual(payload['custom_instructions'], 'Write a film photograph.')
            self.assertEqual(payload['output_target'], 'Natural language')
        finally:
            server.shutdown()
            server.server_close()
            thread.join()

    def test_missing_key_and_missing_model_fail_before_network(self):
        with self.assertRaisesRegex(ValueError, 'environment variable'):
            request_scene('scene', 'http://localhost:1234/v1', 'm', 'Preserve', '', '', 0, api_key_env='DART_TEST_MISSING_KEY')
        with self.assertRaisesRegex(ValueError, 'model identifier'):
            request_scene('scene', 'http://localhost:1234/v1', '', 'Preserve', '', '', 0)


class AppearanceTests(unittest.TestCase):
    def recipe(self, **kwargs):
        return plugin.NODE_CLASS_MAPPINGS['DanbooruTagsTransformerAppearanceOverrides']().build(**kwargs)['result'][0]

    def test_defaults_disabled_and_custom_traits(self):
        from dart_plugin.py.dart.appearance import override_instructions
        self.assertEqual(override_instructions(self.recipe()), ('', ''))
        self.assertEqual(override_instructions(self.recipe(enabled=False, hair_color='Silver', trigger='token')), ('', ''))
        value = self.recipe(subject='Custom subject', subject_custom='person on the left', hair_color='Custom', hair_color_custom='silver with blue tips', breast_size='Large breasts')
        self.assertEqual(value['traits']['hair_color'], 'silver with blue tips')
        self.assertEqual(value['subject'], 'person on the left')
        self.assertNotIn('eye_color', value['traits'])
        with self.assertRaisesRegex(ValueError, 'custom hair color'):
            self.recipe(hair_color='Custom')
        with self.assertRaisesRegex(ValueError, 'trigger'):
            self.recipe(identity_mode='Trigger replaces identity details')

    def test_recipe_reaches_both_assistants_and_preserves_user_instructions(self):
        recipe = self.recipe(hair_color='Silver', eye_color='Green', trigger='vzx_character')
        vision = plugin.NODE_CLASS_MAPPINGS['DanbooruTagsTransformerImageToText']()
        with patch('dart_plugin.py.nodes.vision.caption_image', return_value='caption') as caption:
            vision.describe(torch.zeros(1,16,16,3), instructions='Keep the background.', appearance=recipe, unload_after_generation=True)
        self.assertIn('Keep the background.', caption.call_args.args[1])
        self.assertIn('Silver', caption.call_args.args[1])
        self.assertEqual(caption.call_args.args[2], 'vzx_character')
        self.assertTrue(caption.call_args.kwargs['unload_after_generation'])
        assistant = plugin.NODE_CLASS_MAPPINGS['DanbooruTagsTransformerDescribeImage']()
        for backend, path in [('Local model','describe_local'),('Chat server','request_scene')]:
            with patch('dart_plugin.py.nodes.assistant.' + path, return_value={**SCENE, 'description':'A traveler with silver hair and green eyes.'}) as query:
                result = assistant.describe('cafe', 'Natural language', 'Preserve', 'http://localhost/v1', 'qwen', 0, backend=backend, appearance=recipe, custom_instructions='Use cinematic light.')
            self.assertIn('Use cinematic light.', query.call_args.kwargs['custom_instructions'])
            self.assertIn('Silver', query.call_args.kwargs['custom_instructions'])
            self.assertIn('vzx_character', result['result'][0])
        with self.assertRaisesRegex(ValueError, 'Clear the manual'):
            assistant.describe('cafe','MOSS JSON layout','Preserve','','',0,layout_json='{}',appearance=recipe)


    def test_reported_gigantic_to_large_bust_regression_and_subject_caption(self):
        from dart_plugin.py.dart.appearance import check_layout_appearance, check_appearance_wording
        settings=self.recipe(trigger='test_character',hair_color='Brown',eye_color='Brown',breast_size='Gigantic breasts',skin_tone='Tan')
        weak='test_character, a woman with brown hair, brown eyes, tan skin and a large bust.'
        exact='test_character, a woman with brown hair, brown eyes, tan skin and gigantic breasts.'
        with self.assertRaisesRegex(ValueError,'Gigantic breasts'):
            check_appearance_wording(weak,settings)
        check_appearance_wording(exact,settings)
        check_appearance_wording('A brown-haired, brown-eyed, tan-skinned adult woman with gigantic breasts.',settings)
        check_appearance_wording('Long curly brown hair and green eyes.',self.recipe(hair_color='Brown',hair_length='Long',eye_color='Green'))
        self.assertNotIn('Gigantic breasts',plugin.NODE_CLASS_MAPPINGS['DanbooruTagsTransformerAppearanceOverrides']().build(hair_color='Brown')['result'][1])
        layout={'summary':{'caption':exact},'items':[{'label':'object','caption':weak},
                {'label':'object','caption':'A golf club held by the subject.'}]}
        with self.assertRaisesRegex(ValueError,'subject caption'):
            check_layout_appearance(layout,settings)
        layout['items'][0]['caption']=exact
        check_layout_appearance(layout,settings)
        self.assertEqual(layout['items'][1]['caption'],'A golf club held by the subject.')
        for bad in ('A woman with gigantic breasts and a large bust.','A woman without gigantic breasts.'):
            with self.assertRaises(ValueError):check_appearance_wording(bad,self.recipe(breast_size='Gigantic breasts'))
        check_appearance_wording(weak,self.recipe(breast_size='Gigantic breasts',strict_wording=False))

    def test_text_assistant_corrects_weakened_trait_once_then_rejects_if_still_wrong(self):
        node=plugin.NODE_CLASS_MAPPINGS['DanbooruTagsTransformerDescribeImage']()
        settings=self.recipe(breast_size='Gigantic breasts',apply_size_wording=False)
        weak={**SCENE,'description':'An adult woman with a large bust.'}
        exact={**SCENE,'description':'An adult woman with gigantic breasts.'}
        with patch('dart_plugin.py.nodes.assistant.describe_local',side_effect=[weak,exact]) as model:
            output=node.describe('adult woman','Natural language','Preserve','','',0,appearance=settings)
        self.assertIn('gigantic breasts',output['result'][0])
        self.assertEqual(model.call_count,2)
        with patch('dart_plugin.py.nodes.assistant.describe_local',return_value=weak) as model:
            output=node.describe('adult woman','Natural language','Preserve','','',0,appearance=settings)
            self.assertEqual(output['result'][0],weak['description'])
            self.assertEqual(output['result'][6],'warning')
            self.assertIn('Gigantic breasts',json.dumps(output['ui']['atelier_report']))
        self.assertEqual(model.call_count,2)

    def test_vision_moss_correction_checks_captions_before_returning_json(self):
        from types import SimpleNamespace
        from unittest.mock import Mock
        from dart_plugin.py.dart.vision import caption_image
        settings=self.recipe(breast_size='Gigantic breasts',apply_size_wording=False)
        weak={'summary':{'caption':'A clothed adult woman with a large bust.'},'items':[
             {'label':'object','caption':'An adult woman with a large bust.','bbox':[0,0,1024,1024]}]}
        exact=deepcopy(weak)
        exact['summary']['caption']='A clothed adult woman with gigantic breasts.'
        exact['items'][0]['caption']='An adult woman with gigantic breasts.'
        execute=Mock(side_effect=[SimpleNamespace(args=(json.dumps({'layout_draft':value}),)) for value in (weak,exact)])
        with patch.dict(sys.modules,{'comfy_extras.nodes_textgen':SimpleNamespace(TextGenerate=SimpleNamespace(execute=execute))}):
            text=caption_image(torch.zeros(1,16,16,3),clip='model',output_format='MOSS JSON layout',appearance=settings)
        output=json.loads(text)
        self.assertIn('gigantic breasts',output['summary']['caption'])
        self.assertIn('gigantic breasts',output['items'][0]['caption'])
        self.assertEqual(execute.call_count,2)
        self.assertIn('Gigantic breasts',execute.call_args.kwargs['prompt'])


class OverrideFeedbackTests(unittest.TestCase):
    def settings(self):
        return plugin.NODE_CLASS_MAPPINGS['DanbooruTagsTransformerAppearanceOverrides']().build(breast_size='Gigantic breasts',apply_size_wording=False)['result'][0]

    def run_vision(self, policy='Warn and continue', malformed=False):
        from types import SimpleNamespace
        from unittest.mock import Mock
        node=plugin.NODE_CLASS_MAPPINGS['DanbooruTagsTransformerImageToText']()
        draft={'summary':{'caption':'A clothed adult woman with a large bust.'},'items':[
            {'label':'object','caption':'An adult woman with a large bust.','bbox':[0,0,1024,1024]},
            {'label':'object','caption':'A blue golf club.','bbox':[800,0,1000,1024]}]}
        response='not JSON' if malformed else json.dumps({'layout_draft':draft})
        execute=Mock(return_value=SimpleNamespace(args=(response,)))
        with patch.dict(sys.modules,{'comfy_extras.nodes_textgen':SimpleNamespace(TextGenerate=SimpleNamespace(execute=execute))}), patch('dart_plugin.py.dart.vision.load_local_clip',return_value='model'):
            result=node.describe(torch.zeros(1,16,16,3),appearance=self.settings(),output_format='MOSS JSON layout',on_override_mismatch=policy)
        return result,execute

    def test_vision_warning_preserves_valid_json_and_reports_all_locations(self):
        result,execute=self.run_vision()
        prompt=json.loads(result['result'][0]);report=json.loads(result['result'][5])
        self.assertEqual(result['result'][4],'warning')
        self.assertEqual(report['attempts'],2)
        self.assertEqual(len(report['issues']),2)
        self.assertEqual(report['issues'][0]['missing'],['Gigantic breasts'])
        self.assertEqual(report['issues'][0]['conflicts'],['large bust'])
        self.assertEqual(report['output'],result['result'][0])
        self.assertEqual(result['ui']['text'],[result['result'][0]])
        self.assertEqual(prompt['items'][1]['caption'],'A blue golf club.')
        self.assertEqual(execute.call_count,2)

    def test_block_mode_exposes_preview_and_report_without_data_propagation(self):
        from types import SimpleNamespace
        class Blocker:
            def __init__(self,message):self.message=message
        with patch.dict(sys.modules,{'comfy_execution.graph':SimpleNamespace(ExecutionBlocker=Blocker)}):
            result,_=self.run_vision('Block downstream')
        self.assertTrue(all(isinstance(value,Blocker) for value in result['result'][:4]))
        self.assertEqual(result['result'][4],'blocked')
        self.assertIn('large bust',result['ui']['text'][0])
        self.assertEqual(json.loads(result['result'][5])['status'],'blocked')

    def test_invalid_json_remains_an_error_in_warning_mode(self):
        with self.assertRaisesRegex(ValueError,'valid JSON'):
            self.run_vision(malformed=True)

    def test_corrected_text_result_reports_recovery_and_keeps_output_indices(self):
        node=plugin.NODE_CLASS_MAPPINGS['DanbooruTagsTransformerDescribeImage']()
        weak={**SCENE,'description':'A woman with a large bust.'}
        corrected={**SCENE,'description':'A woman with gigantic breasts.'}
        with patch('dart_plugin.py.nodes.assistant.describe_local',side_effect=[weak,corrected]):
            result=node.describe('woman','Natural language','Preserve','','',0,appearance=self.settings())
        report=json.loads(result['result'][7])
        self.assertEqual(result['result'][0],corrected['description'])
        self.assertEqual(result['result'][6],'corrected')
        self.assertEqual(report['attempts'],2)
        self.assertEqual(report['issues'],[])

    def test_text_moss_persistent_mismatch_warns_and_keeps_generated_layout(self):
        node=plugin.NODE_CLASS_MAPPINGS['DanbooruTagsTransformerDescribeImage']()
        scene={**SCENE,'description':'A woman with a large bust.','layout_draft':{
            'summary':{'caption':'A woman with a large bust.'},'items':[
                {'label':'object','caption':'A woman with a large bust.','bbox':[0,0,1024,1024]}]}}
        with patch('dart_plugin.py.nodes.assistant.describe_local',return_value=scene) as model:
            result=node.describe('woman','MOSS JSON layout','Preserve','','',0,appearance=self.settings())
        self.assertEqual(result['result'][6],'warning')
        self.assertEqual(json.loads(result['result'][0])['bbox_format'],'yxyx')
        report=json.loads(result['result'][7])
        self.assertEqual(len(report['issues']),2)
        self.assertEqual(report['attempts'],model.call_count)
        self.assertLessEqual(model.call_count,4)


class ExactSizeEditTests(unittest.TestCase):
    def settings(self,**kwargs):
        return plugin.NODE_CLASS_MAPPINGS['DanbooruTagsTransformerAppearanceOverrides']().build(breast_size='Gigantic breasts',**kwargs)['result'][0]

    def test_size_edit_replaces_wording_and_preserves_unrelated_items(self):
        from dart_plugin.py.dart.size_edit import edit_layout
        original={'summary':{'caption':'An adult woman with a large bust holds a golf club.'},'items':[
            {'label':'object','caption':'An adult woman with a large bust.','bbox':[0,0,1,1]},
            {'label':'object','caption':'A blue golf club.','bbox':[0,0,1,1]},
            {'label':'text','caption':'White lettering.','text':'large bust','bbox':[0,0,1,1]}]}
        result,edits=edit_layout(original,self.settings())
        self.assertIn('gigantic breasts',result['summary']['caption'])
        self.assertIn('gigantic breasts',result['items'][0]['caption'])
        self.assertEqual(result['items'][1:],original['items'][1:])
        self.assertIn('large bust',original['summary']['caption'])
        self.assertEqual(len(edits),2)

    def test_ambiguous_targets_and_refusals_are_not_rewritten(self):
        from dart_plugin.py.dart.size_edit import edit_text
        from dart_plugin.py.dart.appearance import check_appearance_wording
        settings=self.settings()
        for text in ('Two women have large busts.','A blue circle on white paper.','I cannot describe gigantic breasts.'):
            result,edits=edit_text(text,settings)
            self.assertEqual(result,text)
            self.assertEqual(edits,[])
        with self.assertRaisesRegex(ValueError,'refusal'):
            check_appearance_wording('I cannot describe gigantic breasts.',settings)

    def test_report_distinguishes_post_edit_from_model_compliance(self):
        node=plugin.NODE_CLASS_MAPPINGS['DanbooruTagsTransformerDescribeImage']()
        weak={**SCENE,'description':'An adult woman with a large bust.'}
        with patch('dart_plugin.py.nodes.assistant.describe_local',return_value=weak) as model:
            output=node.describe('adult woman','Natural language','Preserve','','',0,appearance=self.settings())
        report=json.loads(output['result'][7])
        self.assertEqual(model.call_count,1)
        self.assertEqual(report['status'],'edited')
        self.assertIn('gigantic breasts',report['output'])
        self.assertIn('large bust',report['model_output'])
        self.assertEqual(report['post_edits'][0]['trait'],'breast_size')


class ImageBatchTests(unittest.TestCase):
    def test_natural_order_and_independent_resolutions(self):
        from PIL import Image
        cls=plugin.NODE_CLASS_MAPPINGS['DanbooruTagsTransformerImageBatchSelector']
        with tempfile.TemporaryDirectory() as folder:
            for name,size in [('image10.png',(30,20)),('image2.png',(20,10)),('image1.png',(10,30))]:
                Image.new('RGB',size,'red').save(Path(folder)/name)
            result=cls().load(folder='Custom folder',custom_folder=folder,batch_mode='All selected images as list',max_images=3)
            images,names,count,_=result['result']
            self.assertEqual(names,['image1.png','image2.png','image10.png'])
            self.assertEqual([tuple(image.shape) for image in images],[(1,30,10,3),(1,10,20,3),(1,20,30,3)])
            self.assertEqual(count,3)
            one=cls().load(folder='Custom folder',custom_folder=folder,index=4,wrap_index=True)
            self.assertEqual(one['result'][1],['image2.png'])
            with self.assertRaisesRegex(ValueError,'past this folder'):
                cls().load(folder='Custom folder',custom_folder=folder,index=4,wrap_index=False)
            capped=cls().load(folder='Custom folder',custom_folder=folder,batch_mode='All selected images as list',max_images=2)
            self.assertEqual(capped['result'][2],2)
            self.assertIn('2 of 3',capped['ui']['text'][0])

    def test_empty_folder_and_filters_are_actionable(self):
        from PIL import Image
        cls=plugin.NODE_CLASS_MAPPINGS['DanbooruTagsTransformerImageBatchSelector']
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(ValueError,'No supported image'):
                cls().load(folder='Custom folder',custom_folder=folder)
            Image.new('RGB',(8,8)).save(Path(folder)/'test.jpg')
            with self.assertRaisesRegex(ValueError,'No supported image'):
                cls().load(folder='Custom folder',custom_folder=folder,pattern='*.png')
            self.assertEqual(cls.OUTPUT_IS_LIST,(True,True,False,False))


class ImageUploadTests(unittest.TestCase):
    def test_upload_order_dimensions_modes_and_missing_files(self):
        from PIL import Image
        cls=plugin.NODE_CLASS_MAPPINGS['DanbooruTagsTransformerImageBatchUpload']
        with tempfile.TemporaryDirectory() as folder, patch('dart_plugin.py.nodes.image_batch.input_directory',return_value=Path(folder)):
            Image.new('RGB',(16,24)).save(Path(folder)/'second.png')
            Image.new('RGB',(32,16)).save(Path(folder)/'first.png')
            names=json.dumps(['second.png','first.png'])
            values=cls().load(images=names)['result']
            self.assertEqual(values[1],['second.png','first.png'])
            self.assertEqual([tuple(image.shape) for image in values[0]],[(1,24,16,3),(1,16,32,3)])
            self.assertEqual(cls().load(images=names,batch_mode='One image per queued run',index=1)['result'][1],['first.png'])
            self.assertEqual(cls().load(images=names,batch_mode='One image per queued run',index=2)['result'][1],['second.png'])
            self.assertEqual(cls().load(images=names,max_images=1)['result'][2],1)
            with self.assertRaisesRegex(ValueError,'past this collection'):
                cls().load(images=names,batch_mode='One image per queued run',index=2,wrap_index=False)
            self.assertNotEqual(cls.IS_CHANGED(images=names,batch_mode='All selected images as list',index=0,wrap_index=True,max_images=16),cls.IS_CHANGED(images=json.dumps(['first.png','second.png']),batch_mode='All selected images as list',index=0,wrap_index=True,max_images=16))
            with self.assertRaisesRegex(ValueError,'missing on this server'):
                cls().load(images='["missing.png"]')

    def test_upload_manifest_rejects_empty_invalid_and_escaping_paths(self):
        cls=plugin.NODE_CLASS_MAPPINGS['DanbooruTagsTransformerImageBatchUpload']
        with tempfile.TemporaryDirectory() as folder, patch('dart_plugin.py.nodes.image_batch.input_directory',return_value=Path(folder)):
            for value in ['[]','{}','bad','[4]','["../escape.png"]','["/outside.png"]','["code.py"]']:
                with self.subTest(value=value),self.assertRaises(ValueError):cls().load(images=value)
        self.assertEqual(cls.OUTPUT_IS_LIST,(True,True,False,False))


class MemoryTests(unittest.TestCase):
    def test_targeted_offload_runs_on_success_and_error_and_can_be_disabled(self):
        from types import SimpleNamespace
        from unittest.mock import Mock
        from dart_plugin.py.dart.memory import offload_after
        patcher = object()
        clip = SimpleNamespace(patcher=patcher)
        management = SimpleNamespace(unload_model_and_clones=Mock(), soft_empty_cache=Mock(), unload_all_models=Mock())
        with patch.dict(sys.modules, {'comfy': SimpleNamespace(model_management=management), 'comfy.model_management': management}):
            with offload_after(clip, True): pass
            management.unload_model_and_clones.assert_called_once_with(patcher, unload_additional_models=True, all_devices=True)
            with self.assertRaisesRegex(RuntimeError, 'generation failure'), offload_after(clip, True):
                raise RuntimeError('generation failure')
            self.assertEqual(management.unload_model_and_clones.call_count, 2)
            with offload_after(clip, False): pass
            self.assertEqual(management.unload_model_and_clones.call_count, 2)
            management.unload_all_models.assert_not_called()


class VisionTests(unittest.TestCase):
    def test_direct_and_wrapped_native_moss_json_do_not_require_layout_draft(self):
        native = compile_layout({'summary': {'meta': [], 'caption': 'A coat.'}, 'items': [
            {'label': 'object', 'caption': 'A coat.', 'bbox': [0,0,1536,1024]}]}, 1536,1024,draft=True)
        for value in (native, {'moss_layout': native}, {'layout': native}):
            text, execute, _ = self.run_caption(torch.zeros(1,16,16,3), caption=json.dumps(value), output_format='MOSS JSON layout', canvas_width=1536,canvas_height=1024)
            self.assertEqual(json.loads(text), native)
            self.assertEqual(execute.call_count,1)
        with self.assertRaisesRegex(ValueError, 'Returned keys: description'):
            self.run_caption(torch.zeros(1,16,16,3), caption='{"description":"not a layout"}', output_format='MOSS JSON layout')

    def test_vision_releases_encoder_after_generation_failure(self):
        from types import SimpleNamespace
        from unittest.mock import Mock
        from dart_plugin.py.dart.vision import caption_image
        execute = Mock(side_effect=RuntimeError('model failed'))
        with patch.dict(sys.modules, {'comfy_extras.nodes_textgen': SimpleNamespace(TextGenerate=SimpleNamespace(execute=execute))}), patch('dart_plugin.py.dart.memory.release_assistant_model') as release:
            with self.assertRaisesRegex(RuntimeError, 'model failed'):
                caption_image(torch.zeros(1,16,16,3),clip='assistant',unload_after_generation=True)
        release.assert_called_once_with('assistant')
    def test_pixel_budget_resize_uses_selected_batch_method_and_auto_canvas(self):
        from types import SimpleNamespace
        from unittest.mock import Mock
        from dart_plugin.py.dart.vision import prepare_caption_image
        def resize(image, width, height, method, crop):
            return torch.nn.functional.interpolate(image, size=(height, width), mode='bilinear')
        upscale = Mock(side_effect=resize)
        image = torch.zeros(2, 100, 200, 4)
        image[1, :, :, 2] = 1
        with patch.dict(sys.modules, {'comfy.utils': SimpleNamespace(common_upscale=upscale)}):
            prepared, width, height = prepare_caption_image(image, 1, .02, 'Downscale only', 'bicubic', True)
        self.assertEqual((width, height), (192, 96))
        self.assertEqual(tuple(prepared.shape), (1, 96, 192, 3))
        self.assertTrue(torch.all(prepared[..., 2] == 1))
        self.assertEqual(upscale.call_args.args[3:], ('bicubic', 'disabled'))
        self.assertLessEqual(width * height, 20000)

    def test_small_image_stays_small_unless_upscaling_requested(self):
        from types import SimpleNamespace
        from unittest.mock import Mock
        from dart_plugin.py.dart.vision import prepare_caption_image
        upscale = Mock(side_effect=lambda image, w, h, *args: torch.nn.functional.interpolate(image, size=(h, w), mode='nearest'))
        image = torch.zeros(1, 32, 64, 3)
        with patch.dict(sys.modules, {'comfy.utils': SimpleNamespace(common_upscale=upscale)}):
            self.assertEqual(prepare_caption_image(image)[1:], (64, 32))
            upscale.assert_not_called()
            _, width, height = prepare_caption_image(image, megapixels=.01, resize_mode='Resize to budget')
        self.assertGreater(width, 64)
        self.assertLessEqual(width * height, 10000)
        with self.assertRaisesRegex(ValueError, 'megapixel'):
            prepare_caption_image(image, megapixels=float('nan'))

    def test_node_auto_dimensions_reach_moss_and_append_outputs(self):
        node = plugin.NODE_CLASS_MAPPINGS['DanbooruTagsTransformerImageToText']()
        image = torch.zeros(1, 48, 64, 3)
        with patch('dart_plugin.py.nodes.vision.caption_image', return_value='{}') as caption:
            result = node.describe(image, output_format='MOSS JSON layout', canvas_width=1024, canvas_height=1024)
        self.assertEqual(caption.call_args.kwargs['canvas_width'], 64)
        self.assertEqual(caption.call_args.kwargs['canvas_height'], 48)
        self.assertEqual(result['result'][:3], ('{}', 64, 48))
        self.assertEqual(tuple(result['result'][3].shape), (1, 48, 64, 3))
        with patch('dart_plugin.py.nodes.vision.caption_image', return_value='{}') as caption:
            result = node.describe(image, output_format='MOSS JSON layout', dimension_source='Manual canvas', canvas_width=1536)
        self.assertEqual(caption.call_args.kwargs['canvas_width'], 1536)
        self.assertEqual(result['result'][1:3], (1536, 1024))

    def test_all_nodes_have_searchable_atelier_prefix(self):
        self.assertEqual(len(plugin.NODE_DISPLAY_NAME_MAPPINGS), len(plugin.NODE_CLASS_MAPPINGS))
        self.assertTrue(all(name.startswith('Prompt Mage') for name in plugin.NODE_DISPLAY_NAME_MAPPINGS.values()))

    def test_structured_caption_validates_json_and_keeps_literal_trigger(self):
        value = dict(description='A red coat.', subjects=['A traveler wearing a red coat.'],
                     environment='A cafe.', lighting='Warm.', composition='Close view.', visible_text=['CAFE'])
        text, execute, _ = self.run_caption(torch.zeros(1, 16, 16, 3),
            caption='```json\n' + json.dumps(value) + '\n```', output_format='Structured JSON', character_trigger='my_character')
        result = json.loads(text)
        self.assertTrue(result['description'].startswith('my_character, '))
        self.assertEqual(result['visible_text'], ['CAFE'])
        self.assertIn('Apply requested replacements consistently', execute.call_args.kwargs['system_prompt'])
        self.assertIn('\n  "subjects":', text)
        with self.assertRaisesRegex(ValueError, 'subjects'):
            self.run_caption(torch.zeros(1, 16, 16, 3), caption=json.dumps({**value, 'subjects': 'invalid'}), output_format='Structured JSON')

    def test_moss_vision_compiles_boxes_on_requested_canvas(self):
        draft = dict(summary=dict(meta=['photograph'], canvas='single', caption='A red coat.'),
                     items=[dict(label='object', caption='A red coat.', bbox=[0, 0, 1024, 1024])])
        text, execute, _ = self.run_caption(torch.zeros(1, 16, 24, 3), caption=json.dumps({'layout_draft': draft}),
            output_format='MOSS JSON layout', canvas_width=1536, canvas_height=1024, character_trigger='my_character')
        result = json.loads(text)
        self.assertEqual(result['items'][0]['bbox'], [-512, -768, 512, 768])
        self.assertIn('my_character', result['summary']['caption'])
        self.assertEqual(result['bbox_format'], 'yxyx')
        self.assertIn('normalized 1024x1024', execute.call_args.kwargs['system_prompt'])

    def test_invalid_vision_json_fails_without_corrupting_output(self):
        for text in ('{"description":', '[]'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                self.run_caption(torch.zeros(1, 16, 16, 3), caption=text, output_format='Structured JSON')

    def test_vision_json_schema_gets_one_bounded_repair(self):
        from types import SimpleNamespace
        from unittest.mock import Mock
        from dart_plugin.py.dart.vision import caption_image
        value = dict(description='A red coat.', subjects=['A coat.'], environment='', lighting='', composition='', visible_text=[])
        execute = Mock(side_effect=[SimpleNamespace(args=('{"description":',)), SimpleNamespace(args=(json.dumps(value),))])
        with patch.dict(sys.modules, {'comfy_extras.nodes_textgen': SimpleNamespace(TextGenerate=SimpleNamespace(execute=execute))}):
            text = caption_image(torch.zeros(1,16,16,3), clip='model', output_format='Structured JSON')
        self.assertEqual(json.loads(text), value)
        self.assertEqual(execute.call_count, 2)
        self.assertIn('Validation error', execute.call_args.kwargs['prompt'])

    def test_direct_language_reaches_vision_system(self):
        _, execute, _ = self.run_caption(torch.zeros(1, 16, 16, 3), language_style='Direct / explicit')
        self.assertIn('avoid euphemisms', execute.call_args.kwargs['system_prompt'])

    def run_caption(self, image, caption='A blue square on a pale background.', **kwargs):
        from types import SimpleNamespace
        from unittest.mock import Mock
        from dart_plugin.py.dart.vision import caption_image
        execute = Mock(return_value=SimpleNamespace(args=(caption,)))
        module = SimpleNamespace(TextGenerate=SimpleNamespace(execute=execute))
        with patch.dict(sys.modules, {'comfy_extras.nodes_textgen': module}), \
                patch('dart_plugin.py.dart.vision.load_local_clip', return_value='vision-model') as loader:
            result = caption_image(image, **kwargs)
        return result, execute, loader

    def test_selected_image_and_free_instructions_reach_vision_model(self):
        image = torch.zeros(2, 24, 32, 4)
        image[1, :, :, 2] = 1
        text, execute, _ = self.run_caption(image, image_index=1,
                                           instructions='Use silver hair, omit original hair color.',
                                           character_trigger='my_character', max_tokens=512)
        call = execute.call_args.kwargs
        self.assertTrue(torch.equal(call['image'], image[1:2, :, :, :3]))
        self.assertEqual(json.loads(call['prompt'])['instructions'], 'Use silver hair, omit original hair color.')
        self.assertEqual(call['max_length'], 512)
        self.assertTrue(text.startswith('my_character, '))

    def test_exact_trigger_is_not_duplicated(self):
        text, _, _ = self.run_caption(torch.zeros(1, 16, 16, 3), caption='my_character wears a red coat.',
                                      character_trigger='my_character')
        self.assertEqual(text, 'my_character wears a red coat.')

    def test_invalid_image_or_batch_index_fails_before_model_loading(self):
        from dart_plugin.py.dart.vision import caption_image
        with patch('dart_plugin.py.dart.vision.load_local_clip') as loader:
            for image in (torch.zeros(16, 16, 3), torch.zeros(0, 16, 16, 3), torch.zeros(1, 16, 16, 1)):
                with self.assertRaisesRegex(ValueError, 'IMAGE'):
                    caption_image(image)
            with self.assertRaisesRegex(ValueError, 'outside this batch'):
                caption_image(torch.zeros(1, 16, 16, 3), image_index=1)
        loader.assert_not_called()

    def test_empty_caption_has_actionable_error(self):
        with self.assertRaisesRegex(ValueError, 'empty caption'):
            self.run_caption(torch.zeros(1, 16, 16, 3), caption='')

    def test_new_node_previews_caption_and_has_complete_help(self):
        node = plugin.NODE_CLASS_MAPPINGS['DanbooruTagsTransformerImageToText']()
        with patch('dart_plugin.py.nodes.vision.caption_image', return_value='A red coat beside a cafe window.'):
            output = node.describe(torch.zeros(1, 16, 16, 3), instructions='Keep the setting.')
        self.assertEqual(output['ui']['text'], [output['result'][0]])
        self.assertEqual(output['result'][1:3], (16, 16))
        for fields in node.INPUT_TYPES().values():
            for spec in fields.values():
                self.assertTrue(spec[1]['tooltip'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
