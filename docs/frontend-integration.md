# Query sidebar and account controls

The Reading sidebar is a local enquiry-draft UI. It has no authentication, user-to-chat mapping,
conversation messages, or database integration. Login and subscription controls are app-wide placeholders.

## Saved query provider

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

## Account entry points

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
