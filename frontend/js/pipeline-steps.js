// General has three tabs; Expert adds Process Information and Coach.
export const PIPELINE_STAGES = ["extract", "rules", "retrieve", "premise", "report", "verify", "coach"];
export const STEPS = [
  { id: "reading", short: "Reading", label: "Reading", color: "#6d28d9", description: "Enter the customer's enquiry and choose how to assess it.", stages: ["extract"] },
  { id: "process", short: "Process Information", label: "Process Information", color: "#2563eb", description: "Follow model and rule tasks, then review the complete calculation record.", stages: PIPELINE_STAGES, expertOnly: true },
  { id: "assessment", short: "Result Assessment", label: "Result Assessment", color: "#15803d", description: "Review the decision, requirements, recommended methods, and feasibility-study plan.", stages: ["report"] },
  { id: "verification", short: "Confidence & Verification", label: "Confidence and Verification", color: "#c2410c", description: "Review confidence signals, source checks, and quality metrics.", stages: ["verify"] },
  { id: "coach", short: "Coach", label: "Coach", color: "#b91c1c", description: "Fill the important gaps and re-run with customer answers.", stages: ["coach"], expertOnly: true },
];
export const LOADING_PAGE = { id: "loading", label: "Calculating your assessment", color: "#2563eb",
  description: "Follow each step as your assessment is prepared. Your results will open when it is ready.", stages: PIPELINE_STAGES };

const STEP_IDS = new Set(STEPS.map((step) => step.id));
const LEGACY_TABS = {
  extract: "reading", rules: "process", retrieve: "process", premise: "process",
  report: "assessment", verify: "verification", quality: "verification",
  whatif: "coach", council: "process", trace: "process",
  methods: "process", spectral: "process",
};

export function visibleSteps(s) { return STEPS.filter((step) => !step.expertOnly || s.view === "expert"); }
export function isStep(id) { return STEP_IDS.has(id); }
export function normalizeTab(id, view = "general") {
  const tab = LEGACY_TABS[id] || (isStep(id) ? id : "reading");
  return STEPS.find((step) => step.id === tab)?.expertOnly && view !== "expert" ? "verification" : tab;
}
export function canonicalStage(id) {
  return { extract: "reading", rules: "reading", retrieve: "reading", premise: "reading",
    report: "assessment", council: "assessment", verify: "verification", coach: "coach" }[id] || null;
}

function sourceStages(id) { return id === "loading" ? PIPELINE_STAGES : STEPS.find((step) => step.id === id)?.stages || []; }
function rawStage(id) { return id === "council" ? "report" : id; }
function stageEvent(s, id) {
  return [...(s.stages || [])].reverse().find((event) => rawStage(event.stage) === id &&
    (event.status === "start" || event.status === "done"));
}
function stageDone(s, id) {
  const event = stageEvent(s, id);
  const run = s.busy ? s.liveRun : s.run;
  return event?.status === "done" || Object.hasOwn(run?.timings_ms || {}, id) ||
    (id === "report" && Object.hasOwn(run?.timings_ms || {}, "council"));
}

export function latestStageEvent(s, id) {
  return [...(s.stages || [])].reverse().find((event) => sourceStages(id).includes(rawStage(event.stage)) &&
    (event.status === "start" || event.status === "done"));
}

export function processComplete(s) {
  return !s.busy && !!s.run?.id && !s.run.error;
}

export function canOpenStep(s, id) {
  if (!visibleSteps(s).some((step) => step.id === id)) return false;
  if (id === "process") return s.busy || !!s.run;
  return !s.busy && (id === "reading" || processComplete(s));
}

export function stepStatus(s, id) {
  if (id === "loading") return s.busy ? "active" : "pending";
  if (id === "process") return s.busy ? "active" : s.run?.error ? "error" : processComplete(s) ? "done" : "pending";
  if (id === "reading" && s.reading) return "active";
  const stages = sourceStages(id);
  if (!stages.length) return "pending";
  if (stages.every((stage) => stageDone(s, stage))) return "done";
  if (s.busy && activeStep(s) === id) return "active";
  if (!s.busy && (s.error || s.run?.error) && (s.stages.length || s.run)) {
    const firstIncomplete = visibleSteps(s).find((step) => step.id !== "process" && !step.stages.every((stage) => stageDone(s, stage)));
    if (firstIncomplete?.id === id) return "error";
  }
  return "pending";
}

export function activeStep(s) {
  if (s.busy && s.view === "expert") return "process";
  const event = [...s.stages].reverse().find((item) => item.status === "start");
  return s.busy ? normalizeTab(canonicalStage(event?.stage), s.view) : s.reading ? "reading" : null;
}

export function pipelineProgress(s) {
  if (processComplete(s)) return 100;
  const firstPending = PIPELINE_STAGES.findIndex((stage) => !stageDone(s, stage));
  const completed = firstPending === -1 ? PIPELINE_STAGES.length : firstPending;
  const steps = visibleSteps(s);
  const position = (id) => steps.findIndex((step) => step.id === id) / (steps.length - 1) * 100;
  // Extraction reaches Process Information in Expert; drafting then reaches Result Assessment.
  // The final fraction waits for the saved result and the end of the stream.
  if (completed <= 5) {
    if (s.view !== "expert") return completed / 5 * position("assessment");
    if (completed === 0) return 0;
    return position("process") + (completed - 1) / 4 * (position("assessment") - position("process"));
  }
  // Verification is General's last tab; reserve 100% for the end of the stream.
  return completed === 6 ? Math.min(position("verification"), 99) : 99;
}

export const STATUS_LABELS = { pending: "Waiting", active: "Now", done: "Done", error: "Stopped" };