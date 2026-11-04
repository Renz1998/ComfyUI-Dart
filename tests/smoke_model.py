"""Explicitly load/download a DART model and run a repeatability smoke check."""

import argparse
import importlib.util
from pathlib import Path
import sys

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--model', choices=['v1', 'v2', 'v3'], default='v3')
parser.add_argument('--local-files-only', action='store_true')
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('dart_plugin', root / '__init__.py', submodule_search_locations=[str(root)])
plugin = importlib.util.module_from_spec(spec)
sys.modules['dart_plugin'] = plugin
spec.loader.exec_module(plugin)
nodes = plugin.NODE_CLASS_MAPPINGS
names = {'v1': 'dart-v1-sft', 'v2': 'dart-v2-sft', 'v3': 'dart-v3-sft-preview-E (experimental)'}
model, tokenizer = nodes['DanbooruTagsTransformerLoader']().load(names[args.model], local_files_only=args.local_files_only)
if args.model == 'v1':
    prompt = nodes['DanbooruTagsTransformerComposePrompt']().compose('rating:general', 'original', '', 'long', '1girl, solo')[0]
elif args.model == 'v2':
    prompt = nodes['DanbooruTagsTransformerComposePromptV2']().compose('original', '', 'general', 'square', 'medium', '1girl, solo', 'none')[0]
else:
    prompt = nodes['DanbooruTagsTransformerComposePromptV3']().compose('general', 'square', 'medium', 'original', '', '1girl, solo, red hair')[0]
generate = nodes['DanbooruTagsTransformerGenerate']()
kwargs = {'setting': {'max_new_tokens': 32, 'min_new_tokens': 0, 'temperature': 0},
          'ban_tags': 'blue hair', 'remove_tags': 'blush', 'keep_tags': '(red coat:1.2)'}
first = generate.generate(model, tokenizer, prompt, 7, **kwargs)[0]
second = generate.generate(model, tokenizer, prompt, 7, **kwargs)[0]
assert first == second, 'Repeated deterministic generation changed'
assert '(red coat:1.2)' in first, 'Required weighted tag was lost'
assert 'blush' not in first and 'blue hair' not in first
assert '<|' not in first
print('SMOKE_OK', args.model, first)
