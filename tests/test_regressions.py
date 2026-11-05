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
        self.assertEqual(len(result['result']), 6)

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
        self.assertEqual(len(result['result']), 6)

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


class VisionTests(unittest.TestCase):
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
        self.assertEqual(output['ui']['text'], list(output['result']))
        for fields in node.INPUT_TYPES().values():
            for spec in fields.values():
                self.assertTrue(spec[1]['tooltip'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
