// The Read step owns the customer enquiry and its UI-only model preference.
import { esc } from "../api.js";
import { runPrecheck, schedulePrecheck } from "./precheck.js";
import { renderPathPicker } from "./pathq.js";

export function renderEnquiry(el, s, actions) {
  const groups = {};
  for (const example of s.examples) (groups[example.group] ||= []).push(example);
  const enquiry = s.draftEnquiry ?? s.run?.enquiry ?? "";
  const locked = s.busy || s.reading || !!s.understand;
  const configured = s.health?.models || {};
  const models = [...new Set([configured.fast, configured.main, ...(configured.council || []), s.modelChoice]
    .filter((model) => model && model !== "auto"))];

  el.innerHTML = `<section class="panel enquiry-stage">
    <h2>Customer enquiry</h2>
    <label class="enquiry-label" for="enq">What did the customer ask for?</label>
    <textarea class="enq" id="enq" ${locked ? "disabled" : ""} placeholder="Paste or type what the customer said. Only what they said: the assistant treats everything else as unknown.">${esc(enquiry)}</textarea>

    <div class="scenario-picker">
      <label for="example">…or load a scenario</label>
      <select id="example" ${locked ? "disabled" : ""}>
        <option value="">Choose a scenario…</option>
        ${Object.entries(groups).map(([group, items]) => `<optgroup label="${esc(group)}">${items.map((example) =>
          `<option value="${esc(example.id)}" ${s.selectedExample === example.id ? "selected" : ""}>${esc(example.id)}: ${esc(example.title)}</option>`).join("")}</optgroup>`).join("")}
      </select>
    </div>
    <div id="pathpick" class="enquiry-paths"></div>

    <div class="enquiry-options">
      <div class="enquiry-option">
        <span class="enquiry-option-label" id="mode-label">Assessment mode</span>
        <div class="seg" role="group" aria-labelledby="mode-label">
          <button type="button" data-mode="fast" aria-pressed="${s.mode === "fast"}" ${s.busy || s.reading ? "disabled" : ""} title="One model, about 10-20 s">Fast</button>
          <button type="button" data-mode="council" aria-pressed="${s.mode === "council"}" ${s.busy || s.reading ? "disabled" : ""} title="Several models draft and judge each other; slower">Council</button>
        </div>
        <p class="small muted mode-explanation" aria-live="polite">${s.mode === "fast"
          ? "Fast uses one LLM to draft the assessment when connected. Rules and verification still run."
          : "Council uses multiple LLMs to draft and cross-check assessments when connected. It takes longer."}</p>
      </div>
      <div class="enquiry-option">
        <label class="enquiry-option-label" for="model-choice">LLM model</label>
        <select id="model-choice">
          <option value="auto" ${s.modelChoice === "auto" ? "selected" : ""}>Server default</option>
          ${models.map((model) => `<option value="${esc(model)}" ${s.modelChoice === model ? "selected" : ""}>${esc(model)}</option>`).join("")}
        </select>
      </div>
    </div>
    <p class="small muted model-note">Model choice is saved in this browser. The server still uses its configured model.</p>
    <label class="small confirm-choice"><input type="checkbox" id="confirm-choice" ${s.confirm ? "checked" : ""} ${s.busy || s.reading ? "disabled" : ""}> Review the reading and follow-up questions before assessing</label>
    <div class="enquiry-actions"><button type="button" class="btn primary" id="go" ${locked ? "disabled" : ""}>${s.reading ? "Reading…" : s.busy ? "Assessing…" : s.confirm ? "Check and assess" : "Assess enquiry"}</button></div>
    ${s.error ? `<div class="err">${esc(s.error)}</div>` : ""}
  </section>
  <section id="precheck" class="panel precheck reading-support" hidden aria-live="polite"></section>
  <div id="reading-confirm" class="reading-support">${s.reading ? '<section class="section"><h2 id="reading-confirm-title">Reading your enquiry…</h2><p>Preparing the reading and follow-up questions.</p></section>' : ""}</div>`;

  renderPathPicker(el.querySelector("#pathpick"), s, actions);
  const precheck = el.querySelector("#precheck");
  if (!s.understand && !s.busy && !s.reading) runPrecheck(enquiry, precheck);
  const textarea = el.querySelector("#enq");
  textarea.oninput = () => {
    actions.setDraftEnquiry(textarea.value);
    el.querySelector("#example").value = "";
    schedulePrecheck(textarea.value, precheck);
  };
  el.querySelector("#example").onchange = (event) => {
    const example = s.examples.find((item) => item.id === event.target.value);
    if (example) {
      textarea.value = example.enquiry;
      actions.setExample(example.id, example.enquiry);
      runPrecheck(example.enquiry, precheck);
      textarea.focus();
    }
  };
  el.querySelectorAll("[data-mode]").forEach((button) =>
    (button.onclick = () => actions.setMode(button.dataset.mode)));
  el.querySelector("#model-choice").onchange = (event) => actions.setModelChoice(event.target.value);
  el.querySelector("#confirm-choice").onchange = (event) => actions.setConfirm(event.target.checked);
  el.querySelector("#go").onclick = () => actions.assess(textarea.value);
}
