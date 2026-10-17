// Saved enquiries behind one async list/save/remove interface:
//   createLocalQueryRepository   guests: drafts in this browser only, no user or run ids
//   createServerQueryRepository  logged in: drafts in the user's account, with the last run and its status
import { deleteJSON, getJSON, postJSON } from "./api.js";

const STORAGE_KEY = "afs.saved-queries.v1";
const MAX_QUERIES = 50;

const copy = (query) => ({ ...query, paths: [...query.paths] });
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
  };
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
      const query = normalize({ ...draft, id, updatedAt: Date.now() });
      queries = [query, ...queries.filter((item) => item.id !== id)].slice(0, MAX_QUERIES);
      persist();
      return copy(query);
    },
    async remove(id) { queries = queries.filter((query) => query.id !== id); persist(); },
  };
}

const fromServer = (query) => ({ ...normalize({ ...query, updatedAt: Date.parse(query.updatedAt) }),
  view: query.view || null, lastRunId: query.lastRunId || null, lastStatus: query.lastStatus || null });

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
