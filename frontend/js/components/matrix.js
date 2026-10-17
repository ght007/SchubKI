// Method screening matrix + fired rules.
import { esc } from "../api.js";

export function renderMatrix(el, run) {
  const max = Math.max(4, ...run.matrix.map((m) => Math.abs(m.score)));
  const conf = Object.fromEntries((run.confidence?.per_method || []).map((m) => [m.method_id, m.level]));
  const cov = Object.fromEntries((run.coverage || []).map((c) => [c.method_id, c]));
  el.innerHTML = `
    <section class="section"><h2>Method screening <small>every point comes from a sourced rule</small></h2>
      <table class="matrix"><thead><tr><th>Method</th><th>Score</th><th></th><th>Verdict</th><th>Confidence</th><th>Why</th></tr></thead><tbody>
      ${run.matrix.map((m) => {
        const w = (Math.abs(m.score) / max) * 50;
        const bar = m.score >= 0 ? `<i style="left:50%;width:${w}%;background:var(--core)"></i>` : `<i style="right:50%;width:${w}%;background:var(--block)"></i>`;
        const fiberOk = (cov[m.method_id]?.fibers || []).filter((f) => f.covers !== "none").map((f) => f.fiber_id).join(", ");
        return `<tr><td><b>${esc(m.name)}</b>${m.requested_by_client ? `<div class="small muted">requested by client</div>` : ""}
          <div class="small muted">fibers: ${esc(fiberOk || "none")}</div></td>
          <td>${m.score > 0 ? "+" : ""}${m.score}</td><td><div class="bar">${bar}</div></td>
          <td><span class="verdict-chip ${m.verdict}">${esc(m.verdict.replace("_", " "))}</span></td>
          <td><span class="lvl ${conf[m.method_id] || "low"}">${esc(conf[m.method_id] || "-")}</span></td>
          <td><ul class="contrib">${m.contributions.map((c) => `<li>${c.delta > 0 ? "+" : ""}${c.delta} ${esc(c.reason)}</li>`).join("") || "<li>no rule fired</li>"}</ul>
          ${cov[m.method_id]?.asset_check ? `<div class="err" style="margin-top:.3rem">${esc(cov[m.method_id].asset_check)}</div>` : ""}</td></tr>`;
      }).join("")}
      </tbody></table>
    </section>
    <section class="section"><h2>Rules that fired <small>${run.rule_hits.length} of the AFS knowledge base</small></h2>
      <ul class="plain rule-list">${run.rule_hits.map((h) => `<li><span class="sev ${h.severity}">${h.severity}</span><b>${esc(h.title)}</b>
        <span class="small muted">${esc(h.rule_id)} · ${h.sources.map((s) => `${s.source} p.${s.page}`).join(", ")}</span>
        ${h.text ? `<div class="small">${esc(h.text)}</div>` : ""}</li>`).join("")}</ul>
    </section>
    <section class="section"><h2>Evidence retrieved <small>BM25 + dense, fused with RRF, diversified with MMR</small></h2>
      <ul class="plain rule-list">${run.evidence.map((e) => `<li><b>${esc(e.ref)}</b> <button class="cite" data-src="${esc(e.source)}" data-page="${e.page}" data-quote="${esc(e.quote || e.highlight || "")}">${esc(e.source)} p.${e.page}</button>
        <span class="small muted">${esc(e.kind)} · ${esc(e.scope || "")} · RRF ${e.score}</span><div class="small">${e.highlight ? `<mark>${esc(e.highlight)}</mark>` : `${esc(e.text.slice(0, 260))}${e.text.length > 260 ? "…" : ""}`}</div></li>`).join("")}</ul>
    </section>`;
}