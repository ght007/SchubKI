// Completeness, ranked unknowns, answer + re-run.
import { esc } from "../api.js";

export function renderCoach(el, s, actions) {
  const c = s.run?.coach;
  if (!c) {
    el.innerHTML = `<h2>Enquiry coach</h2><p class="muted small">After an assessment, this shows which facts are missing, ranked by how much each answer would change the recommendation.</p>`;
    return;
  }
  const pct = Math.round((c.completeness / c.total) * 100);
  const unknown = c.fields.filter((f) => f.status === "unknown");
  const known = c.fields.filter((f) => f.status !== "unknown");
  const template = esc(c.template || "").replace(/\[([^\]]+)\]/g, '<span class="blank">[$1]</span>');
  el.innerHTML = `
    <div class="row between"><h2 style="margin:0">Enquiry coach</h2><span class="small muted">${c.completeness} of ${c.total} facts known</span></div>
    <div class="meter" role="meter" aria-valuenow="${pct}" aria-valuemin="0" aria-valuemax="100"><div style="width:${pct}%"></div></div>
    <p class="small muted" style="margin-top:0">Answer what you know and re-run. Answers are added as client facts; nothing is filled in for you.</p>
    <ul class="coach-list">
      ${unknown.map((f) => `<li><span class="mark unknown ${f.impact}" title="${f.impact} impact"></span>
        <div><b>${esc(f.label)}</b> <span class="small muted">${f.impact} impact</span>
        <div class="small muted">${esc(f.question)}</div>
        <input type="text" data-answer="${esc(f.label)}" value="${esc(s.answers[f.label] || "")}" placeholder="Client's answer (optional)"></div></li>`).join("")}
      ${known.map((f) => `<li><span class="mark ${f.status}" title="${f.status}"></span><div>${esc(f.label)} <span class="small muted">${f.status}</span></div></li>`).join("")}
    </ul>
    <div class="row" style="margin-top:.7rem"><button class="btn" id="rerun" ${s.busy ? "disabled" : ""}>Re-run with answers</button></div>
    ${c.template ? `<h3>Improved enquiry to send the customer</h3><div class="template">${template}</div>
      <div class="row" style="margin-top:.4rem"><button class="btn link" id="copytpl">Copy template</button></div>` : ""}`;

  el.querySelectorAll("[data-answer]").forEach((inp) => (inp.oninput = () => actions.setAnswer(inp.dataset.answer, inp.value)));
  el.querySelector("#rerun").onclick = () => actions.whatif();
  const cp = el.querySelector("#copytpl");
  if (cp) cp.onclick = () => navigator.clipboard?.writeText(c.template).then(() => (cp.textContent = "Copied"));
}
