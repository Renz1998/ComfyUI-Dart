> Legacy setup guide. For new workflows start with [Archmage](ARCHMAGE_BETA.md).

# Prompt Mage — Quickstart

Prompt Mage is an expanded fork of [nkchocoai/ComfyUI-Dart](https://github.com/nkchocoai/ComfyUI-Dart). It keeps the original node identifiers and adds DART v3, local text/vision assistants, custom instructions and MOSS layouts. Do not install two copies of Dart together: they register the same existing node names.

Source: [Renz1998/ComfyUI-Prompt-Mage](https://github.com/Renz1998/ComfyUI-Prompt-Mage). Start with the [workflow gallery](../workflows/next/README.md).

## Help and appearance

Hover a control or socket for its purpose, option meanings, examples, and wiring advice. Node descriptions explain the complete step. Each DART node has a color-coded guide card: teal for the assistant, blue for loaders, amber for composers, violet for generation, and slate for utilities. Click its **?** button for a short guide. The card shows Working during execution and Done or Check Input afterward. Motion is limited to execution/completion and respects the browser's reduced-motion preference. Right-click a node and choose **Disable Mage design** to return to its previous appearance.

## What DART does

DART predicts more image tags from tags you supply. For example, `1girl, solo, red hair` can become a longer list describing a plausible scene. It can invent details. It is not a conversational assistant.

The separate **Prompt Mage · Text Assistant** node uses a local Qwen model to interpret ordinary descriptions. You can use its prompt directly, or send its tag outputs through DART for further expansion. A chat server is an optional alternative.

## Installation

1. Put this folder under `ComfyUI/custom_nodes/prompt-atelier` (replace or disable any older Dart installation first).
2. Use your ComfyUI Python environment to install `requirements.txt` if needed. Keep its existing Torch build. The development version was checked with Python 3.13.14, Torch 2.14.1+cu130, and Transformers 5.17.0.
3. Restart ComfyUI and load a workflow from `workflows/next/`.

The original project's GPL-3.0 license remains in effect. Registry publication is a separate step; see [PUBLISHING.md](../PUBLISHING.md). Creator/model attribution is in [CREDITS.md](../CREDITS.md).

## Try v3 without a chat server

Load **dart_v3_tags.json**, change the general tags, and click Run. It only generates text, so no image checkpoint is needed. The generated prompt appears in Preview as Text and can be connected to your image workflow's text-encoding node.

The loader defaults to CPU/float32 to leave GPU memory for image generation. CUDA and automatic device/dtype are optional. CUDA models loaded through Transformers are not managed by ComfyUI's automatic offloader; use CPU when GPU memory is tight. Removing an unused loader and clearing the execution cache releases its model.

V3 is `p1atdev/dart-v3-sft-preview-E`. Hugging Face requires accepted access conditions and an authenticated local sign-in. The loader uses Hugging Face's existing authentication; it has no token widget. After the first download, `local_files_only` supports cached operation. `local_model_path` can point at a complete local Transformers model directory matching the selected DART version. `revision` can pin a Hub commit.

Preview E uses a WordLevel tokenizer: known tags are separate tokens. It may not understand an arbitrary phrase. Put exact required text, weights, or LoRA syntax in **keep_tags**, which appends it verbatim after generation. If a tag appears in both Keep and Remove/Ban, Keep wins. Required text is preserved syntactically; this does not guarantee that an image model obeys it. Temperature zero selects deterministic greedy decoding (or beam search when beams > 1). A fixed sampling seed repeats within the same software/hardware setup; cross-device identity is not guaranteed.

## Use ordinary descriptions

Load **describe_image.json**, leave **backend** at **Local model** and **local_model** at **Automatic**, write your description, and click Run. The node shows its result directly. No server, API key, or download is needed when a supported Qwen model is already installed in `text_encoders`.

Automatic prefers an installed Qwen3-VL 4B general model over larger models or specialized upsamplers. This version was tested with `qwen3vl_4b_int8_convrot.safetensors` using ComfyUI's native loading, text generation, and memory management. An optional generation-capable **CLIP** input overrides the filename selection. Use the native loader's general `stable_diffusion` type for this assistant; an image-specific loader can disable text generation. ComfyUI must include the native Generate Text node (`comfy_extras.nodes_textgen`). Server fields stay hidden in local mode; switching Assistant to Chat server reveals them.

Other controls:

- **backend**: Local model by default. Select Chat server only when you have a server configured.
- **local_model**: Automatic, or an installed model filename.
- **endpoint** and **model**: advanced controls used only by Chat server. LM Studio commonly uses `http://localhost:1234/v1`; local Ollama uses `http://localhost:11434/v1`. Enter its exact model identifier.
- **description**: write what you want normally.
- **target**: DART tags, Anima hybrid, MOSS prose, or Natural language.
- **mode**: Preserve requests faithful conversion; Expand allows modest additions; Concept invents a coherent scene around keywords.
- **keep_tags**: optional literal tags/weights to retain.
- **avoid**: optional exclusions, also returned as a negative prompt.

No weights are bundled or downloaded automatically. The local backend uses existing model files and makes no network requests. If no suitable model is installed, the error explains what to add or connect. For the optional Chat server backend, text is sent only when the node runs, to the configured server. Keep a localhost endpoint for local processing. For a server requiring a key, enter an environment-variable name in `api_key_env`; do not put a secret in the workflow.

The output is editable before you use it. **scene_json** retains the original description and the model's reported additions. Preserve/Expand and prose exclusions are model instructions, not hard semantic guarantees. Exact matching excluded tags are removed from the tag list. Common aliases are normalized (woman/man to count tags when a count is missing, rainy to rain); existing counts such as 2girls take precedence. Tags are not checked against a complete Danbooru vocabulary. This version accepts text only; reference images and persistent conversation history are future work.

To add DART expansion, connect **general_tags**, **copyright**, and **character** to the matching inputs of a DART composer. Connect the composer to Dart Generate. Copy any weighted/literal requirements into Generate's **keep_tags** as well. The assistant's `prompt` is already suitable for direct text encoding; it is not a serialized DART control prompt.

Dragging a Dart socket onto empty canvas now shows relevant nodes. For example, **prompt** offers CLIP Text Encode and Preview as Text, **general_tags** offers the three DART composers, and model/tokenizer sockets offer the corresponding loader/generator nodes. Selecting a suggestion connects the named input automatically. Other plugins' drag menus are unchanged; More compatible nodes opens the normal menu.

Anima and MOSS outputs are text-formatting modes. Image quality has not been benchmarked. Variant-specific Anima quality prefixes remain future work. MOSS JSON layouts are available through the dedicated target below.

## Turn generated tags into a concept

Connect **Dart Generate → Describe Image source_tags**. Dragging Generate's text output offers Describe Image and wires this input automatically. Advanced workflows can use Dart Decode or Decode By Parts → general instead. Avoid connecting Describe back into the same Generate node: that creates a workflow cycle.

1. Set **target** to **Natural language** and **mode** to **Concept**.
2. Leave **description** empty, or add context such as `a candid street photograph`.
3. Write your directions in **Custom instructions**, for example:

   > Turn the supplied tags into an interesting real photograph. Develop a coherent setting and action. Describe concrete light, camera framing, materials and texture. Do not use the words realistic or photorealistic. Output only the image prompt, without a heading or commentary.

4. Run. Use **prompt** for text encoding; **scene_json** contains the source tags and reported additions for inspection.

The model follows custom instructions in both local and chat-server modes. The app still requests structured JSON internally so all six outputs keep working; Natural language extracts only the scene description. Custom instructions can request creative reinterpretation even in Preserve mode. Keep exact tags appends literal text and takes priority, so leave it empty when you want prose only. Word exclusions in custom instructions are model-guided; inspect the result.

## Native MOSS JSON layouts

MOSS accepts structured layout JSON as its positive prompt. The [official layout guide](https://github.com/OpenMOSS/MOSS-Image/blob/main/USERGUIDE.md#layout-prompts-experimental) documents `summary`, `items`, centered pixel coordinates and `yxyx` box order. This is different from the assistant debug `scene_json` output.

Select **MOSS JSON layout** as the target. Set **MOSS canvas width/height** to the exact dimensions used by your image latent. Describe subjects, positions and exact visible text, or connect generated tags. Custom instructions can specify media, composition and typography. Run and connect **prompt** to your MOSS positive text encoder. No JSON-writing is needed.

The assistant plans boxes using ordinary top-left pixel coordinates. The node validates and converts them to native `abs_centralized` `[y_min,x_min,y_max,x_max]` boxes. It rejects empty/inverted/out-of-bounds boxes and malformed text items. For an invalid generated draft it requests one correction; a manual override is never rewritten. Matching dimensions matter: on a 1024-square canvas, each axis ranges from -512 to +512. Positions guide the model; OpenMOSS documents layout prompting as experimental.

For manual changes, copy the resulting **prompt** into **Edit MOSS JSON** and edit captions, exact text or boxes. A nonempty override bypasses the assistant entirely and outputs validated JSON; writing instructions, Keep tags and automatic generation are ignored until you clear it. This makes rerunning an edited layout inexpensive. Keep dimensions consistent when editing. `scene_json` includes the compiled layout and dimensions for inspection. The six existing socket positions stay unchanged.

Example: `A minimalist travel poster with a blue mountain below and the exact title EXPLORE at the top.` Set 1024×1024 and ask for cream paper, dark blue type and space between the title and mountain. Keep exact tags, when generating automatically, are stored inside the summary caption so they cannot break JSON syntax.

## Describe an actual image

Add **Prompt Mage · Image to Text**, connect **Load Image → image**, and leave **Local model** at **Automatic**. Run for a detailed visual caption, shown directly on the node. It uses your installed full Qwen vision model through ComfyUI. This node processes the selected image locally; it does not edit its pixels.

Use the open **Instructions** box for changes, for example:

> Replace the main subject with my character. Use silver hair and green eyes instead of the original colors. Keep the pose, clothing, background, framing and lighting. Output only a detailed image caption.

Put an exact training token in **Character trigger**, such as `my_character`. The model is asked to use it for the main subject. If it omits the literal token, the node prepends it. The trigger does not load a LoRA; load your character model in your image workflow separately. Attribute changes follow the instructions given to the vision model, so inspect the result.

**Detailed/Concise** controls the requested caption length. **Caption token limit** sets its output budget. **Image in batch** chooses one image, starting at index 0. An optional full vision-capable **CLIP** overrides the model selector. Text-only weights cannot inspect images; use a full Qwen vision checkpoint.

Connect **description** directly to your positive text encoder, or to **Dart Describe Image → description** for tags, a concept, or a MOSS JSON layout. Dragging the image input offers Load Image; dragging the caption output offers the text assistant and text encoders. This is a separate node, so existing text-assistant workflows keep their inputs and output positions.

## Validation

Run `python tests/test_regressions.py` in an environment with Torch and Transformers. The 37 tests include local/backend routing, tag aliases, settings isolation, RNG restoration, zero-temperature mode, control-token protection, sequence removal, retained weights, aspect boundaries, truncated decoding, response validation, and a temporary loopback HTTP server. Run `node tests/test_connections.mjs` and `node tests/test_menu.mjs` to check drag suggestions, exact connection targets, and backend control visibility. A separate real local-model run verified description conversion with Qwen3-VL 4B; semantic output quality is still model-dependent.

A separate real-model smoke run used v3 revision `80b8bb0f763f14394551b1c542ac368c7e960275`, seed 7, CPU, and repeated generation. See the accompanying validation report. CI is configured for Transformers 4.46.3 and 5.17.0; local validation does not imply that the remote CI jobs have run.

Real model checks also passed for v1-sft and v2-sft. The legacy tokenizer subclass was replaced by direct loading of the published WordLevel vocabulary after detecting incorrect v1 tokenization on Transformers 5.17.0. No tokenizer remote code is needed. Repeat the checks with `python tests/smoke_model.py --model v3` (or `v1`/`v2`); this explicitly downloads a model if not cached. Add `--local-files-only` to prevent downloads. These checks cover runtime behavior, not image quality or subjective prompt quality. V2-MoE has not had a real-model smoke check in this run.
