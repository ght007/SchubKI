"""Report JSON -> Markdown (outputs/ and export)."""
from __future__ import annotations

import re

from ..schemas import RunResult, Statement

KIND_TAG = {"client_fact": "client fact", "sourced": "sourced", "assumption": "assumption", "proposal": "proposal"}
STATUS = {"provisional_assessment": "Provisional assessment", "insufficient_information": "Insufficient information",
          "outside_supported_scope": "Outside the supported scope"}


def _cite(s: Statement) -> str:
    if not s.citations:
        return ""
    return " " + " ".join(f"[{c.source} p.{c.page}]" for c in s.citations)


def _stmt(s: Statement) -> str:
    return f"- {s.text}{_cite(s)} _({KIND_TAG.get(s.kind, s.kind)})_"


def _q(c: dict) -> str:
    return f"[{c['source']} p.{c['page']}]"


def _step_text(text: str) -> str:
    return re.sub(r"^\s*\d+\\?[.)]\s+", "", text, count=1)


def _st(s: dict) -> str:
    cites = " ".join(_q(c) for c in s["citations"])
    flag = "" if s["check"] in ("verified", "unchecked") or s["kind"] != "sourced" else f" ⚠ {s['check'].replace('_', ' ')}"
    return f"- {s['text']}{' ' + cites if cites else ''} _({KIND_TAG.get(s['kind'], s['kind'])}{flag})_"


def render(run: RunResult, title: str = "") -> str:
    """The assessment in the 11-section output format (same sections and order as the Result Assessment page)."""
    from .outline import build
    r = run.report
    if r is None:
        return f"# {title or 'Assessment'}\n\nNo report produced. {run.error}\n"
    o = {s["key"]: s for s in build(run)["sections"]}
    L: list[str] = [f"# {title or 'First technical assessment'}", "", f"> **Enquiry:** {run.enquiry}"]
    if run.answers:
        L += [">", "> **Answers added:** " + "; ".join(f"{k}: {v}" for k, v in run.answers.items())]
    if run.rejected:
        L += [">", "> **Readings marked as wrong by the user (treated as unknown):** " + ", ".join(run.rejected)]
    q = f"{run.quality.passed}/{run.quality.total}" if run.quality else "n/a"
    v = run.verification
    L += ["", f"**Quality checks:** {q} · **Sourced claims verified:** {f'{v.n_verified}/{v.n_sourced}' if v else 'n/a'} · "
              f"**Unsupported numbers:** {v.n_unsupported_numbers if v else 'n/a'}", ""]
    none = ["- (none)"]

    def head(n: int, key: str) -> None:
        L.append(f"## {n:02d}. {o[key]['title']}")

    d = o["decision_status"]
    head(1, "decision_status")
    conf = d["confidence"]
    L.append(f"**{d['status_label']}**" + (f" · **Confidence:** {conf['level']} (computed, not self-reported)" if conf else ""))
    L += ["", d["headline"]]
    if d["blocking"]:
        L += ["", "**Problems found in the request**"]
        L += [f"- {b['title']}: {b['text']} [{', '.join(b['sources'])}]" for b in d["blocking"]]
    if d["premises"]:
        L += ["", "**The customer's own claims, tested first**"]
        L += [f"- **{p['verdict'].replace('_', ' ')}**: \"{p['statement']}\". {p['explanation']} "
              + " ".join(_q(c) for c in p["citations"]) for p in d["premises"]]
    if conf and conf["raise_with"]:
        L += ["", "To raise confidence, answer: " + " / ".join(conf["raise_with"])]
    L.append("")

    head(2, "requirements_stated")
    L += [f"- {x}" for x in o["requirements_stated"]["items"]] or none
    L.append("")
    head(3, "key_unknowns")
    L += [f"- {x}" for x in o["key_unknowns"]["items"]] or none
    if o["key_unknowns"]["assumptions"]:
        L += ["", "**Assumptions made**"] + [f"- {x}" for x in o["key_unknowns"]["assumptions"]]
    L.append("")
    head(4, "clarification_questions")
    L += [f"{i}. **{x['question']}** _({x['impact']} impact)_. Why: {x['why']}"
          for i, x in enumerate(o["clarification_questions"]["items"], 1)] or none
    L.append("")

    head(5, "recommendation")
    for rec in o["recommendation"]["items"]:
        L += ["", f"### {rec['method']} ({rec['role'].replace('_', ' ')})"] + [_st(s) for s in rec["rationale"]]
        if rec["conditions"]:
            L.append(f"- _Applies if:_ {rec['conditions']}")
    if run.matrix:
        L += ["", "**Method screening (deterministic, from sourced rules)**", "",
              "| Method | Score | Verdict |", "|---|---|---|"]
        L += [f"| {m.name} | {m.score} | {m.verdict.replace('_', ' ')} |" for m in run.matrix]
    L.append("")
    head(6, "measurement_concept")
    L += [_st(s) for s in o["measurement_concept"]["statements"]] or none
    L.append("")
    head(7, "spectral_range")
    L += [_st(s) for s in o["spectral_range"]["statements"]] or none
    L.append("")
    head(8, "risks_and_uncertainty")
    rk = o["risks_and_uncertainty"]
    L += [_st(s) for s in rk["statements"]] or none
    if rk["confidence"]:
        L += ["", f"**Confidence: {rk['confidence']['level']}**"]
        L += [f"- {s['name']}: {s['level']} ({s['detail']})" for s in rk["confidence"]["signals"]]
        L += [f"- Cap: {c}" for c in rk["confidence"]["caps"]]
    L.append("")
    head(9, "decision_basis")
    L += [f"- {x}" for x in o["decision_basis"]["items"]] or none
    L.append("")
    head(10, "sources")
    for s in o["sources"]["items"]:
        L.append(f"- **{s['source']} p.{s['page']}**: {s['title']}" + (f" _({s['scope']})_" if s["scope"] else ""))
        L += [f"  - \"{x['quote']}\"" + ("" if x["check"] in ("verified", "unchecked") else f" ⚠ {x['check']}")
              for x in s["quotes"]]
    if not o["sources"]["items"]:
        L += none
    if v:
        bad = [c for c in v.claims if c.status not in ("verified", "fuzzy")]
        if bad:
            L += ["", "**Verifier warnings**"] + [f"- {c.location}: {c.status} {c.detail}" for c in bad]
    L.append("")

    fx = o["first_feasibility_experiment_prototype"]
    head(11, "first_feasibility_experiment_prototype")
    for name, key in (("Samples", "samples"), ("Reference measurements", "reference"), ("Comparison", "comparison")):
        L += [f"**{name}**"] + ([f"- {x}" for x in fx["plan"][key]] or none)
    if fx["plan"]["steps"]:
        L += ["**Steps**"] + [f"{i}. {_step_text(x)}" for i, x in enumerate(fx["plan"]["steps"], 1)]
    pw = fx["pathway"]
    L += ["", "**Next step with AFS**", f"- {pw['next_step']}",
          f"- Likely path: {pw['likely_path']}" + (f" - {pw['why']}" if pw["why"] else "")]
    src = lambda xs: ", ".join(f"{x['source']} p.{x['page']}" for x in xs)  # noqa: E731
    who = {"expert": "chosen by the expert", "enquiry": "asked by the customer", "both": "asked by customer and expert"}
    L += [f"- Path {f['path']} ({who[f['requested_by']]}): **{f['verdict']}**. {f['reason']} [{src(f['sources'])}]"
          for f in pw["requested"]]
    for pa in pw["proceed_anyway"]:
        L += ["", f"**If you proceed anyway with Path {pa['path']}** ({pa['caveat']})"]
        L += [f"{i}. {_step_text(x)}" for i, x in enumerate(pa["steps"], 1)] + [f"_Sources: {src(pa['sources'])}_"]
    setup = fx["setup"]
    if setup["paths"] and setup["systems"]:
        L += ["", "**Proposed setup** (ranked by recommendation; validate in a lab trial)", "",
              "| System | " + " | ".join(f"Path {p}: {setup['path_titles'][p]}" for p in setup["paths"]) + " |",
              "|---|" + "---|" * len(setup["paths"])]
        for i, sy in enumerate(setup["systems"], 1):
            cells = [f"{c['title']}: {', '.join(c['items'])} → {c['output']}" for c in sy["components"].values()]
            L.append(f"| {i}. {sy['method']} ({sy['role']}) | " + " | ".join(cells) + " |")
    elif not setup["paths"]:
        L += ["", "_Proposed setup: select AFS paths to build a setup._"]

    if run.council and run.council.drafts:
        L += ["", "## Council",
              f"Winner: draft {run.council.winner}; agreement {run.council.agreement:.0%} ({run.council.agreement_detail})"]
        L += [f"- Draft {d.letter} ({d.model}): judge score {d.judge_total}, gate failures: "
              f"{', '.join(d.gate_failures) or 'none'}" for d in run.council.drafts]
    models = sorted({t.model for t in run.trace})
    chosen = f"model chosen for every stage: {run.model_choice}" if run.model_choice else "server default models"
    L += ["", f"_Generated by AFS Fiberwise, the AFS assessment assistant (run {run.id}, mode {run.mode}, {chosen}; "
              f"models used: {', '.join(models) or '-'})._"]
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------- full export (everything the UI shows)

def _src(xs) -> str:
    return ", ".join(f"{x.source} p.{x.page}" for x in xs) or "-"


def _cell(x) -> str:
    return str(x).replace("|", "/").replace("\n", " ")


def _um(r) -> str:
    return f"{r[0]:g}-{r[1]:g} µm" if r else "-"


def render_full(run: RunResult, title: str = "") -> str:
    """The assessment, then every working layer as appendices: path analysis, extracted requirements,
    rules, method screening, spectral coverage, evidence, verification, quality, confidence, coach,
    council, what-if changes, retrieval and model trace. Used by the UI export button."""
    L: list[str] = [render(run, title).rstrip(), "", "---", "", "# Appendix: how this assessment was made", "",
                    "Contents: A Path analysis · B Extracted requirements · C Rules that fired · D Method screening · "
                    "E Spectral coverage · F Evidence retrieved · G Verification · H Quality checks · I Confidence · "
                    "J Enquiry coach · K Council · L What-if changes · M Retrieval and model trace", ""]

    # A ---------------------------------------------------------------- paths
    L.append("## A. AFS path analysis")
    if run.paths:
        p = run.paths
        L.append(f"**Suggested path:** {p.suggested}. {' '.join(p.reasons)} [{_src(p.sources)}]")
        path_answers = {k: v for k, v in run.answers.items() if k.startswith("Path ") and " - " in k}
        if path_answers:
            L.append("")
            L.append("**Answers to the path questions**")
            L += [f"- {k}: {v}" for k, v in path_answers.items()]
        if p.requested:
            L.append("")
            L.append("| Path | Requested by | Verdict | Reason | Sources |")
            L.append("|---|---|---|---|---|")
            L += [f"| {f.path} | {f.requested_by} | {f.verdict} | {_cell(f.reason)} | {_src(f.sources)} |" for f in p.requested]
    else:
        L.append("- (not computed)")
    L.append("")

    # B ---------------------------------------------------------------- requirements
    L.append("## B. Extracted requirements")
    rq = run.requirements
    if rq:
        L.append(f"**Summary:** {rq.summary}")
        L.append("")
        L.append("| Field | Value |")
        L.append("|---|---|")
        for k, v in rq.model_dump().items():
            if k in ("summary", "facts", "unknowns", "premises"):
                continue
            L.append(f"| {k.replace('_', ' ')} | {_cell(', '.join(map(str, v)) if isinstance(v, list) else v) or '-'} |")
        if rq.facts:
            L.append("")
            L.append("**Facts** (stated / inferred, with the words they come from)")
            L += [f"- {f.field}: {f.value} _({f.status})_ — \"{f.quote}\"" for f in rq.facts]
        if rq.unknowns:
            L.append("")
            L.append("**Unknowns**")
            L += [f"- {u.item} _({u.impact} impact)_: {u.why_it_matters}" for u in rq.unknowns]
        if rq.premises:
            L.append("")
            L.append("**Client premises found**")
            L += [f"- {p.id} ({p.kind.replace('_', ' ')}): \"{p.statement}\"" for p in rq.premises]
    else:
        L.append("- (not available)")
    L.append("")

    # C ---------------------------------------------------------------- rules
    L.append(f"## C. Rules that fired ({len(run.rule_hits)})")
    if run.rule_hits:
        L.append("| Severity | Rule | Finding | Sources |")
        L.append("|---|---|---|---|")
        for h in run.rule_hits:
            L.append(f"| {h.severity} | {h.rule_id}: {_cell(h.title)} | {_cell(h.text) or '-'} | {_src(h.sources)} |")
    else:
        L.append("- (none)")
    L.append("")

    # D ---------------------------------------------------------------- matrix
    L.append("## D. Method screening (deterministic)")
    if run.matrix:
        L.append("| Method | Score | Verdict | Asked for by client | Contributions |")
        L.append("|---|---|---|---|---|")
        for m in run.matrix:
            contrib = "; ".join(f"{c.delta:+d} {c.reason} ({c.rule_id})" for c in m.contributions) or "-"
            L.append(f"| {m.name} | {m.score} | {m.verdict.replace('_', ' ')} | {'yes' if m.requested_by_client else 'no'} | {_cell(contrib)} |")
    else:
        L.append("- (none)")
    L.append("")

    # E ---------------------------------------------------------------- spectral coverage
    L.append("## E. Spectral coverage (method range vs fiber transmission)")
    if run.coverage:
        L.append("| Method | Method range | Fiber | Fiber range | Overlap | Covers |")
        L.append("|---|---|---|---|---|---|")
        for c in run.coverage:
            for f in c.fibers:
                L.append(f"| {c.method_id} | {_um(c.method_range_um)} | {_cell(f.name)} | {_um(f.range_um)} | {_um(f.overlap_um)} | {f.covers} |")
        checks = [f"- {c.method_id}: {c.asset_check}" for c in run.coverage if c.asset_check]
        if checks:
            L.append("")
            L.append("**Checks against the client's existing equipment**")
            L += checks
    bands = [b for b in (run.spectral or {}).get("bands", []) if b.get("matched")]
    if bands:
        L.append("")
        L.append("**Absorption bands relevant to the targets**")
        L += [f"- {_um(b['range_um'])} ({b.get('region', '')}): {', '.join(b['matched'])} [{b.get('source')} p.{b.get('page')}]" for b in bands]
    if not run.coverage and not bands:
        L.append("- (none)")
    L.append("")

    # F ---------------------------------------------------------------- evidence
    L.append(f"## F. Evidence retrieved ({len(run.evidence)} passages; BM25 + dense, fused with RRF, diversified with MMR)")
    for e in run.evidence:
        text = e.quote or e.highlight or (e.text[:300] + ("…" if len(e.text) > 300 else ""))
        L.append(f"- **{e.ref}** [{e.source} p.{e.page}] _{e.kind}{', ' + e.scope if e.scope else ''}; RRF {e.score}_: {text}")
    if not run.evidence:
        L.append("- (none)")
    L.append("")

    # G ---------------------------------------------------------------- verification
    L.append("## G. Verification (no AI: quotes, numbers, client facts)")
    v = run.verification
    if v:
        L.append(f"Sourced claims verified: {v.n_verified}/{v.n_sourced} · unsupported numbers: {v.n_unsupported_numbers} · "
                 f"client facts not found in the enquiry: {v.n_bad_client_facts}")
        L.append("")
        if v.claims:
            L.append("| Where | Status | Claim | Citation | Detail |")
            L.append("|---|---|---|---|---|")
            for c in v.claims:
                L.append(f"| {c.location} | {c.status} | {_cell(c.text[:140])} | "
                         f"{', '.join(f'{x.source} p.{x.page}' for x in c.citations) or '-'} | {_cell(c.detail) or '-'} |")
        if v.numbers:
            L.append("")
            L.append("**Numbers**")
            L += [f"- {n.location}: {n.number}: {n.status}{' (' + n.detail + ')' if n.detail else ''}" for n in v.numbers]
        if v.client_facts:
            L.append("")
            L.append("**Client facts**")
            L += [f"- {c.location}: {c.status}: {c.text[:140]}" for c in v.client_facts]
    else:
        L.append("- (not run)")
    L.append("")

    # H ---------------------------------------------------------------- quality
    L.append("## H. Quality checks")
    qy = run.quality
    if qy:
        L.append(f"Passed {qy.passed}/{qy.total}{' · one automatic repair round was used' if qy.repaired else ''}")
        L.append("")
        L.append("| Check | Category | Status | Detail |")
        L.append("|---|---|---|---|")
        L += [f"| {i.id} {_cell(i.name)} | {i.category} | {i.status} | {_cell(i.detail) or '-'} |" for i in qy.items]
        if qy.repair_notes:
            L.append("")
            L.append("**Repair notes**")
            L += [f"- {n}" for n in qy.repair_notes]
    else:
        L.append("- (not run)")
    L.append("")

    # I ---------------------------------------------------------------- confidence
    L.append("## I. Confidence (computed from observable signals; the model never rates itself)")
    cf = run.confidence
    if cf:
        L.append(f"**Overall: {cf.level}**")
        L += [f"- Signal {s.name}: {s.level} ({s.value:.2f}): {s.detail}" for s in cf.signals]
        L += [f"- Cap: {c}" for c in cf.caps]
        L += [f"- {m.method_id}: {m.level}: {m.detail}" for m in cf.per_method]
        if cf.raise_with:
            L.append("- To raise it, answer: " + " / ".join(cf.raise_with))
    else:
        L.append("- (not computed)")
    L.append("")

    # J ---------------------------------------------------------------- coach
    L.append("## J. Enquiry coach")
    co = run.coach
    if co:
        L.append(f"Key facts present: {co.completeness}/{co.total}")
        L.append("")
        L.append("| Fact | Status | Impact | Question if missing |")
        L.append("|---|---|---|---|")
        L += [f"| {f.label} | {f.status} | {f.impact} | {_cell(f.question) if f.status != 'stated' else '-'} |" for f in co.fields]
        if co.template:
            L.append("")
            L.append("**Improved enquiry template** (fill the [blanks])")
            L.append("")
            L += ["    " + line for line in co.template.splitlines()]
    else:
        L.append("- (not available)")
    L.append("")

    # K ---------------------------------------------------------------- council
    L.append("## K. Council")
    cc = run.council
    if cc and cc.drafts:
        L.append(f"Winner: draft {cc.winner} · agreement {cc.agreement:.0%} ({cc.agreement_detail}) · model families: {cc.families}")
        if cc.merged_from:
            L.append("Merged sections: " + ", ".join(f"{k} from draft {v}" for k, v in cc.merged_from.items()))
        L.append("")
        L.append("| Draft | Model | Status | Lead methods | Gate failures | Judge score |")
        L.append("|---|---|---|---|---|---|")
        L += [f"| {d.letter} | {d.model} | {d.status or ('error: ' + d.error if not d.ok else '-')} | {', '.join(d.lead_methods) or '-'} | "
              f"{_cell(', '.join(d.gate_failures)) or 'none'} | {d.judge_total} |" for d in cc.drafts]
        for j in cc.judgements:
            L.append(f"- Judge {j.get('judge_model', '?')} picked {j.get('best', '?')}")
    else:
        L.append("- Not used (Fast mode: one model).")
    L.append("")

    # L ---------------------------------------------------------------- what-if
    L.append("## L. What-if changes")
    if run.diff:
        L.append(f"Compared with run {run.parent_run_id}:")
        L += [f"- {d.field}: {d.before} → {d.after}" for d in run.diff]
    else:
        L.append("- (this is not a what-if run)")
    L.append("")

    # M ---------------------------------------------------------------- retrieval + trace
    L.append("## M. Retrieval and model trace")
    rt = run.retrieval or {}
    if rt.get("queries"):
        L.append("**Search queries**")
        L += [f"- {q}" for q in rt["queries"]]
        L.append(f"- Passages pinned by blocking/warning rules: {len(rt.get('pinned', []))}; evidence tokens used: {rt.get('used_tokens', '-')}")
        L.append("")
    if run.trace:
        L.append("| Stage | Model | Prompt tokens | Completion tokens | Latency (ms) | Cached | OK |")
        L.append("|---|---|---|---|---|---|---|")
        L += [f"| {t.stage} | {t.model} | {t.prompt_tokens} | {t.completion_tokens} | {t.latency_ms} | {'yes' if t.cached else 'no'} | "
              f"{'yes' if t.ok else 'no: ' + _cell(t.error[:80])} |" for t in run.trace]
    if run.timings_ms:
        L.append("")
        L.append("Stage timings: " + ", ".join(f"{k} {v} ms" for k, v in run.timings_ms.items()))
    L.append("")
    return "\n".join(L) + "\n"
