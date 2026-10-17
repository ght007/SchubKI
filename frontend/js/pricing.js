// Pricing page: plan cards and comparison table from /api/billing/plans; buttons call /api/billing/checkout.
// Payments are not connected yet. In BILLING_MODE=demo the plan switches at once and the page says no payment
// was taken; a payment provider later answers checkout with {status: "redirect", checkout_url}.
import { esc, getJSON, postJSON } from "./api.js";

const $ = (id) => document.getElementById(id);
const CHECK = `<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M4.5 10.5l3.5 3.5 7.5-8"/></svg>`;
const DASH = `<span class="pricing-no" aria-label="Not included">—</span>`;
let state = { plans: [], current: null, user: null, billingMode: "demo" };

function apiMessage(err) {
  const body = String(err?.message || err).replace(/^\d+\s*/, "");
  try { return JSON.parse(body).detail || body; } catch (_) { return body || "Something went wrong."; }
}

function nav() {
  $("pricing-nav").innerHTML = state.user
    ? `<span class="muted small">${esc(state.user.email)}</span><a class="btn primary" href="/app">Open the assistant</a>`
    : `<a class="btn" href="/login?next=${encodeURIComponent("/pricing")}">Log in</a>
       <a class="btn primary" href="/login?mode=signup&next=${encodeURIComponent("/pricing")}">Sign up</a>`;
}

function button(p) {
  const rank = (id) => state.plans.findIndex((x) => x.id === id);
  if (!state.user) {
    return `<a class="btn pricing-cta ${p.highlight ? "primary" : ""}" href="/login?mode=signup&next=${encodeURIComponent("/pricing")}">Get ${esc(p.name)}</a>`;
  }
  if (state.current === p.id) return `<button type="button" class="btn pricing-cta" disabled>Your current plan</button>`;
  const label = rank(p.id) > rank(state.current) ? `Upgrade to ${p.name}` : `Switch to ${p.name}`;
  return `<button type="button" class="btn pricing-cta ${p.highlight ? "primary" : ""}" data-plan="${esc(p.id)}">${esc(label)}</button>`;
}

function cards() {
  $("plans").innerHTML = state.plans.map((p) => `<article class="pricing-card ${p.highlight ? "featured" : ""} ${state.current === p.id ? "current" : ""}">
      ${p.highlight ? `<span class="pricing-badge">Recommended</span>` : ""}
      ${state.current === p.id ? `<span class="pricing-badge current">Current plan</span>` : ""}
      <h3>${esc(p.name)}</h3>
      <p class="pricing-tagline">${esc(p.tagline)}</p>
      <p class="pricing-price"><span class="amount">$${p.price_usd}</span><span class="per">/ ${esc(p.interval)}</span></p>
      <p class="pricing-views">${p.views.map((v) => `<span class="pill ${v === "expert" ? "core" : ""}">${v === "expert" ? "Expert view" : "General view"}</span>`).join("")}</p>
      ${button(p)}
      <ul class="pricing-features">${p.features.map((f) => `<li>${CHECK}<span>${esc(f)}</span></li>`).join("")}</ul>
    </article>`).join("");
  $("plans").querySelectorAll("[data-plan]").forEach((b) => (b.onclick = () => choose(b)));
}

function compare() {
  const rows = [];
  for (const p of state.plans) {
    for (const f of p.features) {
      if (/^Everything in /.test(f) || rows.some((r) => r.f === f)) continue;
      rows.push({ f, from: state.plans.indexOf(p) });
    }
  }
  $("compare").innerHTML = `<thead><tr><th scope="col">Feature</th>${state.plans.map((p) =>
      `<th scope="col">${esc(p.name)}<span>$${p.price_usd}/${esc(p.interval)}</span></th>`).join("")}</tr></thead>
    <tbody>${rows.map((r) => `<tr><th scope="row">${esc(r.f)}</th>${state.plans.map((_, i) =>
      `<td>${i >= r.from ? `<span class="pricing-yes" aria-label="Included">${CHECK}</span>` : DASH}</td>`).join("")}</tr>`).join("")}</tbody>`;
}

async function choose(b) {
  const msg = $("pricing-message");
  b.disabled = true;
  const label = b.textContent;
  b.textContent = "Please wait…";
  msg.className = "pricing-message";
  msg.textContent = "";
  try {
    const r = await postJSON("/api/billing/checkout", { plan: b.dataset.plan });
    if (r.status === "redirect" && r.checkout_url) { location.assign(r.checkout_url); return; }
    state.current = r.plan;
    state.user = r.user || state.user;
    const name = state.plans.find((p) => p.id === r.plan)?.name || r.plan;
    msg.innerHTML = `You are now on <b>${esc(name)}</b>.${r.demo ? " Demo mode: no payment was taken." : ""}
      <a href="/app">Open the assistant</a>`;
    msg.classList.add("ok");
    cards();
  } catch (err) {
    msg.textContent = apiMessage(err);
    msg.classList.add("bad");
    b.disabled = false;
    b.textContent = label;
  }
}

(async function boot() {
  const params = new URLSearchParams(location.search);
  $("upgrade-banner").hidden = params.get("upgrade") !== "expert";
  try { state.user = (await getJSON("/api/auth/me")).user; } catch (_) { /* treat as logged out */ }
  nav();
  try {
    const info = await getJSON("/api/billing/plans");
    state = { ...state, plans: info.plans, current: info.current, billingMode: info.billing_mode };
  } catch (err) {
    $("plans").innerHTML = `<p class="err">Could not load the plans: ${esc(apiMessage(err))}</p>`;
    return;
  }
  if (state.billingMode !== "demo") {
    $("faq-payment").querySelector("p").textContent = "Online payment is not connected yet. Plan changes open as soon as it is.";
  }
  cards();
  compare();
})();
