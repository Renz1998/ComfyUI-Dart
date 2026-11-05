from .py.nodes.loader import DanbooruTagsTransformerLoader
from .py.nodes.generate import DanbooruTagsTransformerGenerate
from .py.nodes.prompt import DanbooruTagsTransformerComposePrompt
from .py.nodes.prompt_v2 import (
    DanbooruTagsTransformerComposePromptV2,
    DanbooruTagsTransformerGetAspectRatio,
)
from .py.nodes.config import DanbooruTagsTransformerGenerationConfig
from .py.nodes.advanced.generate import DanbooruTagsTransformerGenerateAdvanced
from .py.nodes.advanced.decode import (
    DanbooruTagsTransformerDecode,
    DanbooruTagsTransformerDecodeBySplitedParts,
)
from .py.nodes.advanced.token_ids import (
    DanbooruTagsTransformerRearrangedByAnimagine,
    DanbooruTagsTransformerRemoveTagToken,
)
from .py.nodes.ban_tags import DanbooruTagsTransformerBanTagsFromRegex
from .py.nodes.prompt_v3 import DanbooruTagsTransformerComposePromptV3
from .py.nodes.assistant import DanbooruTagsTransformerDescribeImage
from .py.nodes.vision import DanbooruTagsTransformerImageToText
from .py.nodes.help import attach_help
from .py.nodes.appearance import DanbooruTagsTransformerAppearanceOverrides

NODE_CLASS_MAPPINGS = {
    "DanbooruTagsTransformerAppearanceOverrides": DanbooruTagsTransformerAppearanceOverrides,
    "DanbooruTagsTransformerImageToText": DanbooruTagsTransformerImageToText,
    "DanbooruTagsTransformerComposePromptV3": DanbooruTagsTransformerComposePromptV3,
    "DanbooruTagsTransformerDescribeImage": DanbooruTagsTransformerDescribeImage,
    "DanbooruTagsTransformerLoader": DanbooruTagsTransformerLoader,
    "DanbooruTagsTransformerGenerate": DanbooruTagsTransformerGenerate,
    "DanbooruTagsTransformerComposePrompt": DanbooruTagsTransformerComposePrompt,
    "DanbooruTagsTransformerComposePromptV2": DanbooruTagsTransformerComposePromptV2,
    "DanbooruTagsTransformerGetAspectRatio": DanbooruTagsTransformerGetAspectRatio,
    "DanbooruTagsTransformerGenerationConfig": DanbooruTagsTransformerGenerationConfig,
    "DanbooruTagsTransformerBanTagsFromRegex": DanbooruTagsTransformerBanTagsFromRegex,
    # Advanced
    "DanbooruTagsTransformerGenerateAdvanced": DanbooruTagsTransformerGenerateAdvanced,
    "DanbooruTagsTransformerDecode": DanbooruTagsTransformerDecode,
    "DanbooruTagsTransformerDecodeBySplitedParts": DanbooruTagsTransformerDecodeBySplitedParts,
    "DanbooruTagsTransformerRearrangedByAnimagine": DanbooruTagsTransformerRearrangedByAnimagine,
    "DanbooruTagsTransformerRemoveTagToken": DanbooruTagsTransformerRemoveTagToken,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DanbooruTagsTransformerAppearanceOverrides": "Prompt Atelier · Appearance Overrides",
    "DanbooruTagsTransformerImageToText": "Prompt Atelier · Image to Text",
    "DanbooruTagsTransformerComposePromptV3": "Prompt Atelier · DART Compose Prompt V3 (Experimental)",
    "DanbooruTagsTransformerDescribeImage": "Prompt Atelier · Text Assistant",
    "DanbooruTagsTransformerLoader": "Prompt Atelier · DART Load",
    "DanbooruTagsTransformerGenerate": "Prompt Atelier · DART Generate",
    "DanbooruTagsTransformerComposePrompt": "Prompt Atelier · DART Compose Prompt",
    "DanbooruTagsTransformerComposePromptV2": "Prompt Atelier · DART Compose Prompt V2",
    "DanbooruTagsTransformerGetAspectRatio": "Prompt Atelier · DART Get Aspect Ratio",
    "DanbooruTagsTransformerGenerationConfig": "Prompt Atelier · DART Generation Config",
    "DanbooruTagsTransformerBanTagsFromRegex": "Prompt Atelier · DART Ban Tags From Regex",
    # Advanced
    "DanbooruTagsTransformerGenerateAdvanced": "Prompt Atelier · DART Generate(Advanced)",
    "DanbooruTagsTransformerDecode": "Prompt Atelier · DART Decode",
    "DanbooruTagsTransformerDecodeBySplitedParts": "Prompt Atelier · DART Decode By Splited Parts",
    "DanbooruTagsTransformerRearrangedByAnimagine": "Prompt Atelier · DART Rearranged By Animagine",
    "DanbooruTagsTransformerRemoveTagToken": "Prompt Atelier · DART Remove Tag Token",
}

attach_help(NODE_CLASS_MAPPINGS)

WEB_DIRECTORY = "./web"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
