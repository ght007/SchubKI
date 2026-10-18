// "Is this what you mean?" dialog: step 1 of a run.
// Shows what the assistant read (each reading can be marked wrong), glossary translations, the AFS paths,
// early warnings and ONE de-duplicated list of open questions. Everything is optional: the user can assess
// with the answers given or leave questions unanswered. The customer's text is never rewritten.
// The dialog lives outside the tab content so page updates do not interrupt review or typing.
import { esc } from "../api.js";
import * as store from "../state.js";

let el = null;
let actions = null;
let reading = null;
let view = null;

export function focusReadingReview() {
  const dialog = document.getElementById("reading-review");
  if (!dialog?.querySelector("#reading-confirm-title")) return;
  if (!dialog.open) dialog.showModal();
  dialog.querySelector("#reading-confirm-title").focus({ preventScroll: true });
}

export function renderConfirm(container, s, acts) {
  el = container;
  actions = acts;
  el.oncancel = (event) => {
    event.preventDefault();
    actions.closeConfirm();
  };
  if (!s.understand || s.busy || s.reading || s.tab !== "reading") {
    if (el.open) el.close();
    if (!s.understand) {
      reading = null;
      el.replaceChildren();
    }
    return;
  }
  if (reading !== s.understand || view !== s.view) {
    if (reading !== s.understand) el.replaceChildren();
    draw();
    reading = s.understand;
    view = s.view;
  }
  el.querySelector("#cf-go").disabled = s.savingQuery;
  if (!el.open) focusReadingReview();
}

function draw() {
  const s = store.get();
  const u = s.understand;
  if (!u) return;
  const body = el.querySelector(".cf-dialog-body");
  const scrollTop = body?.scrollTop || 0;
  const focused = el.contains(document.activeElement) ? document.activeElement : null;
  const disclosures = new Map([...el.querySelectorAll("details[id]")].map((node) => [node.id, node.open]));
  const general = s.view === "general";
  const answered = u.questions.filter((q) => (s.answers[q.key] || "").trim()).length;
  const isMain = (q) => q.impact === "high" || (q.path && q.impact === "medium");
  const main = u.questions.filter(isMain);
  const more = u.questions.filter((q) => !isMain(q));
  const pathLine = [...u.paths.chosen.map((p) => [p, "chosen"]), ...u.paths.detected.map((p) => [p, "found in the enquiry"])];

  el.innerHTML = `<header class="cf-dialog-header">
    <div>
      <h2 id="reading-confirm-title" tabindex="-1"><span class="cf-next-step">Review and confirm</span>Is this what you mean?</h2>
      <p id="reading-confirm-description">Check the reading, mark anything that is wrong, and answer what you can. All follow-up questions are optional.</p>
    </div>
    <button type="button" class="cf-close" id="cf-back" aria-label="Close review and edit enquiry" title="Edit enquiry">×</button>
  </header>
  <div class="cf-dialog-body">
    <p class="small muted cf-reader">Read by ${esc(u.read_by)} · the customer's text is not changed</p>

    ${u.warnings.length ? `<div class="pc-warn" style="margin-top:.8rem">${u.warnings.map((w) =>
      `<p><b>${esc(w.title)}.</b> ${esc(w.text)} <span class="small">[${esc(w.sources.join(", "))}]</span></p>`).join("")}</div>` : ""}

    <div class="cf-block"><h3>We understood</h3>
      ${u.summary ? `<p class="cf-summary">${esc(u.summary)}</p>` : ""}
      <ul class="plain readings">${u.readings.map((r) => {
        const wrong = s.rejected.includes(r.field);
        return `<li class="${wrong ? "wrong" : ""}"><span class="lbl">${esc(r.label)}</span><span class="val">${esc(r.value)}</span>
          <span class="seg mini"><button data-ok="${esc(r.field)}" aria-pressed="${!wrong}" aria-label="${esc(r.label)}: correct" title="Correct">✓</button>
          <button data-bad="${esc(r.field)}" aria-pressed="${wrong}" aria-label="${esc(r.label)}: treat as unknown" title="Wrong: treat as unknown">✗</button></span></li>`;
      }).join("") || `<li class="muted small">Nothing specific could be read from the text yet.</li>`}</ul>
      ${u.terms.length ? `<div class="chips" style="margin-top:.5rem">${u.terms.map((t) =>
        `<span class="chip">${esc(t.matched)} → ${esc(t.term)}</span>`).join("")}</div>` : ""}
      ${u.premises.length ? `<p class="small" style="margin:.6rem 0 .2rem"><b>Customer claims we will check against the AFS sources</b></p>
        <ul class="small">${u.premises.map((p) => `<li>${esc(p)}</li>`).join("")}</ul>` : ""}
      ${!general && u.facts.length ? `<details id="cf-facts" class="small" style="margin-top:.5rem"><summary>What the customer said, fact by fact (${u.facts.length})</summary>
        <ul>${u.facts.map((f) => `<li><b>${esc(f.field)}</b>: ${esc(f.value)} <span class="muted">(${esc(f.status)})</span></li>`).join("")}</ul></details>` : ""}
    </div>

    <div class="cf-block"><h3>AFS path</h3>
      ${pathLine.length ? `<ul class="plain small">${pathLine.map(([p, how]) =>
        `<li><b>${p} · ${esc(u.paths.titles[p])}</b> <span class="muted">(${how})</span></li>`).join("")}</ul>`
        : `<p class="small muted">None chosen or found: the assistant will suggest one. Close this review to choose a path in Customer Enquiry.</p>`}
    </div>

    <div class="cf-block"><div class="row between"><h3 id="reading-questions">Follow-up questions</h3>
      <span class="small muted">${answered} of ${u.questions.length} answered · ${u.completeness} of ${u.total} key facts in the text</span></div>
      ${main.map(question).join("")}
      ${more.length ? `<details id="cf-more" ${general ? "" : "open"}><summary class="small">More questions (${more.length})</summary>${more.map(question).join("")}</details>` : ""}
      ${!u.questions.length ? `<p class="small muted">No open questions.</p>` : ""}
    </div>

  </div>
    <footer class="cf-actions" aria-label="Assessment actions">
      <div class="cf-action-buttons">
        <button type="button" class="btn primary" id="cf-go">Yes, assess</button>
      </div>
    </footer>`;

  el.querySelectorAll("[data-ok]").forEach((b) => (b.onclick = () => { store.get().rejected = s.rejected.filter((f) => f !== b.dataset.ok); draw(); }));
  el.querySelectorAll("[data-bad]").forEach((b) => (b.onclick = () => {
    if (!s.rejected.includes(b.dataset.bad)) store.get().rejected = [...s.rejected, b.dataset.bad];
    draw();
  }));
  el.querySelectorAll("[data-q]").forEach((b) => (b.onclick = () => {
    const a = store.get().answers;
    a[b.dataset.q] = a[b.dataset.q] === b.dataset.opt ? "" : b.dataset.opt;
    u.prefilled = u.prefilled.filter((k) => k !== b.dataset.q);
    draw();
  }));
  el.querySelectorAll("[data-t]").forEach((inp) => (inp.oninput = () => { store.get().answers[inp.dataset.t] = inp.value; }));
  el.querySelector("#cf-back").onclick = () => actions.closeConfirm();
  el.querySelector("#cf-go").onclick = () => actions.confirmRun();
  el.querySelectorAll("details[id]").forEach((node) => {
    if (disclosures.has(node.id)) node.open = disclosures.get(node.id);
  });
  if (el.open && focused) {
    const target = [...el.querySelectorAll("button, input, summary")].find((node) =>
      focused.id ? node.id === focused.id : Object.keys(focused.dataset).length &&
        node.tagName === focused.tagName && Object.entries(focused.dataset).every(([key, value]) => node.dataset[key] === value));
    target?.focus({ preventScroll: true });
  }
  el.querySelector(".cf-dialog-body").scrollTop = scrollTop;
}

function question(q) {
  const s = store.get();
  const v = s.answers[q.key] || "";
  const pre = s.understand.prefilled.includes(q.key) && v === q.prefill;
  const tag = q.path ? `<span class="tag">Path ${q.path}</span>` : "";
  const id = `review-question-${s.understand.questions.indexOf(q)}`;
  return `<div class="pc-q">
    <div class="small" id="${id}"><b>${esc(q.text)}</b> ${tag} <span class="muted">${esc(q.impact)} impact</span>
      ${pre ? `<span class="tag fromtext">from your text</span>` : ""}</div>
    <div class="small muted" id="${id}-why">${esc(q.why)}</div>
    ${q.kind === "choice"
      ? `<div class="opts" role="group" aria-labelledby="${id}">${q.options.map((o) => `<button class="opt" data-q="${esc(q.key)}" data-opt="${esc(o)}" aria-pressed="${v === o}">${esc(o)}</button>`).join("")}</div>`
      : `<input type="text" data-t="${esc(q.key)}" aria-labelledby="${id}" aria-describedby="${id}-why" value="${esc(v)}" placeholder="Answer if known (optional)">`}
  </div>`;
}
