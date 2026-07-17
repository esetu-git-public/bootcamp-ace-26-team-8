"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { officerStatusUpdateSchema, type OfficerStatusUpdateFormValues } from "@/lib/validators";
import { Modal } from "@/components/ui/Modal";
import { Textarea } from "@/components/ui/Textarea";
import { Button } from "@/components/ui/Button";
import { Alert } from "@/components/ui/Alert";
import { STATUS_LABELS } from "@/lib/constants";
import { ApiError } from "@/types/api";
import type { LoanStatus } from "@/types/loan";

interface StatusUpdateModalProps {
  isOpen: boolean;
  onClose: () => void;
  targetStatus: LoanStatus | null;
  onConfirm: (values: OfficerStatusUpdateFormValues) => Promise<void>;
}

const toneByStatus: Record<string, "primary" | "danger" | "secondary"> = {
  approved: "primary",
  rejected: "danger",
  review_requested: "secondary",
  under_review: "secondary",
};

export function StatusUpdateModal({ isOpen, onClose, targetStatus, onConfirm }: StatusUpdateModalProps) {
  const [formError, setFormError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<OfficerStatusUpdateFormValues>({
    resolver: zodResolver(officerStatusUpdateSchema),
    values: targetStatus ? { status: targetStatus, note: "" } : undefined,
  });

  if (!targetStatus) return null;

  const submit = async (values: OfficerStatusUpdateFormValues) => {
    setFormError(null);
    setIsSubmitting(true);
    try {
      await onConfirm(values);
      reset();
      onClose();
    } catch (err) {
      setFormError(err instanceof ApiError ? err.detail : "Couldn't update this application. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={`${STATUS_LABELS[targetStatus]} this application`}
      description="A reviewer note is required and will be visible to the applicant."
    >
      <form onSubmit={handleSubmit(submit)} noValidate className="flex flex-col gap-4">
        {formError && <Alert tone="danger">{formError}</Alert>}
        <Textarea
          label="Reviewer note"
          required
          placeholder="Explain the reasoning behind this decision…"
          error={errors.note?.message}
          {...register("note")}
        />
        <div className="flex justify-end gap-2 pt-1">
          <Button type="button" variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" variant={toneByStatus[targetStatus]} isLoading={isSubmitting}>
            Confirm {STATUS_LABELS[targetStatus].toLowerCase()}
          </Button>
        </div>
      </form>
    </Modal>
  );
}