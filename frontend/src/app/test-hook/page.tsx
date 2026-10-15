/**
 * Test page for useLeads hook verification.
 *
 * Tests all hook functionality:
 * - Initial load
 * - Filtering by status
 * - Search
 * - Create lead
 * - Update lead status
 * - Add discussion
 */

"use client";

import { useState } from "react";
import { useLeads } from "@/hooks/useLeads";
import type { LeadStatus } from "@/types/lead";

export default function TestUseLeads() {
  const {
    leads,
    loading,
    error,
    fetchLeads,
    addLead,
    updateLeadStatus,
    addDiscussion,
  } = useLeads();

  const [statusFilter, setStatusFilter] = useState<LeadStatus | "">("");
  const [searchQuery, setSearchQuery] = useState("");
  const [testResults, setTestResults] = useState<string[]>([]);

  const log = (message: string) => {
    console.log(message);
    setTestResults((prev) => [...prev, `${new Date().toLocaleTimeString()}: ${message}`]);
  };

  const handleFilter = () => {
    const filters: { status?: LeadStatus; search?: string } = {};
    if (statusFilter) filters.status = statusFilter;
    if (searchQuery) filters.search = searchQuery;
    fetchLeads(filters);
    log(`Applied filters - Status: ${statusFilter || "none"}, Search: ${searchQuery || "none"}`);
  };

  const handleCreateLead = async () => {
    try {
      const newLead = await addLead({
        name: "Test Lead " + Date.now(),
        company: "Test Company",
        status: "New",
      });
      log(`✓ Created lead: ${newLead.name} (ID: ${newLead.id})`);
    } catch (err) {
      log(`✗ Failed to create lead: ${err}`);
    }
  };

  const handleUpdateStatus = async () => {
    if (leads.length === 0) {
      log("✗ No leads to update");
      return;
    }

    const firstLead = leads[0];
    const newStatus: LeadStatus = firstLead.status === "New" ? "Contacted" : "New";

    try {
      await updateLeadStatus(firstLead.id, newStatus);
      log(`✓ Updated ${firstLead.name} status to ${newStatus}`);
    } catch (err) {
      log(`✗ Failed to update status: ${err}`);
    }
  };

  const handleAddDiscussion = async () => {
    if (leads.length === 0) {
      log("✗ No leads to add discussion to");
      return;
    }

    const firstLead = leads[0];

    try {
      await addDiscussion(firstLead.id, {
        note: "Test discussion added at " + new Date().toLocaleTimeString(),
      });
      log(`✓ Added discussion to ${firstLead.name}`);
    } catch (err) {
      log(`✗ Failed to add discussion: ${err}`);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">
          useLeads Hook Test Page
        </h1>

        {/* Hook State */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Hook State</h2>
          <div className="space-y-2 font-mono text-sm">
            <div>
              <strong>Loading:</strong> {loading ? "true" : "false"}
            </div>
            <div>
              <strong>Error:</strong> {error || "null"}
            </div>
            <div>
              <strong>Leads Count:</strong> {leads.length}
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Filters</h2>
          <div className="flex gap-4 mb-4">
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as LeadStatus | "")}
              className="border rounded px-3 py-2"
            >
              <option value="">All Statuses</option>
              <option value="New">New</option>
              <option value="Contacted">Contacted</option>
              <option value="Qualified">Qualified</option>
              <option value="Proposal Sent">Proposal Sent</option>
              <option value="Won">Won</option>
              <option value="Lost">Lost</option>
            </select>

            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search..."
              className="border rounded px-3 py-2 flex-1"
            />

            <button
              onClick={handleFilter}
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            >
              Apply Filters
            </button>

            <button
              onClick={() => {
                setStatusFilter("");
                setSearchQuery("");
                fetchLeads();
                log("Cleared filters");
              }}
              className="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700"
            >
              Clear
            </button>
          </div>
        </div>

        {/* Actions */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Actions</h2>
          <div className="flex gap-4">
            <button
              onClick={handleCreateLead}
              className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
            >
              Create Lead
            </button>

            <button
              onClick={handleUpdateStatus}
              className="bg-yellow-600 text-white px-4 py-2 rounded hover:bg-yellow-700"
              disabled={leads.length === 0}
            >
              Update First Lead Status
            </button>

            <button
              onClick={handleAddDiscussion}
              className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700"
              disabled={leads.length === 0}
            >
              Add Discussion to First Lead
            </button>
          </div>
        </div>

        {/* Test Results Log */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Test Results</h2>
            <button
              onClick={() => setTestResults([])}
              className="text-sm text-gray-600 hover:text-gray-900"
            >
              Clear Log
            </button>
          </div>
          <div className="bg-gray-50 rounded p-4 max-h-64 overflow-y-auto">
            {testResults.length === 0 ? (
              <p className="text-gray-500 text-sm">No actions yet. Click buttons above to test.</p>
            ) : (
              <div className="space-y-1 font-mono text-sm">
                {testResults.map((result, i) => (
                  <div key={i} className="text-gray-700">
                    {result}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Lead List */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">
            Leads ({leads.length})
          </h2>

          {loading && (
            <div className="text-center py-8 text-gray-500">
              Loading leads...
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          {!loading && !error && leads.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              No leads found
            </div>
          )}

          {!loading && leads.length > 0 && (
            <div className="space-y-3">
              {leads.map((lead) => (
                <div
                  key={lead.id}
                  className="border rounded-lg p-4 hover:bg-gray-50"
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-semibold text-gray-900">
                        {lead.name}
                      </h3>
                      {lead.company && (
                        <p className="text-sm text-gray-600">{lead.company}</p>
                      )}
                    </div>
                    <span
                      className={`px-3 py-1 rounded-full text-sm font-medium ${
                        lead.status === "New"
                          ? "bg-blue-100 text-blue-800"
                          : lead.status === "Won"
                          ? "bg-green-100 text-green-800"
                          : "bg-gray-100 text-gray-800"
                      }`}
                    >
                      {lead.status}
                    </span>
                  </div>

                  <div className="mt-3 text-sm text-gray-600 space-y-1">
                    <div>
                      <strong>Discussions:</strong> {lead.discussion_count}
                    </div>
                    {lead.last_note && (
                      <div>
                        <strong>Last note:</strong> {lead.last_note}
                      </div>
                    )}
                    {lead.follow_up_at && (
                      <div>
                        <strong>Follow-up:</strong>{" "}
                        {new Date(lead.follow_up_at).toLocaleString()}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
