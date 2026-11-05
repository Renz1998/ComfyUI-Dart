# Publishing Prompt Mage

## Current status

**Version 1.6.0 was uploaded on November 6, 2026**, under [@renz1998](https://registry.comfy.org/publishers/renz1998). Its [publishing workflow](https://github.com/Renz1998/ComfyUI-Prompt-Atelier/actions/runs/42102349356) completed validation and upload successfully, using runtime commit ebfc732c52896b0d825722ad4505cd0ded8f0230. The public CDN archive was downloaded and checked for version 1.6.0 and the Prompt Mage branding and simplified upload runtime. Latest-version visibility on the [Registry detail page](https://registry.comfy.org/nodes/prompt-atelier), separate review/indexing status and Manager search visibility remain unverified.

## Registry route

Follow the [official publishing guide](https://docs.comfy.org/registry/publishing) and [metadata specification](https://docs.comfy.org/registry/specifications):

1. Completed: publisher `renz1998` is registered at registry.comfy.org. Its publisher ID is permanent.
2. Completed: `PublisherId = "renz1998"` is set under `[tool.comfy]` in pyproject.toml. The published package ID is `prompt-atelier`.
3. Completed: the publisher key is saved in GitHub Actions Secrets as `REGISTRY_ACCESS_TOKEN`. Never put its value in source, workflow examples, issues or chat.
4. Ensure the public default branch is `main` and includes this implementation, not the untouched upstream branch. Repository, icon and banner URLs must resolve publicly.
5. Completed for 1.6.0: **Publish Prompt Mage** ran on main and passed metadata validation, all 70 Python tests and four JavaScript suites before upload.
6. The 1.6.0 CDN archive is verified. Latest-version visibility on the detail page and Manager search remains to be checked; upload, scanning and indexing can be separate steps.

The action is manual-only; changing documentation or branding does not automatically publish a package. Increment the version for each subsequent Registry release.

## Legacy Manager catalogue

The [Manager registration guide](https://github.com/Comfy-Org/ComfyUI-Manager#how-to-register-your-custom-node-into-comfyui-manager) also documents a PR adding an entry to custom-node-list.json. A candidate entry is in docs/manager-entry.json. Validate it against the live catalogue and verify the default branch before submitting it. A prepared entry is not an accepted listing.

Prompt Mage retains the old DanbooruTagsTransformer class IDs for workflow compatibility. State clearly that it replaces ComfyUI-Dart and cannot be installed alongside it; catalogue conflict detection may report these shared IDs. Do not hide the inherited IDs or claim the original nodes as new model work.

## Release material

- README.md: feature summary, installation and model requirements.
- CREDITS.md + unchanged LICENSE: source/model attribution.
- workflows/next/README.md: runnable text workflows and combined examples.
- assets/icon.svg and banner.svg: Registry/GitHub branding.
- CHANGELOG.md: user-visible release notes.
- .comfyignore: excludes tests/CI from the Registry runtime archive.

Screenshots should use neutral examples, name the tested model/settings and distinguish prompt output from image generation. Do not promise traffic, stars, Registry approval or image quality.
