import json

from .base import BaseNode
from ..dart.assistant import TARGETS, request_scene, format_scene
from ..dart.local_assistant import local_models, describe_local
from ..dart.moss import compile_layout, read_layout


class DanbooruTagsTransformerDescribeImage(BaseNode):
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
        }}

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("prompt", "general_tags", "copyright", "character", "negative_prompt", "scene_json")
    FUNCTION = "describe"
    OUTPUT_NODE = True
    DESCRIPTION = "Turn a description into tags or prose with an existing local Qwen model. Shows the result directly. Chat servers are optional."

    def describe(self, description, target, mode, endpoint, model, seed,
                 keep_tags="", avoid="", timeout=120, api_key_env="", backend=None,
                 local_model="Automatic", clip=None, source_tags="", custom_instructions="",
                 canvas_width=1024, canvas_height=1024, layout_json=""):
        def query(instructions):
            if backend == "Chat server" or (backend is None and model.strip()):
                return request_scene(description, endpoint, model, mode, keep_tags, avoid,
                                     seed, timeout, api_key_env, source_tags=source_tags,
                                     custom_instructions=instructions, target=target,
                                     canvas_width=canvas_width, canvas_height=canvas_height)
            return describe_local(description, mode, keep_tags, avoid, seed, local_model, clip,
                                  source_tags=source_tags, custom_instructions=instructions, target=target,
                                  canvas_width=canvas_width, canvas_height=canvas_height)

        layout = None
        if target == "MOSS JSON layout" and layout_json.strip():
            layout = read_layout(layout_json, canvas_width, canvas_height)
            scene = {"description": layout["summary"]["caption"], "tags": [item["caption"] for item in layout["items"]],
                     "copyright": "original", "character": "", "added_details": [],
                     "source_description": description, "source_tags": source_tags}
        else:
            scene = query(custom_instructions)
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
            prompt = json.dumps(layout, ensure_ascii=False, separators=(",", ":"))
            general = "" if layout_json.strip() else format_scene(scene, "DART tags", keep_tags, avoid)[1]
        else:
            prompt, general = format_scene(scene, target, keep_tags, avoid)
        return {"ui": {"text": [prompt]}, "result": (
            prompt, general, scene["copyright"], scene["character"], avoid,
            json.dumps(scene, ensure_ascii=False, indent=2),
        )}
