# Caption models and exact wording

Prompt Mage does not filter the phrase `gigantic breasts`. A model can still omit or paraphrase requested attributes. A low refusal rate does not establish exact wording, caption accuracy, schema compliance, or good image conditioning.

## Requested local checkpoint

[mdevoz/qwen3.5_9b_ultra_uncensored_heretic_int8_convrot](https://huggingface.co/mdevoz/qwen3.5_9b_ultra_uncensored_heretic_int8_convrot) currently has no model card. Its name alone does not establish provenance, refusal behavior, or compatibility. We downloaded only its requested safetensors file, verified the publisher's SHA-256, found vision tensors, and successfully tested local ComfyUI captioning and MOSS layout output. In a synthetic clothed-adult wording test, raw model output required a correction before preserving the selected size phrase. This is a narrow test, not an uncensored benchmark or a guarantee for other images.

Choose this filename explicitly in Image to Text's Local model selector. Automatic still prefers an installed small general model. Assistant captioning and the encoder used for diffusion conditioning are different roles: do not assume an arbitrary caption model is a valid replacement for your MOSS conditioning encoder.

## Alternatives worth evaluating

- [llmfan46/Qwen3.5-9B-ultra-uncensored-heretic](https://huggingface.co/llmfan46/Qwen3.5-9B-ultra-uncensored-heretic) is published as an image/text model in Transformers format. That does not establish its relationship to the mdevoz conversion or prove better behavior in this node; it is not a verified drop-in native ComfyUI conversion here.
- [HauhauCS/Qwen3.5-9B-Uncensored-HauhauCS-Aggressive](https://huggingface.co/HauhauCS/Qwen3.5-9B-Uncensored-HauhauCS-Aggressive) publishes a zero-refusal test claim. We have not independently verified it. Its card documents GGUF files and a separate vision projector for compatible runtimes. Those files are not a drop-in replacement for this node's native safetensors loader. Do not download them expecting identical integration.
- For caption accuracy, the [OpenMOSS guide](https://github.com/OpenMOSS/MOSS-Image/blob/main/USERGUIDE.md#image-captioning) recommends Gemma 4, Qwen3.5 27B or 35B-A3B. This is an accuracy recommendation, not an assurance about refusals or literal trait wording. Larger models also need suitable runtime and memory support.

## Predictable size wording without a model claim

Appearance Overrides → Apply exact breast-size wording performs an explicit caption edit for an identifiable target. It can replace a weaker size phrase or add the selected attribute. It does not remove model policies, rewrite explicit refusals into claimed compliance, alter source pixels, or guarantee the image generator follows the final prompt. Ambiguous subjects remain unconfirmed.

The report distinguishes model-generated wording from Prompt Mage's post-edit: `model_output` retains the text before the size edit, `post_edits` records changes, and `output` is the actual downstream prompt. Turn this option off when comparing models' own wording. Keep Warn and continue or choose Block downstream according to whether incomplete overrides should stop dependent processing.
