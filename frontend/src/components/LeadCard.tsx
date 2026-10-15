/**
 * LeadCard - Single lead row in the list.
 *
 * Shows lead name, company, status, last discussion note, and time ago.
 * Highlights overdue follow-ups with red border.
 * Pins today's follow-ups with blue border and pin icon.
 */

"use client";

import { parseISO, formatDistanceToNow, isToday, isPast } from "date-fns";
import StatusBadge from "./StatusBadge";
import type { Lead } from "@/types/lead";

interface LeadCardProps {
  lead: Lead;
  onClick: () => void;
  isPinned?: boolean;
}

/**
 * Renders a single lead card with all relevant information.
 *
 * Visual indicators:
 * - Blue left border + pin icon = Today's follow-up (pinned)
 * - Red left border = Overdue follow-up
 * - Gray border = Normal lead
 *
 * @param lead - Lead data
 * @param onClick - Handler when card is clicked
 * @param isPinned - True if this lead has today's follow-up (pinned to top)
 */
export default function LeadCard({ lead, onClick, isPinned }: LeadCardProps) {
  // Determine if follow-up is overdue
  const isOverdue =
    lead.follow_up_at &&
    !isToday(parseISO(lead.follow_up_at)) &&
    isPast(parseISO(lead.follow_up_at));

  // Border color based on follow-up status
  const borderColor = isPinned
    ? "border-l-blue-500 border-l-4"
    : isOverdue
    ? "border-l-red-500 border-l-4"
    : "border-gray-200";

  return (
    <div
      onClick={onClick}
      className={`bg-white border ${borderColor} rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer`}
    >
      {/* Header: Name, Company, Status */}
      <div className="flex justify-between items-start mb-2">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            {isPinned && (
              <svg
                className="w-4 h-4 text-blue-500 flex-shrink-0"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path d="M10 2a1 1 0 011 1v1.323l3.954 1.582 1.599-.8a1 1 0 01.894 1.79l-1.233.616 1.738 5.42a1 1 0 01-.285 1.05A3.989 3.989 0 0115 15a3.989 3.989 0 01-2.667-1.019 1 1 0 01-.285-1.05l1.738-5.42-1.233-.617a1 1 0 01.894-1.788l1.599.799L11 4.323V3a1 1 0 011-1zm-5 8.274l-.818 2.552c-.25.78-.03 1.632.548 2.148.578.515 1.45.553 2.084.1L10 13.9l3.186 1.174c.633.453 1.506.415 2.084-.1.578-.516.798-1.369.548-2.148L15 10.274v-1.638a1 1 0 00-2 0v1.638l-.545 1.697L10 13.382l-2.455-1.411L7 10.274V8.636a1 1 0 00-2 0v1.638z" />
              </svg>
            )}
            <h3 className="text-lg font-semibold text-gray-900 truncate">
              {lead.name}
            </h3>
          </div>
          {lead.company && (
            <p className="text-sm text-gray-600 truncate">{lead.company}</p>
          )}
        </div>
        <StatusBadge status={lead.status} />
      </div>

      {/* Last Discussion Note */}
      {lead.last_note && (
        <p className="text-sm text-gray-700 mb-2 line-clamp-2">
          {lead.last_note}
        </p>
      )}

      {/* Footer: Discussion count, Time ago, Follow-up */}
      <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-gray-500">
        {/* Discussion count */}
        <span className="flex items-center gap-1">
          <svg
            className="w-4 h-4"
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
          {lead.discussion_count} {lead.discussion_count === 1 ? "note" : "notes"}
        </span>

        {/* Time since last discussion */}
        {lead.last_discussion_at && (
          <span>
            Last activity{" "}
            {formatDistanceToNow(parseISO(lead.last_discussion_at), {
              addSuffix: true,
            })}
          </span>
        )}

        {/* Follow-up indicator */}
        {lead.follow_up_at && (
          <span className={isPinned ? "text-blue-600 font-medium" : isOverdue ? "text-red-600 font-medium" : ""}>
            Follow-up:{" "}
            {isPinned
              ? "Today"
              : isOverdue
              ? "Overdue"
              : formatDistanceToNow(parseISO(lead.follow_up_at), {
                  addSuffix: true,
                })}
          </span>
        )}
      </div>
    </div>
  );
}
