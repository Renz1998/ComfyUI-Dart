"""Use ComfyUI's model loader, text generation and offloading for local assistance."""

import json
import logging
import re

from .assistant import scene_request, parse_scene
from .memory import offload_after


def local_models():
    try:
        import folder_paths
    except ImportError:
        return []
    return [name for name in folder_paths.get_filename_list("text_encoders")
            if any(part in name.lower() for part in ("qwen3vl", "qwen3-vl", "qwen3.5", "qwen35"))]


def select_model(names):
    if not names:
        raise ValueError("No local assistant model found. Add a full Qwen3-VL or Qwen3.5 model to text_encoders, or connect a generation-capable CLIP loader.")
    # Prefer a small general instruction model over an image-specific upsampler.
    return min(names, key=lambda name: (
        float(match.group(1)) if (match := re.search(r'(\d+(?:\.\d+)?)b(?:[^a-z]|$)', name.lower())) else 999,
        any(word in name.lower() for word in ("upsampler", "heretic", "moss", "minimax")),
        name,
    ))


FALLBACK_REPO = 'Comfy-Org/Qwen3.5'
FALLBACK_REVISION = '5d50a2252bf1bcd49e5fee9b5f296986d442682b'
FALLBACK_FILE = 'text_encoders/qwen3.5_2b_bf16.safetensors'


def download_fallback():
    """One pinned official checkpoint, cached by HF; interrupted downloads can resume."""
    import folder_paths
    from huggingface_hub import hf_hub_download
    from pathlib import Path
    folders = folder_paths.get_folder_paths('text_encoders')
    target = Path(folders[0]) / 'prompt-mage'
    target.mkdir(parents=True, exist_ok=True)
    logging.warning('Prompt Mage: no compatible encoder installed. Downloading official Qwen3.5 2B (~4 GB) from Hugging Face. This first run may take several minutes.')
    path = hf_hub_download(repo_id=FALLBACK_REPO, filename=FALLBACK_FILE,
                           revision=FALLBACK_REVISION, local_dir=str(target))
    return str(Path(path).relative_to(Path(folders[0])))


def load_local_clip(model_name="Automatic", clip=None, auto_download=False):
    if clip is not None:
        return clip
    from nodes import CLIPLoader
    if model_name == "Automatic":
        names = local_models()
        if names:
            model_name = select_model(names)
        elif auto_download:
            model_name = download_fallback()
        else:
            model_name = select_model(names)
    logging.info('Prompt Mage assistant encoder: %s', model_name)
    return CLIPLoader().load_clip(model_name, type="stable_diffusion")[0]


def describe_local(description, mode, required, avoid, seed, model_name="Automatic", clip=None,
                   source_tags="", custom_instructions="", target="DART tags", canvas_width=1024, canvas_height=1024,
                   prompt_length="Balanced", language_style="Default", max_tokens=4096, unload_after_generation=False):
    system, scene_input = scene_request(description, mode, required, avoid, source_tags, custom_instructions, target,
                                       canvas_width, canvas_height, prompt_length, language_style, max_tokens)
    from comfy_extras.nodes_textgen import TextGenerate

    clip = load_local_clip(model_name, clip)
    with offload_after(clip, unload_after_generation):
        payload = json.dumps(scene_input, ensure_ascii=False)
        sampling = {"sampling_mode": "off"} if mode == "Preserve" else {
            "sampling_mode": "on", "temperature": 0.7, "top_k": 40,
            "top_p": 0.9, "min_p": 0.05, "repetition_penalty": 1.05, "seed": seed,
        }
        output = TextGenerate.execute(
            clip=clip, prompt=payload, max_length=max_tokens, sampling_mode=sampling,
            thinking=False, system_prompt=system, mtp="off",
        )
        scene = parse_scene(output.args[0])
        scene["source_description"] = description
        scene["source_tags"] = source_tags
        return scene
