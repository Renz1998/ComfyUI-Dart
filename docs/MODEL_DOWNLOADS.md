# Model downloads

## Main Archmage → MOSS workflow

The [main workflow](../workflows/start-here/03-moss-full-workflow.json) is the supplied **Moss_Image_Zine_2 - DART Ideas**, with only its character LoRA removed. All other settings and connections are retained, including the accelerator LoRA, custom sampling/SLG, 3.7 MP portrait resolution. Archmage defaults to Local Qwen, sharing the connected encoder with MOSS. No API key is required. The workflow includes setup, download and control-description notes.

Required saved filenames and roles:

| File / link | Role / folder |
| --- | --- |
| [moss_image_base_bf16.safetensors](https://huggingface.co/Comfy-Org/MOSS-Image/resolve/main/diffusion_models/moss_image_base_bf16.safetensors?download=true) | Image generator; `models/diffusion_models/` |
| [Qwen3.5 9B INT8](https://huggingface.co/Comfy-Org/MOSS-Image/resolve/main/text_encoders/qwen3.5_9b_int8_convrot.safetensors?download=true) | Shared local assistant and MOSS encoder; save as `models/text_encoders/qwen3.5_9b_int8_convrot.safetensors`. |
| [flux2-vae_small.safetensors](https://huggingface.co/Comfy-Org/MOSS-Image/resolve/main/vae/flux2-vae_small.safetensors?download=true) | Latent-to-image decoder; `models/vae/` |
| [Lodestones DMD2 accelerator](https://huggingface.co/lodestones/MOSS-Image-Base-8-steps-dmd/resolve/main/lora_dmd2.safetensors?download=true) | Save in `models/loras/` and **rename to `lodestones-8-steps-dmd2-lora-moss.safetensors`**. SHA-256 verified identical to the supplied setup's local LoRA. The character LoRA remains removed. |

The graph retains `ManualSigmas` and `SkipLayerGuidanceDiTSimple`, both native ComfyUI nodes; update ComfyUI if missing. Do not replace the accelerator's manual schedule with the base-model settings accidentally. Model filename changes may require corresponding compatible settings.

The saved Archmage uses **Local Qwen** with the connected full encoder. OpenAI is optional; switch Assistant and add a key only if you want it. DART v3 access requirements are below. These links identify models; they do not install them automatically.

### Optional alternatives

| Download | Use / change |
| --- | --- |
| [MOSS Base INT8](https://huggingface.co/Comfy-Org/MOSS-Image/resolve/main/diffusion_models/moss_image_base_int8_convrot.safetensors?download=true) | Lower weight memory; save in `models/diffusion_models/` and select in Load Diffusion Model. |
| [Qwen3.5 9B BF16](https://huggingface.co/Comfy-Org/MOSS-Image/resolve/main/text_encoders/qwen3.5_9b_bf16.safetensors?download=true) | Higher weight memory; save in `models/text_encoders/` and select in Load CLIP. |
| [FLUX.2 small VAE](https://huggingface.co/Comfy-Org/MOSS-Image/resolve/main/vae/flux2-vae_small.safetensors?download=true) | Smaller VAE; save in `models/vae/` and select in Load VAE. |

## DART v3: random tag ideas

[DART v3 Preview E — model card and access terms](https://huggingface.co/p1atdev/dart-v3-sft-preview-E) · [Files](https://huggingface.co/p1atdev/dart-v3-sft-preview-E/tree/main)

DART is a tag continuation model by **p1atdev**. Connect **DART v3 Load** to **Generate**, and **Compose Prompt V3** to Generate's prompt input. Archmage screens known conflicts and develops a coherent subset of the generated scene candidates. Appearance settings and the selected style take priority. [How the tag input works](DART_SCENE_IDEAS.md).

The model is gated. Sign in to Hugging Face, accept its terms and authenticate on the computer running ComfyUI if needed. **DART v3 Load** downloads the model, tokenizer and configuration into the normal Hugging Face cache on first use. Do not put a lone DART safetensors file in `text_encoders`. Offline users can cache the complete repository or use Local model path and Local files only. CPU is the default to leave GPU memory for MOSS.

**New DART workflows use v3 only.** The multi-version loader, v1/v2 composers and v2 aspect helper are deprecated. Their IDs, options and execution remain for saved graphs. Generate, Config, Decode and tag utilities support v3 and stay available.

## Archmage without MOSS

For prompt-only workflows, [Qwen3.5 2B BF16](https://huggingface.co/Comfy-Org/Qwen3.5/resolve/main/text_encoders/qwen3.5_2b_bf16.safetensors?download=true) is the small native assistant fallback. Save it in `models/text_encoders/`. Archmage Automatic downloads a pinned copy once when no compatible encoder is available. Keep the matching **MOSS 9B** encoder for MOSS image conditioning; 2B is an assistant option.

OpenAI users need no local assistant weights, but MOSS still needs its diffusion model, encoder and VAE. Use the masked key panel; see [API setup](OPENAI_API.md). Optional checkpoint notes are in [Model choices](MODEL_CHOICES.md).
