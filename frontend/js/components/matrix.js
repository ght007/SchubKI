// Deterministic rule findings and method screening. Retrieval has its own stage.
import { esc } from "../api.js";

const list = (value) => Array.isArray(value) ? value : [];

export function renderMatrix(el, run = {}) {
  const hits = list(run.rule_hits);
  const methods = list(run.matrix);
  const coverage = Object.fromEntries(list(run.coverage).map((item) => [item.method_id, item]));
  const max = Math.max(4, ...methods.map((item) => Math.abs(Number(item.score) || 0)));

  el.innerHTML = `
    <section class="section"><h2>Rules that fired <small>${hits.length} of the AFS knowledge base</small></h2>
      ${hits.length ? `<ul class="plain rule-list">${hits.map((hit) => `<li>
        <span class="sev ${esc(hit.severity)}">${esc(hit.severity)}</span><b>${esc(hit.title)}</b>
        <span class="small muted">${esc(hit.rule_id)} · ${list(hit.sources).map((source) => `${esc(source.source)} p.${esc(source.page)}`).join(", ") || "no source listed"}</span>
        ${hit.text ? `<div class="small">${esc(hit.text)}</div>` : ""}
      </li>`).join("")}</ul>` : `<p class="muted">No rules fired for the extracted requirements.</p>`}
    </section>
    <section class="section"><h2>Method screening <small>scores from the rules above</small></h2>
      ${methods.length ? `<div class="table-scroll"><table class="matrix"><thead><tr><th>Method</th><th>Score</th><th></th><th>Verdict</th><th>Why</th></tr></thead><tbody>
      ${methods.map((method) => {
        const score = Number(method.score) || 0;
        const width = Math.min(50, Math.abs(score) / max * 50);
        const bar = score >= 0 ? `<i style="left:50%;width:${width}%;background:var(--core)"></i>` : `<i style="right:50%;width:${width}%;background:var(--block)"></i>`;
        const fit = coverage[method.method_id];
        const fibers = list(fit?.fibers).filter((fiber) => fiber.covers !== "none").map((fiber) => fiber.fiber_id).join(", ");
        return `<tr><td><b>${esc(method.name)}</b>${method.requested_by_client ? `<div class="small muted">requested by client</div>` : ""}
          <div class="small muted">fibers: ${esc(fibers || "none")}</div></td>
          <td>${score > 0 ? "+" : ""}${esc(score)}</td><td><div class="bar">${bar}</div></td>
          <td><span class="verdict-chip ${esc(method.verdict)}">${esc(String(method.verdict || "candidate").replaceAll("_", " "))}</span></td>
          <td><ul class="contrib">${list(method.contributions).map((contribution) => `<li>${Number(contribution.delta) > 0 ? "+" : ""}${esc(contribution.delta)} ${esc(contribution.reason)}</li>`).join("") || "<li>no rule fired</li>"}</ul>
          ${fit?.asset_check ? `<div class="err" style="margin-top:.3rem">${esc(fit.asset_check)}</div>` : ""}</td></tr>`;
      }).join("")}
      </tbody></table></div>` : `<p class="muted">No method scores were produced.</p>`}
    </section>`;
}