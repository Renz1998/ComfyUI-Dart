from ...dart.tokenizer.tokenizer import DartTokenizer

from ..base import BaseNode
from ...dart.tags import remove_tags as remove_tag_sequences


class DanbooruTagsTransformerRearrangedByAnimagine(BaseNode):
    @classmethod
    def INPUT_TYPES(s):
        input_types = {
            "required": {
                "tokenizer": ("DART_TOKENIZER",),
                "token_ids": ("DART_TOKEN_IDS",),
            },
        }

        return input_types

    RETURN_TYPES = ("DART_TOKEN_IDS",)
    FUNCTION = "rearrange"

    def rearrange(self, tokenizer: DartTokenizer, token_ids):
        rearranged_tokens = tokenizer.rearrange_by_animagine(token_ids)
        return (rearranged_tokens,)


class DanbooruTagsTransformerRemoveTagToken(BaseNode):
    @classmethod
    def INPUT_TYPES(s):
        input_types = {
            "required": {
                "tokenizer": ("DART_TOKENIZER",),
                "token_ids": ("DART_TOKEN_IDS",),
                "remove_tags": (
                    "STRING",
                    {
                        "default": "",
                        "display": "remove tags",
                        "multiline": True,
                    },
                ),
            },
        }

        return input_types

    RETURN_TYPES = ("DART_TOKEN_IDS",)
    FUNCTION = "remove"

    def remove(self, tokenizer: DartTokenizer, token_ids, remove_tags):
        token_ids = remove_tag_sequences(tokenizer.tokenizer, token_ids, remove_tags)
        return (token_ids,)
