# Model downloads

## Main Archmage → MOSS workflow

Start with [03 · Main Archmage workflow](../workflows/start-here/03-moss-full-workflow.json), the public default version of the Zine setup. No character LoRA, accelerator LoRA, private checkpoint or extra node pack is required. Use a recent ComfyUI with native MOSS and text-generation support.

Download these **three files**, keeping the filenames. Folder paths are relative to your **ComfyUI** directory. Refresh model lists after adding them, then select each filename in its loader.

| Model / download | What it does | Save in |
| --- | --- | --- |
| [MOSS-Image Base BF16](https://huggingface.co/Comfy-Org/MOSS-Image/resolve/main/diffusion_models/moss_image_base_bf16.safetensors?download=true) | The image generator: interprets the prompt and creates the image latent. | `models/diffusion_models/` |
| [Qwen3.5 9B INT8](https://huggingface.co/Comfy-Org/MOSS-Image/resolve/main/text_encoders/qwen3.5_9b_int8_convrot.safetensors?download=true) | MOSS's text encoder and the shared local Archmage assistant. Its CLIP output feeds both. INT8 reduces weight memory compared with BF16. | `models/text_encoders/` |
| [FLUX.2 VAE](https://huggingface.co/Comfy-Org/MOSS-Image/resolve/main/vae/flux2-vae.safetensors?download=true) | Decodes the generated latent into an image. | `models/vae/` |

These are the [Comfy-Org MOSS repackaged files](https://huggingface.co/Comfy-Org/MOSS-Image), derived from the [OpenMOSS models](https://huggingface.co/OpenMOSS-Team/MOSS-Image-Base). Review the source cards and licenses. File size does not establish peak VRAM usage; resolution, runtime and offloading also matter.

**Base settings:** 1 MP portrait, 50 steps, Euler, CFG 3, shift 5, full denoise. Thinking is off for the first run. The [OpenMOSS base guide](https://github.com/OpenMOSS/MOSS-Image/blob/main/USERGUIDE.md#inference-parameters) explains sampling choices. Layout JSON is experimental; switch to Prose to compare without changing models or sampling. This starter uses zeroed negative conditioning and no SLG: a simple baseline, rather than every upstream pipeline feature.

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
