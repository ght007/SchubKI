// LLM calls: model, tokens, latency + retrieval internals.
import { esc } from "../api.js";

export function renderTrace(el, run) {
  const t = run.trace || [];
  const tok = t.reduce((a, x) => a + x.prompt_tokens + x.completion_tokens, 0);
  const rd = run.retrieval || {};
  el.innerHTML = `
    <section class="section"><h2>LLM calls <small>${t.length} calls · ${tok.toLocaleString()} tokens · total ${(run.timings_ms?.total / 1000 || 0).toFixed(1)} s</small></h2>
      <table class="data"><thead><tr><th>Stage</th><th>Model</th><th>Prompt</th><th>Output</th><th>Latency</th><th>Result</th></tr></thead><tbody>
      ${t.map((x) => `<tr><td>${esc(x.stage)}</td><td>${esc(x.model)}</td><td>${x.prompt_tokens}</td><td>${x.completion_tokens}</td>
        <td>${x.latency_ms} ms</td><td>${x.cached ? "cache" : x.ok ? "ok" : `<span class="res fail">fallback</span> <span class="small muted">${esc(x.error)}</span>`}</td></tr>`).join("")}
      </tbody></table>
      <p class="small muted">"fallback" means the model failed and the stage used its rule-based version, so the run still completed.</p>
    </section>
    <section class="section"><h2>Stage timings</h2>
      <table class="data"><tbody>${Object.entries(run.timings_ms || {}).map(([k, v]) => `<tr><td>${esc(k)}</td><td>${v} ms</td></tr>`).join("")}</tbody></table>
    </section>
    <section class="section"><h2>Retrieval</h2>
      <p class="small">Queries built from the extracted requirements:</p>
      <ul class="plain small">${(rd.queries || []).map((q) => `<li>${esc(q)}</li>`).join("")}</ul>
      <p class="small muted">Each query is ranked by SQLite FTS5 BM25 and by dense cosine similarity; all rankings are fused with Reciprocal Rank Fusion (k = 60), then Maximal Marginal Relevance (λ = 0.7) selects diverse passages within a ${rd.used_tokens ?? "?"}-token budget. Claims on pages cited by blocking or warning rules are pinned.</p>
    </section>`;
}
