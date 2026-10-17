// Confidence breakdown + quality scorecard + verifier details.
import { esc } from "../api.js";

export function renderQuality(el, run) {
  const c = run.confidence, q = run.quality, v = run.verification;
  const bad = (v?.claims || []).filter((x) => x.kind === "sourced" && x.status !== "verified");
  const nums = (v?.numbers || []);
  el.innerHTML = `
    ${c ? `<section class="section"><h2>Confidence <small>computed from the signals below, never self-reported by the model</small></h2>
      <div class="conf-level ${c.level}">${esc(c.level)}</div>
      <div class="signals">${c.signals.map((s) => `<div class="signal"><div class="n">${esc(s.name)} <span class="lvl ${s.level}">${esc(s.level)}</span></div>
        <div class="d">${esc(s.detail)}</div></div>`).join("")}</div>
      ${c.caps.length ? `<h3>Caps applied</h3><ul class="plain small">${c.caps.map((x) => `<li>${esc(x)}</li>`).join("")}</ul>` : ""}
      ${c.raise_with.length ? `<h3>What would raise confidence</h3><ul class="plain">${c.raise_with.map((x) => `<li>${esc(x)}</li>`).join("")}</ul>
        <p class="small muted">Answer these in the enquiry coach and re-run.</p>` : ""}
    </section>` : ""}

    ${q ? `<section class="section"><h2>Quality gate <small>${q.passed}/${q.total} passed${q.repaired ? " · auto-repaired once" : ""}</small></h2>
      ${["structure", "grounding", "honesty", "usefulness"].map((cat) => `<h3>${cat[0].toUpperCase() + cat.slice(1)}</h3>
        ${q.items.filter((i) => i.category === cat).map((i) => `<div class="qitem"><span class="res ${i.status}">${i.status}</span><div>${esc(i.name)}</div>
          ${i.detail ? `<div class="detail">${esc(i.detail)}</div>` : ""}</div>`).join("")}`).join("")}
      ${q.repair_notes?.length ? `<p class="small muted">Repair fixed: ${esc(q.repair_notes.join(", "))}</p>` : ""}
    </section>` : ""}

    ${v ? `<section class="section"><h2>Verifier <small>${v.n_verified}/${v.n_sourced} sourced claims verified on their pages</small></h2>
      ${bad.length ? `<table class="data"><thead><tr><th>Where</th><th>Status</th><th>Claim</th><th>Detail</th></tr></thead><tbody>
        ${bad.map((b) => `<tr><td>${esc(b.location)}</td><td><span class="res ${b.status === "fuzzy" ? "warn" : "fail"}">${esc(b.status)}</span></td><td>${esc(b.text)}</td><td>${esc(b.detail)}</td></tr>`).join("")}
      </tbody></table>` : `<p>Every sourced claim's quote was found on the cited page.</p>`}
      <h3>Numbers</h3>
      ${nums.length ? `<table class="data"><thead><tr><th>Number</th><th>Where</th><th>Status</th></tr></thead><tbody>
        ${nums.map((n) => `<tr><td>${esc(n.number)}</td><td>${esc(n.location)}</td><td><span class="res ${n.status === "supported" ? "pass" : "fail"}">${esc(n.status)}</span></td></tr>`).join("")}
      </tbody></table>` : `<p class="muted">The report states no numbers with units.</p>`}
      ${(v.client_facts || []).some((x) => x.status !== "verified") ? `<h3>Client facts not found in the enquiry</h3><ul class="plain">${v.client_facts.filter((x) => x.status !== "verified").map((x) => `<li>${esc(x.text)} <span class="small muted">${esc(x.detail)}</span></li>`).join("")}</ul>` : ""}
    </section>` : ""}`;
}
