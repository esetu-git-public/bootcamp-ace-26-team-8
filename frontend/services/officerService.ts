import { apiClient } from "@/services/apiClient";
import type {
  LoanApplicationListResponse,
  OfficerApplicationFilterParams,
  OfficerStatusUpdateRequest,
  OfficerStatusUpdateResponse,
} from "@/types/loan";

/**
 * Officer-facing operations. Mirrors backend/app/api/v1/routes_officer.py
 * exactly: GET /officer/applications (status/date_from/date_to/page/page_size
 * query params) and PATCH /officer/applications/{id} ({status, note}).
 */
export const officerService = {
  async listApplications(params: OfficerApplicationFilterParams = {}): Promise<LoanApplicationListResponse> {
    return apiClient.get<LoanApplicationListResponse>("/officer/applications", {
      query: {
        status: params.status,
        date_from: params.date_from,
        date_to: params.date_to,
        page: params.page ?? 1,
        page_size: params.page_size ?? 20,
      },
    });
  },

  async updateApplicationStatus(
    applicationId: string,
    payload: OfficerStatusUpdateRequest
  ): Promise<OfficerStatusUpdateResponse> {
    return apiClient.patch<OfficerStatusUpdateResponse>(`/officer/applications/${applicationId}`, payload);
  },
};