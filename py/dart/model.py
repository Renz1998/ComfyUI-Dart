from copy import deepcopy
import threading

import torch
from transformers import AutoModelForCausalLM, __version__ as transformers_version
from packaging.version import Version

from .tags import encode_tags


class DartModel:
    _generation_lock = threading.Lock()

    def __init__(self, model_name, device="cpu", dtype="auto", **load_options):
        if device == "auto":
            device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = torch.device(device)
        if dtype == "auto":
            dtype = "float32" if self.device.type == "cpu" else (
                "bfloat16" if torch.cuda.is_bf16_supported() else "float16"
            )
        dtype_key = "dtype" if Version(transformers_version) >= Version("4.56") else "torch_dtype"
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name, **{dtype_key: getattr(torch, dtype)}, **load_options
        ).to(self.device).eval()

    def generate(self, tokenizer, prompt, seed, config=None, ban_tags=""):
        generation_config = deepcopy(self.model.generation_config)
        generation_config.max_new_tokens = 128
        generation_config.top_k = 20
        if config is not None:
            self.update_generation_config(generation_config, config)
        if generation_config.min_new_tokens is not None and (
            generation_config.min_new_tokens > generation_config.max_new_tokens
        ):
            raise ValueError("Minimum new tokens must not exceed maximum new tokens.")
        generation_config.do_sample = generation_config.temperature != 0
        if not generation_config.do_sample:
            generation_config.temperature = 1.0
            generation_config.top_p = 1.0
            generation_config.top_k = 50

        inputs = tokenizer.tokenizer(prompt, return_tensors="pt").to(self.device)
        generation_config.bad_words_ids = encode_tags(tokenizer.tokenizer, ban_tags) or None
        cuda_devices = []
        if self.device.type == "cuda":
            cuda_devices = [self.device.index if self.device.index is not None else torch.cuda.current_device()]
        with self._generation_lock, torch.random.fork_rng(devices=cuda_devices):
            torch.random.default_generator.manual_seed(seed)
            for device in cuda_devices:
                torch.cuda.default_generators[device].manual_seed(seed)
            with torch.inference_mode():
                outputs = self.model.generate(
                    **inputs,
                    generation_config=generation_config,
                )
        return outputs.cpu()

    @classmethod
    def update_generation_config(cls, generation_config, config):
        for key in ("max_new_tokens", "min_new_tokens", "temperature", "top_p", "top_k", "num_beams"):
            if key in config:
                setattr(generation_config, key, config[key])
        return generation_config
