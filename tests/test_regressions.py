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
        ids = self.sequences.get(…4039 tokens truncated…   self.wfile.write(json.dumps({'choices': [{'message': {'content': '```json\n' + json.dumps(SCENE) + '\n```'}}]}).encode())

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


if __name__ == '__main__':
    unittest.main(verbosity=2)
