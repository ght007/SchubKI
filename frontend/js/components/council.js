// Judge x draft scores, gates, agreement.
import { esc } from "../api.js";

export function renderCouncil(el, run, actions) {
  const c = run.council;
  if (!c || !c.drafts?.length) {
    el.innerHTML = `<div class="empty"><h2>Council not used for this run</h2>
      <p>In Council mode, several models (different families where available) each write a draft from the same evidence.
      Deterministic gates check grounding and honesty, then every model judges the other drafts blind, in shuffled order,
      against the jury criteria. Where the models disagree, that is reported as uncertainty.</p>
      <button class="btn primary" id="runCouncil">Re-run this enquiry in Council mode</button></div>`;
    el.querySelector("#runCouncil").onclick = () => actions.assessCouncil();
    return;
  }
  const letters = c.drafts.map((d) => d.letter);
  el.innerHTML = `
    <section class="section"><h2>Council <small>${c.drafts.length} drafts · ${c.families} model famil${c.families === 1 ? "y" : "ies"}</small></h2>
      <p>Winner: <span class="winner">draft ${esc(c.winner)}</span>${Object.keys(c.merged_from || {}).length ? ` · merged ${Object.entries(c.merged_from).map(([k, v]) => `${esc(k.replace("_", " "))} from ${esc(v)}`).join(", ")}` : ""}</p>
      <p>Agreement <b>${Math.round(c.agreement * 100)}%</b>: ${esc(c.agreement_detail)}</p>
      ${c.families < 3 ? `<p class="small muted">Fewer than three model families: agreement is weaker evidence than with fully independent models.</p>` : ""}
      <table class="data"><thead><tr><th>Draft</th><th>Model</th><th>Status</th><th>Lead</th><th>Gate failures</th><th>Mean judge score</th></tr></thead><tbody>
      ${c.drafts.map((d) => `<tr><td class="${d.letter === c.winner ? "winner" : ""}">${esc(d.letter)}</td><td>${esc(d.model)}</td>
        <td>${esc((d.status || (d.ok ? "" : "failed")).replace(/_/g, " "))}</td><td>${esc(d.lead_methods.join("+") || "-")}</td>
        <td>${esc(d.gate_failures.join(", ") || "none")}</td><td>${d.judge_total || "-"}</td></tr>`).join("")}
      </tbody></table>
      <h3>Who judged whom (blind, self-judging excluded)</h3>
      <table class="data"><thead><tr><th>Judge</th>${letters.map((l) => `<th>${l}</th>`).join("")}<th>Picked</th></tr></thead><tbody>
      ${c.judgements.map((j) => `<tr><td>${esc(j.judge)} (${esc(j.judge_model)})</td>${letters.map((l) => `<td>${j.scores[l] ?? (l === j.judge ? "self" : "-")}</td>`).join("")}<td>${esc(j.best || "-")}</td></tr>`).join("")}
      </tbody></table>
    </section>`;
}
