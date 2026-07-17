"use client";

import { useCallback, useEffect, useState } from "react";
import { officerService } from "@/services/officerService";
import type { LoanApplicationRecord, LoanStatus, OfficerStatusUpdateRequest } from "@/types/loan";
import { ApiError } from "@/types/api";

interface UseOfficerApplicationsOptions {
  statusFilter?: LoanStatus | "";
  dateFrom?: string;
  dateTo?: string;
  pageSize?: number;
}

/**
 * Server-side paginated/filtered officer queue — unlike the customer's
 * small personal history (Milestone 3, paginated client-side), the full
 * application set can be large, so filtering and paging happen against
 * GET /officer/applications directly.
 */
export function useOfficerApplications({
  statusFilter,
  dateFrom,
  dateTo,
  pageSize = 10,
}: UseOfficerApplicationsOptions) {
  const [applications, setApplications] = useState<LoanApplicationRecord[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  const fetchApplications = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await officerService.listApplications({
        status: statusFilter || undefined,
        date_from: dateFrom,
        date_to: dateTo,
        page,
        page_size: pageSize,
      });
      setApplications(response.items);
      setTotal(response.total);
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Couldn't load the applications queue.");
    } finally {
      setIsLoading(false);
    }
  }, [statusFilter, dateFrom, dateTo, page, pageSize]);

  useEffect(() => {
    setPage(1);
  }, [statusFilter, dateFrom, dateTo]);

  useEffect(() => {
    void fetchApplications();
  }, [fetchApplications]);

  const updateStatus = useCallback(
    async (applicationId: string, payload: OfficerStatusUpdateRequest) => {
      const result = await officerService.updateApplicationStatus(applicationId, payload);
      setApplications((prev) =>
        prev.map((app) => (app.application_id === applicationId ? result.application : app))
      );
      return result;
    },
    []
  );

  return {
    applications,
    total,
    page,
    totalPages,
    setPage,
    nextPage: () => setPage((p) => Math.min(p + 1, totalPages)),
    prevPage: () => setPage((p) => Math.max(p - 1, 1)),
    isLoading,
    error,
    refetch: fetchApplications,
    updateStatus,
  };
}