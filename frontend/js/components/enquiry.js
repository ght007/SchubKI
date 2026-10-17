// Enquiry box, mode toggle, stage progress.
import { esc } from "../api.js";
import { runPrecheck, schedulePrecheck } from "./precheck.js";
import { renderPathPicker } from "./pathq.js";

export function renderEnquiry(el, s, actions) {
  const groups = {};
  for (const e of s.examples) (groups[e.group] ||= []).push(e);
  const current = el.querySelector("textarea")?.value || s.run?.enquiry || "";
  el.innerHTML = `
    <h2>Customer enquiry</h2>
    ${s.view === "expert" ? `<div class="row" style="margin-bottom:.5rem">
      <label class="small muted" for="example">Load a scenario</label>
      <select id="example" style="flex:1;min-width:0">
        <option value="">Choose…</option>
        ${Object.entries(groups).map(([g, items]) => `<optgroup label="${esc(g)}">${items.map((e) =>
          `<option value="${esc(e.id)}">${esc(e.id)}: ${esc(e.title)}</option>`).join("")}</optgroup>`).join("")}
      </select>
    </div>` : ""}
    <textarea class="enq" id="enq" placeholder="Paste or type what the customer said. Only what they said: the assistant treats everything else as unknown.">${esc(current)}</textarea>
    <div id="pathpick" style="margin-top:.6rem"></div>
    <div class="row between" style="margin-top:.6rem">
      <div class="seg" role="group" aria-label="Mode">
        <button data-mode="fast" aria-pressed="${s.mode === "fast"}" title="One model, about 10-20 s">Fast</button>
        <button data-mode="council" aria-pressed="${s.mode === "council"}" title="Several models draft, judge each other blind; slower">Council</button>
      </div>
      <button class="btn primary" id="go" ${s.busy || s.reading ? "disabled" : ""}>${s.reading ? "Reading…" : s.busy ? "Assessing…" : s.confirm ? "Check and assess" : "Assess enquiry"}</button>
    </div>
    ${s.stages.length && (s.view === "expert" || s.busy) ? `<ul class="stage-log">${s.stages.filter((x) => x.status === "done").map((x) =>
      `<li><b>${esc(x.stage)}</b> ${esc(x.detail || "")} <span class="muted">${x.ms ?? ""} ms</span></li>`).join("")}
      ${s.details.slice(-3).map((d) => `<li class="muted">${esc(d)}</li>`).join("")}</ul>` : ""}
    ${s.error ? `<div class="err">${esc(s.error)}</div>` : ""}`;

  const pc = document.getElementById("precheck");
  renderPathPicker(el.querySelector("#pathpick"), s, actions);
  const ex = el.querySelector("#example");
  if (ex) ex.onchange = (ev) => {
    const item = s.examples.find((e) => e.id === ev.target.value);
    if (item) { el.querySelector("#enq").value = item.enquiry; runPrecheck(item.enquiry, pc); }
  };
  el.querySelector("#enq").oninput = (ev) => schedulePrecheck(ev.target.value, pc);
  el.querySelectorAll("[data-mode]").forEach((b) => (b.onclick = () => actions.setMode(b.dataset.mode)));
  el.querySelector("#go").onclick = () => actions.assess(el.querySelector("#enq").value);
}