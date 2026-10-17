// A distinct page header with live timing and links into the rendered content.
import { esc } from "../api.js";
import { STEPS, activeStep, latestStageEvent, stepStatus } from "../pipeline-steps.js";

const formatTime = (ms) => ms < 1000 ? `${ms} ms` : `${(ms / 1000).toFixed(1)} s`;

function contents(content, tab) {
  if (tab === "reading") return [
    ["Customer enquiry", "enq"],
    ["Load a scenario", "example"],
    ["Preferred AFS path", "pathpick"],
    ["Assessment mode", "mode-label"],
    ["LLM model", "model-choice"],
    ["Review the reading", "reading-confirm-title"],
    ["Follow-up questions", "reading-questions"],
    ["Path follow-up questions", "path-questions"],
  ].filter(([, id]) => content.querySelector(`#${id}`));

  const headings = [...content.querySelectorAll("h2, h3, summary")].filter((node) => {
    if (node.tagName === "SUMMARY" && node.parentElement.classList.contains("srcs")) return false;
    if (node.tagName === "H3" && (tab !== "coach" || !node.textContent.includes("Improved enquiry"))) return false;
    return node.tagName === "SUMMARY" || !node.closest("details");
  });
  return headings.map((node, index) => {
    const small = node.querySelector("small")?.textContent || "";
    const label = node.textContent.replace(small, "").trim();
    node.id ||= `section-${tab}-${index}`;
    return [label, node.id];
  });
}

function stageTime(s, run, id) {
  const timings = run?.timings_ms || {};
  const direct = timings[id] ?? (id === "report" ? timings.council : undefined);
  if (direct != null) return direct;
  const event = [...s.stages].reverse().find((item) =>
    (item.stage === id || (id === "report" && item.stage === "council")) && item.status === "done");
  return event?.ms;
}

export function renderPageHeader(view, content, s, step, run) {
  const status = stepStatus(s, step.id);
  const current = activeStep(s);
  const stageTimes = step.stages.map((id) => stageTime(s, run, id)).filter((ms) => Number.isFinite(ms));
  const runtime = stageTimes.reduce((sum, ms) => sum + ms, 0);
  const total = run?.timings_ms?.total;
  const event = latestStageEvent(s, step.id);
  const detail = [...s.details].reverse().find((item) =>
    step.stages.includes(item.stage === "council" ? "report" : item.stage) &&
    (step.id !== "loading" || item.stage === event?.stage));
  const detailParts = [event?.detail?.replaceAll("_", " "), detail?.detail,
    s.busy && current && current !== step.id ? `Current stage: ${STEPS.find((item) => item.id === current)?.label || current}` : ""]
    .filter(Boolean);
  const links = contents(content, step.id);
  const header = document.createElement("header");
  header.className = "page-header";
  header.style.setProperty("--page-accent", step.color);
  header.innerHTML = `<div class="page-header-main">
    <div class="page-header-copy"><h1 id="page-title-${step.id}">${esc(step.label)}</h1><p>${esc(step.description)}</p></div>
    <div class="page-runtime" aria-label="Runtime statistics">
      <span class="page-stat">${stageTimes.length ? `${status === "active" ? "Runtime so far" : "Page runtime"}: <b>${formatTime(runtime)}</b>` :
        s.busy || (s.reading && current === step.id) ? "Running…" : "Runtime: awaiting assessment"}</span>
      ${Number.isFinite(total) ? `<span class="page-stat">Full run: <b>${formatTime(total)}</b></span>` : ""}
    </div>
  </div>
  ${detailParts.length ? `<p class="page-detail">${detailParts.map(esc).join(" · ")}</p>` : ""}
  <nav class="page-toc" aria-label="Contents of ${esc(step.label)}">
    <span class="page-toc-label">On this page</span>
    <div class="page-toc-links">${links.map(([label, id]) => `<a href="#${id}">${esc(label)}</a>`).join("")}</div>
  </nav>`;
  view.prepend(header);
  header.querySelectorAll(".page-toc a").forEach((link) => link.addEventListener("click", (event) => {
    event.preventDefault(); // keep #run=<id> deep links when jumping within a page
    const target = document.getElementById(link.hash.slice(1));
    if (!target) return;
    let disclosure = target.closest("details");
    while (disclosure) {
      disclosure.open = true;
      disclosure = disclosure.parentElement?.closest("details");
    }
    target.scrollIntoView({ behavior: "smooth", block: "start" });
  }));
}
