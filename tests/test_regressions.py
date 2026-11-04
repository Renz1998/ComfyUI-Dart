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
from dart_plugin.py.dart.assistant import request_scene, format_scene
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


class AssistantTests(unittest.TestCase):
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
            result = request_scene('rainy cafe', endpoint, 'test-model', 'Preserve', '', '', 5)
            self.assertEqual(result['source_description'], 'rainy cafe')
            self.assertEqual(received[0][0], '/v1/chat/completions')
            self.assertEqual(received[0][1]['model'], 'test-model')
            self.assertIn('rainy cafe', received[0][1]['messages'][1]['content'])
        finally:
            server.shutdown()
            server.server_close()
            thread.join()

    def test_missing_key_and_missing_model_fail_before_network(self):
        with self.assertRaisesRegex(ValueError, 'environment variable'):
            request_scene('scene', 'http://localhost:1234/v1', 'm', 'Preserve', '', '', 0, api_key_env='DART_TEST_MISSING_KEY')
        with self.assertRaisesRegex(ValueError, 'model identifier'):
            request_scene('scene', 'http://localhost:1234/v1', '', 'Preserve', '', '', 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
