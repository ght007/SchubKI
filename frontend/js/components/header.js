// Summary badges and the navigable spectrum line with completion dots.
import { esc } from "../api.js";
import { STEPS, STATUS_LABELS, activeStep, canOpenStep, isStep, processComplete, stepStatus } from "../pipeline-steps.js";

const STATUS = {
  provisional_assessment: ["Provisional assessment", "core"],
  insufficient_information: ["Insufficient information", "warn"],
  outside_supported_scope: ["Outside supported scope", "block"],
};
const CONF = { high: "ok", medium: "core", low: "warn", insufficient: "block" };
let lastSelectedStep = null;
let lastComplete = false;

function revealStep(nav, button) {
  const bounds = button.getBoundingClientRect();
  const viewport = nav.getBoundingClientRect();
  if (bounds.left < viewport.left) nav.scrollLeft += bounds.left - viewport.left - 12;
  else if (bounds.right > viewport.right) nav.scrollLeft += bounds.right - viewport.right + 12;
}

export function renderStatus(el, s) {
  const r = s.busy ? s.liveRun : s.run;
  if (!r || !r.report) {
    const h = s.health;
    el.innerHTML = h ? `<span class="pill ${h.mock || !h.has_key ? "warn" : "ok"}"><span class="dot"></span>${
      h.mock ? "Rule-only mode (no LLM)" : h.has_key ? "Groq connected" : "No Groq key: rule-only"}</span>
      <span class="pill">${h.kb_records} indexed passages</span>` : "";
    return;
  }
  const [label, cls] = STATUS[r.report.decision_status];
  const v = r.verification, q = r.quality, c = r.confidence;
  el.innerHTML = `<span class="pill ${cls}"><span class="dot"></span><b>${label}</b></span>
    ${c ? `<span class="pill ${CONF[c.level]}" title="Computed from observable signals, not self-reported">Confidence <b>${esc(c.level)}</b></span>` : ""}
    ${q ? `<span class="pill ${q.passed === q.total ? "ok" : q.items.some((i) => i.status === "fail") ? "block" : "warn"}">Quality <b>${q.passed}/${q.total}</b></span>` : ""}
    ${v ? `<span class="pill ${v.n_verified === v.n_sourced ? "ok" : "warn"}">${v.n_verified}/${v.n_sourced} claims verified</span>
           <span class="pill ${v.n_unsupported_numbers ? "block" : "ok"}">${v.n_unsupported_numbers} unsupported numbers</span>` : ""}`;
}

export function renderFiber(el, s, onSelect) {
  const focused = el.contains(document.activeElement) ? document.activeElement.dataset.step : null;
  const current = s.busy ? activeStep(s) : null;
  const focusable = isStep(s.tab) ? s.tab : "reading";
  const complete = processComplete(s);
  const stops = STEPS.map((step, index) => `${step.color} ${(index / (STEPS.length - 1) * 100).toFixed(2)}%`);
  stops.splice(3, 0, "#eab308 62.50%");
  const spectrum = `linear-gradient(90deg, ${stops.join(", ")})`;
  if (!el.querySelector(".fiber-rail")) {
    el.innerHTML = `<div class="fiber-rail" style="--spectrum:${spectrum};--progress:0%">
      <div class="fiber-track" aria-hidden="true"></div>
      <div class="fiber-lit" aria-hidden="true"></div>
      ${STEPS.map((step, index) => `<button type="button" id="tab-${step.id}" role="tab" aria-controls="view"
        class="fiber-node" style="--step-color:${step.color};--node-index:${index}"
        data-step="${step.id}"><span class="step-count">Step ${index + 1} of ${STEPS.length}</span>
        <span class="step-name">${step.short}</span></button>`).join("")}</div>`;
    el.onclick = (event) => {
      const button = event.target.closest("[data-step]");
      if (button && !button.disabled) onSelect(button.dataset.step);
    };
  }
  const rail = el.querySelector(".fiber-rail");
  el.querySelectorAll("[data-step]").forEach((button) => {
      const step = STEPS.find((item) => item.id === button.dataset.step);
      const index = STEPS.indexOf(step);
      const status = stepStatus(s, step.id);
      const available = canOpenStep(s, step.id);
      button.disabled = !available;
      button.className = `fiber-node ${status} ${s.tab === step.id ? "selected" : ""}`;
      button.tabIndex = focusable === step.id ? 0 : -1;
      button.setAttribute("aria-selected", String(s.tab === step.id));
      button.setAttribute("aria-current", current === step.id ? "step" : "false");
      button.setAttribute("aria-disabled", String(!available));
      button.setAttribute("aria-label", `Step ${index + 1} of ${STEPS.length}: ${step.label}. ${available ? STATUS_LABELS[status] : "Available after processing"}`);
      button.title = available ? "" : "Available after processing";
  });
  rail.style.setProperty("--progress", complete ? "100%" : "0%");
  if (complete && !lastComplete) {
    rail.classList.add("revealing");
    setTimeout(() => rail.classList.remove("revealing"), 1700);
  }
  lastComplete = complete;
  el.onkeydown = (ev) => {
    if (!["ArrowRight", "ArrowLeft", "Home", "End"].includes(ev.key)) return;
    const available = STEPS.filter((step) => canOpenStep(s, step.id));
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
  if (s.tab !== lastSelectedStep && isStep(s.tab)) revealStep(el, el.querySelector(`[data-step="${s.tab}"]`));
  lastSelectedStep = s.tab;
}
