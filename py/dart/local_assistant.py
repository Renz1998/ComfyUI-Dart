"""Use ComfyUI's model loader, text generation and offloading for local assistance."""

import json

from .assistant import scene_request, parse_scene


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


def load_local_clip(model_name="Automatic", clip=None):
    if clip is not None:
        return clip
    from nodes import CLIPLoader
    if model_name == "Automatic":
        model_name = select_model(local_models())
    return CLIPLoader().load_clip(model_name, type="stable_diffusion")[0]


def describe_local(description, mode, required, avoid, seed, model_name="Automatic", clip=None,
                   source_tags="", custom_instructions="", target="DART tags", canvas_width=1024, canvas_height=1024):
    system, scene_input = scene_request(description, mode, required, avoid, source_tags, custom_instructions, target,
                                       canvas_width, canvas_height)
    from comfy_extras.nodes_textgen import TextGenerate

    clip = load_local_clip(model_name, clip)
    payload = json.dumps(scene_input, ensure_ascii=False)
    sampling = {"sampling_mode": "off"} if mode == "Preserve" else {
        "sampling_mode": "on", "temperature": 0.7, "top_k": 40,
        "top_p": 0.9, "min_p": 0.05, "repetition_penalty": 1.05, "seed": seed,
    }
    output = TextGenerate.execute(
        clip=clip, prompt=payload, max_length=3072 if target == "MOSS JSON layout" else 1536, sampling_mode=sampling,
        thinking=False, system_prompt=system, mtp="off",
    )
    scene = parse_scene(output.args[0])
    scene["source_description"] = description
    scene["source_tags"] = source_tags
    return scene
