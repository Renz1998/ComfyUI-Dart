from .base import BaseNode
from ..dart.local_assistant import local_models
from ..dart.vision import caption_image, prepare_caption_image, VISION_FORMATS, RESIZE_METHODS
from ..dart.assistant import LANGUAGE_STYLES
from ..dart.appearance import override_instructions, MISMATCH_POLICIES, appearance_report, reported_result


class DanbooruTagsTransformerImageToText(BaseNode):
    CATEGORY = "Prompt Atelier/Vision"
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "image": ("IMAGE",),
            "instructions": ("STRING", {"default": "", "multiline": True}),
            "detail": (["Detailed", "Concise"], {"default": "Detailed"}),
            "local_model": (["Automatic"] + local_models(), {"default": "Automatic"}),
        }, "optional": {
            "character_trigger": ("STRING", {"default": ""}),
            "image_index": ("INT", {"default": 0, "min": 0, "max": 65535}),
            "max_tokens": ("INT", {"default": 4096, "min": 64, "max": 16384, "step": 64}),
            "clip": ("CLIP",),
            "language_style": (LANGUAGE_STYLES, {"default": "Default", "tooltip": "Direct / explicit requests precise visual and anatomical wording without euphemisms or masked words. Preserves supplied terminology; the model's own policies still apply."}),
            "output_format": (VISION_FORMATS, {"default": "Plain text", "tooltip": "Plain text: caption. Structured JSON: description, subjects, environment, lighting, composition and visible_text; useful for editing and tools, not native MOSS conditioning. MOSS JSON layout: native MOSS summary/items and estimated object/text boxes, ready for its text encoder. Instructions and character triggers apply to every format."}),
            "canvas_width": ("INT", {"default": 1024, "min": 16, "max": 8192, "step": 16, "tooltip": "MOSS JSON only: target generation width, in pixels and multiples of 16. Match your latent dimensions. The vision model estimates boxes on this canvas; the input image may have different dimensions."}),
            "canvas_height": ("INT", {"default": 1024, "min": 16, "max": 8192, "step": 16, "tooltip": "MOSS JSON only: target generation height, in pixels and multiples of 16. Match your latent dimensions. Does not resize the source image or generate an image."}),
            "image_megapixels": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 16.0, "step": 0.05, "tooltip": "Resize the selected image before vision inference. 1.0 means at most 1,000,000 pixels, with aspect ratio preserved as closely as rounding allows. 0 keeps original size (8192 pixels per side maximum). MOSS auto dimensions align to multiples of 16."}),
            "resize_mode": (["Downscale only", "Resize to budget"], {"default": "Downscale only", "tooltip": "Downscale only leaves small images at their current size. Resize to budget also enlarges small images toward the megapixel target. MOSS auto mode additionally aligns dimensions to multiples of 16."}),
            "resize_method": (RESIZE_METHODS, {"default": "lanczos", "tooltip": "Lanczos: sharp photographic resize. Bicubic: smoother interpolation. Bilinear: fast and smooth. Area: useful for reducing size. Nearest-exact: hard pixel edges. These are standard interpolation methods, not learned AI upscalers; no model downloads."}),
            "dimension_source": (["From processed image", "Manual canvas"], {"default": "From processed image", "tooltip": "MOSS JSON: automatically use the resized image width/height for layout coordinates, or enter a separate manual generation canvas. Width/height outputs match the layout canvas; other formats output processed image dimensions."}),
            "appearance": ("ATELIER_APPEARANCE", {"tooltip": "Optional Appearance Overrides recipe. Drag from this input to create its matching node. Selected replacements override source traits; its nonempty trigger overrides Character trigger."}),
            "unload_after_generation": ("BOOLEAN", {"default": False, "tooltip": "Offload this assistant's local text/vision model and its clones after generation, including errors, using ComfyUI's model manager. Does not unload unrelated diffusion models. Enable for a separate assistant encoder; a shared encoder may need reloading later. Ignored on cached executions."}),
            "on_override_mismatch": (MISMATCH_POLICIES, {"default": "Warn and continue", "tooltip": "After one correction still misses selected wording: Warn and continue returns the model output with a visible warning. Block downstream keeps the output in the preview/report but blocks dependent processing. Invalid JSON or model failures still stop normally."}),
            "source_name": ("STRING", {"default": "", "forceInput": True, "tooltip": "Optional filename label from Image Batch Selector. Included in the feedback report, not in model instructions."}),
        }}

    RETURN_TYPES = ("STRING", "INT", "INT", "IMAGE", "STRING", "STRING")
    RETURN_NAMES = ("description", "width", "height", "image", "status", "report")
    FUNCTION = "describe"
    OUTPUT_NODE = True

    def describe(self, image, instructions="", detail="Detailed", local_model="Automatic",
                 character_trigger="", image_index=0, max_tokens=4096, clip=None, language_style="Default",
                 output_format="Plain text", canvas_width=1024, canvas_height=1024, image_megapixels=1.0,
                 resize_mode="Downscale only", resize_method="lanczos", dimension_source="From processed image",
                 appearance=None, unload_after_generation=False, on_override_mismatch="Warn and continue", source_name=""):
        if on_override_mismatch not in MISMATCH_POLICIES:
            raise ValueError("Choose Warn and continue or Block downstream.")
        replacements, trigger = override_instructions(appearance)
        instructions += replacements
        if trigger:
            character_trigger = trigger
        if dimension_source not in ("From processed image", "Manual canvas"):
            raise ValueError("Choose From processed image or Manual canvas dimensions.")
        auto_layout = output_format == "MOSS JSON layout" and dimension_source == "From processed image"
        prepared, width, height = prepare_caption_image(image, image_index, image_megapixels, resize_mode, resize_method, auto_layout)
        if auto_layout:
            canvas_width, canvas_height = width, height
        diagnostics = {}
        text = caption_image(prepared, instructions, character_trigger, detail, 0,
                             max_tokens, model_name=local_model, clip=clip, language_style=language_style,
                             output_format=output_format, canvas_width=canvas_width, canvas_height=canvas_height,
                             unload_after_generation=unload_after_generation, appearance=appearance, diagnostics=diagnostics)
        if output_format == "MOSS JSON layout":
            width, height = canvas_width, canvas_height
        report = appearance_report(appearance, diagnostics.get("issues", []), on_override_mismatch,
                                   diagnostics.get("attempts", 0), diagnostics.get("correction_attempted", False), text,
                                   diagnostics.get("edits"), diagnostics.get("model_output"))
        report["source"] = source_name
        return {"ui": {"text": [text], "json_preview": [output_format != "Plain text"], "atelier_report": [report]},
                "result": reported_result((text, width, height, prepared), report)}
