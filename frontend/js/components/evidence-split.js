// Resize the source/report split without re-rendering either pane or reloading the PDF page.
export function mountEvidenceSplit(shell, divider) {
  const compact = window.matchMedia("(max-width: 760px)");
  let preferred = 50;
  let open = false;
  let pointer = null;

  function geometry() {
    const style = getComputedStyle(shell);
    const left = parseFloat(style.paddingLeft);
    const width = shell.clientWidth - left - parseFloat(style.paddingRight) - divider.offsetWidth;
    // Keep both panes readable on smaller laptops as well as at either end of the drag range.
    const minimum = Math.min(45, Math.max(25, Math.ceil(280 / Math.max(width, 1) * 100)));
    return { left: shell.getBoundingClientRect().left + left, width, minimum, maximum: 100 - minimum };
  }

  function apply() {
    if (!open || compact.matches) return preferred;
    const { minimum, maximum } = geometry();
    const value = Math.max(minimum, Math.min(maximum, preferred));
    shell.style.setProperty("--evidence-track", `${value}fr`);
    shell.style.setProperty("--assessment-track", `${100 - value}fr`);
    divider.setAttribute("aria-valuemin", String(minimum));
    divider.setAttribute("aria-valuemax", String(maximum));
    divider.setAttribute("aria-valuenow", String(Math.round(value)));
    divider.setAttribute("aria-valuetext", `Evidence ${Math.round(value)}%, assessment ${Math.round(100 - value)}%`);
    return value;
  }

  function resize(value) {
    const { minimum, maximum } = geometry();
    preferred = Math.max(minimum, Math.min(maximum, value));
    apply();
  }

  function finish(event) {
    if (pointer === null || event && event.pointerId !== pointer) return;
    const id = pointer;
    pointer = null;
    shell.classList.remove("resizing-evidence");
    if (divider.hasPointerCapture(id)) divider.releasePointerCapture(id);
  }

  divider.addEventListener("pointerdown", (event) => {
    if (event.button !== 0 || !open || compact.matches || pointer !== null) return;
    event.preventDefault();
    pointer = event.pointerId;
    divider.focus({ preventScroll: true });
    divider.setPointerCapture(pointer);
    shell.classList.add("resizing-evidence");
  });
  divider.addEventListener("pointermove", (event) => {
    if (event.pointerId !== pointer) return;
    const { left, width } = geometry();
    resize((event.clientX - left - divider.offsetWidth / 2) / width * 100);
  });
  divider.addEventListener("pointerup", finish);
  divider.addEventListener("pointercancel", finish);
  divider.addEventListener("lostpointercapture", finish);
  divider.addEventListener("dblclick", () => resize(50));
  divider.addEventListener("keydown", (event) => {
    if (!open || compact.matches) return;
    const { minimum, maximum } = geometry();
    const value = apply();
    const next = { ArrowLeft: value - 5, ArrowRight: value + 5, Home: minimum, End: maximum, Enter: 50 }[event.key];
    if (next === undefined) return;
    event.preventDefault();
    resize(next);
  });

  function update(visible = open, reset = false) {
    if (visible && (!open || reset)) {
      finish();
      preferred = 50;
    }
    open = visible;
    divider.hidden = !open || compact.matches;
    if (divider.hidden) finish();
    else apply();
  }
  compact.addEventListener("change", () => update());
  new ResizeObserver(() => apply()).observe(shell);
  return { update };
}
