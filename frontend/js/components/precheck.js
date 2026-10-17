// Pre-check panel: instant keyword check of the enquiry before a run (no AI, no tokens).
// It renders itself (not through the store) so typing in the enquiry box never loses focus.
import { esc, postJSON } from "../api.js";
import * as store from "../state.js";
import { setDetected } from "./pathq.js";

let timer = null;
let lastText = "";

export function schedulePrecheck(text, el) {
  clearTimeout(timer);
  timer = setTimeout(() => runPrecheck(text, el), 450);
}

export async function runPrecheck(text, el) {
  if (text === lastText) return;
  lastText = text;
  if (!text.trim()) { el.innerHTML = ""; el.hidden = true; setDetected([]); return; }
  try {
    const res = await postJSON("/api/precheck", { enquiry: text, answers: {} });
    renderPrecheck(el, res);
    setDetected(res.paths_detected || []);
  } catch (_) { el.hidden = true; }
}

function srcLabel(s) { return s ? ` [${s.source} p.${s.page}]` : ""; }

export function renderPrecheck(el, r) {
  const s = store.get();
  const general = s.view === "general";
  el.hidden = false;
  const missing = (general ? r.missing.filter((m) => m.impact === "high") : r.missing).slice(0, general ? 3 : 6);
  el.innerHTML = `
    <div class="row between"><h2 style="margin:0">Before you run it</h2>
      <span class="small muted">${r.completeness} of ${r.total} key facts present</span></div>
    <p class="small muted" style="margin:.2rem 0 .6rem">Instant check while you type, no AI. ${s.confirm ? "The open questions are asked on the next step." : "Answers you add are sent as a separate \"added by the expert\" block; the customer's text is not changed."}</p>

    ${r.warnings.length ? `<div class="pc-warn">${r.warnings.map((w) => `<p><b>${esc(w.title)}.</b> ${esc(w.text)} <span class="small">[${esc(w.sources.join(", "))}]</span></p>`).join("")}</div>` : ""}

    ${r.terms.length ? `<div class="pc-block"><div class="small"><b>Recognised</b></div><div class="chips">${r.terms.map((t) =>
      `<span class="chip ${esc(t.category)}" title="${esc(t.definition + srcLabel(t.source))}">${esc(t.matched)}${t.matched.toLowerCase() !== t.term.toLowerCase() ? ` → ${esc(t.term)}` : ""}</span>`).join("")}</div></div>` : ""}

    ${r.vague.length ? `<div class="pc-block"><div class="small"><b>Too vague to act on</b></div>${r.vague.map((v) => `
      <div class="pc-q"><span class="chip vague">${esc(v.matched)}</span> <span class="small">${esc(v.ask)}</span>
      ${s.confirm ? "" : `<input type="text" data-pc="${esc(v.ask)}" value="${esc(s.answers[v.ask] || "")}" placeholder="Answer if known">`}</div>`).join("")}</div>` : ""}

    ${missing.length ? `<div class="pc-block"><div class="small"><b>Missing facts</b></div>${missing.map((m) => `
      <div class="pc-q"><span class="small"><b>${esc(m.label)}</b> <span class="muted">${m.impact} impact</span></span>
      ${s.confirm ? "" : `<input type="text" data-pc="${esc(m.label)}" value="${esc(s.answers[m.label] || "")}" placeholder="${esc(m.question)}">`}</div>`).join("")}</div>` : ""}`;
  el.querySelectorAll("[data-pc]").forEach((inp) => (inp.oninput = () => { store.get().answers[inp.dataset.pc] = inp.value; }));
}

export function resetPrecheck() { lastText = ""; }