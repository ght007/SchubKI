// AFS path picker with full names (multi-select). The questions for chosen or detected paths are asked on the
// "Is this what you mean?" dialog (confirm.js), merged with the other open questions.
// Renders into its own container, so typing elsewhere never loses focus.
import { esc, getJSON } from "../api.js";
import * as store from "../state.js";

const FALLBACK = {
  A: { title: "Chemometric model for process automation", questions: [], note_key: "Path A - Note" },
  B: { title: "Multi-spectral system for your R&D lab", questions: [], note_key: "Path B - Note" },
  C: { title: "Low-cost spectral sensor(s)", questions: [], note_key: "Path C - Note" },
};
let defs = FALLBACK;
let detected = [];          // paths the pre-check found in the customer's text
let el = null;
let actions = null;

export async function loadPathQuestions() {
  try { defs = await getJSON("/api/paths"); } catch (_) { /* keep fallback names */ }
  if (el?.isConnected) draw();
}

export function setDetected(paths) {
  const next = (paths || []).slice().sort();
  if (JSON.stringify(next) === JSON.stringify(detected)) return;
  detected = next;
  if (el?.isConnected) draw();
}

/** Path answers for paths that are neither chosen nor detected are dropped before a run. */
export function activePathAnswers(answers) {
  const active = new Set([...store.get().paths, ...detected]);
  return Object.fromEntries(Object.entries(answers).filter(([k]) => {
    const m = k.match(/^Path ([ABC]) - /);
    return !m || active.has(m[1]);
  }));
}

export function renderPathPicker(container, s, acts) {
  el = container;
  actions = acts;
  draw();
}

function draw() {
  const s = store.get();
  const chosen = s.paths;
  const shown = [...new Set([...chosen, ...detected])].sort();
  el.innerHTML = `
    <div class="pathpick" role="group" aria-label="Preferred AFS path">
      <div class="row between"><span class="small"><b>Preferred AFS path</b> <span class="muted">optional, several allowed</span></span>
        <span class="small muted">${chosen.length ? "" : "Auto: the assistant suggests one"}</span></div>
      ${["A", "B", "C"].map((p) => `<button type="button" class="pathopt" data-path="${p}" aria-pressed="${chosen.includes(p)}" ${s.busy || s.reading ? "disabled" : ""}>
          <span class="pl">${p}</span><span>${esc(defs[p]?.title || FALLBACK[p].title)}</span>
          ${detected.includes(p) && !chosen.includes(p) ? `<span class="tag">in the enquiry</span>` : ""}</button>`).join("")}
      ${shown.length ? `<span class="small muted">Choose Check and assess to open the review dialog with questions for ${shown.length > 1 ? "these paths" : "this path"}.</span>` : ""}
    </div>`;

  el.querySelectorAll("[data-path]").forEach((b) => (b.onclick = () => actions.togglePath(b.dataset.path)));
}
