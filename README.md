# KYC Workshop App

A deliberately-simple Know-Your-Customer console used as a playground for Claude Code trainings. This is not a production app: no external APIs, no database, no auth.

## Stack

- **Frontend:** Vue 3 + Vite + TypeScript + Pinia + Vue Router + Chart.js (port **3000**)
- **Backend:** Python FastAPI + Uvicorn + Pydantic v2 (port **8001**)
- **Data:** In-memory store, seeded with ~120 mock applications on startup

## Features

- **Applicant onboarding** — 4-step form (identity, address, document, confirmation) with optional file upload.
- **Risk scoring** — rule-based, using country/nationality watchlists, PEP flag, and age. Exposed as weighted factors.
- **Sanctions screening** — token-overlap match against a mock OFAC/EU/UN watchlist; can be re-run from the UI.
- **Liveness check** — fake challenge-response, deterministic per applicant email (so demos are reproducible).
- **Document OCR (stub)** — server returns fake extracted fields matching the applicant record.
- **Reviewer dashboard** — headline cards, status / risk / submissions charts, filterable queue.
- **Analytics page** — review funnel, top risk factors, top countries, liveness confidence histogram, reviewer leaderboard.
- **Application detail** — risk, sanctions, liveness, documents, and approve/reject with note.
- **Audit log** — every state-changing action is recorded; viewable globally or per application.

## Project layout

```
backend/
  requirements.txt
  requirements-dev.txt
  pytest.ini
  app/
    main.py             create_app() factory + CORS + lifespan + exception handlers
    models.py           Pydantic schemas (inputs, results, stats)
    errors.py           Domain exceptions (ApplicationNotFound, ApplicationAlreadyDecided)
    utils.py            utcnow() helper
    store.py            In-memory application store
    audit.py            In-memory audit log
    mock_data.py        Seed data — 12 anchor cases + 40 bulk + 70 extra = ~122 applicants
    domain/             Pure domain logic (no HTTP / storage)
      risk.py
      sanctions.py
      liveness.py
    services/           Orchestration — called by the API layer
      applications.py
      stats.py
    api/                Thin HTTP adapters, one router per resource
      health.py
      applications.py
      audit.py
      stats.py
  tests/
    conftest.py, test_risk.py, test_sanctions.py, test_liveness.py,
    test_api_applications.py, test_api_audit.py, test_api_stats.py

frontend/
  package.json, vite.config.ts, tsconfig.json
  src/
    main.ts, App.vue, router.ts, api.ts, types.ts, styles.css, charts.ts
    views/
      OnboardingView, DashboardView, AnalyticsView, ApplicationDetailView, AuditView
    components/
      StatusBadge, RiskPanel, SanctionsPanel, LivenessPanel, DocumentsPanel
      charts/
        StatusBreakdownBar, RiskDonut, SubmissionsSparkline,
        FunnelBar, TopFactorsBar, TopCountriesBar,
        LivenessHistogram, ReviewerLeaderboard
```

## API

```
GET    /api/health
GET    /api/applications?status=&risk=&q=
POST   /api/applications                      body: ApplicantInput
GET    /api/applications/{id}
POST   /api/applications/{id}/documents       multipart: file, doc_type
POST   /api/applications/{id}/liveness        multipart: file (optional)
POST   /api/applications/{id}/sanctions       re-runs screening
POST   /api/applications/{id}/decision        body: { outcome, reviewer, note }
GET    /api/audit?application_id=
GET    /api/stats                             aggregates for dashboard + analytics
```

Full Swagger UI: http://localhost:8001/docs.

## Running

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000. Vite proxies `/api/*` to the FastAPI server on 8001.

### Tests

```bash
cd backend
pip install -r requirements-dev.txt
pytest
```

31 tests covering the domain modules (risk, sanctions, liveness), the HTTP API (create/list/get, document upload, liveness, sanctions rerun, decision flow, 404/409 error paths, audit log), and the stats endpoint.

## Seed data

On startup the backend seeds ~120 applications across all statuses and risk levels, spread over ~60 days so the submissions sparkline and analytics charts have shape. Restarting the backend resets the in-memory store.

Interesting seeded profiles:

- **Dmitri Ivanov** — Russian applicant flagged as PEP; medium/high risk.
- **Hassan Karimi** — residence in Iran, rejected with reviewer note.
- **Ivan Volkov** — exact match on the fake OFAC watchlist entry; sanctions hit.
- **Chen Wei / Maria Delacroix** — partial-name matches on the UK HMT / EU mock lists.
- **Alice Martin / Emma Johnson / Jiro Tanaka** — clean low-risk files already approved.

## Workshop hooks

Because every piece is small and stubbed, there are many natural exercises:

- Add a new risk factor (e.g., mismatched nationality vs. document country) in `domain/risk.py`.
- Swap the mock sanctions list for a CSV import.
- Add reviewer authentication / roles.
- Extend the pytest suite with new scenarios (sanctions edge cases, senior age buckets, reviewer permission checks).
- Add E2E tests with Playwright driving the onboarding flow.
- Add a new chart to the Analytics page (e.g., time-to-decision by risk tier).

## Not implemented on purpose

- Real sanctions APIs (OpenSanctions, OFAC feeds) — they require accounts or bulk downloads.
- File persistence — uploaded bytes are inspected for size but not stored.
- Authentication — the `reviewer` field is freely editable in the UI.
- Encryption / PII redaction — this is a training app, do not put real data in it.
