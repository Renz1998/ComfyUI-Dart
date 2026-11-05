const statuses = new WeakMap();

export function combineReports(reports) {
    if (!reports?.length) return null;
    if (reports.length === 1) return reports[0];
    const counts = {};
    for (const report of reports) counts[report.status] = (counts[report.status] || 0) + 1;
    const status = ["error", "blocked", "warning", "edited", "corrected", "ok", "unchecked"].find(key => counts[key]);
    const labels = {unchecked:"generated (trait checks off)",ok:"confirmed",edited:"size-edited",corrected:"corrected",warning:"with warnings",blocked:"blocked",error:"failed"};
    const totals = Object.entries(counts).map(([key, count]) => `${count} ${labels[key] || key}`).join(", ");
    return {status, counts, batch_count: reports.length, all_blocked: counts.blocked === reports.length,
        has_appearance: reports.some(report => report.has_appearance),
        title: `Batch: ${reports.length} images · ${totals}`,
        message: `Batch results: ${totals}. ` + (counts.blocked ? "Blocked items skip downstream; other items can continue.\n" : "\n") +
            reports.map((report,index) => `${report.source || `Image ${index+1}`}: ${report.status}`).join("\n"),
        issues: reports.flatMap((report,index) => (report.issues || []).map(issue => ({...issue,
            location: `${report.source || `Image ${index+1}`} · ${issue.location}`}))),
        next_step: reports.find(report => report.next_step)?.next_step || ""};
}

export function statusView(report) {
    const status = report?.status || "unchecked";
    const titles = {
        warning: "Overrides not confirmed · output continues",
        blocked: "Overrides not confirmed · downstream blocked",
        corrected: "Overrides confirmed after correction",
        edited: "Selected size phrase applied by Prompt Mage",
        ok: "Selected appearance wording confirmed",
        unchecked: "Appearance wording checks are off",
        running: "Checking appearance overrides…",
        error: "Generation failed · check details",
    };
    const lines = [];
    if (report?.message) lines.push(report.message);
    for (const issue of report?.issues || []) {
        lines.push(`\n${issue.location}:`);
        if (issue.missing?.length) lines.push(`Missing: ${issue.missing.join(", ")}`);
        if (issue.conflicts?.length) lines.push(`Model used: ${issue.conflicts.join(", ")}`);
    }
    for (const edit of report?.post_edits || []) {
        lines.push(`\n${edit.location}: ${edit.action} → ${edit.selected}`);
        if (edit.replaced?.length) lines.push(`Replaced: ${edit.replaced.join(", ")}`);
    }
    if (report?.next_step) lines.push("\n" + report.next_step);
    return { status, title: report?.title || titles[status] || titles.unchecked, detail: lines.join("\n"),
        visible: Boolean(report?.has_appearance || report?.batch_count > 1 || ["warning", "blocked", "error"].includes(status)) };
}

export function installStatusWidget(node) {
    if (statuses.has(node)) return;
    const root = document.createElement("details");
    root.className = "atelier-status";
    root.setAttribute("role", "status");
    root.setAttribute("aria-live", "polite");
    const summary = document.createElement("summary");
    const detail = document.createElement("div");
    detail.className = "atelier-status-details";
    root.append(summary, detail);
    const height = () => root.hidden ? 0 : root.open ? 250 : 66;
    const widget = node.addDOMWidget("atelier_status", "ATELIER_STATUS", root, {
        serialize: false, getMinHeight: height, getMaxHeight: height,
    });
    widget.serialize = false;
    root.hidden = widget.hidden = true;
    const resize = () => {
        const size = node.computeSize();
        node.setSize([Math.max(420, node.size[0], size[0]), size[1]]);
        node.setDirtyCanvas(true, true);
    };
    root.addEventListener("toggle", resize);
    statuses.set(node, {root, summary, detail, widget, resize});
}

export function updateStatusWidget(node, report) {
    node.atelierLastReport = report;
    const view = statusView(report);
    const state = statuses.get(node);
    if (!state) return;
    state.root.dataset.status = view.status;
    state.root.hidden = state.widget.hidden = !view.visible;
    state.root.open = ["warning", "blocked", "error"].includes(view.status);
    // Model-derived text is plain text, never HTML or Markdown.
    state.summary.textContent = view.title;
    state.summary.title = view.detail;
    state.detail.textContent = view.detail;
    state.resize();
}

export function finishedState(node) {
    if (node?.atelierLastReport?.batch_count > 1 && node.atelierLastReport.status === "blocked" && !node.atelierLastReport.all_blocked) return "warning";
    return ["warning", "blocked"].includes(node?.atelierLastReport?.status) ? node.atelierLastReport.status : "done";
}
