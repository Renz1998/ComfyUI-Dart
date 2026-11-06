# Prompt Mage — Quickstart

## 1. Install once

Follow [README installation](README.md#install), restart ComfyUI and refresh your browser. Search **Prompt Mage · Archmage (Beta)**. Disable the original ComfyUI-Dart if it is also installed; the packs share legacy IDs.

## 2. Pick a model

Install a full generation-capable Qwen checkpoint in `ComfyUI/models/text_encoders`. Choose it in Local model, or connect CLIP from a compatible loader. Reference images require vision weights. Automatic prefers a small general model; choose a compatible Qwen3.5 explicitly when testing Thinking mode. No weights are bundled or automatically downloaded.

## 3. Write or connect your idea

- Enter Concepts such as `an adult explorer reading a map in a small workshop`, or leave blank for a seeded scene.
- Connect an image to prioritize a reference. Instructions and Appearance Overrides request changes to its generated description.
- Choose Style / theme, for example **Photo · Amateur Instagram** or **Anime · Sci-fi**. Custom style notes refine any preset. Reference images retain their style unless Reference style is set to Apply selected style.
- Choose an aspect ratio or custom width/height. From image when connected uses processed reference dimensions; Manual uses your canvas choice.

## 4. Choose and connect the output

Use **prompt** for your positive text encoder. Prose produces plain text; MOSS JSON layout produces validated native JSON. **description** stays prose for a separate tagger. **moss_json** is inactive in Prose mode. **width/height** can drive your latent. Without a reference the image output is inactive rather than a fake blank image.

Start with Balanced length, 4096 tokens and Thinking mode off. With a compatible model, enable thinking and try 8192 tokens. Thinking shares the per-stage ceiling with the final answer and can take much longer. Missing final answers or invalid layouts show an actionable blocked report; review appearance warnings separately.

## 5. Add a reusable character or image list

Connect **Appearance Overrides → appearance**. Choose a trigger and only the traits you want replaced. Keep unchanged leaves other traits alone. Custom reveals a free-text option. These instructions edit text, not pixels.

For local/RunPod uploads, connect **Upload Images.image → Archmage.image** and **filename → source_name**. Choose a sequential list or one image per queued run; keep Image index at 0 for lists. The image drag-create shortcut suggests Archmage and wires filenames too. Wait for uploads to complete.

## Examples and deeper help

[Workflow gallery](workflows/next/README.md) · [Archmage controls](docs/ARCHMAGE_BETA.md) · [Model choices](docs/MODEL_CHOICES.md) · [DART/legacy setup](docs/DART_AND_LEGACY_SETUP.md)

Scene Composer, Text Assistant and Image to Text are deprecated but remain under Prompt Mage/Deprecated. Their IDs and sockets are retained. General Structured JSON captions and external chat-server features remain available in the legacy nodes; Archmage currently focuses on prose and native MOSS layouts.
