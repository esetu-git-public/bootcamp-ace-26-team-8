import { apiClient } from "@/services/apiClient";
import type {
  LoanApplicationListResponse,
  LoanApplicationRecord,
  LoanApplicationRequest,
  LoanApplicationSubmitResponse,
} from "@/types/loan";

/**
 * All customer-facing loan operations. Mirrors backend/app/api/v1/routes_loans.py
 * exactly: POST /loan/apply, GET /loan/applications, GET /loan/applications/{id}.
 * No table is ever queried directly — every call goes through apiClient to FastAPI.
 */
export const loanService = {
  async submitApplication(payload: LoanApplicationRequest): Promise<LoanApplicationSubmitResponse> {
    return apiClient.post<LoanApplicationSubmitResponse>("/loan/apply", payload);
  },

  async getMyApplications(): Promise<LoanApplicationListResponse> {
    return apiClient.get<LoanApplicationListResponse>("/loan/applications");
  },

  async getApplicationById(applicationId: string): Promise<LoanApplicationRecord> {
    return apiClient.get<LoanApplicationRecord>(`/loan/applications/${applicationId}`);
  },
};