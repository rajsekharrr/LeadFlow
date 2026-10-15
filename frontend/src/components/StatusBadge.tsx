/**
 * StatusBadge - Display lead status with color-coded badge.
 *
 * Pure presentational component - no state or side effects.
 * Takes a status string and renders a colored pill with appropriate styling.
 */

"use client";

import type { LeadStatus } from "@/types/lead";

interface StatusBadgeProps {
  status: LeadStatus;
}

// Static color map - one-line change to add new status
const STATUS_COLORS: Record<LeadStatus, string> = {
  New: "bg-blue-100 text-blue-800",
  Contacted: "bg-purple-100 text-purple-800",
  Qualified: "bg-green-100 text-green-800",
  "Proposal Sent": "bg-yellow-100 text-yellow-800",
  Won: "bg-emerald-100 text-emerald-800",
  Lost: "bg-gray-100 text-gray-800",
};

/**
 * Renders a color-coded badge for lead status.
 *
 * @param status - Lead status from LeadStatus enum
 * @returns Styled span element with status text
 */
export default function StatusBadge({ status }: StatusBadgeProps) {
  const colorClass = STATUS_COLORS[status] || "bg-gray-100 text-gray-800";

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colorClass}`}
    >
      {status}
    </span>
  );
}
