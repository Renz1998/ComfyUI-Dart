# Changelog

## 1.5.2 — Appearance recipes, targeted offloading and MOSS parsing

- Added optional Appearance Overrides with trait dropdowns, custom values, subject selection, literal character trigger and identity wording controls, shared by both assistants.
- Dragging from either appearance input suggests and connects the recipe node; the recipe output suggests either assistant.
- Added opt-in targeted assistant model offloading after successful generation or errors; unrelated diffusion models stay loaded. Shared encoders can reload when needed.
- Vision MOSS parsing accepts direct native summary/items layouts and supported wrappers instead of requiring layout_draft. Missing layout errors now identify returned keys; native coordinates are validated without double conversion.

## 1.5.1 — Vision JSON and searchable node names

- Image to Text now supports Plain text, Structured JSON and native MOSS JSON layout, with character instructions and formatted previews.
- MOSS vision layouts expose canvas dimensions, validate boxes and convert to native centered yxyx coordinates. Box placement is model-estimated.
- All DART display names now start with Prompt Atelier for node search. Persisted class IDs and output socket positions are unchanged.
- Added an image megapixel budget, downscale-only or upscale-to-budget mode, five interpolation methods, automatic MOSS canvas sizing and width/height/processed-image outputs. Existing description connections keep output index 0.

## 1.5.0 — Prompt Atelier branding and workflow gallery

- Renamed the pack and assistant display names to Prompt Atelier; preserved legacy class IDs, sockets and the upstream license/history.
- Added source/model credits, Registry-shaped metadata, icon/banner, manual publication preparation and contributor guidance.
- Added combined workflows for descriptions/photos → DART v3, photos → MOSS JSON, shared vision-to-prose, and keywords → MOSS JSON.
- Grouped tools into Assistants, Vision and DART categories.
- Added four prompt lengths, a configurable generation budget, and direct-language wording options for both assistants.
- Formatted MOSS JSON output and Markdown preview; inactive layout sockets no longer draw or accept drops outside JSON mode.
- Improved MOSS caption detail, removed a misleading example text box, and added one bounded revision for very short Detailed/Extensive creative responses.

## 1.4.0

- Added local Image to Text with free instructions, exact character trigger, detail/token limits and batch selection.

## 1.3.0

- Added source tags, custom instructions, Concept/Natural language modes, validated MOSS JSON layouts and named settings persistence.

## 1.2.0

- Added complete hover help, role palettes, expandable guides, execution animations and reduced-motion support.

## 1.1.x

- Added DART v3 Preview E support, native local Qwen assistance, direct previews, compatible socket menus and reliability fixes.

Earlier DART node foundation: [nkchocoai/ComfyUI-Dart](https://github.com/nkchocoai/ComfyUI-Dart).
