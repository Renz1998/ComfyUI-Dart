from pathlib import Path

from huggingface_hub import hf_hub_download
from tokenizers import Tokenizer
from transformers import PreTrainedTokenizerFast


def load_tag_tokenizer(model_name, special_tags, **load_options):
    path = Path(model_name)
    if path.is_dir():
        filename = path / "tokenizer.json"
    else:
        filename = hf_hub_download(model_name, "tokenizer.json", **load_options)
    backend = Tokenizer.from_file(str(filename))
    if type(backend.model).__name__ != "WordLevel":
        raise ValueError("DART requires a WordLevel tag tokenizer.")
    vocab = backend.get_vocab()
    missing = [tag for tag in special_tags if tag not in vocab]
    if missing:
        raise ValueError("This DART tokenizer lacks expected control tokens: " + ", ".join(missing))
    # Load the published vocabulary directly: the old remote tokenizer subclass
    # builds an incorrect BPE backend on Transformers 5.
    return PreTrainedTokenizerFast(
        tokenizer_object=backend,
        bos_token="<|bos|>", eos_token="<|eos|>",
        unk_token="<|unk|>", pad_token="<|pad|>",
        additional_special_tokens=special_tags,
        clean_up_tokenization_spaces=False,
    )
