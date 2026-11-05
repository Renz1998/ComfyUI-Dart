# Prompt Atelier workflow gallery

These are complete **text-processing graphs** you can drag into ComfyUI. They create prompts for an existing image-generation workflow; diffusion checkpoints, samplers and image saving are deliberately left to that workflow. Existing DanbooruTagsTransformer node IDs remain compatible.

## Choose a starting point

| Example | Pipeline | Models / cost |
| --- | --- | --- |
| [keywords_to_concept.json](keywords_to_concept.json) | Keywords → Text Assistant → photographic concept | Full instruction Qwen; one assistant pass |
| [describe_image.json](describe_image.json) | Description → tags + prose + debug preview | Full instruction Qwen; one pass |
| [image_to_text.json](image_to_text.json) | Load Image → Image to Text caption | Full vision Qwen; one pass |
| [moss_json_layout.json](moss_json_layout.json) | Scene description → native MOSS layout JSON | Full instruction Qwen; layout planning |
| [dart_v3_tags.json](dart_v3_tags.json) | V3 Composer → DART Generate → tag preview | DART v3 Preview E; no Qwen required |
| [tags_to_concept.json](tags_to_concept.json) | DART v3 expansion → Text Assistant → prose | DART v3 + instruction Qwen |
| [description_to_dart_v3.json](description_to_dart_v3.json) | Text Assistant → V3 Composer → DART expansion | Instruction Qwen + DART v3 |
| [photo_to_dart_v3.json](photo_to_dart_v3.json) | Image caption → assistant tags → DART v3 | Vision Qwen, two assistant passes + DART |
| [photo_to_moss_layout.json](photo_to_moss_layout.json) | Image caption → MOSS JSON, sharing Load CLIP | Full vision Qwen, two passes |
| [shared_vision_to_prose.json](shared_vision_to_prose.json) | Image caption → new scene concept, sharing Load CLIP | Full vision Qwen, two passes |
| [keywords_to_moss_layout.json](keywords_to_moss_layout.json) | Keywords → scene + MOSS object/text boxes | Instruction Qwen; no DART required |

The five combined graphs include a START HERE note on the canvas. A small [neutral demo image](../../assets/demo.png) is included; upload it in Load Image or choose your own photo. Image examples reference dart-vision-example.png for the local demo; on another installation, select/upload an image first.

## Before running

- Install this pack once. Disable the original ComfyUI-Dart installation; both packs share legacy class IDs.
- Local text assistance needs recent native Generate Text support and a complete Qwen generation model in text_encoders. Image to Text additionally needs vision weights.
- In shared-model examples, choose your installed full Qwen checkpoint in **Load CLIP**. Its output overrides both assistants' Automatic selectors. Use a general generation-capable loader type; the examples use stable_diffusion.
- DART v3 Preview E is gated. Accept the model's access terms and cache its files or configure normal Hugging Face authentication. This project does not include or bypass model access. CPU DART leaves GPU memory for image work.
- For MOSS JSON, set canvas width/height equal to your image latent dimensions. Connect the assistant **prompt** to the MOSS positive text encoder. **scene_json** is diagnostics, not the native prompt format.

## Make the examples yours

**Character caption replacement:** in Image to Text, set Character trigger to your training token. Instructions can say: `Use silver hair and green eyes instead of the original colors. Keep pose, clothing, framing, background and lighting. Output only the caption.` This edits text, not pixels, and does not load a LoRA.

**Photographic concept from tags:** set Text Assistant target to Natural language and mode to Concept. Ask for concrete camera, lighting, materials and texture rather than generic quality adjectives. Keep exact tags is for literal requirements, not creative instructions.

**Faithful reference conversion:** choose Preserve and avoid extra creative directions. DART expansion can still add detail; leave it out when a faithful caption is the goal.

**Layout editing:** copy a generated MOSS prompt into Edit MOSS JSON to adjust boxes/text without another assistant call. Clear the override to generate a fresh layout.

## Validation

Graph links, socket names, node availability and cycles are checked during development. The neutral image-to-text, keyword concept and MOSS layout paths have real local Qwen checks. The shared photo-to-layout graph is checked separately in the release validation. DART v1/v2/v3 have earlier CPU smoke checks. No gallery example claims a benchmark of final image quality or perfect semantic preservation.
