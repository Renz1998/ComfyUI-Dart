from .base import BaseNode
from ..dart.tokenizer.tokenizer_v3 import RATINGS, ASPECT_RATIOS, LENGTHS


class DanbooruTagsTransformerComposePromptV3(BaseNode):
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "rating": (RATINGS,),
            "aspect_ratio": (ASPECT_RATIOS, {"default": "square"}),
            "length": (LENGTHS, {"default": "medium"}),
            "copyright": ("STRING", {"default": "original"}),
            "character": ("STRING", {"default": ""}),
            "general": ("STRING", {"default": "1girl, solo", "multiline": True}),
        }}

    RETURN_TYPES = ("STRING",)
    FUNCTION = "compose"

    def compose(self, rating, aspect_ratio, length, copyright, character, general):
        for value, choices in ((rating, RATINGS), (aspect_ratio, ASPECT_RATIOS), (length, LENGTHS)):
            if value not in choices:
                raise ValueError(f"Unsupported DART v3 option: {value}")
        return (f"<|bos|><|rating:{rating}|><|aspect_ratio:{aspect_ratio}|><|length:{length}|>"
                f"<copyright>{copyright}</copyright><character>{character}</character>"
                f"<general>{general}<|input_end|>",)
