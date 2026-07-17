import type { HTMLAttributes } from "react";
import { cn } from "@/lib/utils";
import type { LoanStatus } from "@/types/loan";
import { STATUS_LABELS } from "@/lib/constants";

type Tone = "success" | "warning" | "danger" | "neutral" | "brand";

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  tone?: Tone;
}

const toneClasses: Record<Tone, string> = {
  success: "bg-success-subtle text-success",
  warning: "bg-warning-subtle text-warning",
  danger: "bg-danger-subtle text-danger",
  brand: "bg-brand-subtle text-brand",
  neutral: "bg-surface-inset text-ink-muted",
};

export function Badge({ className, tone = "neutral", ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium",
        toneClasses[tone],
        className
      )}
      {...props}
    />
  );
}

const STATUS_TONE: Record<LoanStatus, Tone> = {
  submitted: "neutral",
  under_review: "brand",
  approved: "success",
  rejected: "danger",
  review_requested: "warning",
};

/** Convenience badge that maps a LoanStatus directly to the right tone + label. */
export function StatusBadge({ status, className }: { status: LoanStatus; className?: string }) {
  return (
    <Badge tone={STATUS_TONE[status]} className={className}>
      {STATUS_LABELS[status]}
    </Badge>
  );
}

/** Convenience badge for a 0/1 model prediction. */
export function RiskBadge({ prediction, className }: { prediction: 0 | 1; className?: string }) {
  return (
    <Badge tone={prediction === 1 ? "danger" : "success"} className={className}>
      {prediction === 1 ? "Default Risk" : "Low Risk"}
    </Badge>
  );
}