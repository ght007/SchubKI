// Verification and quality arrive first; confidence is added when coaching finishes.
import { esc } from "../api.js";

const list = (value) => Array.isArray(value) ? value : [];

function confidenceMarkup(confidence) {
  if (!confidence) return `<div class="stage-placeholder">Confidence has not been computed yet.</div>`;
  const signals = list(confidence.signals);
  const caps = list(confidence.caps);
  const raiseWith = list(confidence.raise_with);
  return `<section class="section"><h2>Confidence <small>computed from observable signals</small></h2>
    <div class="conf-level ${esc(confidence.level)}">${esc(confidence.level)}</div>
    <div class="signals">${signals.map((signal) => `<div class="signal"><div class="n">${esc(signal.name)} <span class="lvl ${esc(signal.level)}">${esc(signal.level)}</span></div>
      <div class="d">${esc(signal.detail)}</div></div>`).join("")}</div>
    ${caps.length ? `<h3>Caps applied</h3><ul class="plain small">${caps.map((item) => `<li>${esc(item)}</li>`).join("")}</ul>` : ""}
    ${raiseWith.length ? `<h3>What would raise confidence</h3><ul class="plain">${raiseWith.map((item) => `<li>${esc(item)}</li>`).join("")}</ul>
      <p class="small muted">In Expert mode, answer these in Coach and re-run.</p>` : ""}
    ${list(confidence.per_method).length ? `<h3>Confidence by method</h3><ul class="plain small">${confidence.per_method.map((method) =>
      `<li><b>${esc(method.method_id)}</b> <span class="lvl ${esc(method.level)}">${esc(method.level)}</span> ${esc(method.detail)}</li>`).join("")}</ul>` : ""}
  </section>`;
}

function verificationMarkup(run) {
  const quality = run.quality;
  const verification = run.verification;
  if (!quality && !verification) return `<div class="stage-placeholder">Verification results are not available yet.</div>`;
  const items = list(quality?.items);
  const bad = list(verification?.claims).filter((claim) => claim.kind === "sourced" && claim.status !== "verified");
  const numbers = list(verification?.numbers);
  const badClientFacts = list(verification?.client_facts).filter((claim) => claim.status !== "verified");

  return `
    ${quality ? `<section class="section"><h2>Quality gate <small>${esc(quality.passed)}/${esc(quality.total)} passed${quality.repaired ? " · auto-repaired once" : ""}</small></h2>
      ${["structure", "grounding", "honesty", "usefulness"].map((category) => `<h3>${category[0].toUpperCase() + category.slice(1)}</h3>
        ${items.filter((item) => item.category === category).map((item) => `<div class="qitem"><span class="res ${esc(item.status)}">${esc(item.status)}</span><div>${esc(item.name)}</div>
          ${item.detail ? `<div class="detail">${esc(item.detail)}</div>` : ""}</div>`).join("")}`).join("")}
      ${list(quality.repair_notes).length ? `<p class="small muted">Repair fixed: ${esc(quality.repair_notes.join(", "))}</p>` : ""}
    </section>` : ""}

    ${verification ? `<section class="section"><h2>Verifier <small>${esc(verification.n_verified)}/${esc(verification.n_sourced)} sourced claims verified on their pages</small></h2>
      ${bad.length ? `<div class="table-scroll"><table class="data"><thead><tr><th>Where</th><th>Status</th><th>Claim</th><th>Detail</th></tr></thead><tbody>
        ${bad.map((claim) => `<tr><td>${esc(claim.location)}</td><td><span class="res ${claim.status === "fuzzy" ? "warn" : "fail"}">${esc(claim.status)}</span></td><td>${esc(claim.text)}</td><td>${esc(claim.detail)}</td></tr>`).join("")}
      </tbody></table></div>` : `<p>${Number(verification.n_sourced) ? "Every sourced claim's quote was found on the cited page." : "No sourced claims were available to verify."}</p>`}
      <h3>Numbers</h3>
      ${numbers.length ? `<div class="table-scroll"><table class="data"><thead><tr><th>Number</th><th>Where</th><th>Status</th></tr></thead><tbody>
        ${numbers.map((number) => `<tr><td>${esc(number.number)}</td><td>${esc(number.location)}</td><td><span class="res ${number.status === "supported" ? "pass" : "fail"}">${esc(number.status)}</span></td></tr>`).join("")}
      </tbody></table></div>` : `<p class="muted">The report states no numbers with units.</p>`}
      ${badClientFacts.length ? `<h3>Client facts not found in the enquiry</h3><ul class="plain">${badClientFacts.map((claim) => `<li>${esc(claim.text)} <span class="small muted">${esc(claim.detail)}</span></li>`).join("")}</ul>` : ""}
    </section>` : ""}`;
}

export function renderConfidence(el, run = {}) {
  el.innerHTML = confidenceMarkup(run.confidence);
}

export function renderVerification(el, run = {}) {
  el.innerHTML = verificationMarkup(run);
}

export function renderQuality(el, run = {}) {
  el.innerHTML = confidenceMarkup(run.confidence) + verificationMarkup(run);
}
