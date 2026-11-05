# Publishing Prompt Atelier

## Current status

**Version 1.5.0 was published on November 5, 2026**, under [@renz1998](https://registry.comfy.org/publishers/renz1998). The [public Registry page](https://registry.comfy.org/nodes/prompt-atelier) shows Version 1.5.0 and its install command. The [publishing workflow](https://github.com/Renz1998/ComfyUI-Prompt-Atelier/actions/runs/42039759348) completed validation and upload successfully, using source commit efda46a62b7e0e73ce4c0845478d5b8741e07085. Manager search visibility and any separate review/indexing status have not been verified.

## Registry route

Follow the [official publishing guide](https://docs.comfy.org/registry/publishing) and [metadata specification](https://docs.comfy.org/registry/specifications):

1. Completed: publisher `renz1998` is registered at registry.comfy.org. Its publisher ID is permanent.
2. Completed: `PublisherId = "renz1998"` is set under `[tool.comfy]` in pyproject.toml. The published package ID is `prompt-atelier`.
3. Completed: the publisher key is saved in GitHub Actions Secrets as `REGISTRY_ACCESS_TOKEN`. Never put its value in source, workflow examples, issues or chat.
4. Ensure the public default branch is `main` and includes this implementation, not the untouched upstream branch. Repository, icon and banner URLs must resolve publicly.
5. Completed for 1.5.0: **Publish Prompt Atelier** ran on main and passed metadata validation, all 42 Python tests and both JavaScript suites before upload.
6. Public Registry version/page verified. Manager search visibility remains to be checked; publication/scanning/indexing can be separate steps.

The action is manual-only; changing documentation or branding does not automatically publish a package. Increment the version for each subsequent Registry release.

## Legacy Manager catalogue

The [Manager registration guide](https://github.com/Comfy-Org/ComfyUI-Manager#how-to-register-your-custom-node-into-comfyui-manager) also documents a PR adding an entry to custom-node-list.json. A candidate entry is in docs/manager-entry.json. Validate it against the live catalogue and verify the default branch before submitting it. A prepared entry is not an accepted listing.

Prompt Atelier retains the old DanbooruTagsTransformer class IDs for workflow compatibility. State clearly that it replaces ComfyUI-Dart and cannot be installed alongside it; catalogue conflict detection may report these shared IDs. Do not hide the inherited IDs or claim the original nodes as new model work.

## Release material

- README.md: feature summary, installation and model requirements.
- CREDITS.md + unchanged LICENSE: source/model attribution.
- workflows/next/README.md: runnable text workflows and combined examples.
- assets/icon.svg and banner.svg: Registry/GitHub branding.
- CHANGELOG.md: user-visible release notes.
- .comfyignore: excludes tests/CI from the Registry runtime archive.

Screenshots should use neutral examples, name the tested model/settings and distinguish prompt output from image generation. Do not promise traffic, stars, Registry approval or image quality.
