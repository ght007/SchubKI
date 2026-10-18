# Frontend integration

## Page navigation

`frontend/index.html` groups the app's top bar and spectrum pipeline navigation in `.app-header`.
This wrapper stays sticky at the top in every run state, keeping the AFS logo/title, account controls,
view toggle, and tabs visible together. The pipeline bar no longer sticks separately only while running.
While evidence is open, the wrapper is temporarily hidden and restored when evidence closes or the user
leaves Result Assessment. The app measures the wrapper and publishes `--app-header-height`, synchronously
setting it to zero when the header hides so no empty header space is reserved.
Section scroll offsets, the right-side panel, the Reading query sidebar, and the source drawer use this
height so they remain below the pinned controls as account/status rows wrap or change. On narrow screens
the source drawer is capped to the space below the header and scrolls as one panel.

`frontend/js/components/page-navigation.js` wraps page content with a sticky sidebar on the right.
The `.page-sidebar` wrapper inherits `--page-navigation-top` from the layout, measured from the pinned header.
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

## Back/Forward navigation and resizable evidence

The persistent `#nav-back` and `#nav-forward` arrow buttons flank the tab list. `previousStep(state)`
and `nextStep(state)` select available steps from `visibleSteps(state)`, so General skips Expert-only
tabs. Each button's tooltip and accessible name identify its destination. Both are disabled while
`busy` or `reading`; a button is also disabled when no available step exists in its direction. They use
the existing tab-selection action, retaining the current enquiry, run and source selection.

`components/evidence-split.js` mounts once on `.shell` and `#evidence-divider`. When the source viewer
opens, CSS grid gives the source and assessment equal tracks with a divider between them. Each citation
selection or reopening resets the ratio to 50/50, including returning to Result Assessment with a source selected.
Pointer capture keeps dragging active outside the handle. ArrowLeft/ArrowRight adjust the split by five
percentage points, Home/End select the current bounds, and Enter or a double-click restores 50/50.
The focusable separator exposes its orientation, controlled pane, bounds and current percentage to
assistive technology. The split stays between 25% and 75%, with tighter bounds when needed to keep both
panes at least about 280px wide on smaller desktops.

Resizing changes only CSS tracks and separator metadata; it does not update application state, rebuild
the report or reload the source page. The ratio is kept only for the current opening; previous saved
`afs.evidenceSplit` values are ignored. Viewport changes temporarily constrain the applied ratio without
overwriting the current drag preference. Unrelated state updates do not reset it. The source
body scrolls independently under a fixed viewer heading. Leaving Result Assessment hides the source and
divider while retaining the selected page and scroll position. At 760px and below, the divider is hidden
and the source stacks above the report, taking up to half the viewport height. Selecting a citation on
these screens scrolls the source viewer into view, with the app header hidden.

## Reading review dialog

`frontend/index.html` owns the persistent native `dialog#reading-review`, outside the tab content.
After `actions.understand` succeeds, `renderConfirm()` opens it with `showModal()` and focuses
`#reading-confirm-title`. The background becomes inert and stops scrolling. Pending or failed reading
requests do not open the dialog or append a review panel to Customer Enquiry.

The reading and follow-up questions scroll in `.cf-dialog-body`. The footer keeps **Yes, assess** visible
on desktop and mobile. It includes any answers given and preserves rejected readings; questions may be
left unanswered. Escape or the close button calls `actions.closeConfirm()` and
returns focus to the enquiry field without assessing. Starting a run closes the dialog.

The dialog stays mounted across page updates. Text input does not redraw it; choice and correction
updates preserve keyboard focus, scroll position, answers, and expanded disclosures. The dialog footer
contains only **Yes, assess**. Each new enquiry assessment goes through this dialog. Both preference
checkboxes and the `confirm` state have been removed; legacy `afs.confirm=off` browser preferences are
ignored. The enquiry button stays **Check and assess**. Path and pre-check follow-up answers are collected
inside the dialog. Page navigation links to the enquiry form, rather than into the modal.
The existing submission, optional-question, reading-correction, and backend contracts are unchanged.

## General and Expert processing

`pipeline-steps.js` defines all five tabs; `visibleSteps(state)` excludes Process Information and Coach in General
using their `expertOnly` flag. `canOpenStep` also rejects these tabs in General.
`normalizeTab(id, view)` handles stored legacy tab names and maps Expert-only tabs to Confidence and
Verification in General, including a stored Coach/what-if tab or switching away from an open Coach page.
The spectrum line derives its columns, endpoint positions, colors, and progress from the visible steps.

- General: three tabs (Customer Enquiry, Result Assessment, Confidence and Verification) and a temporary
  `renderLoadingFlow` screen containing only the simple stage flow. No process-detail or Coach markup is rendered.
  A successful run opens Result Assessment. If a what-if starts in Expert and switches to General while busy,
  completion opens Confidence and Verification instead of the hidden Coach tab.
- Expert: five tabs, including **Coach** and `process` labeled **Process Information**. Starting a run selects Process Information.
  `renderProcessInformation` renders live stage outputs and the completed record. It remains selected when
  processing finishes, and is available whenever a run or partial failed run exists.
- While busy, only Expert's process tab is available; other navigation remains locked until the stream ends.
  A final result event alone does not unlock it. After failure, Reading and Expert's process record are
  available, while result tabs remain locked.
- `#run-stop` is visible during processing in both views and aborts the active stream's `AbortController`.
  It becomes disabled while stopping and disappears after cancellation, failure or the final result.
  Cancelled callbacks are ignored; the enquiry, answers and partial process record remain available.
  The UI reports a stopped assessment rather than a connection error and allows a fresh review and retry.
  The SSE generator sets a per-request cancellation event on disconnect. Queued workers abandon their
  slot request; active workers check cancellation at stage boundaries, before saving, and before model
  attempts. Retry waits are interruptible, and cancellation bypasses error fallback and history recording.
  An already running synchronous model request may finish before its worker releases the semaphore slot;
  no later model calls or stages start for that cancelled request. Sync API calls are unaffected.
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
The merged backend adds `run.outline` to stream results and saved runs, and shares its section ordering
with the Markdown export. Existing report and process fields remain available.

## Data retention

Remove frontend sections only when requested; preserve their underlying backend data.
A field being hidden or unused in the UI does not authorize removing it from the backend schema,
pipeline output, API response, stored run, or export. This includes requirements, rule hits, method scores,
spectral and fiber coverage, retrieval, evidence, premises, paths, reports, verification, quality, confidence,
coaching, council records, traces, timings, and what-if differences.

The current result outline intentionally leaves some generated data unused. Keep the backend data and the
original report/summary renderers available for future integration. The outline slots present the backend's
additive `run.outline` format without removing the original report fields.

The removed requirements, rules, retrieval, premise, and spectral-map panels leave their data in
`run.requirements`, `rule_hits`, `matrix`, `spectral`, `coverage`, `retrieval`, `evidence`, and `premises`.
Legacy renderers remain in the frontend for future integration. No backend field, stream payload,
saved run, or Markdown export is deleted or rewritten by this visibility change.

## Result Assessment outline

`frontend/js/components/assessment-outline.js` owns the new result outline. General and Expert show the same
11 sections from `run.outline`, in the order below. Sections show placeholders before the outline is available.
The sticky right-side navigation builds its contents links from their
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
| `decision_basis` | Decision basis |
| `sources` | Sources |
| `first_feasibility_experiment_prototype` | First feasibility experiment |

Each section has `data-assessment-field="<slot>"`, a heading ID `assessment-<slot-with-hyphens>`, and a content
container with that ID plus `-content`. Keys and ordering match `backend/app/render/outline.py`, which builds
the outline from the existing assessment data. The presenter accepts the run payload and renders its outline
without inventing claims. Grounded statements reuse the citation/source drawer components and show quotes.
The proposed setup diagrams from `project-setup.js` appear in a separate Setup Overview after the 11 sections.
Feasibility steps use the list's own numbering. The page and Markdown export remove an existing numeric
step prefix (including an escaped Markdown period) when rendering; saved step text stays unchanged.

`pipeline.js` shows the outline after the report stage completes and keeps the Markdown download available
above and below it. Saved runs without an outline show placeholders. Existing report/summary renderers remain intact.
Confidence and Verification, Coach, Reading, and processing behavior continue using their existing data.

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
