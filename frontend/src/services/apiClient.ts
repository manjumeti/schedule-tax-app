import axios from "axios";
import type { ApiErrorPayload } from "@/types/schedules";

// Single Axios instance: base URL, timeouts, and interceptors live in one place
// so pages/hooks never configure HTTP concerns themselves.
export const apiClient = axios.create({
  baseURL: "/api/v1",
  timeout: 15_000,
  headers: { "Content-Type": "application/json" },
});

export class ApiError extends Error {
  readonly errorCode: string;
  readonly details?: Record<string, unknown>;
  readonly status?: number;

  constructor(payload: ApiErrorPayload, status?: number) {
    super(payload.message);
    this.errorCode = payload.error_code;
    this.details = payload.details;
    this.status = status;
  }
}

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (axios.isAxiosError(error) && error.response?.data?.error_code) {
      throw new ApiError(error.response.data as ApiErrorPayload, error.response.status);
    }
    throw error;
  }
);
