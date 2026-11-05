"""Targeted assistant-model offloading through the native model manager."""
from contextlib import contextmanager
import logging


def release_assistant_model(clip):
    import comfy.model_management as management
    patcher = getattr(clip, "patcher", None)
    if patcher is None:
        raise RuntimeError("The connected assistant CLIP has no model patcher for targeted offloading.")
    unload = getattr(management, "unload_model_and_clones", None)
    if not callable(unload):
        raise RuntimeError("This ComfyUI version does not support targeted assistant offloading. Update ComfyUI or disable Unload assistant model.")
    unload(patcher, unload_additional_models=True, all_devices=True)
    management.soft_empty_cache()


@contextmanager
def offload_after(clip, enabled=False):
    try:
        yield clip
    except BaseException:
        if enabled:
            try:
                release_assistant_model(clip)
            except Exception:
                logging.exception("Assistant offloading failed while handling a generation error")
        raise
    else:
        if enabled:
            release_assistant_model(clip)
