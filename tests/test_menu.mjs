import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";
import { connectionsFor, resolveSlot } from "../web/connections.mjs";

let extension, menu, previewMessage;
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
    addTextPreviewWidgets() {}, updateTextPreviewWidgets(node, message) { previewMessage = message; }, convertToInput() {},
    LiteGraph: {
        registered_node_types: {
            CLIPTextEncode: { title: "CLIP Text Encode" }, PreviewAny: { title: "Preview as Text" },
            DanbooruTagsTransformerComposePromptV3: { title: "Dart Compose Prompt V3" },
            DanbooruTagsTransformerLoader: { title: "Dart Load" },
            DanbooruTagsTransformerDescribeImage: { title: "Dart Describe Image" },
        },
        ContextMenu: class { constructor(entries) { menu = entries; } },
        createNode(type) {
            return { type, inputs: [{ name: "text" }, { name: "general" }, { name: "source_tags" }],
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
canvas.showConnectionMenu({ nodeFrom: { ...source, type: "DanbooruTagsTransformerGenerate" }, slotFrom: 0, e: {} });
assert.equal(menu[0].content, "Dart Describe Image");
menu[0].callback();
assert.equal(connections[3].args[1].type, "DanbooruTagsTransformerDescribeImage");
assert.equal(connections[3].args[2], 2); // source_tags, not description or another STRING.
class Describe {
    constructor() {
        this.size = [380, 500];
        this.properties = {};
        this.inputs = ["canvas_width", "canvas_height", "layout_json"].map((name) => ({name,
            link: 123, draw() { return "drawn"; }, isValidTarget() { return true; }}));
        this.widgets = ["backend", "local_model", "endpoint", "model", "timeout", "api_key_env", "keep_tags", "avoid", "target", "canvas_width", "canvas_height", "layout_json", "preview_mode"]
            .map((name) => ({ name, value: name === "backend" ? "Local model" : "" }));
    }
    setSize(size) { this.size = size; }
    computeSize() { return [400, 500]; }
    setDirtyCanvas() {}
    getSlotInPosition() { return {input: this.inputs[0]}; }
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
assert.equal(describeNode.widgets.find((w) => w.name === "canvas_width").hidden, true);
assert.equal(describeNode.inputs[0].draw(), undefined);
assert.equal(describeNode.inputs[0].isValidTarget(), false);
assert.equal(describeNode.getSlotInPosition(), null);
const targetControl = describeNode.widgets.find((w) => w.name === "target");
targetControl.value = "MOSS JSON layout";
targetControl.callback("MOSS JSON layout");
assert.equal(describeNode.widgets.find((w) => w.name === "canvas_width").hidden, false);
assert.equal(describeNode.widgets.find((w) => w.name === "layout_json").hidden, false);
assert.equal(describeNode.inputs[0].draw(), "drawn");
assert.equal(describeNode.inputs[0].isValidTarget(), true);
assert.equal(describeNode.inputs[0].link, 123);
assert.equal(describeNode.getSlotInPosition().input.name, "canvas_width");
describeNode.onExecuted({text: ['{\n  "summary": {}\n}'], moss_json: [true]});
assert.equal(previewMessage.text[0], '```json\n{\n  "summary": {}\n}\n```');
const previewMode = describeNode.widgets.find((w) => w.name === "preview_mode");
previewMode.value = false;
previewMode.callback();
assert.equal(previewMessage.text[0], '{\n  "summary": {}\n}');
targetControl.value = "Natural language";
targetControl.callback("Natural language");
assert.equal(describeNode.widgets.find((w) => w.name === "layout_json").hidden, true);
describeNode.widgets.find((w) => w.name === "local_model").value = "Automatic";
const saved = {};
describeNode.onSerialize(saved);
describeNode.widgets.find((w) => w.name === "local_model").value = "shifted value";
describeNode.onConfigure(saved);
assert.equal(describeNode.widgets.find((w) => w.name === "local_model").value, "Automatic");
console.log("Drag menus create and connect the intended node sockets; other plugins retain their menu.");
