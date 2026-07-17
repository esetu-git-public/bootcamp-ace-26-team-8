"use client";

import { use } from "react";
import { useApplicationDetail } from "@/hooks/useLoanApplications";
import { PredictionResultCard } from "@/components/customer/PredictionResultCard";
import { FullPageSpinner } from "@/components/ui/Spinner";
import { Alert } from "@/components/ui/Alert";

export default function ApplicationResultPage({
  params,
}: {
  params: Promise<{ applicationId: string }>;
}) {
  const { applicationId } = use(params);
  const { application, isLoading, error } = useApplicationDetail(applicationId);

  if (isLoading) return <FullPageSpinner label="Loading your result…" />;

  if (error || !application) {
    return (
      <div className="max-w-lg mx-auto mt-12">
        <Alert tone="danger" title="Couldn't load your result">
          {error ?? "This application couldn't be found."}
        </Alert>
      </div>
    );
  }

  return (
    <div className="py-6">
      <PredictionResultCard
        applicationId={application.application_id}
        prediction={application.prediction}
        probability={application.probability}
      />
    </div>
  );
}