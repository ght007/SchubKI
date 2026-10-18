// Knowledge-base editor page (/kb). All checks, versions, rebuilds and publishing happen on the server
// (/api/kb/*, backend/app/kb/files.py); this page edits text, shows the check results and a diff, uploads
// documents and polls the rebuild status.
import { esc, getJSON, postJSON } from "./api.js";

const $ = (id) => document.getElementById(id);
const state = { files: null, current: null, original: "", sha: "", dirty: false, polling: null };

async function send(method, url, body) {
  const r = await fetch(url, { method, headers: { "content-type": "application/json" }, body: JSON.stringify(body) });
  const data = await r.json().catch(() => ({}));
  if (!r.ok) throw Object.assign(new Error(data.detail?.message || data.detail || r.statusText), { status: r.status, detail: data.detail });
  return data;
}

function fmtSize(n) { return n > 1048576 ? `${(n / 1048576).toFixed(1)} MB` : n > 1024 ? `${Math.round(n / 1024)} KB` : `${n} B`; }

// ------------------------------------------------------------------ status bar
function showStatus(s) {
  const el = $("kb-status");
  if (!s || s.state === "idle") { el.hidden = true; return; }
  el.hidden = false;
  el.className = `kb-status ${s.state}`;
  const busy = s.state === "running" || s.state === "publishing";
  el.innerHTML = `${busy ? '<span class="kb-spinner" aria-hidden="true"></span>' : ""}<b>${esc(s.message || s.state)}</b>
    ${s.reason ? `<span class="muted"> · ${esc(s.reason)}</span>` : ""}${s.finished ? `<span class="muted"> · ${esc(s.finished.replace("T", " "))}</span>` : ""}`;
}

function pollStatus() {
  clearInterval(state.polling);
  state.polling = setInterval(async () => {
    try {
      const s = await getJSON("/api/kb/status");
      showStatus(s);
      if (!["running", "publishing"].includes(s.state) && !s.queued) { clearInterval(state.polling); loadList(); }
    } catch (_) { clearInterval(state.polling); }
  }, 1500);
}

// ------------------------------------------------------------------ file list
async function loadList() {
  try {
    state.files = await getJSON("/api/kb/files");
  } catch (err) {
    const status = Number(String(err.message).slice(0, 3));
    $("kb-work").innerHTML = `<div class="kb-empty"><h1>Knowledge base</h1>
      <p>${status === 401 ? `Log in to edit the knowledge base. <a href="/login?next=/kb">Log in</a>` :
        status === 403 ? `Editing the knowledge base is part of the Pro plan. <a href="/pricing?upgrade=expert">See plans</a>` :
        esc(err.message)}</p></div>`;
    document.querySelector(".kb-side").hidden = true;
    return;
  }
  const cur = state.current;
  $("kb-files").innerHTML = state.files.kb.map((f) => `<li><button type="button" data-area="kb" data-name="${esc(f.name)}"
    aria-current="${cur?.area === "kb" && cur?.name === f.name}"><b>${esc(f.name)}</b>
    <span class="small muted">v${f.version}${f.updated ? ` · ${esc(f.author)} · ${esc(f.updated.slice(0, 16).replace("T", " "))}` : " · as shipped"}</span></button></li>`).join("");
  $("kb-docs").innerHTML = state.files.raw.map((f) => `<li><button type="button" data-area="raw" data-name="${esc(f.name)}"
    aria-current="${cur?.area === "raw" && cur?.name === f.name}"><b>${esc(f.source_id || "not registered")}</b>
    <span class="small ${f.registered ? "muted" : "kb-warn-text"}">${esc(f.name)} · ${fmtSize(f.size)}</span></button></li>`).join("");
  document.querySelectorAll(".kb-list [data-name]").forEach((b) => (b.onclick = () => open(b.dataset.area, b.dataset.name)));
  showStatus(state.files.rebuild);
  if (["running", "publishing"].includes(state.files.rebuild?.state)) pollStatus();
}

function confirmLeave() {
  return !state.dirty || confirm("You have unsaved changes. Discard them?");
}
window.addEventListener("beforeunload", (e) => { if (state.dirty) { e.preventDefault(); e.returnValue = ""; } });

// ------------------------------------------------------------------ text files
async function open(area, name) {
  if (!confirmLeave()) return;
  state.current = { area, name };
  state.dirty = false;
  loadList();
  if (area === "raw") return openDoc(name);
  const f = await getJSON(`/api/kb/files/kb/${encodeURIComponent(name)}`);
  const about = state.files.kb.find((x) => x.name === name)?.about || "";
  state.original = f.text;
  state.sha = f.sha;
  $("kb-work").innerHTML = `<div class="kb-head"><div><h1>${esc(name)}</h1><p class="muted small">${esc(about)}</p></div></div>
    <textarea id="kb-text" class="kb-text" spellcheck="false" aria-label="${esc(name)}">${esc(f.text)}</textarea>
    <div class="kb-actions">
      <input type="text" id="kb-comment" placeholder="What did you change? (shown in the history)" aria-label="Change note">
      <button type="button" class="btn" id="kb-check">Check changes</button>
      <button type="button" class="btn primary" id="kb-save" disabled>Save and rebuild</button>
    </div>
    <div id="kb-result" class="kb-result"></div>
    <details class="kb-history" id="kb-history"><summary>Version history</summary><div>Loading…</div></details>`;
  const ta = $("kb-text");
  ta.oninput = () => { state.dirty = ta.value !== state.original; $("kb-save").disabled = true; $("kb-result").innerHTML = ""; };
  ta.onkeydown = (e) => { if (e.key === "Tab") { e.preventDefault(); ta.setRangeText("  ", ta.selectionStart, ta.selectionEnd, "end"); ta.oninput(); } };
  $("kb-check").onclick = () => check(name);
  $("kb-save").onclick = () => save(name);
  $("kb-history").ontoggle = (e) => { if (e.target.open) history("kb", name); };
}

async function check(name) {
  const text = $("kb-text").value;
  const r = await postJSON(`/api/kb/files/kb/${encodeURIComponent(name)}/preview`, { text });
  $("kb-result").innerHTML = resultHTML(r);
  $("kb-save").disabled = !r.ok || !r.changed;
}

function resultHTML(r) {
  if (!r.changed) return `<p class="muted small">No changes.</p>`;
  return `${r.problems.length ? `<div class="kb-problems"><b>Cannot be saved (${r.problems.length})</b><ul>${r.problems.map((p) => `<li>${esc(p)}</li>`).join("")}</ul></div>`
    : `<div class="kb-ok"><b>Checks passed.</b> ${r.added} line(s) added, ${r.removed} removed.</div>`}
    ${r.warnings.length ? `<div class="kb-warnings"><b>Warnings</b><ul>${r.warnings.map((w) => `<li>${esc(w)}</li>`).join("")}</ul></div>` : ""}
    <pre class="kb-diff" aria-label="Changes">${r.diff.map((l) => `<span class="${l.startsWith("+") && !l.startsWith("+++") ? "add" : l.startsWith("-") && !l.startsWith("---") ? "del" : l.startsWith("@@") ? "hunk" : ""}">${esc(l)}</span>`).join("\n")}${r.diff_truncated ? "\n…" : ""}</pre>`;
}

async function save(name) {
  const btn = $("kb-save");
  btn.disabled = true;
  btn.textContent = "Saving…";
  try {
    const r = await send("PUT", `/api/kb/files/kb/${encodeURIComponent(name)}`,
      { text: $("kb-text").value, comment: $("kb-comment").value, base_sha: state.sha });
    state.dirty = false;
    $("kb-result").innerHTML = `<div class="kb-ok"><b>Saved as version ${r.version}.</b> The knowledge base is rebuilding; the next assessment uses it.
      ${r.warnings.length ? `<br>${r.warnings.map(esc).join("<br>")}` : ""}</div>`;
    showStatus(r.rebuild);
    pollStatus();
    const f = await getJSON(`/api/kb/files/kb/${encodeURIComponent(name)}`);
    state.original = f.text;
    state.sha = f.sha;
  } catch (err) {
    $("kb-result").innerHTML = `<div class="kb-problems"><b>${esc(err.message)}</b>${err.detail?.problems?.length ? `<ul>${err.detail.problems.map((p) => `<li>${esc(p)}</li>`).join("")}</ul>` : ""}</div>`;
  } finally {
    btn.textContent = "Save and rebuild";
  }
}

async function history(area, name) {
  const box = document.querySelector("#kb-history > div");
  const rows = await getJSON(`/api/kb/files/${area}/${encodeURIComponent(name)}/history`);
  box.innerHTML = rows.length ? `<table class="kb-table"><thead><tr><th>Version</th><th>When</th><th>Who</th><th>Note</th><th></th></tr></thead><tbody>
    ${rows.map((v, i) => `<tr><td>v${v.version}</td><td>${esc((v.created || "").replace("T", " "))}</td><td>${esc(v.author || "")}</td>
      <td>${esc(v.comment || "")}</td><td>${i === 0 ? '<span class="muted small">current</span>' : `<button type="button" class="btn" data-restore="${v.version}">Restore</button>`}</td></tr>`).join("")}
    </tbody></table>` : `<p class="muted small">No saved versions yet: this is the file as shipped.</p>`;
  box.querySelectorAll("[data-restore]").forEach((b) => (b.onclick = async () => {
    if (!confirm(`Restore ${name} to version ${b.dataset.restore}? It is saved as a new version and the knowledge base is rebuilt.`)) return;
    try {
      const r = await send("POST", `/api/kb/files/${area}/${encodeURIComponent(name)}/restore`, { version: Number(b.dataset.restore) });
      showStatus(r.rebuild);
      pollStatus();
      state.dirty = false;
      open(area, name);
    } catch (err) { alert(err.message); }
  }));
}

// ------------------------------------------------------------------ documents
function openDoc(name) {
  const f = state.files.raw.find((x) => x.name === name);
  $("kb-work").innerHTML = `<div class="kb-head"><div><h1>${esc(f.source_id || "Unregistered document")}</h1>
    <p class="muted small">${esc(f.name)} · ${fmtSize(f.size)}${f.title ? ` · ${esc(f.title)}` : ""}</p></div></div>
    ${f.registered ? `<p>This document is registered as <b>${esc(f.source_id)}</b> and searched by the assistant. To change its title or
      evidence level, edit <a href="#" data-goto="sources.json">sources.json</a>.</p>`
      : `<div class="kb-warnings"><b>Not searched yet.</b> Register the document so the assistant can find and cite it.</div>${registerForm(f.name)}`}
    <h2 class="kb-h2">Replace the file</h2>
    <p class="small muted">Upload a new version with the same name. Evidence cards that quote it are checked again on the next save.</p>
    ${uploadInput("kb-replace")}
    <details class="kb-history" id="kb-history"><summary>Version history</summary><div>Loading…</div></details>`;
  document.querySelector("[data-goto]")?.addEventListener("click", (e) => { e.preventDefault(); open("kb", "sources.json"); });
  wireUpload("kb-replace", name);
  wireRegister();
  $("kb-history").ontoggle = (e) => { if (e.target.open) history("raw", name); };
}

function uploadInput(id) {
  return `<div class="kb-upload"><input type="file" id="${id}" accept=".pdf,.docx,.txt,.md">
    <button type="button" class="btn primary" id="${id}-go" disabled>Upload</button><span class="small muted" id="${id}-msg"></span></div>`;
}

function readB64(file) {
  return new Promise((resolve, reject) => {
    const r = new FileReader();
    r.onload = () => resolve(String(r.result).split(",")[1] || "");
    r.onerror = () => reject(r.error);
    r.readAsDataURL(file);
  });
}

function wireUpload(id, fixedName = null) {
  const input = $(id), go = $(`${id}-go`), msg = $(`${id}-msg`);
  input.onchange = () => { go.disabled = !input.files.length; msg.textContent = ""; };
  go.onclick = async () => {
    const file = input.files[0];
    if (!file) return;
    if (file.size > 15 * 1048576) { msg.textContent = "The file is larger than 15 MB."; return; }
    go.disabled = true;
    msg.textContent = "Uploading…";
    try {
      const r = await send("POST", "/api/kb/upload", { filename: fixedName || file.name, content_b64: await readB64(file) });
      msg.textContent = `Uploaded (${r.pages} page${r.pages === 1 ? "" : "s"} readable).`;
      await loadList();
      if (r.registered_as) { showStatus(r.rebuild); pollStatus(); }
      state.current = { area: "raw", name: r.name };
      openDoc(r.name);
    } catch (err) {
      msg.textContent = err.message;
      go.disabled = false;
    }
  };
}

function registerForm(file) {
  const levels = state.files.evidence_levels;
  return `<form class="kb-register" id="kb-register" data-file="${esc(file)}">
    <label>Source id<input name="id" placeholder="next free id, e.g. S07"></label>
    <label class="wide">Title<input name="title" required placeholder="What the document is, e.g. 'Moisture in milk powder: lab report 2024'"></label>
    <label>Evidence level<select name="evidence_level">${levels.map((l) => `<option>${esc(l)}</option>`).join("")}</select></label>
    <label>Type<input name="type" placeholder="e.g. lab report, slides, paper"></label>
    <label class="wide">Scope<input name="scope" placeholder="What it can support, e.g. 'laboratory measurements on milk powder'"></label>
    <label class="wide">Notes<input name="notes" placeholder="Optional"></label>
    <p class="small muted wide">Evidence levels decide what a source may support: a lab demonstration, an in-vitro proof of concept
      or business material never supports a readiness claim (the verifier warns).</p>
    <div class="wide"><button type="submit" class="btn primary">Register and rebuild</button> <span class="small muted" id="kb-register-msg"></span></div>
  </form>`;
}

function wireRegister() {
  const form = $("kb-register");
  if (!form) return;
  form.onsubmit = async (e) => {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(form).entries());
    data.file = form.dataset.file;
    const msg = $("kb-register-msg");
    msg.textContent = "Registering…";
    try {
      const r = await send("POST", "/api/kb/sources", data);
      msg.textContent = `Registered (sources.json v${r.version}). Rebuilding…`;
      showStatus(r.rebuild);
      pollStatus();
      await loadList();
      openDoc(form.dataset.file);
    } catch (err) {
      msg.textContent = err.detail?.problems?.join("; ") || err.message;
    }
  };
}

$("kb-upload-open").onclick = () => {
  if (!confirmLeave()) return;
  state.current = null;
  state.dirty = false;
  loadList();
  $("kb-work").innerHTML = `<div class="kb-head"><div><h1>Upload a document</h1>
    <p class="muted small">PDF with selectable text, Word (.docx), text or Markdown, up to 15 MB. After the upload, register it so the assistant searches and cites it.</p></div></div>
    ${uploadInput("kb-new")}`;
  wireUpload("kb-new");
};

loadList();
