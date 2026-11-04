const prefix = "DanbooruTagsTransformer";
const node = (name, slot) => ({ type: prefix + name, slot });
const preview = { type: "PreviewAny", slot: "source" };
const encode = { type: "CLIPTextEncode", slot: "text" };
const composers = (slot) => [node("ComposePromptV3", slot), node("ComposePromptV2", slot), node("ComposePrompt", slot)];
const generators = (slot) => [node("Generate", slot), node("GenerateAdvanced", slot)];

export function connectionsFor(type, name, slotType, isOutput) {
    if (!type?.startsWith(prefix)) return [];
    if (!isOutput) {
        if (name === "model") return [node("Loader", 0)];
        if (name === "tokenizer") return [node("Loader", 1)];
        if (name === "setting") return [node("GenerationConfig", 0)];
        if (name === "token_ids") return [node("GenerateAdvanced", 0)];
        if (name === "clip") return [{ type: "CLIPLoader", slot: 0 }];
        if (name === "prompt" && /Generate/.test(type)) return composers(0);
        const describeSlots = { general: 1, copyright: 2, character: 3 };
        if (name in describeSlots) return [node("DescribeImage", describeSlots[name])];
        return [];
    }
    if (slotType === "DART_MODEL") return generators("model");
    if (slotType === "DART_TOKENIZER") return [
        ...generators("tokenizer"), node("Decode", "tokenizer"),
        node("DecodeBySplitedParts", "tokenizer"), node("BanTagsFromRegex", "tokenizer"),
    ];
    if (slotType === "DART SETTING") return generators("setting");
    if (slotType === "DART_TOKEN_IDS") return [
        node("Decode", "token_ids"), node("DecodeBySplitedParts", "token_ids"),
        node("RearrangedByAnimagine", "token_ids"), node("RemoveTagToken", "token_ids"),
    ];
    if (type === prefix + "DescribeImage") {
        if (name === "general_tags") return [...composers("general"), preview];
        if (name === "copyright" || name === "character") return [...composers(name), preview];
        if (name === "scene_json") return [preview];
        return [encode, preview];
    }
    if (/ComposePrompt/.test(type)) return [...generators("prompt"), preview];
    if (/BanTagsFromRegex/.test(type)) return [...generators("ban_tags"), preview];
    if (slotType === "STRING") return [encode, preview];
    return [];
}

export function resolveSlot(slots, value) {
    const index = typeof value === "number" ? value : slots.findIndex(
        (slot) => slot === value || slot.name === (typeof value === "string" ? value : value?.name),
    );
    return { index, slot: slots[index] };
}
