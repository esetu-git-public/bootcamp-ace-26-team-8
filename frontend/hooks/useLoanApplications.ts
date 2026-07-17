"use client";

import { useCallback, useEffect, useState } from "react";
import { loanService } from "@/services/loanService";
import type { LoanApplicationRecord } from "@/types/loan";
import { ApiError } from "@/types/api";

interface UseLoanApplicationsResult {
  applications: LoanApplicationRecord[];
  total: number;
  isLoading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

/** Fetches and caches the authenticated customer's own application history. */
export function useLoanApplications(): UseLoanApplicationsResult {
  const [applications, setApplications] = useState<LoanApplicationRecord[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchApplications = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await loanService.getMyApplications();
      setApplications(response.items);
      setTotal(response.total);
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Couldn't load your applications.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void fetchApplications();
  }, [fetchApplications]);

  return { applications, total, isLoading, error, refetch: fetchApplications };
}

interface UseApplicationDetailResult {
  application: LoanApplicationRecord | null;
  isLoading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

/** Fetches a single application's full detail (owner or officer, per backend rules). */
export function useApplicationDetail(applicationId: string): UseApplicationDetailResult {
  const [application, setApplication] = useState<LoanApplicationRecord | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchApplication = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const record = await loanService.getApplicationById(applicationId);
      setApplication(record);
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.status === 404
            ? "This application doesn't exist or has been removed."
            : err.detail
          : "Couldn't load this application."
      );
    } finally {
      setIsLoading(false);
    }
  }, [applicationId]);

  useEffect(() => {
    void fetchApplication();
  }, [fetchApplication]);

  return { application, isLoading, error, refetch: fetchApplication };
}