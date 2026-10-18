// Boot, live pipeline state, and navigation between its steps.
import { esc, getJSON, postJSON, stream } from "./api.js";
import * as store from "./state.js";
import { STEPS, LOADING_PAGE, canOpenStep, normalizeTab, stepStatus } from "./pipeline-steps.js";
import { renderStatus, renderFiber } from "./components/header.js";
import { renderPageNavigation } from "./components/page-navigation.js";
import { renderEnquiry } from "./components/enquiry.js";
import { hasStageData, renderPipelineStep, renderLoadingFlow, renderProcessInformation } from "./components/pipeline.js";
import { renderEvidence } from "./components/evidence.js";
import { renderConfirm } from "./components/confirm.js";
import { resetPrecheck } from "./components/precheck.js";
import { activePathAnswers, loadPathQuestions, setDetected } from "./components/pathq.js";
import { loadGlossary } from "./glossary.js";
import { createLocalQueryRepository, createServerQueryRepository, importLocalDrafts, runSummary } from "./query-history.js";
import { renderQuerySidebar } from "./components/query-sidebar.js";
import { isPro, mountAccountControls, openAccountMenu } from "./components/account-controls.js";

const $ = (id) => document.getElementById(id);
// Reserve the pinned header's actual height, including wrapped account controls and pipeline tabs.
const appHeader = document.querySelector(".app-header");
if (appHeader) {
  const updateHeaderHeight = () => document.documentElement.style.setProperty(
    "--app-header-height", `${appHeader.offsetHeight}px`);
  updateHeaderHeight();
  new ResizeObserver(updateHeaderHeight).observe(appHeader);
}
const localQueries = createLocalQueryRepository();
let queryRepository = localQueries;   // swapped for the account store after login (boot)
const compactSidebar = window.matchMedia("(max-width: 900px)");
let readingRequest = 0;

function openReadingDraft(query = null) {
  ++readingRequest;
  resetPrecheck();
  setDetected([]);
  history.replaceState(null, "", location.pathname + location.search);
  store.remember("tab", "reading");
  store.set({ tab: "reading", run: null, previous: null, liveRun: null, stages: [], details: [], error: "",
    understand: null, reading: false, rejected: [], answers: {}, evidence: null, selectedExample: "",
    draftEnquiry: query?.enquiry || "", activeQueryId: query?.id || null, paths: query?.paths || [],
    mode: query?.mode || store.get().mode, modelChoice: query?.modelChoice || store.get().modelChoice,
    querySidebarOpen: !compactSidebar.matches, queryNotice: "", skipQueryAutosave: false, queryRuns: null });
  window.scrollTo(0, 0);
  $("enq")?.focus({ preventScroll: true });
}

// Every result generated for a saved query (newest first) -> s.queryRuns, listed under it in the sidebar.
async function loadQueryRuns(queryId) {
  if (!queryId) { store.set({ queryRuns: null }); return []; }
  let runs = [];
  try { runs = await queryRepository.runsFor(queryId); } catch (_) { /* list stays empty */ }
  if (store.get().activeQueryId === queryId) store.set({ queryRuns: { queryId, runs } });
  return runs;
}

const actions = {
  setMode(mode) { store.remember("mode", mode); store.set({ mode }); },
  setView(view) {
    if (view === "expert" && !isPro(store.get().user)) { location.assign("/pricing?upgrade=expert"); return; } // Basic plan
    const s = store.get();
    const preferred = normalizeTab(s.tab, view);
    const tab = s.busy ? view === "expert" ? "process" : "reading" :
      canOpenStep({ ...s, view }, preferred) ? preferred : "reading";
    store.remember("view", view);
    store.remember("tab", tab);
    store.set({ view, tab });
  },
  openAccountMenu(anchor) { openAccountMenu(anchor, store.get().user, { openRun: (id) => actions.openRun(id) }); },
  setConfirm(confirm) { store.remember("confirm", confirm ? "on" : "off"); store.set({ confirm }); },
  togglePath(path) {
    const s = store.get();
    if (s.busy || s.reading) return;
    store.set({ paths: s.paths.includes(path) ? s.paths.filter((item) => item !== path) : [...s.paths, path].sort() });
    if (s.understand) actions.understand(s.understand.enquiry);
  },
  setModelChoice(modelChoice) { store.remember("modelChoice", modelChoice); store.set({ modelChoice }); },
  setDraftEnquiry(draftEnquiry) {
    Object.assign(store.get(), { draftEnquiry, selectedExample: "", answers: {}, rejected: [], queryNotice: "", skipQueryAutosave: false }); // keep typing without a re-render
    renderQuerySidebar($("query-sidebar"), store.get(), actions);
  },
  setExample(selectedExample, draftEnquiry) {
    Object.assign(store.get(), { selectedExample, draftEnquiry, answers: {}, rejected: [], queryNotice: "", skipQueryAutosave: false });
    renderQuerySidebar($("query-sidebar"), store.get(), actions);
  },
  toggleQuerySidebar() { store.set({ querySidebarOpen: !store.get().querySidebarOpen }); },
  async saveQuery({ silent = false } = {}) {
    const s = store.get();
    const enquiry = s.draftEnquiry ?? s.run?.enquiry ?? "";
    if (!enquiry.trim() || s.savingQuery) return;
    const id = s.activeQueryId;
    const draft = { id, enquiry, mode: s.mode, modelChoice: s.modelChoice, paths: [...s.paths], view: s.view };
    store.set({ savingQuery: true, queryNotice: "" });
    try {
      const saved = await queryRepository.save(draft);
      const savedQueries = await queryRepository.list();
      const current = store.get();
      const stillCurrent = current.activeQueryId === id && (current.draftEnquiry ?? current.run?.enquiry ?? "") === enquiry;
      store.set({ savedQueries, queryPersistent: queryRepository.persistent, queryStorageLabel: queryRepository.label, savingQuery: false,
        ...(stillCurrent ? { activeQueryId: saved.id, skipQueryAutosave: false } : {}),
        queryNotice: silent ? "" : queryRepository.persistent ? "Query saved." : "Saved for this session." });
    } catch (_) { store.set({ savingQuery: false, queryNotice: "Could not save this query." }); }
  },
  async newQuery() {
    if (store.get().busy) return;
    if (!store.get().skipQueryAutosave) await actions.saveQuery({ silent: true });
    openReadingDraft();
  },
  async openQuery(id) {
    if (store.get().busy) return;
    if (!store.get().skipQueryAutosave) await actions.saveQuery({ silent: true });
    const query = (await queryRepository.list()).find((item) => item.id === id);
    if (!query) return;
    openReadingDraft(query);
    const runs = await loadQueryRuns(id);
    if (runs.length && store.get().activeQueryId === id) await actions.openRun(runs[0].runId, id);  // latest result
  },
  async removeQuery(id) {
    await queryRepository.remove(id);
    store.set({ savedQueries: await queryRepository.list(), queryPersistent: queryRepository.persistent,
      ...(store.get().activeQueryId === id ? { activeQueryId: null, skipQueryAutosave: true } : {}), queryNotice: "Query removed." });
  },
  async openRun(id, queryId = null) {
    if (store.get().busy) return;
    try {
      const run = await getJSON(`/api/runs/${encodeURIComponent(id)}`);
      setDetected(run.requirements?.preferred_paths || []);
      const tab = run.error ? "reading" : "assessment";
      const activeQueryId = queryId || store.get().savedQueries.find((q) => q.lastRunId === id)?.id || null;
      store.remember("tab", tab);
      if (activeQueryId !== store.get().queryRuns?.queryId) store.set({ queryRuns: null });
      store.set({ run, previous: null, liveRun: null, error: "", understand: null, evidence: null, tab,
        draftEnquiry: null, activeQueryId,
        paths: run.preferred_paths || [], rejected: [],
        answers: Object.fromEntries(Object.entries(run.answers || {}).filter(([key]) => /^Path [ABC] - /.test(key))) });
      history.replaceState(null, "", `#run=${id}`);
      window.scrollTo(0, 0);
      if (activeQueryId && store.get().queryRuns?.queryId !== activeQueryId) loadQueryRuns(activeQueryId);
    } catch (err) {
      store.set({ queryNotice: "Could not open that result.", error: `Could not open the saved result: ${err.message}` });
    }
  },
  selectTab(id) {
    const tab = normalizeTab(id, store.get().view);
    if (!canOpenStep(store.get(), tab)) return;
    store.remember("tab", tab);
    store.set({ tab });
  },
  setAnswer(key, value) { store.get().answers[key] = value; },           // no re-render while typing
  async understand(enquiry) {
    const request = ++readingRequest;
    store.set({ reading: true, error: "", draftEnquiry: enquiry, tab: "reading" });
    await actions.saveQuery({ silent: true });
    if (request !== readingRequest) return;
    try {
      const data = await postJSON("/api/understand", { enquiry, answers: {}, preferred_paths: [...store.get().paths],
        model: chosenModel() });
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
      if (request === readingRequest) {
        store.set({ reading: false });
      }
    }
  },
  closeConfirm() {
    ++readingRequest;
    store.set({ understand: null, rejected: [], reading: false });
    $("enq")?.focus({ preventScroll: true });
  },
  async confirmRun() {
    const s = store.get();
    const u = s.understand;
    if (!u || s.busy || s.reading || s.savingQuery) return;
    const shown = new Set([...u.paths.chosen, ...u.paths.detected]);
    const answers = Object.fromEntries(Object.entries(s.answers).filter(([key, value]) => {
      if (!value.trim()) return false;
      const path = key.match(/^Path ([ABC]) - /);
      return !path || shown.has(path[1]);
    }));
    await actions.saveQuery({ silent: true });
    if (store.get().understand !== u || store.get().busy) return;
    await run("/api/assess", { enquiry: u.enquiry, answers, mode: s.mode,
      preferred_paths: s.paths, rejected: [...s.rejected], model: chosenModel() });
  },
  async assess(enquiry) {
    if (!enquiry.trim()) { store.set({ error: "Type or load an enquiry first." }); return; }
    const s = store.get();
    if (s.busy || s.reading) return;
    Object.assign(s, { draftEnquiry: enquiry });
    if (s.confirm) { await actions.understand(enquiry.trim()); return; }
    await actions.saveQuery({ silent: true });
    const answers = activePathAnswers(Object.fromEntries(Object.entries(s.answers).filter(([, value]) => value.trim())));
    await run("/api/assess", { enquiry, answers, mode: s.mode, preferred_paths: s.paths, model: chosenModel() });
  },
  async assessCouncil() {
    const r = store.get().busy ? null : store.get().run;
    if (r) { store.remember("mode", "council"); store.set({ mode: "council", answers: {} }); await run("/api/assess", {
      enquiry: r.enquiry, answers: r.answers, mode: "council", preferred_paths: r.preferred_paths || [], rejected: r.rejected || [],
      model: r.model_choice || null }); }
  },
  async whatif() {
    const s = store.get();
    if (!s.run) return;
    const answers = activePathAnswers(Object.fromEntries(Object.entries(s.answers).filter(([key, value]) =>
      value.trim() && s.run.answers?.[key] !== value)));
    const pathsChanged = JSON.stringify(s.paths) !== JSON.stringify(s.run.preferred_paths || []);
    if (!Object.keys(answers).length && !pathsChanged) { store.set({ error: "Type at least one answer, or change the preferred path in Customer Enquiry, first." }); return; }
    await run("/api/whatif", { run_id: s.run.id, answers, mode: s.mode, preferred_paths: s.paths, model: chosenModel() });
  },
};

// The chosen LLM for a request ("auto" = server defaults, sent as null).
function chosenModel() { const m = store.get().modelChoice; return m && m !== "auto" ? m : null; }

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
    run: null, liveRun, understand: null, reading: false, evidence: null,
    tab: store.get().view === "expert" ? "process" : "reading" });
  window.scrollTo(0, 0);
  let receivedResult = false;
  const s0 = store.get();
  const queryId = s0.activeQueryId;            // the saved query this run's result belongs to
  const headers = { "X-AFS-View": s0.view, ...(queryId ? { "X-AFS-Query-Id": queryId } : {}) };
  let finished = null;
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
        finished = e.run;
        const answers = Object.fromEntries(Object.entries(e.run.answers || {}).filter(([key]) => /^Path [ABC] - /.test(key)));
        const tab = s.view === "expert" ? "process" : e.run.error ? "reading" : normalizeTab(completionTab, s.view);
        store.remember("tab", tab);
        setDetected(e.run.requirements?.preferred_paths || []);
        store.set({ run: e.run, liveRun: e.run, tab,
          answers, paths: e.run.preferred_paths || [], rejected: [] });
        if (e.run.id) history.replaceState(null, "", `#run=${e.run.id}`);
      }
    }, headers);
  } catch (err) {
    store.set({ error: `Could not reach the assistant: ${err.message}` });
  } finally {
    if (!receivedResult) {
      const s = store.get();
      store.set({ run: { ...s.liveRun, error: s.error || "Run ended before a result was returned." },
        liveRun: null, busy: false, tab: s.view === "expert" ? "process" : "reading" });
    } else {
      const s = store.get();
      const tab = s.view === "expert" ? "process" : s.run?.error ? "reading" : normalizeTab(completionTab, s.view);
      store.remember("tab", tab);
      store.set({ liveRun: null, busy: false, tab });
    }
    if (store.get().run?.error) document.querySelector("#view .err")?.scrollIntoView({ block: "center" });
    else window.scrollTo(0, 0);
  }
  if (queryId && finished?.id) {                    // keep this result with its query (server: already linked)
    try {
      await queryRepository.attachRun(queryId, runSummary(finished, s0.view));
      store.set({ savedQueries: await queryRepository.list() });
    } catch (_) { /* keep the old list */ }
    await loadQueryRuns(queryId);
  }
}

function renderView(s) {
  const el = $("view");
  const disclosures = new Map([...el.querySelectorAll("[data-process-section]")]
    .map((node) => [node.dataset.processSection, node.open]));
  const run = s.busy ? s.liveRun : s.run;
  const step = s.busy && s.view !== "expert" ? LOADING_PAGE : STEPS.find((item) => item.id === s.tab);
  const readingPage = !s.busy && s.tab === "reading";
  el.innerHTML = readingPage ? `<div class="reading-layout">
    <aside id="query-sidebar" class="query-sidebar" aria-labelledby="saved-queries-title"></aside>
    <div id="reading-main" class="reading-main"><div id="stage-content" class="page-content"></div></div>
  </div>` : `<div id="stage-content" class="page-content"></div>`;
  const content = el.querySelector("#stage-content");
  if (s.busy && s.view !== "expert") {
    renderLoadingFlow(content, run, s);
  } else if (s.view === "expert" && s.tab === "process") {
    renderProcessInformation(content, run, s, actions);
    content.querySelectorAll("[data-process-section]").forEach((node) => {
      if (disclosures.has(node.dataset.processSection)) node.open = disclosures.get(node.dataset.processSection);
    });
  } else if (s.tab === "reading") {
    renderQuerySidebar($("query-sidebar"), s, actions);
    renderEnquiry(content, s, actions);
  } else {
    const stage = { assessment: "report", verification: "verify", coach: "coach" }[s.tab];
    if (hasStageData(run, stage)) {
      renderPipelineStep(content, stage, run, { ...s, run }, actions);
    } else if (!run && !s.busy && !s.error) {
      content.innerHTML = `<div class="empty"><h2>Start with a customer enquiry</h2>
        <p>Open Customer Enquiry to type an enquiry or load a scenario. Each tab above shows its results as the pipeline runs.</p></div>`;
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
  renderPageNavigation(content, s, step);
}

let lastEvidence = null;
function render(s) {
  renderStatus($("status"), s, actions);
  renderFiber($("fiber"), s, actions.selectTab);
  const transientLoading = s.busy && s.view !== "expert";
  $("view").setAttribute("role", transientLoading ? "region" : "tabpanel");
  $("view").setAttribute("aria-busy", String(s.busy || s.reading));
  $("view").setAttribute("aria-labelledby", transientLoading ? "page-title-loading" : `tab-${s.tab}`);
  renderView(s);
  renderConfirm($("reading-review"), s, actions);
  // Keep the selected source and its scroll position when leaving the assessment.
  const showEvidence = s.tab === "assessment" && !s.busy && !!s.evidence;
  $("drawer").hidden = !showEvidence;
  document.querySelector(".shell").classList.toggle("with-drawer", showEvidence);
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
document.addEventListener("keydown", (ev) => {
  if (ev.key === "Escape" && !$("drawer").hidden && store.get().evidence && !document.querySelector(".page-navigation:popover-open")) store.set({ evidence: null });
});

store.subscribe(render);
const accountProps = { openRun: (id) => actions.openRun(id) };
compactSidebar.addEventListener("change", (event) => store.set({ querySidebarOpen: !event.matches }));

// Logged in: history lives in the account (Supabase, local SQLite as fallback). Guest (only with
// AUTH_REQUIRED=0): in this browser. The plan decides the views: Basic = General, Pro = General + Expert.
async function loadAccount() {
  let user = null;
  try { user = (await getJSON("/api/auth/me")).user; } catch (_) { /* server starting: stay guest */ }
  store.set({ user });
  mountAccountControls($("account-actions"), { ...accountProps, user });
  if (!user) return;
  const server = createServerQueryRepository();
  try {
    await importLocalDrafts(user.id, localQueries, server);
    await server.list();
    queryRepository = server;
  } catch (_) { /* account store unreachable: keep browser drafts */ }
}

(async function boot() {
  await loadAccount();
  const linkedRun = location.hash.match(/run=([\w-]+)/);
  const view = isPro(store.get().user) ? store.recall("view", "general") : "general";
  const preferredTab = normalizeTab(store.recall("tab", linkedRun ? "assessment" : "reading"), view);
  store.set({ tab: canOpenStep(store.get(), preferredTab) ? preferredTab : "reading",
    savedQueries: await queryRepository.list(), queryPersistent: queryRepository.persistent,
    queryStorageLabel: queryRepository.label, querySidebarOpen: !compactSidebar.matches,
    mode: store.recall("mode", "fast"), modelChoice: store.recall("modelChoice", "auto"),
    view, confirm: store.recall("confirm", "on") === "on" });
  try { store.set({ health: await getJSON("/api/health") }); } catch (_) { /* server starting */ }
  try { store.set({ examples: await getJSON("/api/examples") }); } catch (_) { /* optional */ }
  try {
    const modelList = await getJSON("/api/models");
    const keep = modelList.models.some((m) => m.id === store.get().modelChoice);
    store.set({ modelList, modelChoice: keep ? store.get().modelChoice : "auto" });   // a stored model the key lost
  } catch (_) { /* older server: dropdown falls back to the health list */ }
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
