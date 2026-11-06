# Move to the Prompt Mage Registry ID

The distribution is moving from **prompt-atelier** to **prompt-mage**. The repository remains [Renz1998/ComfyUI-Prompt-Mage](https://github.com/Renz1998/ComfyUI-Prompt-Mage), publisher **renz1998**. The new command is:

```bash
comfy node install prompt-mage
```

**Only install one copy.** Prompt Mage, the legacy prompt-atelier distribution and the original ComfyUI-Dart share DanbooruTagsTransformer class IDs. Installing two simultaneously can register conflicting implementations. Renaming the package does not rename the saved workflow nodes.

## Why this is a new listing

Registry package IDs are immutable after creation; display names are editable. The old ID cannot be changed into prompt-mage. The legacy listing is retained with a migration notice, not deleted. No automatic Registry redirect or automatic package switch is claimed.

## Existing Git installation

Keep your current directory and workflow files. Confirm its origin is this fork, then update the remote and pull the current main branch:

```bash
git remote set-url origin https://github.com/Renz1998/ComfyUI-Prompt-Mage.git
git pull --ff-only origin main
```

Run these commands inside the existing Prompt Mage custom-node directory. Preserve local modifications first; if Git reports a conflict or divergent history, do not discard changes blindly. A directory still named ComfyUI-Dart or prompt-atelier can remain named that way for Git installs. Restart ComfyUI and refresh the browser after updating. Do not clone another copy next to it.

## Existing Registry installation

Back up workflows and any local plugin modifications. Once the new listing has a usable Registry version, disable the old package, install **prompt-mage**, and restart ComfyUI. Verify your workflows before removing the disabled legacy copy. Preserve your ComfyUI input/user/model directories; the package move does not require deleting images, models or workflows.

Existing class IDs and socket order remain intact. Uploaded paths under `input/prompt-atelier/` still load; only newly uploaded files use `input/prompt-mage/`.

## Registry review and Manager visibility

The naming migration and Registry review are separate. On November 7, 2026 the public API reported legacy versions 1.5.0–1.7.0 as **Flagged** and 1.8.0 as **Pending**. The Registry UI and public version responses did not expose a reason. We cannot assert that these are false positives or that the rename resolves them.

The new listing goes through the same Registry review. An uploaded/downloadable ZIP does **not** prove that a version is Active, searchable/installable through every Manager view, or approved by security review. See [publishing status](../PUBLISHING.md) for the actual current states.

Use Manager's default channel and refresh its database when a new listing becomes available; other channels or stale local caches can omit Registry-only packages. The legacy Manager catalogue is a separate registration route. No review bypass or security-setting change is part of this migration.
