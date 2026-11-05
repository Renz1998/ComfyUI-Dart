import assert from "node:assert/strict";
import { connectionsFor, resolveSlot } from "../web/connections.mjs";

const describe = "DanbooruTagsTransformerDescribeImage";
assert.equal(connectionsFor('DanbooruTagsTransformerImageToText','image','IMAGE',false)[1].type,'DanbooruTagsTransformerImageBatchUpload');
assert.equal(connectionsFor('DanbooruTagsTransformerImageToText','image','IMAGE',false)[2].type,'DanbooruTagsTransformerImageBatchSelector');
assert.equal(connectionsFor('DanbooruTagsTransformerImageBatchUpload','image','IMAGE',true)[0].type,'DanbooruTagsTransformerImageToText');
assert.deepEqual(connectionsFor('DanbooruTagsTransformerImageBatchSelector','filename','STRING',true)[0],{type:'DanbooruTagsTransformerImageToText',slot:'source_name'});
assert.deepEqual(connectionsFor(describe,'report','STRING',true),[{type:'PreviewAny',slot:'source'}]);
assert.deepEqual(connectionsFor('DanbooruTagsTransformerImageToText','status','STRING',true),[{type:'PreviewAny',slot:'source'}]);
for (const type of [describe, 'DanbooruTagsTransformerImageToText']) {
    assert.deepEqual(connectionsFor(type, 'appearance', 'ATELIER_APPEARANCE', false), [{type:'DanbooruTagsTransformerAppearanceOverrides',slot:0}]);
}
assert.deepEqual(connectionsFor('DanbooruTagsTransformerAppearanceOverrides', 'appearance', 'ATELIER_APPEARANCE', true).map(x => x.slot), ['appearance','appearance']);
assert.deepEqual(connectionsFor("DanbooruTagsTransformerImageToText", "width", "INT", true)[0], { type: "EmptySD3LatentImage", slot: "width" });
assert.deepEqual(connectionsFor("DanbooruTagsTransformerImageToText", "height", "INT", true)[0], { type: "EmptySD3LatentImage", slot: "height" });
assert.deepEqual(connectionsFor("DanbooruTagsTransformerImageToText", "image", "IMAGE", true)[0], { type: "PreviewImage", slot: "images" });
assert.deepEqual(connectionsFor("DanbooruTagsTransformerImageToText", "description", "STRING", true)[0], { type: describe, slot: "description" });
assert.deepEqual(connectionsFor("DanbooruTagsTransformerImageToText", "image", "IMAGE", false)[0], { type: "LoadImage", slot: 0 });
assert.deepEqual(connectionsFor("DanbooruTagsTransformerGenerate", "STRING", "STRING", true)[0], { type: describe, slot: "source_tags" });
assert.deepEqual(connectionsFor(describe, "source_tags", "STRING", false)[0], { type: "DanbooruTagsTransformerGenerate", slot: 0 });
assert.deepEqual(connectionsFor(describe, "prompt", "STRING", true).map((x) => x.type), ["CLIPTextEncode", "PreviewAny"]);
assert.deepEqual(connectionsFor(describe, "general_tags", "STRING", true).slice(0, 3).map((x) => x.slot), ["general", "general", "general"]);
assert.deepEqual(connectionsFor(describe, "character", "STRING", true)[0], { type: "DanbooruTagsTransformerComposePromptV3", slot: "character" });
assert.deepEqual(connectionsFor("DanbooruTagsTransformerLoader", "DART_MODEL", "DART_MODEL", true)[0], { type: "DanbooruTagsTransformerGenerate", slot: "model" });
assert.deepEqual(connectionsFor("DanbooruTagsTransformerGenerate", "tokenizer", "DART_TOKENIZER", false)[0], { type: "DanbooruTagsTransformerLoader", slot: 1 });
assert.deepEqual(connectionsFor("DanbooruTagsTransformerGenerate", "prompt", "STRING", false)[0], { type: "DanbooruTagsTransformerComposePromptV3", slot: 0 });
assert.deepEqual(connectionsFor("AnotherPlugin", "prompt", "STRING", true), []);
const slots = [{ name: "model" }, { name: "tokenizer" }];
assert.equal(resolveSlot(slots, 0).index, 0);
assert.equal(resolveSlot(slots, slots[1]).index, 1);
assert.equal(resolveSlot(slots, "tokenizer").index, 1);
console.log("Connection suggestions passed (including first socket and named inputs).");
