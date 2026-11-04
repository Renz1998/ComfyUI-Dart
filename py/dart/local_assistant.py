"""Use ComfyUI's model loader, text generation and offloading for local assistance."""

import json

from .assistant import SYSTEM_PROMPT, parse_scene


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
        any(word in name.lower() for word in ("upsampler", "heretic", "moss", "minimax")),
        "4b" not in name.lower(), "8b" not in name.lower(), name,
    ))


def describe_local(description, mode, required, avoid, seed, model_name="Automatic", clip=None):
    if not description.strip():
        raise ValueError("Describe the image you want first.")
    from nodes import CLIPLoader
    from comfy_extras.nodes_textgen import TextGenerate

    if clip is None:
        if model_name == "Automatic":
            model_name = select_model(local_models())
        # Native loader resolves the filename inside configured model directories.
        clip = CLIPLoader().load_clip(model_name, type="stable_diffusion")[0]
    payload = json.dumps({"description": description, "mode": mode,
                          "required_literal_tags": required, "avoid": avoid}, ensure_ascii=False)
    sampling = {"sampling_mode": "off"} if mode == "Preserve" else {
        "sampling_mode": "on", "temperature": 0.7, "top_k": 40,
        "top_p": 0.9, "min_p": 0.05, "repetition_penalty": 1.05, "seed": seed,
    }
    output = TextGenerate.execute(
        clip=clip, prompt=payload, max_length=1536, sampling_mode=sampling,
        thinking=False, system_prompt=SYSTEM_PROMPT, mtp="off",
    )
    scene = parse_scene(output.args[0])
    scene["source_description"] = description
    return scene
