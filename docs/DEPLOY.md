# Deploy: Render (backend) + Vercel (frontend)

```
browser ──► Vercel  (static frontend/, CDN)
              └─ /api/*  ──proxy──►  Render  (FastAPI, knowledge base, LLM calls)
```

The browser only talks to the Vercel domain, so the session cookie (`SameSite=Lax`) works and no CORS is
needed. The Render URL on its own also serves the complete app (fallback link for the demo).

| File | Purpose |
|---|---|
| `render.yaml` | Render Blueprint: build, start, health check, env vars |
| `frontend/vercel.json` | Vercel: page routes, `/static/*` mapping, `/api/*` proxy to Render |
| `scripts/fetch_sources.py` | Render build: downloads the S01–S05 PDFs (not in git) from `SOURCES_URL` |

## 1. Sources zip (the PDFs stay out of git)

PowerShell, in the repo root:
```powershell
Compress-Archive -Path data\raw\S01_*.pdf,data\raw\S02_*.pdf,data\raw\S03_*.pdf,data\raw\S04_*.pdf,data\raw\S05_*.pdf -DestinationPath sources.zip
```
bash:
```bash
(cd data/raw && zip ../../sources.zip S0[1-5]_*.pdf)
```
Upload `sources.zip` to a **private** Supabase Storage bucket (e.g. `build`), then use *Create signed URL*
with an expiry that covers the jury period. That URL is a secret: put it in Render only, never in git.
Do not commit `sources.zip`.

## 2. Render (backend)

1. Render → **New → Blueprint** → repo `ght007/SchubKI`, branch `feature/deploy` (later `main`).
2. Fill in the secret env vars it asks for:
   - `GROQ_API_KEY`
   - `SUPABASE_DB_URL`: the **Session pooler** URI from Supabase → Connect (the direct host is IPv6-only).
     Without it, accounts and runs live in the instance's SQLite and are lost whenever it sleeps or redeploys.
   - `SOURCES_URL`: the signed URL from step 1.
   - `GOOGLE_CLIENT_ID`: optional.
3. Wait for the deploy, then check `https://<service>.onrender.com/api/health`: `"ok": true`, `kb_records` > 0.

The build runs `fetch_sources.py`, then `python -m backend.app.kb.ingest`, so the index and the embedding
model are in place before the server starts. A missing PDF fails the build on purpose.

## 3. Vercel (frontend)

1. Vercel → **Add New → Project** → import `ght007/SchubKI`.
2. **Root Directory: `frontend`**, Framework Preset: **Other**, no build command, no output directory.
3. Settings → Git → Production Branch: `feature/deploy` (or merge to `main` first).
4. If Render gave the service a URL other than `https://schubki-api.onrender.com`, change the `/api/:path*`
   destination in `frontend/vercel.json` and push.

## 4. Google sign-in (only if `GOOGLE_CLIENT_ID` is set)

Google Cloud Console → the OAuth client → *Authorized JavaScript origins*: add the Vercel URL
(e.g. `https://schubki.vercel.app`) and the Render URL.

## Known limits

- **Free Render instance sleeps after 15 min idle**; the first request then takes about a minute.
  Open `/api/live` before a demo or before submitting the link.
- **Vercel proxy timeout**: Vercel waits up to 120 s for the first byte and then needs data at least every
  120 s. The streaming `/api/assess` sends stage events and fits; a long `/api/assess/sync` (council mode)
  may not, so use the Render URL directly for that. Eval runs (`eval.run_cases`) stay local.
- `/` on Vercel always redirects to `/login`. With `AUTH_REQUIRED=0` the login page shows "Continue as guest".
- The LLM cache and local SQLite on Render are rebuilt on every deploy (Supabase holds the durable data).
