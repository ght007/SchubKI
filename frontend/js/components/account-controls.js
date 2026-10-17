// App-wide UI placeholders. Future auth/billing handlers can cancel the events below
// to replace the local dialogs. These controls never submit credentials or payments.
export function mountAccountControls(el, { previewExpert }) {
  el.innerHTML = `<button type="button" class="btn account-login" id="loginButton">
      <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><circle cx="10" cy="6" r="3"/><path d="M3.5 17v-1a6.5 6.5 0 0 1 13 0v1"/></svg>Log in</button>
    <button type="button" class="btn account-subscribe" id="subscribeButton">Subscribe to Expert</button>`;

  const dialog = document.createElement("dialog");
  dialog.id = "accountDialog";
  dialog.className = "account-dialog";
  dialog.setAttribute("aria-labelledby", "accountDialogTitle");
  document.body.appendChild(dialog);

  function open(kind) {
    const event = new CustomEvent(kind === "login" ? "afs:login-requested" : "afs:subscription-requested", { cancelable: true });
    if (!document.dispatchEvent(event)) return;
    dialog.innerHTML = `<div class="account-dialog-content">
      <button type="button" class="dialog-close" aria-label="Close dialog">×</button>
      <span class="account-coming-soon">Coming soon</span>
      <h2 id="accountDialogTitle">${kind === "login" ? "Log in" : "Expert subscription"}</h2>
      ${kind === "login" ? `<p>Account sign-in will be available soon.</p>
        <p class="muted">Queries you save now stay in this browser.</p>` : `<p>Subscriptions will be available soon. You can explore the current Expert view now.</p>
        <ul><li>Detailed method comparisons</li><li>Full model trace and council records</li><li>Evidence and verification details</li></ul>`}
      <div class="account-dialog-actions">
        <button type="button" class="btn" data-dismiss>${kind === "login" ? "Got it" : "Close"}</button>
        ${kind === "subscribe" ? '<button type="button" class="btn primary" id="previewExpert">Preview Expert view</button>' : ""}
      </div>
    </div>`;
    dialog.querySelector(".dialog-close").onclick = () => dialog.close();
    dialog.querySelector("[data-dismiss]").onclick = () => dialog.close();
    dialog.querySelector("#previewExpert")?.addEventListener("click", () => { dialog.close(); previewExpert(); });
    dialog.showModal();
  }

  dialog.addEventListener("click", (event) => { if (event.target === dialog) dialog.close(); });
  el.querySelector("#loginButton").onclick = () => open("login");
  el.querySelector("#subscribeButton").onclick = () => open("subscribe");
}
