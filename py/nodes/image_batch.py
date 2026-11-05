"""Folder selection using native ComfyUI image-list mapping, without GPU parallelism."""
from pathlib import Path
import fnmatch
import json
import re

from .base import BaseNode

EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff", ".gif"}
MODES = ["One image per queued run", "All selected images as list"]


def input_directory():
    import folder_paths
    return Path(folder_paths.get_input_directory())


def folder_choices():
    try:
        children = sorted(path.name for path in input_directory().iterdir() if path.is_dir())
    except (ImportError, OSError):
        children = []
    return ["Input directory"] + ["input/" + name for name in children] + ["Custom folder"]


def select_files(folder, custom_folder, pattern, recursive, batch_mode, index, wrap_index, max_images):
    if batch_mode not in MODES:
        raise ValueError("Choose one image per queued run or all selected images as list.")
    if not isinstance(index, int) or isinstance(index, bool) or index < 0:
        raise ValueError("Image index must be a nonnegative integer; the first image is 0.")
    if not isinstance(max_images, int) or not 1 <= max_images <= 512:
        raise ValueError("Max images must be between 1 and 512.")
    if folder == "Custom folder":
        if not custom_folder.strip(): raise ValueError("Enter the image folder path in Custom folder.")
        root = Path(custom_folder).expanduser().resolve()
    elif folder == "Input directory":
        root = input_directory().resolve()
    elif folder.startswith("input/"):
        base = input_directory().resolve()
        root = (base / folder[6:]).resolve()
        if not root.is_relative_to(base): raise ValueError("Choose a subfolder of ComfyUI input, or use Custom folder.")
    else:
        raise ValueError("Choose an input folder or Custom folder.")
    if not root.is_dir(): raise ValueError("Image folder does not exist: " + str(root))
    patterns = [part.strip().casefold() for part in pattern.split(",") if part.strip()] or ["*"]
    paths = root.rglob("*") if recursive else root.iterdir()
    files = [path for path in paths if path.is_file() and path.suffix.casefold() in EXTENSIONS and
             any(fnmatch.fnmatchcase(path.relative_to(root).as_posix().casefold(), item) for item in patterns)]
    files.sort(key=lambda path: [int(part) if part.isdigit() else part.casefold()
                               for part in re.split(r"(\d+)", path.relative_to(root).as_posix())])
    if not files: raise ValueError("No supported image files match this folder/pattern.")
    total = len(files)
    if batch_mode == MODES[0]:
        if index >= total and not wrap_index:
            raise ValueError(f"Image index {index} is past this folder's {total} images. Select 0–{total-1}, or enable Wrap index.")
        selected = [files[index % total]]
    else:
        selected = files[:max_images]
    return root, files, selected


class DanbooruTagsTransformerImageBatchSelector(BaseNode):
    CATEGORY = "Prompt Atelier/Vision"

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "folder": (folder_choices(), {"tooltip": "Choose ComfyUI input, one of its subfolders, or Custom folder. Folder paths refer to the computer/server running ComfyUI."}),
            "custom_folder": ("STRING", {"default": "", "tooltip": "Absolute or server-relative image directory. Only used with Custom folder. On RunPod this is a pod path, not a Windows path."}),
            "pattern": ("STRING", {"default": "*", "tooltip": "File filter, e.g. *.png or *.jpg,*.png. PNG/JPEG/WebP/BMP/TIFF/GIF are supported; animated files use their first frame."}),
            "recursive": ("BOOLEAN", {"default": False, "tooltip": "Include nested image folders."}),
            "batch_mode": (MODES, {"default": MODES[0], "tooltip": "One image per queued run uses Index; native increment advances it for the next queued run. All selected images as list sends a native list, so Image to Text processes each image sequentially in one run. This is not parallel GPU inference."}),
            "index": ("INT", {"default": 0, "min": 0, "max": 2**32-1, "control_after_generate": "increment", "tooltip": "First image is 0, in natural filename order. Keep the native control on increment and queue multiple runs to advance one file per run. Fixed repeats the same file."}),
            "wrap_index": ("BOOLEAN", {"default": True, "tooltip": "Wrap back to the first image when Index passes the folder length. Off gives an actionable end-of-folder message."}),
            "max_images": ("INT", {"default": 16, "min": 1, "max": 512, "tooltip": "Maximum files in list mode. Decoded images are held in CPU memory; use one-per-queue mode for large folders. The preview shows selected versus available files."}),
        }}

    RETURN_TYPES = ("IMAGE", "STRING", "INT", "STRING")
    RETURN_NAMES = ("image", "filename", "count", "selection")
    OUTPUT_IS_LIST = (True, True, False, False)
    FUNCTION = "load"
    OUTPUT_NODE = True

    def load(self, folder="Input directory", custom_folder="", pattern="*", recursive=False,
             batch_mode=MODES[0], index=0, wrap_index=True, max_images=16):
        from PIL import Image, ImageOps
        import numpy as np
        import torch
        root, files, selected = select_files(folder, custom_folder, pattern, recursive, batch_mode, index, wrap_index, max_images)
        images = []
        for path in selected:
            try:
                with Image.open(path) as opened:
                    rgb = ImageOps.exif_transpose(opened).convert("RGB")
                    image = torch.from_numpy(np.asarray(rgb, dtype=np.float32).copy() / 255.0).unsqueeze(0)
            except (OSError, ValueError) as error:
                raise ValueError("Could not read image " + path.name + ": " + str(error)) from None
            images.append(image)
        names = [path.relative_to(root).as_posix() for path in selected]
        info = f"Selected {len(selected)} of {len(files)} images · {batch_mode}\n" + "\n".join(names[:12])
        if len(names) > 12: info += f"\n… and {len(names)-12} more"
        return {"ui": {"text": [info]}, "result": (images, names, len(selected), info)}

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        root, files, selected = select_files(**kwargs)
        return json.dumps([(str(path), path.stat().st_size, path.stat().st_mtime_ns) for path in files] +
                          [(str(path.relative_to(root)),) for path in selected])
