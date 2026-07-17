/**
 * Mirrors backend/app/schemas/loan_schema.py and prediction_schema.py
 * exactly — enum string values are the literal values the trained
 * loan_pipeline.pkl encoders expect (ml/src/data_cleaning.py
 * CATEGORICAL_LABEL_MAP). Do not alter these string literals.
 */

export type EducationLevel = "High School" | "Bachelor's" | "Master's" | "PhD";

export type EmploymentType = "Full-time" | "Part-time" | "Self-employed" | "Unemployed";

export type MaritalStatus = "Single" | "Married" | "Divorced";

export type YesNo = "Yes" | "No";

export type LoanPurpose = "Auto" | "Business" | "Education" | "Home" | "Other";

export type LoanStatus =
  | "submitted"
  | "under_review"
  | "approved"
  | "rejected"
  | "review_requested";

/** Request body for POST /api/v1/loan/apply */
export interface LoanApplicationRequest {
  applicant_name: string;
  email: string;
  phone: string;
  age: number;
  income: number;
  loan_amount: number;
  credit_score: number;
  months_employed: number;
  num_credit_lines: number;
  interest_rate: number;
  loan_term: number;
  dti_ratio: number;
  education: EducationLevel;
  employment_type: EmploymentType;
  marital_status: MaritalStatus;
  has_mortgage: YesNo;
  has_dependents: YesNo;
  loan_purpose: LoanPurpose;
  has_co_signer: YesNo;
}

/** Response body for POST /api/v1/loan/apply */
export interface LoanApplicationSubmitResponse {
  application_id: string;
  prediction: 0 | 1;
  probability: number;
  status: LoanStatus;
}

/** Full persisted record — GET /loan/applications, /loan/applications/{id}, officer endpoints */
export interface LoanApplicationRecord {
  application_id: string;
  user_id: string;
  applicant_name: string;
  email: string;
  phone: string;
  age: number;
  income: number;
  loan_amount: number;
  credit_score: number;
  months_employed: number;
  num_credit_lines: number;
  interest_rate: number;
  loan_term: number;
  dti_ratio: number;
  education: EducationLevel;
  employment_type: EmploymentType;
  marital_status: MaritalStatus;
  has_mortgage: YesNo;
  has_dependents: YesNo;
  loan_purpose: LoanPurpose;
  has_co_signer: YesNo;
  prediction: 0 | 1;
  probability: number;
  status: LoanStatus;
  submitted_date: string;
  reviewed_by: string | null;
  reviewed_date: string | null;
  updated_date: string | null;
  review_note: string | null;
}

export interface LoanApplicationListResponse {
  total: number;
  items: LoanApplicationRecord[];
}

/** Request body for POST /api/v1/predictions/predict (ML-relevant subset only) */
export interface PredictionRequest {
  age: number;
  income: number;
  loan_amount: number;
  credit_score: number;
  months_employed: number;
  num_credit_lines: number;
  interest_rate: number;
  loan_term: number;
  dti_ratio: number;
  education: EducationLevel;
  employment_type: EmploymentType;
  marital_status: MaritalStatus;
  has_mortgage: YesNo;
  has_dependents: YesNo;
  loan_purpose: LoanPurpose;
  has_co_signer: YesNo;
}

export interface PredictionResponse {
  prediction: 0 | 1;
  probability: number;
  risk_label: string;
  top_features: Record<string, number> | null;
}

/** PATCH /api/v1/officer/applications/{id} */
export interface OfficerStatusUpdateRequest {
  status: LoanStatus;
  note: string;
}

export interface OfficerStatusUpdateResponse {
  application_id: string;
  status: LoanStatus;
  reviewed_by: string;
  reviewed_date: string;
  note: string;
  application: LoanApplicationRecord;
}

export interface OfficerApplicationFilterParams {
  status?: LoanStatus;
  date_from?: string;
  date_to?: string;
  page?: number;
  page_size?: number;
}

/** GET /api/v1/health */
export interface HealthCheckResponse {
  status: "ok";
  model_loaded: boolean;
  model_path: string;
  model_version: string | null;
}