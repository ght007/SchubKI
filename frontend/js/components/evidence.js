// Source drawer: page text with the quote marked, and the PDF page image with the passage highlighted.
import { esc, getJSON } from "../api.js";

function markQuote(text, quote) {
  const safe = esc(text);
  if (!quote) return safe;
  const words = quote.split(/\s+/).filter(Boolean).map((w) => esc(w).replace(/[.*+?^${}()|[\]\\]/g, "\\$&"));
  if (!words.length) return safe;
  const re = new RegExp(words.join("[\\s\\S]{0,3}?\\s*"), "i");   // tolerate line breaks / hyphenation
  return safe.replace(re, (m) => `<mark id="hit">${m}</mark>`);
}

const STATUS_TEXT = {
  verified: "Quote found verbatim on this page.",
  fuzzy: "Quote found nearly verbatim on this page.",
  unverified: "The quote was NOT found on this page: treat this claim as unsupported.",
  scope_warning: "Quote found, but the source's scope (lab / in vitro / business) cannot support this claim.",
};

export async function renderEvidence(el, ev, close) {
  if (!ev) { el.innerHTML = ""; return; }
  el.innerHTML = `<div class="drawer-inner"><div class="drawer-head"><b>${esc(ev.source)} p.${ev.page}</b>
    <button class="btn" id="close">Close</button></div><div class="drawer-body"><p class="muted">Loading the page…</p></div></div>`;
  el.querySelector("#close").onclick = close;
  try {
    const data = await getJSON(`/api/source/${encodeURIComponent(ev.source)}/${ev.page}?q=${encodeURIComponent(ev.quote || "")}`);
    const meta = data.meta || {};
    const found = data.quote_found;
    const status = ev.status && ev.status !== "unchecked" ? ev.status : found === true ? "verified" : found === false ? "unverified" : null;
    const isPdf = (meta.file || "").endsWith(".pdf");
    el.querySelector(".drawer-body").innerHTML = `
      <div class="small muted">${esc(meta.title || "")}</div>
      <div class="small" style="margin:.3rem 0 .6rem">Evidence scope: <b>${esc(meta.scope || "n/a")}</b></div>
      ${ev.quote ? `<div class="quote">“${esc(ev.quote)}”</div>` : ""}
      ${status ? `<div class="pill ${status === "verified" ? "ok" : status === "fuzzy" ? "warn" : "block"}" style="white-space:normal;margin-bottom:.7rem">${esc(STATUS_TEXT[status] || status)}</div>` : ""}
      ${data.transcribed ? `<p class="small muted">S02 slides are images: the text below is the team's transcription of this slide; compare it with the slide image.</p>` : ""}
      <div class="pagetext">${markQuote(data.text, ev.quote)}</div>
      ${isPdf ? `<h3>Original page</h3><img alt="${esc(ev.source)} page ${ev.page}" loading="lazy"
        src="/api/source/${encodeURIComponent(ev.source)}/${ev.page}/image?q=${encodeURIComponent(data.transcribed ? "" : ev.quote || "")}">` : ""}`;
    el.querySelector("#hit")?.scrollIntoView({ block: "center" });
  } catch (e) {
    el.querySelector(".drawer-body").innerHTML = `<div class="err">Could not load ${esc(ev.source)} p.${ev.page}: ${esc(e.message)}</div>`;
  }
}
