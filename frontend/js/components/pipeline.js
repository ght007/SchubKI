// Pipeline result views. The Reading tab contains the enquiry form in enquiry.js.
import { esc } from "../api.js";
import { renderMatrix } from "./matrix.js";
import { renderSpectral } from "./spectral-map.js";
import { renderAssessmentOutline } from "./assessment-outline.js";
import { renderCouncil } from "./council.js";
import { renderQuality } from "./quality.js";
import { renderCoach } from "./coach.js";
import { renderTrace } from "./trace.js";
import { renderWhatIf } from "./whatif.js";

const list = (value) => Array.isArray(value) ? value : [];
const own = (object, key) => !!object && Object.prototype.hasOwnProperty.call(object, key);

// A finished run has default empty arrays even for stages it never reached after an error.
// Stage-result deltas, in contrast, add a field only when that stage finishes.
function stageCompleted(run, stage, field) {
  if (own(run?.timings_ms, "total")) return own(run.timings_ms, stage);
  return own(run, field);
}

export function hasStageData(run, stepId) {
  if (!run) return false;
  switch (stepId) {
    case "extract": return !!run.requirements;
    case "rules": return stageCompleted(run, "rules", "matrix") || list(run.matrix).length > 0;
    case "retrieve": return stageCompleted(run, "retrieve", "retrieval") || list(run.evidence).length > 0;
    case "premise": return stageCompleted(run, "premise", "premises") || list(run.premises).length > 0;
    case "report": return !!run.report;
    case "verify": return !!run.verification || !!run.quality;
    case "coach": return !!run.coach || !!run.confidence;
    default: return false;
  }
}

function cite(item) {
  return `<button type="button" class="cite" data-src="${esc(item.source)}" data-page="${esc(item.page)}"
    data-quote="${esc(item.quote || item.highlight || "")}" aria-label="Open ${esc(item.source)} page ${esc(item.page)}">${esc(item.source)} p.${esc(item.page)}</button>`;
}

function renderExtract(el, run) {
  const requirements = run.requirements || {};
  const facts = list(requirements.facts);
  const unknowns = list(requirements.unknowns);
  const premises = list(requirements.premises);
  el.innerHTML = `
    <section class="section"><h2>Extracted requirements <small>${facts.length} facts · ${unknowns.length} unknowns · ${premises.length} premises</small></h2>
      <p>${esc(requirements.summary || "No summary was produced.")}</p>
      <div class="stage-grid">
        <div class="stage-card"><h3>Target</h3><p>${list(requirements.target_variables).map(esc).join(", ") || "Not yet defined"}</p>
          <p class="small muted">Definition: ${esc(requirements.target_defined || "unknown")}</p></div>
        <div class="stage-card"><h3>Sample and process</h3><p>${esc(requirements.matrix || "unknown")} · ${esc(requirements.phase || "unknown")}</p>
          <p class="small muted">Context: ${esc(String(requirements.process_context || "unknown").replaceAll("_", " "))}</p></div>
        <div class="stage-card"><h3>Requested methods and assets</h3>
          <p>${list(requirements.requested_methods).map(esc).join(", ") || "No method specified"}</p>
          <p class="small muted">Assets: ${list(requirements.existing_assets).map(esc).join(", ") || "none stated"}</p></div>
      </div>
      ${facts.some((fact) => fact.status === "inferred") ? `<p class="stage-note">Inferred facts are marked below and should be confirmed with the client.</p>` : ""}
    </section>
    <div class="stage-grid">
      <section class="stage-card"><h3>Known facts</h3>
        ${facts.length ? `<ul class="plain">${facts.map((fact) => `<li><b>${esc(fact.field)}:</b> ${esc(fact.value)}
          <span class="small muted">(${esc(fact.status)})</span>${fact.quote ? `<div class="small muted"><q>${esc(fact.quote)}</q></div>` : ""}</li>`).join("")}</ul>` : `<p class="muted">No facts were extracted.</p>`}
      </section>
      <section class="stage-card"><h3>Unknowns to resolve</h3>
        ${unknowns.length ? `<ul class="plain">${unknowns.map((unknown) => `<li><span class="impact ${esc(unknown.impact)}">${esc(unknown.impact)}</span>
          <b>${esc(unknown.item)}</b>${unknown.why_it_matters ? `<div class="small muted">${esc(unknown.why_it_matters)}</div>` : ""}</li>`).join("")}</ul>` : `<p class="muted">No unknowns were listed.</p>`}
      </section>
      <section class="stage-card"><h3>Client premises to check</h3>
        ${premises.length ? `<ul class="plain">${premises.map((premise) => `<li><b>${esc(premise.id)}</b> ${esc(premise.statement)}
          <div class="small muted">${esc(String(premise.kind || "other").replaceAll("_", " "))}</div></li>`).join("")}</ul>` : `<p class="muted">No explicit client premises were identified.</p>`}
      </section>
    </div>`;
}

function renderRules(el, run) {
  el.innerHTML = `<p class="stage-note">These screening scores come from deterministic AFS rules. They identify methods to compare in a feasibility study.</p>`;
  const matrixEl = document.createElement("div");
  el.appendChild(matrixEl);
  renderMatrix(matrixEl, run);
  const mapEl = document.createElement("div");
  el.appendChild(mapEl);
  if (run.spectral && Object.keys(run.spectral).length) {
    renderSpectral(mapEl, { ...run, matrix: list(run.matrix), coverage: list(run.coverage) });
  } else {
    mapEl.innerHTML = `<div class="stage-placeholder">Spectral coverage was not mapped for this run.</div>`;
  }
}

function renderRetrieve(el, run) {
  const retrieval = run.retrieval || {};
  const queries = list(retrieval.queries);
  const evidence = list(run.evidence);
  el.innerHTML = `
    <section class="section"><h2>Search queries <small>${queries.length} built from requirements and rule findings</small></h2>
      ${queries.length ? `<ol class="steps">${queries.map((query) => `<li>${esc(query)}</li>`).join("")}</ol>` : `<p class="muted">No search queries were recorded.</p>`}
      <p class="small muted">SQLite full-text search and dense similarity are fused before diverse passages are selected.
        ${retrieval.used_tokens != null ? `Selected passage budget: ${esc(retrieval.used_tokens)} tokens.` : ""}</p>
    </section>
    <section class="section"><h2>Retrieved evidence <small>${evidence.length} passages</small></h2>
      ${evidence.length ? `<ul class="plain rule-list">${evidence.map((item) => {
        const excerpt = String(item.text || "");
        return `<li><b>${esc(item.ref)}</b> ${cite(item)}
          <span class="small muted">${esc(item.kind)}${item.scope ? ` · ${esc(item.scope)}` : ""}${item.score != null ? ` · RRF ${esc(item.score)}` : ""}</span>
          <div class="small">${item.highlight ? `<mark>${esc(item.highlight)}</mark>` : `${esc(excerpt.slice(0, 360))}${excerpt.length > 360 ? "…" : ""}`}</div></li>`;
      }).join("")}</ul>` : `<p class="muted">No passages were selected. Review the search queries and source index.</p>`}
    </section>`;
}

function renderPremise(el, run) {
  const verdicts = list(run.premises);
  const expected = list(run.requirements?.premises);
  el.innerHTML = `
    <section class="section"><h2>Client premise check <small>${verdicts.length} verdicts</small></h2>
      <p class="small muted">Each client claim is tested against the retrieved AFS sources before the assessment is written.</p>
      ${verdicts.length ? verdicts.map((item) => `<div class="premise"><div class="verdict ${esc(item.verdict)}">${esc(String(item.verdict || "").replaceAll("_", " "))}</div>
        <div><b>${esc(item.premise_id)}</b> <q>${esc(item.statement)}</q><p>${esc(item.explanation)}
          ${list(item.citations).map(cite).join("")}</p></div></div>`).join("") :
          `<p class="stage-note">${expected.length ? "No verdicts were produced for the identified premises." : "No client premises needed a separate check."}</p>`}
    </section>`;
}

function renderAssessment(el, run, state) {
  renderAssessmentOutline(el, run);
  if (!state.busy && run.id) {
    const download = `<div class="assessment-export">
      <a class="btn" href="/api/runs/${encodeURIComponent(run.id)}/export.md" download>Download report (Markdown)</a>
    </div>`;
    el.insertAdjacentHTML("afterbegin", download);
    el.insertAdjacentHTML("beforeend", download);
  }
}

function renderCoachStep(el, run, state, actions) {
  el.innerHTML = `<section class="section" data-coach></section><details class="section" data-whatif ${run.parent_run_id ? "open" : ""}>
    <summary>What if the customer supplies answers?</summary><div></div></details>`;
  renderCoach(el.querySelector("[data-coach]"), { ...state, answers: state?.answers || {}, run }, actions);
  renderWhatIf(el.querySelector("[data-whatif] > div"), { ...state, run }, actions);
}

const PROCESS_STAGES = [
  ["extract", "Read the enquiry", "LLM extracts facts; rule fallback if unavailable", "Reading your enquiry"],
  ["rules", "Apply AFS rules", "Deterministic rules, screening, and fiber coverage", "Checking suitable methods"],
  ["retrieve", "Retrieve knowledge base evidence", "Full-text and dense search; deterministic ranking", "Finding supporting sources"],
  ["premise", "Check customer premises", "LLM compares claims with sources; rule fallback if unavailable", "Reviewing the enquiry"],
  ["report", "Write the assessment", "Single LLM or Council drafts and judging", "Preparing the assessment"],
  ["verify", "Verify and check quality", "Deterministic checks; optional LLM repair", "Checking the results"],
  ["coach", "Coach and compute confidence", "LLM drafts follow-up text; confidence is computed", "Preparing follow-up questions"],
];

function processStageState(state, run, stage) {
  const event = [...state.stages].reverse().find((item) => (item.stage === stage ||
    (stage === "report" && item.stage === "council")) && ["start", "done"].includes(item.status));
  if (event?.status === "done" || own(run?.timings_ms, stage) || (stage === "report" && own(run?.timings_ms, "council"))) return "done";
  if (event?.status === "start") return state.busy ? "active" : "error";
  return "pending";
}

function processActor(run, stage, fallback) {
  const calls = list(run?.trace).filter((item) => item.stage === stage ||
    (stage === "report" && item.stage.startsWith("council_")) ||
    (stage === "verify" && item.stage === "repair"));
  if (!calls.length) return fallback;
  return [...new Set(calls.map((item) => `${item.model}${item.ok ? "" : " (fallback)"}`))].map(esc).join(", ");
}

export function renderLoadingFlow(el, run, state) {
  el.innerHTML = `<section class="section process-flow"><h2 id="loading-progress">Assessment progress</h2>
    <p class="muted">Your results will open when all steps are complete.</p>
    <ol class="process-list">${PROCESS_STAGES.map(([stage, , , label]) => {
      const status = processStageState(state, run, stage);
      const statusLabel = { done: "Complete", active: "In progress", pending: "Waiting", error: "Stopped" }[status];
      return `<li class="process-item ${status}" aria-label="${esc(label)}: ${statusLabel}">
        <span class="process-marker" aria-hidden="true"></span><div class="process-title"><b>${esc(label)}</b>
          ${status === "active" ? '<span class="small muted" role="status">In progress</span>' : ""}</div></li>`;
    }).join("")}</ol>
  </section>`;
}

export function renderProcessInformation(el, run, state, actions) {
  if (state.view !== "expert") { renderLoadingFlow(el, run, state); return; }
  const active = PROCESS_STAGES.find(([stage]) => processStageState(state, run, stage) === "active");
  const activeStage = [...state.stages].reverse().find((event) => event.status === "start")?.stage;
  const activity = [...state.details].reverse().find((item) => item.stage === activeStage)?.detail;
  const finishing = PROCESS_STAGES.every(([stage]) => processStageState(state, run, stage) === "done");
  el.innerHTML = `${state.busy ? `<section class="section process-live" aria-live="polite">
    <h2 id="process-activity">Working on your assessment</h2>
    <p><b>${esc(active?.[1] || (finishing ? "Finalizing the assessment" : "Starting the pipeline"))}</b></p>
    <p>${esc(finishing ? "Waiting for the calculation to finish before unlocking the result tabs." :
      activity || [...state.stages].reverse().find((event) => event.status === "start")?.label || "Preparing the first stage…")}</p>
  </section>` : run?.error ? `<section class="section stage-placeholder"><h2 id="process-activity">Processing stopped</h2><p class="err">${esc(run.error)}</p><p>Open Customer Enquiry to edit the enquiry and try again.</p></section>` :
    run?.id ? `<section class="section process-live"><h2 id="process-activity">Calculation complete</h2><p>Result Assessment, Confidence and Verification, and Coach are now available. The calculation record stays here for review.</p></section>` : ""}
  <section class="section"><h2 id="process-stages">Calculation stages</h2>
    <p class="small muted">${state.busy ? "Follow each model or rule task as it runs. Completed model calls appear in the trace below as soon as their stage finishes." : "Recorded model and rule tasks, with their timings and outputs."}</p>
    <ol class="process-list">${PROCESS_STAGES.map(([stage, label, actor]) => {
      const status = processStageState(state, run, stage);
      const time = run?.timings_ms?.[stage] ?? (stage === "report" ? run?.timings_ms?.council : null);
      return `<li class="process-item ${status}"><span class="process-marker" aria-hidden="true"></span><div>
        <div class="process-title"><b>${esc(label)}</b><span class="res ${status === "done" ? "pass" : status === "error" ? "fail" : "warn"}">${status === "done" ? "Finished" : status === "active" ? "Running" : status === "error" ? "Stopped" : "Waiting"}</span></div>
        <p class="small muted">${processActor(run, stage, actor)}${time != null ? ` · ${esc(time)} ms` : ""}</p>
      </div></li>`;
    }).join("")}</ol>
  </section>`;
  if (!run) return;
  const trace = document.createElement("details");
  trace.className = "section";
  trace.dataset.processSection = "trace";
  trace.innerHTML = `<summary id="process-trace">Model calls and timing</summary><div></div>`;
  trace.open = state.busy && state.view === "expert";
  el.appendChild(trace);
  renderTrace(trace.querySelector("div"), run);
  if (run.mode === "council" || (!state.busy && run.id)) {
    const council = document.createElement("details");
    council.className = "section";
    council.dataset.processSection = "council";
    council.innerHTML = `<summary id="process-council">Council drafts and judging</summary><div></div>`;
    council.open = state.busy && activeStage === "council";
    el.appendChild(council);
    if (state.busy && !run.council) {
      council.querySelector("div").innerHTML = `<p class="small muted">${esc(activity && activeStage === "council" ? activity :
        "Council drafting and blind judging will appear here when this stage runs.")}</p>`;
    } else {
      renderCouncil(council.querySelector("div"), run, actions);
    }
  }
}

export function renderPipelineStep(el, stepId, run, state = {}, actions = {}) {
  if (!hasStageData(run, stepId)) {
    const message = run?.error && !state.busy
      ? `This run stopped before this stage: ${run.error}`
      : state.busy ? "This stage has not finished yet. Its results will appear here as the pipeline runs."
        : "Start an assessment to see this stage's results.";
    el.innerHTML = `<div class="stage-placeholder"><h2>${esc(stepId === "report" ? "Assessment" : stepId || "Pipeline step")}</h2><p>${esc(message)}</p></div>`;
    return;
  }
  switch (stepId) {
    case "extract": renderExtract(el, run); break;
    case "rules": renderRules(el, run); break;
    case "retrieve": renderRetrieve(el, run); break;
    case "premise": renderPremise(el, run); break;
    case "report": renderAssessment(el, run, state); break;
    case "verify": renderQuality(el, run); break;
    case "coach": renderCoachStep(el, run, state, actions); break;
  }
}