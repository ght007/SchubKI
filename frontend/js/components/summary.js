// General view: one compact page for internal non-experts (sales, management).
// Same run as the expert view; nothing is recomputed. Bad news is never hidden.
import { esc } from "../api.js";
import { citeChip, renderPathDetails } from "./report.js";
import { annotate } from "../glossary.js";

const STATUS_PLAIN = {
  provisional_assessment: ["First assessment", "A starting point to confirm in an AFS lab trial."],
  insufficient_information: ["More information needed", "The facts given are not enough to recommend a method yet."],
  outside_supported_scope: ["Outside what the evidence supports", "The requested use goes beyond what the AFS material can back up."],
};
const CONF_PLAIN = {
  high: "High confidence: the facts given and AFS's own examples support this.",
  medium: "Medium confidence: plausible, but important facts still need confirming.",
  low: "Low confidence: key facts are missing or the request has a problem.",
  insufficient: "No confidence yet: not enough information for a recommendation.",
};
const METHOD_PLAIN = {
  NIR: "near-infrared light; the standard choice for powders, food and many liquids",
  MIR: "mid-infrared light measured through a crystal touching the sample; very specific, needs special IR fibers",
  RAMAN: "laser light scattered by molecules; works well in water-based samples, can be disturbed by fluorescence",
  UVVIS: "ultraviolet / visible light; simple and sensitive, but not very specific",
  FLUO: "light given off by fluorescent substances; very sensitive, but only for substances that fluoresce",
};
const PATH_PLAIN = {
  A: "Path A: a chemometric model that turns spectra into live values for process automation",
  B: "Path B: a customised multi-spectral system for the customer's own R&D lab",
  C: "Path C: customised low-cost spectral sensors for one specific process control",
  undecided: "Path to be decided after the lab trial",
};

function sources(stmts, base, checks) {
  const cites = stmts.flatMap((s, index) => (s.citations || []).map((c) => citeChip(c, checks[`${base}[${index}]`])));
  if (!cites.length) return "";
  return `<details class="srcs"><summary>Show sources</summary>${cites.join("")}</details>`;
}

export function renderSummary(el, run, actions) {
  const r = run.report;
  const [statusTitle, statusText] = STATUS_PLAIN[r.decision_status];
  const conf = run.confidence?.level || "low";
  const blocks = (run.rule_hits || []).filter((h) => h.severity === "block");
  const contra = (run.premises || []).filter((p) => p.verdict === "contradicted");
  const recs = r.recommendations.filter((x) => x.role !== "not_recommended");
  const notRec = r.recommendations.filter((x) => x.role === "not_recommended");
  const fp = r.feasibility_plan;
  const checks = Object.fromEntries((run.verification?.claims || []).map((check) => [check.location, check.status]));
  const steps = (fp.steps?.length ? fp.steps : [...fp.samples, ...fp.comparison]).slice(0, 4);
  const plainFor = (x) => (x.method_ids || []).map((m) => METHOD_PLAIN[m]).filter(Boolean)[0] || "";

  el.innerHTML = `
    <div class="sum">
      <div class="sum-status ${r.decision_status}">
        <div><b>${esc(statusTitle)}</b> <span class="muted">${esc(statusText)}</span></div>
        <div class="small">${esc(CONF_PLAIN[conf])}</div>
      </div>

      <div class="headline ${r.decision_status}">${annotate(r.headline)}</div>

      ${blocks.length || contra.length ? `<section class="section sum-issues"><h2>Problems found in the request</h2>
        <ul class="plain">
          ${contra.map((p) => `<li><b>“${esc(p.statement)}”</b>: not supported. ${esc(p.explanation)}</li>`).join("")}
          ${blocks.filter((b) => !contra.some((p) => p.explanation === b.text)).map((b) => `<li>${esc(b.text)}</li>`).join("")}
        </ul></section>` : ""}

      <section class="section"><h2>What to test first</h2>
        ${recs.length ? recs.map((x) => `<div class="sum-rec">
            <div><b>${esc(x.method)}</b> <span class="role ${x.role}">${esc(x.role.replace("_", " "))}</span></div>
            ${plainFor(x) ? `<div class="small muted">${esc(plainFor(x))}</div>` : ""}
            <p class="${x.rationale[0]?.kind === "sourced" ? `stmt sourced ${checks[`recommendations[${r.recommendations.indexOf(x)}].rationale[0]`] || "unchecked"}` : ""}">${x.rationale[0]?.kind === "sourced" && x.rationale[0]?.citations?.length ? `<span class="grounded-text">${annotate(x.rationale[0].text)}</span>` : annotate(x.rationale[0]?.text || "")}</p>${sources(x.rationale, `recommendations[${r.recommendations.indexOf(x)}].rationale`, checks)}</div>`).join("")
          : `<p>No method can be recommended yet. Answer the questions below first.</p>`}
        ${notRec.length ? `<p class="small"><b>Not recommended:</b> ${notRec.map((x) => `${esc(x.method)} (${esc(x.rationale[0]?.text || "")})`).join("; ")}</p>` : ""}
      </section>

      <div class="two-col">
        <section class="section"><h2>Ask the customer</h2>
          <ol class="steps">${r.clarification_questions.slice(0, 3).map((q) => `<li>${esc(q.question)}</li>`).join("")}</ol>
        </section>
        <section class="section"><h2>First experiment</h2>
          <ol class="steps">${steps.map((s) => `<li>${esc(s)}</li>`).join("")}</ol>
        </section>
      </div>

      <section class="section"><h2>Next step with AFS</h2>
        <p>${esc(r.pathway.next_step)}</p>
        <p class="small muted">${esc(PATH_PLAIN[r.pathway.likely_path] || "")}</p>
        ${renderPathDetails(run)}
      </section>

      <div class="row">
        <button class="btn" id="toExpert">Open the expert view</button>
        <a class="btn" href="/api/runs/${run.id}/export.md" download>Download Markdown</a>
      </div>
    </div>`;
  el.querySelector("#toExpert").onclick = () => actions.setView("expert");
}
