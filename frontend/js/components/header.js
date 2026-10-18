// Summary badges and the navigable spectrum line with completion dots.
import { esc } from "../api.js";
import { STATUS_LABELS, activeStep, canOpenStep, pipelineProgress, stepStatus, visibleSteps } from "../pipeline-steps.js";

const STATUS = {
  provisional_assessment: ["Provisional assessment", "core"],
  insufficient_information: ["Insufficient information", "warn"],
  outside_supported_scope: ["Outside supported scope", "block"],
};
const CONF = { high: "ok", medium: "core", low: "warn", insufficient: "block" };
let lastSelectedStep = null;

function revealStep(nav, button) {
  const bounds = button.getBoundingClientRect();
  const viewport = nav.getBoundingClientRect();
  if (bounds.left < viewport.left) nav.scrollLeft += bounds.left - viewport.left - 12;
  else if (bounds.right > viewport.right) nav.scrollLeft += bounds.right - viewport.right + 12;
}

function viewToggle(s) {
  return `<div class="seg view-toggle" role="group" aria-label="View">
    <button data-view="general" aria-pressed="${s.view === "general"}" title="Simple progress and assessment views">General</button>
    <button data-view="expert" aria-pressed="${s.view === "expert"}" title="Includes Process Information: models, rules, evidence, and trace">Expert</button></div>`;
}

export function renderStatus(el, s, actions) {
  const r = s.busy ? s.liveRun : s.run;
  const wire = () => el.querySelectorAll("[data-view]").forEach((b) => (b.onclick = () => actions.setView(b.dataset.view)));
  if (s.busy && s.view === "general") {
    el.innerHTML = viewToggle(s);
    wire();
    return;
  }
  if (!r || !r.report) {
    const h = s.health;
    el.innerHTML = (h ? `<span class="pill ${h.mock || !h.has_key ? "warn" : "ok"}"><span class="dot"></span>${
      h.mock ? "Rule-only mode (no LLM)" : h.has_key ? "Groq connected" : "No Groq key: rule-only"}</span>
      ${s.view === "expert" ? `<span class="pill">${h.kb_records} indexed passages</span>` : ""}` : "") + viewToggle(s);
    wire();
    return;
  }
  const [label, cls] = STATUS[r.report.decision_status];
  const v = r.verification, q = r.quality, c = r.confidence;
  if (s.view === "general") {
    el.innerHTML = `<span class="pill ${cls}"><span class="dot"></span><b>${label}</b></span>
      ${c ? `<span class="pill ${CONF[c.level]}">Confidence <b>${esc(c.level)}</b></span>` : ""}${viewToggle(s)}`;
    wire();
    return;
  }
  el.innerHTML = viewToggle(s) + `
    <span class="pill ${cls}"><span class="dot"></span><b>${label}</b></span>
    ${c ? `<span class="pill ${CONF[c.level]}" title="Computed from observable signals, not self-reported">Confidence <b>${esc(c.level)}</b></span>` : ""}
    ${q ? `<span class="pill ${q.passed === q.total ? "ok" : q.items.some((i) => i.status === "fail") ? "block" : "warn"}">Quality <b>${q.passed}/${q.total}</b></span>` : ""}
    ${v ? `<span class="pill ${v.n_verified === v.n_sourced ? "ok" : "warn"}">${v.n_verified}/${v.n_sourced} claims verified</span>
           <span class="pill ${v.n_unsupported_numbers ? "block" : "ok"}">${v.n_unsupported_numbers} unsupported numbers</span>` : ""}`;
  wire();
}

export function renderFiber(el, s, onSelect) {
  const steps = visibleSteps(s);
  const focused = el.contains(document.activeElement) ? document.activeElement.dataset.step : null;
  const current = activeStep(s);
  const focusable = steps.some((step) => step.id === s.tab) ? s.tab : "reading";
  const progress = pipelineProgress(s);
  const stops = steps.flatMap((step, index) => {
    const position = index / (steps.length - 1) * 100;
    const colors = [`${step.color} ${position.toFixed(2)}%`];
    if (step.id === "reading" && steps[index + 1]?.id !== "process") colors.push(`#2563eb ${(position + 50 / (steps.length - 1)).toFixed(2)}%`);
    if (step.id === "assessment") colors.push(`#eab308 ${(position + 50 / (steps.length - 1)).toFixed(2)}%`);
    return colors;
  });
  const spectrum = `linear-gradient(90deg, ${stops.join(", ")})`;
  el.classList.toggle("running", s.busy);
  const stepKey = steps.map((step) => step.id).join(",");
  if (el.dataset.steps !== stepKey) {
    el.dataset.steps = stepKey;
    el.innerHTML = `<div class="fiber-rail" style="--step-count:${steps.length};--half-step:${50 / steps.length}%;--edge-factor:${1 - 1 / steps.length};--spectrum:${spectrum};--progress:0%">
      <div class="fiber-track" aria-hidden="true"></div>
      <div class="fiber-lit" role="progressbar" aria-label="Assessment calculation" aria-valuemin="0" aria-valuemax="100"></div>
      ${steps.map((step, index) => `<button type="button" id="tab-${step.id}" role="tab" aria-controls="view"
        class="fiber-node" style="--step-color:${step.color}"
        data-step="${step.id}"><span class="step-count">Step ${index + 1} of ${steps.length}</span>
        <span class="step-name">${step.short}</span></button>`).join("")}</div>`;
    el.onclick = (event) => {
      const button = event.target.closest("[data-step]");
      if (button && !button.disabled) onSelect(button.dataset.step);
    };
  }
  const rail = el.querySelector(".fiber-rail");
  el.querySelectorAll("[data-step]").forEach((button) => {
      const step = steps.find((item) => item.id === button.dataset.step);
      const index = steps.indexOf(step);
      const status = stepStatus(s, step.id);
      const available = canOpenStep(s, step.id);
      const selected = s.tab === step.id && (!s.busy || step.id === "process");
      button.disabled = !available;
      button.className = `fiber-node ${status} ${selected ? "selected" : ""}`;
      button.tabIndex = available && focusable === step.id ? 0 : -1;
      button.setAttribute("aria-selected", String(selected));
      button.setAttribute("aria-current", current === step.id ? "step" : "false");
      button.setAttribute("aria-disabled", String(!available));
      button.setAttribute("aria-label", `Step ${index + 1} of ${steps.length}: ${step.label}. ${STATUS_LABELS[status]}${available ? "" : ". Available after processing"}`);
      button.title = available ? "" : "Available after processing";
  });
  rail.style.setProperty("--progress", `${progress.toFixed(2)}%`);
  const progressbar = rail.querySelector("[role=progressbar]");
  progressbar.setAttribute("aria-hidden", String(!s.busy));
  progressbar.setAttribute("aria-valuenow", String(Math.round(progress)));
  progressbar.setAttribute("aria-valuetext", `${Math.round(progress)}%${current ? `; ${steps.find((step) => step.id === current).label}` : ""}`);
  el.onkeydown = (ev) => {
    if (!["ArrowRight", "ArrowLeft", "Home", "End"].includes(ev.key)) return;
    const available = steps.filter((step) => canOpenStep(s, step.id));
    const index = available.findIndex((step) => step.id === ev.target.dataset.step);
    if (index < 0) return;
    ev.preventDefault();
    const next = ev.key === "Home" ? 0 : ev.key === "End" ? available.length - 1 :
      (index + (ev.key === "ArrowRight" ? 1 : -1) + available.length) % available.length;
    onSelect(available[next].id);
    const selected = el.querySelector(`[data-step="${available[next].id}"]`);
    selected.focus({ preventScroll: true });
    revealStep(el, selected);
  };
  if (focused) el.querySelector(`[data-step="${focused}"]`)?.focus({ preventScroll: true });
  const visibleStep = s.busy ? current : s.tab;
  if (visibleStep !== lastSelectedStep && steps.some((step) => step.id === visibleStep)) revealStep(el, el.querySelector(`[data-step="${visibleStep}"]`));
  lastSelectedStep = visibleStep;
}
