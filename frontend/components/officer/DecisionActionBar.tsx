"use client";

import { useState } from "react";
import { Check, X, RotateCcw, Clock } from "lucide-react";

import { Button } from "@/components/ui/Button";
import { StatusUpdateModal } from "@/components/officer/StatusUpdateModal";
import { VALID_STATUS_TRANSITIONS } from "@/lib/constants";

import type {
  LoanStatus,
  OfficerStatusUpdateRequest,
  OfficerStatusUpdateResponse,
} from "@/types/loan";

interface DecisionActionBarProps {
  applicationId: string;
  currentStatus: LoanStatus;
  onUpdate: (
    applicationId: string,
    payload: OfficerStatusUpdateRequest
  ) => Promise<OfficerStatusUpdateResponse>;
}

const actionConfig: Record<
  string,
  {
    label: string;
    icon: typeof Check;
    variant: "primary" | "danger" | "outline" | "secondary";
  }
> = {
  approved: {
    label: "Approve",
    icon: Check,
    variant: "primary",
  },
  rejected: {
    label: "Reject",
    icon: X,
    variant: "danger",
  },
  review_requested: {
    label: "Request Review",
    icon: RotateCcw,
    variant: "outline",
  },
  under_review: {
    label: "Move to Under Review",
    icon: Clock,
    variant: "secondary",
  },
};

export function DecisionActionBar({
  applicationId,
  currentStatus,
  onUpdate,
}: DecisionActionBarProps) {
  const [targetStatus, setTargetStatus] = useState<LoanStatus | null>(null);

  const validTargets =
    VALID_STATUS_TRANSITIONS[currentStatus] ?? [];

  if (validTargets.length === 0) {
    return (
      <p className="text-sm text-gray-500">
        This application has reached a final status.
      </p>
    );
  }

  return (
    <>
      <div className="flex flex-wrap gap-2">
        {validTargets.map((status) => {
          const config = actionConfig[status];
          const Icon = config.icon;

          return (
            <Button
              key={status}
              variant={config.variant}
              onClick={() => setTargetStatus(status)}
            >
              <Icon className="mr-2 h-4 w-4" />
              {config.label}
            </Button>
          );
        })}
      </div>

      <StatusUpdateModal
        isOpen={targetStatus !== null}
        onClose={() => setTargetStatus(null)}
        targetStatus={targetStatus}
        onConfirm={async (values) => {
          await onUpdate(applicationId, values);
        }}
      />
    </>
  );
}