// Report sections with typed, clickable claims.
import { esc } from "../api.js";
import { annotate } from "../glossary.js";

const KIND = { client_fact: "client fact", sourced: "sourced", assumption: "assumption", proposal: "proposal" };
const PATHS = {
  A: ["Path A", "Chemometric model for process automation"],
  B: ["Path B", "Customized multi-spectral system for R&D"],
  C: ["Path C", "Customized spectral IoT sensors"],
};

function checksByLocation(run) {
  const m = {};
  for (const c of run.verification?.claims || []) m[c.location] = c.status;
  return m;
}

export function citeChip(c, status) {
  const st = status || "unchecked";
  return `<button type="button" class="cite ${st}" data-src="${esc(c.source)}" data-page="${c.page}" data-quote="${esc(c.quote)}" data-status="${st}"
    title="${esc(c.quote)} (${st})" aria-label="Open highlighted source ${esc(c.source)} page ${c.page}"><span class="v"></span>${esc(c.source)} p.${c.page}</button>`;
}

function stmt(s, loc, checks) {
  const st = checks[loc];
  const grounded = s.kind === "sourced" && (s.citations || []).length;
  return `<div class="stmt ${s.kind} ${esc(st || "unchecked")}">${grounded ? `<span class="grounded-text">${annotate(s.text)}</span>` : annotate(s.text)}${(s.citations || []).map((c) => citeChip(c, st)).join("")}<span class="kind">${KIND[s.kind] || s.kind}</span></div>`;
}

export function renderReport(el, run) {
  const r = run.report;
  const checks = checksByLocation(run);
  const fp = r.feasibility_plan;
  el.innerHTML = `
    ${run.id ? `<div class="toolbar">
      <a class="btn" href="/api/runs/${run.id}/export.md" download>Download Markdown</a>
    </div>` : ""}
    <div class="headline ${r.decision_status}">${annotate(r.headline)}</div>

    ${run.premises?.length ? `<section class="section"><h2>Premise check <small>the client's own claims, tested first</small></h2>
      ${run.premises.map((p) => `<div class="premise"><div class="verdict ${p.verdict}">${esc(p.verdict.replace("_", " "))}</div>
        <div><q>${esc(p.statement)}</q><p>${esc(p.explanation)}${(p.citations || []).map((c) => citeChip(c)).join("")}</p></div></div>`).join("")}
    </section>` : ""}

    <section class="section"><h2>Requirements</h2>
      <div class="two-col">
        <div><h3 style="margin-top:0">Stated by the client</h3><ul class="plain">${r.requirements_stated.map((x) => `<li>${esc(x)}</li>`).join("") || "<li class='muted'>none</li>"}</ul></div>
        <div><h3 style="margin-top:0">Key unknowns</h3><ul class="plain">${r.key_unknowns.map((x) => `<li>${esc(x)}</li>`).join("") || "<li class='muted'>none</li>"}</ul></div>
      </div>
      ${r.assumptions?.length ? `<h3>Assumptions made</h3><ul class="plain">${r.assumptions.map((x) => `<li>${esc(x)}</li>`).join("")}</ul>` : ""}
    </section>

    <section class="section"><h2>Clarification questions <small>highest impact first</small></h2>
      ${r.clarification_questions.map((q) => `<div class="q"><span class="impact ${q.impact}">${q.impact}</span><div>${esc(q.question)}</div><div class="why">${esc(q.why)}</div></div>`).join("")}
    </section>

    <section class="section"><h2>Recommendation</h2>
      <div class="legend"><span class="l-client">client fact</span><span class="l-sourced">sourced (click to see the page)</span><span class="l-assume">assumption</span><span class="l-proposal">proposal</span></div>
      ${r.recommendations.map((x, i) => `<div class="rec"><div class="rec-head"><b>${esc(x.method)}</b><span class="role ${x.role}">${esc(x.role.replace("_", " "))}</span></div>
        ${x.rationale.map((s, j) => stmt(s, `recommendations[${i}].rationale[${j}]`, checks)).join("")}
        ${x.conditions ? `<div class="cond">Applies if: ${esc(x.conditions)}</div>` : ""}</div>`).join("") || "<p class='muted'>No method can be recommended on the current facts.</p>"}
    </section>

    <div class="two-col">
      <section class="section"><h2>Measurement concept</h2>${r.measurement_concept.map((s, j) => stmt(s, `measurement_concept[${j}]`, checks)).join("")}</section>
      <section class="section"><h2>Spectral range</h2>${r.spectral_range.map((s, j) => stmt(s, `spectral_range[${j}]`, checks)).join("") || "<p class='muted'>Not determined yet.</p>"}</section>
    </div>

    <section class="section"><h2>Risks and uncertainty</h2>${r.risks.map((s, j) => stmt(s, `risks[${j}]`, checks)).join("")}</section>

    <section class="section"><h2>First feasibility experiment</h2>
      <div class="plan-grid">
        ${[["Samples", fp.samples], ["Reference measurements", fp.reference], ["Comparison", fp.comparison], ["Decision basis", fp.decision_basis]]
          .map(([t, items]) => `<div><h3>${t}</h3><ul class="plain">${items.map((x) => `<li>${esc(x)}</li>`).join("")}</ul></div>`).join("")}
      </div>
      ${fp.steps?.length ? `<h3>Steps</h3><ol class="steps">${fp.steps.map((x) => `<li>${esc(x)}</li>`).join("")}</ol>` : ""}
    </section>

    <section class="section"><h2>AFS pathway</h2>
      <p>${esc(r.pathway.next_step)}${r.pathway.why ? ` <span class="muted">${esc(r.pathway.why)}</span>` : ""}</p>
      <div class="paths">${Object.entries(PATHS).map(([k, [t, d]]) => {
        const req = (run.paths?.requested || []).find((f) => f.path === k);
        return `<div class="path ${r.pathway.likely_path === k ? "on" : ""}"><b>${t}</b>${d}
          ${r.pathway.likely_path === k ? `<span class="fit suggested">suggested</span>` : ""}
          ${req ? `<span class="fit ${req.verdict}">${req.requested_by === "enquiry" ? "asked by customer" : req.requested_by === "both" ? "asked by customer and expert" : "chosen by expert"}: ${req.verdict}</span>` : ""}</div>`;
      }).join("")}</div>
      ${r.pathway.likely_path === "undecided" ? `<p class="small muted" style="margin-top:.5rem">Path not chosen yet: it is decided after the lab trial.</p>` : ""}
      ${renderPathDetails(run)}
    </section>`;
}

export function renderPathDetails(run) {
  const a = run.paths;
  if (!a) return "";
  const src = (list) => (list || []).map((s) => `${s.source} p.${s.page}`).join(", ");
  return `
    ${a.reasons?.length ? `<p class="small" style="margin-top:.6rem"><b>Why this path:</b> ${esc(a.reasons.join(" "))}${a.sources?.length ? ` <span class="muted">[${esc(src(a.sources))}]</span>` : ""}</p>` : ""}
    ${(a.requested || []).map((f) => `<p class="small"><b>Path ${f.path}, ${esc(f.verdict)}:</b> ${esc(f.reason)} <span class="muted">[${esc(src(f.sources))}]</span></p>`).join("")}
    ${(a.proceed_anyway || []).map((p) => `<details class="proceed"><summary><b>If you proceed anyway with Path ${p.path}</b></summary>
      <p class="small">${esc(p.caveat)}</p><ol class="steps">${p.steps.map((x) => `<li>${esc(x)}</li>`).join("")}</ol>
      <p class="small muted">Sources: ${esc(src(p.sources))}</p></details>`).join("")}`;
}
