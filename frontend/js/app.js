// Boot, live pipeline state, and navigation between its steps.
import { esc, getJSON, stream } from "./api.js";
import * as store from "./state.js";
import { STEPS, UTILITIES, activeStep, canonicalStage, isStep, latestStageEvent, normalizeTab, stepStatus } from "./pipeline-steps.js";
import { renderStatus, renderFiber } from "./components/header.js";
import { renderEnquiry } from "./components/enquiry.js";
import { hasStageData, renderPipelineStep } from "./components/pipeline.js";
import { renderEvidence } from "./components/evidence.js";
import { renderCouncil } from "./components/council.js";
import { renderWhatIf } from "./components/whatif.js";
import { renderTrace } from "./components/trace.js";

const $ = (id) => document.getElementById(id);

const actions = {
  setMode(mode) { store.remember("mode", mode); store.set({ mode }); },
  selectTab(id) {
    const tab = normalizeTab(id);
    store.remember("tab", tab);
    store.set({ tab, followStage: false });
  },
  followCurrent() {
    const current = activeStep(store.get());
    if (current) store.set({ tab: current, followStage: true });
  },
  setAnswer(key, value) { store.get().answers[key] = value; },           // no re-render while typing
  async assess(enquiry) {
    if (!enquiry.trim()) { store.set({ error: "Type or load an enquiry first." }); return; }
    store.set({ answers: {} });
    await run("/api/assess", { enquiry, mode: store.get().mode });
  },
  async assessCouncil() {
    const r = store.get().busy ? null : store.get().run;
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
  const previous = store.get().run;
  const liveRun = {
    enquiry: body.enquiry || previous?.enquiry || "",
    answers: body.answers || previous?.answers || {},
    mode: body.mode || store.get().mode,
    timings_ms: {},
  };
  store.set({ busy: true, error: "", stages: [], details: [], previous,
    run: null, liveRun, tab: "extract", followStage: true });
  let receivedResult = false;
  try {
    await stream(url, body, (e) => {
      const s = store.get();
      if (e.type === "stage") {
        store.set({ stages: [...s.stages, e],
          ...(e.status === "start" && s.followStage ? { tab: canonicalStage(e.stage) } : {}) });
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
        const tab = s.followStage && !e.run.error ? (isWhatIf ? "whatif" : "report") : s.tab;
        store.set({ run: e.run, liveRun: e.run, tab, answers: {} });
        if (e.run.id) history.replaceState(null, "", `#run=${e.run.id}`);
      }
    });
  } catch (err) {
    store.set({ error: `Could not reach the assistant: ${err.message}` });
  } finally {
    if (!receivedResult) {
      const s = store.get();
      store.set({ run: { ...s.liveRun, error: s.error || "Run ended before a result was returned." },
        liveRun: null, busy: false });
    } else {
      store.set({ liveRun: null, busy: false });
    }
  }
}

function renderTools(s) {
  const focused = document.activeElement?.dataset.tab;
  $("tools").innerHTML = `<span class="small muted">Explore</span>${UTILITIES.map((item) =>
    `<button type="button" id="tab-${item.id}" data-tab="${item.id}" aria-controls="view"
      aria-pressed="${s.tab === item.id}" class="${s.tab === item.id ? "selected" : ""}">${item.label}</button>`).join("")}`;
  $("tools").querySelectorAll("[data-tab]").forEach((button) =>
    (button.onclick = () => actions.selectTab(button.dataset.tab)));
  if (focused) $("tools").querySelector(`[data-tab="${focused}"]`)?.focus({ preventScroll: true });
  $("view").setAttribute("role", isStep(s.tab) ? "tabpanel" : "region");
  $("view").setAttribute("aria-labelledby", `tab-${s.tab}`);
}

function renderView(s) {
  const el = $("view");
  const run = s.busy ? s.liveRun : s.run;
  if (!isStep(s.tab)) {
    if (!run?.id || s.busy) {
      const current = s.busy ? activeStep(s) : null;
      el.innerHTML = `<div class="stage-placeholder">This view is available when the current assessment finishes.
        ${current ? `<p>Currently running: ${esc(STEPS.find((item) => item.id === current).label)}</p>` : ""}
        ${s.busy && !s.followStage && current ? `<button type="button" class="btn" id="followStep">Follow current step</button>` : ""}</div>`;
      el.querySelector("#followStep")?.addEventListener("click", actions.followCurrent);
      return;
    }
    if (s.tab === "whatif") renderWhatIf(el, { ...s, run }, actions);
    else if (s.tab === "council") renderCouncil(el, run, actions);
    else renderTrace(el, run);
    return;
  }

  const step = STEPS.find((item) => item.id === s.tab);
  const status = stepStatus(s, step.id);
  const event = latestStageEvent(s, step.id);
  const current = s.busy ? activeStep(s) : null;
  const details = s.details.filter((item) => canonicalStage(item.stage) === step.id);
  el.innerHTML = `<div class="stage-header">
    <div><h2>${step.label}</h2><p class="small muted">${step.description}</p>
      ${event?.detail ? `<p class="stage-note">${esc(event.detail)}${event.ms != null ? ` · ${event.ms} ms` : ""}</p>` : ""}
      ${details.length ? `<p class="stage-note">${esc(details.at(-1).detail)}</p>` : ""}
      ${s.busy && current && current !== step.id ? `<p class="stage-note">Currently running: ${esc(STEPS.find((item) => item.id === current).label)}</p>` : ""}</div>
    ${s.busy && !s.followStage && current ? `<button type="button" class="btn" id="followStep">Follow current step</button>` : ""}
  </div><div id="stage-content"></div>`;
  el.querySelector("#followStep")?.addEventListener("click", actions.followCurrent);
  const content = el.querySelector("#stage-content");
  if (hasStageData(run, step.id)) {
    renderPipelineStep(content, step.id, run, { ...s, run }, actions);
  } else if (!run && !s.busy && !s.error) {
    content.innerHTML = `<div class="empty"><h2>Start with a customer enquiry</h2>
      <p>Load a scenario or type an enquiry. Each step above opens its own result as the pipeline runs; choose a step to inspect it, or follow the live step.</p>
      <p class="small">Fast mode uses one model; Council mode lets several models draft and judge each other.</p></div>`;
  } else {
    const message = status === "active" ? "This step is running. Its output will appear here when it finishes." :
      status === "error" ? "The run stopped before this step produced an output." :
      status === "done" ? "This step finished. Waiting for its output to arrive." :
      "This step has not run yet.";
    content.innerHTML = `<div class="stage-placeholder">${message}${status === "error" && (s.error || run?.error) ?
      `<div class="err">${esc(s.error || run.error)}</div>` : ""}</div>`;
  }
}

let lastEvidence = null;
function render(s) {
  renderStatus($("status"), s);
  renderFiber($("fiber"), s, actions.selectTab);
  renderEnquiry($("enquiry"), s, actions);
  renderTools(s);
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
  store.set({ tab: normalizeTab(store.recall("tab", linkedRun ? "report" : "extract")),
    mode: store.recall("mode", "fast") });
  try { store.set({ health: await getJSON("/api/health") }); } catch (_) { /* server starting */ }
  try { store.set({ examples: await getJSON("/api/examples") }); } catch (_) { /* optional */ }
  if (linkedRun) { try { store.set({ run: await getJSON(`/api/runs/${linkedRun[1]}`) }); } catch (_) { /* old link */ } }
})();
