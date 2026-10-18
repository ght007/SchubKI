# Frontend integration

## Page navigation

`frontend/js/components/page-navigation.js` wraps page content with a sticky navigation panel on the right.
It owns the title, explanation, runtime stats, section links, and `aria-current="location"` tracking.
Reading's link list deliberately excludes the scenario loader, assessment mode, and model choice;
their form controls remain available. Other pages derive their links from content headings.
On viewports up to 1100px, or when the content area is narrower than 740px (for example beside the source
drawer), the panel uses a native popover opened by “On this page”. Section selection closes the popover.
Observers and global listeners are cleaned up when the view is rebuilt.

## General and Expert processing

`pipeline-steps.js` defines all five tabs; `visibleSteps(state)` excludes Process Information in General.
`normalizeTab(id, view)` also handles stored legacy tab names without exposing the process tab in General.
The spectrum line derives its columns, endpoint positions, colors, and progress from the visible steps.

- General: four tabs and a temporary `renderLoadingFlow` screen containing only the simple stage flow.
  No process-detail markup is rendered. A successful run opens Result Assessment (Coach after a what-if).
- Expert: five tabs, with `process` labeled **Process Information**. Starting a run selects this tab.
  `renderProcessInformation` renders live stage outputs and the completed record. It remains selected when
  processing finishes, and is available whenever a run or partial failed run exists.
- While busy, only Expert's process tab is available; other navigation remains locked until the stream ends.
  A final result event alone does not unlock it. After failure, Reading and Expert's process record are
  available, while result tabs remain locked.
- Switching display mode during calculation immediately switches between the simple flow and the expert
  record, using the same in-memory run. It neither restarts nor changes the backend request.
- Confidence and Verification contains evaluation outputs only. Rule, retrieval, premise, trace, and
  council diagnostics live in Process Information. Disclosure sections use stable `data-process-section`
  keys and heading IDs so open sections and contents links survive live updates.

This distinction is a frontend presentation preference; account authorization remains separate.
The existing RAG pipeline, stream payloads, saved run objects, and Markdown export are unchanged.

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

The Reading sidebar is a local enquiry-draft UI. It has no authentication, user-to-chat mapping,
conversation messages, or database integration. Login and subscription controls are app-wide placeholders.

### Saved query provider

`frontend/js/query-history.js` exports `createLocalQueryRepository()`. `app.js` uses its asynchronous interface:

- `list()` returns saved query drafts, most recent first.
- `save({ id?, enquiry, mode, modelChoice, paths })` creates or updates a draft and returns it.
- `remove(id)` removes a saved draft.
- `persistent` reports whether the current data could be written to browser storage.

Drafts contain only `id`, `title`, `enquiry`, `mode`, `modelChoice`, `paths`, and `updatedAt` (epoch milliseconds).
These IDs identify local drafts only. No user ID, chat ID, run ID, answer history, credentials, or tokens are stored.
The provider keeps the latest 50 drafts under `afs.saved-queries.v1` in localStorage. If browser storage is
unavailable, it retains drafts in memory and the sidebar says they last for this session only.

Reading saves a draft when the user chooses Save, checks/assesses an enquiry, or leaves a draft through
New query or another saved query. Opening a saved query restores its text and intake options without making
an assessment request. It clears the current result and its URL hash so previous results are not shown for
the restored draft. Follow-up answers are supplied again when assessing.

The future per-user chat implementation can replace the repository construction in `app.js` with its own
provider. Conversation history and authentication remain the responsibility of that implementation.

### Account entry points

`frontend/js/components/account-controls.js` mounts once in `#account-actions`, outside the tab content.
The buttons dispatch cancelable events on `document`:

- `afs:login-requested`
- `afs:subscription-requested`

An integration can call `event.preventDefault()` to replace the default “Coming soon” dialog:

```js
document.addEventListener("afs:login-requested", (event) => {
  event.preventDefault();
  // Open the real authentication flow here.
});
```

The default dialogs make no network requests and collect no credentials or payment details.
“Preview Expert view” changes the existing display preference only. It grants no subscription or login state;
General/Expert remains an ungated UI toggle until the account implementation defines access rules.
