import { esc } from "../api.js";

const LANES = {
  A: "Chemometric model for process automation",
  B: "Multi-spectral system for your R&D lab",
  C: "Low-cost spectral sensors",
};
const PRIORITY = { primary: 0, comparison: 1, conditional: 2 };

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
  const heading = `<h2>Project setup prototype</h2>`;
  if (!paths.length) return `<section class="section project-setup">${heading}
    <p class="muted">Select AFS paths in Reading to build a setup.</p></section>`;
  if (!systems.length) return `<section class="section project-setup">${heading}
    <p class="muted">No setup proposed yet. Resolve the open assessment questions.</p></section>`;
  return `<section class="section project-setup">${heading}
    <p class="small muted">Proposed systems · ranked by recommendation · validate in a lab trial</p>
    <div class="prototype-scroll" tabindex="0" role="region" aria-label="Project setup diagrams">
      <div class="prototype-board" style="--lane-count:${paths.length}">
        <div class="prototype-lanes">${paths.map((path) => `<div class="prototype-lane"><span class="prototype-path">Path ${path}</span><h3>${LANES[path]}</h3></div>`).join("")}</div>
        ${systems.map(({ recommendation: rec, components }, index) => `<article class="prototype-system">
          <header class="prototype-system-head"><h3>${index + 1}. ${esc(rec.method)}</h3><span class="role ${esc(rec.role)}">${esc(rec.role)}</span></header>
          <div class="prototype-cells">${paths.map((path) => {
            const component = components[path];
            return `<div class="prototype-cell"><section class="prototype-box" aria-label="System ${index + 1}, Path ${path}">
              <h4>${component.title}</h4><ul>${component.items.map((item) => `<li>${esc(item)}</li>`).join("")}</ul>
              <p class="prototype-output">${esc(component.output)}</p>
            </section></div>`;
          }).join("")}</div>
        </article>`).join("")}
      </div>
    </div>
  </section>`;
}
