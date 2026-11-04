import { app } from "../../scripts/app.js";
import { convertToInput } from "../../extensions/core/widgetInputs.js";
import { addTextPreviewWidgets, updateTextPreviewWidgets } from "../../extensions/core/textPreviewWidgets.js";
import { connectionsFor, resolveSlot } from "./connections.mjs";

const labels = new Map();

function updateDescribeControls(node) {
    const server = node.widgets?.find((widget) => widget.name === "backend")?.value === "Chat server";
    for (const widget of node.widgets || []) {
        if (["endpoint", "model", "timeout", "api_key_env"].includes(widget.name)) widget.hidden = !server;
        if (widget.name === "local_model") widget.hidden = server;
    }
    const size = node.computeSize();
    node.setSize([Math.max(420, node.size[0], size[0]), size[1]]);
    node.setDirtyCanvas(true, true);
}

app.registerExtension({
    name: "Dart.ConnectionsAndPreview",
    beforeRegisterNodeDef(nodeType, nodeData) {
        labels.set(nodeData.name, nodeData.display_name || nodeData.name);
        if (nodeData.name !== "DanbooruTagsTransformerDescribeImage") return;
        const created = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            created?.apply(this, arguments);
            addTextPreviewWidgets(this);
            const preview = this.widgets?.find((widget) => widget.name === "preview_text");
            if (preview) preview.options.getMinHeight = () => 120;
            const names = { backend: "Assistant", local_model: "Local model", endpoint: "Server URL",
                model: "Chat model", keep_tags: "Keep exact tags", avoid: "Avoid" };
            for (const widget of this.widgets || []) {
                if (names[widget.name]) widget.label = names[widget.name];
            }
            const backend = this.widgets?.find((widget) => widget.name === "backend");
            if (backend) {
                const callback = backend.callback;
                backend.callback = (...args) => {
                    callback?.apply(backend, args);
                    updateDescribeControls(this);
                };
            }
            updateDescribeControls(this);
        };
        const configured = nodeType.prototype.onConfigure;
        nodeType.prototype.onConfigure = function () {
            configured?.apply(this, arguments);
            updateDescribeControls(this);
        };
        const executed = nodeType.prototype.onExecuted;
        nodeType.prototype.onExecuted = function (message) {
            executed?.apply(this, arguments);
            updateTextPreviewWidgets(this, message);
        };
    },
    setup() {
        const canvas = app.canvas;
        const original = canvas.showConnectionMenu;
        canvas.showConnectionMenu = function (options) {
            const source = options?.nodeFrom || options?.nodeTo;
            if (!source || options.afterRerouteId != null) return original.apply(this, arguments);
            const isOutput = Boolean(options.nodeFrom);
            const { index, slot } = resolveSlot(isOutput ? source.outputs : source.inputs,
                isOutput ? options.slotFrom : options.slotTo);
            if (!slot) return original.apply(this, arguments);
            const candidates = connectionsFor(source.comfyClass || source.type, slot.name, slot.type, isOutput)
                .filter(({ type }) => LiteGraph.registered_node_types[type]);
            if (!candidates.length) return original.apply(this, arguments);
            const position = this.convertEventToCanvasOffset(options.e);
            const graph = source.graph;
            const entries = candidates.map(({ type, slot: targetSlot }) => ({
                content: labels.get(type) || LiteGraph.registered_node_types[type].title || type,
                callback: () => {
                    const next = LiteGraph.createNode(type);
                    graph.beforeChange();
                    try {
                        graph.add(next);
                        next.pos = position;
                        let targetIndex = typeof targetSlot === "number" ? targetSlot : next.findInputSlot(targetSlot);
                        if (isOutput && targetIndex < 0) {
                            const widget = next.widgets?.find((widget) => widget.name === targetSlot);
                            if (widget) convertToInput(next, widget);
                            targetIndex = next.findInputSlot(targetSlot);
                        }
                        if (isOutput) source.connect(index, next, targetIndex);
                        else next.connect(targetIndex, source, index);
                    } finally {
                        graph.afterChange();
                    }
                    this.setDirty(true, true);
                },
            }));
            entries.push(null, { content: "More compatible nodes…", callback: () => original.call(this, options) });
            return new LiteGraph.ContextMenu(entries, { event: options.e, title: `${slot.name} | ${slot.type}` });
        };
    },
});
