// App state: a tiny store with subscribers (no framework).

const state = {
  run: null,            // current RunResult
  previous: null,       // run before the last what-if
  liveRun: null,        // fields received from the run currently in progress
  stages: [],           // [{stage, label, status, detail, ms}]
  details: [],          // [{stage, detail}] council / repair progress lines
  busy: false,
  error: "",
  tab: "extract",
  followStage: true,    // follow the live step until the user selects another view
  mode: "fast",
  examples: [],
  health: null,
  evidence: null,       // {source, page, quote, verified}
  answers: {},          // pending what-if answers
};

const subs = new Set();

export function get() { return state; }

export function set(patch) {
  Object.assign(state, patch);
  subs.forEach((fn) => fn(state));
}

export function subscribe(fn) { subs.add(fn); return () => subs.delete(fn); }

const memo = { tab: "afs.tab", mode: "afs.mode" };
export function remember(key, value) { try { localStorage.setItem(memo[key], value); } catch (_) { /* private mode */ } }
export function recall(key, fallback) { try { return localStorage.getItem(memo[key]) || fallback; } catch (_) { return fallback; } }
