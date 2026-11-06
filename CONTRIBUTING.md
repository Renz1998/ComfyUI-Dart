# Contributing

Keep the original authors and model provenance visible. Do not change persisted DanbooruTagsTransformer node IDs or existing socket order without a migration. New UI controls need concise hover help; example graphs should avoid cycles and external node-pack dependencies.

## Checks

```bash
python -m unittest discover -s tests -p 'test_*.py'
node tests/test_connections.mjs
node tests/test_menu.mjs
```

Python checks require Torch and Transformers. CI checks Transformers 4.46.3 and 5.17.0. Real-model smoke tests are optional and explicitly download/cache weights; see QUICKSTART.md. A UI-only change does not require generating images.

For a bug report include the pack version/commit, ComfyUI/frontend versions, model filename, relevant error, and a minimal workflow with private prompts and credentials removed. Explain the expected and actual behavior. For prompt quality reports, include a neutral input and exact settings where possible.

Model-generated captions and instructions are not semantic guarantees. Report model behavior separately from crashes, schema validation, wrong connections or missing controls.
