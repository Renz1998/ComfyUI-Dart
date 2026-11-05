# Publishing Prompt Atelier

## Current status

The repository metadata, credits, icon/banner, workflow gallery, tests and manual publishing action are prepared. **Publisher [@renz1998](https://registry.comfy.org/publishers/renz1998) and its GitHub Actions publishing secret are configured. This pack has not yet been published to Comfy Registry; release validation is in progress.** A GitHub repository or a successful test run does not establish Manager visibility.

## Registry route

Follow the [official publishing guide](https://docs.comfy.org/registry/publishing) and [metadata specification](https://docs.comfy.org/registry/specifications):

1. Completed: publisher `renz1998` is registered at registry.comfy.org. Its publisher ID is permanent.
2. Completed: `PublisherId = "renz1998"` is set under `[tool.comfy]` in pyproject.toml. The package ID is `prompt-atelier`; it is not reserved until Registry publication.
3. Completed: the publisher key is saved in GitHub Actions Secrets as `REGISTRY_ACCESS_TOKEN`. Never put its value in source, workflow examples, issues or chat.
4. Ensure the public default branch is `main` and includes this implementation, not the untouched upstream branch. Repository, icon and banner URLs must resolve publicly.
5. Run **Publish Prompt Atelier** manually from GitHub Actions on main. It validates metadata and runs the test suites before the official publish action.
6. Check the actual Registry version status and search result in Manager. Publication/scanning/indexing may require additional review. Do not label it installable in Manager before verifying the listing.

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
