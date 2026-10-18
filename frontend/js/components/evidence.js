// Source drawer: highlighted document page and the cited page/line location.
import { esc, getJSON } from "../api.js";

function quoteRanges(text, quote) {
  if (!quote) return [];
  const words = quote.match(/[\p{L}\p{N}]+/gu) || [];
  const escapePattern = (word) => word.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const fullPattern = words.map(escapePattern).join("[^\\p{L}\\p{N}]{0,12}");
  if (words.length) {
    const exact = new RegExp(`(?<![\\p{L}\\p{N}])${fullPattern}(?![\\p{L}\\p{N}])`, "iu").exec(text);
    if (exact) return [[exact.index, exact.index + exact[0].length]];
  }
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
  return ranges;
}

function markQuote(text, ranges) {
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

function lineLocation(text, ranges) {
  if (!ranges.length) return "Line unavailable";
  const lines = [...new Set(ranges.flatMap(([start, stop]) => {
    const first = text.slice(0, start).split("\n").length;
    const last = text.slice(0, stop).split("\n").length;
    return Array.from({ length: last - first + 1 }, (_, i) => first + i);
  }))].sort((a, b) => a - b);
  const groups = [];
  for (const line of lines) {
    const group = groups.at(-1);
    if (group && line === group[1] + 1) group[1] = line;
    else groups.push([line, line]);
  }
  return `${lines.length === 1 ? "Line" : "Lines"} ${groups.map(([first, last]) => first === last ? first : `${first}–${last}`).join(", ")}`;
}

let latestRequest = 0;

export async function renderEvidence(el, ev, close) {
  const request = ++latestRequest;
  if (!ev) { el.innerHTML = ""; return; }
  el.innerHTML = `<div class="drawer-inner"><div class="drawer-head"><b>${esc(ev.source)} · Page ${ev.page}<span class="source-lines small" title="Line numbers in the extracted page text"></span></b>
    <button class="btn" id="close">Close</button></div><div class="drawer-body"><p class="muted">Loading the page…</p></div></div>`;
  el.querySelector("#close").onclick = close;
  try {
    const data = await getJSON(`/api/source/${encodeURIComponent(ev.source)}/${ev.page}?q=${encodeURIComponent(ev.quote || "")}`);
    if (request !== latestRequest) return;
    const meta = data.meta || {};
    const text = data.text || "";
    const ranges = quoteRanges(text, ev.quote);
    el.querySelector(".source-lines").textContent = ` · ${lineLocation(text, ranges)}`;
    const isPdf = (meta.file || "").toLowerCase().endsWith(".pdf");
    el.querySelector(".drawer-body").innerHTML = isPdf
      ? `<img alt="${esc(ev.source)} page ${ev.page}" loading="lazy"
          src="/api/source/${encodeURIComponent(ev.source)}/${ev.page}/image?q=${encodeURIComponent(data.transcribed ? "" : ev.quote || "")}">`
      : `<div class="source-document" aria-label="Source document with cited passage highlighted">${markQuote(text, ranges)}</div>`;
  } catch (e) {
    if (request !== latestRequest) return;
    el.querySelector(".drawer-body").innerHTML = `<div class="err">Could not load ${esc(ev.source)} p.${ev.page}: ${esc(e.message)}</div>`;
  }
}
