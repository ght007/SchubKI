// The seven navigable pipeline views. Each reads only the data produced at its stage.
import { esc } from "../api.js";
import { renderMatrix } from "./matrix.js";
import { renderSpectral } from "./spectral-map.js";
import { renderReport } from "./report.js";
import { renderCouncil } from "./council.js";
import { renderVerification, renderConfidence } from "./quality.js";
import { renderCoach } from "./coach.js";

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
    data-quote="${esc(item.quote || "")}" aria-label="Open ${esc(item.source)} page ${esc(item.page)}">${esc(item.source)} p.${esc(item.page)}</button>`;
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
          <div class="small">${esc(excerpt.slice(0, 360))}${excerpt.length > 360 ? "…" : ""}</div></li>`;
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

function renderAssessment(el, run, state, actions) {
  const reportEl = document.createElement("div");
  el.replaceChildren(reportEl);
  renderReport(reportEl, run);
  // The export endpoint is available after the run is saved, not while the draft streams.
  if (state?.busy || !run.id) reportEl.querySelector(".toolbar")?.remove();
  if (list(run.council?.drafts).length) {
    const details = document.createElement("details");
    details.className = "section";
    details.innerHTML = `<summary>How the council selected this assessment</summary><div></div>`;
    el.appendChild(details);
    renderCouncil(details.querySelector("div"), run, actions);
  }
}

function renderVerify(el, run) {
  renderVerification(el, run);
}

function renderCoachStep(el, run, state, actions) {
  el.innerHTML = `<section class="section" data-coach></section><div data-confidence></div>`;
  renderCoach(el.querySelector("[data-coach]"), { ...state, answers: state?.answers || {}, run }, actions);
  renderConfidence(el.querySelector("[data-confidence]"), run);
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
    case "report": renderAssessment(el, run, state, actions); break;
    case "verify": renderVerify(el, run); break;
    case "coach": renderCoachStep(el, run, state, actions); break;
  }
}
