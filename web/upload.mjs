import {installBatchRunner} from './batch_runner.mjs?v=1.8.1';
const collections = new WeakMap();
const supported = /\.(png|jpe?g|webp|bmp|tiff?|gif)$/i;

export function uploadSessionName(cryptoApi = globalThis.crypto) {
    return cryptoApi?.randomUUID?.() || Date.now().toString(36) + "-" + Math.random().toString(36).slice(2);
}

export function uploadSubfolder(file, base) {
    const parts = (file.webkitRelativePath || "").replaceAll("\\", "/").split("/").slice(0, -1);
    if (parts.some(part => !part || part === "." || part === ".." || part.includes(":"))) throw new Error("Invalid selected folder path.");
    return [base, ...parts].join("/");
}

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

export function installUploadWidget(node, api, app) {
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
    const folderPicker = document.createElement("input"); folderPicker.type = "file"; folderPicker.multiple = true; folderPicker.hidden = true;
    folderPicker.setAttribute("webkitdirectory", "");
    const folder = document.createElement("button"); folder.type = "button"; folder.textContent = "Choose folder";
    folder.title = "Choose an image folder on your computer, including subfolders. Your browser uploads its image files to this ComfyUI server; no RunPod folder path is needed. Best supported in Chrome/Edge.";
    const dropzone = document.createElement("button"); dropzone.type = "button"; dropzone.className = "mage-dropzone";
    dropzone.textContent = "Drop images here or click to browse";
    dropzone.title = "Select one or many images from your computer. For a local folder, use Choose folder. Uploads go to the server running this ComfyUI session.";
    const status = document.createElement("div"); status.className = "atelier-upload-status";
    status.setAttribute("role", "status"); status.setAttribute("aria-live", "polite");
    const list = document.createElement("div"); list.className = "atelier-upload-list";
    toolbar.append(add, folder, clear); root.append(dropzone, toolbar, picker, folderPicker, status, list);
    let busy = false, runner;
    const changed = names => {
        manifest.value = JSON.stringify(names);
        manifest.callback?.(manifest.value);
        node.graph?.change?.();
        render();
        node.setDirtyCanvas?.(true, true);
    };
    const render = () => {
        const locked = busy || runner?.isQueuing;
        const names = readCollection(manifest.value);
        root.dataset.theme = node.properties?.atelier_theme === "studio" ? "studio" : "ember";
        list.replaceChildren();
        status.textContent = names.length ? `${names.length} ${names.length === 1 ? "image" : "images"} · list order is processing order` : "Select several files or drop images here. Then connect image → Archmage.";
        clear.disabled = locked || !names.length;
        add.disabled = locked;
        folder.disabled = dropzone.disabled = locked;
        for (const [index, name] of names.entries()) {
            const row = document.createElement("div"); row.className = "atelier-upload-row";
            const image = document.createElement("img"); image.loading = "lazy"; image.alt = name.split("/").pop();
            const parts = name.split("/"); const filename = parts.pop();
            image.src = api.apiURL("/view?" + new URLSearchParams({filename,subfolder:parts.join("/"),type:"input"}));
            const label = document.createElement("span"); label.textContent = `${index+1}. ${filename}`; label.title = name;
            const controls = document.createElement("div"); controls.className = "atelier-upload-actions";
            for (const [text, title, action, disabled] of [
                ["↑", `Move image ${index} up`, () => { [names[index-1],names[index]] = [names[index],names[index-1]]; changed(names); }, index === 0],
                ["↓", `Move image ${index} down`, () => { [names[index+1],names[index]] = [names[index],names[index+1]]; changed(names); }, index === names.length-1],
                ["×", `Remove image ${index} from list; keep server file`, () => changed(names.filter((_,i) => i !== index)), false],
            ]) {
                const button = document.createElement("button"); button.type = "button"; button.textContent = text; button.title = title; button.setAttribute("aria-label",title); button.disabled = locked || disabled;
                button.addEventListener("click", action); controls.append(button);
            }
            row.append(image,label,controls); list.append(row);
        }
        runner?.refresh();
    };
    const upload = async files => {
        if (busy || runner?.isQueuing) { status.textContent = "Upload or queue submission in progress. Wait before adding more files."; return; }
        if (!files.length) return;
        const names = readCollection(manifest.value);
        const accepted = [...files].filter(file => supported.test(file.name));
        const errors = files.length === accepted.length ? [] : ["Unsupported files skipped; use PNG/JPEG/WebP/BMP/TIFF/GIF."];
        const pending = accepted.slice(0,512-names.length);
        if (pending.length < accepted.length) errors.push("Collection limit is 512 images. Remaining files were skipped.");
        busy = true; render();
        // Separate upload sessions avoid overwriting an existing node's files.
        const subfolder = "prompt-mage/" + uploadSessionName();
        try {
            for (const [index,file] of pending.entries()) {
                status.textContent = `Uploading ${index+1}/${pending.length}: ${file.name}. Wait for completion before queuing.`;
                try { const path = await uploadImage(file,api,uploadSubfolder(file,subfolder)); if (!names.includes(path)) names.push(path); }
                catch (error) { errors.push(`${file.name}: ${error.message}`); }
                // Save each success immediately; a later failed upload does not discard earlier files.
                manifest.value = JSON.stringify(names);
                node.graph?.change?.();
            }
        } finally {
            busy = false; changed(names); picker.value = folderPicker.value = "";
            if (errors.length) status.textContent = `${names.length} images ready. ` + errors.join("\n");
        }
    };
    add.addEventListener("click", () => picker.click());
    dropzone.addEventListener("click", () => picker.click());
    folder.addEventListener("click", () => folderPicker.click());
    clear.addEventListener("click", () => changed([]));
    picker.addEventListener("change", () => upload([...picker.files]));
    folderPicker.addEventListener("change", () => upload([...folderPicker.files]));
    root.addEventListener("dragover", event => {event.preventDefault(); event.stopPropagation(); root.dataset.dragging = "true";});
    root.addEventListener("dragleave", event => {if (!root.contains(event.relatedTarget)) delete root.dataset.dragging;});
    root.addEventListener("drop", event => {event.preventDefault(); event.stopPropagation(); delete root.dataset.dragging; upload([...event.dataTransfer.files]);});
    const previousOver = node.onDragOver;
    const previousDrop = node.onDragDrop;
    node.onDragOver = function (event) {
        if ([...(event.dataTransfer?.types || [])].includes("Files")) return true;
        return previousOver?.apply(this, arguments) || false;
    };
    node.onDragDrop = async function (event) {
        const files = [...(event.dataTransfer?.files || [])];
        if (!files.some(file => supported.test(file.name))) return previousDrop?.apply(this, arguments) || false;
        await upload(files);
        return true;
    };
    root.addEventListener("wheel", event => event.stopPropagation());
    const widget = node.addDOMWidget("atelier_upload", "ATELIER_UPLOAD", root, {serialize:false,getMinHeight:()=>360,getMaxHeight:()=>360});
    widget.serialize = false;
    if (app) runner = installBatchRunner(node, api, app, {isUploading: () => busy, onStateChange: render});
    collections.set(node,{render});
    render();
}

export function refreshUploadWidget(node) { collections.get(node)?.render(); }
