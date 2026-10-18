// Sign-in page: e-mail/password log-in and sign-up, Google Identity Services button, already-signed-in state.
import { esc, getJSON, postJSON } from "./api.js";

const $ = (id) => document.getElementById(id);
const errorEl = $("login-error");

// Only same-site relative targets after login (no open redirect).
function nextUrl() {
  const next = new URLSearchParams(location.search).get("next") || "/app";
  return next.startsWith("/") && !next.startsWith("//") ? next : "/app";
}

function showError(message) { errorEl.textContent = message || ""; }

function apiMessage(err) {
  const raw = String(err?.message || err);
  const body = raw.replace(/^\d+\s*/, "");
  try {
    const detail = JSON.parse(body).detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) return "Check the fields and try again.";
  } catch (_) { /* not JSON */ }
  return raw.startsWith("5") ? "The server could not complete this. Try again." : body || "Something went wrong.";
}

function selectTab(which) {
  for (const name of ["login", "signup"]) {
    const on = name === which;
    $(`tab-${name}`).setAttribute("aria-selected", String(on));
    $(`tab-${name}`).setAttribute("aria-pressed", String(on));
    $(`form-${name}`).hidden = !on;
  }
  showError("");
  $(`form-${which}`).querySelector("input")?.focus();
}

async function submit(form, url, body) {
  const button = form.querySelector("button[type=submit]");
  const label = button.textContent;
  button.disabled = true;
  button.textContent = "Please wait…";
  showError("");
  try {
    await postJSON(url, body);
    location.assign(nextUrl());
  } catch (err) {
    showError(apiMessage(err));
    button.disabled = false;
    button.textContent = label;
  }
}

$("tab-login").onclick = () => selectTab("login");
$("tab-signup").onclick = () => selectTab("signup");
if (new URLSearchParams(location.search).get("mode") === "signup") selectTab("signup");

$("form-login").addEventListener("submit", (event) => {
  event.preventDefault();
  const data = Object.fromEntries(new FormData(event.target));
  if (!data.identifier.trim() || !data.password) { showError("Enter your e-mail or username and your password."); return; }
  submit(event.target, "/api/auth/login", { identifier: data.identifier.trim(), password: data.password });
});

$("form-signup").addEventListener("submit", (event) => {
  event.preventDefault();
  const data = Object.fromEntries(new FormData(event.target));
  if (!data.email.trim()) { showError("Enter your e-mail address."); return; }
  if (data.password.length < 8) { showError("Password: at least 8 characters."); return; }
  submit(event.target, "/api/auth/signup", { email: data.email.trim(), password: data.password,
    name: data.name.trim(), username: data.username.trim() });
});

function loadGoogle(clientId) {
  const script = document.createElement("script");
  script.src = "https://accounts.google.com/gsi/client";
  script.async = true;
  script.onload = () => {
    $("google-block").hidden = false;
    google.accounts.id.initialize({
      client_id: clientId,
      ux_mode: "popup",
      callback: async ({ credential }) => {
        showError("");
        try { await postJSON("/api/auth/google", { credential }); location.assign(nextUrl()); }
        catch (err) { showError(apiMessage(err)); }
      },
    });
    const holder = $("google-button");
    google.accounts.id.renderButton(holder, { theme: "outline", size: "large", text: "continue_with",
      shape: "rectangular", width: Math.min(360, holder.clientWidth || 320) });
  };
  script.onerror = () => { $("google-block").hidden = true; };   // blocked or offline: e-mail still works
  document.head.appendChild(script);
}

function showSignedIn(user) {
  $("auth-forms").hidden = true;
  $("guest-link").hidden = true;
  const box = $("signed-in");
  box.hidden = false;
  box.innerHTML = `<h2>You are signed in</h2>
    <p class="muted">${esc(user.name || user.username)} · ${esc(user.email)}</p>
    <div class="row"><a class="btn primary" href="${esc(nextUrl())}">Open the assistant</a>
      <button type="button" class="btn" id="logout">Log out</button></div>`;
  box.querySelector("#logout").onclick = async () => {
    try { await postJSON("/api/auth/logout", {}); } catch (_) { /* cookie cleared anyway on next visit */ }
    location.reload();
  };
}

(async function boot() {
  try {
    const { user } = await getJSON("/api/auth/me");
    if (user) { showSignedIn(user); return; }
  } catch (_) { /* server starting: forms still usable */ }
  try {
    const config = await getJSON("/api/auth/config");
    if (config.google_enabled) loadGoogle(config.google_client_id);
    $("guest-link").hidden = config.auth_required;     // guests only when login is switched off
  } catch (_) { /* no Google button */ }
  $("form-login").querySelector("input").focus();
})();
