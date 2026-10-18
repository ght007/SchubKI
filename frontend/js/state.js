// App state: a tiny store with subscribers (no framework).

const state = {
  run: null,            // current RunResult
  previous: null,       // run before the last what-if
  liveRun: null,        // fields received from the run currently in progress
  stages: [],           // [{stage, label, status, detail, ms}]
  details: [],          // [{stage, detail}] council / repair progress lines
  busy: false,
  error: "",
  tab: "reading",
  view: "general",      // "general" (compact, default) | "expert" (full workbench)
  mode: "fast",
  modelChoice: "auto", // "auto" = server defaults; otherwise one model for every stage of the run
  modelList: null,      // GET /api/models: the models this server's key may use
  draftEnquiry: null, // null means use the loaded run's enquiry
  selectedExample: "",
  user: null,             // logged-in account with plan and allowed views (null = guest); /api/auth/me
  savedQueries: [],       // enquiry drafts: browser-local for guests, from the account when logged in
  queryStorageLabel: "",
  queryRuns: null,        // {queryId, runs}: every result generated for the active saved query, newest first  // where the drafts are kept, shown under the sidebar
  activeQueryId: null,
  querySidebarOpen: true,
  queryPersistent: true,
  savingQuery: false,
  queryNotice: "",
  skipQueryAutosave: false, // keep a removed query from reappearing when leaving its draft
  examples: [],
  health: null,
  evidence: null,       // {source, page, quote, verified}
  answers: {},          // pending what-if answers
  paths: [],            // AFS paths chosen by the expert (multi-select A/B/C; empty = Auto)
  understand: null,     // "Is this what you mean?" dialog data (step 1 of a run), null when closed
  rejected: [],         // requirement fields marked as misread in that dialog
  reading: false,       // step 1 in progress
  confirm: true,        // show the review dialog before every run (remembered)
};

const subs = new Set();

export function get() { return state; }

export function set(patch) {
  Object.assign(state, patch);
  subs.forEach((fn) => fn(state));
}

export function subscribe(fn) { subs.add(fn); return () => subs.delete(fn); }

const memo = { tab: "afs.tab", mode: "afs.mode", modelChoice: "afs.modelChoice", view: "afs.view", confirm: "afs.confirm", evidenceSplit: "afs.evidenceSplit" };
export function remember(key, value) { try { localStorage.setItem(memo[key], value); } catch (_) { /* private mode */ } }
export function recall(key, fallback) { try { return localStorage.getItem(memo[key]) || fallback; } catch (_) { return fallback; } }
