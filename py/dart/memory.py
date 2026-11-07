"""Targeted assistant-model offloading through the native model manager."""
from contextlib import contextmanager
import logging


def release_assistant_model(clip):
    if getattr(clip, 'is_remote', False) is True:
        return
    import comfy.model_management as management
    patcher = getattr(clip, "patcher", None)
    if patcher is None:
        raise RuntimeError("The connected assistant CLIP has no model patcher for targeted offloading.")
    unload = getattr(management, "unload_model_and_clones", None)
    if not callable(unload):
        raise RuntimeError("This ComfyUI version does not support targeted assistant offloading. Update ComfyUI or disable Unload assistant model.")
    unload(patcher, unload_additional_models=True, all_devices=True)
    management.soft_empty_cache()


def prepare_assistant_memory(clip, reserve_gb=2.0):
    """Ask native management for headroom, without evicting this encoder or clearing all VRAM."""
    patcher = getattr(clip, 'patcher', None)
    if patcher is None:
        return
    import comfy.model_management as management
    device = patcher.load_device
    if getattr(device, 'type', str(device)) == 'cpu':
        return
    loaded = management.current_loaded_models
    own = [entry for entry in loaded if entry.model is patcher or
           (getattr(entry.model, 'clone_base_uuid', None) is not None and
            entry.model.clone_base_uuid == getattr(patcher, 'clone_base_uuid', None))]
    resident = max((entry.model.loaded_size() for entry in own), default=0)
    required = max(0, patcher.model_size() - resident) + int(reserve_gb * 1024 ** 3)
    logging.info('Prompt Mage: preparing assistant VRAM; requesting %.1f GB free, preserving the shared encoder.', required / 1024 ** 3)
    management.free_memory(required, device, keep_loaded=own)
    management.soft_empty_cache()


@contextmanager
def offload_after(clip, enabled=False, release_on_error=False):
    try:
        yield clip
    except BaseException:
        if enabled or release_on_error:
            try:
                release_assistant_model(clip)
            except Exception:
                logging.exception("Assistant offloading failed while handling a generation error")
        raise
    else:
        if enabled:
            release_assistant_model(clip)
