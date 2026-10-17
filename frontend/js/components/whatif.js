// "What would change my mind": decision tree of high-impact questions + before/after diff.
import { esc } from "../api.js";

export function renderWhatIf(el, s, actions) {
  const run = s.run;
  const qs = run.report?.clarification_questions || [];
  const diff = run.diff || [];
  el.innerHTML = `
    ${diff.length ? `<section class="section"><h2>What changed <small>after the last answers</small></h2>
      <div class="diff">${diff.map((d) => `<div class="f">${esc(d.field)}</div><div class="b">${esc(d.before)}</div><div>→</div><div class="a">${esc(d.after)}</div>`).join("")}</div>
      ${Object.keys(run.answers || {}).length ? `<p class="small muted" style="margin-top:.8rem">Answers used: ${Object.entries(run.answers).map(([k, v]) => `${esc(k)}: ${esc(v)}`).join("; ")}</p>` : ""}
    </section>` : run.parent_run_id ? `<section class="section"><p>The answers did not change the status, confidence or method ranking.</p></section>` : ""}
    <section class="section"><h2>What would change the recommendation</h2>
      <p class="muted">Each question is listed with what its answer would decide. Type what the client answered and re-run: the assessment is redone with your answers as stated facts.</p>
      <ul class="tree">${qs.map((q, i) => `<li><b>${esc(q.question)}</b> <span class="impact ${q.impact}">${q.impact}</span>
        <div class="small muted">Decides: ${esc(q.why)}</div>
        <input type="text" data-q="${i}" value="${esc(s.answers[q.question] || "")}" placeholder="Client's answer"></li>`).join("")}</ul>
      <div class="row"><button class="btn primary" id="wi" ${s.busy ? "disabled" : ""}>Re-run with these answers</button></div>
    </section>`;
  el.querySelectorAll("[data-q]").forEach((inp) => (inp.oninput = () => actions.setAnswer(qs[+inp.dataset.q].question, inp.value)));
  el.querySelector("#wi").onclick = () => actions.whatif();
}
