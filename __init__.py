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
from .py.nodes.image_batch import DanbooruTagsTransformerImageBatchSelector, DanbooruTagsTransformerImageBatchUpload

NODE_CLASS_MAPPINGS = {
    "DanbooruTagsTransformerImageBatchUpload": DanbooruTagsTransformerImageBatchUpload,
    "DanbooruTagsTransformerImageBatchSelector": DanbooruTagsTransformerImageBatchSelector,
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
    "DanbooruTagsTransformerImageBatchUpload": "Prompt Mage · Upload Images",
    "DanbooruTagsTransformerImageBatchSelector": "Prompt Mage · Server Folder (Advanced)",
    "DanbooruTagsTransformerAppearanceOverrides": "Prompt Mage · Appearance Overrides",
    "DanbooruTagsTransformerImageToText": "Prompt Mage · Image to Text",
    "DanbooruTagsTransformerComposePromptV3": "Prompt Mage · DART Compose Prompt V3 (Experimental)",
    "DanbooruTagsTransformerDescribeImage": "Prompt Mage · Text Assistant",
    "DanbooruTagsTransformerLoader": "Prompt Mage · DART Load",
    "DanbooruTagsTransformerGenerate": "Prompt Mage · DART Generate",
    "DanbooruTagsTransformerComposePrompt": "Prompt Mage · DART Compose Prompt",
    "DanbooruTagsTransformerComposePromptV2": "Prompt Mage · DART Compose Prompt V2",
    "DanbooruTagsTransformerGetAspectRatio": "Prompt Mage · DART Get Aspect Ratio",
    "DanbooruTagsTransformerGenerationConfig": "Prompt Mage · DART Generation Config",
    "DanbooruTagsTransformerBanTagsFromRegex": "Prompt Mage · DART Ban Tags From Regex",
    # Advanced
    "DanbooruTagsTransformerGenerateAdvanced": "Prompt Mage · DART Generate(Advanced)",
    "DanbooruTagsTransformerDecode": "Prompt Mage · DART Decode",
    "DanbooruTagsTransformerDecodeBySplitedParts": "Prompt Mage · DART Decode By Splited Parts",
    "DanbooruTagsTransformerRearrangedByAnimagine": "Prompt Mage · DART Rearranged By Animagine",
    "DanbooruTagsTransformerRemoveTagToken": "Prompt Mage · DART Remove Tag Token",
}

attach_help(NODE_CLASS_MAPPINGS)

WEB_DIRECTORY = "./web"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
