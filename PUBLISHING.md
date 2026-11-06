# Publishing Prompt Mage

## Verified release: 1.7.0

**Prompt Mage 1.7.0 was published on November 6, 2026**, under [@renz1998](https://registry.comfy.org/publishers/renz1998), from runtime commit `de78851ba9d01ea493b31e727c81b54124280d70`.

- [GitHub repository](https://github.com/Renz1998/ComfyUI-Prompt-Mage): renamed to **ComfyUI-Prompt-Mage**, with updated docs and actual neutral node screenshots.
- [Registry listing](https://registry.comfy.org/nodes/prompt-atelier): display name **Prompt Mage**, with the renamed repository link.
- [Publish workflow](https://github.com/Renz1998/ComfyUI-Prompt-Mage/actions/runs/42204872962): validation and upload completed successfully, including all **102 Python tests** and four JavaScript suites.
- [Version 1.7.0 CDN archive](https://cdn.comfy.org/renz1998/prompt-atelier/1.7.0/node.zip): downloaded and checked for metadata, Archmage, native thinking, style presets, the offline tag vocabulary and legacy deprecation markers.

The Registry package ID stays **prompt-atelier**. [Official publishing metadata](https://docs.comfy.org/registry/publishing) marks package IDs immutable after creation; display names can change. Keeping the ID preserves the existing update route. A separate duplicate package is unnecessary. Manager search/index timing is independent of a verified upload.

Archmage remains labeled **Beta**; Tag Composer remains **Experimental**. Deprecated assistants retain their class IDs, socket order and execution behavior. Their labels/categories guide new users toward Archmage without deleting older graphs or specialized legacy features.

## Publish another version

1. Increment the version in pyproject.toml and update CHANGELOG.md.
2. Verify docs, public asset URLs, workflows and tests. Use neutral screenshots with no private prompts, images or credentials.
3. Commit to main, then run **Publish Prompt Mage** manually from GitHub Actions.
4. The existing `REGISTRY_ACCESS_TOKEN` secret supplies the publisher key. Never put its value in source, issues or chat. No new key is needed for a repository rename.
5. Verify validation/upload results, the CDN package metadata, the Registry detail page and any separate Manager indexing status.

The workflow is manual-only; documentation changes do not automatically republish a version. Refer to the [publishing guide](https://docs.comfy.org/registry/publishing) and [metadata specification](https://docs.comfy.org/registry/specifications).

## Compatibility and credits

Prompt Mage replaces the original ComfyUI-Dart installation and keeps its DanbooruTagsTransformer IDs. Do not install both copies together. The original GPL-3.0 license and upstream/model credits remain in LICENSE and CREDITS.md.

The legacy Manager catalogue candidate in docs/manager-entry.json points to the renamed repository. It is prepared material, not a claim of an accepted catalogue PR. Follow the [Manager registration guide](https://github.com/Comfy-Org/ComfyUI-Manager#how-to-register-your-custom-node-into-comfyui-manager) if a separate catalogue contribution is needed.

## Earlier release

Version 1.6.0 was also verified through its [workflow](https://github.com/Renz1998/ComfyUI-Prompt-Mage/actions/runs/42102349356) and CDN archive. The 1.7.0 release adds the unified beta assistant, styles/thinking, experimental tagging and migration guidance on top of that version.
