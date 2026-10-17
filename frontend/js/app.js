// Boot, live pipeline state, and navigation between its steps.
import { esc, getJSON, postJSON, stream } from "./api.js";
import * as store from "./state.js";
import { STEPS, LOADING_PAGE, canOpenStep, normalizeTab, stepStatus } from "./pipeline-steps.js";
import { renderStatus, renderFiber } from "./components/header.js";
import { renderPageHeader } from "./components/page-header.js";
import { renderEnquiry } from "./components/enquiry.js";
import { hasStageData, renderPipelineStep, renderProcess } from "./components/pipeline.js";
import { renderEvidence } from "./components/evidence.js";
import { renderConfirm } from "./components/confirm.js";
import { resetPrecheck } from "./components/precheck.js";
import { activePathAnswers, loadPathQuestions, setDetected } from "./components/pathq.js";
import { loadGlossary } from "./glossary.js";

const $ = (id) => document.getElementById(id);
let readingRequest = 0;

const actions = {
  setMode(mode) { store.remember("mode", mode); store.set({ mode }); },
  setView(view) { store.remember("view", view); store.set({ view }); },
  setConfirm(confirm) { store.remember("confirm", confirm ? "on" : "off"); store.set({ confirm }); },
  togglePath(path) {
    const s = store.get();
    if (s.busy || s.reading) return;
    store.set({ paths: s.paths.includes(path) ? s.paths.filter((item) => item !== path) : [...s.paths, path].sort() });
    if (s.understand) actions.understand(s.understand.enquiry);
  },
  setModelChoice(modelChoice) { store.remember("modelChoice", modelChoice); store.set({ modelChoice }); },
  setDraftEnquiry(draftEnquiry) {
    Object.assign(store.get(), { draftEnquiry, selectedExample: "", answers: {}, rejected: [] }); // keep typing without a re-render
  },
  setExample(selectedExample, draftEnquiry) {
    Object.assign(store.get(), { selectedExample, draftEnquiry, answers: {}, rejected: [] });
  },
  selectTab(id) {
    const tab = normalizeTab(id);
    if (!canOpenStep(store.get(), tab)) return;
    store.remember("tab", tab);
    store.set({ tab });
  },
  setAnswer(key, value) { store.get().answers[key] = value; },           // no re-render while typing
  async understand(enquiry) {
    const request = ++readingRequest;
    store.set({ reading: true, error: "", draftEnquiry: enquiry, tab: "reading" });
    try {
      const data = await postJSON("/api/understand", { enquiry, answers: {}, preferred_paths: [...store.get().paths] });
      if (request !== readingRequest) return;
      const s = store.get();
      const answers = { ...s.answers };
      data.prefilled = [];
      for (const q of data.questions) {
        if (q.prefill && !answers[q.key]) { answers[q.key] = q.prefill; data.prefilled.push(q.key); }
      }
      data.enquiry = enquiry;
      setDetected(data.paths.detected);
      store.set({ understand: data, answers, rejected: s.understand ? s.rejected : [] });
    } catch (err) {
      if (request === readingRequest) store.set({ error: `Could not read the enquiry: ${err.message}` });
    } finally {
      if (request === readingRequest) store.set({ reading: false });
    }
  },
  closeConfirm() { ++readingRequest; store.set({ understand: null, rejected: [], reading: false }); },
  async confirmRun(withAnswers) {
    const s = store.get();
    const u = s.understand;
    if (!u || s.busy || s.reading) return;
    const shown = new Set([...u.paths.chosen, ...u.paths.detected]);
    const keys = new Set(u.questions.map((q) => q.key));
    const answers = Object.fromEntries(Object.entries(s.answers).filter(([key, value]) => {
      if (!value.trim()) return false;
      const path = key.match(/^Path ([ABC]) - /);
      return withAnswers ? !path || shown.has(path[1]) : !keys.has(key) && !path;
    }));
    await run("/api/assess", { enquiry: u.enquiry, answers, mode: s.mode,
      preferred_paths: s.paths, rejected: [...s.rejected] });
  },
  async assess(enquiry) {
    if (!enquiry.trim()) { store.set({ error: "Type or load an enquiry first." }); return; }
    const s = store.get();
    if (s.busy || s.reading) return;
    Object.assign(s, { draftEnquiry: enquiry });
    if (s.confirm) { await actions.understand(enquiry.trim()); return; }
    const answers = activePathAnswers(Object.fromEntries(Object.entries(s.answers).filter(([, value]) => value.trim())));
    await run("/api/assess", { enquiry, answers, mode: s.mode, preferred_paths: s.paths });
  },
  async assessCouncil() {
    const r = store.get().busy ? null : store.get().run;
    if (r) { store.remember("mode", "council"); store.set({ mode: "council", answers: {} }); await run("/api/assess", {
      enquiry: r.enquiry, answers: r.answers, mode: "council", preferred_paths: r.preferred_paths || [], rejected: r.rejected || [] }); }
  },
  async whatif() {
    const s = store.get();
    if (!s.run) return;
    const answers = activePathAnswers(Object.fromEntries(Object.entries(s.answers).filter(([key, value]) =>
      value.trim() && s.run.answers?.[key] !== value)));
    const pathsChanged = JSON.stringify(s.paths) !== JSON.stringify(s.run.preferred_paths || []);
    if (!Object.keys(answers).length && !pathsChanged) { store.set({ error: "Type at least one answer, or change the preferred path in Reading, first." }); return; }
    await run("/api/whatif", { run_id: s.run.id, answers, mode: s.mode, preferred_paths: s.paths });
  },
};

async function run(url, body) {
  ++readingRequest;
  resetPrecheck();
  const previous = store.get().run;
  const completionTab = url === "/api/whatif" ? "coach" : "assessment";
  const liveRun = {
    enquiry: body.enquiry || previous?.enquiry || "",
    answers: { ...(url === "/api/whatif" ? previous?.answers : {}), ...body.answers },
    mode: body.mode || store.get().mode,
    preferred_paths: body.preferred_paths || previous?.preferred_paths || [],
    rejected: body.rejected || previous?.rejected || [],
    timings_ms: {},
  };
  store.set({ busy: true, error: "", stages: [], details: [], previous,
    run: null, liveRun, understand: null, reading: false, evidence: null });
  window.scrollTo(0, 0);
  let receivedResult = false;
  try {
    await stream(url, body, (e) => {
      const s = store.get();
      if (e.type === "stage") {
        store.set({ stages: [...s.stages, e] });
      } else if (e.type === "stage_result") {
        const stageDone = [...s.stages].reverse().find((item) => item.stage === e.stage && item.status === "done");
        store.set({ liveRun: { ...s.liveRun, ...e.data,
          timings_ms: { ...s.liveRun.timings_ms, [e.stage]: stageDone?.ms ?? 0 } } });
      } else if (e.type === "detail") {
        store.set({ details: [...s.details, { stage: e.stage, detail: e.detail }] });
      } else if (e.type === "error") {
        store.set({ error: `The run hit an error: ${e.detail}` });
      } else if (e.type === "result") {
        receivedResult = true;
        const answers = Object.fromEntries(Object.entries(e.run.answers || {}).filter(([key]) => /^Path [ABC] - /.test(key)));
        const tab = e.run.error ? "reading" : completionTab;
        store.remember("tab", tab);
        setDetected(e.run.requirements?.preferred_paths || []);
        store.set({ run: e.run, liveRun: e.run, tab,
          answers, paths: e.run.preferred_paths || [], rejected: [] });
        if (e.run.id) history.replaceState(null, "", `#run=${e.run.id}`);
      }
    });
  } catch (err) {
    store.set({ error: `Could not reach the assistant: ${err.message}` });
  } finally {
    if (!receivedResult) {
      const s = store.get();
      store.set({ run: { ...s.liveRun, error: s.error || "Run ended before a result was returned." },
        liveRun: null, busy: false, tab: "reading" });
    } else {
      store.set({ liveRun: null, busy: false });
    }
    if (store.get().run?.error) document.querySelector("#view .err")?.scrollIntoView({ block: "center" });
    else window.scrollTo(0, 0);
  }
}

function renderView(s) {
  const el = $("view");
  const run = s.busy ? s.liveRun : s.run;
  const step = s.busy ? LOADING_PAGE : STEPS.find((item) => item.id === s.tab);
  el.innerHTML = `<div id="stage-content" class="page-content"></div>`;
  const content = el.querySelector("#stage-content");
  if (s.busy) {
    renderProcess(content, run, s, actions);
  } else if (s.tab === "reading") {
    renderEnquiry(content, s, actions);
    if (s.understand && !s.busy && !s.reading) renderConfirm(content.querySelector("#reading-confirm"), s, actions);
  } else {
    const stage = { assessment: "report", verification: "verify", coach: "coach" }[s.tab];
    if (hasStageData(run, stage)) {
      renderPipelineStep(content, stage, run, { ...s, run }, actions);
    } else if (!run && !s.busy && !s.error) {
      content.innerHTML = `<div class="empty"><h2>Start with a customer enquiry</h2>
        <p>Open Reading to type an enquiry or load a scenario. Each tab above shows its results as the pipeline runs.</p></div>`;
    } else {
      const status = stepStatus(s, step.id);
      const message = status === "active" ? "This step is running. Its output will appear here when it finishes." :
        status === "error" ? "The run stopped before this step produced an output." :
        status === "done" ? "This step finished. Waiting for its output to arrive." :
        "This step has not run yet.";
      content.innerHTML = `<div class="stage-placeholder">${message}${status === "error" && (s.error || run?.error) ?
        `<div class="err">${esc(s.error || run.error)}</div>` : ""}</div>`;
    }
  }
  renderPageHeader(el, content, s, step, run);
}

let lastEvidence = null;
function render(s) {
  renderStatus($("status"), s, actions);
  renderFiber($("fiber"), s, actions.selectTab);
  $("view").setAttribute("role", s.busy ? "region" : "tabpanel");
  $("view").setAttribute("aria-busy", String(s.busy || s.reading));
  $("view").setAttribute("aria-labelledby", s.busy ? "page-title-loading" : `tab-${s.tab}`);
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
  const linkedRun = location.hash.match(/run=([\w-]+)/);
  const preferredTab = normalizeTab(store.recall("tab", linkedRun ? "assessment" : "reading"));
  store.set({ tab: canOpenStep(store.get(), preferredTab) ? preferredTab : "reading",
    mode: store.recall("mode", "fast"), modelChoice: store.recall("modelChoice", "auto"),
    view: store.recall("view", "general"), confirm: store.recall("confirm", "on") === "on" });
  try { store.set({ health: await getJSON("/api/health") }); } catch (_) { /* server starting */ }
  try { store.set({ examples: await getJSON("/api/examples") }); } catch (_) { /* optional */ }
  await Promise.all([loadGlossary(), loadPathQuestions()]);
  if (linkedRun) {
    try {
      const run = await getJSON(`/api/runs/${linkedRun[1]}`);
      setDetected(run.requirements?.preferred_paths || []);
      store.set({ run, paths: run.preferred_paths || [],
        answers: Object.fromEntries(Object.entries(run.answers || {}).filter(([key]) => /^Path [ABC] - /.test(key))),
        tab: canOpenStep({ ...store.get(), run }, preferredTab) ? preferredTab : "reading" });
    } catch (_) { /* old link */ }
  }
})();
