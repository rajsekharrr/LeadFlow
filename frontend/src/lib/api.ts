/**
 * API client for LeadFlow backend.
 *
 * Provides typed functions for all backend endpoints.
 * Uses Axios for HTTP requests with automatic JSON handling.
 */

import axios, { AxiosError } from "axios";
import type {
  Lead,
  Discussion,
  CreateLeadRequest,
  UpdateLeadRequest,
  CreateDiscussionRequest,
  GetLeadsParams,
  APIError,
} from "@/types/lead";

/**
 * Axios instance configured with the backend base URL.
 */
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

/**
 * Error handler that extracts useful error messages from API responses.
 *
 * @param error - Axios error object
 * @returns User-friendly error message
 */
function handleAPIError(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<APIError>;

    // Server responded with error status
    if (axiosError.response) {
      const detail = axiosError.response.data?.detail;

      // Validation error (422) - format all errors
      if (Array.isArray(detail)) {
        return detail
          .map((err) => `${err.loc.join(".")}: ${err.msg}`)
          .join(", ");
      }

      // Simple error message (404, etc.)
      if (typeof detail === "string") {
        return detail;
      }

      // Fallback to status text
      return axiosError.response.statusText || "Request failed";
    }

    // Network error (no response)
    if (axiosError.request) {
      return "Cannot connect to server. Please ensure the backend is running.";
    }
  }

  // Unknown error
  return error instanceof Error ? error.message : "An unexpected error occurred";
}

// ==================== Lead API Functions ====================

/**
 * Get all leads with optional filtering.
 *
 * @param params - Optional status and search filters
 * @returns Promise resolving to array of leads
 */
export async function getLeads(params?: GetLeadsParams): Promise<Lead[]> {
  try {
    const response = await api.get<Lead[]>("/api/leads", { params });
    return response.data;
  } catch (error) {
    throw new Error(handleAPIError(error));
  }
}

/**
 * Get a single lead by ID.
 *
 * @param id - Lead UUID
 * @returns Promise resolving to lead object
 * @throws Error if lead not found (404)
 */
export async function getLead(id: string): Promise<Lead> {
  try {
    const response = await api.get<Lead>(`/api/leads/${id}`);
    return response.data;
  } catch (error) {
    throw new Error(handleAPIError(error));
  }
}

/**
 * Create a new lead.
 *
 * @param data - Lead creation data
 * @returns Promise resolving to created lead
 */
export async function createLead(data: CreateLeadRequest): Promise<Lead> {
  try {
    const response = await api.post<Lead>("/api/leads", data);
    return response.data;
  } catch (error) {
    throw new Error(handleAPIError(error));
  }
}

/**
 * Update a lead's status or follow-up date.
 *
 * @param id - Lead UUID
 * @param data - Fields to update (partial)
 * @returns Promise resolving to updated lead
 * @throws Error if lead not found (404)
 */
export async function updateLead(
  id: string,
  data: UpdateLeadRequest
): Promise<Lead> {
  try {
    const response = await api.patch<Lead>(`/api/leads/${id}`, data);
    return response.data;
  } catch (error) {
    throw new Error(handleAPIError(error));
  }
}

// ==================== Discussion API Functions ====================

/**
 * Get all discussions for a lead.
 *
 * @param leadId - Lead UUID
 * @returns Promise resolving to array of discussions (reverse chronological)
 * @throws Error if lead not found (404)
 */
export async function getDiscussions(leadId: string): Promise<Discussion[]> {
  try {
    const response = await api.get<Discussion[]>(
      `/api/leads/${leadId}/discussions`
    );
    return response.data;
  } catch (error) {
    throw new Error(handleAPIError(error));
  }
}

/**
 * Create a new discussion for a lead.
 *
 * If follow_up_at is provided, the parent lead's follow_up_at
 * is also updated atomically.
 *
 * @param leadId - Lead UUID
 * @param data - Discussion creation data
 * @returns Promise resolving to created discussion
 * @throws Error if lead not found (404)
 */
export async function createDiscussion(
  leadId: string,
  data: CreateDiscussionRequest
): Promise<Discussion> {
  try {
    const response = await api.post<Discussion>(
      `/api/leads/${leadId}/discussions`,
      data
    );
    return response.data;
  } catch (error) {
    throw new Error(handleAPIError(error));
  }
}

/**
 * Export the configured Axios instance for advanced use cases.
 */
export { api };
