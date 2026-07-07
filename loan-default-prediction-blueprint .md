# Loan Default Prediction System — Complete Project Blueprint

**Stack:** Next.js + Tailwind (Frontend) · FastAPI (Backend) · Scikit-learn/Pandas/NumPy/Joblib (ML) · Supabase/PostgreSQL (Database) · Vercel + Render (Deployment) · GitHub Monorepo

> This document is a planning blueprint only. No source code, SQL, or file contents are included — only structure, purpose, and reasoning.

---

## Table of Contents
1. Complete Repository Structure
2. Development Roadmap
3. Machine Learning Module
4. Backend Module
5. Database Module
6. Frontend Module
7. Integration Workflow
8. API Design
9. Environment Variables
10. Deployment Plan
11. Testing Plan
12. Documentation
13. Viva Preparation
14. Final Checklist

---

## 1. Complete Repository Structure

```
loan-default-prediction/                     # Monorepo root
│
├── .github/
│   └── workflows/
│       ├── backend-ci.yml                   # Lints/tests backend on push/PR to backend/**
│       ├── frontend-ci.yml                  # Lints/builds frontend on push/PR to frontend/**
│       └── ml-ci.yml                        # Validates ML training script + artifact integrity
│
├── ml/                                       # Machine Learning module
│   ├── data/
│   │   ├── raw/                             # Original, untouched dataset(s)
│   │   │   └── loan_data.csv
│   │   ├── processed/                       # Cleaned/encoded dataset used for training
│   │   │   └── loan_data_clean.csv
│   │   └── README.md                        # Data source, license, column dictionary
│   │
│   ├── notebooks/
│   │   └── eda.ipynb                        # Exploratory Data Analysis (kept out of prod)
│   │
│   ├── src/
│   │   ├── preprocess.py                    # Cleaning, encoding, imputation logic
│   │   ├── feature_engineering.py           # Derived features, scaling logic
│   │   ├── train.py                         # Trains model, runs CV, logs metrics
│   │   ├── evaluate.py                      # Generates evaluation report/plots
│   │   └── utils.py                         # Shared helpers (paths, logging, seeds)
│   │
│   ├── models/
│   │   ├── model.joblib                     # Final trained model artifact
│   │   ├── preprocessing_pipeline.joblib    # Fitted encoder/scaler pipeline
│   │   ├── feature_names.json               # Ordered list of features model expects
│   │   └── metrics.json                     # Accuracy, precision, recall, ROC-AUC, etc.
│   │
│   ├── requirements.txt                     # ML-only Python dependencies
│   └── README.md                            # How to reproduce training end-to-end
│
├── backend/                                  # FastAPI service
│   ├── app/
│   │   ├── main.py                          # FastAPI app entrypoint, middleware, routers
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routes_predict.py            # /predict endpoint(s)
│   │   │   ├── routes_history.py            # /history endpoint(s) (past predictions)
│   │   │   └── routes_health.py             # /health, /version endpoints
│   │   │
│   │   ├── core/
│   │   │   ├── config.py                    # Loads env vars into a typed Settings object
│   │   │   ├── logging_config.py            # Centralized logging setup
│   │   │   └── security.py                  # API key / CORS / rate-limit helpers
│   │   │
│   │   ├── models/
│   │   │   ├── request_schemas.py           # Pydantic request models (input validation)
│   │   │   └── response_schemas.py          # Pydantic response models
│   │   │
│   │   ├── services/
│   │   │   ├── ml_service.py                # Loads joblib model + pipeline, runs inference
│   │   │   ├── prediction_service.py        # Business logic connecting request → ML → DB
│   │   │   └── supabase_service.py          # Supabase client, insert/query helpers
│   │   │
│   │   └── db/
│   │       ├── supabase_client.py           # Initializes Supabase client with env creds
│   │       └── schemas.py                   # Python-side representation of DB tables
│   │
│   ├── tests/
│   │   ├── test_predict.py                  # Unit/integration tests for /predict
│   │   ├── test_health.py
│   │   └── conftest.py                      # Pytest fixtures (test client, mock model)
│   │
│   ├── requirements.txt                     # Backend Python dependencies
│   ├── Procfile                             # Render start command (uvicorn)
│   ├── render.yaml                          # Render service definition (IaC, optional)
│   └── README.md                            # Backend setup, run, test instructions
│
├── frontend/                                  # Next.js application
│   ├── app/  (or pages/, depending on router choice)
│   │   ├── layout.tsx                       # Root layout, global styles, fonts
│   │   ├── page.tsx                         # Landing page
│   │   ├── predict/
│   │   │   └── page.tsx                     # Loan input form page
│   │   ├── result/
│   │   │   └── page.tsx                     # Prediction result page
│   │   └── history/
│   │       └── page.tsx                     # Past predictions list (optional)
│   │
│   ├── components/
│   │   ├── forms/
│   │   │   └── LoanForm.tsx                 # Main input form component
│   │   ├── ui/
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Loader.tsx
│   │   │   └── ErrorBanner.tsx
│   │   └── layout/
│   │       ├── Navbar.tsx
│   │       └── Footer.tsx
│   │
│   ├── hooks/
│   │   ├── usePredictLoan.ts                # Encapsulates API call + loading/error state
│   │   └── useFormValidation.ts             # Client-side validation logic
│   │
│   ├── services/
│   │   └── api.ts                           # Axios/fetch wrapper, base URL from env
│   │
│   ├── lib/
│   │   └── validators.ts                    # Shared validation schemas (e.g., zod/yup)
│   │
│   ├── styles/
│   │   └── globals.css                      # Tailwind base/components/utilities imports
│   │
│   ├── public/
│   │   └── assets/                          # Logos, icons, static images
│   │
│   ├── .env.local.example                   # Template for local frontend env vars
│   ├── next.config.js                       # Next.js configuration
│   ├── tailwind.config.ts                   # Tailwind theme/config
│   ├── postcss.config.js                    # Required by Tailwind
│   ├── tsconfig.json                        # TypeScript configuration
│   ├── package.json                         # Frontend dependencies/scripts
│   └── README.md                            # Frontend setup/run instructions
│
├── docs/                                       # Project-wide documentation
│   ├── ARCHITECTURE.md
│   ├── API_REFERENCE.md
│   ├── DATABASE_SCHEMA.md
│   ├── DEPLOYMENT_GUIDE.md
│   ├── ML_PIPELINE.md
│   ├── TESTING_GUIDE.md
│   └── VIVA_QA.md
│
├── .gitignore                                 # Excludes node_modules, venv, .env, models cache
├── .env.example                               # Root-level combined reference of all env vars
├── LICENSE
├── README.md                                  # Top-level project overview, quickstart
└── docker-compose.yml (optional)               # Local orchestration of backend+db for dev
```

### File-by-file rationale (key files)

| File | Why it exists | Depends on / Depended on by |
|---|---|---|
| `ml/src/preprocess.py` | Encodes categorical fields, imputes missing values, ensures consistent schema before training | Used by `train.py`; output pipeline consumed by `backend/app/services/ml_service.py` |
| `ml/src/train.py` | Single source of truth for how the model is produced — ensures reproducibility | Produces `model.joblib`, `preprocessing_pipeline.joblib` |
| `ml/models/model.joblib` | Serialized trained classifier that backend loads at startup | Loaded by `ml_service.py` |
| `ml/models/preprocessing_pipeline.joblib` | Ensures backend transforms raw user input identically to training-time transformation | Loaded by `ml_service.py` before calling `model.predict()` |
| `ml/models/feature_names.json` | Guards against silent column-order mismatches between training and inference | Read by `ml_service.py` to validate/order incoming request fields |
| `backend/app/core/config.py` | Centralizes all environment variable access so nothing reads `os.environ` directly elsewhere | Used by `supabase_client.py`, `ml_service.py`, `main.py` |
| `backend/app/services/ml_service.py` | Isolates all ML-loading/inference logic from API/routing logic | Called by `prediction_service.py` |
| `backend/app/services/supabase_service.py` | Single place for all DB reads/writes, so DB provider could be swapped later | Called by `prediction_service.py` |
| `backend/app/api/routes_predict.py` | Defines the public prediction contract (request/response validation, HTTP semantics) | Registered in `main.py`; calls `prediction_service.py` |
| `backend/Procfile` / `render.yaml` | Tells Render how to start the FastAPI app in production | Used only during Render deployment |
| `frontend/services/api.ts` | Single point of contact with backend so URL/headers are configured once | Used by `usePredictLoan.ts` |
| `frontend/hooks/usePredictLoan.ts` | Encapsulates loading/error/success state so components stay declarative | Used by `predict/page.tsx` |
| `frontend/components/forms/LoanForm.tsx` | The primary user-facing input surface; source of the prediction request payload | Depends on `validators.ts`, `useFormValidation.ts` |
| `.env.example` (root) & `.env.local.example` (frontend) | Documents every required variable without leaking secrets into git | Referenced by every module's README |
| `docs/DATABASE_SCHEMA.md` | Human-readable schema so frontend/backend devs don't need direct DB access to understand structure | Referenced during backend/frontend development |

---

## 2. Development Roadmap

**Phase 1 — Machine Learning**
Build the model first because everything downstream (API contract, DB schema, frontend form) depends on knowing the exact input features and output format the model expects/produces. Building backend or frontend first would risk rework once feature engineering changes the input shape.

**Phase 2 — Database**
Design the schema next, informed by the finalized feature set (so the `predictions` table mirrors the model's input fields) and by what needs to be persisted (inputs, prediction, probability, timestamp).

**Phase 3 — Backend**
Build FastAPI once the model artifacts and DB schema are stable, so routes, services, and Pydantic schemas can be written against a known contract instead of guessing.

**Phase 4 — Frontend**
Build the UI once the API contract (request/response shape) is frozen, so the form fields and result page map 1:1 to real backend fields instead of placeholder data.

**Phase 5 — Integration**
Connect frontend → backend → ML → Supabase end-to-end locally, resolving CORS, env var, and payload-mismatch issues in a controlled environment before deployment.

**Phase 6 — Testing**
Run unit, integration, and API tests once the whole flow works, catching regressions before they reach production.

**Phase 7 — Deployment**
Deploy backend (Render), frontend (Vercel), and connect Supabase, since deploying a tested/integrated system is far less error-prone than deploying and debugging in production.

**Phase 8 — Documentation**
Write final documentation last, once behavior is stable, so docs describe what was actually built rather than what was planned.

**Why this order overall:** each phase produces a stable "contract" (feature list → schema → API shape → UI) that the next phase builds against. Reversing the order (e.g., frontend before ML) causes churn every time an upstream decision changes.

---

## 3. Machine Learning Module

**Dataset workflow**
Raw data is stored untouched in `ml/data/raw/`. A copy is never edited in place — this preserves reproducibility and lets you re-run preprocessing from scratch if logic changes.

**Data preprocessing workflow**
- Handle missing values (imputation strategy per column type: median for numeric, mode/"unknown" category for categorical).
- Encode categorical variables (label/one-hot encoding, decided per cardinality).
- Detect and treat outliers in fields like income or loan amount.
- Split into train/test sets with a fixed random seed for reproducibility.

**Feature engineering**
- Derive ratios that are typically more predictive than raw values (e.g., debt-to-income ratio, loan-to-income ratio).
- Bucket/bin continuous variables where it improves model stability (e.g., age groups).
- Scale numeric features consistently with whatever the chosen model family requires (tree-based models often skip scaling; logistic regression needs it).

**Model training workflow**
- Try baseline models (Logistic Regression) before more complex ones (Random Forest, Gradient Boosting) to establish a performance floor.
- Use cross-validation to avoid overfitting to a single train/test split.
- Tune hyperparameters (grid/random search) against a validation metric appropriate for imbalanced classification (loan default datasets are usually imbalanced).

**Model evaluation workflow**
- Report accuracy, precision, recall, F1, and ROC-AUC — recall and AUC matter most since missing a real default (false negative) is usually costlier than a false alarm.
- Generate a confusion matrix and ROC curve for the evaluation report.
- Store all metrics in `metrics.json` so the backend/docs can reference model performance without re-running training.

**Model saving process**
The final chosen model is serialized with Joblib into `model.joblib`. Joblib is preferred over pickle for scikit-learn objects because it handles NumPy arrays more efficiently.

**Pipeline saving process**
The preprocessing steps (imputers, encoders, scalers) are wrapped into a single scikit-learn `Pipeline`/`ColumnTransformer` object and saved separately (or combined with the model into one pipeline object) as `preprocessing_pipeline.joblib`, so raw user input can be transformed identically to how training data was transformed — this prevents "training/serving skew."

**Folder organization**
`data/` (raw + processed), `notebooks/` (exploration only, never used in production), `src/` (reusable scripts), `models/` (versionless "latest" artifacts committed via Git LFS or excluded from git and uploaded separately).

**Generated artifacts**
`model.joblib`, `preprocessing_pipeline.joblib`, `feature_names.json`, `metrics.json` — these four files are the only ML outputs the backend ever needs.

**How backend will use the saved model**
At startup, `ml_service.py` loads `preprocessing_pipeline.joblib` and `model.joblib` once into memory (not per-request, for performance). Each incoming request is validated against `feature_names.json`, passed through the pipeline's `.transform()`, then the model's `.predict()`/`.predict_proba()`, and the result is returned to the API layer.

---

## 4. Backend Module

**Folder structure** — see Section 1. Organized by responsibility: `api/` (HTTP layer), `core/` (config/security/logging), `models/` (Pydantic schemas), `services/` (business logic), `db/` (Supabase access) — this separation keeps route handlers thin and testable.

**FastAPI architecture**
`main.py` creates the app, registers CORS middleware, includes routers from `api/`, and triggers a startup event that loads the ML model into memory once.

**API routes** (see full list in Section 8): prediction, history retrieval, and health check routers, each isolated in its own file and included into `main.py`.

**Request flow**
1. Client sends JSON to `/predict`.
2. FastAPI validates it against the Pydantic request schema (type/range checks).
3. `routes_predict.py` calls `prediction_service.py`.
4. `prediction_service.py` calls `ml_service.py` for inference and `supabase_service.py` to persist the record.
5. A structured response is returned.

**Response flow**
The response schema (`response_schemas.py`) guarantees a consistent shape (prediction label, probability, timestamp, request id) regardless of internal changes to the model.

**Validation**
Pydantic models enforce required fields, types, and value ranges (e.g., loan amount > 0, age between realistic bounds) before any code touches the ML pipeline — invalid requests are rejected with `422` before reaching business logic.

**Error handling**
A global exception handler in `main.py` catches unhandled errors and returns a consistent JSON error shape; specific handlers catch validation errors, model-loading errors, and Supabase connectivity errors distinctly, each mapped to an appropriate HTTP status code.

**Environment variables** — see Section 9.

**Model loading process**
The model and pipeline are loaded once in a FastAPI startup event and cached as module-level or app-state objects, avoiding the cost of reloading a joblib file on every request.

**Prediction workflow**
Validated request → mapped to a DataFrame matching `feature_names.json` order → transformed by pipeline → predicted by model → probability + label formatted → persisted to Supabase → returned to client.

---

## 5. Database Module

**Supabase project setup**
Create a Supabase project, note the project URL and API keys (anon/public key for frontend-safe reads if ever needed, service role key kept backend-only), and enable the Postgres database.

**Database schema (described, not in SQL)**

*Table: `predictions`*
| Column | Type (conceptual) | Purpose |
|---|---|---|
| `id` | UUID, primary key | Unique record identifier |
| `created_at` | timestamp | When the prediction was made |
| `applicant_income` | numeric | Model input feature |
| `loan_amount` | numeric | Model input feature |
| `credit_history` | boolean/categorical | Model input feature |
| `...other model input fields` | various | Mirrors `feature_names.json` exactly |
| `prediction_label` | text/boolean | "Default" / "No Default" |
| `prediction_probability` | numeric | Confidence score from the model |
| `model_version` | text | Traceability to which model produced the result |

*Table: `users` (optional, only if auth is added)*
| Column | Purpose |
|---|---|
| `id` | Supabase Auth user id |
| `email` | Login identity |
| `created_at` | Account creation time |

**Relationships**
If authentication is added, `predictions.user_id` references `users.id` (one user → many predictions). Without auth, `predictions` stands alone.

**Indexes**
An index on `created_at` (for history sorting/pagination) and on `user_id` (if present) for fast per-user lookups.

**Authentication (if applicable)**
Supabase Auth (email/password or magic link) can be layered on later to associate predictions with a logged-in user; not required for a minimum viable version.

**Environment variables** — `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` (backend only, never exposed to frontend), and optionally `SUPABASE_ANON_KEY` if the frontend ever talks to Supabase directly.

**How backend communicates with Supabase**
`supabase_service.py` initializes the Supabase Python client once using `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` from `config.py`, then exposes simple functions like "insert prediction record" and "fetch recent predictions" that `prediction_service.py` calls — the rest of the backend never talks to Supabase directly.

---

## 6. Frontend Module

**Folder structure** — see Section 1: `app/` (routed pages), `components/` (reusable UI split into `forms/`, `ui/`, `layout/`), `hooks/` (stateful logic), `services/` (API layer), `lib/` (validation schemas).

**Pages**
- Landing page — brief product explanation and a call-to-action into the prediction flow.
- Predict page — the loan input form.
- Result page — shows prediction outcome and probability.
- History page (optional) — lists past predictions if persistence/auth is enabled.

**Components**
`LoanForm` (the core form), generic `ui/` primitives (Button, Input, Loader, ErrorBanner) reused across pages, and `layout/` components (Navbar, Footer) shared via the root layout.

**Hooks**
`usePredictLoan` wraps the API call and exposes `{ data, loading, error, predict() }` to components. `useFormValidation` centralizes field-level validation so the form component stays focused on presentation.

**Services**
`api.ts` wraps `fetch`/axios with the backend base URL (from an environment variable) and standard headers, so every API call goes through one configured client.

**Utilities**
`validators.ts` holds shared validation rules (e.g., required fields, numeric ranges) used both by the form and by `useFormValidation`.

**API communication**
The form collects input → `usePredictLoan` calls `api.ts` → POST request to backend `/predict` → response is stored in hook state → the Result page reads that state (or receives it via routing state/query) and renders it.

**Form validation**
Client-side validation mirrors backend validation rules (same ranges/required fields) so users get instant feedback without waiting on a round trip, while the backend still re-validates independently as the source of truth.

**Prediction page**
Presents the `LoanForm`; on submit, shows a loading state, then either navigates to the Result page or displays an inline error.

**Result page**
Displays the prediction label (e.g., "Likely to Default" / "Likely to Repay"), the probability/confidence score, and a plain-language explanation, plus a button to run another prediction.

**Loading states**
A shared `Loader` component is shown while the API call is in flight, driven by the `loading` flag from `usePredictLoan`.

**Error handling**
Network failures, validation errors, and backend error responses are all caught and surfaced via a shared `ErrorBanner` component with a human-readable message rather than raw error objects.

**Responsive design**
Tailwind's responsive utility classes (`sm:`, `md:`, `lg:`) are used throughout so the form and result layouts adapt from mobile to desktop without separate mobile-specific components.

---

## 7. Integration Workflow

```
[Frontend: LoanForm]
   │  user fills form, clicks "Predict"
   ▼
[Frontend: usePredictLoan -> api.ts]
   │  POST /predict  { applicant_income, loan_amount, credit_history, ... }
   ▼
[Backend: routes_predict.py]
   │  Pydantic validates request schema
   ▼
[Backend: prediction_service.py]
   │  orchestrates the next two calls
   ▼
[Backend: ml_service.py] ──► [ML: preprocessing_pipeline.joblib + model.joblib]
   │  transforms input, runs .predict()/.predict_proba()
   ▼
[Backend: prediction_service.py]
   │  formats result: { label, probability, model_version, timestamp }
   ▼
[Backend: supabase_service.py] ──► [Supabase: predictions table]
   │  INSERT the request fields + result (persistence/audit trail)
   ▼
[Backend: routes_predict.py]
   │  returns validated response schema
   ▼
[Frontend: usePredictLoan]
   │  stores response in state
   ▼
[Frontend: Result page]
      renders prediction label + probability to the user
```

Every arrow above is a JSON request/response boundary except the ML step (in-process function call) and the Supabase step (client library call over HTTPS).

---

## 8. API Design

### `POST /predict`
- **Purpose:** Run the loan default model on submitted applicant data.
- **Request body (conceptual):** applicant income, co-applicant income, loan amount, loan term, credit history, employment status, property area, education, marital status, dependents — exact set matches `feature_names.json`.
- **Response body (conceptual):** `prediction_label`, `prediction_probability`, `model_version`, `request_id`, `created_at`.
- **Possible errors:** missing/invalid field (422), model not loaded (503), internal error during inference (500), Supabase write failure (207/500 depending on whether prediction is still returned).
- **Status codes:** `200` success, `422` validation error, `500` internal error, `503` model unavailable.

### `GET /history`
- **Purpose:** Retrieve recent predictions (optionally per user, if auth is added).
- **Request:** query params for pagination (`limit`, `offset`) and optional `user_id`.
- **Response body:** list of past prediction records.
- **Possible errors:** invalid pagination params (422), DB read failure (500).
- **Status codes:** `200`, `422`, `500`.

### `GET /health`
- **Purpose:** Confirm the API is running and the model is loaded (used by uptime monitors and deployment checks).
- **Response body:** `{ status: "ok", model_loaded: true, version: "..." }`.
- **Status codes:** `200` healthy, `503` unhealthy.

### `GET /version`
- **Purpose:** Report backend and model version for traceability.
- **Response body:** `{ api_version, model_version }`.
- **Status codes:** `200`.

---

## 9. Environment Variables

**Frontend (Vercel + local `.env.local`)**
| Variable | Purpose |
|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | Backend URL the frontend calls (Render URL in prod, localhost in dev) |
| `NEXT_PUBLIC_SUPABASE_URL` (optional) | Only needed if frontend ever reads Supabase directly |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` (optional) | Public-safe Supabase key, never the service role key |

**Backend (Render + local `.env`)**
| Variable | Purpose |
|---|---|
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | Full-access key for backend DB writes — kept secret |
| `MODEL_PATH` | Path to `model.joblib` inside the deployed backend |
| `PIPELINE_PATH` | Path to `preprocessing_pipeline.joblib` |
| `ALLOWED_ORIGINS` | CORS whitelist (frontend's Vercel domain) |
| `ENVIRONMENT` | `development` / `production` flag for logging/behavior toggles |

**Storage locations**
- Local development: `.env` (backend) and `.env.local` (frontend), both git-ignored.
- Production: set directly in Render's and Vercel's dashboard "Environment Variables" sections — never committed to GitHub.
- `.env.example` (root) and `.env.local.example` (frontend) are committed to document required keys without real values.

---

## 10. Deployment Plan

**Backend on Render**
1. Push `backend/` to GitHub (monorepo — set Render's "root directory" to `backend/`).
2. Create a new Web Service on Render, connect the GitHub repo.
3. Set build command (`pip install -r requirements.txt`) and start command (from `Procfile`, e.g., `uvicorn app.main:app --host 0.0.0.0 --port $PORT`).
4. Add all backend environment variables in Render's dashboard.
5. Ensure `model.joblib`/`preprocessing_pipeline.joblib` are included in the deployed artifact (either committed via Git LFS or fetched at build time from storage).
6. Deploy and verify `/health` returns `200`.

**Frontend on Vercel**
1. Import the GitHub repo into Vercel, set the project root to `frontend/`.
2. Vercel auto-detects Next.js; confirm build command (`next build`) and output.
3. Add `NEXT_PUBLIC_API_BASE_URL` (pointing at the Render backend URL) in Vercel's Environment Variables.
4. Deploy and verify the predict flow hits the live backend.

**Connecting Supabase**
1. Confirm the Supabase project's URL and service role key match what's set on Render.
2. Confirm the `predictions` table exists in the Supabase dashboard before the first live prediction.
3. Test an insert manually from the Supabase SQL editor/table UI to confirm permissions before relying on the backend to do it.

**Configuring environment variables**
Set them once per platform's dashboard (Render for backend, Vercel for frontend); never rely on `.env` files being deployed, since they're git-ignored.

**Testing production**
- Hit `/health` on the deployed backend URL directly.
- Submit a real prediction through the deployed frontend and confirm a row appears in Supabase.
- Check CORS by confirming the browser console shows no blocked cross-origin errors.

**Common deployment mistakes**
- Forgetting to update `ALLOWED_ORIGINS`/CORS after the Vercel domain is known, breaking all frontend requests.
- Leaving `NEXT_PUBLIC_API_BASE_URL` pointed at `localhost` in production.
- Not committing/uploading the joblib model artifacts, causing the backend to crash on startup.
- Using the anon Supabase key on the backend (should use the service role key) or accidentally exposing the service role key to the frontend.
- Mismatched Python versions between local training and Render's runtime causing joblib deserialization errors.

---

## 11. Testing Plan

**ML testing**
Validate that `preprocess.py` and `feature_engineering.py` produce the expected columns/shapes on a small fixed sample; assert the saved model's metrics meet a minimum threshold before it's allowed to replace the deployed artifact.

**Backend testing**
Unit tests for each service function (`ml_service`, `supabase_service` mocked) and integration tests hitting FastAPI's TestClient against `/predict`, `/health`, `/history` with both valid and invalid payloads.

**Frontend testing**
Component tests for `LoanForm` (validation errors render correctly) and `usePredictLoan` (loading/error/success states), plus a smoke test that the predict page renders.

**Integration testing**
A full local run: start backend + frontend together, submit a real form through the UI, and confirm the response and a Supabase row match expectations.

**API testing**
Use a tool like Postman/HTTPie or automated pytest+httpx calls against every documented endpoint, covering both success and every documented error code.

**Deployment testing**
After deploying, repeat the integration test against the live URLs (see Section 10's "Testing production").

---

## 12. Documentation

| File | Contents |
|---|---|
| `README.md` (root) | Project overview, architecture diagram, quickstart for all three modules |
| `ml/README.md` | How to reproduce data prep + training, how artifacts are generated |
| `backend/README.md` | How to run FastAPI locally, env vars needed, how to run tests |
| `frontend/README.md` | How to run Next.js locally, env vars needed, how to run tests |
| `docs/ARCHITECTURE.md` | System diagram and explanation of how the three modules interact |
| `docs/API_REFERENCE.md` | Full endpoint list with request/response examples (mirrors Section 8) |
| `docs/DATABASE_SCHEMA.md` | Table/column documentation (mirrors Section 5) |
| `docs/ML_PIPELINE.md` | Detailed explanation of preprocessing, features, and model choice/metrics |
| `docs/DEPLOYMENT_GUIDE.md` | Step-by-step deployment instructions (mirrors Section 10) |
| `docs/TESTING_GUIDE.md` | How to run each layer's test suite |
| `docs/VIVA_QA.md` | The viva question bank (Section 13), kept as a standalone study doc |

---

## 13. Viva Preparation

**Q: Why did you choose FastAPI over Flask/Django?**
A: FastAPI gives automatic request validation via Pydantic, automatic OpenAPI docs, and async support with less boilerplate than Django, while being more structured for typed APIs than plain Flask.

**Q: Why is the preprocessing pipeline saved separately/alongside the model instead of re-implemented in the backend?**
A: To guarantee training/serving consistency — if the backend re-implemented preprocessing in a different language or logic, small mismatches would silently corrupt predictions ("training-serving skew").

**Q: Why Joblib instead of Pickle?**
A: Joblib is optimized for objects containing large NumPy arrays (common in scikit-learn models), making it faster and more memory-efficient to (de)serialize than standard pickle.

**Q: Why is recall/AUC emphasized over raw accuracy for this problem?**
A: Loan default datasets are typically imbalanced (few defaults vs. many repayments); a model can get high accuracy by always predicting "no default" while still missing real defaults, which is the costliest error for a lender.

**Q: Why Supabase instead of a self-managed PostgreSQL instance?**
A: Supabase provides a managed Postgres database with built-in auth, instant APIs, and a dashboard, reducing DevOps overhead for a project of this scope while still being standard SQL underneath.

**Q: Why is the model loaded once at startup instead of per request?**
A: Deserializing a joblib file is relatively expensive; loading once into memory and reusing it keeps prediction latency low.

**Q: How do you prevent the frontend from bypassing backend validation?**
A: Backend validation (Pydantic schemas) is the source of truth and re-validates every request regardless of what the frontend already checked, since client-side validation can always be bypassed.

**Q: Why a monorepo instead of separate repositories?**
A: Keeps ML, backend, and frontend versioned together so a given commit represents a consistent, working snapshot of the whole system, simplifying coordination for a small team/single deployment target.

**Q: What happens if the model file fails to load on backend startup?**
A: The `/health` endpoint reports `model_loaded: false` and returns a `503`, and `/predict` should fail fast with a clear error rather than crashing unpredictably mid-request.

**Q: How would you retrain and roll out a new model version safely?**
A: Retrain in `ml/`, validate new metrics meet/exceed the current threshold, bump `model_version`, replace the artifact, redeploy the backend, and monitor `/health` and a sample of live predictions before considering it fully rolled out.

---

## 14. Final Checklist

**Folder completion**
- [ ] All folders in Section 1 created
- [ ] `.gitignore` excludes `node_modules`, virtual envs, `.env*`, and large data files as appropriate

**ML completion**
- [ ] Raw dataset stored, documented in `ml/data/README.md`
- [ ] Preprocessing and feature engineering scripts finalized
- [ ] Model trained, evaluated, metrics meet agreed threshold
- [ ] `model.joblib`, `preprocessing_pipeline.joblib`, `feature_names.json`, `metrics.json` generated

**Database completion**
- [ ] Supabase project created
- [ ] `predictions` table created matching `feature_names.json`
- [ ] Indexes added
- [ ] Backend can successfully insert/read test rows

**Backend completion**
- [ ] All routes implemented and passing tests
- [ ] Model loads successfully on startup
- [ ] Environment variables documented and set locally
- [ ] `/health` returns `200` locally

**Frontend completion**
- [ ] Predict and Result pages implemented
- [ ] Form validation matches backend validation rules
- [ ] Loading/error states implemented
- [ ] Responsive on mobile and desktop

**Integration completion**
- [ ] Full local flow (form → backend → model → Supabase → result) verified end-to-end

**Deployment completion**
- [ ] Backend deployed on Render, `/health` passes in production
- [ ] Frontend deployed on Vercel, connects to live backend
- [ ] Supabase connected in production, live inserts verified
- [ ] CORS configured correctly for the production frontend domain

**Documentation completion**
- [ ] All files in Section 12 written
- [ ] Viva Q&A reviewed
