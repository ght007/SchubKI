// Saved enquiries behind one async interface: list / save / remove, plus runsFor(queryId) (every result
// generated for that query, newest first) and attachRun(queryId, run) (called when a run finishes).
//   createLocalQueryRepository   guests: drafts and their result ids in this browser only
//   createServerQueryRepository  logged in: the account; the server links each run to its query itself
import { deleteJSON, getJSON, postJSON } from "./api.js";

const STORAGE_KEY = "afs.saved-queries.v1";
const MAX_QUERIES = 50;
const MAX_RUNS = 30;                       // results remembered per query in the browser (guest mode)

const copy = (query) => ({ ...query, paths: [...query.paths], runs: [...(query.runs || [])] });
const titleFor = (text) => text.replace(/\s+/g, " ").trim().slice(0, 72);

function normalize(query) {
  return {
    id: query.id,
    title: titleFor(query.enquiry),
    enquiry: query.enquiry,
    mode: query.mode === "council" ? "council" : "fast",
    modelChoice: typeof query.modelChoice === "string" ? query.modelChoice : "auto",
    paths: [...new Set((Array.isArray(query.paths) ? query.paths : []).filter((path) => ["A", "B", "C"].includes(path)))].sort(),
    updatedAt: Number.isFinite(query.updatedAt) ? query.updatedAt : Date.now(),
    runs: Array.isArray(query.runs) ? query.runs.filter((run) => run && typeof run.runId === "string").slice(0, MAX_RUNS) : [],
    lastRunId: query.lastRunId || query.runs?.[0]?.runId || null,
    lastStatus: query.lastStatus || query.runs?.[0]?.status || null,
    runCount: Number.isFinite(query.runCount) ? query.runCount : (Array.isArray(query.runs) ? query.runs.length : 0),
  };
}

// What the sidebar needs about one result; the result itself is loaded from /api/runs/{id}.
export function runSummary(run, view) {
  return { runId: run.id, createdAt: run.created, mode: run.mode, view: view || "general",
    parentRunId: run.parent_run_id || null, status: run.report?.decision_status || null };
}

export function createLocalQueryRepository() {
  let queries = [];
  let persistent = true;
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
    if (Array.isArray(saved)) queries = saved.filter((query) => query && typeof query.id === "string" &&
      typeof query.enquiry === "string" && query.enquiry.trim()).map(normalize)
      .sort((a, b) => b.updatedAt - a.updatedAt).slice(0, MAX_QUERIES);
  } catch (_) { persistent = false; }

  function persist() {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(queries)); persistent = true; }
    catch (_) { persistent = false; } // drafts still work in memory for this session
  }

  return {
    kind: "local",
    get persistent() { return persistent; },
    get label() { return persistent ? "Saved on this browser" : "Kept for this session only"; },
    async list() { return queries.map(copy); },
    async save(draft) {
      if (!draft.enquiry?.trim()) return null;
      const id = draft.id || globalThis.crypto?.randomUUID?.() || `${Date.now()}-${Math.random().toString(36).slice(2)}`;
      const previous = queries.find((item) => item.id === id);
      const query = normalize({ ...draft, id, updatedAt: Date.now(), runs: previous?.runs || [] });  // keep its results
      queries = [query, ...queries.filter((item) => item.id !== id)].slice(0, MAX_QUERIES);
      persist();
      return copy(query);
    },
    async remove(id) { queries = queries.filter((query) => query.id !== id); persist(); },
    async runsFor(id) { return [...(queries.find((query) => query.id === id)?.runs || [])]; },
    async attachRun(id, summary) {
      const query = queries.find((item) => item.id === id);
      if (!query || !summary?.runId) return;
      const runs = [summary, ...query.runs.filter((run) => run.runId !== summary.runId)].slice(0, MAX_RUNS);
      Object.assign(query, { runs, runCount: runs.length, lastRunId: summary.runId, lastStatus: summary.status });
      persist();
    },
  };
}

const fromServer = (query) => ({ ...normalize({ ...query, updatedAt: Date.parse(query.updatedAt) }),
  view: query.view || null, lastRunId: query.lastRunId || null, lastStatus: query.lastStatus || null,
  runCount: query.runCount || 0 });

export function createServerQueryRepository() {
  return {
    kind: "server",
    persistent: true,
    label: "Saved to your account",
    async list() { return (await getJSON("/api/me/queries")).map(fromServer); },
    async save(draft) {
      if (!draft.enquiry?.trim()) return null;
      return fromServer(await postJSON("/api/me/queries", { id: draft.id || null, enquiry: draft.enquiry, mode: draft.mode,
        modelChoice: draft.modelChoice, paths: draft.paths || [], view: draft.view || null }));
    },
    async remove(id) { await deleteJSON(`/api/me/queries/${encodeURIComponent(id)}`); },
    async runsFor(id) { return getJSON(`/api/me/queries/${encodeURIComponent(id)}/runs`); },
    async attachRun() { /* the server links the run to the query when it finishes (X-AFS-Query-Id) */ },
  };
}

// First login on this browser: copy the guest drafts into the account once (the local copy is kept).
export async function importLocalDrafts(userId, local, server) {
  const flag = `afs.imported-drafts.${userId}`;
  try { if (localStorage.getItem(flag)) return 0; } catch (_) { return 0; }
  const drafts = await local.list();
  let n = 0;
  for (const draft of drafts.reverse()) {               // oldest first keeps the order
    try { await server.save({ ...draft, id: null }); n += 1; } catch (_) { /* skip one bad draft */ }
  }
  try { localStorage.setItem(flag, String(Date.now())); } catch (_) { /* ignore */ }
  return n;
}
