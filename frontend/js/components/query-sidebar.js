import { esc } from "../api.js";
import { accountChip } from "./account-controls.js";

const QUERY_ICON = `<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M4 3.5h12a1.5 1.5 0 0 1 1.5 1.5v8a1.5 1.5 0 0 1-1.5 1.5H8l-4.5 3v-3A1.5 1.5 0 0 1 2.5 13V5A1.5 1.5 0 0 1 4 3.5Z"/><path d="M6 7h8M6 10h5"/></svg>`;
const RESULT_ICON = `<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M4 16.5V9M8.5 16.5V5M13 16.5v-5M17 16.5V3.5"/></svg>`;
const STATUS_LABEL = { provisional_assessment: "Provisional", insufficient_information: "Insufficient info",
  outside_supported_scope: "Outside scope" };
const DELETE_ICON = `<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M3.5 5.5h13M7 5.5v-2h6v2M5 5.5l1 11h8l1-11M8 8v5.5M12 8v5.5"/></svg>`;

export function renderQuerySidebar(el, s, actions) {
  if (!el) return;
  const enquiry = s.draftEnquiry ?? s.run?.enquiry ?? "";
  el.innerHTML = `<div class="query-sidebar-heading">
      <h2 id="saved-queries-title">Queries</h2>
      <button type="button" class="btn query-sidebar-toggle" aria-expanded="${s.querySidebarOpen}" aria-controls="saved-query-list" id="toggleQueries">${s.querySidebarOpen ? "Hide" : "Show"}</button>
    </div>
    <button type="button" class="btn query-new" id="newQuery"><span aria-hidden="true">＋</span> New query</button>
    <div id="saved-query-list" class="query-sidebar-body" ${s.querySidebarOpen ? "" : "hidden"}>
      <div class="query-list-label">Recent <span>${s.savedQueries.length}</span></div>
      ${s.savedQueries.length ? `<nav aria-label="Saved queries"><ul class="query-list">${s.savedQueries.map((query) => `<li class="query-row ${s.activeQueryId === query.id ? "active" : ""}">
        <button type="button" class="query-open" data-open-query="${esc(query.id)}" ${s.activeQueryId === query.id ? 'aria-current="true"' : ""} title="${esc(query.title)}">
          ${QUERY_ICON}<span>${esc(query.title)}</span></button>
        ${query.lastRunId ? `<button type="button" class="query-result" data-open-run="${esc(query.lastRunId)}"
          title="Open last result${query.lastStatus ? `: ${esc(STATUS_LABEL[query.lastStatus] || query.lastStatus)}` : ""}${query.view ? ` (${esc(query.view)} view)` : ""}"
          aria-label="Open last result of: ${esc(query.title)}">${RESULT_ICON}</button>` : ""}
        <button type="button" class="query-delete" data-delete-query="${esc(query.id)}" aria-label="Remove saved query: ${esc(query.title)}" title="Remove saved query">${DELETE_ICON}</button>
      </li>`).join("")}</ul></nav>` : `<p class="query-empty">No saved queries yet.<br>Save an enquiry or assess it to keep it here.</p>`}
      <div class="query-sidebar-footer">
        <button type="button" class="btn" id="saveQuery" ${!enquiry.trim() || s.reading || s.savingQuery ? "disabled" : ""}>${s.savingQuery ? "Saving…" : s.activeQueryId ? "Save changes" : "Save query"}</button>
        <p class="query-storage-note">${esc(s.queryStorageLabel || (s.queryPersistent ? "Saved on this browser" : "Kept for this session only"))}</p>
        <p class="query-notice" role="status">${esc(s.queryNotice)}</p>
      </div>
    </div>
    <div class="query-account">${accountChip(s.user)}</div>`;
  el.querySelector("#toggleQueries").onclick = actions.toggleQuerySidebar;
  el.querySelector("#newQuery").onclick = actions.newQuery;
  el.querySelector("#saveQuery").onclick = () => actions.saveQuery();
  el.querySelectorAll("[data-open-query]").forEach((button) => (button.onclick = () => actions.openQuery(button.dataset.openQuery)));
  el.querySelector("[data-account-menu]")?.addEventListener("click", (e) => actions.openAccountMenu(e.currentTarget));
  el.querySelectorAll("[data-open-run]").forEach((button) => (button.onclick = () => actions.openRun(button.dataset.openRun)));
  el.querySelectorAll("[data-delete-query]").forEach((button) => (button.onclick = () => actions.removeQuery(button.dataset.deleteQuery)));
}
