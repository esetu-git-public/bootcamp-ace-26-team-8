# Loan Default Prediction System — Complete Project Blueprint

**Type:** Enterprise Production Architecture & Delivery Blueprint (No source code, no SQL)
**Stack:** Next.js (Vercel) · FastAPI (Render) · Scikit-learn/Joblib · Supabase (Postgres + Auth)
**Repository model:** Single Monorepo

---

## Table of Contents

1. Complete Repository Structure
2. System Architecture
3. Development Roadmap
4. Machine Learning Module
5. Backend Module
6. Database Module
7. Frontend Module
8. Integration Workflow
9. Data Flow Requirements
10. API Design
11. Environment Variables
12. Deployment Plan
13. Testing Strategy
14. Documentation
15. Final Checklist

---

## 1. Complete Repository Structure

```
loan-default-prediction-system/
├── .github/
│   └── workflows/
│       ├── frontend-ci.yml
│       ├── backend-ci.yml
│       └── ml-ci.yml
├── frontend/
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── login/
│   │   │   │   └── page.tsx
│   │   │   ├── register/
│   │   │   │   └── page.tsx
│   │   │   └── layout.tsx
│   │   ├── (customer)/
│   │   │   ├── dashboard/
│   │   │   │   └── page.tsx
│   │   │   ├── apply/
│   │   │   │   └── page.tsx
│   │   │   ├── applications/
│   │   │   │   ├── page.tsx
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx
│   │   │   ├── profile/
│   │   │   │   └── page.tsx
│   │   │   └── layout.tsx
│   │   ├── (officer)/
│   │   │   ├── dashboard/
│   │   │   │   └── page.tsx
│   │   │   ├── applications/
│   │   │   │   ├── page.tsx
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx
│   │   │   ├── analytics/
│   │   │   │   └── page.tsx
│   │   │   └── layout.tsx
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── globals.css
│   ├── components/
│   │   ├── ui/
│   │   │   ├── Button.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Select.tsx
│   │   │   ├── Table.tsx
│   │   │   ├── Badge.tsx
│   │   │   ├── Modal.tsx
│   │   │   └── Spinner.tsx
│   │   ├── customer/
│   │   │   ├── LoanApplicationForm.tsx
│   │   │   ├── PredictionResultCard.tsx
│   │   │   ├── ApplicationStatusTimeline.tsx
│   │   │   └── ApplicationHistoryTable.tsx
│   │   ├── officer/
│   │   │   ├── ApplicationsQueueTable.tsx
│   │   │   ├── ApplicationDetailPanel.tsx
│   │   │   ├── DecisionActionBar.tsx
│   │   │   └── AnalyticsCharts.tsx
│   │   └── shared/
│   │       ├── Navbar.tsx
│   │       ├── Sidebar.tsx
│   │       ├── RoleGuard.tsx
│   │       └── ErrorBoundary.tsx
│   ├── services/
│   │   ├── apiClient.ts
│   │   ├── authService.ts
│   │   ├── loanService.ts
│   │   └── officerService.ts
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useLoanApplications.ts
│   │   └── useRole.ts
│   ├── lib/
│   │   ├── supabaseClient.ts
│   │   ├── constants.ts
│   │   └── validators.ts
│   ├── types/
│   │   ├── loan.d.ts
│   │   ├── user.d.ts
│   │   └── api.d.ts
│   ├── middleware.ts
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── tsconfig.json
│   ├── package.json
│   ├── .env.local.example
│   └── .eslintrc.json
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── logging.py
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── routes_auth.py
│   │   │   │   ├── routes_loans.py
│   │   │   │   ├── routes_predictions.py
│   │   │   │   ├── routes_officer.py
│   │   │   │   └── routes_health.py
│   │   ├── schemas/
│   │   │   ├── loan_schema.py
│   │   │   ├── user_schema.py
│   │   │   └── prediction_schema.py
│   │   ├── services/
│   │   │   ├── prediction_service.py
│   │   │   ├── loan_service.py
│   │   │   ├── officer_service.py
│   │   │   └── supabase_service.py
│   │   ├── ml/
│   │   │   ├── model_loader.py
│   │   │   └── preprocessing.py
│   │   ├── middleware/
│   │   │   ├── auth_middleware.py
│   │   │   └── error_handler.py
│   │   └── utils/
│   │       ├── validators.py
│   │       └── constants.py
│   ├── tests/
│   │   ├── test_auth.py
│   │   ├── test_loans.py
│   │   ├── test_predictions.py
│   │   └── test_officer.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── render.yaml
│   └── .env.example
├── ml/
│   ├── data/
│   │   ├── raw/
│   │   └── processed/
│   ├── notebooks/
│   │   ├── 01_eda.ipynb
│   │   ├── 02_feature_engineering.ipynb
│   │   ├── 03_model_training.ipynb
│   │   └── 04_model_evaluation.ipynb
│   ├── src/
│   │   ├── data_cleaning.py
│   │   ├── feature_engineering.py
│   │   ├── train_pipeline.py
│   │   └── evaluate_model.py
│   ├── models/
│   │   └── loan_pipeline.pkl
│   ├── reports/
│   │   ├── model_comparison_report.md
│   │   └── evaluation_metrics.json
│   └── requirements.txt
├── docs/
│   ├── README.md
│   ├── ARCHITECTURE.md
│   ├── API_DOCUMENTATION.md
│   ├── DATABASE_DOCUMENTATION.md
│   ├── DEPLOYMENT_GUIDE.md
│   ├── USER_MANUAL.md
│   ├── INSTALLATION_GUIDE.md
│   ├── BUSINESS_REQUIREMENTS.md
│   └── PROJECT_REPORT.md
├── assets/
│   ├── diagrams/
│   │   ├── architecture-diagram.png
│   │   ├── er-diagram.png
│   │   └── sequence-diagrams/
│   └── screenshots/
├── scripts/
│   ├── setup_env.sh
│   ├── seed_test_data.py
│   └── retrain_model.sh
├── tests/
│   └── integration/
│       ├── test_loan_submission_flow.py
│       └── test_officer_review_flow.py
├── deployment/
│   ├── vercel.json
│   ├── render.yaml
│   └── supabase/
│       └── config_notes.md
├── .gitignore
├── LICENSE
└── README.md
```

### File Purpose Reference

| Path | Purpose | Responsibility | Depends On | Implemented Later |
|---|---|---|---|---|
| `frontend/app/(auth)/*` | Login/Register pages | UI for Supabase Auth sign-in/sign-up | `authService.ts`, Supabase Auth | Full auth UI + validation |
| `frontend/app/(customer)/*` | Customer-only routes | Apply, track, view history, profile | `RoleGuard`, `loanService.ts` | Forms, status views |
| `frontend/app/(officer)/*` | Officer-only routes | Review queue, decisions, analytics | `RoleGuard`, `officerService.ts` | Tables, charts, actions |
| `frontend/components/ui/*` | Design-system primitives | Reusable visual building blocks | Tailwind config | Styling, variants |
| `frontend/services/apiClient.ts` | Central HTTP client | Attaches auth token, base URL, error handling | Backend API only | Interceptors, retries |
| `frontend/middleware.ts` | Route protection | Redirects unauthenticated/wrong-role users | Supabase session | Role-based redirects |
| `backend/app/main.py` | FastAPI entrypoint | App instance, router registration, CORS, startup model load | All routers | Lifespan events |
| `backend/app/core/config.py` | Settings | Loads env vars (Supabase keys, model path) | `.env` | Validation via pydantic settings |
| `backend/app/core/security.py` | Auth verification | Validates Supabase JWT, extracts role | `python-jose`/Supabase JWKS | Token refresh handling |
| `backend/app/api/v1/routes_predictions.py` | Prediction endpoint | Orchestrates validate→preprocess→predict→save | `prediction_service.py` | Business rule enforcement |
| `backend/app/api/v1/routes_officer.py` | Officer endpoints | List/filter applications, status updates | `officer_service.py` | Pagination, filters |
| `backend/app/ml/model_loader.py` | Loads `loan_pipeline.pkl` | Singleton model instance in memory | `joblib`, `ml/models/` | Version pinning, reload endpoint |
| `backend/app/ml/preprocessing.py` | Feature transform | Converts raw request → model input schema | Same encoders used in training | Shared schema with `ml/` |
| `backend/app/services/supabase_service.py` | DB access layer | All reads/writes to Supabase from backend | Supabase Python client | Query optimization |
| `ml/src/train_pipeline.py` | Model training | Cleans data, engineers features, trains, saves pipeline | scikit-learn | Hyperparameter tuning |
| `ml/models/loan_pipeline.pkl` | Serialized model artifact | Loaded once by backend at startup | `train_pipeline.py` output | Retraining cadence |
| `docs/*.md` | All documentation | See Section 14 | N/A | Populated progressively per phase |
| `.github/workflows/*.yml` | CI pipelines | Lint/test on push/PR for each package | GitHub Actions | Auto-deploy hooks |
| `deployment/render.yaml` | Render service definition | Backend build/start commands, env var references | Render account | Health check path |
| `deployment/vercel.json` | Vercel project config | Build settings, redirects | Vercel account | Custom domains |

---

## 2. System Architecture

### 2.1 Component Responsibilities

- **Next.js Frontend (single app):** Presentation layer only. Renders customer and officer UIs from one codebase using route groups. Holds no business logic, no direct DB access, no ML code.
- **FastAPI Backend (single gateway):** The only service allowed to talk to Supabase and the ML model. Owns authentication verification, validation, business rules, preprocessing, prediction, persistence, and status transitions.
- **ML Model (`loan_pipeline.pkl`):** A serialized scikit-learn pipeline (preprocessing + classifier) loaded exclusively inside the FastAPI process memory. Never exposed as a separate network service, never imported by the frontend.
- **Supabase:** Provides (a) Authentication — issuing JWTs and managing user identity/role metadata, and (b) PostgreSQL — persistent storage for the complete loan application lifecycle. It performs no business logic.

### 2.2 Why FastAPI Is the Single Gateway

Centralizing all writes/reads/predictions in FastAPI guarantees one place enforces validation, authorization, and consistency. If the frontend could call Supabase or the model directly, business rules (e.g., "only officers can change status," "predictions must be logged with the full applicant record") could be bypassed client-side. A single gateway also simplifies auditing, rate-limiting, versioning the ML pipeline, and swapping the model without touching the frontend or the database contract.

### 2.3 Why the Frontend Never Accesses the ML Model Directly

The model expects a specific, versioned feature schema. Exposing it to the browser would leak the schema/model file, prevent server-side validation of malicious input, and make it impossible to guarantee that every prediction is paired with a persisted, complete loan record. Keeping the model server-side also allows retraining/hot-swapping without any frontend deployment.

### 2.4 Why Business Logic Belongs in FastAPI

Business rules (eligibility checks, status transition rules, role permissions) must be enforced somewhere the client cannot tamper with. FastAPI is the trust boundary; the frontend is treated as untrusted input.

### 2.5 Why Supabase Is Only Persistent Storage

Supabase is used for what it's best at: managed Postgres and Auth. It is intentionally kept "dumb" — no business logic in database functions/triggers is relied upon for the model-driven parts of the workflow, so all decisioning logic remains in one auditable, testable Python codebase (FastAPI).

### 2.6 Authentication Flow

1. User registers/logs in via Supabase Auth from the Next.js `(auth)` route group.
2. Supabase issues a JWT (session) and stores the user's role (`customer` or `officer`) in user metadata / a `profiles` table.
3. Frontend stores the session (Supabase client-side SDK) and attaches the access token to every request to FastAPI via `apiClient.ts`.
4. FastAPI's `security.py` verifies the JWT signature against Supabase's JWKS/secret, extracts `user_id` and `role`.
5. Route-level dependency checks the role: customer-only routes reject officer tokens and vice versa (and vice versa), returning `403`.
6. On the frontend, `middleware.ts` + `RoleGuard` redirect users to `(customer)` or `(officer)` route groups based on the role claim, purely for UX; the real enforcement is server-side in FastAPI.

### 2.7 Deployment Architecture

- **Vercel** hosts the Next.js frontend, builds from the `frontend/` folder, injects `NEXT_PUBLIC_*` env vars at build time.
- **Render** hosts the FastAPI backend as a web service, loads `loan_pipeline.pkl` at container startup, injects secrets as environment variables.
- **Supabase** hosts Postgres + Auth in the cloud; both Vercel and Render connect to it using project URL and keys (frontend uses the anon key only for Auth session handling; backend uses the service role key for privileged reads/writes).

### 2.8 Request-Response Sequence (Customer Submission)

```
Customer → Next.js (form submit)
        → FastAPI POST /loan/apply (Authorization: Bearer <token>)
        → FastAPI verifies token + role=customer
        → FastAPI validates payload (schema + business rules)
        → FastAPI preprocesses features
        → FastAPI runs loan_pipeline.pkl → prediction + probability
        → FastAPI assembles complete loan record
        → FastAPI writes record to Supabase (service role key)
        → FastAPI returns { application_id, prediction, probability, status } 
        → Next.js renders PredictionResultCard
```

### 2.9 Component Interaction Diagram (textual)

```
[Browser: Next.js App]
        |
        |  HTTPS (JWT in Authorization header)
        v
[FastAPI on Render] --owns--> [ML Pipeline in-process]
        |
        |  Service-role DB calls
        v
[Supabase: Postgres + Auth]
```

No arrow exists directly from the Browser to Supabase's data tables, and none from the Browser to the ML Pipeline — by design.

---

## 3. Development Roadmap

| Phase | Focus | Why This Order |
|---|---|---|
| **1. Business Analysis** | Confirm problem, objectives, requirements, success metrics | Everything downstream (features, schema, endpoints) is derived from business rules; skipping this risks building the wrong thing. |
| **2. Machine Learning** | Data cleaning → features → training → evaluation → `loan_pipeline.pkl` | The model's input/output contract determines both the database schema (Section 9) and the prediction API contract (Section 10); it must exist before backend integration. |
| **3. Backend** | FastAPI structure, auth verification, prediction + loan + officer endpoints | The backend is the contract both frontend and database depend on; building it before the frontend avoids UI rework. |
| **4. Database** | Supabase schema, roles, auth, indexes | Finalized once the backend's data requirements (Section 9 fields) are locked in from ML + business logic. |
| **5. Frontend** | Next.js UI for customer + officer flows | Built last among the "build" phases because it consumes the now-stable API contract, minimizing rework. |
| **6. Integration** | Wire frontend ↔ backend ↔ database end-to-end | Confirms the full request lifecycle (Section 8) works as designed. |
| **7. Testing** | Unit, API, integration, UAT | Validates correctness across all layers before real deployment risk. |
| **8. Deployment** | Vercel + Render + Supabase go-live | Only after functional and integration correctness is confirmed. |
| **9. Documentation** | README, architecture, API docs, manuals | Finalized last so documentation reflects the actual shipped system rather than an evolving draft. |

---

## 4. Machine Learning Module

- **Dataset workflow:** Source a historical loan dataset (application-level records with a known default/no-default outcome). Perform an initial data audit for missing values, class imbalance, and outliers before any modeling.
- **Data cleaning:** Handle missing values (imputation or row/column removal where justified), remove duplicate records, correct inconsistent categorical labels (e.g., employment type spellings), and cap/flag extreme outliers in numeric fields like income or loan amount.
- **Feature engineering:** Derive fields such as debt-to-income ratio, loan-to-income ratio, and credit score bands; encode categorical variables (employment type, loan purpose) via one-hot or ordinal encoding as appropriate; scale numeric features for models sensitive to feature magnitude.
- **Data preprocessing:** Assemble a single scikit-learn `Pipeline`/`ColumnTransformer` combining imputers, encoders, and scalers so that the exact same transformation is reproducible at inference time inside FastAPI.
- **Train/Test Split:** Stratified split (e.g., 80/20) on the target label to preserve default/no-default ratio in both sets; a held-out validation set or cross-validation is used for model selection.
- **Binary Classification:** The target is `Default` (1) vs `No Default` (0). Candidate algorithms include Logistic Regression (baseline/interpretable), Random Forest, and Gradient Boosting (e.g., XGBoost/LightGBM) for stronger performance.
- **Model comparison:** Each candidate is evaluated on the same validation folds using consistent metrics; results are recorded in `ml/reports/model_comparison_report.md`.
- **Model evaluation:** Accuracy, Precision, Recall, F1-Score, and ROC-AUC are all reported — Recall on the "Default" class is weighted heavily since missing a true defaulter is costlier to the business than a false alarm.
- **Model selection:** The final model balances overall accuracy with strong recall on defaults and reasonable interpretability for loan officers reviewing predictions.
- **Pipeline creation:** The winning model and its full preprocessing chain are wrapped into one `Pipeline` object so raw applicant input can be fed in directly at inference time.
- **Saving `loan_pipeline.pkl`:** The trained pipeline is serialized with `joblib.dump` and stored under `ml/models/`, then copied/mounted into the backend's deployment artifact.
- **Backend integration:** At FastAPI startup, `model_loader.py` loads `loan_pipeline.pkl` once into memory (singleton), so every prediction request reuses the same loaded pipeline rather than reloading from disk, keeping response times low.

---

## 5. Backend Module

- **Folder organization:** `app/api` (routers), `app/schemas` (Pydantic request/response models), `app/services` (business logic), `app/ml` (model loading/preprocessing), `app/core` (config/security/logging), `app/middleware` (cross-cutting concerns) — a layered structure separating HTTP concerns from business and ML concerns.
- **FastAPI architecture:** Routers are versioned under `/api/v1`, each router delegates to a service module rather than embedding logic inline, keeping endpoints thin and testable.
- **Authentication flow:** A dependency (`security.py`) intercepts every protected route, verifies the Supabase-issued JWT signature/expiry, and injects the authenticated user's ID and role into the route handler.
- **Business logic:** Encapsulated in `services/` — e.g., `loan_service.py` enforces submission rules, `officer_service.py` enforces valid status transitions (e.g., a rejected loan cannot be re-approved without a "request review" step).
- **Prediction API:** Validates the applicant payload, calls `preprocessing.py` to build the model's feature vector, invokes the loaded pipeline, and returns prediction + probability alongside the persisted record ID.
- **Loan APIs:** Submit application, fetch a customer's own applications, fetch a single application by ID (with ownership check).
- **Officer APIs:** List/filter all applications (by status, date, risk level), fetch full application detail, update status with a mandatory reviewer note.
- **Validation:** Pydantic schemas enforce types, ranges (e.g., age, income > 0), and required fields before any business logic executes.
- **Exception handling:** A centralized handler (`middleware/error_handler.py`) converts internal exceptions into consistent JSON error responses with appropriate HTTP status codes, without leaking stack traces in production.
- **Logging:** Structured logs (`core/logging.py`) capture request IDs, user IDs, prediction outcomes, and errors for observability and audit trails, without logging sensitive PII in plaintext.
- **Model loading:** Happens once at process startup (or lazily on first request) via a singleton pattern; a health check confirms the model loaded successfully.
- **Prediction workflow:** validate → preprocess → predict → assemble full record → persist → respond, always in that order, always within one request/transaction.
- **Supabase communication:** All done through `services/supabase_service.py`, using the service role key server-side only — never exposed to the frontend.
- **Environment variables:** Supabase URL/keys, model path, JWT secret/JWKS URL, CORS origins, log level — loaded via `core/config.py` using a settings object, never hardcoded.

---

## 6. Database Module

- **Supabase project setup:** One Supabase project hosts both Auth and Postgres for the whole system; separate environments (dev/staging/prod) use separate Supabase projects.
- **Authentication:** Supabase Auth manages email/password (or OAuth) sign-up/sign-in and issues session JWTs consumed by FastAPI.
- **Role management:** A `profiles` table (linked 1:1 to `auth.users`) stores a `role` column (`customer` or `officer`); role is set at registration and checked by FastAPI on every request, not trusted from client-supplied data.
- **Database schema (conceptual):**
  - `profiles` — user_id (FK to auth.users), full_name, role, created_at.
  - `loan_applications` — the complete record described in Section 9, one row per submitted application.
  - Relationships: `loan_applications.user_id` → `profiles.user_id` (many applications per customer); `loan_applications.reviewed_by` → `profiles.user_id` (an officer).
  - Indexes: on `user_id`, `status`, and `submitted_date` to keep customer history lookups and officer queue filtering fast as volume grows.
- **Loan lifecycle:** `submitted` → (`under_review`) → `approved` / `rejected` / `review_requested`, each transition timestamped and attributed to an officer where applicable.
- **Prediction storage:** The model's output (`prediction`, `prediction_probability`) is stored directly on the `loan_applications` row at submission time — never recomputed or overwritten on officer review.
- **Approval workflow:** Officer actions only ever update `status`, `reviewed_by`, and `reviewed_date` — they never alter the original applicant data or the stored prediction, preserving an accurate audit trail.
- **Audit fields:** `submitted_date`, `reviewed_by`, `reviewed_date`, `updated_date` are present on every record to support compliance and traceability.
- **Environment variables:** `SUPABASE_URL`, `SUPABASE_ANON_KEY` (frontend, Auth only), `SUPABASE_SERVICE_ROLE_KEY` (backend only, never shipped to the client).
- **Backend communication:** FastAPI uses the Supabase Python client (service role key) exclusively; the frontend never imports this key or queries tables directly.

---

## 7. Frontend Module

- **Folder structure:** One Next.js app under `frontend/app`, using route groups `(auth)`, `(customer)`, `(officer)` so URLs stay clean while code stays organized by audience; `components/`, `services/`, `hooks/`, `lib/`, `types/` are shared across all groups.
- **Routing:** `(auth)` holds `/login` and `/register`; `(customer)` holds `/dashboard`, `/apply`, `/applications`, `/applications/[id]`, `/profile`; `(officer)` holds `/dashboard`, `/applications`, `/applications/[id]`, `/analytics`. A root `middleware.ts` redirects unauthenticated users to `(auth)` and mismatched-role users to their correct dashboard.
- **Authentication pages:** Login and register forms call Supabase Auth client-side for session creation only; no business data is written here.
- **Customer dashboard:** Summarizes application count/status, quick links to apply, most recent status, and profile info.
- **Loan application page and form validation:** Client-side validation (required fields, numeric ranges, formats) mirrors backend validation for fast feedback, but the backend remains the source of truth.
- **Prediction result page:** Displays the prediction label, probability, and next steps immediately after submission, using data returned from FastAPI (never computed client-side).
- **Application history:** A paginated/sortable table of the customer's own past applications and their current status.
- **Loan Officer dashboard:** All applications with pending/approved/rejected filter tabs, summary analytics (approval rate, average risk score), and a detail panel with Approve/Reject/Request Review actions.
- **Reusable components, services, hooks, utilities:** `apiClient.ts` centralizes all HTTP calls to FastAPI (never to Supabase tables); `useAuth`/`useRole` hooks expose session/role state; `ui/` holds design-system primitives shared by both customer and officer screens.
- **Responsive design:** Tailwind CSS breakpoints ensure both dashboards work on mobile, tablet, and desktop.
- **Loading states:** Skeletons/spinners shown while awaiting FastAPI responses (prediction can take a moment).
- **Error handling:** A shared `ErrorBoundary` plus per-request error states surface FastAPI error responses (e.g., validation failures, 403s) in a user-friendly way.
- **API communication:** Every data operation — submitting a loan, fetching history, updating status — goes exclusively through `apiClient.ts` to FastAPI endpoints; there is no direct Supabase table access or ML call from any frontend code.

---

## 8. Integration Workflow

### Loan Submission — Full Lifecycle

| Step | Component | Data Sent | Data Returned/Stored |
|---|---|---|---|
| 1 | Customer → Frontend | Form input (personal + financial fields) | — |
| 2 | Frontend → FastAPI `POST /loan/apply` | JSON payload + JWT | — |
| 3 | FastAPI validates | — | 400 on invalid payload |
| 4 | FastAPI preprocesses | — | Feature vector (internal) |
| 5 | FastAPI runs `loan_pipeline.pkl` | Feature vector | Prediction + probability |
| 6 | FastAPI assembles full record | Applicant data + prediction + status=`submitted` | — |
| 7 | FastAPI → Supabase | Complete record | Row persisted, `application_id` generated |
| 8 | FastAPI → Frontend | `{application_id, prediction, probability, status}` | — |
| 9 | Frontend renders result | — | — |

### Officer Review — Full Lifecycle

| Step | Component | Data Sent | Data Returned/Stored |
|---|---|---|---|
| 1 | Officer → Frontend | Login | — |
| 2 | Frontend → FastAPI `GET /officer/applications` | JWT (role=officer) | — |
| 3 | FastAPI → Supabase | Query with filters | Full application rows |
| 4 | FastAPI → Frontend | Complete applications list | — |
| 5 | Officer reviews, chooses action | — | — |
| 6 | Frontend → FastAPI `PATCH /officer/applications/{id}` | `{status, note}` + JWT | — |
| 7 | FastAPI validates officer role + valid transition | — | 403/400 on failure |
| 8 | FastAPI → Supabase | `status`, `reviewed_by`, `reviewed_date`, `updated_date` | Row updated |
| 9 | Customer dashboard (next fetch) | — | Reflects new status from Supabase via FastAPI |

**Why the ML model is called only once, at submission:** The prediction reflects the applicant's financial profile at the moment of application; officer decisions are a human business process layered on top of that prediction, not a re-evaluation of creditworthiness. Re-running the model on review would also make the audit trail ambiguous — reviewers must see the same prediction the system generated originally.

**Why officer actions never call the ML model again:** Officer actions only change workflow state (`status`, `reviewed_by`, `reviewed_date`); they are pure database writes through FastAPI's business logic layer.

**Why all applications are stored, not just predictions:** Officers need the complete applicant context (not just a risk score) to make a defensible, auditable decision, and the business requires a full historical record for compliance and future model retraining.

---

## 9. Data Flow Requirements

| Field | Used By Model? | Purpose |
|---|---|---|
| Application ID | No | Unique record identifier |
| User ID | No | Links application to the authenticated customer |
| Applicant Name | No | Business/display/audit purposes |
| Email | No | Communication, identity |
| Phone | No | Communication, identity |
| Age | Yes | Risk feature |
| Employment Type | Yes | Risk feature |
| Annual Income | Yes | Risk feature |
| Loan Amount | Yes | Risk feature |
| Loan Purpose | Yes | Risk feature |
| Credit Score | Yes | Risk feature |
| Existing Debt | Yes | Risk feature (debt-to-income derivation) |
| Other ML Features | Yes | Additional engineered/raw predictors |
| Prediction | No (output) | Model's classification result |
| Prediction Probability | No (output) | Model's confidence score |
| Loan Status | No | Business workflow state |
| Submitted Date | No | Audit/timeline |
| Reviewed By | No | Audit/accountability |
| Reviewed Date | No | Audit/timeline |
| Updated Date | No | Audit/timeline |

**Full lifecycle of one application:** Customer submits → FastAPI validates and preprocesses the ML-relevant fields → model predicts and returns a probability → FastAPI stores the complete record (identity fields + ML fields + prediction fields + `status=submitted` + `submitted_date`) → officer retrieves it, reviews both the applicant data and the prediction → officer sets `status` to `approved`, `rejected`, or `review_requested`, stamping `reviewed_by`/`reviewed_date`/`updated_date` → customer's dashboard reflects the final state on next fetch.

---

## 10. API Design

| Endpoint | Purpose | Request Body | Response Body | Validation | Errors | Status Codes |
|---|---|---|---|---|---|---|
| `POST /auth/session` (or Supabase-handled) | Confirm/verify session and role for frontend routing | JWT (header) | `{user_id, role}` | Token must be valid/unexpired | Invalid/expired token | 200, 401 |
| `POST /loan/apply` | Submit a new loan application and receive a prediction | Applicant + financial fields | `{application_id, prediction, probability, status}` | All required fields present, numeric ranges valid, role=customer | 400 invalid payload, 401 unauthenticated, 500 model/DB failure | 201, 400, 401, 500 |
| `GET /loan/applications` | Customer's own application history | — (JWT only) | List of the customer's applications | role=customer, user can only see own records | 401 unauthenticated | 200, 401 |
| `GET /loan/applications/{id}` | Single application detail (owner or officer) | — | Full application record | Requesting user must be owner or an officer | 403 not owner/officer, 404 not found | 200, 403, 404 |
| `GET /officer/applications` | List/filter all applications | Query params: status, date range, page | Paginated list of applications | role=officer | 401, 403 | 200, 401, 403 |
| `PATCH /officer/applications/{id}` | Approve/Reject/Request Review | `{status, note}` | Updated application record | role=officer, status must be a valid transition | 400 invalid transition, 403 not officer, 404 not found | 200, 400, 403, 404 |
| `GET /health` | Service and model liveness check | — | `{status: "ok", model_loaded: true}` | None | 500 if model failed to load | 200, 500 |

---

## 11. Environment Variables

| Variable | Used By | Stored Where | Why Required |
|---|---|---|---|
| `NEXT_PUBLIC_SUPABASE_URL` | Frontend | Vercel project env vars | Supabase client init for Auth session handling |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Frontend | Vercel project env vars | Public, restricted-scope key for Auth only |
| `NEXT_PUBLIC_API_BASE_URL` | Frontend | Vercel project env vars | Points `apiClient.ts` to the deployed FastAPI base URL |
| `SUPABASE_URL` | Backend | Render environment variables | Backend's Supabase client initialization |
| `SUPABASE_SERVICE_ROLE_KEY` | Backend | Render environment variables (secret) | Privileged server-side reads/writes; never exposed to frontend |
| `SUPABASE_JWT_SECRET` / JWKS URL | Backend | Render environment variables (secret) | Verifying tokens issued by Supabase Auth |
| `MODEL_PATH` | Backend | Render environment variables | Path to `loan_pipeline.pkl` inside the deployed container |
| `CORS_ALLOWED_ORIGINS` | Backend | Render environment variables | Restricts which frontend origin(s) may call the API |
| `LOG_LEVEL` | Backend | Render environment variables | Controls verbosity of structured logging |
| `ENVIRONMENT` | Backend/Frontend | Both platforms | Distinguishes dev/staging/production behavior |

---

## 12. Deployment Plan

- **GitHub repository setup:** One monorepo with `frontend/`, `backend/`, `ml/`, `docs/` at the root; branch protection on `main`; CI workflows run lint/test on every PR.
- **Backend deployment on Render:** Configure a Web Service pointing at `backend/`, build via `requirements.txt`/Dockerfile, set the start command to launch FastAPI (e.g., via `uvicorn`), attach all backend environment variables, and set a health check path to `/health`.
- **Frontend deployment on Vercel:** Import the repo, set the root directory to `frontend/`, configure build command/output automatically detected for Next.js, attach `NEXT_PUBLIC_*` env vars.
- **Supabase configuration:** Create the project, define the schema (Section 6), enable email/password auth, generate anon and service role keys, and restrict table access appropriately so only the service role can write to `loan_applications`.
- **Environment variable configuration across all three:** Mirror the variable list in Section 11 exactly in each platform's dashboard; never commit real secrets to the repo (`.env.example` files only).
- **Production testing:** Smoke test registration, login, loan submission, prediction, and officer status update against the live URLs before announcing go-live.
- **Monitoring:** Use Render's built-in logs/metrics and Vercel's analytics/logs; consider forwarding backend structured logs to an external log sink for longer retention.
- **Common deployment issues and fixes:**
  - *CORS errors:* Ensure `CORS_ALLOWED_ORIGINS` on Render exactly matches the Vercel production URL (and any preview URLs if needed).
  - *Env vars missing at build time:* Confirm `NEXT_PUBLIC_*` vars are set before the Vercel build runs, since they're baked in at build time, not runtime.
  - *Model loading errors:* Verify `MODEL_PATH` and that `loan_pipeline.pkl` is actually included in the deployed backend artifact (not excluded by `.gitignore` or Docker ignore rules).
  - *Build failures:* Check Python/Node version pinning matches what Render/Vercel expect; confirm `requirements.txt`/`package.json` are up to date.
- **Recovery steps:** Roll back to the last known-good deployment on Render/Vercel; if a bad model was deployed, redeploy backend with the previous `loan_pipeline.pkl` artifact; if Supabase schema changes broke the backend, apply a corrective migration and redeploy.

---

## 13. Testing Strategy

- **Machine Learning testing:** Validate the pipeline's preprocessing on edge-case inputs (missing fields, extreme values), and confirm evaluation metrics remain within acceptable bounds after any retraining.
- **Backend testing:** Unit tests for each service function (validation, business rules, status transition logic) and for the model loader/preprocessing functions, run against `backend/tests/`.
- **Frontend testing:** Component-level tests for forms, tables, and role-gated rendering; verify `apiClient.ts` handles success/error responses correctly.
- **API testing:** Exercise every endpoint in Section 10 for both valid and invalid inputs, confirming correct status codes and response shapes.
- **Integration testing:** End-to-end flows in `tests/integration/` covering full submission (customer) and full review (officer) lifecycles against a test Supabase project.
- **Database testing:** Confirm constraints/indexes behave as expected, and that audit fields are populated correctly on every transition.
- **User Acceptance Testing:** Walk through both the customer and officer journeys with stakeholders against the staging deployment to confirm the system meets the business requirements in the brief.
- **Deployment testing:** Post-deploy smoke tests (Section 12) on the live production URLs before wider rollout.

---

## 14. Documentation

| Document | Contents |
|---|---|
| `README.md` | Project overview, tech stack, quick start, folder map |
| `docs/PROJECT_REPORT.md` | Business problem, objectives, methodology, results, conclusions |
| `docs/BUSINESS_REQUIREMENTS.md` | Functional/non-functional requirements, assumptions, constraints, success criteria (as given in the brief) |
| `docs/API_DOCUMENTATION.md` | Full endpoint reference matching Section 10 |
| `docs/DATABASE_DOCUMENTATION.md` | Schema, relationships, indexes, lifecycle (Section 6/9) |
| `docs/DEPLOYMENT_GUIDE.md` | Step-by-step Vercel/Render/Supabase deployment (Section 12) |
| `docs/USER_MANUAL.md` | How-to guide for customers and officers using the live app |
| `docs/ARCHITECTURE.md` | Full architecture narrative and diagrams (Section 2) |
| `docs/INSTALLATION_GUIDE.md` | Local dev setup for frontend, backend, and ML environments |

---

## 15. Final Checklist

| Area | Status |
|---|---|
| Business Analysis (problem, objectives, requirements, success criteria) | ☐ Not Started |
| Repository Structure (all folders/files scaffolded) | ☐ Not Started |
| Machine Learning (data → training → `loan_pipeline.pkl`) | ☐ Not Started |
| Backend (FastAPI routers, services, auth, ML integration) | ☐ Not Started |
| Database (Supabase schema, roles, indexes) | ☐ Not Started |
| Frontend (single Next.js app, all route groups) | ☐ Not Started |
| Integration (full request lifecycles verified) | ☐ Not Started |
| Testing (unit, API, integration, UAT) | ☐ Not Started |
| Deployment (Vercel + Render + Supabase live) | ☐ Not Started |
| Documentation (all 9 docs authored) | ☐ Not Started |
| Project Completion (sign-off against success criteria) | ☐ Not Started |

*(Update each row to ☑ In Progress / ☑ Done as the team advances through the roadmap in Section 3.)*