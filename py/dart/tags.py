"""Sequence operations preserve multi-token tags and protect control tokens."""

def split_tags(text):
    tags, current = [], []
    depth = 0
    escaped = False
    for char in text:
        if char in ",\n" and depth == 0 and not escaped:
            if "".join(current).strip():
                tags.append("".join(current).strip())
            current = []
        else:
            current.append(char)
            if not escaped:
                if char in "([":
                    depth += 1
                elif char in ")]":
                    depth = max(0, depth - 1)
        escaped = char == "\\" and not escaped
    if "".join(current).strip():
        tags.append("".join(current).strip())
    return tags


def encode_tags(tokenizer, text):
    special_ids = set(tokenizer.all_special_ids)
    sequences = []
    for tag in split_tags(text):
        ids = tokenizer(tag, add_special_tokens=False)["input_ids"]
        if ids and not special_ids.intersection(ids):
            sequences.append(ids)
    return sequences


def remove_tags(tokenizer, token_ids, text):
    ids = [int(token) for token in token_ids]
    for sequence in encode_tags(tokenizer, text):
        remaining = []
        index = 0
        while index < len(ids):
            if ids[index:index + len(sequence)] == sequence:
                index += len(sequence)
            else:
                remaining.append(ids[index])
                index += 1
        ids = remaining
    return ids


def keep_tags(prompt, required):
    """Required text is appended verbatim, retaining weights and LoRA syntax."""
    existing = {tag.casefold() for tag in split_tags(prompt)}
    additions = []
    for tag in split_tags(required):
        if tag.casefold() not in existing:
            additions.append(tag)
            existing.add(tag.casefold())
    return ", ".join(part for part in (prompt.strip().strip(","), ", ".join(additions)) if part)
