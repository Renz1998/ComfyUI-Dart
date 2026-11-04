import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";
import { connectionsFor, resolveSlot } from "../web/connections.mjs";

let extension, menu;
const connections = [];
const graph = { beforeChange() {}, afterChange() {}, add(node) { node.graph = this; } };
class Canvas {
    showConnectionMenu() { return "original"; }
    convertEventToCanvasOffset() { return [100, 200]; }
    setDirty() {}
}
const context = {
    app: { canvas: new Canvas(), registerExtension(value) { extension = value; } },
    api: { addEventListener() {} },
    installDesign() {}, configureDesign() {}, toggleDesign() {}, setDesignState() {}, updateDesignBackend() {},
    connectionsFor, resolveSlot, LGraphCanvas: Canvas,
    addTextPreviewWidgets() {}, updateTextPreviewWidgets() {}, convertToInput() {},
    LiteGraph: {
        registered_node_types: {
            CLIPTextEncode: { title: "CLIP Text Encode" }, PreviewAny: { title: "Preview as Text" },
            DanbooruTagsTransformerComposePromptV3: { title: "Dart Compose Prompt V3" },
            DanbooruTagsTransformerLoader: { title: "Dart Load" },
        },
        ContextMenu: class { constructor(entries) { menu = entries; } },
        createNode(type) {
            return { type, inputs: [{ name: "text" }, { name: "general" }],
                findInputSlot(name) { return this.inputs.findIndex((slot) => slot.name === name); },
                connect(...args) { connections.push({ from: type, args }); } };
        },
    },
};
vm.runInNewContext(readFileSync(new URL("../web/dart.js", import.meta.url), "utf8").replace(/^import .*;\r?\n/gm, ""), context);
extension.setup();
const canvas = context.app.canvas;
const source = { type: "DanbooruTagsTransformerDescribeImage", graph,
    outputs: [{ name: "prompt", type: "STRING" }, { name: "general_tags", type: "STRING" }],
    connect(...args) { connections.push({ from: "describe", args }); } };
canvas.showConnectionMenu({ nodeFrom: source, slotFrom: 0, e: {} });
assert.equal(menu[0].content, "CLIP Text Encode");
menu[0].callback();
assert.equal(connections[0].args[0], 0);
assert.equal(connections[0].args[1].type, "CLIPTextEncode");
assert.equal(connections[0].args[2], 0);
canvas.showConnectionMenu({ nodeFrom: source, slotFrom: source.outputs[1], e: {} });
assert.equal(menu[0].content, "Dart Compose Prompt V3");
menu[0].callback();
assert.equal(connections[1].args[2], 1); // The actual general input, not an arbitrary STRING.
const target = { type: "DanbooruTagsTransformerGenerate", graph, inputs: [{ name: "tokenizer", type: "DART_TOKENIZER" }] };
canvas.showConnectionMenu({ nodeTo: target, slotTo: 0, e: {} });
menu[0].callback();
assert.equal(connections[2].from, "DanbooruTagsTransformerLoader");
assert.equal(connections[2].args[0], 1); // Loader's tokenizer output, not its model output.
assert.equal(connections[2].args[2], 0);
assert.equal(canvas.showConnectionMenu({ nodeFrom: { ...source, type: "OtherPlugin" }, slotFrom: 0, e: {} }), "original");
class Describe {
    constructor() {
        this.size = [380, 500];
        this.widgets = ["backend", "local_model", "endpoint", "model", "timeout", "api_key_env", "keep_tags", "avoid"]
            .map((name) => ({ name, value: name === "backend" ? "Local model" : "" }));
    }
    setSize(size) { this.size = size; }
    computeSize() { return [400, 500]; }
    setDirtyCanvas() {}
}
extension.beforeRegisterNodeDef(Describe, {name: "DanbooruTagsTransformerDescribeImage"});
const describeNode = new Describe();
describeNode.onNodeCreated();
assert.equal(describeNode.widgets.find((w) => w.name === "endpoint").hidden, true);
assert.equal(describeNode.widgets.find((w) => w.name === "local_model").hidden, false);
const backend = describeNode.widgets.find((w) => w.name === "backend");
backend.value = "Chat server";
backend.callback("Chat server");
assert.equal(describeNode.widgets.find((w) => w.name === "endpoint").hidden, false);
assert.equal(describeNode.widgets.find((w) => w.name === "local_model").hidden, true);
assert.equal(backend.label, "Assistant");
assert.equal(describeNode.size[0], 420);
console.log("Drag menus create and connect the intended node sockets; other plugins retain their menu.");
