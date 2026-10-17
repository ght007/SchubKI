// Boot, wiring, tab switching.
import { esc, getJSON, postJSON, stream } from "./api.js";
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
import { renderSummary } from "./components/summary.js";
import { resetPrecheck } from "./components/precheck.js";
import { activePathAnswers, loadPathQuestions } from "./components/pathq.js";
import { renderConfirm } from "./components/confirm.js";
import { loadGlossary } from "./glossary.js";

const $ = (id) => document.getElementById(id);
const TABS = [
  ["assessment", "Assessment"], ["methods", "Methods & evidence"], ["spectral", "Spectral map"],
  ["quality", "Confidence & quality"], ["whatif", "What-if"], ["council", "Council"], ["trace", "Trace"],
];

const actions = {
  setMode(mode) { store.remember("mode", mode); store.set({ mode }); },
  setView(view) { store.remember("view", view); store.set({ view }); },
  togglePath(p) {
    const cur = store.get().paths;
    store.set({ paths: cur.includes(p) ? cur.filter((x) => x !== p) : [...cur, p].sort() });
    if (store.get().understand) actions.understand(store.get().understand.enquiry);   // refresh the card's path questions
  },
  setConfirm(on) { store.remember("confirm", on ? "on" : "off"); store.set({ confirm: on }); },
  // step 1: "Is this what you mean?" (the run's own extraction; reused when the user confirms)
  async understand(enquiry) {
    store.set({ reading: true, error: "" });
    try {
      const data = await postJSON("/api/understand", { enquiry, answers: {}, preferred_paths: store.get().paths });
      const answers = store.get().answers;
      data.prefilled = [];
      for (const q of data.questions) if (q.prefill && !answers[q.key]) { answers[q.key] = q.prefill; data.prefilled.push(q.key); }
      data.enquiry = enquiry;
      store.set({ understand: data, rejected: store.get().understand ? store.get().rejected : [] });
    } catch (err) {
      store.set({ error: `Could not read the enquiry: ${err.message}` });
    } finally {
      store.set({ reading: false });
    }
  },
  closeConfirm() { store.set({ understand: null, rejected: [] }); },
  // step 2: the full run, with the confirmed reading, answers given on the card, and rejected readings
  async confirmRun(withAnswers) {
    const s = store.get();
    const u = s.understand;
    const shown = new Set([...u.paths.chosen, ...u.paths.detected]);
    const keys = new Set(u.questions.map((q) => q.key));
    const answers = withAnswers ? Object.fromEntries(Object.entries(s.answers).filter(([k, v]) => {
      const m = k.match(/^Path ([ABC]) - /);
      return v.trim() && (m ? shown.has(m[1]) : true);
    })) : Object.fromEntries(Object.entries(s.answers).filter(([k, v]) => v.trim() && !keys.has(k) && !/^Path [ABC] - /.test(k)));
    const rejected = [...s.rejected];
    store.set({ understand: null });
    await run("/api/assess", { enquiry: u.enquiry, answers, mode: s.mode, preferred_paths: s.paths, rejected });
  },
  setAnswer(key, value) { store.get().answers[key] = value; },           // no re-render while typing
  async assess(enquiry) {
    if (!enquiry.trim()) { store.set({ error: "Type or load an enquiry first." }); return; }
    if (store.get().confirm) { await actions.understand(enquiry.trim()); return; }
    // answers typed in the pre-check travel as a separate "added by the expert" block
    // path answers count only for chosen or detected paths; empty answers are skipped (the run proceeds without them)
    const answers = activePathAnswers(Object.fromEntries(Object.entries(store.get().answers).filter(([, v]) => v.trim())));
    await run("/api/assess", { enquiry, answers, mode: store.get().mode, preferred_paths: store.get().paths });
  },
  async assessCouncil() {
    const r = store.get().run;
    if (r) { store.set({ mode: "council", answers: {} }); await run("/api/assess", { enquiry: r.enquiry, answers: r.answers, mode: "council", preferred_paths: r.preferred_paths || [], rejected: r.rejected || [] }); }
  },
  async whatif() {
    const s = store.get();
    if (!s.run) return;
    const prev = s.run.answers || {};
    const answers = Object.fromEntries(Object.entries(s.answers).filter(([k, v]) => v.trim() && prev[k] !== v));
    const pathsChanged = JSON.stringify(s.paths) !== JSON.stringify(s.run.preferred_paths || []);
    if (!Object.keys(answers).length && !pathsChanged) { store.set({ error: "Type at least one answer, or change the preferred path, first." }); return; }
    await run("/api/whatif", { run_id: s.run.id, answers, mode: s.mode, preferred_paths: s.paths }, true);
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
        const pc = document.getElementById("precheck");
        if (pc) pc.hidden = true;
        resetPrecheck();
        // keep the path answers that were used visible (and reused on the next run); other answers are cleared
        const kept = Object.fromEntries(Object.entries(e.run.answers || {}).filter(([k]) => /^Path [ABC] - /.test(k)));
        store.set({ run: e.run, tab, answers: kept, paths: e.run.preferred_paths || [], rejected: [] });
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
  $("tabs").hidden = s.view === "general";
  if (s.view === "general") return;
  const r = s.run;
  const counts = r ? { methods: r.rule_hits.length, quality: r.quality ? `${r.quality.passed}/${r.quality.total}` : "" } : {};
  $("tabs").innerHTML = TABS.map(([k, l]) => `<button role="tab" aria-selected="${s.tab === k}" data-tab="${k}">${l}${counts[k] ? `<span class="count">${counts[k]}</span>` : ""}</button>`).join("");
  $("tabs").querySelectorAll("[data-tab]").forEach((b) => (b.onclick = () => { store.remember("tab", b.dataset.tab); store.set({ tab: b.dataset.tab }); }));
}

function renderView(s) {
  const el = $("view");
  if (s.understand && !s.busy) { renderConfirm(el, s, actions); return; }
  if (!s.run) {
    el.innerHTML = `<div class="empty"><h2>Start with a customer enquiry</h2>
      <p>${s.view === "expert" ? "Load one of the scenarios or paste" : "Paste or type"} a customer enquiry, optionally pick an AFS path and answer its few questions, then choose <b>Assess enquiry</b>. The assistant will:</p>
      <ol><li>separate what the customer said from what is unknown,</li><li>test the customer's own premises against the AFS sources,</li>
      <li>screen the methods with sourced rules and check fiber coverage,</li><li>write a cited assessment and verify every quote on its page,</li>
      <li>rate its confidence from observable signals and coach the next questions.</li></ol>
      <p class="small">Fast mode uses one model; Council mode lets several models draft and judge each other blind.</p></div>`;
    return;
  }
  if (!s.run.report) { el.innerHTML = `<div class="err">This run produced no report. ${esc(s.run.error || "")}</div>`; return; }
  if (s.view === "general") { renderSummary(el, s.run, actions); return; }
  const views = {
    assessment: () => renderReport(el, s.run), methods: () => renderMatrix(el, s.run), spectral: () => renderSpectral(el, s.run),
    quality: () => renderQuality(el, s.run), whatif: () => renderWhatIf(el, s, actions), council: () => renderCouncil(el, s.run, actions),
    trace: () => renderTrace(el, s.run),
  };
  (views[s.tab] || views.assessment)();
}

let lastEvidence = null;
function render(s) {
  renderStatus($("status"), s, actions);
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
  store.set({ tab: store.recall("tab", "assessment"), mode: store.recall("mode", "fast"),
              view: store.recall("view", "general"), confirm: store.recall("confirm", "on") === "on" });
  try { store.set({ health: await getJSON("/api/health") }); } catch (_) { /* server starting */ }
  try { store.set({ examples: await getJSON("/api/examples") }); } catch (_) { /* optional */ }
  await Promise.all([loadGlossary(), loadPathQuestions()]);
  if (store.get().run) store.set({});
  const m = location.hash.match(/run=([\w-]+)/);
  if (m) { try { store.set({ run: await getJSON(`/api/runs/${m[1]}`) }); } catch (_) { /* old link */ } }
})();