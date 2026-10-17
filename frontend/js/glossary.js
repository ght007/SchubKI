// Glossary on the client: plain-language tooltips for domain terms in report text.
import { esc, getJSON } from "./api.js";

let entries = [];
let patterns = [];

export async function loadGlossary() {
  try {
    entries = (await getJSON("/api/glossary")).filter((e) => e.category !== "vague");
    const forms = [];
    for (const e of entries) {
      // English forms only in report text; skip very short or generic aliases to avoid noise
      for (const f of [e.term, ...e.aliases]) {
        if (f.length >= 3 && /^[\x00-\x7F]+$/.test(f) && !["probe", "clear", "blend", "melt", "online", "best"].includes(f.toLowerCase())) {
          forms.push([f, e]);
        }
      }
    }
    forms.sort((a, b) => b[0].length - a[0].length);
    patterns = forms.map(([f, e]) => [new RegExp(`(?<![\\w-])${f.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}(?![\\w-])`, "i"), e]);
  } catch (_) { entries = []; patterns = []; }
}

// Escape the text, then wrap the first occurrence of each known term in <abbr title="definition (source)">.
export function annotate(text) {
  let html = esc(text);
  if (!patterns.length) return html;
  const used = new Set();
  for (const [re, e] of patterns) {
    if (used.has(e.term)) continue;
    let done = false;
    html = html.replace(new RegExp(re.source, "i"), (m, off, whole) => {
      // skip matches inside an existing tag or abbr
      const before = whole.slice(0, off);
      if (before.lastIndexOf("<") > before.lastIndexOf(">") || before.lastIndexOf("<abbr") > before.lastIndexOf("</abbr>")) return m;
      done = true;
      const src = e.source ? ` [${e.source.source} p.${e.source.page}]` : "";
      return `<abbr class="gl" title="${esc(e.definition + src)}">${m}</abbr>`;
    });
    if (done) used.add(e.term);
  }
  return html;
}
