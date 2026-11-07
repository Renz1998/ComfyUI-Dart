# Contributing

Prompt Mage is a community project, and help is welcome! You do not need to code to contribute.

- **Try the [main Archmage workflow](workflows/start-here/03-moss-full-workflow.json)** and report confusing controls or reproducible errors.
- **Share a clean workflow or comparison:** prose versus JSON, local versus API, or a style that works well. Include models and settings so others can reproduce it.
- **Test model compatibility:** public download link, exact filename, runtime, GPU/VRAM, generation speed and any failures.
- **Help with development:** UI accessibility, memory/cancellation handling, tests, DART v3 integration and layout quality. Small focused pull requests are welcome.
- **Improve the docs:** clearer setup instructions, screenshots and corrections are useful contributions.

[Report a bug or share an idea](https://github.com/Renz1998/ComfyUI-Prompt-Mage/issues/new/choose) · [Open a pull request](https://github.com/Renz1998/ComfyUI-Prompt-Mage/compare) · [Optional financial support](SUPPORT.md)

Check existing issues first. Keep examples shareable and remove credentials, personal paths and private LoRAs. Link to original model downloads and access terms rather than redistributing weights.

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
