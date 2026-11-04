import json

from .base import BaseNode
from ..dart.assistant import TARGETS, request_scene, format_scene


class DanbooruTagsTransformerDescribeImage(BaseNode):
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "description": ("STRING", {"default": "A woman in a red coat waiting at a rainy cafe, looking out the window.", "multiline": True}),
            "target": (TARGETS,),
            "mode": (["Preserve", "Expand"],),
            "endpoint": ("STRING", {"default": "http://localhost:1234/v1", "tooltip": "LM Studio: port 1234. Ollama: port 11434. Include /v1."}),
            "model": ("STRING", {"default": "", "tooltip": "The model identifier from your chat server."}),
            "seed": ("INT", {"default": 0, "min": 0, "max": 2**32 - 1}),
        }, "optional": {
            "keep_tags": ("STRING", {"default": "", "multiline": True, "tooltip": "Required literal tags or weights. These override Avoid."}),
            "avoid": ("STRING", {"default": "", "multiline": True}),
            "timeout": ("INT", {"default": 120, "min": 5, "max": 600}),
            "api_key_env": ("STRING", {"default": "", "tooltip": "Optional environment variable name. Never paste the key itself."}),
        }}

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("prompt", "general_tags", "copyright", "character", "negative_prompt", "scene_json")
    FUNCTION = "describe"
    DESCRIPTION = "Turn a description into tags or prose using a configured chat server. DART expansion is optional."

    def describe(self, description, target, mode, endpoint, model, seed,
                 keep_tags="", avoid="", timeout=120, api_key_env=""):
        scene = request_scene(description, endpoint, model, mode, keep_tags, avoid,
                              seed, timeout, api_key_env)
        prompt, general = format_scene(scene, target, keep_tags, avoid)
        return (prompt, general, scene["copyright"], scene["character"], avoid,
                json.dumps(scene, ensure_ascii=False, indent=2))
