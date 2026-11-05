from .base import BaseNode
from ..dart.appearance import TRAITS, KEEP, override_instructions


class DanbooruTagsTransformerAppearanceOverrides(BaseNode):
    CATEGORY = "Prompt Atelier/Assistants"

    @classmethod
    def INPUT_TYPES(cls):
        fields = {
            "enabled": ("BOOLEAN", {"default": True, "tooltip": "Turn all appearance replacements on/off without removing connections."}),
            "subject": (["Main subject", "All people", "Custom subject"], {"default": "Main subject", "tooltip": "Choose who receives the replacements. Custom subject can identify the person on the left or another subject without naming a real person."}),
            "subject_custom": ("STRING", {"default": "", "tooltip": "Custom subject selector, for example: the adult person on the left. Used only with Custom subject."}),
            "trigger": ("STRING", {"default": "", "tooltip": "Optional exact training/character trigger. Overrides the Image to Text character trigger when provided. Does not load a LoRA."}),
            "identity_mode": (["Keep other appearance details", "Trigger replaces identity details"], {"tooltip": "Keep unselected traits, or use the trigger instead of describing unselected identity traits. The second option needs a trigger; selected replacements still appear."}),
        }
        for name, choices in TRAITS.items():
            fields[name] = ([KEEP] + choices + ["Custom"], {"default": KEEP, "tooltip": f"Replace {name.replace('_', ' ')} for the selected subject. Keep unchanged makes no request. Custom reveals a free-text value."})
            fields[name + "_custom"] = ("STRING", {"default": "", "tooltip": f"Your own {name.replace('_', ' ')} value. Used only when its dropdown is Custom."})
        fields["custom_overrides"] = ("STRING", {"default": "", "multiline": True, "tooltip": "Extra appearance replacements, accessories, makeup, clothing or other directions. Selected dropdown traits win if they conflict. Existing assistant writing instructions remain available."})
        fields["strict_wording"] = ("BOOLEAN", {"default": True, "tooltip": "Require selected trait phrases in generated descriptions and target-person captions. Reject missing or weakened size wording, request one correction, then report an error if still wrong. Disable to allow paraphrasing. Checks wording, not visual/semantic accuracy or free-form extra instructions."})
        return {"required": fields}

    RETURN_TYPES = ("ATELIER_APPEARANCE", "STRING")
    RETURN_NAMES = ("appearance", "instructions")
    FUNCTION = "build"
    OUTPUT_NODE = True

    def build(self, enabled=True, subject="Main subject", subject_custom="", trigger="",
              identity_mode="Keep other appearance details", custom_overrides="", strict_wording=True, **values):
        if subject not in ("Main subject", "All people", "Custom subject"):
            raise ValueError("Choose a supported subject selector.")
        if identity_mode not in ("Keep other appearance details", "Trigger replaces identity details"):
            raise ValueError("Choose a supported identity mode.")
        if enabled and subject == "Custom subject" and not subject_custom.strip():
            raise ValueError("Enter a custom subject, or choose Main subject.")
        if enabled and identity_mode == "Trigger replaces identity details" and not trigger.strip():
            raise ValueError("Enter a trigger for Trigger replaces identity details.")
        traits = {}
        for name, choices in TRAITS.items():
            choice = values.get(name, KEEP)
            if choice not in [KEEP] + choices + ["Custom"]:
                raise ValueError(f"Choose a supported {name.replace('_', ' ')} option.")
            value = values.get(name + "_custom", "").strip() if choice == "Custom" else choice
            if enabled and choice == "Custom" and not value:
                raise ValueError(f"Enter a custom {name.replace('_', ' ')} value.")
            if choice != KEEP and value:
                traits[name] = value
        settings = {"version": 1, "enabled": enabled, "subject": subject_custom.strip() if subject == "Custom subject" else subject,
                    "trigger": trigger.strip(), "identity_mode": identity_mode, "traits": traits, "custom": custom_overrides.strip(), "strict_wording": strict_wording}
        instructions, _ = override_instructions(settings)
        return {"ui": {"text": [instructions or "No appearance replacements requested."]}, "result": (settings, instructions)}
