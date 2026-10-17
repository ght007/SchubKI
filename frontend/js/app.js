// Boot, wiring, tab switching.
import { esc, getJSON, stream } from "./api.js";
import * as store from "./state.js";
import { renderStatus, renderFiber } from "./components/header.js";
import { renderEnquiry } from "./components/enquiry.js";
import { renderCoach } from "./components/coach.js";
import { renderReport } from "./components/report.js";
import { renderMatrix } from "./components/matrix.js";
import { renderSpectral } from "./components/spectral-map.js";
import { renderEvidence } from "./components/evidence.js";
import { renderQuality } from "./components/quality.js";
import { renderCouncil } from "./components/council.js";
import { renderWhatIf } from "./components/whatif.js";
import { renderTrace } from "./components/trace.js";

const $ = (id) => document.getElementById(id);
const TABS = [
  ["assessment", "Assessment"], ["methods", "Methods & evidence"], ["spectral", "Spectral map"],
  ["quality", "Confidence & quality"], ["whatif", "What-if"], ["council", "Council"], ["trace", "Trace"],
];

const actions = {
  setMode(mode) { store.remember("mode", mode); store.set({ mode }); },
  setAnswer(key, value) { store.get().answers[key] = value; },           // no re-render while typing
  async assess(enquiry) {
    if (!enquiry.trim()) { store.set({ error: "Type or load an enquiry first." }); return; }
    store.set({ answers: {} });
    await run("/api/assess", { enquiry, mode: store.get().mode });
  },
  async assessCouncil() {
    const r = store.get().run;
    if (r) { store.set({ mode: "council", answers: {} }); await run("/api/assess", { enquiry: r.enquiry, answers: r.answers, mode: "council" }); }
  },
  async whatif() {
    const s = store.get();
    if (!s.run) return;
    const answers = Object.fromEntries(Object.entries(s.answers).filter(([, v]) => v.trim()));
    if (!Object.keys(answers).length) { store.set({ error: "Type at least one answer first." }); return; }
    await run("/api/whatif", { run_id: s.run.id, answers, mode: s.mode }, true);
  },
};

async function run(url, body, isWhatIf = false) {
  store.set({ busy: true, error: "", stages: [], details: [], previous: store.get().run });
  try {
    await stream(url, body, (e) => {
      const s = store.get();
      if (e.type === "stage") {
        const stages = s.stages.filter((x) => !(x.stage === e.stage && x.status === "start" && e.status === "done"));
        store.set({ stages: [...stages, e] });
      } else if (e.type === "detail") {
        store.set({ details: [...s.details, e.detail] });
      } else if (e.type === "error") {
        store.set({ error: `The run hit an error: ${e.detail}` });
      } else if (e.type === "result") {
        const tab = isWhatIf ? "whatif" : s.tab;
        store.set({ run: e.run, tab, answers: {} });
        history.replaceState(null, "", `#run=${e.run.id}`);
      }
    });
  } catch (err) {
    store.set({ error: `Could not reach the assistant: ${err.message}` });
  } finally {
    store.set({ busy: false });
  }
}

function renderTabs(s) {
  const r = s.run;
  const counts = r ? { methods: r.rule_hits.length, quality: r.quality ? `${r.quality.passed}/${r.quality.total}` : "" } : {};
  $("tabs").innerHTML = TABS.map(([k, l]) => `<button role="tab" aria-selected="${s.tab === k}" data-tab="${k}">${l}${counts[k] ? `<span class="count">${counts[k]}</span>` : ""}</button>`).join("");
  $("tabs").querySelectorAll("[data-tab]").forEach((b) => (b.onclick = () => { store.remember("tab", b.dataset.tab); store.set({ tab: b.dataset.tab }); }));
}

function renderView(s) {
  const el = $("view");
  if (!s.run) {
    el.innerHTML = `<div class="empty"><h2>Start with a customer enquiry</h2>
      <p>Load one of the scenarios or paste a new enquiry, then choose <b>Assess enquiry</b>. The assistant will:</p>
      <ol><li>separate what the customer said from what is unknown,</li><li>test the customer's own premises against the AFS sources,</li>
      <li>screen the methods with sourced rules and check fiber coverage,</li><li>write a cited assessment and verify every quote on its page,</li>
      <li>rate its confidence from observable signals and coach the next questions.</li></ol>
      <p class="small">Fast mode uses one model; Council mode lets several models draft and judge each other blind.</p></div>`;
    return;
  }
  if (!s.run.report) { el.innerHTML = `<div class="err">This run produced no report. ${esc(s.run.error || "")}</div>`; return; }
  const views = {
    assessment: () => renderReport(el, s.run), methods: () => renderMatrix(el, s.run), spectral: () => renderSpectral(el, s.run),
    quality: () => renderQuality(el, s.run), whatif: () => renderWhatIf(el, s, actions), council: () => renderCouncil(el, s.run, actions),
    trace: () => renderTrace(el, s.run),
  };
  (views[s.tab] || views.assessment)();
}

let lastEvidence = null;
function render(s) {
  renderStatus($("status"), s);
  renderFiber($("fiber"), s);
  renderEnquiry($("enquiry"), s, actions);
  renderCoach($("coach"), s, actions);
  renderTabs(s);
  renderView(s);
  document.querySelector(".shell").classList.toggle("with-drawer", !!s.evidence);
  if (s.evidence !== lastEvidence) {
    lastEvidence = s.evidence;
    renderEvidence($("drawer"), s.evidence, () => store.set({ evidence: null }));
  }
}

// citation chips anywhere open the source drawer
document.addEventListener("click", (ev) => {
  const b = ev.target.closest(".cite");
  if (!b) return;
  store.set({ evidence: { source: b.dataset.src, page: +b.dataset.page, quote: b.dataset.quote, status: b.dataset.status } });
});
document.addEventListener("keydown", (ev) => { if (ev.key === "Escape" && store.get().evidence) store.set({ evidence: null }); });

store.subscribe(render);

(async function boot() {
  store.set({ tab: store.recall("tab", "assessment"), mode: store.recall("mode", "fast") });
  try { store.set({ health: await getJSON("/api/health") }); } catch (_) { /* server starting */ }
  try { store.set({ examples: await getJSON("/api/examples") }); } catch (_) { /* optional */ }
  const m = location.hash.match(/run=([\w-]+)/);
  if (m) { try { store.set({ run: await getJSON(`/api/runs/${m[1]}`) }); } catch (_) { /* old link */ } }
})();
