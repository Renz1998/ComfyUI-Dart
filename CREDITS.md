# Credits and provenance

Prompt Mage is maintained by [Renz1998](https://github.com/Renz1998). It extends the original ComfyUI-Dart node pack with local language/vision assistance, prompt design, MOSS layout compilation, workflow examples and interface improvements. The new name does not imply authorship of the underlying models.

| Contribution | Creator / source |
| --- | --- |
| Original ComfyUI-Dart implementation and DART node foundation | [nkchocoai and contributors](https://github.com/nkchocoai/ComfyUI-Dart) |
| DART model family, tokenizer formats and model training | [p1atdev](https://huggingface.co/p1atdev): [v1-sft](https://huggingface.co/p1atdev/dart-v1-sft), [v2-sft](https://huggingface.co/p1atdev/dart-v2-sft), [v2-moe-sft](https://huggingface.co/p1atdev/dart-v2-moe-sft), [v3 Preview E](https://huggingface.co/p1atdev/dart-v3-sft-preview-E) |
| Qwen language/vision models | [Qwen team](https://huggingface.co/Qwen), including [Qwen3-VL 4B Instruct](https://huggingface.co/Qwen/Qwen3-VL-4B-Instruct); checkpoint conversion authors retain their own credits |
| MOSS-Image model and native layout format | [OpenMOSS team](https://github.com/OpenMOSS/MOSS-Image), [layout guide](https://github.com/OpenMOSS/MOSS-Image/blob/main/USERGUIDE.md) |
| Native model loading, text generation, offloading and graph frontend | [ComfyUI contributors](https://github.com/Comfy-Org/ComfyUI) |
| Transformers model runtime | [Hugging Face and contributors](https://github.com/huggingface/transformers) |

## Source and models

The original [GPL-3.0 LICENSE](LICENSE) is retained unchanged for this derived node pack. Git history preserves the upstream source and subsequent changes. Model weights are not bundled; the software license does not replace each model's own license, access conditions or attribution. Refer to the specific model/checkpoint card before redistribution. MOSS-Image is a downstream target, not a model trained by this project.

The Anima hybrid and MOSS prose options are formatting choices, not endorsements or renamed model releases. Prompt Mage is an independent community project.
