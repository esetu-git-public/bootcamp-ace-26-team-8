"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Check } from "lucide-react";
import { loanApplicationSchema, type LoanApplicationFormValues } from "@/lib/validators";
import { loanService } from "@/services/loanService";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { Button } from "@/components/ui/Button";
import { Alert } from "@/components/ui/Alert";
import { cn } from "@/lib/utils";
import {
  EDUCATION_LEVELS,
  EMPLOYMENT_TYPES,
  LOAN_PURPOSES,
  MARITAL_STATUSES,
  YES_NO,
} from "@/lib/constants";
import { ApiError } from "@/types/api";

const STEPS = ["Personal details", "Financial profile", "Loan details", "Review & submit"] as const;

const personalFields: (keyof LoanApplicationFormValues)[] = ["applicant_name", "email", "phone"];
const financialFields: (keyof LoanApplicationFormValues)[] = [
  "income",
  "credit_score",
  "employment_type",
  "months_employed",
  "num_credit_lines",
  "dti_ratio",
];
const loanFields: (keyof LoanApplicationFormValues)[] = [
  "loan_amount",
  "loan_term",
  "interest_rate",
  "loan_purpose",
  "education",
  "marital_status",
  "has_mortgage",
  "has_dependents",
  "has_co_signer",
  "age",
];

const toOptions = (values: readonly string[]) => values.map((v) => ({ label: v, value: v }));

export function LoanApplicationForm() {
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [formError, setFormError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    trigger,
    formState: { errors },
  } = useForm<LoanApplicationFormValues>({
    resolver: zodResolver(loanApplicationSchema),
    mode: "onBlur",
  });

  const stepFieldMap = [personalFields, financialFields, loanFields, []];

  const goNext = async () => {
    const valid = await trigger(stepFieldMap[step] as (keyof LoanApplicationFormValues)[]);
    if (valid) setStep((s) => Math.min(s + 1, STEPS.length - 1));
  };
  const goBack = () => setStep((s) => Math.max(s - 1, 0));

  const onSubmit = async (values: LoanApplicationFormValues) => {
    setFormError(null);
    setIsSubmitting(true);
    try {
      const response = await loanService.submitApplication(values as never);
      router.push(`/customer/apply/${response.application_id}/result`);
    } catch (err) {
      setFormError(err instanceof ApiError ? err.detail : "Couldn't submit your application. Please try again.");
      setIsSubmitting(false);
    }
  };

  return (
    <div>
      <ol className="flex items-center gap-2 mb-8">
        {STEPS.map((label, index) => (
          <li key={label} className="flex items-center gap-2 flex-1">
            <div
              className={cn(
                "flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-xs font-medium figure",
                index < step
                  ? "bg-brand text-white"
                  : index === step
                  ? "bg-brand-subtle text-brand border-2 border-brand"
                  : "bg-surface-inset text-ink-faint"
              )}
            >
              {index < step ? <Check className="h-3.5 w-3.5" /> : index + 1}
            </div>
            <span className={cn("text-xs hidden sm:block", index === step ? "text-ink font-medium" : "text-ink-muted")}>
              {label}
            </span>
            {index < STEPS.length - 1 && <div className="flex-1 h-px bg-border" />}
          </li>
        ))}
      </ol>

      {formError && (
        <Alert tone="danger" className="mb-5">
          {formError}
        </Alert>
      )}

      <form onSubmit={handleSubmit(onSubmit)} noValidate>
        {step === 0 && (
          <div className="grid sm:grid-cols-2 gap-4 animate-fade-in">
            <Input
              label="Full name"
              required
              error={errors.applicant_name?.message}
              className="sm:col-span-2"
              {...register("applicant_name")}
            />
            <Input label="Email" type="email" required error={errors.email?.message} {...register("email")} />
            <Input label="Phone" required error={errors.phone?.message} {...register("phone")} />
            <Input
              label="Age"
              type="number"
              required
              isFigure
              error={errors.age?.message}
              {...register("age")}
            />
          </div>
        )}

        {step === 1 && (
          <div className="grid sm:grid-cols-2 gap-4 animate-fade-in">
            <Input
              label="Annual Income (₹)"
              type="number"
              step="0.01"
              required
              isFigure
              error={errors.income?.message}
              {...register("income")}
            />
            <Input
              label="Credit score"
              type="number"
              required
              isFigure
              hint="Between 300 and 850"
              error={errors.credit_score?.message}
              {...register("credit_score")}
            />
            <Select
              label="Employment type"
              required
              options={toOptions(EMPLOYMENT_TYPES)}
              error={errors.employment_type?.message}
              {...register("employment_type")}
            />
            <Input
              label="Months employed"
              type="number"
              required
              isFigure
              error={errors.months_employed?.message}
              {...register("months_employed")}
            />
            <Input
              label="Number of open credit lines"
              type="number"
              required
              isFigure
              error={errors.num_credit_lines?.message}
              {...register("num_credit_lines")}
            />
            <Input
              label="Debt-to-income ratio"
              type="number"
              step="0.01"
              required
              isFigure
              hint="A decimal between 0 and 1, e.g. 0.32"
              error={errors.dti_ratio?.message}
              {...register("dti_ratio")}
            />
          </div>
        )}

        {step === 2 && (
          <div className="grid sm:grid-cols-2 gap-4 animate-fade-in">
            <Input
              label="Loan Amount (₹)"
              type="number"
              step="0.01"
              required
              isFigure
              error={errors.loan_amount?.message}
              {...register("loan_amount")}
            />
            <Input
              label="Loan term (months)"
              type="number"
              required
              isFigure
              error={errors.loan_term?.message}
              {...register("loan_term")}
            />
            <Input
              label="Proposed interest rate (%)"
              type="number"
              step="0.01"
              required
              isFigure
              error={errors.interest_rate?.message}
              {...register("interest_rate")}
            />
            <Select
              label="Loan purpose"
              required
              options={toOptions(LOAN_PURPOSES)}
              error={errors.loan_purpose?.message}
              {...register("loan_purpose")}
            />
            <Select
              label="Education level"
              required
              options={toOptions(EDUCATION_LEVELS)}
              error={errors.education?.message}
              {...register("education")}
            />
            <Select
              label="Marital status"
              required
              options={toOptions(MARITAL_STATUSES)}
              error={errors.marital_status?.message}
              {...register("marital_status")}
            />
            <Select
              label="Existing mortgage?"
              required
              options={toOptions(YES_NO)}
              error={errors.has_mortgage?.message}
              {...register("has_mortgage")}
            />
            <Select
              label="Has dependents?"
              required
              options={toOptions(YES_NO)}
              error={errors.has_dependents?.message}
              {...register("has_dependents")}
            />
            <Select
              label="Has a co-signer?"
              required
              options={toOptions(YES_NO)}
              error={errors.has_co_signer?.message}
              {...register("has_co_signer")}
            />
          </div>
        )}

        {step === 3 && (
          <div className="animate-fade-in">
            <Alert tone="info" title="Ready to submit">
              Your application will be scored the moment you submit it. Double-check your details
              — identity fields (name, email, phone) can't be edited after submission.
            </Alert>
          </div>
        )}

        <div className="flex items-center justify-between mt-8">
          <Button type="button" variant="outline" onClick={goBack} disabled={step === 0}>
            Back
          </Button>
          {step < STEPS.length - 1 ? (
            <Button type="button" onClick={goNext}>
              Continue
            </Button>
          ) : (
            <Button type="submit" isLoading={isSubmitting}>
              Submit application
            </Button>
          )}
        </div>
      </form>
    </div>
  );
}