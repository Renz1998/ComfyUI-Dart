const ARCHMAGE = 'DanbooruTagsTransformerArchmageBeta';
const link = value => Array.isArray(value) && value.length === 2 && Number.isInteger(value[1]);

function dependsOn(output, id, target, seen = new Set()) {
    id = String(id);
    if (id === String(target)) return true;
    if (seen.has(id)) return false;
    seen.add(id);
    return Object.values(output[id]?.inputs || {}).some(value => link(value) && dependsOn(output, value[0], target, seen));
}

function compatibleClip(output, source, seen = new Set()) {
    if (!link(source)) return false;
    const id = String(source[0]);
    if (seen.has(id)) return false;
    seen.add(id);
    const node = output[id];
    if (node?.class_type === 'CLIPLoader') return /qwen3[.-]?(?:5|vl)|qwen35/i.test(node.inputs.clip_name || '');
    // Follow the CLIP branch only, never model/conditioning branches or arbitrary encoders.
    return compatibleClip(output, node?.inputs?.clip, seen);
}

export function bindWorkflowEncoders(snapshot) {
    const output = snapshot.output || {};
    for (const [id, node] of Object.entries(output)) {
        if (node.class_type !== ARCHMAGE || node.inputs.clip || node.inputs.local_model !== 'Automatic') continue;
        const candidates = new Map();
        for (const consumer of Object.values(output)) {
            if (consumer.class_type !== 'CLIPTextEncode' || !link(consumer.inputs?.text) || !link(consumer.inputs?.clip)) continue;
            if (!dependsOn(output, consumer.inputs.text[0], id)) continue;
            const source = consumer.inputs.clip;
            if (dependsOn(output, source[0], id) || !compatibleClip(output, source)) continue;
            candidates.set(JSON.stringify(source), source);
        }
        // Ambiguous graphs require the explicit CLIP socket. Never guess between two encoders.
        if (candidates.size === 1) node.inputs.clip = [...candidates.values()][0];
    }
    return snapshot;
}

const GROUPS = [
    ['STYLE', ['style_preset', 'style_notes']],
    ['SCENE', ['concepts', 'instructions', 'length', 'output_format', 'seed', 'control_after_generate']],
    ['CANVAS', ['canvas_source', 'aspect_ratio', 'width', 'height']],
    ['REFERENCE IMAGE · OPTIONAL', ['reference_style', 'image_index', 'image_megapixels', 'resize_mode', 'resize_method']],
    ['MODEL & PERFORMANCE', ['local_model', 'thinking', 'max_tokens', 'language_style', 'memory_mode', 'unload_after_generation', 'source_name']],
];

export function arrangeArchmage(node) {
    if (!(node.comfyClass || node.type || '').endsWith('ArchmageBeta')) return;
    if (!node.mageSectionWidgets) {
        node.mageSectionWidgets = GROUPS.map(([title]) => {
            const el = document.createElement('div'); el.className = 'mage-section'; el.textContent = title;
            const widget = node.addDOMWidget(`mage_section_${title}`, 'MAGE_SECTION', el,
                {serialize: false, hideOnZoom: true, getMinHeight: () => 26, getMaxHeight: () => 26});
            widget.serialize = false;
            return widget;
        });
    }
    const old = [...node.widgets];
    const ordered = [];
    GROUPS.forEach(([, names], i) => {
        ordered.push(node.mageSectionWidgets[i]);
        ordered.push(...names.map(name => old.find(widget => widget.name === name)).filter(Boolean));
    });
    node.widgets = [...ordered, ...old.filter(widget => !ordered.includes(widget))];
}

export function updateArchmageControls(node) {
    const type = node.comfyClass || node.type || '';
    const get = name => node.widgets?.find(widget => widget.name === name);
    if (type.endsWith('Resolution')) {
        for (const name of ['custom_width', 'custom_height']) if (get(name)) get(name).hidden = get('aspect_ratio')?.value !== 'Custom';
        if (get('megapixels')) get('megapixels').hidden = get('aspect_ratio')?.value === 'Custom';
    }
    if (!type.endsWith('ArchmageBeta')) return;
    const hasImage = node.inputs?.some(slot => slot.name === 'image' && slot.link != null);
    for (const name of ['reference_style', 'image_index', 'image_megapixels', 'resize_mode', 'resize_method']) {
        if (get(name)) get(name).hidden = !hasImage;
    }
    if (node.mageSectionWidgets) node.mageSectionWidgets[3].hidden = !hasImage;
    if (get('reference_style')) get('reference_style').label = 'Image treatment (preserve or restyle)';
    if (get('canvas_source')) get('canvas_source').label = hasImage ? 'Canvas size source' : 'Canvas size (uses width / height below)';
    if (get('canvas_source')) get('canvas_source').hidden = !hasImage;
    if (get('concepts')) get('concepts').label = 'Scene idea · WHAT to depict (blank = random)';
    if (get('instructions')) get('instructions').label = 'Writing rules · HOW to describe it';
    const wired = node.inputs?.some(slot => ['width','height'].includes(slot.name) && slot.link != null);
    if (get('aspect_ratio')) get('aspect_ratio').hidden = wired;
    if (get('source_name')) get('source_name').hidden = true;
}
