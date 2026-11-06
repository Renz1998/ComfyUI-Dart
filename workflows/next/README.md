# Prompt Mage workflow gallery

These are complete **text-processing graphs** you can drag into ComfyUI. They create prompts for an existing image-generation workflow; diffusion checkpoints, samplers and image saving are deliberately left to that workflow. Existing DanbooruTagsTransformer node IDs remain compatible.

## Choose a starting point

Start with an Archmage example. Other assistant examples are retained as legacy workflows: Scene Composer, Text Assistant and Image to Text are deprecated but remain compatible. Upload and DART tools are active.


| Example | Pipeline | Models / cost |
| --- | --- | --- |
| [archmage_character_scene.json](archmage_character_scene.json) | Appearance Overrides → Archmage; everyday-photo style | Full local Qwen; one scene pass |
| [archmage_beta_compare.json](archmage_beta_compare.json) | Shared Appearance Overrides → Scene Composer beside Archmage Beta | Full local Qwen; compare prose with added canvas context |
| [archmage_beta_thinking_moss.json](archmage_beta_thinking_moss.json) | Thinking-enabled landscape layout example | Compatible full Qwen; 8192 tokens per stage, slower |
| [archmage_beta_text_moss.json](archmage_beta_text_moss.json) | Text concepts → Archmage Beta → native MOSS JSON | Full local Qwen; scene pass plus layout conversion |
| [archmage_beta_reference_moss.json](archmage_beta_reference_moss.json) | Upload Images → Archmage Beta reference layout | Full vision Qwen; upload your images first |
| [random_character_scenes.json](random_character_scenes.json) | Appearance Overrides → Scene Composer; empty concepts invents a scene | Full local Qwen; one prose pass |
| [random_scene_to_tags.json](random_scene_to_tags.json) | Character scene → experimental vocabulary tags in Faithful mode | Full local Qwen; inspect tag diagnostics |
| [keywords_to_concept.json](keywords_to_concept.json) | Keywords → Text Assistant → photographic concept | Full instruction Qwen; one assistant pass |
| [describe_image.json](describe_image.json) | Description → tags + prose + debug preview | Full instruction Qwen; one pass |
| [upload_images_to_captions.json](upload_images_to_captions.json) | Upload multiple files → thumbnails → sequential captions or one per queue | Full vision model; upload images before running |
| [image_to_text.json](image_to_text.json) | Load Image → Image to Text caption | Full vision Qwen; one pass |
| [folder_one_per_queue.json](folder_one_per_queue.json) | Folder → one caption per queued run; index advances | Full vision model; one image per run |
| [folder_caption_list.json](folder_caption_list.json) | Folder → native image list → sequential captions | Full vision model; up to Max images per run |
| [image_to_structured_json.json](image_to_structured_json.json) | Load Image → structured scene JSON with pixel-budget resize | Full vision Qwen; one pass |
| [image_to_moss_json_auto.json](image_to_moss_json_auto.json) | Load Image → native MOSS JSON, automatic canvas size + dimension outputs | Full vision Qwen; one pass |
| [appearance_text_assistant.json](appearance_text_assistant.json) | Appearance Overrides → Text Assistant, silver hair/green eyes and exact trigger | Full instruction Qwen |
| [appearance_image_to_moss.json](appearance_image_to_moss.json) | Optional appearance recipe + image → MOSS JSON, automatic size and model offload | Full vision model; choose your desired traits |
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

- Folder examples use Image Batch Selector. Choose a server folder, connect image to Image to Text and filename to source_name (already wired in these examples), and keep Image in batch at 0. One image per queued run uses the native increment control: queue several runs to advance through files. All selected images as list processes up to Max images sequentially in one run; it holds decoded images in CPU memory, so use one-per-queue for large folders. Different image sizes are supported. Custom folder is a path on the ComfyUI server, including on RunPod. The filename labels reports; it is not included in the caption prompt.

- For the direct vision JSON examples, connect/upload an image and choose a megapixel budget. MOSS defaults to From processed image, so no Get Image Size node is required. Connect width/height to your latent and description to MOSS positive text encoding. The image output is resized RGB, without caption-requested appearance edits. Structured JSON is a general scene record; choose MOSS JSON layout for native MOSS conditioning.
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
