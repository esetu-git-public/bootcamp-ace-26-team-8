# Loan Default Prediction System — Architecture & Diagrams

This document consolidates the full system architecture and every diagram needed to understand how the system fits together: high-level architecture, component interaction, sequence flows, authentication flow, database ER diagram, deployment topology, and the loan status lifecycle.

> Diagrams are written in [Mermaid](https://mermaid.js.org/) syntax inside fenced code blocks. They render automatically on GitHub, GitLab, Obsidian, VS Code (with the Mermaid extension), and most modern Markdown viewers.

---

## Table of Contents

1. High-Level System Architecture
2. Component Interaction Diagram
3. Customer Loan Submission — Sequence Diagram
4. Officer Review — Sequence Diagram
5. Authentication & Role Routing Flow
6. Database ER Diagram
7. Loan Application Status Lifecycle (State Diagram)
8. Deployment Topology
9. Layered Architecture (Backend Internals)
10. Why This Architecture — Design Rationale Recap

---

## 1. High-Level System Architecture

```mermaid
flowchart TB
    subgraph Client["Client Layer"]
        A[Customer Browser]
        B[Officer Browser]
    end

    subgraph Frontend["Single Next.js Application (Vercel)"]
        direction TB
        F1["(auth) route group<br/>Login / Register"]
        F2["(customer) route group<br/>Apply / Track / Profile"]
        F3["(officer) route group<br/>Review / Analytics"]
    end

    subgraph Backend["FastAPI Backend (Render) — Single Gateway"]
        direction TB
        G1[Auth Verification]
        G2[Validation & Business Rules]
        G3[Preprocessing]
        G4[ML Prediction]
        G5[Persistence Layer]
    end

    subgraph ML["ML Layer — in-process only"]
        M1["loan_pipeline.pkl<br/>(loaded in FastAPI memory)"]
    end

    subgraph Data["Supabase"]
        D1[(Postgres:<br/>profiles, loan_applications)]
        D2[Supabase Auth]
    end

    A --> F1 & F2
    B --> F1 & F3
    F1 -.session.-> D2
    F2 -- HTTPS + JWT --> Backend
    F3 -- HTTPS + JWT --> Backend
    G1 --> G2 --> G3 --> G4 --> G5
    G4 <--> M1
    G1 -.verify token.-> D2
    G5 <--> D1

    style Frontend fill:#eef4ff,stroke:#4c6ef5
    style Backend fill:#fff4e6,stroke:#f08c00
    style ML fill:#fff0f6,stroke:#e64980
    style Data fill:#e6fcf5,stroke:#12b886
```

**Key rule visualized:** there is no arrow from the Frontend directly into `ML` or into `Data` — every path is mediated by the FastAPI Backend.

---

## 2. Component Interaction Diagram

```mermaid
graph LR
    Browser["Browser<br/>(Next.js rendered UI)"]
    API["FastAPI<br/>/api/v1/*"]
    Model["ML Pipeline<br/>(joblib-loaded)"]
    DB[("Supabase Postgres")]
    Auth["Supabase Auth"]

    Browser -- "1. HTTPS request + JWT" --> API
    API -- "2. verify JWT" --> Auth
    API -- "3. run inference" --> Model
    API -- "4. read/write records" --> DB
    API -- "5. JSON response" --> Browser

    classDef trust fill:#fff,stroke:#333,stroke-width:2px;
    class API trust;
```

FastAPI is the only node with edges to every other component — the trust boundary is drawn around it deliberately.

---

## 3. Customer Loan Submission — Sequence Diagram

```mermaid
sequenceDiagram
    actor C as Customer
    participant FE as Next.js Frontend
    participant API as FastAPI Backend
    participant ML as loan_pipeline.pkl
    participant DB as Supabase (Postgres)

    C->>FE: Fill & submit loan application form
    FE->>API: POST /loan/apply (JWT + payload)
    API->>API: Verify JWT, extract user_id/role
    API->>API: Validate payload (schema + business rules)
    API->>API: Preprocess features
    API->>ML: predict(features)
    ML-->>API: prediction, probability
    API->>API: Assemble complete loan record
    API->>DB: INSERT loan_applications (full record + prediction)
    DB-->>API: application_id
    API-->>FE: 201 { application_id, prediction, probability, status }
    FE-->>C: Display PredictionResultCard
```

---

## 4. Officer Review — Sequence Diagram

```mermaid
sequenceDiagram
    actor O as Loan Officer
    participant FE as Next.js Frontend (officer)
    participant API as FastAPI Backend
    participant DB as Supabase (Postgres)
    actor Cust as Customer (later)

    O->>FE: Open officer dashboard
    FE->>API: GET /officer/applications?status=pending (JWT)
    API->>API: Verify JWT, require role=officer
    API->>DB: SELECT loan_applications WHERE ...
    DB-->>API: Application rows
    API-->>FE: 200 [applications...]
    FE-->>O: Render queue table
    O->>FE: Choose Approve / Reject / Request Review
    FE->>API: PATCH /officer/applications/{id} { status, note }
    API->>API: Validate officer role + valid status transition
    API->>DB: UPDATE status, reviewed_by, reviewed_date, updated_date
    DB-->>API: Updated row
    API-->>FE: 200 { updated application }
    Note over Cust,DB: On next visit, customer dashboard fetch reflects new status
```

---

## 5. Authentication & Role Routing Flow

```mermaid
flowchart TD
    Start([User visits site]) --> HasSession{Has valid<br/>Supabase session?}
    HasSession -- No --> Login["(auth) Login / Register page"]
    Login --> SupabaseAuth[Supabase Auth issues JWT]
    SupabaseAuth --> RoleCheck

    HasSession -- Yes --> RoleCheck{Check role claim<br/>in middleware.ts}
    RoleCheck -- role = customer --> CustDash["(customer) dashboard"]
    RoleCheck -- role = officer --> OffDash["(officer) dashboard"]

    CustDash --> APICall1["Every data call → FastAPI<br/>(server re-verifies role)"]
    OffDash --> APICall2["Every data call → FastAPI<br/>(server re-verifies role)"]

    APICall1 -- role mismatch --> Reject1[403 Forbidden]
    APICall2 -- role mismatch --> Reject2[403 Forbidden]
```

**Important:** the frontend role check is for UX/routing convenience only. The authoritative check happens again on every FastAPI request — a customer JWT can never successfully call an officer-only endpoint, regardless of what the frontend renders.

---

## 6. Database ER Diagram

```mermaid
erDiagram
    PROFILES ||--o{ LOAN_APPLICATIONS : "submits"
    PROFILES ||--o{ LOAN_APPLICATIONS : "reviews (as officer)"

    PROFILES {
        uuid user_id PK
        string full_name
        string role "customer or officer"
        timestamp created_at
    }

    LOAN_APPLICATIONS {
        uuid application_id PK
        uuid user_id FK "applicant"
        string applicant_name
        string email
        string phone
        int age
        string employment_type
        numeric annual_income
        numeric loan_amount
        string loan_purpose
        int credit_score
        numeric existing_debt
        jsonb other_ml_features
        string prediction "Default / No Default"
        numeric prediction_probability
        string status "submitted, under_review, approved, rejected, review_requested"
        timestamp submitted_date
        uuid reviewed_by FK "officer"
        timestamp reviewed_date
        timestamp updated_date
    }
```

---

## 7. Loan Application Status Lifecycle (State Diagram)

```mermaid
stateDiagram-v2
    [*] --> submitted: Customer submits application<br/>(prediction generated & stored)
    submitted --> under_review: Officer opens application
    under_review --> approved: Officer approves
    under_review --> rejected: Officer rejects
    under_review --> review_requested: Officer requests more info
    review_requested --> under_review: Additional info reviewed
    approved --> [*]
    rejected --> [*]

    note right of submitted
        Prediction + probability
        are locked in at this point
        and never recomputed later.
    end note
```

---

## 8. Deployment Topology

```mermaid
flowchart LR
    subgraph GH["GitHub Monorepo"]
        FE_CODE["/frontend"]
        BE_CODE["/backend"]
        ML_CODE["/ml"]
    end

    subgraph Vercel["Vercel"]
        FE_DEPLOY["Next.js Build & Hosting"]
    end

    subgraph Render["Render"]
        BE_DEPLOY["FastAPI Web Service<br/>+ loan_pipeline.pkl bundled"]
    end

    subgraph SB["Supabase Cloud"]
        SB_DB[(Postgres)]
        SB_AUTH[Auth Service]
    end

    FE_CODE -- CI/CD on push --> FE_DEPLOY
    BE_CODE -- CI/CD on push --> BE_DEPLOY
    ML_CODE -- artifact copied into build --> BE_DEPLOY

    FE_DEPLOY -- "NEXT_PUBLIC_* env vars<br/>calls FastAPI only" --> BE_DEPLOY
    FE_DEPLOY -. "Auth session only" .-> SB_AUTH
    BE_DEPLOY -- "service role key" --> SB_DB
    BE_DEPLOY -- "verify JWT" --> SB_AUTH
```

---

## 9. Layered Architecture (Backend Internals)

```mermaid
flowchart TB
    subgraph API_Layer["API Layer (app/api/v1)"]
        R1[routes_auth.py]
        R2[routes_loans.py]
        R3[routes_predictions.py]
        R4[routes_officer.py]
        R5[routes_health.py]
    end

    subgraph Schema_Layer["Schema Layer (app/schemas)"]
        S1[loan_schema.py]
        S2[user_schema.py]
        S3[prediction_schema.py]
    end

    subgraph Service_Layer["Service Layer (app/services)"]
        SV1[prediction_service.py]
        SV2[loan_service.py]
        SV3[officer_service.py]
        SV4[supabase_service.py]
    end

    subgraph ML_Layer["ML Layer (app/ml)"]
        ML1[model_loader.py]
        ML2[preprocessing.py]
    end

    subgraph Core["Core (app/core)"]
        C1[config.py]
        C2[security.py]
        C3[logging.py]
    end

    R2 --> S1 --> SV2
    R3 --> S3 --> SV1
    R4 --> SV3
    SV1 --> ML2 --> ML1
    SV1 --> SV4
    SV2 --> SV4
    SV3 --> SV4
    R1 & R2 & R3 & R4 --> C2
    SV4 -.uses config.-> C1
```

---

## 10. Why This Architecture — Design Rationale Recap

- **Single gateway (FastAPI):** every business rule, validation step, and data mutation flows through one auditable service — no rule can be bypassed by calling Supabase or the model directly from the browser.
- **ML model isolated server-side:** the pipeline's schema, weights, and versioning stay private to the backend, and can be swapped/retrained without any frontend change.
- **Supabase kept "dumb":** used purely for Auth + Postgres storage, so all decisioning logic lives in one testable Python codebase rather than being split across database triggers and application code.
- **One Next.js app, two route groups:** avoids duplicated UI infrastructure while still giving customers and officers fully distinct experiences, gated by server-verified roles.
- **Prediction locked at submission time:** preserves an accurate, auditable record of what the model said when the applicant applied, independent of any later human review outcome.