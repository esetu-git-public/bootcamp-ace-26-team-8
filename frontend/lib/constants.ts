import type { EducationLevel, EmploymentType, LoanPurpose, LoanStatus, MaritalStatus, YesNo } from "@/types/loan";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

export const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL ?? "";
export const SUPABASE_ANON_KEY = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ?? "";

export const APP_NAME = "Ledger";
export const APP_FULL_NAME = "Loan Default Prediction System";

/** Route targets — kept centralized so a routing-structure fix only
 * needs to change one file. See README note on the (customer)/(officer)
 * route-group collision pending resolution. */
export const ROUTES = {
  home: "/",
  login: "/login",
  register: "/register",
  forgotPassword: "/forgot-password",
  resetPassword: "/reset-password",
  about: "/about",
  faq: "/faq",
  contact: "/contact",
  customerDashboard: "/customer/dashboard",
  customerApply: "/customer/apply",
  customerApplications: "/customer/applications",
  customerProfile: "/customer/profile",
  officerDashboard: "/officer/dashboard",
  officerApplications: "/officer/applications",
  officerAnalytics: "/officer/analytics",
} as const;

export const EDUCATION_LEVELS: EducationLevel[] = ["High School", "Bachelor's", "Master's", "PhD"];

export const EMPLOYMENT_TYPES: EmploymentType[] = [
  "Full-time",
  "Part-time",
  "Self-employed",
  "Unemployed",
];

export const MARITAL_STATUSES: MaritalStatus[] = ["Single", "Married", "Divorced"];

export const YES_NO: YesNo[] = ["Yes", "No"];

export const LOAN_PURPOSES: LoanPurpose[] = ["Auto", "Business", "Education", "Home", "Other"];

export const LOAN_STATUSES: LoanStatus[] = [
  "submitted",
  "under_review",
  "approved",
  "rejected",
  "review_requested",
];

export const STATUS_LABELS: Record<LoanStatus, string> = {
  submitted: "Submitted",
  under_review: "Under Review",
  approved: "Approved",
  rejected: "Rejected",
  review_requested: "Review Requested",
};

/** Valid officer transition targets — mirrors officer_service.py's
 * _VALID_TRANSITIONS, used only for client-side UX hints; the backend
 * remains the source of truth and re-validates every transition. */
export const VALID_STATUS_TRANSITIONS: Record<LoanStatus, LoanStatus[]> = {
  submitted: ["under_review", "approved", "rejected", "review_requested"],
  under_review: ["approved", "rejected", "review_requested"],
  review_requested: ["under_review", "approved", "rejected"],
  approved: [],
  rejected: ["review_requested"],
};