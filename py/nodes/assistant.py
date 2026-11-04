import json

from .base import BaseNode
from ..dart.assistant import TARGETS, request_scene, format_scene
from ..dart.local_assistant import local_models, describe_local


class DanbooruTagsTransformerDescribeImage(BaseNode):
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "description": ("STRING", {"default": "A woman in a red coat waiting at a rainy cafe, looking out the window.", "multiline": True}),
            "target": (TARGETS,),
            "mode": (["Preserve", "Expand"],),
            "endpoint": ("STRING", {"default": "http://localhost:1234/v1", "advanced": True, "tooltip": "Only used by Chat server. Local model needs no server."}),
            "model": ("STRING", {"default": "", "advanced": True, "tooltip": "Only used by Chat server."}),
            "seed": ("INT", {"default": 0, "min": 0, "max": 2**32 - 1}),
        }, "optional": {
            "keep_tags": ("STRING", {"default": "", "multiline": True, "tooltip": "Required literal tags or weights. These override Avoid."}),
            "avoid": ("STRING", {"default": "", "multiline": True}),
            "timeout": ("INT", {"default": 120, "min": 5, "max": 600, "advanced": True}),
            "api_key_env": ("STRING", {"default": "", "advanced": True, "tooltip": "Only used by Chat server. Environment variable name, never the key."}),
            "backend": (["Local model", "Chat server"], {"default": "Local model"}),
            "local_model": (["Automatic"] + local_models(), {"default": "Automatic", "tooltip": "Uses an existing full Qwen model in text_encoders. No download or server."}),
            "clip": ("CLIP", {"tooltip": "Optional generation-capable CLIP from the native loader. Overrides local_model."}),
        }}

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("prompt", "general_tags", "copyright", "character", "negative_prompt", "scene_json")
    FUNCTION = "describe"
    OUTPUT_NODE = True
    DESCRIPTION = "Turn a description into tags or prose with an existing local Qwen model. Shows the result directly. Chat servers are optional."

    def describe(self, description, target, mode, endpoint, model, seed,
                 keep_tags="", avoid="", timeout=120, api_key_env="", backend=None,
                 local_model="Automatic", clip=None):
        if backend == "Chat server" or (backend is None and model.strip()):
            scene = request_scene(description, endpoint, model, mode, keep_tags, avoid,
                                  seed, timeout, api_key_env)
        else:
            scene = describe_local(description, mode, keep_tags, avoid, seed, local_model, clip)
        prompt, general = format_scene(scene, target, keep_tags, avoid)
        return {"ui": {"text": [prompt]}, "result": (
            prompt, general, scene["copyright"], scene["character"], avoid,
            json.dumps(scene, ensure_ascii=False, indent=2),
        )}
