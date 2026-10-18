// A sticky navigation panel to the right of each page, with live timings and section tracking.
import { esc } from "../api.js";
import { STEPS, activeStep, latestStageEvent, stepStatus } from "../pipeline-steps.js";

const formatTime = (ms) => ms < 1000 ? `${ms} ms` : `${(ms / 1000).toFixed(1)} s`;
let cleanupNavigation = () => {};

const contentsLinks = (links) => links.map(([label, id]) => `<a href="#${id}">${esc(label)}</a>`).join("");

function contents(content, tab) {
  if (tab === "reading") return [
    ["Customer enquiry", "enq"],
    ["Preferred AFS path", "pathpick"],
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

function trackContents(panel, content, tab) {
  const layout = panel.parentElement;
  const toc = panel.querySelector(".page-toc-links");
  const toggle = layout.querySelector(".page-navigation-toggle");
  const compact = window.matchMedia("(max-width: 1100px)");
  const loadingBar = document.querySelector(".fiber.running");
  let frame = 0;
  let refresh = true;
  let signature = "";
  let entries = [];
  let activeId = "";
  let jump = null;

  function update() {
    frame = 0;
    // A source drawer or Reading's query sidebar can also reduce the available width.
    const collapsed = compact.matches || layout.clientWidth < 740;
    if (collapsed !== layout.classList.contains("compact-navigation")) {
      layout.classList.toggle("compact-navigation", collapsed);
      if (collapsed) panel.setAttribute("popover", "auto");
      else {
        if (panel.matches(":popover-open")) panel.hidePopover();
        panel.removeAttribute("popover");
      }
      activeId = "";
    }
    if (refresh) {
      refresh = false;
      const links = contents(content, tab);
      const nextSignature = JSON.stringify(links);
      if (nextSignature !== signature) {
        signature = nextSignature;
        toc.innerHTML = contentsLinks(links);
        entries = [...toc.querySelectorAll("a")].map((link) => ({ link, id: link.hash.slice(1) }));
        activeId = "";
      }
    }
    const top = loadingBar?.getBoundingClientRect().height || 0;
    const offset = top + 16;
    panel.style.setProperty("--page-navigation-top", `${offset}px`);
    content.style.setProperty("--page-scroll-offset", `${offset}px`);
    // Resolve IDs again: follow-up answers can replace their own DOM without a page render.
    const visible = entries.map((entry) => {
      const target = content.querySelector(`#${entry.id}`);
      return target?.checkVisibility() ? { ...entry, top: target.getBoundingClientRect().top } : null;
    }).filter(Boolean).sort((a, b) => a.top - b.top);
    let current = visible.filter((entry) => entry.top <= offset + 1).at(-1) || visible[0];
    if (window.scrollY > 0 && window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 2) {
      current = visible.at(-1); // Short final sections cannot always reach the top of the viewport.
    }
    if (jump) {
      if (Math.abs(window.scrollY - jump.y) < 2) {
        current = visible.find((entry) => entry.id === jump.id) || current;
        jump.arrived = true;
      } else if (jump.arrived) jump = null;
    }
    for (const entry of entries) {
      if (entry.id === current?.id) entry.link.setAttribute("aria-current", "location");
      else entry.link.removeAttribute("aria-current");
    }
    if (current && current.id !== activeId && panel.checkVisibility()) {
      activeId = current.id;
      // Scroll long navigation lists internally without moving the page.
      const link = current.link.getBoundingClientRect();
      const bounds = panel.getBoundingClientRect();
      if (link.top < bounds.top + 12) panel.scrollTop -= bounds.top + 12 - link.top;
      else if (link.bottom > bounds.bottom - 12) panel.scrollTop += link.bottom - bounds.bottom + 12;
    }
  }
  function schedule() {
    if (!frame) frame = requestAnimationFrame(update);
  }
  panel.addEventListener("beforetoggle", (event) => {
    toggle.setAttribute("aria-expanded", String(event.newState === "open"));
  });
  panel.addEventListener("toggle", () => {
    activeId = "";
    schedule();
  });
  compact.addEventListener("change", schedule);
  const mutations = new MutationObserver(() => { refresh = true; schedule(); });
  mutations.observe(content, { childList: true, subtree: true });
  const sizes = new ResizeObserver(schedule);
  [layout, panel, content, loadingBar].filter(Boolean).forEach((node) => sizes.observe(node));
  window.addEventListener("scroll", schedule, { passive: true });
  window.addEventListener("resize", schedule);
  content.addEventListener("toggle", schedule, true);
  toc.addEventListener("click", (event) => {
    const link = event.target.closest("a");
    if (!link) return;
    event.preventDefault(); // Preserve #run=<id> deep links when jumping within a page.
    const target = content.querySelector(link.hash);
    if (!target) return;
    if (panel.matches(":popover-open")) panel.hidePopover();
    let disclosure = target.closest("details");
    while (disclosure) {
      disclosure.open = true;
      disclosure = disclosure.parentElement?.closest("details");
    }
    // If a jump is clamped at the page bottom, keep the chosen section accented until scrolling resumes.
    const offset = parseFloat(content.style.getPropertyValue("--page-scroll-offset"));
    jump = { id: target.id, y: Math.max(0, Math.min(document.documentElement.scrollHeight - window.innerHeight,
      window.scrollY + target.getBoundingClientRect().top - offset)), arrived: false };
    target.scrollIntoView({ behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "instant" : "smooth", block: "start" });
    schedule();
  });
  update();
  return () => {
    cancelAnimationFrame(frame);
    mutations.disconnect();
    sizes.disconnect();
    compact.removeEventListener("change", schedule);
    window.removeEventListener("scroll", schedule);
    window.removeEventListener("resize", schedule);
    content.removeEventListener("toggle", schedule, true);
  };
}

export function renderPageNavigation(content, s, step, run) {
  cleanupNavigation();
  const status = stepStatus(s, step.id);
  const current = activeStep(s);
  const stageTimes = step.stages.map((id) => stageTime(s, run, id)).filter((ms) => Number.isFinite(ms));
  const runtime = stageTimes.reduce((sum, ms) => sum + ms, 0);
  const total = run?.timings_ms?.total;
  const event = latestStageEvent(s, step.id);
  const detail = [...s.details].reverse().find((item) =>
    step.stages.includes(item.stage === "council" ? "report" : item.stage) &&
    (step.id !== "loading" || item.stage === event?.stage));
  const detailParts = s.view === "expert" && step.id === "process" ? [event?.detail?.replaceAll("_", " "), detail?.detail,
    s.busy && current && current !== step.id ? `Current stage: ${STEPS.find((item) => item.id === current)?.label || current}` : ""]
    .filter(Boolean) : [];
  const links = contents(content, step.id);
  const panel = document.createElement("aside");
  panel.id = "page-navigation";
  panel.className = "page-navigation";
  panel.setAttribute("aria-label", `${step.label} page navigation`);
  panel.style.setProperty("--page-accent", step.color);
  panel.innerHTML = `<button type="button" class="page-navigation-close" popovertarget="page-navigation" popovertargetaction="hide" aria-label="Close page navigation" autofocus>Close ×</button>
    <div class="page-navigation-copy"><h1 id="page-title-${step.id}">${esc(step.label)}</h1><p>${esc(step.description)}</p></div>
    <div class="page-runtime" aria-label="Runtime statistics">
      <span class="page-stat">${stageTimes.length ? `${status === "active" ? "Runtime so far" : "Page runtime"}: <b>${formatTime(runtime)}</b>` :
        s.busy || (s.reading && current === step.id) ? "Running…" : "Runtime: awaiting assessment"}</span>
      ${Number.isFinite(total) ? `<span class="page-stat">Full run: <b>${formatTime(total)}</b></span>` : ""}
    </div>
  ${detailParts.length ? `<p class="page-detail">${detailParts.map(esc).join(" · ")}</p>` : ""}
  <nav class="page-toc" aria-label="Contents of ${esc(step.label)}">
    <span class="page-toc-label">On this page</span>
    <div class="page-toc-links">${contentsLinks(links)}</div>
  </nav>`;
  const layout = document.createElement("div");
  layout.className = "page-layout";
  content.before(layout);
  layout.append(panel, content);
  layout.insertAdjacentHTML("beforeend", `<button type="button" class="page-navigation-toggle" popovertarget="page-navigation" aria-controls="page-navigation" aria-expanded="false">
    <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M7 5h10M7 10h10M7 15h10M2 5h1M2 10h1M2 15h1"/></svg>On this page</button>`);
  cleanupNavigation = trackContents(panel, content, step.id);
}
