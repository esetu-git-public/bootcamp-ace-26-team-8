import { Check, Clock, X, RotateCcw } from "lucide-react";
import type { LoanStatus } from "@/types/loan";
import { cn, formatDateTime } from "@/lib/utils";

interface ApplicationStatusTimelineProps {
  status: LoanStatus;
  submittedDate: string;
  reviewedDate: string | null;
  reviewNote: string | null;
}

const terminalConfig: Record<string, { icon: typeof Check; tone: string; label: string }> = {
  approved: { icon: Check, tone: "text-success bg-success-subtle", label: "Approved" },
  rejected: { icon: X, tone: "text-danger bg-danger-subtle", label: "Rejected" },
  review_requested: { icon: RotateCcw, tone: "text-warning bg-warning-subtle", label: "Review requested" },
};

export function ApplicationStatusTimeline({
  status,
  submittedDate,
  reviewedDate,
  reviewNote,
}: ApplicationStatusTimelineProps) {
  const isReviewed = status !== "submitted" && status !== "under_review";
  const terminal = terminalConfig[status];

  return (
    <ol className="relative border-l-2 border-border ml-3 space-y-8">
      <li className="ml-6">
        <span className="absolute -left-[9px] flex h-4 w-4 items-center justify-center rounded-full bg-brand">
          <Check className="h-2.5 w-2.5 text-white" />
        </span>
        <p className="text-sm font-medium text-ink">Application submitted</p>
        <p className="text-xs text-ink-muted mt-0.5">{formatDateTime(submittedDate)}</p>
      </li>

      <li className="ml-6">
        <span
          className={cn(
            "absolute -left-[9px] flex h-4 w-4 items-center justify-center rounded-full",
            status === "under_review" || isReviewed ? "bg-brand" : "bg-surface-inset border-2 border-border"
          )}
        >
          {(status === "under_review" || isReviewed) && <Clock className="h-2.5 w-2.5 text-white" />}
        </span>
        <p className={cn("text-sm font-medium", status === "under_review" || isReviewed ? "text-ink" : "text-ink-faint")}>
          Under officer review
        </p>
        {status === "under_review" && <p className="text-xs text-ink-muted mt-0.5">In progress</p>}
      </li>

      <li className="ml-6">
        <span
          className={cn(
            "absolute -left-[9px] flex h-4 w-4 items-center justify-center rounded-full",
            terminal ? terminal.tone : "bg-surface-inset border-2 border-border"
          )}
        >
          {terminal && <terminal.icon className="h-2.5 w-2.5" />}
        </span>
        <p className={cn("text-sm font-medium", terminal ? "text-ink" : "text-ink-faint")}>
          {terminal ? terminal.label : "Decision pending"}
        </p>
        {reviewedDate && <p className="text-xs text-ink-muted mt-0.5">{formatDateTime(reviewedDate)}</p>}
        {reviewNote && (
          <p className="text-xs text-ink-muted mt-2 bg-surface-muted border border-border rounded p-2.5 max-w-md">
            "{reviewNote}"
          </p>
        )}
      </li>
    </ol>
  );
}