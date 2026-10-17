// Status badge, confidence, quality, verified counter + the fiber progress line.
import { esc } from "../api.js";
import { STEPS, STATUS_LABELS, activeStep, stepStatus } from "../pipeline-steps.js";

const STATUS = {
  provisional_assessment: ["Provisional assessment", "core"],
  insufficient_information: ["Insufficient information", "warn"],
  outside_supported_scope: ["Outside supported scope", "block"],
};
const CONF = { high: "ok", medium: "core", low: "warn", insufficient: "block" };

export function renderStatus(el, s) {
  const r = s.busy ? s.liveRun : s.run;
  const current = s.busy ? activeStep(s) : null;
  const progress = current ? `<span class="pill core"><span class="dot"></span>Now: ${esc(STEPS.find((step) => step.id === current).short)}</span>` : "";
  if (!r || !r.report) {
    const h = s.health;
    el.innerHTML = progress + (h ? `<span class="pill ${h.mock || !h.has_key ? "warn" : "ok"}"><span class="dot"></span>${
      h.mock ? "Rule-only mode (no LLM)" : h.has_key ? "Groq connected" : "No Groq key: rule-only"}</span>
      <span class="pill">${h.kb_records} indexed passages</span>` : "");
    return;
  }
  const [label, cls] = STATUS[r.report.decision_status];
  const v = r.verification, q = r.quality, c = r.confidence;
  el.innerHTML = `${progress}
    <span class="pill ${cls}"><span class="dot"></span><b>${label}</b></span>
    ${c ? `<span class="pill ${CONF[c.level]}" title="Computed from observable signals, not self-reported">Confidence <b>${esc(c.level)}</b></span>` : ""}
    ${q ? `<span class="pill ${q.passed === q.total ? "ok" : q.items.some((i) => i.status === "fail") ? "block" : "warn"}">Quality <b>${q.passed}/${q.total}</b></span>` : ""}
    ${v ? `<span class="pill ${v.n_verified === v.n_sourced ? "ok" : "warn"}">${v.n_verified}/${v.n_sourced} claims verified</span>
           <span class="pill ${v.n_unsupported_numbers ? "block" : "ok"}">${v.n_unsupported_numbers} unsupported numbers</span>` : ""}`;
}

export function renderFiber(el, s, onSelect) {
  const focused = el.contains(document.activeElement) ? document.activeElement.dataset.step : null;
  const current = s.busy ? activeStep(s) : null;
  const done = STEPS.filter((step) => stepStatus(s, step.id) === "done").length;
  const frac = Math.min(1, (done + (current ? 0.35 : 0)) / STEPS.length);
  el.classList.toggle("running", s.busy);
  el.innerHTML = `
    <div class="fiber-track"><div class="fiber-lit" style="width:${(frac * 100).toFixed(1)}%"></div>
      <div class="fiber-pulse" style="--lit:${Math.max(40, frac * (el.scrollWidth - 40))}px"></div></div>
    <div class="fiber-nodes">${STEPS.map((step) => {
      const status = stepStatus(s, step.id);
      return `<button type="button" class="fiber-node ${status} ${s.tab === step.id ? "selected" : ""}"
        data-step="${step.id}" aria-current="${current === step.id ? "step" : "false"}"
        aria-pressed="${s.tab === step.id}" aria-label="Step ${STEPS.indexOf(step) + 1}: ${step.label}. ${STATUS_LABELS[status]}">
        <span>${step.short}</span></button>`;
    }).join("")}</div>`;
  el.querySelectorAll("[data-step]").forEach((button) => (button.onclick = () => onSelect(button.dataset.step)));
  if (focused) el.querySelector(`[data-step="${focused}"]`)?.focus({ preventScroll: true });
}
