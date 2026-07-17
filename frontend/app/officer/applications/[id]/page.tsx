"use client";

import { use } from "react";
import { useApplicationDetail } from "@/hooks/useLoanApplications";
import { officerService } from "@/services/officerService";
import { ApplicationDetailPanel } from "@/components/officer/ApplicationDetailPanel";
import { FullPageSpinner } from "@/components/ui/Spinner";
import { Alert } from "@/components/ui/Alert";

export default function OfficerApplicationDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);

  const { application, isLoading, error, refetch } = useApplicationDetail(id);

  if (isLoading) {
    return <FullPageSpinner label="Loading application…" />;
  }

  if (error || !application) {
    return (
      <Alert tone="danger" title="Couldn't load this application">
        {error ?? "This application couldn't be found."}
      </Alert>
    );
  }

  return (
    <ApplicationDetailPanel
      application={application}
      onUpdate={async (applicationId, payload) => {
        const result = await officerService.updateApplicationStatus(
          applicationId,
          payload
        );
        await refetch();
        return result;
      }}
    />
  );
}
