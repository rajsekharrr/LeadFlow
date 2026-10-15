/**
 * TimelineDialog - Discussion history and new note form for a lead.
 *
 * Most complex component - handles:
 * - Fetching discussions from API
 * - Displaying timeline in reverse chronological order
 * - Adding new discussions with optional follow-up
 * - Changing lead status
 * - Loading, error, and empty states
 */

"use client";

import { useState, useEffect } from "react";
import { parseISO, formatDistanceToNow, format } from "date-fns";
import StatusBadge from "./StatusBadge";
import { getDiscussions, createDiscussion as apiCreateDiscussion } from "@/lib/api";
import type { Lead, Discussion, LeadStatus } from "@/types/lead";

interface TimelineDialogProps {
  lead: Lead | null;
  onClose: () => void;
  onStatusChange: (leadId: string, status: LeadStatus) => Promise<void>;
  onDiscussionAdded: (leadId: string, note: string, followUpAt?: string) => Promise<void>;
}

const STATUSES: LeadStatus[] = [
  "New",
  "Contacted",
  "Qualified",
  "Proposal Sent",
  "Won",
  "Lost",
];

/**
 * Full-screen dialog showing lead timeline and actions.
 *
 * Features:
 * - Discussion history (reverse chronological)
 * - Add new discussion with optional follow-up
 * - Change lead status
 * - Show lead details
 * - Loading and error states
 *
 * @param lead - Lead to show (null = closed)
 * @param onClose - Handler to close dialog
 * @param onStatusChange - Handler to update lead status
 * @param onDiscussionAdded - Handler to add discussion
 */
export default function TimelineDialog({
  lead,
  onClose,
  onStatusChange,
  onDiscussionAdded,
}: TimelineDialogProps) {
  const [discussions, setDiscussions] = useState<Discussion[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form state
  const [note, setNote] = useState("");
  const [followUpDate, setFollowUpDate] = useState("");
  const [followUpTime, setFollowUpTime] = useState("");
  const [submitting, setSubmitting] = useState(false);

  // Status change state
  const [changingStatus, setChangingStatus] = useState(false);

  // Fetch discussions when lead changes
  useEffect(() => {
    if (!lead) {
      setDiscussions([]);
      return;
    }

    const fetchDiscussions = async () => {
      setLoading(true);
      setError(null);

      try {
        const data = await getDiscussions(lead.id);
        setDiscussions(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load discussions");
      } finally {
        setLoading(false);
      }
    };

    fetchDiscussions();
  }, [lead]);

  if (!lead) return null;

  const handleSubmitDiscussion = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!note.trim() || submitting) return;

    setSubmitting(true);
    setError(null);

    try {
      // Build follow-up datetime if both date and time provided
      let followUpAt: string | undefined;
      if (followUpDate && followUpTime) {
        followUpAt = `${followUpDate}T${followUpTime}:00`;
      }

      // Call parent handler (updates lead in useLeads hook)
      await onDiscussionAdded(lead.id, note.trim(), followUpAt);

      // Refresh discussions list
      const updatedDiscussions = await getDiscussions(lead.id);
      setDiscussions(updatedDiscussions);

      // Reset form
      setNote("");
      setFollowUpDate("");
      setFollowUpTime("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to add discussion");
    } finally {
      setSubmitting(false);
    }
  };

  const handleStatusChange = async (newStatus: LeadStatus) => {
    if (newStatus === lead.status || changingStatus) return;

    setChangingStatus(true);
    setError(null);

    try {
      await onStatusChange(lead.id, newStatus);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update status");
    } finally {
      setChangingStatus(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
        onClick={onClose}
      />

      {/* Dialog */}
      <div className="flex min-h-full items-start justify-center p-4 sm:p-6 lg:p-8">
        <div className="relative bg-white rounded-lg shadow-xl max-w-4xl w-full my-8">
          {/* Header */}
          <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 rounded-t-lg">
            <div className="flex items-start justify-between">
              <div className="flex-1 min-w-0">
                <h2 className="text-2xl font-bold text-gray-900 truncate">
                  {lead.name}
                </h2>
                {lead.company && (
                  <p className="text-sm text-gray-600 mt-1">{lead.company}</p>
                )}
                {lead.phone && (
                  <p className="text-sm text-gray-600">{lead.phone}</p>
                )}
              </div>
              <button
                onClick={onClose}
                className="ml-4 text-gray-400 hover:text-gray-500"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            </div>

            {/* Status Change */}
            <div className="mt-4 flex items-center gap-3">
              <label className="text-sm font-medium text-gray-700">Status:</label>
              <select
                value={lead.status}
                onChange={(e) => handleStatusChange(e.target.value as LeadStatus)}
                disabled={changingStatus}
                className="rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm disabled:bg-gray-100 disabled:cursor-not-allowed"
              >
                {STATUSES.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
              <StatusBadge status={lead.status} />
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mx-6 mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          {/* Content */}
          <div className="p-6">
            {/* New Discussion Form */}
            <div className="bg-gray-50 rounded-lg p-4 mb-6">
              <h3 className="text-sm font-semibold text-gray-900 mb-3">
                Add Discussion Note
              </h3>
              <form onSubmit={handleSubmitDiscussion} className="space-y-3">
                <div>
                  <textarea
                    value={note}
                    onChange={(e) => setNote(e.target.value)}
                    placeholder="Enter discussion notes..."
                    disabled={submitting}
                    rows={3}
                    className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed text-sm"
                    required
                  />
                </div>

                {/* Follow-up Date/Time */}
                <div className="flex gap-3">
                  <div className="flex-1">
                    <label className="block text-xs font-medium text-gray-700 mb-1">
                      Follow-up Date (optional)
                    </label>
                    <input
                      type="date"
                      value={followUpDate}
                      onChange={(e) => setFollowUpDate(e.target.value)}
                      disabled={submitting}
                      className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm disabled:bg-gray-100"
                    />
                  </div>
                  <div className="flex-1">
                    <label className="block text-xs font-medium text-gray-700 mb-1">
                      Time
                    </label>
                    <input
                      type="time"
                      value={followUpTime}
                      onChange={(e) => setFollowUpTime(e.target.value)}
                      disabled={submitting || !followUpDate}
                      className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm disabled:bg-gray-100"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={submitting || !note.trim()}
                  className="w-full px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                >
                  {submitting ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Saving...
                    </>
                  ) : (
                    "Add Note"
                  )}
                </button>
              </form>
            </div>

            {/* Discussion Timeline */}
            <div>
              <h3 className="text-sm font-semibold text-gray-900 mb-3">
                Discussion History ({discussions.length})
              </h3>

              {loading && (
                <div className="flex items-center justify-center py-8">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                  <span className="ml-2 text-sm text-gray-600">Loading discussions...</span>
                </div>
              )}

              {!loading && discussions.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  <svg
                    className="mx-auto h-10 w-10 text-gray-400 mb-2"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                    />
                  </svg>
                  <p className="text-sm">No discussions yet</p>
                  <p className="text-xs mt-1">Add your first note above</p>
                </div>
              )}

              {!loading && discussions.length > 0 && (
                <div className="space-y-4">
                  {discussions.map((discussion) => (
                    <div
                      key={discussion.id}
                      className="border border-gray-200 rounded-lg p-4 bg-white"
                    >
                      <div className="flex justify-between items-start mb-2">
                        <span className="text-xs text-gray-500">
                          {formatDistanceToNow(parseISO(discussion.created_at), {
                            addSuffix: true,
                          })}
                        </span>
                        <span className="text-xs text-gray-400">
                          {format(parseISO(discussion.created_at), "MMM d, yyyy 'at' h:mm a")}
                        </span>
                      </div>
                      <p className="text-sm text-gray-900 whitespace-pre-wrap">
                        {discussion.note}
                      </p>
                      {discussion.follow_up_at && (
                        <div className="mt-2 text-xs text-blue-600 flex items-center gap-1">
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                            />
                          </svg>
                          Follow-up: {format(parseISO(discussion.follow_up_at), "MMM d, yyyy 'at' h:mm a")}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
