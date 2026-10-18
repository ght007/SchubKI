// The Result Assessment in the 11-section output format.
// Content comes from run.outline, built once by the backend (backend/app/render/outline.py) and also used by
// the Markdown export and outputs/. This file only presents it: no claims are written or rewritten here.
// Without an outline (run still in progress) the sections show their placeholders.
// Section keys, headings, IDs and order are stable hooks (docs/frontend-integration.md).
import { esc } from "../api.js";
import { annotate } from "../glossary.js";
import { citeChip } from "./report.js";
import { projectSetupHTML } from "./project-setup.js";

const SECTIONS = [
  ["decision_status", "Decision Status", "The feasibility decision and what can be concluded at this stage."],
  ["requirements_stated", "Requirements stated", "The customer's process, target, measurement location, and practical constraints."],
  ["key_unknowns", "Key unknowns", "Missing material, performance, reference, or installation information."],
  ["clarification_questions", "Clarification questions", "Questions needed to resolve the important gaps in the enquiry."],
  ["recommendation", "Recommendation", "Spectroscopy candidates, their reasoning, applicable conditions, and supporting sources."],
  ["measurement_concept", "Measurement concept", "A high-level probe, sampling interface, and installation concept."],
  ["spectral_range", "Spectral range", "Relevant usable spectral ranges and method-specific wavelength or shift details."],
  ["risks_and_uncertainty", "Risks and uncertainty", "Limitations, assumptions, and factors that could change the decision."],
  ["decision_basis", "Decision basis", "Client-agreed acceptance criteria for choosing an approach after the study."],
  ["sources", "Sources", "Supporting AFS materials, with quoted passages for any external sources."],
  ["first_feasibility_experiment_prototype", "First feasibility experiment", "Samples, reference measurements, comparisons, and steps for the first experiment."],
];
const KIND = { client_fact: "client fact", sourced: "sourced", assumption: "assumption", proposal: "proposal" };
const STATUS_PILL = { provisional_assessment: "core", insufficient_information: "warn", outside_supported_scope: "block" };
const CONF_PILL = { high: "ok", medium: "core", low: "warn", insufficient: "block" };
const WHO = { expert: "chosen in Reading", enquiry: "asked for by the customer", both: "asked for by customer and in Reading" };

const list = (items, tag = "ul") => items.length ? `<${tag} class="outline-list">${items.map((x) => `<li>${annotate(x)}</li>`).join("")}</${tag}>` : none();
const none = () => `<p class="muted small">Nothing reported for this section.</p>`;
const srcs = (xs) => xs.map((x) => `${esc(x.source)} p.${x.page}`).join(", ");

function stmt(s) {
  const grounded = s.kind === "sourced" && s.citations.length;
  return `<div class="stmt ${esc(s.kind)} ${esc(s.check)}">${grounded ? `<span class="grounded-text">${annotate(s.text)}</span>` : annotate(s.text)}${s.citations.map((c) => citeChip(c, s.check)).join("")}<span class="kind">${KIND[s.kind] || esc(s.kind)}</span></div>`;
}
const stmts = (items) => items.length ? items.map(stmt).join("") : none();

const RENDER = {
  decision_status: (c) => `
    <div class="outline-pills"><span class="pill ${STATUS_PILL[c.status] || ""}"><span class="dot"></span><b>${esc(c.status_label)}</b></span>
      ${c.confidence ? `<span class="pill ${CONF_PILL[c.confidence.level] || ""}" title="Computed from observable signals, not self-reported">Confidence <b>${esc(c.confidence.level)}</b></span>` : ""}</div>
    <div class="headline ${esc(c.status)}">${annotate(c.headline)}</div>
    ${c.blocking.length ? `<div class="pc-warn">${c.blocking.map((b) => `<p><b>${esc(b.title)}.</b> ${esc(b.text)} <span class="small">[${esc(b.sources.join(", "))}]</span></p>`).join("")}</div>` : ""}
    ${c.premises.length ? `<h3 class="outline-sub">The customer's own claims, tested first</h3>
      ${c.premises.map((p) => `<div class="premise"><div class="verdict ${esc(p.verdict)}">${esc(p.verdict.replace("_", " "))}</div>
        <div><q>${esc(p.statement)}</q><p>${esc(p.explanation)}${p.citations.map((x) => citeChip(x)).join("")}</p></div></div>`).join("")}` : ""}
    ${c.confidence?.raise_with?.length ? `<p class="small muted">To raise confidence, answer: ${c.confidence.raise_with.map(esc).join(" / ")}</p>` : ""}`,
  requirements_stated: (c) => list(c.items),
  key_unknowns: (c) => `${list(c.items)}${c.assumptions.length ? `<h3 class="outline-sub">Assumptions made</h3>${list(c.assumptions)}` : ""}`,
  clarification_questions: (c) => c.items.length ? `<ol class="outline-list">${c.items.map((q) => `<li><b>${annotate(q.question)}</b>
    <span class="tag">${esc(q.impact)} impact</span><div class="small muted">Why: ${esc(q.why)}</div></li>`).join("")}</ol>` : none(),
  recommendation: (c) => c.items.length ? c.items.map((r) => `<div class="outline-rec">
    <h3 class="outline-sub">${esc(r.method)} <span class="role ${esc(r.role)}">${esc(r.role.replace("_", " "))}</span></h3>
    ${stmts(r.rationale)}${r.conditions ? `<p class="small"><b>Applies if:</b> ${annotate(r.conditions)}</p>` : ""}</div>`).join("") : none(),
  measurement_concept: (c) => stmts(c.statements),
  spectral_range: (c) => stmts(c.statements),
  risks_and_uncertainty: (c) => `${stmts(c.statements)}${c.confidence ? `<details class="outline-details"><summary>Why the confidence is ${esc(c.confidence.level)}</summary>
    <ul class="outline-list small">${c.confidence.signals.map((s) => `<li><b>${esc(s.name)}</b>: ${esc(s.level)} (${esc(s.detail)})</li>`).join("")}
    ${c.confidence.caps.map((x) => `<li>Cap: ${esc(x)}</li>`).join("")}</ul></details>` : ""}`,
  decision_basis: (c) => list(c.items),
  sources: (c) => c.items.length ? `<ul class="outline-sources">${c.items.map((s) => `<li>
    <button type="button" class="cite" data-src="${esc(s.source)}" data-page="${s.page}" data-quote="${esc(s.quotes[0]?.quote || "")}"
      aria-label="Open source ${esc(s.source)} page ${s.page}"><span class="v"></span>${esc(s.source)} p.${s.page}</button>
    <span>${esc(s.title)}</span>${s.scope ? ` <span class="tag">${esc(s.scope)}</span>` : ""}
    ${s.quotes.map((q) => `<blockquote class="${esc(q.check)}">${esc(q.quote)}</blockquote>`).join("")}</li>`).join("")}</ul>` : none(),
  first_feasibility_experiment_prototype: (c) => {
    const plan = c.plan, pw = c.pathway;
    const block = (title, items, tag) => `<div class="outline-plan-block"><h3 class="outline-sub">${title}</h3>${list(items, tag)}</div>`;
    return `<div class="outline-plan">
      ${block("Samples", plan.samples)}${block("Reference measurements", plan.reference)}${block("Comparison", plan.comparison)}
      ${plan.steps.length ? block("Steps", plan.steps, "ol") : ""}</div>
    <h3 class="outline-sub">Next step with AFS</h3>
    <p>${annotate(pw.next_step)}</p>
    <p class="small">${pw.likely_path === "undecided" ? "Path to be decided after the lab trial." : `Likely path: <b>${esc(pw.likely_path)}</b>`}${pw.why ? ` · ${esc(pw.why)}` : ""}</p>
    ${pw.requested.map((f) => `<p class="small"><b>Path ${esc(f.path)}, ${esc(f.verdict)}</b> (${WHO[f.requested_by] || ""}): ${esc(f.reason)} <span class="muted">[${srcs(f.sources)}]</span></p>`).join("")}
    ${pw.proceed_anyway.map((p) => `<details class="proceed"><summary><b>If you proceed anyway with Path ${esc(p.path)}</b></summary>
      <p class="small">${esc(p.caveat)}</p><ol>${p.steps.map((x) => `<li>${esc(x)}</li>`).join("")}</ol>
      <p class="small muted">Sources: ${srcs(p.sources)}</p></details>`).join("")}`;
  },
};

export function renderAssessmentOutline(el, run = {}) {
  const filled = Object.fromEntries((run.outline?.sections || []).map((s) => [s.key, s]));
  const ready = Object.keys(filled).length > 0;
  el.innerHTML = `${ready ? "" : `<div class="assessment-preview" role="note">
    <span class="assessment-preview-label">Layout preview</span>
    <p>The sections fill in when the assessment is complete.</p>
  </div>`}
  <article class="assessment-document${ready ? " filled" : ""}" aria-label="Result assessment">
    ${SECTIONS.map(([key, title, description], index) => {
      const id = `assessment-${key.replaceAll("_", "-")}`;
      const content = filled[key];
      let body;
      if (content) body = RENDER[key](content);
      else body = `<p class="assessment-placeholder-copy">${esc(description)}</p>
          <div class="assessment-placeholder-lines" aria-hidden="true"><span></span><span></span></div>`;
      return `<section class="assessment-section" data-assessment-field="${key}" aria-labelledby="${id}">
        <div class="assessment-section-heading"><span class="assessment-section-number" aria-hidden="true">${String(index + 1).padStart(2, "0")}</span>
          <h2 id="${id}">${esc(title)}</h2></div>
        <div class="assessment-field-content" id="${id}-content">${body}</div>
      </section>`;
    }).join("")}
  </article>
  <section class="section setup-overview" aria-labelledby="setup-overview-title">
    <h2 id="setup-overview-title">Setup Overview</h2>
    ${projectSetupHTML(run)}
  </section>`;
}
