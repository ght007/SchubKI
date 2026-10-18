// Local enquiry drafts only. No user, conversation, or run IDs are stored here.
// A future provider can implement the same async list/save/remove interface.
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
    get persistent() { return persistent; },
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
