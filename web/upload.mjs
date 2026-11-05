const collections = new WeakMap();
const supported = /\.(png|jpe?g|webp|bmp|tiff?|gif)$/i;

export function readCollection(value) {
    try { const list = JSON.parse(value); return Array.isArray(list) && list.every(name => typeof name === "string") ? list : []; }
    catch { return []; }
}

export async function uploadImage(file, api, subfolder) {
    const data = new FormData();
    data.append("image", file, file.name);
    data.append("type", "input");
    data.append("subfolder", subfolder);
    const response = await api.fetchApi("/upload/image", {method:"POST", body:data});
    if (!response.ok) throw new Error(`Server rejected upload (${response.status}). Check ComfyUI's upload-size limit and connection.`);
    const result = await response.json();
    if (result.type !== "input" || typeof result.name !== "string" || !result.name || typeof result.subfolder !== "string") throw new Error("Server returned an invalid upload result.");
    return [result.subfolder, result.name].filter(Boolean).join("/");
}

export function installUploadWidget(node, api) {
    if (collections.has(node)) return;
    const manifest = node.widgets.find(widget => widget.name === "images");
    if (!manifest) return;
    manifest.hidden = true;
    const root = document.createElement("section");
    root.className = "atelier-upload";
    root.setAttribute("aria-label", "Uploaded image collection");
    const toolbar = document.createElement("div"); toolbar.className = "atelier-upload-toolbar";
    const add = document.createElement("button"); add.type = "button"; add.textContent = "＋ Upload images";
    add.title = "Select multiple images from your computer. Files are uploaded to this ComfyUI server, including RunPod.";
    const clear = document.createElement("button"); clear.type = "button"; clear.textContent = "Clear list";
    clear.title = "Remove all images from this node's list. Uploaded server files are kept.";
    const picker = document.createElement("input"); picker.type = "file"; picker.multiple = true;
    picker.accept = ".png,.jpg,.jpeg,.webp,.bmp,.tif,.tiff,.gif"; picker.hidden = true;
    const status = document.createElement("div"); status.className = "atelier-upload-status";
    status.setAttribute("role", "status"); status.setAttribute("aria-live", "polite");
    const list = document.createElement("div"); list.className = "atelier-upload-list";
    toolbar.append(add, clear); root.append(toolbar, picker, status, list);
    let busy = false;
    const changed = names => {
        manifest.value = JSON.stringify(names);
        manifest.callback?.(manifest.value);
        node.graph?.change?.();
        render();
        node.setDirtyCanvas?.(true, true);
    };
    const render = () => {
        const names = readCollection(manifest.value);
        root.dataset.theme = node.properties?.atelier_theme === "studio" ? "studio" : "ember";
        list.replaceChildren();
        status.textContent = names.length ? `${names.length} ${names.length === 1 ? "image" : "images"} · list order is processing order` : "Select several files or drop images here. Then connect image → Image to Text.";
        clear.disabled = busy || !names.length;
        add.disabled = busy;
        for (const [index, name] of names.entries()) {
            const row = document.createElement("div"); row.className = "atelier-upload-row";
            const image = document.createElement("img"); image.loading = "lazy"; image.alt = name.split("/").pop();
            const parts = name.split("/"); const filename = parts.pop();
            image.src = api.apiURL("/view?" + new URLSearchParams({filename,subfolder:parts.join("/"),type:"input"}));
            const label = document.createElement("span"); label.textContent = `${index}: ${filename}`; label.title = name;
            const controls = document.createElement("div"); controls.className = "atelier-upload-actions";
            for (const [text, title, action, disabled] of [
                ["↑", `Move image ${index} up`, () => { [names[index-1],names[index]] = [names[index],names[index-1]]; changed(names); }, index === 0],
                ["↓", `Move image ${index} down`, () => { [names[index+1],names[index]] = [names[index],names[index+1]]; changed(names); }, index === names.length-1],
                ["×", `Remove image ${index} from list; keep server file`, () => changed(names.filter((_,i) => i !== index)), false],
            ]) {
                const button = document.createElement("button"); button.type = "button"; button.textContent = text; button.title = title; button.setAttribute("aria-label",title); button.disabled = busy || disabled;
                button.addEventListener("click", action); controls.append(button);
            }
            row.append(image,label,controls); list.append(row);
        }
    };
    const upload = async files => {
        if (busy || !files.length) return;
        const names = readCollection(manifest.value);
        const accepted = [...files].filter(file => supported.test(file.name));
        const errors = files.length === accepted.length ? [] : ["Unsupported files skipped; use PNG/JPEG/WebP/BMP/TIFF/GIF."];
        const pending = accepted.slice(0,512-names.length);
        if (pending.length < accepted.length) errors.push("Collection limit is 512 images. Remaining files were skipped.");
        busy = true; render();
        // Separate upload sessions avoid overwriting an existing node's files.
        const subfolder = "prompt-atelier/" + crypto.randomUUID();
        try {
            for (const [index,file] of pending.entries()) {
                status.textContent = `Uploading ${index+1}/${pending.length}: ${file.name}. Wait for completion before queuing.`;
                try { const path = await uploadImage(file,api,subfolder); if (!names.includes(path)) names.push(path); }
                catch (error) { errors.push(`${file.name}: ${error.message}`); }
                // Save each success immediately; a later failed upload does not discard earlier files.
                manifest.value = JSON.stringify(names);
                node.graph?.change?.();
            }
        } finally {
            busy = false; changed(names); picker.value = "";
            if (errors.length) status.textContent = `${names.length} images ready. ` + errors.join("\n");
        }
    };
    add.addEventListener("click", () => picker.click());
    clear.addEventListener("click", () => changed([]));
    picker.addEventListener("change", () => upload([...picker.files]));
    root.addEventListener("dragover", event => {event.preventDefault(); event.stopPropagation();});
    root.addEventListener("drop", event => {event.preventDefault(); event.stopPropagation(); upload([...event.dataTransfer.files]);});
    root.addEventListener("wheel", event => event.stopPropagation());
    const widget = node.addDOMWidget("atelier_upload", "ATELIER_UPLOAD", root, {serialize:false,getMinHeight:()=>300,getMaxHeight:()=>300});
    widget.serialize = false;
    collections.set(node,{render});
    render();
}

export function refreshUploadWidget(node) { collections.get(node)?.render(); }
