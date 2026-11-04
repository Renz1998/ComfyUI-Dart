import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";
import { convertToInput } from "../../extensions/core/widgetInputs.js";
import { addTextPreviewWidgets, updateTextPreviewWidgets } from "../../extensions/core/textPreviewWidgets.js";
import { connectionsFor, resolveSlot } from "./connections.mjs";
import { installDesign, configureDesign, toggleDesign, setDesignState, updateDesignBackend } from "./design.mjs";

const labels = new Map();

function updateDescribeControls(node) {
    const server = node.widgets?.find((widget) => widget.name === "backend")?.value === "Chat server";
    for (const widget of node.widgets || []) {
        if (["endpoint", "model", "timeout", "api_key_env"].includes(widget.name)) widget.hidden = !server;
        if (widget.name === "local_model") widget.hidden = server;
    }
    updateDesignBackend(node, server);
    const size = node.computeSize();
    node.setSize([Math.max(420, node.size[0], size[0]), size[1]]);
    node.setDirtyCanvas(true, true);
}

app.registerExtension({
    name: "Dart.ConnectionsAndPreview",
    beforeRegisterNodeDef(nodeType, nodeData) {
        labels.set(nodeData.name, nodeData.display_name || nodeData.name);
        if (!nodeData.name.startsWith("DanbooruTagsTransformer")) return;
        const baseCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            baseCreated?.apply(this, arguments);
            installDesign(this, nodeData);
            for (const widget of this.widgets || []) {
                const spec = nodeData.input?.required?.[widget.name] || nodeData.input?.optional?.[widget.name];
                const tip = spec?.[1]?.tooltip;
                if (tip) widget.tooltip = tip;
                if (widget.name === "control_after_generate") widget.tooltip = "fixed keeps the seed; increment/decrement changes it by one; randomize picks a new seed for the next run. Deterministic modes may still produce the same text.";
            }
        };
        const baseConfigured = nodeType.prototype.onConfigure;
        nodeType.prototype.onConfigure = function () {
            baseConfigured?.apply(this, arguments);
            configureDesign(this);
        };
        const baseExecuted = nodeType.prototype.onExecuted;
        nodeType.prototype.onExecuted = function () {
            baseExecuted?.apply(this, arguments);
            setDesignState(this, "done");
        };
        const baseMenu = nodeType.prototype.getExtraMenuOptions;
        nodeType.prototype.getExtraMenuOptions = function (_, options) {
            baseMenu?.apply(this, arguments);
            options.push({ content: this.properties.dart_design === false ? "Enable DART design" : "Disable DART design", callback: () => toggleDesign(this) });
        };
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
        let activeNode;
        api.addEventListener("executing", ({ detail }) => {
            if (activeNode) setDesignState(activeNode, "done");
            const id = detail && typeof detail === "object" ? detail.node : detail;
            activeNode = id != null ? app.graph.getNodeById(id) : null;
            if (activeNode) setDesignState(activeNode, "running");
        });
        for (const event of ["execution_error", "execution_interrupted"]) {
            api.addEventListener(event, () => {
                if (activeNode) setDesignState(activeNode, "error");
                activeNode = null;
            });
        }
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
