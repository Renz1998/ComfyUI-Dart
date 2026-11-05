import json

from .base import BaseNode
from ..dart.assistant import TARGETS, PROMPT_LENGTHS, LANGUAGE_STYLES, request_scene, format_scene
from ..dart.local_assistant import local_models, describe_local
from ..dart.moss import compile_layout, read_layout


class DanbooruTagsTransformerDescribeImage(BaseNode):
    CATEGORY = "Prompt Atelier/Assistants"
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "description": ("STRING", {"default": "", "multiline": True}),
            "target": (TARGETS,),
            "mode": (["Preserve", "Expand", "Concept"],),
            "endpoint": ("STRING", {"default": "http://localhost:1234/v1", "advanced": True, "tooltip": "Only used by Chat server. Local model needs no server."}),
            "model": ("STRING", {"default": "", "advanced": True, "tooltip": "Only used by Chat server."}),
            "seed": ("INT", {"default": 0, "min": 0, "max": 2**32 - 1}),
        }, "optional": {
            "keep_tags": ("STRING", {"default": "", "multiline": True, "tooltip": "Required literal tags or weights. These override Avoid."}),
            "avoid": ("STRING", {"default": "", "multiline": True}),
            "timeout": ("INT", {"default": 120, "min": 5, "max": 600, "advanced": True}),
            "api_key_env": ("STRING", {"default": "", "advanced": True, "tooltip": "Only used by Chat server. Environment variable name, never the key."}),
            "backend": (["Local model", "Chat server"], {"default": "Local model"}),
            "local_model": (["Automatic"] + local_models(), {"default": "Automatic", "tooltip": "Uses an existing full Qwen model in text_encoders. No download or server."}),
            "clip": ("CLIP", {"tooltip": "Optional generation-capable CLIP from the native loader. Overrides local_model."}),
            "source_tags": ("STRING", {"forceInput": True, "default": ""}),
            "custom_instructions": ("STRING", {"default": "", "multiline": True}),
            "canvas_width": ("INT", {"default": 1024, "min": 16, "max": 8192, "step": 16}),
            "canvas_height": ("INT", {"default": 1024, "min": 16, "max": 8192, "step": 16}),
            "layout_json": ("STRING", {"default": "", "multiline": True}),
            "prompt_length": (PROMPT_LENGTHS, {"default": "Balanced", "tooltip": "Brief: 40–80 words; Balanced: 100–180; Detailed: 200–350; Extensive: 400–650. Approximate targets, not guarantees. Preserve mode never invents details just to fill space. JSON length covers all captions together."}),
            "max_tokens": ("INT", {"default": 4096, "min": 512, "max": 16384, "step": 256, "tooltip": "Maximum generated tokens for the whole response, including internal JSON and tags. This is a ceiling, not a desired length. Try 8192 for Extensive layouts; larger limits can take longer."}),
            "language_style": (LANGUAGE_STYLES, {"default": "Default", "tooltip": "Direct / explicit asks for precise visual and anatomical terms, preserves supplied explicit wording and avoids euphemisms. It does not add sexual details or change the model's own policies."}),
        }}

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("prompt", "general_tags", "copyright", "character", "negative_prompt", "scene_json")
    FUNCTION = "describe"
    OUTPUT_NODE = True
    DESCRIPTION = "Turn a description into tags or prose with an existing local Qwen model. Shows the result directly. Chat servers are optional."

    def describe(self, description, target, mode, endpoint, model, seed,
                 keep_tags="", avoid="", timeout=120, api_key_env="", backend=None,
                 local_model="Automatic", clip=None, source_tags="", custom_instructions="",
                 canvas_width=1024, canvas_height=1024, layout_json="", prompt_length="Balanced",
                 max_tokens=4096, language_style="Default"):
        def query(instructions):
            if backend == "Chat server" or (backend is None and model.strip()):
                return request_scene(description, endpoint, model, mode, keep_tags, avoid,
                                     seed, timeout, api_key_env, source_tags=source_tags,
                                     custom_instructions=instructions, target=target,
                                     canvas_width=canvas_width, canvas_height=canvas_height,
                                     prompt_length=prompt_length, language_style=language_style, max_tokens=max_tokens)
            return describe_local(description, mode, keep_tags, avoid, seed, local_model, clip,
                                  source_tags=source_tags, custom_instructions=instructions, target=target,
                                  canvas_width=canvas_width, canvas_height=canvas_height,
                                  prompt_length=prompt_length, language_style=language_style, max_tokens=max_tokens)

        layout = None
        if target == "MOSS JSON layout" and layout_json.strip():
            layout = read_layout(layout_json, canvas_width, canvas_height)
            scene = {"description": layout["summary"]["caption"], "tags": [item["caption"] for item in layout["items"]],
                     "copyright": "original", "character": "", "added_details": [],
                     "source_description": description, "source_tags": source_tags}
        else:
            scene = query(custom_instructions)
            if prompt_length in ("Detailed", "Extensive") and mode != "Preserve":
                def caption_words(value):
                    if target == "MOSS JSON layout":
                        draft = value.get("layout_draft")
                        if not isinstance(draft, dict):
                            return 0
                        summary = draft.get("summary")
                        captions = [summary.get("caption", "") if isinstance(summary, dict) else ""]
                        items = draft.get("items")
                        if isinstance(items, list):
                            captions.extend(item.get("caption", "") for item in items if isinstance(item, dict))
                        return len(" ".join(str(caption) for caption in captions).split())
                    return len(value.get("description", "").split())
                minimum = 120 if prompt_length == "Detailed" else 240
                if caption_words(scene) < minimum:
                    previous = scene
                    scene = query(custom_instructions + "\nThe previous response was much shorter than the requested "
                                  + prompt_length + " length. Rewrite the complete scene JSON with substantially richer visual captions. "
                                  "Develop supported subject, pose, material, framing, lighting, background and spatial details; "
                                  "avoid repetition and preserve all user constraints. Never render this instruction as visible image text. "
                                  "Previous scene: " + json.dumps(previous, ensure_ascii=False))
                    if caption_words(scene) < caption_words(previous):
                        scene = previous
                    scene["length_revision_attempted"] = True
        if target == "MOSS JSON layout":
            if layout is None:
                try:
                    layout = compile_layout(scene.get("layout_draft"), canvas_width, canvas_height, draft=True)
                except ValueError as error:
                    # One bounded repair for small instruction models; never alter a manual override.
                    repair = (custom_instructions + "\nRepair the previous layout draft. Validation error: " + str(error)
                              + "\nReturn the complete scene JSON again with a corrected layout_draft. Previous draft: "
                              + json.dumps(scene.get("layout_draft"), ensure_ascii=False))
                    scene = query(repair)
                    layout = compile_layout(scene.get("layout_draft"), canvas_width, canvas_height, draft=True)
                    scene["layout_repaired"] = True
                if keep_tags.strip():
                    layout["summary"]["caption"] += "\n" + keep_tags.strip()
            scene["moss_layout"] = layout
            scene["canvas_width"], scene["canvas_height"] = canvas_width, canvas_height
            prompt = json.dumps(layout, ensure_ascii=False, indent=2)
            general = "" if layout_json.strip() else format_scene(scene, "DART tags", keep_tags, avoid)[1]
        else:
            prompt, general = format_scene(scene, target, keep_tags, avoid)
        return {"ui": {"text": [prompt], "moss_json": [target == "MOSS JSON layout"]}, "result": (
            prompt, general, scene["copyright"], scene["character"], avoid,
            json.dumps(scene, ensure_ascii=False, indent=2),
        )}
