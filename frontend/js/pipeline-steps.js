// Five browser tabs group the underlying pipeline stages without hiding their progress.
export const STEPS = [
  { id: "reading", short: "Reading", label: "Reading", color: "#6d28d9", description: "Enter the customer's enquiry and choose how to assess it.", stages: ["extract"] },
  { id: "process", short: "Process", label: "Process", color: "#2563eb", description: "Follow the models, rules, and evidence search while the assessment is calculated.", stages: ["extract", "rules", "retrieve", "premise", "report", "verify", "coach"] },
  { id: "assessment", short: "Result Assessment", label: "Result Assessment", color: "#15803d", description: "Review recommendations and open the highlighted evidence behind sourced claims.", stages: ["report"] },
  { id: "verification", short: "Confidence & Verification", label: "Confidence and Verification", color: "#c2410c", description: "Review confidence signals, source checks, and quality metrics.", stages: ["verify"] },
  { id: "coach", short: "Coach", label: "Coach", color: "#b91c1c", description: "Fill the important gaps and re-run with customer answers.", stages: ["coach"] },
];

const STEP_IDS = new Set(STEPS.map((step) => step.id));
const LEGACY_TABS = {
  extract: "reading", rules: "process", retrieve: "process", premise: "process",
  report: "assessment", verify: "verification", quality: "verification",
  whatif: "coach", council: "process", trace: "process",
  methods: "process", spectral: "process",
};

export function isStep(id) { return STEP_IDS.has(id); }
export function normalizeTab(id) { return LEGACY_TABS[id] || (isStep(id) ? id : "reading"); }
export function canonicalStage(id) { return id === "council" ? "assessment" : LEGACY_TABS[id] || id; }

function sourceStages(id) { return STEPS.find((step) => step.id === id)?.stages || []; }
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
  return id === "reading" || id === "process" || processComplete(s);
}

export function stepStatus(s, id) {
  if (id === "reading" && s.reading) return "active";
  if (id === "process") {
    if (s.busy) return "active";
    if (s.run?.error) return "error";
    return processComplete(s) ? "done" : "pending";
  }
  if (id !== "reading" && !processComplete(s)) return "pending";
  const stages = sourceStages(id);
  if (!stages.length) return "pending";
  if (stages.every((stage) => stageDone(s, stage))) return "done";
  const started = stages.some((stage) => !!stageEvent(s, stage) || stageDone(s, stage));
  if (s.busy && started) return "active";
  if (!s.busy && (s.error || s.run?.error) && (s.stages.length || s.run)) {
    const firstIncomplete = STEPS.find((step) => !step.stages.every((stage) => stageDone(s, stage)));
    if (firstIncomplete?.id === id) return "error";
  }
  return "pending";
}

export function activeStep(s) {
  return s.busy ? "process" : s.reading ? "reading" : null;
}

export const STATUS_LABELS = { pending: "Waiting", active: "Now", done: "Done", error: "Stopped" };
