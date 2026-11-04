# Dart Next: first development version

This is a local development fork of [nkchocoai/ComfyUI-Dart](https://github.com/nkchocoai/ComfyUI-Dart). It keeps the old node identifiers and adds experimental v3 and a description assistant. Do not install two copies of Dart together: they register the same existing node names.

Development source: [Renz1998/ComfyUI-Dart](https://github.com/Renz1998/ComfyUI-Dart/tree/feature/modern-dart-assistant), branch `feature/modern-dart-assistant`.

## What DART does

DART predicts more image tags from tags you supply. For example, `1girl, solo, red hair` can become a longer list describing a plausible scene. It can invent details. It is not a conversational assistant.

The separate **Dart Describe Image** node asks a configured chat model to interpret ordinary descriptions. You can use its prompt directly, or send its tag outputs through DART for further expansion.

## Installation

1. Put this folder under `ComfyUI/custom_nodes/ComfyUI-Dart` (replace or disable any older Dart installation first).
2. Use your ComfyUI Python environment to install `requirements.txt` if needed. Keep its existing Torch build. The development version was checked with Python 3.13.14, Torch 2.14.1+cu130, and Transformers 5.17.0.
3. Restart ComfyUI and load a workflow from `workflows/next/`.

The original project's GPL-3.0 license remains in effect. This development package is not published to the Comfy registry and has no configured publisher identity.

## Try v3 without a chat server

Load **dart_v3_tags.json**, change the general tags, and click Run. It only generates text, so no image checkpoint is needed. The generated prompt appears in Preview as Text and can be connected to your image workflow's text-encoding node.

The loader defaults to CPU/float32 to leave GPU memory for image generation. CUDA and automatic device/dtype are optional. CUDA models loaded through Transformers are not managed by ComfyUI's automatic offloader; use CPU when GPU memory is tight. Removing an unused loader and clearing the execution cache releases its model.

V3 is `p1atdev/dart-v3-sft-preview-E`. Hugging Face requires accepted access conditions and an authenticated local sign-in. The loader uses Hugging Face's existing authentication; it has no token widget. After the first download, `local_files_only` supports cached operation. `local_model_path` can point at a complete local Transformers model directory matching the selected DART version. `revision` can pin a Hub commit.

Preview E uses a WordLevel tokenizer: known tags are separate tokens. It may not understand an arbitrary phrase. Put exact required text, weights, or LoRA syntax in **keep_tags**, which appends it verbatim after generation. If a tag appears in both Keep and Remove/Ban, Keep wins. Required text is preserved syntactically; this does not guarantee that an image model obeys it. Temperature zero selects deterministic greedy decoding (or beam search when beams > 1). A fixed sampling seed repeats within the same software/hardware setup; cross-device identity is not guaranteed.

## Use ordinary descriptions

Load **describe_image.json**. Start a compatible chat server, then fill in:

- **endpoint**: LM Studio commonly uses `http://localhost:1234/v1`; local Ollama uses `http://localhost:11434/v1`.
- **model**: the exact model identifier displayed by that server. Use an instruction/chat model; Qwen3-4B-Instruct-2507 is one baseline to compare, not a tested default here.
- **description**: write what you want normally.
- **target**: DART tags, Anima hybrid, or MOSS prose.
- **mode**: Preserve requests faithful conversion; Expand allows modest additions.
- **keep_tags**: optional literal tags/weights to retain.
- **avoid**: optional exclusions, also returned as a negative prompt.

No chat server or assistant model is bundled or started automatically. This node supports a chat-completions endpoint; it does not turn an image model's CLIP encoder into a chatbot. Text is sent only when the node runs, to the configured server. Keep a localhost endpoint for local processing. For a server requiring a key, enter an environment-variable name in `api_key_env`; do not put a secret in the workflow.

The output is editable before you use it. **scene_json** retains the original description and the model's reported additions. Preserve/Expand and prose exclusions are model instructions, not hard semantic guarantees. Exact matching excluded tags are removed from the tag list. Tags are not checked against a complete Danbooru vocabulary. This version accepts text only; reference images and persistent conversation history are future work.

To add DART expansion, connect **general_tags**, **copyright**, and **character** to the matching inputs of a DART composer. Connect the composer to Dart Generate. Copy any weighted/literal requirements into Generate's **keep_tags** as well. The assistant's `prompt` is already suitable for direct text encoding; it is not a serialized DART control prompt.

Anima and MOSS outputs are text-formatting modes. Image quality has not been benchmarked. Variant-specific Anima quality prefixes and MOSS layout JSON are future additions.

## Validation

Run `python tests/test_regressions.py` in an environment with Torch and Transformers. Tests cover settings isolation, RNG restoration, zero-temperature mode, control-token protection, sequence removal, retained weights, aspect boundaries, truncated decoding, old workflow node names, response validation, and an HTTP request to a temporary loopback server. The loopback server returns a fixture, so it checks the connection protocol rather than LLM quality.

A separate real-model smoke run used v3 revision `80b8bb0f763f14394551b1c542ac368c7e960275`, seed 7, CPU, and repeated generation. See the accompanying validation report. CI is configured for Transformers 4.46.3 and 5.17.0; local validation does not imply that the remote CI jobs have run.

Real model checks also passed for v1-sft and v2-sft. The legacy tokenizer subclass was replaced by direct loading of the published WordLevel vocabulary after detecting incorrect v1 tokenization on Transformers 5.17.0. No tokenizer remote code is needed. Repeat the checks with `python tests/smoke_model.py --model v3` (or `v1`/`v2`); this explicitly downloads a model if not cached. Add `--local-files-only` to prevent downloads. These checks cover runtime behavior, not image quality or subjective prompt quality. V2-MoE has not had a real-model smoke check in this run.
