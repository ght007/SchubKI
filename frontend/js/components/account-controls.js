// Account UI. The account chip sits at the bottom of the Queries box (as in Claude's sidebar) and a compact
// copy in the top bar; both open the same menu: run history, plans, log out.
// Plans: Basic = General view, Pro = General + Expert (see /pricing). Guests only exist with AUTH_REQUIRED=0.
import { esc, getJSON, postJSON } from "../api.js";

const STATUS = { provisional_assessment: ["Provisional assessment", "core"],
  insufficient_information: ["Insufficient information", "warn"], outside_supported_scope: ["Outside supported scope", "block"] };
const CHEVRON = `<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M6 8l4 4 4-4"/></svg>`;
const when = (iso) => { const d = new Date(iso); return Number.isNaN(+d) ? "" :
  d.toLocaleString(undefined, { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" }); };
const plural = (n, one, many = `${one}s`) => `${n} ${n === 1 ? one : many}`;
const initials = (u) => (u.name || u.username || u.email).split(/[\s@._-]+/).filter(Boolean).slice(0, 2)
  .map((part) => part[0].toUpperCase()).join("");

export const isPro = (user) => !user || (user.views || []).includes("expert");   // guest mode (no login) keeps both views
export const planName = (user) => (user?.subscription_tier === "pro" ? "Pro plan" : "Basic plan");

function avatar(user, cls = "") {
  return user.avatar_url ? `<img class="account-avatar ${cls}" src="${esc(user.avatar_url)}" alt="" referrerpolicy="no-referrer">`
    : `<span class="account-avatar ${cls}" aria-hidden="true">${esc(initials(user))}</span>`;
}

async function logout(everywhere = false) {
  try { await postJSON(`/api/auth/logout${everywhere ? "?everywhere=true" : ""}`, {}); } catch (_) { /* leave anyway */ }
  location.assign("/login");
}

// ------------------------------------------------------------------ chip (Queries box footer)
export function accountChip(user) {
  if (!user) return `<a class="account-chip guest" href="/login?next=${encodeURIComponent("/app")}">Log in to save your history</a>`;
  return `<button type="button" class="account-chip" data-account-menu aria-haspopup="menu" title="Account, plan and history">
      ${avatar(user)}<span class="account-chip-text"><span class="account-chip-name">${esc(user.name || user.username)}</span>
      <span class="account-chip-plan">${esc(planName(user))}</span></span>${CHEVRON}</button>`;
}

// ------------------------------------------------------------------ menu (popover)
let menuEl = null;
function closeMenu() { menuEl?.remove(); menuEl = null; }
document.addEventListener("keydown", (e) => { if (e.key === "Escape") closeMenu(); });
document.addEventListener("click", (e) => {
  if (menuEl && !menuEl.contains(e.target) && !e.target.closest("[data-account-menu]")) closeMenu();
});

export function openAccountMenu(anchor, user, { openRun }) {
  if (menuEl) { closeMenu(); return; }
  const pro = isPro(user);
  menuEl = document.createElement("div");
  menuEl.className = "account-menu";
  menuEl.setAttribute("role", "menu");
  menuEl.innerHTML = `<div class="account-menu-head"><span class="account-menu-email">${esc(user.email)}</span>
      <span class="pill ${pro ? "core" : ""}">${esc(planName(user))}</span></div>
    ${pro ? "" : `<a role="menuitem" class="account-menu-item upgrade" href="/pricing">Upgrade to Pro<span>Unlock the Expert view</span></a>`}
    <button role="menuitem" type="button" class="account-menu-item" data-act="history">Run history</button>
    ${pro ? '<a role="menuitem" class="account-menu-item" href="/kb">Knowledge base<span>Edit evidence, rules and documents</span></a>' : ""}
    <a role="menuitem" class="account-menu-item" href="/pricing">Plans and pricing</a>
    <div class="account-menu-sep"></div>
    <button role="menuitem" type="button" class="account-menu-item" data-act="logout">Log out</button>`;
  document.body.appendChild(menuEl);
  const r = anchor.getBoundingClientRect();
  const up = r.top > window.innerHeight / 2;
  const width = Math.max(r.width, 250);
  menuEl.style.width = `${width}px`;
  menuEl.style.left = `${Math.max(8, Math.min(r.left, window.innerWidth - width - 8))}px`;
  menuEl.style[up ? "bottom" : "top"] = up ? `${window.innerHeight - r.top + 6}px` : `${r.bottom + 6}px`;
  menuEl.querySelector("[data-act=history]").onclick = () => { closeMenu(); openHistory(user, openRun); };
  menuEl.querySelector("[data-act=logout]").onclick = () => logout(false);
  menuEl.querySelector(".account-menu-item")?.focus();
}

// ------------------------------------------------------------------ history panel (dialog)
function dialog() {
  const d = document.getElementById("accountDialog") || document.body.appendChild(Object.assign(
    document.createElement("dialog"), { id: "accountDialog", className: "account-dialog" }));
  d.setAttribute("aria-labelledby", "accountDialogTitle");
  d.onclick = (event) => { if (event.target === d) d.close(); };
  return d;
}

async function renderHistory(d, list, view, openRun) {
  list.innerHTML = `<p class="muted small">Loading…</p>`;
  try {
    const runs = await getJSON(`/api/me/runs?limit=30${view ? `&view=${view}` : ""}`);
    list.innerHTML = runs.length ? `<ul class="account-runs">${runs.map((r) => {
      const [label, cls] = STATUS[r.status] || ["No result", ""];
      return `<li><button type="button" data-run="${esc(r.runId)}">
        <span class="account-run-title">${esc(r.title || "Untitled enquiry")}</span>
        <span class="account-run-meta"><span class="pill ${cls}">${esc(label)}</span>
          <span class="account-view-tag">${esc(r.view === "expert" ? "Expert" : "General")}${r.mode === "council" ? " · council" : ""}${r.parentRunId ? " · what-if" : ""}</span>
          <span>${esc(when(r.createdAt))}</span></span></button></li>`; }).join("")}</ul>`
      : `<p class="muted small">No runs yet${view ? ` in the ${view === "expert" ? "Expert" : "General"} view` : ""}. Assess an enquiry and it appears here.</p>`;
    list.querySelectorAll("[data-run]").forEach((b) => (b.onclick = () => { d.close(); openRun(b.dataset.run); }));
  } catch (_) {
    list.innerHTML = `<p class="err small">Could not load your history. Your session may have expired: <a href="/login">log in again</a>.</p>`;
  }
}

export async function openHistory(user, openRun) {
  let me = { user, stats: null };
  try { me = await getJSON("/api/auth/me"); } catch (_) { /* show what we have */ }
  if (!me.user) { location.assign("/login"); return; }
  const u = me.user;
  const d = dialog();
  d.innerHTML = `<div class="account-dialog-content account-panel">
    <button type="button" class="dialog-close" aria-label="Close dialog">×</button>
    <div class="account-head">${avatar(u, "large")}<div>
      <h2 id="accountDialogTitle">${esc(u.name || u.username)}</h2>
      <p class="muted small">${esc(u.email)} · @${esc(u.username)}</p></div></div>
    <p class="account-facts small">
      <span class="pill ${isPro(u) ? "core" : ""}">${esc(planName(u))}</span>
      ${me.stats ? `<span>${plural(me.stats.runs, "run")} · ${plural(me.stats.queries, "saved enquiry", "saved enquiries")}</span>` : ""}
      <span class="muted">${u.auth_provider.includes("google") ? "Google" : "E-mail"} sign-in${u.last_login_at ? ` · last login ${esc(when(u.last_login_at))}` : ""}</span>
      <a href="/pricing">${isPro(u) ? "Manage plan" : "Upgrade to Pro"}</a>
    </p>
    <div class="account-history-head"><h3>Run history</h3>
      <div class="seg" role="group" aria-label="Filter by view">
        <button type="button" data-filter="" aria-pressed="true">All</button>
        <button type="button" data-filter="general" aria-pressed="false">General</button>
        <button type="button" data-filter="expert" aria-pressed="false">Expert</button></div></div>
    <div id="accountHistory" class="account-history"></div>
    <div class="account-dialog-actions">
      <button type="button" class="btn link" id="logoutAll">Log out on all devices</button>
      <button type="button" class="btn primary" id="logout">Log out</button>
    </div></div>`;
  const list = d.querySelector("#accountHistory");
  d.querySelector(".dialog-close").onclick = () => d.close();
  d.querySelector("#logout").onclick = () => logout(false);
  d.querySelector("#logoutAll").onclick = () => logout(true);
  d.querySelectorAll("[data-filter]").forEach((b) => (b.onclick = () => {
    d.querySelectorAll("[data-filter]").forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
    renderHistory(d, list, b.dataset.filter, openRun);
  }));
  d.showModal();
  renderHistory(d, list, "", openRun);
}

// ------------------------------------------------------------------ top bar
export function mountAccountControls(el, { user = null, openRun }) {
  if (!user) {
    el.innerHTML = `<a class="btn" href="/pricing">Pricing</a>
      <a class="btn primary" href="/login?next=${encodeURIComponent("/app")}">Log in</a>`;
    return;
  }
  el.innerHTML = (isPro(user) ? `<span class="pill core" title="General and Expert view">Pro</span>`
      : `<a class="btn account-subscribe" href="/pricing">Upgrade to Pro</a>`)
    + `<button type="button" class="btn account-profile" data-account-menu aria-haspopup="menu" title="Account, plan and history">
        ${avatar(user)}<span>${esc(user.name || user.username)}</span></button>`;
  el.querySelector("[data-account-menu]").onclick = (e) => openAccountMenu(e.currentTarget, user, { openRun });
}