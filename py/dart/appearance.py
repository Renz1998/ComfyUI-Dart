"""Reusable, optional visual-edit instructions shared by both assistants."""
import json
from copy import deepcopy

KEEP = "Keep unchanged"
TRAITS = {
    "hair_color": ["Black", "Brown", "Blonde", "Red", "Auburn", "White", "Silver", "Grey", "Blue", "Pink", "Purple", "Green"],
    "hair_style": ["Straight", "Wavy", "Curly", "Bob", "Pixie cut", "Ponytail", "Twin tails", "Braid", "Bun", "Loose hair"],
    "eye_color": ["Brown", "Blue", "Green", "Hazel", "Grey", "Amber", "Violet", "Red"],
    "breast_size": ["Flat chest", "Small breasts", "Medium breasts", "Large breasts", "Very large breasts", "Massive breasts", "Gigantic breasts"],
    "hair_length": ["Bald", "Very short", "Short", "Shoulder length", "Long", "Very long"],
    "body_type": ["Slim", "Athletic", "Muscular", "Curvy", "Full figured"],
    "skin_tone": ["Fair", "Light", "Medium", "Tan", "Brown", "Dark"],
    "clothing": ["Casual clothes", "Dress", "Suit", "Shirt and jeans", "Swimwear", "Lingerie"],
    "expression": ["Neutral", "Smiling", "Serious", "Laughing", "Surprised", "Confident"],
}


def apply_trigger(scene, trigger):
    if not trigger:
        return scene
    scene = deepcopy(scene)
    scene["character"] = trigger
    if trigger not in scene["description"]:
        scene["description"] = trigger + ", " + scene["description"]
    draft = scene.get("layout_draft")
    if isinstance(draft, dict) and isinstance(draft.get("summary"), dict):
        caption = draft["summary"].get("caption")
        if isinstance(caption, str) and trigger not in caption:
            draft["summary"]["caption"] = trigger + ", " + caption
    return scene


def override_instructions(settings):
    if settings is None:
        return "", ""
    if not isinstance(settings, dict) or settings.get("version") != 1 or not isinstance(settings.get("enabled"), bool):
        raise ValueError("Connect appearance from Prompt Atelier · Appearance Overrides.")
    if not settings["enabled"]:
        return "", ""
    traits = settings.get("traits")
    if not isinstance(traits, dict) or any(key not in TRAITS or not isinstance(value, str) for key, value in traits.items()):
        raise ValueError("Appearance overrides contain unsupported traits.")
    for field in ("subject", "trigger", "identity_mode", "custom"):
        if not isinstance(settings.get(field), str):
            raise ValueError("Appearance override fields must be text.")
    if not traits and not settings["trigger"] and not settings["custom"]:
        return "", ""
    instructions = (
        "\nApply these requested appearance replacements to the selected subject, even in Preserve mode. "
        "Describe the changed version directly; omit conflicting original attributes instead of explaining the edits. "
        "Apply changes consistently to tags, prose, every JSON field and every layout caption. "
        "Keep pose, framing, background, lighting and unselected attributes unless another instruction changes them. "
        "For multiple people, change only the specified subject; do not transfer traits to other people. "
        "Use a nonempty trigger as the exact literal character reference, not a guessed name. "
        "If identity_mode is 'Trigger replaces identity details', omit unselected identity traits such as original "
        "hair, eyes and body attributes, retaining the trigger and explicitly selected replacements. "
        "Selected replacements take priority over conflicting input descriptions and writing instructions. "
        "Do not render these settings as visible writing in the image. Do not change the required output schema. "
        "These instructions modify generated text, not image pixels. Settings:\n"
        + json.dumps({key: settings[key] for key in ("subject", "trigger", "identity_mode", "traits", "custom")}, ensure_ascii=False)
    )
    return instructions, settings["trigger"].strip()
