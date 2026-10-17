// The Read step owns the customer enquiry and its UI-only model preference.
import { esc } from "../api.js";

export function renderEnquiry(el, s, actions) {
  const groups = {};
  for (const example of s.examples) (groups[example.group] ||= []).push(example);
  const enquiry = s.draftEnquiry ?? s.run?.enquiry ?? "";
  const configured = s.health?.models || {};
  const models = [...new Set([configured.fast, configured.main, ...(configured.council || []), s.modelChoice]
    .filter((model) => model && model !== "auto"))];

  el.innerHTML = `<section class="panel enquiry-stage">
    <h2>Customer enquiry</h2>
    <label class="enquiry-label" for="enq">What did the customer ask for?</label>
    <textarea class="enq" id="enq" placeholder="Paste or type what the customer said. Only what they said: the assistant treats everything else as unknown.">${esc(enquiry)}</textarea>

    <div class="scenario-picker">
      <label for="example">…or load a scenario</label>
      <select id="example">
        <option value="">Choose a scenario…</option>
        ${Object.entries(groups).map(([group, items]) => `<optgroup label="${esc(group)}">${items.map((example) =>
          `<option value="${esc(example.id)}" ${s.selectedExample === example.id ? "selected" : ""}>${esc(example.id)}: ${esc(example.title)}</option>`).join("")}</optgroup>`).join("")}
      </select>
    </div>

    <div class="enquiry-options">
      <div class="enquiry-option">
        <span class="enquiry-option-label" id="mode-label">Assessment mode</span>
        <div class="seg" role="group" aria-labelledby="mode-label">
          <button type="button" data-mode="fast" aria-pressed="${s.mode === "fast"}" title="One model, about 10-20 s">Fast</button>
          <button type="button" data-mode="council" aria-pressed="${s.mode === "council"}" title="Several models draft and judge each other; slower">Council</button>
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
    <div class="enquiry-actions"><button type="button" class="btn primary" id="go" ${s.busy ? "disabled" : ""}>${s.busy ? "Assessing…" : "Assess enquiry"}</button></div>
    ${s.error ? `<div class="err">${esc(s.error)}</div>` : ""}
  </section>`;

  const textarea = el.querySelector("#enq");
  textarea.oninput = () => {
    actions.setDraftEnquiry(textarea.value);
    el.querySelector("#example").value = "";
  };
  el.querySelector("#example").onchange = (event) => {
    const example = s.examples.find((item) => item.id === event.target.value);
    if (example) {
      textarea.value = example.enquiry;
      actions.setExample(example.id, example.enquiry);
      textarea.focus();
    }
  };
  el.querySelectorAll("[data-mode]").forEach((button) =>
    (button.onclick = () => actions.setMode(button.dataset.mode)));
  el.querySelector("#model-choice").onchange = (event) => actions.setModelChoice(event.target.value);
  el.querySelector("#go").onclick = () => actions.assess(textarea.value);
}
