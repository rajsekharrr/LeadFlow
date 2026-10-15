/**
 * TypeScript type definitions for LeadFlow.
 *
 * These types match the backend API contract exactly.
 * They provide type safety for API requests and responses.
 */

/**
 * Lead status enum.
 * Must match the backend's LeadStatus enum values exactly.
 */
export type LeadStatus =
  | "New"
  | "Contacted"
  | "Qualified"
  | "Proposal Sent"
  | "Won"
  | "Lost";

/**
 * Lead response from the API.
 * Includes all database fields plus computed fields.
 */
export interface Lead {
  id: string;
  name: string;
  company: string | null;
  phone: string | null;
  status: LeadStatus;
  follow_up_at: string | null;  // ISO datetime string
  created_at: string;            // ISO datetime string
  updated_at: string;            // ISO datetime string

  // Computed fields (added by backend CRUD layer)
  last_note: string | null;
  last_discussion_at: string | null;  // ISO datetime string
  discussion_count: number;
}

/**
 * Discussion response from the API.
 */
export interface Discussion {
  id: string;
  lead_id: string;
  note: string;
  follow_up_at: string | null;  // ISO datetime string
  created_at: string;            // ISO datetime string
}

/**
 * Request payload for creating a new lead.
 */
export interface CreateLeadRequest {
  name: string;
  company?: string | null;
  phone?: string | null;
  status?: LeadStatus;
}

/**
 * Request payload for updating a lead.
 * All fields are optional (PATCH semantics).
 */
export interface UpdateLeadRequest {
  status?: LeadStatus;
  follow_up_at?: string | null;  // ISO datetime string
}

/**
 * Request payload for creating a discussion.
 */
export interface CreateDiscussionRequest {
  note: string;
  follow_up_at?: string | null;  // ISO datetime string
}

/**
 * Query parameters for listing leads.
 */
export interface GetLeadsParams {
  status?: LeadStatus;
  search?: string;
}

/**
 * API error response structure.
 */
export interface APIError {
  detail: string | Array<{
    type: string;
    loc: string[];
    msg: string;
  }>;
}
