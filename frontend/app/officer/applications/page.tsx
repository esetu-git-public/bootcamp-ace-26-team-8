"use client";

import { useState } from "react";
import { Tabs } from "@/components/ui/Tabs";
import { ApplicationsQueueTable } from "@/components/officer/ApplicationsQueueTable";
import { useOfficerApplications } from "@/hooks/useOfficerApplications";
import { Alert } from "@/components/ui/Alert";
import type { LoanStatus } from "@/types/loan";
import { LOAN_STATUSES, STATUS_LABELS } from "@/lib/constants";

export default function OfficerApplicationsPage() {
  const [statusFilter, setStatusFilter] = useState<LoanStatus | "">("");

  const { applications, total, page, totalPages, setPage, nextPage, prevPage, isLoading, error } =
    useOfficerApplications({ statusFilter, pageSize: 10 });

  const tabs = [
    { label: "All", value: "" },
    ...LOAN_STATUSES.map((status) => ({ label: STATUS_LABELS[status], value: status })),
  ];

  return (
    <div>
      <div className="mb-6">
        <h1 className="font-display font-semibold text-2xl text-ink">Applications</h1>
        <p className="text-sm text-ink-muted mt-1">
          <span className="figure">{total}</span> total application{total === 1 ? "" : "s"}.
        </p>
      </div>

      {error && (
        <Alert tone="danger" className="mb-6">
          {error}
        </Alert>
      )}

      <div className="mb-4">
        <Tabs tabs={tabs} activeValue={statusFilter} onChange={(v) => setStatusFilter(v as LoanStatus | "")} />
      </div>

      <ApplicationsQueueTable
        applications={applications}
        isLoading={isLoading}
        page={page}
        totalPages={totalPages}
        onPrev={prevPage}
        onNext={nextPage}
        onPageSelect={setPage}
      />
    </div>
  );
}