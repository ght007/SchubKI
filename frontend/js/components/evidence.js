// Source drawer: page text with the quote marked, and the PDF page image with the passage highlighted.
import { esc, getJSON } from "../api.js";

function markQuote(text, quote) {
  if (!quote) return esc(text);
  const words = quote.match(/[\p{L}\p{N}]+/gu) || [];
  const escapePattern = (word) => word.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  let ranges = [];
  // PDF extraction may add line breaks and hyphens. Mark matching quote fragments
  // on the original page text so escaping cannot shift the highlighted offsets.
  for (const size of [...new Set([Math.min(words.length, 8), 4, 3, 2])]) {
    if (size < 2 || size > words.length) continue;
    const found = [];
    for (let start = 0; start < words.length; start += size) {
      const group = words.slice(start, start + size);
      if (group.length < 2) continue;
      const pattern = group.map(escapePattern).join("[^\\p{L}\\p{N}]{0,12}");
      const match = new RegExp(pattern, "iu").exec(text);
      if (match) found.push([match.index, match.index + match[0].length]);
    }
    if (found.length) { ranges = found.sort((a, b) => a[0] - b[0]); break; }
  }
  if (!ranges.length) return esc(text);
  let html = "", end = 0, marked = false;
  for (const [start, stop] of ranges) {
    if (start < end) continue;
    html += esc(text.slice(end, start)) + `<mark${marked ? "" : ' id="hit"'}>${esc(text.slice(start, stop))}</mark>`;
    marked = true;
    end = stop;
  }
  return html + esc(text.slice(end));
}

const STATUS_TEXT = {
  verified: "Quote found verbatim on this page.",
  fuzzy: "Quote found nearly verbatim on this page.",
  unverified: "The quote was NOT found on this page: treat this claim as unsupported.",
  scope_warning: "Quote found, but the source's scope (lab / in vitro / business) cannot support this claim.",
};
let latestRequest = 0;

export async function renderEvidence(el, ev, close) {
  const request = ++latestRequest;
  if (!ev) { el.innerHTML = ""; return; }
  el.innerHTML = `<div class="drawer-inner"><div class="drawer-head"><b>${esc(ev.source)} p.${ev.page}</b>
    <button class="btn" id="close">Close</button></div><div class="drawer-body"><p class="muted">Loading the page…</p></div></div>`;
  el.querySelector("#close").onclick = close;
  try {
    const data = await getJSON(`/api/source/${encodeURIComponent(ev.source)}/${ev.page}?q=${encodeURIComponent(ev.quote || "")}`);
    if (request !== latestRequest) return;
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
      <div class="pagetext" aria-label="Knowledge base page text with matching evidence highlighted">${markQuote(data.text, ev.quote)}</div>
      ${isPdf ? `<h3>Original page</h3><img alt="${esc(ev.source)} page ${ev.page}" loading="lazy"
        src="/api/source/${encodeURIComponent(ev.source)}/${ev.page}/image?q=${encodeURIComponent(data.transcribed ? "" : ev.quote || "")}">` : ""}`;
    const pageText = el.querySelector(".pagetext");
    const hit = pageText.querySelector("#hit");
    if (hit) pageText.scrollTop += hit.getBoundingClientRect().top - pageText.getBoundingClientRect().top - pageText.clientHeight / 2;
  } catch (e) {
    if (request !== latestRequest) return;
    el.querySelector(".drawer-body").innerHTML = `<div class="err">Could not load ${esc(ev.source)} p.${ev.page}: ${esc(e.message)}</div>`;
  }
}
