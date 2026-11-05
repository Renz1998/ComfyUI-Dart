# Changelog

## 1.6.0 — Prompt Mage and simpler remote uploads

- Rebranded visible node names, categories, guides, documentation and Registry display name to Prompt Mage. Existing class IDs, repository URL and Registry package ID stay compatible.
- Upload Images now has a large click-to-browse drop area, whole-node image drops and a local Choose folder action, preserving nested folder paths during upload.
- Renamed the path-based selector to Server Folder (Advanced) to distinguish server paths from uploads on RunPod.
- Removed the dependency on secure-context crypto.randomUUID so uploads do not hang on HTTP hosts where it is unavailable.


## 1.5.5 — Direct multi-image uploads

- Added Image Batch Upload: multi-file picker, drag-and-drop, thumbnail previews, reorder/remove/clear controls and upload progress/errors. Uses native ComfyUI input uploads, including on remote servers.
- Supports one image per queued run or a sequential native image list, preserving independent dimensions and filename labels. Dragging from image also wires the filename to Image to Text.
- Saved collections use input-relative paths; invalid, escaping or missing files report actionable errors. Removing from the list leaves server files intact.
- Added Ember/Studio themes, animated flames and rising embers during execution, a stronger RUNNING badge and a canvas outline. Animation respects reduced motion and stops with execution.
- Added an upload workflow example and upload endpoint/backend regression coverage.

## 1.5.4 — Visible override feedback and graceful handling

- Added Image Batch Selector: folder choice, natural filename order, one image per queued run or a native list mapped sequentially through Image to Text. Images retain independent dimensions and filenames label reports.
- Added explicit Apply exact breast-size wording. Identifiable target captions can be post-edited to use the selected phrase, with original output and edit details retained. This is labeled as an Prompt Mage caption edit, not a model unlock/compliance guarantee; ambiguous targets are not blindly rewritten.
- Both assistants now default to Warn and continue when valid model output still misses selected wording after correction. A visible amber report names missing/conflicting phrases and their output locations.
- Added On override mismatch directly to each assistant. Block downstream preserves the raw preview/report while blocking dependent data outputs, without an appearance-validation traceback.
- Appended status/report outputs; existing output positions remain unchanged. Reports include attempts, issues, policy and the actual generated text. Prompt wires remain clean prose/JSON.
- Feedback remains visible when node branding is disabled. Invalid JSON, model failures and invalid inputs still stop normally.

## 1.5.3 — Preserve selected appearance wording

- Appearance Overrides now defaults to Strict trait wording: missing selected phrases or weakened/conflicting size wording trigger a bounded correction instead of being returned silently.
- Checks prose, structured descriptions/subjects, DART tags and MOSS summaries/target-person captions. Unrelated object captions are not modified. Remaining failures report the missing/conflicting phrases.
- Disable Strict trait wording to allow model paraphrasing. Wording checks do not prove visual accuracy, multi-person identity assignment or free-form instruction compliance.

## 1.5.2 — Appearance recipes, targeted offloading and MOSS parsing

- Added optional Appearance Overrides with trait dropdowns, custom values, subject selection, literal character trigger and identity wording controls, shared by both assistants.
- Dragging from either appearance input suggests and connects the recipe node; the recipe output suggests either assistant.
- Added opt-in targeted assistant model offloading after successful generation or errors; unrelated diffusion models stay loaded. Shared encoders can reload when needed.
- Vision MOSS parsing accepts direct native summary/items layouts and supported wrappers instead of requiring layout_draft. Missing layout errors now identify returned keys; native coordinates are validated without double conversion.

## 1.5.1 — Vision JSON and searchable node names

- Image to Text now supports Plain text, Structured JSON and native MOSS JSON layout, with character instructions and formatted previews.
- MOSS vision layouts expose canvas dimensions, validate boxes and convert to native centered yxyx coordinates. Box placement is model-estimated.
- All DART display names now start with Prompt Mage for node search. Persisted class IDs and output socket positions are unchanged.
- Added an image megapixel budget, downscale-only or upscale-to-budget mode, five interpolation methods, automatic MOSS canvas sizing and width/height/processed-image outputs. Existing description connections keep output index 0.

## 1.5.0 — Prompt Mage branding and workflow gallery

- Renamed the pack and assistant display names to Prompt Mage; preserved legacy class IDs, sockets and the upstream license/history.
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
