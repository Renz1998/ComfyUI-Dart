from .base import BaseNode
from ..dart.local_assistant import local_models
from ..dart.vision import caption_image
from ..dart.assistant import LANGUAGE_STYLES


class DanbooruTagsTransformerImageToText(BaseNode):
    CATEGORY = "Prompt Atelier/Vision"
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "image": ("IMAGE",),
            "instructions": ("STRING", {"default": "", "multiline": True}),
            "detail": (["Detailed", "Concise"], {"default": "Detailed"}),
            "local_model": (["Automatic"] + local_models(), {"default": "Automatic"}),
        }, "optional": {
            "character_trigger": ("STRING", {"default": ""}),
            "image_index": ("INT", {"default": 0, "min": 0, "max": 65535}),
            "max_tokens": ("INT", {"default": 1024, "min": 64, "max": 4096, "step": 64}),
            "clip": ("CLIP",),
            "language_style": (LANGUAGE_STYLES, {"default": "Default", "tooltip": "Direct / explicit requests precise visual and anatomical wording without euphemisms or masked words. Preserves supplied terminology; the model's own policies still apply."}),
        }}

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("description",)
    FUNCTION = "describe"
    OUTPUT_NODE = True

    def describe(self, image, instructions="", detail="Detailed", local_model="Automatic",
                 character_trigger="", image_index=0, max_tokens=1024, clip=None, language_style="Default"):
        text = caption_image(image, instructions, character_trigger, detail, image_index,
                             max_tokens, model_name=local_model, clip=clip, language_style=language_style)
        return {"ui": {"text": [text]}, "result": (text,)}
