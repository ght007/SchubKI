# Frontend integration

## Page navigation

`frontend/index.html` groups the app's top bar and spectrum pipeline navigation in `.app-header`.
This wrapper stays sticky at the top in every run state, keeping the AFS logo/title, account controls,
view toggle, and tabs visible together. The pipeline bar no longer sticks separately only while running.
The page-navigation resize observer measures the whole wrapper and publishes `--app-header-height`.
Section scroll offsets, the right-side panel, the Reading query sidebar, and the source drawer use this
height so they remain below the pinned controls as account/status rows wrap or change. On narrow screens
the source drawer is capped to the space below the header and scrolls as one panel.

`frontend/js/components/page-navigation.js` wraps page content with a sticky navigation panel on the right.
It owns the title, explanation, section links, and `aria-current="location"` tracking.
Page runtime and Full run badges are not rendered here. Detailed stage timings remain in Process
Information → Model calls and timing.
Reading's link list deliberately excludes the scenario loader, assessment mode, and model choice;
their form controls remain available. Other pages derive their links from content headings.
Headings inside collapsed sections can opt into navigation with `data-page-toc`.
Selecting such a link opens its parent disclosure before scrolling to the heading.
On viewports up to 1100px, or when the content area is narrower than 740px (for example beside the source
drawer), the panel uses a native popover opened by “On this page”. Section selection closes the popover.
Observers and global listeners are cleaned up when the view is rebuilt.

## Reading review handoff

When `actions.understand` finishes successfully, `focusReadingReview()` focuses and scrolls to
`#reading-confirm-title`. This happens once for the current request, after the review renders; changing
an answer or display preference does not trigger another automatic jump. Scrolling respects reduced motion.
If reading fails or the request is superseded, it does not move focus to a stale review.

`confirm.js` explains that assessment is waiting for the user's review. Its top shortcut scrolls to the
highlighted `#reading-assess-title` action block, where **Yes, assess** includes answers and **Skip questions
and assess** omits them. Neither this shortcut nor scrolling starts an assessment.
The original enquiry button becomes **Continue review ↓** and returns to the review without another request.
The right-side panel shows **Awaiting your review** and a **Start assessment** contents link marked **Next**
while the review is open. The same link and status are available in the compact “On this page” popover.
The existing submission, optional-question, reading-correction, and backend contracts are unchanged.

## General and Expert processing

`pipeline-steps.js` defines all five tabs; `visibleSteps(state)` excludes Process Information and Coach in General
using their `expertOnly` flag. `canOpenStep` also rejects these tabs in General.
`normalizeTab(id, view)` handles stored legacy tab names and maps Expert-only tabs to Confidence and
Verification in General, including a stored Coach/what-if tab or switching away from an open Coach page.
The spectrum line derives its columns, endpoint positions, colors, and progress from the visible steps.

- General: three tabs (Reading, Result Assessment, Confidence and Verification) and a temporary
  `renderLoadingFlow` screen containing only the simple stage flow. No process-detail or Coach markup is rendered.
  A successful run opens Result Assessment. If a what-if starts in Expert and switches to General while busy,
  completion opens Confidence and Verification instead of the hidden Coach tab.
- Expert: five tabs, including **Coach** and `process` labeled **Process Information**. Starting a run selects Process Information.
  `renderProcessInformation` renders live stage outputs and the completed record. It remains selected when
  processing finishes, and is available whenever a run or partial failed run exists.
- While busy, only Expert's process tab is available; other navigation remains locked until the stream ends.
  A final result event alone does not unlock it. After failure, Reading and Expert's process record are
  available, while result tabs remain locked.
- Switching display mode during calculation immediately switches between the simple flow and the expert
  record, using the same in-memory run. It neither restarts nor changes the backend request.
  The coaching stage still runs in both modes to compute confidence. General maps its active navigation
  marker to Confidence and Verification; progress remains below 100% until the stream ends.
- Confidence and Verification contains evaluation outputs only. Process Information shows live activity,
  the seven calculation stages, model calls, stage timings, and council records. The requirements,
  rule/method-screening, evidence-retrieval, customer-premise, and spectral-map panels are not mounted
  in this view or included in its contents links. Retrieval queries and ranking details are also omitted
  from the trace UI.
  Model-call and council disclosures use stable `data-process-section` keys and heading IDs so open
  sections and contents links survive live updates.

Display mode uses main's account plan rules: Basic accounts have General, Pro accounts have both views,
and guest demo mode permits both. `actions.setView` preserves the upgrade redirect for Basic accounts;
boot normalizes stored tabs against the plan's effective view before restoring a saved run.
The existing RAG pipeline, stream payloads, saved run objects, and Markdown export are unchanged.

## Data retention

Remove frontend sections only when requested; preserve their underlying backend data.
A field being hidden or unused in the UI does not authorize removing it from the backend schema,
pipeline output, API response, stored run, or export. This includes requirements, rule hits, method scores,
spectral and fiber coverage, retrieval, evidence, premises, paths, reports, verification, quality, confidence,
coaching, council records, traces, timings, and what-if differences.

The current result outline intentionally leaves some generated data unused. Keep the backend data and the
original report/summary renderers available for future integration. The new outline slots are presentation
hooks; defining them does not migrate or replace the existing backend response format.

The removed requirements, rules, retrieval, premise, and spectral-map panels leave their data in
`run.requirements`, `rule_hits`, `matrix`, `spectral`, `coverage`, `retrieval`, `evidence`, and `premises`.
Legacy renderers remain in the frontend for future integration. No backend field, stream payload,
saved run, or Markdown export is deleted or rewritten by this visibility change.

## Result Assessment outline

`frontend/js/components/assessment-outline.js` owns the new result outline. General and Expert show the same
11 placeholder sections, in the order below. The sticky right-side navigation builds its contents links from their
headings, so section jumps and the current-section accent work without a separate navigation definition.

| Frontend slot | Heading |
| --- | --- |
| `decision_status` | Decision Status |
| `requirements_stated` | Requirements stated |
| `key_unknowns` | Key unknowns |
| `clarification_questions` | Clarification questions |
| `recommendation` | Recommendation |
| `measurement_concept` | Measurement concept |
| `spectral_range` | Spectral range |
| `risks_and_uncertainty` | Risks and uncertainty |
| `first_feasibility_experiment` | First feasibility experiment |
| `decision_basis` | Decision basis |
| `sources` | Sources |

Each section has `data-assessment-field="<slot>"`, a heading ID `assessment-<slot-with-hyphens>`, and a content
container with that ID plus `-content`. These are frontend hooks, not a new backend response contract.
When the future RAG format is agreed, add a presenter that renders its fields into these content containers.
Keep the heading IDs and section order stable. Escape plain text and reuse the existing citation/source drawer
components when adding grounded statements; external sources must display their quoted passages.

The outline intentionally accepts no run payload and does not adapt, rewrite, or manufacture values from
`run.report`, requirements, premises, or evidence. No scenario-specific example content is embedded.
`pipeline.js` shows the outline after the existing report stage completes and keeps the current report's
Markdown download available. Current run objects, API responses, saved data, prompts, retrieval, verification,
and the original `report.js` / `summary.js` components are retained. Confidence and Verification, Coach,
Reading, and processing behavior continue using their existing data.

## Query sidebar and account controls

The branch now includes main's authentication, session, account-query, run-history, pricing, and database
integration. `backend/app/auth/`, `backend/app/api/auth.py`, and the Supabase/local database code are
preserved from main. The frontend presentation changes do not replace those services.

### Saved query provider

`frontend/js/query-history.js` exports `createLocalQueryRepository()`, `createServerQueryRepository()`,
and `importLocalDrafts()`. `app.js` starts with the local provider and switches to the account provider
after `/api/auth/me` returns a signed-in user. Both implement:

- `list()` returns saved query drafts, most recent first.
- `save({ id?, enquiry, mode, modelChoice, paths, view? })` creates or updates a draft and returns it.
- `remove(id)` removes a saved draft.
- `persistent` reports whether persistent storage is available (`true` for the account provider).

The guest provider keeps the latest 50 drafts under `afs.saved-queries.v1` in localStorage. Its fields are
`id`, `title`, `enquiry`, `mode`, `modelChoice`, `paths`, and `updatedAt` (epoch milliseconds). If browser
storage is unavailable, it retains drafts in memory. Guest drafts contain no account credentials or session tokens.
The account provider uses `GET/POST /api/me/queries` and `DELETE /api/me/queries/{id}`; returned queries also
carry `view`, `lastRunId`, and `lastStatus`. The server associates them with the signed-in user. Local drafts
are imported once per account per browser, retaining the local copy. If the account store cannot be reached
during boot, the existing provider fallback keeps browser drafts available.

Reading saves a draft when the user chooses Save, checks/assesses an enquiry, or leaves a draft through
New query or another saved query. Opening a saved query restores its text and intake options without making
an assessment request. It clears the current result and its URL hash so previous results are not shown for
the restored draft. Follow-up answers are supplied again when assessing.

Assessment streams retain main's `X-AFS-View` and `X-AFS-Query-Id` headers. The server links each completed
run to the account/query, and the frontend refreshes account queries afterward to show their latest-result
links. `actions.openRun` restores a saved result from the account menu or sidebar.
For integration, review `git diff origin/main...HEAD` (the changes since the common ancestor). Merge current
main before publishing an integrated branch, retaining its backend/auth/database modules and account behavior.

### Account entry points

`frontend/js/components/account-controls.js` mounts in `#account-actions`, outside the tab content, after
account loading. The same account menu is available from the Queries sidebar. Signed-in users can view
run history, open saved results, manage plans, and log out; guests get pricing and login links. The earlier
placeholder dialogs and `afs:login-requested` / `afs:subscription-requested` events have been replaced by
main's implementation.

`/login` provides sign-in/sign-up, `/pricing` lists plans, and `/app` requires a session by default.
Basic users are sent to `/pricing?upgrade=expert` when selecting Expert. `AUTH_REQUIRED=0` restores the
open guest demo. Plans and demo checkout remain defined by `backend/app/auth/plans.py` and the billing API;
no payment provider is connected. Session cookies, account ownership, database persistence, and API access
continue to follow main's backend implementation.

## Documentation maintenance

Update both `README.md` and this integration guide with every subsequent update. Keep the descriptions of
visible sections, navigation, integration hooks, and backend data retention consistent with the implementation.
