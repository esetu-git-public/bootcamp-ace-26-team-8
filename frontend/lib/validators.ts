import { z } from "zod";
import {
  EDUCATION_LEVELS,
  EMPLOYMENT_TYPES,
  LOAN_PURPOSES,
  MARITAL_STATUSES,
  YES_NO,
} from "@/lib/constants";

/** Client-side mirror of backend/app/schemas/loan_schema.py::LoanApplicationRequest.
 * Ranges match Pydantic Field constraints exactly so users see validation
 * errors before a round trip; the backend remains the source of truth. */
export const loanApplicationSchema = z.object({
  applicant_name: z.string().min(2, "Enter the applicant's full name").max(150),
  email: z.string().email("Enter a valid email address"),
  phone: z
    .string()
    .min(7, "Enter a valid phone number")
    .max(20)
    .refine((v) => v.replace(/\D/g, "").length >= 7, "Phone number must contain at least 7 digits"),
  age: z.coerce.number().int().min(18, "Applicant must be at least 18").max(100),
  income: z.coerce.number().positive("Annual income must be greater than 0"),
  loan_amount: z.coerce.number().positive("Loan amount must be greater than 0"),
  credit_score: z.coerce.number().int().min(300).max(850),
  months_employed: z.coerce.number().int().min(0).max(720),
  num_credit_lines: z.coerce.number().int().min(0).max(50),
  interest_rate: z.coerce.number().min(0).max(100),
  loan_term: z.coerce.number().int().positive().max(480),
  dti_ratio: z.coerce.number().min(0).max(1, "Debt-to-income ratio must be between 0 and 1"),
  education: z.enum(EDUCATION_LEVELS as [string, ...string[]]),
  employment_type: z.enum(EMPLOYMENT_TYPES as [string, ...string[]]),
  marital_status: z.enum(MARITAL_STATUSES as [string, ...string[]]),
  has_mortgage: z.enum(YES_NO as [string, ...string[]]),
  has_dependents: z.enum(YES_NO as [string, ...string[]]),
  loan_purpose: z.enum(LOAN_PURPOSES as [string, ...string[]]),
  has_co_signer: z.enum(YES_NO as [string, ...string[]]),
});

export type LoanApplicationFormValues = z.infer<typeof loanApplicationSchema>;

export const loginSchema = z.object({
  email: z.string().email("Enter a valid email address"),
  password: z.string().min(8, "Password must be at least 8 characters"),
});

export type LoginFormValues = z.infer<typeof loginSchema>;

export const registerSchema = z
  .object({
    fullName: z.string().min(2, "Enter your full name").max(150),
    email: z.string().email("Enter a valid email address"),
    role: z.enum(["customer", "officer"]),
    password: z.string().min(8, "Password must be at least 8 characters"),
    confirmPassword: z.string().min(8, "Confirm your password"),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords do not match",
    path: ["confirmPassword"],
  });

export type RegisterFormValues = z.infer<typeof registerSchema>;

export const forgotPasswordSchema = z.object({
  email: z.string().email("Enter a valid email address"),
});

export type ForgotPasswordFormValues = z.infer<typeof forgotPasswordSchema>;

export const contactSchema = z.object({
  name: z.string().min(2, "Enter your name"),
  email: z.string().email("Enter a valid email address"),
  message: z.string().min(10, "Message must be at least 10 characters").max(2000),
});

export type ContactFormValues = z.infer<typeof contactSchema>;

export const officerStatusUpdateSchema = z.object({
  status: z.enum(["approved", "rejected", "review_requested", "under_review"]),
  note: z.string().min(3, "A reviewer note is required").max(1000),
});

export type OfficerStatusUpdateFormValues = z.infer<typeof officerStatusUpdateSchema>;