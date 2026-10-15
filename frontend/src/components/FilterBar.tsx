/**
 * FilterBar - Status filter dropdown and search input.
 *
 * Debounces search input to avoid excessive API calls.
 * Calls parent's onFilterChange with both status and search values.
 */

"use client";

import { useState, useEffect } from "react";
import type { LeadStatus } from "@/types/lead";

interface FilterBarProps {
  onFilterChange: (filters: { status?: LeadStatus; search?: string }) => void;
  disabled?: boolean;
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
 * Filter controls for lead list.
 *
 * Features:
 * - Status dropdown (all statuses + "All")
 * - Search input with 300ms debounce
 * - Disabled state during loading
 *
 * @param onFilterChange - Callback when filters change
 * @param disabled - Disable inputs during loading
 */
export default function FilterBar({ onFilterChange, disabled }: FilterBarProps) {
  const [status, setStatus] = useState<LeadStatus | "">("");
  const [searchInput, setSearchInput] = useState("");

  // Debounce search input - only call onFilterChange after 300ms of no typing
  useEffect(() => {
    const timer = setTimeout(() => {
      const filters: { status?: LeadStatus; search?: string } = {};
      if (status) filters.status = status;
      if (searchInput.trim()) filters.search = searchInput.trim();
      onFilterChange(filters);
    }, 300);

    return () => clearTimeout(timer);
  }, [status, searchInput, onFilterChange]);

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
      <div className="flex flex-col sm:flex-row gap-4">
        {/* Status Filter */}
        <div className="flex-1">
          <label
            htmlFor="status-filter"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Status
          </label>
          <select
            id="status-filter"
            value={status}
            onChange={(e) => setStatus(e.target.value as LeadStatus | "")}
            disabled={disabled}
            className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
          >
            <option value="">All Statuses</option>
            {STATUSES.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </div>

        {/* Search Input */}
        <div className="flex-1">
          <label
            htmlFor="search-input"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Search
          </label>
          <input
            id="search-input"
            type="text"
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            placeholder="Search name or company..."
            disabled={disabled}
            className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
          />
        </div>

        {/* Clear Button */}
        {(status || searchInput) && (
          <div className="flex items-end">
            <button
              onClick={() => {
                setStatus("");
                setSearchInput("");
              }}
              disabled={disabled}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Clear
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
