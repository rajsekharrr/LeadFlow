/**
 * useLeads - Custom React hook for lead management.
 *
 * Single source of truth for lead list state, loading, errors, and mutations.
 * Provides optimistic updates for status changes and discussion creation.
 */

"use client";

import { useState, useEffect, useCallback } from "react";
import {
  getLeads as apiGetLeads,
  createLead as apiCreateLead,
  updateLead as apiUpdateLead,
  createDiscussion as apiCreateDiscussion,
} from "@/lib/api";
import type {
  Lead,
  CreateLeadRequest,
  CreateDiscussionRequest,
  LeadStatus,
} from "@/types/lead";

interface UseLeadsState {
  leads: Lead[];
  loading: boolean;
  error: string | null;
}

interface UseLeadsReturn extends UseLeadsState {
  fetchLeads: (filters?: { status?: LeadStatus; search?: string }) => Promise<void>;
  addLead: (data: CreateLeadRequest) => Promise<Lead>;
  updateLeadStatus: (leadId: string, status: LeadStatus) => Promise<void>;
  addDiscussion: (
    leadId: string,
    data: CreateDiscussionRequest
  ) => Promise<void>;
  refreshLead: (leadId: string) => Promise<void>;
}

/**
 * Custom hook for managing lead list state and operations.
 *
 * Features:
 * - Fetches and caches lead list
 * - Supports status and search filtering
 * - Optimistic updates for better UX
 * - Automatic error handling
 * - Single source of truth for lead data
 *
 * @returns Lead state and mutation functions
 */
export function useLeads(): UseLeadsReturn {
  const [state, setState] = useState<UseLeadsState>({
    leads: [],
    loading: true,
    error: null,
  });

  /**
   * Fetch leads from API with optional filters.
   * Replaces entire lead list in state.
   *
   * @param filters - Optional status and search filters
   */
  const fetchLeads = useCallback(
    async (filters?: { status?: LeadStatus; search?: string }) => {
      setState((prev) => ({ ...prev, loading: true, error: null }));

      try {
        const leads = await apiGetLeads(filters);
        setState({ leads, loading: false, error: null });
      } catch (error) {
        setState((prev) => ({
          ...prev,
          loading: false,
          error: error instanceof Error ? error.message : "Failed to fetch leads",
        }));
      }
    },
    []
  );

  /**
   * Create a new lead.
   * Adds to local state immediately (optimistic update).
   *
   * @param data - Lead creation data
   * @returns Created lead with server-assigned ID
   */
  const addLead = useCallback(async (data: CreateLeadRequest): Promise<Lead> => {
    try {
      const newLead = await apiCreateLead(data);

      // Add to local state
      setState((prev) => ({
        ...prev,
        leads: [newLead, ...prev.leads], // Prepend to list
        error: null,
      }));

      return newLead;
    } catch (error) {
      setState((prev) => ({
        ...prev,
        error: error instanceof Error ? error.message : "Failed to create lead",
      }));
      throw error;
    }
  }, []);

  /**
   * Update a lead's status with optimistic update.
   * Updates local state immediately, rolls back on error.
   *
   * @param leadId - Lead UUID
   * @param status - New status value
   */
  const updateLeadStatus = useCallback(
    async (leadId: string, status: LeadStatus): Promise<void> => {
      // Store previous state for rollback
      const previousLeads = state.leads;

      // Optimistic update - update UI immediately
      setState((prev) => ({
        ...prev,
        leads: prev.leads.map((lead) =>
          lead.id === leadId
            ? { ...lead, status, updated_at: new Date().toISOString() }
            : lead
        ),
        error: null,
      }));

      try {
        // Send request to backend
        await apiUpdateLead(leadId, { status });
      } catch (error) {
        // Rollback on error
        setState((prev) => ({
          ...prev,
          leads: previousLeads,
          error:
            error instanceof Error ? error.message : "Failed to update lead status",
        }));
        throw error;
      }
    },
    [state.leads]
  );

  /**
   * Add a discussion to a lead with optimistic update.
   * Updates lead's last_note, last_discussion_at, and discussion_count.
   * If follow_up_at is provided, also updates the lead's follow_up_at.
   *
   * @param leadId - Lead UUID
   * @param data - Discussion creation data
   */
  const addDiscussion = useCallback(
    async (leadId: string, data: CreateDiscussionRequest): Promise<void> => {
      // Store previous state for rollback
      const previousLeads = state.leads;
      const now = new Date().toISOString();

      // Optimistic update - update lead immediately
      setState((prev) => ({
        ...prev,
        leads: prev.leads.map((lead) =>
          lead.id === leadId
            ? {
                ...lead,
                last_note: data.note,
                last_discussion_at: now,
                discussion_count: lead.discussion_count + 1,
                // Update follow_up_at if provided in discussion
                follow_up_at: data.follow_up_at ?? lead.follow_up_at,
                updated_at: now,
              }
            : lead
        ),
        error: null,
      }));

      try {
        // Send request to backend
        await apiCreateDiscussion(leadId, data);

        // Note: Backend returns the created discussion, but we don't need it
        // since we already updated the lead optimistically
      } catch (error) {
        // Rollback on error
        setState((prev) => ({
          ...prev,
          leads: previousLeads,
          error:
            error instanceof Error
              ? error.message
              : "Failed to create discussion",
        }));
        throw error;
      }
    },
    [state.leads]
  );

  /**
   * Refresh a single lead from the backend.
   * Useful after operations where we want fresh computed fields.
   *
   * @param leadId - Lead UUID
   */
  const refreshLead = useCallback(async (leadId: string): Promise<void> => {
    try {
      // Note: This would require getLead(id) function from API
      // For now, we'll just refetch all leads
      // In a production app, you'd fetch just the one lead
      await fetchLeads();
    } catch (error) {
      setState((prev) => ({
        ...prev,
        error:
          error instanceof Error ? error.message : "Failed to refresh lead",
      }));
    }
  }, [fetchLeads]);

  // Initial fetch on mount
  useEffect(() => {
    fetchLeads();
  }, [fetchLeads]);

  return {
    leads: state.leads,
    loading: state.loading,
    error: state.error,
    fetchLeads,
    addLead,
    updateLeadStatus,
    addDiscussion,
    refreshLead,
  };
}
