"""Preview E uses a WordLevel vocabulary with one token per comma-separated tag."""

from .tokenizer_v2 import DartTokenizerV2

RATINGS = ["general", "sensitive", "questionable", "explicit"]
# too_wide is present in the actual preview-E tokenizer despite the model-card typo.
ASPECT_RATIOS = ["too_tall", "tall_wallpaper", "tall", "square", "wide", "wide_wallpaper", "too_wide"]
LENGTHS = ["very_short", "medium", "very_long"]
SPECIAL_TAGS_V3 = ["<|bos|>", "<|eos|>", "<|input_end|>", "<copyright>",
                   "</copyright>", "<character>", "</character>", "<general>", "</general>"]
SPECIAL_TAGS_V3 += [f"<|{name}:{value}|>" for name, values in (
    ("rating", RATINGS), ("aspect_ratio", ASPECT_RATIOS), ("length", LENGTHS)
) for value in values]


class DartTokenizerV3(DartTokenizerV2):
    pass
