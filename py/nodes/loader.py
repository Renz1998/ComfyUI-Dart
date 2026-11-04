from ..dart.model import DartModel
from ..dart.tokenizer.tokenizer import DartTokenizer
from ..dart.tokenizer.tokenizer_v2 import DartTokenizerV2
from ..dart.tokenizer.tokenizer_v3 import DartTokenizerV3, SPECIAL_TAGS_V3

from .base import BaseNode
from ..dart.defs.token import SPECIAL_TAGS
from ..dart.defs.token_v2 import SPECIAL_TAGS_V2


class DanbooruTagsTransformerLoader(BaseNode):
    MODEL_NAMES = {
        "dart-v1-sft": {
            "model_name": "p1atdev/dart-v1-sft",
            "special_tags": SPECIAL_TAGS,
            "tokenizer": DartTokenizer,
        },
        "dart-v2-moe-sft": {
            "model_name": "p1atdev/dart-v2-moe-sft",
            "special_tags": SPECIAL_TAGS_V2,
            "tokenizer": DartTokenizerV2,
        },
        "dart-v2-sft": {
            "model_name": "p1atdev/dart-v2-sft",
            "special_tags": SPECIAL_TAGS_V2,
            "tokenizer": DartTokenizerV2,
        },
        "dart-v3-sft-preview-E (experimental)": {
            "model_name": "p1atdev/dart-v3-sft-preview-E",
            "special_tags": SPECIAL_TAGS_V3,
            "tokenizer": DartTokenizerV3,
        },
    }

    @classmethod
    def INPUT_TYPES(cls):
        input_types = {
            "required": {
                "model": (list(cls.MODEL_NAMES.keys()),),
            },
            "optional": {
                "device": (["cpu", "auto", "cuda"], {"default": "cpu"}),
                "dtype": (["auto", "float32", "bfloat16", "float16"],),
                "local_model_path": ("STRING", {"default": ""}),
                "revision": ("STRING", {"default": "main"}),
                "local_files_only": ("BOOLEAN", {"default": False}),
            },
        }

        return input_types

    RETURN_TYPES = ("DART_MODEL", "DART_TOKENIZER")
    FUNCTION = "load"

    def load(self, model, device="cpu", dtype="auto", local_model_path="", revision="main", local_files_only=False):
        model_name = local_model_path.strip() or self.MODEL_NAMES[model]["model_name"]
        special_tags = self.MODEL_NAMES[model]["special_tags"]
        load_options = {"revision": revision, "local_files_only": local_files_only}
        tokenizer = self.MODEL_NAMES[model]["tokenizer"](model_name, special_tags, **load_options)
        dart_model = DartModel(model_name, device=device, dtype=dtype, **load_options)
        return (dart_model, tokenizer)
