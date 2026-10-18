import { esc } from "../api.js";

const LANES = {
  A: "Chemometric model for process automation",
  B: "Multi-spectral system for your R&D lab",
  C: "Low-cost spectral sensors",
};
const PRIORITY = { primary: 0, comparison: 1, conditional: 2 };
const ICONS = {
  A: '<circle cx="5" cy="6" r="2"/><circle cx="19" cy="6" r="2"/><circle cx="12" cy="18" r="2"/><path d="M7 6h10M6 8l5 8m7-8-5 8"/>',
  B: '<path d="M9 3h6m-5 0v7l-6 9a1.3 1.3 0 0 0 1 2h14a1.3 1.3 0 0 0 1-2l-6-9V3M7 15h10"/>',
  C: '<circle cx="12" cy="12" r="2"/><path d="M7 7a7 7 0 0 0 0 10m10-10a7 7 0 0 1 0 10M4 4a11 11 0 0 0 0 16M20 4a11 11 0 0 1 0 16"/>',
};

// Keep this tied to the assessed selection, including when viewing a saved run.
export function projectSystems(run) {
  const paths = Object.keys(LANES).filter((path) => (run.preferred_paths || []).includes(path));
  const recommendations = (run.report?.recommendations || [])
    .filter((rec) => Object.hasOwn(PRIORITY, rec.role))
    .sort((a, b) => PRIORITY[a.role] - PRIORITY[b.role]);
  const targets = run.requirements?.target_variables || [];
  return {
    paths,
    systems: recommendations.map((rec) => {
      const methods = rec.method_ids?.length ? rec.method_ids : [rec.method];
      const components = {
        A: {
          title: "Models",
          items: targets.length
            ? targets.map((target) => `${target} calibration`)
            : ["Target calibration"],
          output: "Process predictions",
        },
        B: {
          title: "Lab system",
          items: [...methods.map((method) => `${method} measurement channel`),
            "Sample / probe", "Acquisition + reference data"],
          output: "Spectra + reference values",
        },
        C: {
          title: "Sensor system",
          items: [...methods.map((method) => `${method} sensor`),
            "Process probe(s)", "Acquisition + control interface"],
          output: "Process monitoring",
        },
      };
      return { recommendation: rec, components };
    }),
  };
}

export function projectSetupHTML(run) {
  const { paths, systems } = projectSystems(run);
  if (!paths.length) return `<p class="muted">Select AFS paths in Customer Enquiry to build a setup.</p>`;
  if (!systems.length) return `<p class="muted">No setup proposed yet. Resolve the open assessment questions.</p>`;
  return `<div class="project-setup">
    <p class="small muted">Proposed systems · ranked by recommendation · validate in a lab trial</p>
    <div class="prototype-scroll" tabindex="0" role="region" aria-label="Project setup diagrams">
      <div class="prototype-board" style="--lane-count:${paths.length}">
        <div class="prototype-lanes">${paths.map((path) => `<div class="prototype-lane"><span class="prototype-path">Path ${path}</span><h3>${LANES[path]}</h3></div>`).join("")}</div>
        ${systems.map(({ recommendation: rec, components }, index) => `<article class="prototype-system">
          <header class="prototype-system-head"><h3>${index + 1}. ${esc(rec.method)}</h3><span class="role ${esc(rec.role)}">${esc(rec.role)}</span></header>
          <div class="prototype-cells">${paths.map((path) => {
            const component = components[path];
            return `<div class="prototype-cell"><section class="prototype-box" aria-label="System ${index + 1}, Path ${path}">
              <h4><svg class="prototype-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${ICONS[path]}</svg>${component.title}</h4><ul>${component.items.map((item) => `<li>${esc(item)}</li>`).join("")}</ul>
              <p class="prototype-output">${esc(component.output)}</p>
            </section></div>`;
          }).join("")}</div>
        </article>`).join("")}
      </div>
    </div>
  </div>`;
}
