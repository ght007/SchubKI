// One ordered model drives the segmented spectrum navigation and live status.
export const STEPS = [
  { id: "extract", short: "Read", label: "Read the enquiry", color: "#6d28d9", ink: "#fff", description: "Facts, unknowns, and assumptions found in the customer's words." },
  { id: "rules", short: "Rules", label: "Rules and screening", color: "#2563eb", ink: "#fff", description: "AFS rules, method scores, fiber coverage, and spectral ranges." },
  { id: "retrieve", short: "Evidence", label: "Retrieve evidence", color: "#0e7490", ink: "#fff", description: "The passages selected to support or challenge the assessment." },
  { id: "premise", short: "Premises", label: "Check premises", color: "#15803d", ink: "#fff", description: "The customer's own claims checked against the available evidence." },
  { id: "report", short: "Assess", label: "Write the assessment", color: "#eab308", ink: "#1f2937", description: "Recommendations, measurement concept, risks, and first experiment." },
  { id: "verify", short: "Verify", label: "Verify and review quality", color: "#c2410c", ink: "#fff", description: "Citation, number, and client fact checks, plus the quality gate." },
  { id: "coach", short: "Coach", label: "Coach and confidence", color: "#b91c1c", ink: "#fff", description: "Missing facts, follow-up questions, and computed confidence." },
];

export const UTILITIES = [
  { id: "whatif", label: "What-if" },
  { id: "council", label: "Council" },
  { id: "trace", label: "Trace" },
];

const STEP_IDS = new Set(STEPS.map((step) => step.id));
const LEGACY_TABS = { assessment: "report", methods: "rules", spectral: "rules", quality: "verify" };

export function isStep(id) { return STEP_IDS.has(id); }
export function normalizeTab(id) {
  const value = LEGACY_TABS[id] || id;
  return isStep(value) || UTILITIES.some((item) => item.id === value) ? value : "extract";
}
export function canonicalStage(id) { return id === "council" ? "report" : id; }

export function latestStageEvent(s, id) {
  return [...(s.stages || [])].reverse().find((event) => canonicalStage(event.stage) === id &&
    (event.status === "start" || event.status === "done"));
}

function hasTiming(run, id) {
  const timings = run?.timings_ms || {};
  return Object.hasOwn(timings, id) || (id === "report" && Object.hasOwn(timings, "council"));
}

export function stepStatus(s, id) {
  const event = latestStageEvent(s, id);
  if (event?.status === "done") return "done";
  if (event?.status === "start") return s.busy ? "active" : "error";

  const run = s.busy ? s.liveRun : s.run;
  if (hasTiming(run, id)) return "done";
  if (!s.busy && (s.error || run?.error)) {
    const index = STEPS.findIndex((step) => step.id === id);
    const lastDone = Math.max(-1, ...STEPS.map((step, i) => hasTiming(run, step.id) ? i : -1));
    if (index === lastDone + 1) return "error";
  }
  return "pending";
}

export function activeStep(s) {
  return STEPS.find((step) => stepStatus(s, step.id) === "active")?.id ||
    (s.busy ? STEPS.find((step) => stepStatus(s, step.id) === "pending")?.id : null) || null;
}

export const STATUS_LABELS = { pending: "Waiting", active: "Now", done: "Done", error: "Stopped" };
