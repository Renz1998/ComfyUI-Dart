"""ComfyUI descriptions and socket/widget help, kept separate from execution."""

INPUT_HELP = {
    "model": "Connect the DART_MODEL output of Dart Load. Use its matching tokenizer too.",
    "tokenizer": "Connect DART_TOKENIZER from the same Dart Load node as your model. It translates tags to and from that model's vocabulary.",
    "prompt": "Connect a Dart Compose Prompt node that matches the loaded model version. This contains DART control tokens, not an ordinary image prompt.",
    "seed": "Controls random variation. Keep the same seed and settings to repeat a result on the same setup. Greedy/Preserve modes can give the same result across different seeds.",
    "setting": "Optional sampling controls from Dart Generation Config. Leave disconnected to use DART's defaults.",
    "ban_tags": "Comma-separated tags to discourage during generation, e.g. text, watermark. Unknown/control tokens are ignored. Keep exact tags overrides this list.",
    "remove_tags": "Comma-separated known tags to remove after generation, e.g. blush, watermark. This edits the output; it does not guide the model while generating.",
    "keep_tags": "Append these exact tags after generation, keeping weights and LoRA syntax. Example: (red coat:1.2), <lora:my_style:0.8>. Keep takes priority over Avoid, bans and removal.",
    "animagine_order": "On: put people, characters and series before general details. Off: preserve the decoded model order. This changes text ordering, not the image model itself.",
    "copyright": "Series/franchise tags, e.g. vocaloid. Use original for an original character. You can connect Describe's copyright output.",
    "character": "Named character tags, e.g. hatsune miku. Leave blank for an unnamed subject. Use spaces rather than underscores.",
    "general": "Starting visual tags, e.g. 1girl, solo, red coat, rain. DART expands these. Connect Describe's general_tags output for natural-language input; put exact weights in Generate's Keep tags.",
    "rating": "Content category to steer DART: general is the least suggestive; sensitive, questionable and explicit allow progressively more mature tags. In v2, sfw combines general/sensitive and nsfw combines questionable/explicit. This is model guidance, not a guaranteed filter.",
    "aspect_ratio": "Steers tags toward the composition: square, tall/portrait or wide/landscape. Wallpaper and too/ultra options are more elongated. This does not set or resize the image's pixel dimensions.",
    "length": "Desired tag-list length, from very_short to very_long. This is approximate model guidance. Generation Config's max_new_tokens is the separate hard generation limit.",
    "identity": "V2 only. none allows creative additions; lax tries to keep the supplied subject's identity; strict is more restrictive and less creative. Start with lax when preserving a character matters.",
    "width": "Target image width in pixels. Used with height to choose a v2 aspect tag; no image is resized.",
    "height": "Target image height in pixels. Equal width/height produces square. This node does not set the image resolution.",
    "max_new_tokens": "Maximum extra tokens DART may generate. More allows longer output but takes longer. It does not include the input prompt or guarantee this many tags.",
    "min_new_tokens": "Minimum extra tokens before stopping is allowed. Usually leave at 0; forcing a high minimum can add unwanted tags. Must not exceed max_new_tokens.",
    "temperature": "0 selects deterministic decoding; lower nonzero values favor likely tags; higher values add variety. Start around 0.7 for sampling. top_p/top_k do not affect greedy decoding at 0.",
    "top_p": "Sampling probability cutoff. Lower values keep a smaller set of likely choices; 1 keeps the full distribution before other filters. Ignored when temperature is 0.",
    "top_k": "Sampling considers this many likely next tokens. Lower values are narrower; larger values allow more variety. Ignored when temperature is 0.",
    "num_beams": "1 is ordinary generation. More beams search more candidate continuations and use more memory/time; they are not automatically better for creative tags.",
    "token_ids": "DART's encoded tag sequence from Generate (Advanced). Use the matching tokenizer to decode it; these are not CLIP conditioning or image latents.",
    "skip_special_tokens": "On hides internal markers such as <general>. Leave on for an image prompt; turn off only to inspect the DART format.",
    "patterns": "Regular expressions, one per line, matched from the start of each vocabulary tag. Example: .*hair.* matches tags containing hair. Connect this output to Generate's ban_tags.",
    "device": "cpu leaves GPU memory for image generation. cuda uses your NVIDIA GPU. auto selects CUDA when available, otherwise CPU. DART's Transformers loader does not use ComfyUI's automatic offloader.",
    "dtype": "Number format for DART weights. auto uses float32 on CPU and a supported 16-bit format on CUDA. float32 uses more memory; bfloat16/float16 depend on hardware support.",
    "local_model_path": "Optional complete Transformers model directory on disk. Leave blank to use the selected Hugging Face model. Its DART version must match the selected profile.",
    "revision": "Hugging Face branch or commit to load. main follows the default branch; a commit SHA pins a specific model revision.",
    "local_files_only": "On: use only files already downloaded or supplied locally. Off: missing model files can be downloaded from Hugging Face; gated v3 needs accepted access and a local sign-in.",
}

ASSISTANT_HELP = {
    "canvas_width": "MOSS JSON only. Match your image latent width exactly, in pixels and multiples of 16. The model plans ordinary pixel boxes; this node converts to MOSS centered yxyx coordinates. This does not resize the latent.",
    "canvas_height": "MOSS JSON only. Match the image latent height in pixels, in multiples of 16. Layout positions depend on both dimensions. Change these when changing generation resolution.",
    "layout_json": "Optional MOSS JSON override. Leave blank for the assistant to plan a layout. To edit, copy the prompt output here and change captions, text or centered yxyx boxes. A nonempty override is validated and used directly WITHOUT running the assistant; other writing instructions and Keep tags are ignored. Width/height must still match.",
    "description": "Write a scene, keywords, or extra context for connected source_tags. Can be empty when source_tags is connected. Example: a candid night photograph. Put writing directions in Custom instructions.",
    "source_tags": "Connect Dart Generate or Dart Decode text here. These keywords become material for the scene. Choose Concept to invent an idea around them. Description can add context or stay empty. Keep exact tags is the separate literal-preservation control.",
    "custom_instructions": "Directions for style, interpretation and wording. Example: Turn the supplied tags into an interesting real photograph. Describe concrete camera, lighting and texture details. Do not use the words realistic or photorealistic. Output only the image prompt. Choose Natural language for prose. Instructions are model-guided; Keep exact tags still appends literal text.",
    "target": "DART tags: comma-separated tags. Anima hybrid: tags plus prose. MOSS prose and Natural language: only the scene description. MOSS JSON layout: native summary/items layout with object/text boxes; set its canvas dimensions to match generation. Choose Natural language for a photographic concept from tags. prompt can go to CLIP Text Encode; general_tags can go to a DART composer.",
    "mode": "Preserve translates the supplied scene; Expand adds modest lighting/background detail; Concept invents a coherent scene around keywords with setting, action and composition. Custom instructions can request creative changes. Additions are model-reported in scene_json. Concept uses seed-based sampling for variation.",
    "backend": "Local model uses an installed Qwen model inside ComfyUI; no separate server or API key. Chat server uses your configured compatible endpoint and reveals its settings. Start with Local model.",
    "local_model": "Automatic prefers a small general Qwen3-VL model already in text_encoders. Or select an installed filename. A connected generation-capable CLIP overrides this selector. No model downloads are triggered here.",
    "clip": "Optional full, generation-capable Qwen CLIP from the native loader. Overrides Local model selection. Image-only encoders such as Anima's base encoder may not generate useful replies.",
    "endpoint": "Chat server only. Base URL including /v1: LM Studio usually http://localhost:1234/v1; Ollama usually http://localhost:11434/v1. Local model mode ignores this field.",
    "model": "Chat server only. Exact model identifier shown by your server. This is not an image-checkpoint filename. It may stay blank in Local model mode.",
    "avoid": "Things the assistant should leave out, e.g. extra people, text, watermark. Exact matching tags are removed and this text is also returned as negative_prompt. Prose exclusions are model-guided; Keep exact tags takes priority.",
    "timeout": "Chat server only. Maximum seconds to wait for its HTTP reply. Increase for a slow server. It does not limit local-model execution time.",
    "api_key_env": "Chat server only. Name of an environment variable containing the key, e.g. MY_CHAT_KEY. Never paste the actual secret into this widget or a shared workflow. Leave blank if your local server needs no key.",
}

NODE_HELP = {
    "ImageBatchUpload": ("Click the drop area to browse local images, drop images onto the node, or use Choose folder for local image folders, including on RunPod. Use the thumbnail list to reorder/remove files. Process a list sequentially in one run, or advance Index between queued runs. Files are uploaded to ComfyUI input; saved workflows keep paths, not image bytes. Removing a thumbnail does not delete the server file. Keep Image to Text's Image in batch at 0.", ["Connect to Image to Text image. Separate images retain their own dimensions and are captioned sequentially.", "Matching input-relative filenames. Connect to Image to Text source_name to label reports.", "Number of selected images in this run.", "Selected-file list and selected/available counts."], {}),
    "ImageBatchSelector": ("Select a folder of images. One image per queued run advances Index using the native increment control. List mode lets ComfyUI map Image to Text sequentially over separate images without stacking their resolutions. Use Image to Text's Image in batch = 0.", ["Connect to Image to Text image. A native list of separate single-image tensors, processed sequentially.", "Matching relative filenames, in the same order as the image list. Can label downstream results.", "Number of images selected in this run, not the total folder count.", "Human-readable selected-file list and selected/available counts."], {}),
    "AppearanceOverrides": ("Optional dropdown/custom appearance recipe. Connect appearance to Image to Text or Text Assistant. Keep unchanged leaves a trait alone; Custom reveals your own value. This changes generated text, not image pixels.", ["Connect to either assistant's appearance input. One recipe can be shared by both assistants.", "Compiled plain writing instructions for inspection or use with another text tool."], {}),
    "ImageToText": ("Caption an image as prose, structured JSON or native MOSS layout. Connect Load Image and choose a megapixel budget and resize method. Auto dimensions use the processed image for MOSS; width/height can feed a latent node. Instructions edit the caption, not image content.", ["Caption, structured scene JSON or native MOSS JSON according to Output format. The description socket keeps its original position.", "Layout canvas width for MOSS JSON; processed image width for other formats. Connect to a latent width input.", "Layout canvas height for MOSS JSON; processed image height for other formats. Connect to a latent height input.", "Selected RGB image after pixel-budget resizing. Resizing does not apply the caption's requested character or appearance changes."], {
        "image": "Connect Load Image or any IMAGE output. This node sees the selected image and produces text; it does not alter image pixels.",
        "instructions": "Open writing instructions. Example: Replace the main subject with my character. Use silver hair and green eyes; omit the original hair color. Keep pose, clothing, setting and lighting. Output only the caption. Blank gives a faithful visual description. Changes are model-guided, so inspect the result.",
        "detail": "Detailed requests a rich visual caption; Concise requests a short paragraph. max_tokens separately limits output length. Inference is deterministic, so identical inputs usually repeat the caption.",
        "character_trigger": "Optional exact training trigger, e.g. my_character. The model uses it for the main subject. If omitted by the model, the node prepends it literally. This does not load a LoRA or identify a real person. Put appearance replacements in Instructions.",
        "image_index": "Which image in a batch to describe, starting at 0. Only this image is sent to the local vision model. An out-of-range index reports an error instead of silently selecting another image.",
        "max_tokens": "Caption output budget, not a word count. 1024 can suit prose; start with 4096 for structured JSON/MOSS layouts and increase if cut off. Larger limits can take longer.",
        "local_model": "Automatic prefers an installed general Qwen3-VL 4B. Requires full vision weights as well as text generation weights. An optional vision-capable CLIP input overrides this selector. Images are processed locally; no download or server request is made.",
        "clip": "Optional full vision-and-generation-capable Qwen CLIP from the native loader. Overrides Local model. Text-only or image-conditioning-only encoders cannot caption images.",
    }),
    "Loader": ("Load a DART tag-expansion model and its matching tokenizer. Connect both outputs to Generate. Pick a composer with the same version; CPU is a useful default alongside an image model.", ["DART model. Connect to Generate or Generate (Advanced) → model.", "Matching tag tokenizer. Connect to Generate and any decoder/filter nodes."], {"model": "DART version/profile. v1 and v2 use their matching composers; v2-moe uses the V2 composer. Preview E uses V3 and is experimental. This selects a tag model, not your image checkpoint."}),
    "Generate": ("Expand a few visual tags into a fuller image prompt. Connect a DART model, its tokenizer and the matching composer. Use Keep tags for text that must survive exactly.", ["Generated tags. Connect to CLIP Text Encode, Preview as Text, or Describe Image → source_tags to develop a prose concept."], {}),
    "GenerateAdvanced": ("Generate an encoded DART sequence for advanced filtering/reordering. Add Dart Decode afterward to get readable text.", ["Encoded DART sequence. Connect to Dart Decode or a token-processing node."], {}),
    "ComposePrompt": ("Build the internal prompt for DART v1. Connect this output to Generate → prompt with dart-v1-sft loaded.", ["Internal v1 control prompt. Connect to Generate → prompt; do not feed this directly to image text encoding."], {}),
    "ComposePromptV2": ("Build a prompt for DART v2 or v2-MoE. Choose composition and identity guidance, then connect to Generate → prompt.", ["Internal v2 control prompt. Use with a v2 model and tokenizer."], {}),
    "ComposePromptV3": ("Build a prompt for DART v3 Preview E. Start with general rating, square composition and medium length. Connect to Generate with the v3 profile.", ["Internal v3 control prompt. Use with v3 Preview E, not a v1/v2 profile."], {}),
    "GetAspectRatio": ("Convert width/height into a DART v2 composition tag. Connect to Compose Prompt V2 → aspect_ratio. It does not resize images and its output is not the v3 option set.", ["V2 aspect-ratio choice. Connect to the V2 composer's aspect_ratio input."], {}),
    "GenerationConfig": ("Optional controls for DART expansion. Connect to Generate → setting. Start with one beam, zero minimum tokens, and a temperature of 0 for deterministic output or about 0.7 for variety.", ["DART generation settings. Connect to Generate or Generate (Advanced) → setting."], {}),
    "BanTagsFromRegex": ("Find vocabulary tags by regular expression and ban them during generation. Use one expression per line; this does not edit an already generated prompt.", ["Comma-separated banned tags. Connect to Generate → ban_tags."], {}),
    "Decode": ("Turn an encoded DART sequence into readable text. Use the tokenizer that generated the sequence.", ["Decoded text. With special tokens hidden, connect to Preview as Text or image text encoding."], {}),
    "DecodeBySplitedParts": ("Decode a DART sequence into separate categories for custom prompt formatting. Missing/truncated sections can be empty.", ["Content-rating text.", "Series/franchise tags.", "Named-character tags.", "Subject-count tags, such as 1girl or 1boy.", "Remaining visual tags: clothing, action, setting, lighting, etc."], {}),
    "RearrangedByAnimagine": ("Reorder encoded tags into people, character, series, general details and rating. Connect the result to Decode; this does not change your image checkpoint.", ["Reordered encoded sequence. Connect to Dart Decode using the same tokenizer."], {}),
    "RemoveTagToken": ("Remove encoded tag sequences before decoding. Use the same tokenizer; internal control tokens are protected.", ["Filtered encoded sequence. Connect to Dart Decode or another token-processing node."], {}),
    "DescribeImage": ("Describe your image or connect generated source tags, then click Run. Concept invents a scene from keywords; Custom instructions control its style and wording. Natural language outputs prose. Local model + Automatic uses installed Qwen. The result appears here.", ["Formatted prompt, or native JSON when target is MOSS JSON layout. Connect to the image model positive text encoder. This is not a DART control prompt.", "Unweighted visual tags. Connect to a DART composer → general, then Generate. Exact weights belong in Generate's Keep tags.", "Detected series/franchise, or original. Connect to a DART composer → copyright.", "Detected named character, or blank. Connect to a DART composer → character.", "Your Avoid text. Connect to your image workflow's negative text encoder if it supports negative prompts.", "Debug scene JSON, source tags and reported additions; for MOSS includes compiled moss_layout and canvas dimensions. Connect to Preview as Text to inspect; this is not image conditioning."], ASSISTANT_HELP),
}


NODE_HELP['LoaderV3'] = (
    'Load p1atdev DART v3 Preview E for tag expansion. Pair with Compose Prompt V3. '
    'Accept its Hugging Face access terms before downloading. CPU leaves GPU memory for images.',
    NODE_HELP['Loader'][1],
    {**NODE_HELP['Loader'][2], 'model': 'DART v3 Preview E is the supported entry point for new workflows. Accept its model access terms on Hugging Face; files download into the normal HF cache.'},
)


def attach_help(node_classes):
    for name, node_class in node_classes.items():
        description, outputs, overrides = NODE_HELP[name.removeprefix("DanbooruTagsTransformer")]
        original = node_class.INPUT_TYPES
        if name.endswith(("DescribeImage", "ImageToText")):
            outputs = list(outputs) + ["Appearance feedback status: ok, corrected, edited, warning, blocked or unchecked. Edited means Prompt Mage applied a selected size phrase, not model compliance. Connect to Preview as Text or conditional logic.",
                                       "JSON diagnostics with missing/conflicting phrases, output locations, attempt count and the actual generated prompt. Available even when data outputs are blocked."]

        def input_types(cls, original=original, overrides=overrides):
            schema = original()
            for group in ("required", "optional"):
                for field, spec in schema.get(group, {}).items():
                    tooltip = overrides.get(field, INPUT_HELP.get(field))
                    if tooltip:
                        options = dict(spec[1]) if len(spec) > 1 else {}
                        options["tooltip"] = tooltip
                        schema[group][field] = (spec[0], options, *spec[2:])
            return schema

        node_class.INPUT_TYPES = classmethod(input_types)
        node_class.DESCRIPTION = description
        node_class.OUTPUT_TOOLTIPS = tuple(outputs)
