// Status badge, confidence, quality, verified counter + the fiber progress line.
import { esc } from "../api.js";

const STATUS = {
  provisional_assessment: ["Provisional assessment", "core"],
  insufficient_information: ["Insufficient information", "warn"],
  outside_supported_scope: ["Outside supported scope", "block"],
};
const CONF = { high: "ok", medium: "core", low: "warn", insufficient: "block" };

function viewToggle(s) {
  return `<div class="seg view-toggle" role="group" aria-label="View">
    <button data-view="general" aria-pressed="${s.view === "general"}" title="Compact summary for non-experts">General</button>
    <button data-view="expert" aria-pressed="${s.view === "expert"}" title="Full workbench: matrix, evidence, checks, trace">Expert</button></div>`;
}

// Where data lives: Supabase (online), offline fallback to the local file, or local only.
function dbPill(db) {
  if (!db) return "";
  const [label, cls] = db.mode === "supabase" ? [db.kb === "supabase" ? "Supabase" : "Supabase (KB local)", "ok"]
    : db.mode === "offline" ? ["Supabase offline: saving locally", "warn"] : ["Local database", ""];
  return `<span class="pill ${cls}" title="${esc(db.detail || "")}">${esc(label)}</span>`;
}

export function renderStatus(el, s, actions) {
  const r = s.run;
  const wire = () => el.querySelectorAll("[data-view]").forEach((b) => (b.onclick = () => actions.setView(b.dataset.view)));
  if (!r || !r.report) {
    const h = s.health;
    el.innerHTML = (h ? `<span class="pill ${h.mock || !h.has_key ? "warn" : "ok"}"><span class="dot"></span>${
      h.mock ? "Rule-only mode (no LLM)" : h.has_key ? "Groq connected" : "No Groq key: rule-only"}</span>
      ${s.view === "expert" ? `<span class="pill">${h.kb_records} indexed passages</span>${dbPill(h.db)}` : ""}` : "") + viewToggle(s);
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

const NODES = [
  ["extract", "Read"], ["rules", "Rules"], ["retrieve", "Evidence"], ["premise", "Premises"],
  ["report", "Assess"], ["verify", "Verify"], ["coach", "Coach"],
];

export function renderFiber(el, s) {
  const done = new Set(s.stages.filter((x) => x.status === "done").map((x) => (x.stage === "council" ? "report" : x.stage)));
  const active = s.busy ? (s.stages.filter((x) => x.status === "start").map((x) => (x.stage === "council" ? "report" : x.stage)).pop()) : null;
  const n = done.size;
  const frac = s.run && !s.busy ? 1 : Math.min(1, n / (NODES.length - 1));
  el.classList.toggle("running", s.busy);
  el.innerHTML = `
    <div class="fiber-track"><div class="fiber-lit" style="width:${(frac * 100).toFixed(1)}%"></div>
      <div class="fiber-pulse" style="--lit:${Math.max(40, frac * (el.clientWidth - 40))}px"></div></div>
    <div class="fiber-nodes">${NODES.map(([k, l]) =>
      `<div class="node ${done.has(k) ? "done" : ""} ${active === k ? "active" : ""}"><span>${l}</span></div>`).join("")}</div>`;
}