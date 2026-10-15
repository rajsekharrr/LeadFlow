/**
 * LeadList - Container for lead cards with pinning logic.
 *
 * Pins today's follow-ups to the top of the list.
 * Handles loading, error, and empty states.
 * Uses useLeads hook for data and filters.
 */

"use client";

import { isToday, parseISO } from "date-fns";
import LeadCard from "./LeadCard";
import type { Lead } from "@/types/lead";

interface LeadListProps {
  leads: Lead[];
  loading: boolean;
  error: string | null;
  onLeadClick: (lead: Lead) => void;
}

/**
 * Renders list of leads with today's follow-ups pinned to top.
 *
 * Pinning logic:
 * - Leads with follow_up_at = today are pinned
 * - Pinned leads shown first, then regular leads
 * - Both groups maintain their original order
 *
 * @param leads - Array of leads to display
 * @param loading - Loading state
 * @param error - Error message if any
 * @param onLeadClick - Handler when a lead card is clicked
 */
export default function LeadList({
  leads,
  loading,
  error,
  onLeadClick,
}: LeadListProps) {
  // Separate pinned (today's follow-up) and regular leads
  const pinnedLeads = leads.filter(
    (lead) => lead.follow_up_at && isToday(parseISO(lead.follow_up_at))
  );
  const regularLeads = leads.filter(
    (lead) => !lead.follow_up_at || !isToday(parseISO(lead.follow_up_at))
  );

  // Loading state
  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
        <div className="flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-3 text-gray-600">Loading leads...</span>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-red-200 p-6">
        <div className="flex items-start gap-3">
          <svg
            className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
              clipRule="evenodd"
            />
          </svg>
          <div>
            <h3 className="text-sm font-medium text-red-800">
              Failed to load leads
            </h3>
            <p className="mt-1 text-sm text-red-700">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  // Empty state
  if (leads.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
        <svg
          className="mx-auto h-12 w-12 text-gray-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
          />
        </svg>
        <h3 className="mt-2 text-sm font-medium text-gray-900">No leads found</h3>
        <p className="mt-1 text-sm text-gray-500">
          Get started by adding a new lead.
        </p>
      </div>
    );
  }

  // Lead list with pinned section
  return (
    <div className="space-y-4">
      {/* Pinned Section Header */}
      {pinnedLeads.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-3">
            <svg
              className="w-5 h-5 text-blue-600"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path d="M10 2a1 1 0 011 1v1.323l3.954 1.582 1.599-.8a1 1 0 01.894 1.79l-1.233.616 1.738 5.42a1 1 0 01-.285 1.05A3.989 3.989 0 0115 15a3.989 3.989 0 01-2.667-1.019 1 1 0 01-.285-1.05l1.738-5.42-1.233-.617a1 1 0 01.894-1.788l1.599.799L11 4.323V3a1 1 0 011-1zm-5 8.274l-.818 2.552c-.25.78-.03 1.632.548 2.148.578.515 1.45.553 2.084.1L10 13.9l3.186 1.174c.633.453 1.506.415 2.084-.1.578-.516.798-1.369.548-2.148L15 10.274v-1.638a1 1 0 00-2 0v1.638l-.545 1.697L10 13.382l-2.455-1.411L7 10.274V8.636a1 1 0 00-2 0v1.638z" />
            </svg>
            <h2 className="text-sm font-semibold text-blue-900 uppercase tracking-wide">
              Follow up today ({pinnedLeads.length})
            </h2>
          </div>
          <div className="space-y-3 mb-6">
            {pinnedLeads.map((lead) => (
              <LeadCard
                key={lead.id}
                lead={lead}
                onClick={() => onLeadClick(lead)}
                isPinned={true}
              />
            ))}
          </div>
        </div>
      )}

      {/* Regular Leads Section */}
      {regularLeads.length > 0 && (
        <div>
          {pinnedLeads.length > 0 && (
            <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-3">
              All Leads ({regularLeads.length})
            </h2>
          )}
          <div className="space-y-3">
            {regularLeads.map((lead) => (
              <LeadCard
                key={lead.id}
                lead={lead}
                onClick={() => onLeadClick(lead)}
                isPinned={false}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
