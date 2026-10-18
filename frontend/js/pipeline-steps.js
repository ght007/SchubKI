// Four persistent tabs; calculation is a temporary view, independent of navigation.
export const PIPELINE_STAGES = ["extract", "rules", "retrieve", "premise", "report", "verify", "coach"];
export const STEPS = [
  { id: "reading", short: "Reading", label: "Reading", color: "#6d28d9", description: "Enter the customer's enquiry and choose how to assess it.", stages: ["extract"] },
  { id: "assessment", short: "Result Assessment", label: "Result Assessment", color: "#15803d", description: "Review the decision, requirements, recommended methods, and feasibility-study plan.", stages: ["report"] },
  { id: "verification", short: "Confidence & Verification", label: "Confidence and Verification", color: "#c2410c", description: "Review confidence signals, source checks, and quality metrics.", stages: ["verify"] },
  { id: "coach", short: "Coach", label: "Coach", color: "#b91c1c", description: "Fill the important gaps and re-run with customer answers.", stages: ["coach"] },
];
export const LOADING_PAGE = { id: "loading", label: "Calculating your assessment", color: "#2563eb",
  description: "Follow the current model and rule tasks. Your results will open when the calculation finishes.", stages: PIPELINE_STAGES };

const STEP_IDS = new Set(STEPS.map((step) => step.id));
const LEGACY_TABS = {
  extract: "reading", rules: "verification", retrieve: "verification", premise: "verification",
  report: "assessment", verify: "verification", quality: "verification",
  whatif: "coach", council: "verification", trace: "verification",
  process: "verification", methods: "verification", spectral: "verification",
};

export function isStep(id) { return STEP_IDS.has(id); }
export function normalizeTab(id) { return LEGACY_TABS[id] || (isStep(id) ? id : "reading"); }
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
  return !s.busy && isStep(id) && (id === "reading" || processComplete(s));
}

export function stepStatus(s, id) {
  if (id === "loading") return s.busy ? "active" : "pending";
  if (id === "reading" && s.reading) return "active";
  const stages = sourceStages(id);
  if (!stages.length) return "pending";
  if (stages.every((stage) => stageDone(s, stage))) return "done";
  if (s.busy && activeStep(s) === id) return "active";
  if (!s.busy && (s.error || s.run?.error) && (s.stages.length || s.run)) {
    const firstIncomplete = STEPS.find((step) => !step.stages.every((stage) => stageDone(s, stage)));
    if (firstIncomplete?.id === id) return "error";
  }
  return "pending";
}

export function activeStep(s) {
  const event = [...s.stages].reverse().find((item) => item.status === "start");
  return s.busy ? canonicalStage(event?.stage) || "reading" : s.reading ? "reading" : null;
}

export function pipelineProgress(s) {
  if (processComplete(s)) return 100;
  const firstPending = PIPELINE_STAGES.findIndex((stage) => !stageDone(s, stage));
  const completed = firstPending === -1 ? PIPELINE_STAGES.length : firstPending;
  // Preparation and drafting lead to the Result Assessment point; verification and coaching
  // then advance to their own points. The final fraction waits for the saved result.
  return completed <= 5 ? completed / 5 * (100 / 3) : completed === 6 ? 200 / 3 : 99;
}

export const STATUS_LABELS = { pending: "Waiting", active: "Now", done: "Done", error: "Stopped" };
