const UPLOAD = 'DanbooruTagsTransformerImageBatchUpload';
const CAPTIONERS = new Set(['DanbooruTagsTransformerArchmageBeta', 'DanbooruTagsTransformerImageToText']);
const runners = new WeakMap();
const clone = value => JSON.parse(JSON.stringify(value));

function fromImageSource(output, link, sourceId, seen = new Set()) {
    if (!Array.isArray(link) || link.length !== 2 || !Number.isInteger(link[1])) return false;
    const id = String(link[0]);
    if (id === sourceId) return link[1] === 0;
    if (seen.has(id)) return false;
    seen.add(id);
    return Object.values(output[id]?.inputs || {}).some(value => fromImageSource(output, value, sourceId, seen));
}

function savedSettings(workflow, id, values) {
    const node = workflow.nodes?.find(node => String(node.id) === String(id));
    if (node) node.dart_widget_values = {...node.dart_widget_values, ...values};
}

export function planBatch(snapshot, sourceId, names, batchMode, runId) {
    sourceId = String(sourceId);
    if (!Array.isArray(names) || !names.length || names.length > 512 || names.some(name => typeof name !== 'string' || !name)) {
        throw new Error('Upload 1–512 images before running the list.');
    }
    if (snapshot?.output?.[sourceId]?.class_type !== UPLOAD) {
        throw new Error('Upload Images is missing from the executable workflow. Enable this node and try again.');
    }
    if (!snapshot.workflow || typeof snapshot.workflow !== 'object') throw new Error('Could not capture the workflow. Refresh ComfyUI and try again.');
    if (!Object.entries(snapshot.output).some(([id, node]) => id !== sourceId &&
        Object.values(node.inputs || {}).some(value => Array.isArray(value) && String(value[0]) === sourceId && value[1] === 0))) {
        throw new Error('Connect this node’s image output to your workflow before running the list.');
    }
    const jobs = batchMode ? [names] : names.map(name => [name]);
    return {length: jobs.length, *[Symbol.iterator]() { for (const [index, selected] of jobs.entries()) {
        const prompt = clone(snapshot);
        const settings = {images: JSON.stringify(selected), index: 0, wrap_index: false,
            batch_mode: batchMode ? 'All selected images as list' : 'One image per queued run',
            max_images: selected.length, batch_run_id: `${runId}:${index}`};
        Object.assign(prompt.output[sourceId].inputs, settings);
        savedSettings(prompt.workflow, sourceId, {...settings, control_after_generate: 'fixed'});
        for (const [id, node] of Object.entries(prompt.output)) {
            if (CAPTIONERS.has(node.class_type) && fromImageSource(prompt.output, node.inputs?.image, sourceId)) {
                node.inputs.image_index = 0;
                savedSettings(prompt.workflow, id, {image_index: 0});
            }
        }
        prompt.workflow.extra ||= {};
        prompt.workflow.extra.prompt_mage_batch = {source_node_id: sourceId, mode: batchMode ? 'image list' : 'workflow per image',
            position: index + 1, jobs: jobs.length, images: names.length, filenames: [...selected]};
        yield prompt;
    } }};
}

export async function submitBatch(api, jobs, {stopped = () => false, progress = () => {}} = {}) {
    const ids = [];
    for (const job of jobs) {
        if (stopped()) break;
        try {
            // Append separate complete prompts. ComfyUI runs its prompt queue sequentially.
            const result = await api.queuePrompt(0, job);
            if (!result?.prompt_id) throw new Error('The server did not confirm a prompt ID.');
            ids.push(result.prompt_id);
            if (result.node_errors && Object.keys(result.node_errors).length) {
                throw new Error('The server accepted this job but reported validation errors for node(s): ' +
                    Object.keys(result.node_errors).join(', ') + '. The complete workflow may not execute. Fix the workflow before running the list again.');
            }
            progress(ids.length, jobs.length);
        } catch (error) {
            throw new Error(`Confirmed ${ids.length}/${jobs.length} jobs. ${error?.message || String(error)} ` +
                'Check the native queue before retrying: the last request may already have been accepted. No automatic retry was made.');
        }
    }
    return ids;
}

export function installBatchRunner(node, api, app, {isUploading = () => false, onStateChange = () => {}} = {}) {
    if (runners.has(node)) return runners.get(node);
    node.properties ||= {};
    const root = document.createElement('section'); root.className = 'mage-batch-runner';
    root.setAttribute('aria-label', 'Run the complete image list');
    const label = document.createElement('label');
    const toggle = document.createElement('input'); toggle.type = 'checkbox'; toggle.setAttribute('role', 'switch');
    toggle.setAttribute('aria-label', 'Batch mode: one run with the image list');
    const title = document.createElement('strong'); title.textContent = 'Batch mode · one run with image list';
    label.append(toggle, title);
    const help = document.createElement('div'); help.className = 'mage-batch-help';
    const actions = document.createElement('div'); actions.className = 'atelier-upload-toolbar';
    const start = document.createElement('button'); start.type = 'button';
    start.title = 'Run every uploaded image from the beginning. Ignores manual Index, Max images, caption image index and the global queue Batch Count. Captures your current settings and seeds. Uses the whole workflow, including connected samplers and saving nodes.';
    const stop = document.createElement('button'); stop.type = 'button'; stop.textContent = 'Stop adding jobs';
    stop.title = 'Stop submitting further jobs. Jobs already accepted remain in ComfyUI’s queue; use its queue controls to manage them.';
    const status = document.createElement('div'); status.className = 'atelier-upload-status'; status.setAttribute('role', 'status');
    status.setAttribute('aria-live', 'polite');
    actions.append(start, stop); root.append(label, help, actions, status);
    let busy = false, stopped = false;
    const refresh = () => {
        const manifest = node.widgets.find(widget => widget.name === 'images');
        let names = []; try { names = JSON.parse(manifest?.value || '[]'); } catch {}
        const count = Array.isArray(names) ? names.length : 0;
        toggle.checked = node.properties.mage_batch_mode === true;
        toggle.disabled = busy || isUploading();
        help.textContent = toggle.checked
            ? `${count} images → 1 workflow run using ComfyUI lists. Starts at the first image; downstream list handling controls outputs. Uses more CPU memory.`
            : `${count} images → ${count} complete workflow runs, in list order, starting at the first image.`;
        help.textContent += ' Use this Run all button; the global Run button keeps its manual behavior.';
        start.textContent = count ? `Run all ${count} images from first` : 'Run all images from first';
        start.disabled = busy || isUploading() || count === 0;
        stop.disabled = !busy || stopped;
    };
    toggle.addEventListener('change', () => { node.properties.mage_batch_mode = toggle.checked; node.graph?.change?.(); refresh(); });
    stop.addEventListener('click', () => { stopped = true; status.textContent = 'Stopping submissions. Already queued jobs remain in the native queue.'; refresh(); });
    start.addEventListener('click', async () => {
        if (busy || isUploading()) return;
        busy = true; stopped = false; refresh(); onStateChange();
        try {
            // Freeze names, mode, graph and seeds once; never rewrite the live editor or its index controls.
            const names = JSON.parse(node.widgets.find(widget => widget.name === 'images')?.value || '[]');
            const batchMode = node.properties.mage_batch_mode === true;
            status.textContent = 'Preparing your complete workflow… Keep this tab open until all jobs are queued.';
            const response = await api.fetchApi('/object_info/' + UPLOAD);
            if (!response.ok || !(await response.json())?.[UPLOAD]?.input?.optional?.batch_run_id) {
                throw new Error('Restart ComfyUI and refresh the browser once to enable the updated list runner.');
            }
            const snapshot = await app.graphToPrompt();
            const runId = globalThis.crypto?.randomUUID?.() || `${Date.now()}-${Math.random().toString(36).slice(2)}`;
            const jobs = planBatch(snapshot, node.id, names, batchMode, runId);
            const ids = await submitBatch(api, jobs, {stopped: () => stopped,
                progress: (done, total) => { status.textContent = `Queued ${done}/${total} complete workflow runs. See ComfyUI’s queue for execution.`; }});
            status.textContent = `${stopped ? 'Stopped adding jobs. ' : ''}${ids.length}/${jobs.length} workflow runs queued. ` +
                'Queued does not mean finished. Check the native queue for progress.';
        } catch (error) {
            status.textContent = error?.message || String(error);
        } finally { busy = false; refresh(); onStateChange(); }
    });
    const widget = node.addDOMWidget('mage_batch_runner', 'MAGE_BATCH_RUNNER', root,
        {serialize: false, getMinHeight: () => 240, getMaxHeight: () => 240});
    widget.serialize = false;
    const state = {refresh, get isQueuing() { return busy; }};
    runners.set(node, state); refresh(); return state;
}
