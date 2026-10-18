// SVG band / method / fiber coverage map on a log wavelength axis (0.18-20 um).
import { esc } from "../api.js";

const LO = 0.18, HI = 20, W = 980, L = 250, R = 70;
const x = (um) => L + ((Math.log10(um) - Math.log10(LO)) / (Math.log10(HI) - Math.log10(LO))) * (W - L - R);
const TICKS = [0.2, 0.4, 0.7, 1, 1.5, 2.5, 4, 6, 10, 16];

export function renderSpectral(el, run) {
  const sp = run.spectral || {};
  const verdict = Object.fromEntries(run.matrix.map((m) => [m.method_id, m.verdict]));
  const leadIds = run.matrix.filter((m) => m.verdict === "lead").map((m) => m.method_id);
  const blocked = (run.coverage || []).filter((c) => c.asset_check);
  const rows = [];
  let y = 64;
  const row = (label, sub, lo, hi, cls, note = "") => {
    const x1 = x(Math.max(lo, LO)), x2 = x(Math.min(hi, HI));
    rows.push(`<g><text class="lbl" x="8" y="${y + 12}">${esc(label)}</text>${sub ? `<text x="8" y="${y + 25}">${esc(sub)}</text>` : ""}
      <rect x="${x1}" y="${y}" width="${Math.max(3, x2 - x1)}" height="16" rx="3" ${cls}/>
      ${note ? `<text x="${x2 + 6}" y="${y + 12}" style="fill:var(--block)">${esc(note)}</text>` : ""}</g>`);
    y += sub ? 34 : 26;
  };

  rows.push(`<text class="lbl" x="8" y="${y - 6}" style="font-weight:600">Bands linked to this enquiry</text>`);
  y += 6;
  if ((sp.bands || []).length) {
    for (const b of sp.bands) row(b.matched.join(", "), `${b.source} p.${b.page}`, b.range_um[0], b.range_um[1], `fill="#eab308" fill-opacity=".55"`);
  } else {
    rows.push(`<text x="8" y="${y + 12}">No mapped band for the named target (ask for the analyte).</text>`); y += 26;
  }
  y += 10;
  rows.push(`<text class="lbl" x="8" y="${y - 2}" style="font-weight:600">Methods (nominal ranges)</text>`); y += 8;
  for (const m of sp.methods || []) {
    const v = verdict[m.id];
    const style = v === "lead" ? `fill="var(--core)"` : v === "not_supported" ? `fill="var(--block)" fill-opacity=".35"` : `fill="var(--graphite)" fill-opacity=".3"`;
    row(m.name.replace(" (ATR fiber probe)", " (ATR)").replace(" (fluorimetry)", ""), m.source, m.range_um[0], m.range_um[1], style);
  }
  y += 10;
  rows.push(`<text class="lbl" x="8" y="${y - 2}" style="font-weight:600">Fibers (S02 p.6)</text>`); y += 8;
  for (const f of sp.fibers || []) {
    const isSilica = f.family === "silica";
    const flag = sp.client_silica && isSilica && blocked.length;
    const style = flag ? `fill="var(--block)" fill-opacity=".25" stroke="var(--block)" stroke-width="1.5"`
      : f.family === "chalcogenide" || f.family === "polycrystalline" ? `fill="#7c3aed" fill-opacity=".45"` : `fill="var(--graphite)" fill-opacity=".25"`;
    row(f.name.replace(/ \(.*\)$/, ""), "", f.range_um[0], f.range_um[1], style, flag ? "client's link" : "");
  }
  const H = y + 20;
  const silicaLine = sp.client_silica ? `<line x1="${x(2.4)}" x2="${x(2.4)}" y1="40" y2="${H - 10}" stroke="var(--block)" stroke-dasharray="4 4"/>
    <text x="${x(2.4) + 4}" y="${H - 12}" style="fill:var(--block)">silica limit ~2.4 µm</text>` : "";

  el.innerHTML = `
    ${blocked.map((b) => `<div class="alert block">${esc(b.asset_check)}</div>`).join("")}
    <section class="section"><h2 id="spectral-coverage-map" data-page-toc>Spectral coverage map <small>wavelength in µm, log scale</small></h2>
      <p class="map-note">Where the analyte absorbs, what each method covers, and which fibers can carry that light to the probe.
      ${leadIds.length ? `Lead method${leadIds.length > 1 ? "s" : ""} highlighted.` : ""} Nominal ranges, not the usable range of a specific instrument or probe.</p>
      <svg class="specmap" viewBox="0 0 ${W} ${H}" role="img" aria-label="Spectral coverage map">
        <defs><linearGradient id="vis" x1="0" x2="1">
          <stop offset="0" stop-color="#6d28d9"/><stop offset=".2" stop-color="#2563eb"/><stop offset=".45" stop-color="#16a34a"/>
          <stop offset=".65" stop-color="#eab308"/><stop offset=".85" stop-color="#ea580c"/><stop offset="1" stop-color="#dc2626"/></linearGradient></defs>
        <rect x="${x(0.18)}" y="12" width="${x(0.4) - x(0.18)}" height="14" fill="#6d28d9" fill-opacity=".25"/>
        <rect x="${x(0.4)}" y="12" width="${x(0.74) - x(0.4)}" height="14" fill="url(#vis)"/>
        <rect x="${x(0.74)}" y="12" width="${x(2.5) - x(0.74)}" height="14" fill="#991b1b" fill-opacity=".35"/>
        <rect x="${x(2.5)}" y="12" width="${x(20) - x(2.5)}" height="14" fill="#7f1d1d" fill-opacity=".2"/>
        <text x="${x(0.25)}" y="40">UV</text><text x="${x(0.5)}" y="40">VIS</text><text x="${x(1.2)}" y="40">NIR</text><text x="${x(6)}" y="40">MIR</text>
        ${TICKS.map((t) => `<line class="grid" x1="${x(t)}" x2="${x(t)}" y1="44" y2="${H - 10}"/><text x="${x(t) - 8}" y="${H}">${t}</text>`).join("")}
        ${silicaLine}
        ${rows.join("")}
      </svg>
    </section>`;
}