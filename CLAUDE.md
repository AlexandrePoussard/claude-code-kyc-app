# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A deliberately-simple **client-onboarding console** (branded in the UI as *Meridian Private Bank — Client Onboarding Console*) used as a teaching sandbox for Claude Code trainings. The app covers three sequential stages — KYC verification, bank account creation, relationship-manager assignment — and **it is not production software.** Everything touching the outside world is faked: no database, no auth, no real sanctions feed, no real OCR, no real liveness detection, no real account ledger. The goal is a realistic-looking but fully self-contained app that workshop participants can explore, extend, and refactor without fighting infrastructure.

The git repository is still named `claude-code-kyc-app` for historical reasons. The UI branding (bank name, headers, titles) is defined in `frontend/src/App.vue` and `frontend/index.html`.

Preserve these workshop-friendly properties unless explicitly asked otherwise:

- **No new external services.** Default to stubbing anything that would need one.
- **No persistence.** The in-memory `store` / `audit` modules are deliberate — do not introduce SQLite/Postgres/Redis.
- **Deterministic mocks.** Seeds, liveness scoring, sanctions matching, RM matching, and account-number generation must stay reproducible across restarts so demos behave the same every time.
- **Readable over clever.** Students read this code. Prefer explicit names and straightforward structures to abstractions.

See `README.md` for the product-level feature list, seeded anchor cases (Alice Martin, Emma Johnson, Jiro Tanaka, Dmitri Ivanov, Ivan Volkov, Chen Wei, etc.), and the full API surface.

## Common commands

All commands assume you are in the repo root.

```bash
# Backend — dev server on :8001 (hot-reload)
cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8001

# Frontend — dev server on :3000, proxies /api/* → :8001
cd frontend && npm run dev

# Frontend typecheck + production build
cd frontend && npm run build

# Backend tests (46 tests)
cd backend && pytest

# Single test file / single test
cd backend && pytest tests/test_risk.py
cd backend && pytest tests/test_api_onboarding.py::test_auto_assign_rm_completes_journey
cd backend && pytest tests/test_api_applications.py::test_list_applications_supports_stage_filter

# First-time setup
cd backend && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt -r requirements-dev.txt
cd frontend && npm install
```

On Python 3.9, `pip install -r requirements.txt` alone is not sufficient at runtime — FastAPI route signatures use PEP 604 `X | None` unions that need `eval_type_backport` to evaluate. If you hit `TypeError: Unable to evaluate type annotation`, either upgrade to Python 3.10+ or `pip install eval_type_backport`.

## Architecture

The backend is a **layered FastAPI app**, not a flat `main.py`. Understanding the layer boundaries matters because routing a change through the wrong layer is the most common source of friction.

```
app/api/         HTTP adapters — one router per resource, mounted under /api
app/services/    Orchestration — mutates store + writes audit entries
app/domain/      Pure functions — risk.assess, sanctions.screen, liveness.run_check,
                 relationship_managers.match / all_managers / get_by_id
app/store.py     Module-level dict of Application objects
app/audit.py     Module-level list of AuditEntry objects
app/models.py    All Pydantic schemas (inputs, domain results, stats, stages, ManagerWithLoad)
app/errors.py    Domain exceptions mapped to HTTP status in main.create_app()
app/mock_data.py seed() — called from the FastAPI lifespan hook
```

**Layer rules:**

- `api/*.py` routers are thin. They unwrap `UploadFile`/`Form` and delegate to `services.*`. They must not touch `store`, `audit`, or `domain` directly.
- `services/*` is the only layer allowed to call both `store`/`audit` and `domain`. This is where state transitions live (e.g., `PENDING → IN_REVIEW` on first document upload, `KYC → ACCOUNT_CREATION` on approval, `ACCOUNT_CREATION → RM_ASSIGNMENT` on account opening, `RM_ASSIGNMENT → COMPLETED` on RM assignment).
- `domain/*` is pure: no HTTP, no storage, no time except what the caller passes in. Unit tests in `tests/test_risk.py`, `tests/test_sanctions.py`, `tests/test_liveness.py` call these directly.
- `main.py` is just the `create_app()` factory: CORS, router mount, lifespan seeding, exception-to-HTTP mapping. New endpoints go in `api/`, not here.

**Error handling.** Services raise `ApplicationNotFound`, `ApplicationAlreadyDecided`, `StageNotReachable`, or `RelationshipManagerNotFound` from `errors.py`. `create_app()` registers exception handlers that translate these to 404 / 409. Do not raise `HTTPException` from services — it couples them to HTTP.

**Audit is coupled to mutations.** Every state-changing operation in `services/applications.py` and `services/onboarding.py` calls `audit.record(...)`. When you add a new mutating endpoint or service function, add the matching `audit.record` call — tests in `test_api_audit.py` and `test_api_onboarding.py` assume this invariant.

**Test fixtures reset state, not lifespan.** `tests/conftest.py` builds the `TestClient` directly from `create_app()` but wraps each test with a `store.clear()` / `audit.clear()` fixture. The startup `lifespan` that seeds ~122 applicants does **not** fire in tests — each test starts from an empty store and builds only what it needs via `applicant_factory` / `applicant_payload`.

## Behaviors that span layers (and are easy to break)

**Onboarding stages.** Each `Application` carries both a KYC `status` (pending / in_review / approved / rejected) *and* an onboarding `stage` (kyc / account_creation / rm_assignment / completed). Stage is the source of truth for which step the client is currently on; status only describes the KYC sub-state. Stages advance automatically on successful mutations:

| From | To | Trigger |
|---|---|---|
| `kyc` | `account_creation` | `POST /decision` with `outcome=approved` |
| `account_creation` | `rm_assignment` | `POST /account` succeeds |
| `rm_assignment` | `completed` | `POST /relationship-manager` succeeds |

Stage **gates** are enforced in `services/onboarding.py`: calling `/account` when stage ≠ `account_creation` raises `StageNotReachable` (409). Same for `/relationship-manager` when stage ≠ `rm_assignment`. Pins: `test_api_onboarding.py::test_cannot_create_account_before_approval`, `test_cannot_assign_rm_before_account_creation`.

**KYC rejection is terminal.** A rejected decision keeps `stage=kyc` forever; there is no "retry" endpoint. If you add one, document that it must bypass `ApplicationAlreadyDecided`.

**Stage filtering on the list endpoint.** `GET /api/applications?stage=X` is how the stage-specific queue views (`/kyc`, `/accounts`, `/rm`) load their data. Keep the `stage` query param wired from the API layer all the way down to `services.applications.list_applications` — `test_list_applications_supports_stage_filter` pins this.

**Application KYC lifecycle (stage 1).** `pending` → `in_review` → `approved` / `rejected`. The `pending` → `in_review` transition is implicit: it happens in `services.upload_document` on the first document. There is no direct status-setter endpoint. `approved` / `rejected` is terminal for the KYC sub-state — a second `POST /decision` raises `ApplicationAlreadyDecided` (409). `test_api_applications.py` pins this.

**Risk scoring is additive.** `domain/risk.py::assess` appends `RiskFactor(code, label, weight)` entries, sums their weights, then maps to low/medium/high via thresholds (≥50 → high, ≥20 → medium). To add a new factor, append to the `factors` list — do not rewrite the scoring model. The frontend `RiskPanel` renders whatever factors the backend returns.

**Sanctions matching is a toy.** `domain/sanctions.py` does token-overlap (≥0.5) against a 5-entry in-code `WATCHLIST`. The anchor seeds `Ivan Volkov`, `Chen Wei`, `Maria Delacroix` exist specifically to produce hits; preserve those names when editing `mock_data.py`. If asked for "real sanctions data," flag that OpenSanctions/OFAC feeds require accounts or bulk downloads, and propose a CSV-import exercise instead.

**Liveness is deterministic.** `domain/liveness.py` seeds a `random.Random` with `sha256(applicant_email)` so repeat runs return the same confidence. This is intentional for demo reproducibility — do not swap in `random.random()`. A selfie payload smaller than 100 bytes is treated as a failure (tested in `test_liveness.py`).

**Account number generation is deterministic.** `services/onboarding.py::_generate_account_number` hashes the application id and takes the first 10 digits. This means re-seeding produces identical numbers for identical applicants — desirable for demo reproducibility. Do not swap in a random generator.

**RM auto-match priorities.** `domain/relationship_managers.py::match` picks a specialization in this order:
1. High-risk profile → compliance specialist.
2. Investment account → investment specialist.
3. Medium-risk profile → wealth advisor.
4. Otherwise → retail.

Language preference (derived from country code via `_COUNTRY_LANG`) breaks ties but never overrides specialization. Manual selection via `manager_id` skips the matcher entirely; its `reason` is `"manually selected by reviewer"`. Pins: `test_api_onboarding.py::test_high_risk_profile_routes_to_compliance`.

**RM workload is computed on demand.** `services/onboarding.py::managers_with_load` counts, across **every** application (not just stage=rm_assignment), how many have each manager assigned. `GET /api/relationship-managers` returns `list[ManagerWithLoad]` so the Relationship-manager tab can render the pool-workload sidebar without a second round-trip.

**Account-type suggestion lives in the frontend.** `frontend/src/utils.ts::suggestAccountType` is the heuristic used on the Account-creation queue to propose a product. It is deliberately frontend-only so students can move it to the backend as a domain function — a natural workshop exercise. Do not silently add an identical backend copy.

**Typed end-to-end.** Pydantic models in `backend/app/models.py` are mirrored as TypeScript interfaces in `frontend/src/types.ts`. When you change a model (new field, renamed enum value, new stage), update both — the frontend won't fail loudly at runtime if a field is missing, it will just render blank.

## Frontend notes

- Vue 3 `<script setup lang="ts">` composition style throughout. No options API. No UI component library — styles are plain CSS with CSS variables in `src/styles.css`.
- Pinia is installed but **currently unused**. Views fetch via `src/api.ts` directly. Wiring up Pinia as a shared store is an intentional workshop exercise.
- Charts use `vue-chartjs` + `chart.js`. Chart components live in `src/components/charts/` and all read from the `/api/stats` response. Palette + color maps are centralised in `src/charts.ts`.
- **Route structure**: `/` = Overview, then one route per onboarding stage (`/kyc`, `/accounts`, `/rm`) + `/onboarding` for the new-client form + `/applications/:id` + `/audit`. Legacy `/dashboard` redirects to `/kyc` and legacy `/analytics` redirects to `/`.
- `StageFlow.vue` is the chevron pipeline bar at the top of the Overview page (counts per stage). `StageStepper.vue` is the chevron stepper at the top of the application detail view (where this specific client is right now). Both share the same clip-path trick; keep the visual language consistent if you add a new stage.
- `AccountPanel.vue` and `RelationshipManagerPanel.vue` each show three states: *locked* (stage hasn't been reached), *actionable* (current stage, form / auto-match button visible), *done* (summary card). This is the pattern to follow if you add a 4th stage.
- Queue views (`KycQueueView`, `AccountQueueView`, `RmQueueView`) all load via `api.listApplications({ stage: ... })`. They each have their own summary cards; click any row to go to the universal `ApplicationDetailView` where the actual mutating actions live.
- Vite proxies `/api/*` to `http://localhost:8001`. The frontend never talks to `:8001` directly.

## Conventions

- **Python:** `from __future__ import annotations` at the top of every module, type hints everywhere, Pydantic v2.
- **Backend file sizes.** `api/` routers stay small (thin adapters). If a services module grows past ~300 lines, split by concern (as we did for `services/onboarding.py`). Do not preemptively split `services/applications.py`.
- **Imports in services.** Prefer `from ..domain import assess, screen, run_check, relationship_managers` (the re-exports in `domain/__init__.py`) over reaching into submodules.
- **Time.** Use `utils.utcnow()`, never `datetime.utcnow()` directly — keeps a single place to patch if tests need to freeze time.

## Things NOT to do (unless explicitly asked)

- Add a database, ORM, or persistence layer.
- Add authentication, sessions, or JWTs.
- Replace the fake sanctions/liveness/OCR/RM-matching/account-number generator with real services.
- Introduce a UI component library (Vuetify, PrimeVue, Naive UI, etc.).
- Collapse the `api` / `services` / `domain` split back into `main.py`.
- Raise `HTTPException` from services.
- Skip the `audit.record(...)` call on a new mutating endpoint.
- Bypass stage gates in `services/onboarding.py`.
- Mirror `frontend/src/utils.ts::suggestAccountType` into the backend without being asked (it's a workshop exercise).
- Add Docker / compose / k8s files.
