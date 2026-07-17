/**
 * Shared HTTP/error envelope types. Mirrors the centralized handler in
 * backend/app/middleware/error_handler.py, which always returns the
 * app.schemas.user_schema.ErrorResponse shape: {detail, status_code,
 * request_id}, regardless of which layer raised the exception.
 */

export interface ApiErrorResponse {
    detail: string;
    status_code: number;
    request_id: string | null;
  }
  
  /** Thrown by apiClient.ts on any non-2xx response. */
  export class ApiError extends Error {
    status: number;
    requestId: string | null;
    detail: string;
  
    constructor(detail: string, status: number, requestId: string | null = null) {
      super(detail);
      this.name = "ApiError";
      this.status = status;
      this.detail = detail;
      this.requestId = requestId;
    }
  }
  
  export type ApiMethod = "GET" | "POST" | "PATCH" | "PUT" | "DELETE";
  
  export interface RequestOptions {
    method?: ApiMethod;
    body?: unknown;
    query?: Record<string, string | number | boolean | undefined>;
    signal?: AbortSignal;
  }