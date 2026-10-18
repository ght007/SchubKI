// LLM calls: model, tokens, latency, and stage timings.
import { esc } from "../api.js";

export function renderTrace(el, run) {
  const t = run.trace || [];
  const tok = t.reduce((a, x) => a + x.prompt_tokens + x.completion_tokens, 0);
  const total = run.timings_ms?.total;
  el.innerHTML = `
    <section class="section"><h2>LLM calls <small>${t.length} calls · ${tok.toLocaleString()} tokens${total == null ? " · running" : ` · total ${(total / 1000).toFixed(1)} s`}</small></h2>
      <table class="data"><thead><tr><th>Stage</th><th>Model</th><th>Prompt</th><th>Output</th><th>Latency</th><th>Result</th></tr></thead><tbody>
      ${t.length ? "" : '<tr><td colspan="6">Completed model calls will appear here as the pipeline runs.</td></tr>'}
      ${t.map((x) => `<tr><td>${esc(x.stage)}</td><td>${esc(x.model)}</td><td>${x.prompt_tokens}</td><td>${x.completion_tokens}</td>
        <td>${x.latency_ms} ms</td><td>${x.cached ? "cache" : x.ok ? "ok" : `<span class="res fail">fallback</span> <span class="small muted">${esc(x.error)}</span>`}</td></tr>`).join("")}
      </tbody></table>
      <p class="small muted">"fallback" means the model failed and the stage used its rule-based version, so the run still completed.</p>
    </section>
    <section class="section"><h2>Stage timings</h2>
      <table class="data"><tbody>${Object.entries(run.timings_ms || {}).map(([k, v]) => `<tr><td>${esc(k)}</td><td>${v} ms</td></tr>`).join("")}</tbody></table>
    </section>`;
}
