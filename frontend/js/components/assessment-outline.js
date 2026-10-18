// Presentation slots for the next assessment format. No mapping from the current RAG report yet.
import { esc } from "../api.js";
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
  ["first_feasibility_experiment_prototype", "First feasibility experiment prototype", ""],
];

export function renderAssessmentOutline(el, run = {}) {
  el.innerHTML = `<div class="assessment-preview" role="note">
    <span class="assessment-preview-label">Layout preview</span>
    <p>These sections are placeholders for the next assessment format.</p>
  </div>
  <article class="assessment-document" aria-label="Result assessment outline">
    ${SECTIONS.map(([key, title, description], index) => {
      const id = `assessment-${key.replaceAll("_", "-")}`;
      const diagram = key === "first_feasibility_experiment_prototype";
      return `<section class="assessment-section${diagram ? " assessment-diagram" : ""}" data-assessment-field="${key}" aria-labelledby="${id}">
        <div class="assessment-section-heading"><span class="assessment-section-number" aria-hidden="true">${String(index + 1).padStart(2, "0")}</span>
          <h2 id="${id}">${esc(title)}</h2></div>
        <div class="assessment-field-content" id="${id}-content">
          ${diagram ? projectSetupHTML(run) : `<p class="assessment-placeholder-copy">${esc(description)}</p>
          <div class="assessment-placeholder-lines" aria-hidden="true"><span></span><span></span></div>`}
        </div>
      </section>`;
    }).join("")}
  </article>`;
}
