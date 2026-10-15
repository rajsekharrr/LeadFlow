"use client";

import { useState } from "react";
import { useLeads } from "@/hooks/useLeads";
import FilterBar from "@/components/FilterBar";
import LeadList from "@/components/LeadList";
import AddLeadModal from "@/components/AddLeadModal";
import TimelineDialog from "@/components/TimelineDialog";
import type { Lead, LeadStatus } from "@/types/lead";

export default function Home() {
  const {
    leads,
    loading,
    error,
    fetchLeads,
    addLead,
    updateLeadStatus,
    addDiscussion,
  } = useLeads();

  // Modal/dialog state
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null);

  // Handle filter changes
  const handleFilterChange = (filters: { status?: LeadStatus; search?: string }) => {
    fetchLeads(filters);
  };

  // Handle create lead
  const handleCreateLead = async (data: {
    name: string;
    company?: string;
    phone?: string;
    status?: LeadStatus;
  }) => {
    await addLead(data);
  };

  // Handle status change
  const handleStatusChange = async (leadId: string, status: LeadStatus) => {
    await updateLeadStatus(leadId, status);
  };

  // Handle add discussion
  const handleAddDiscussion = async (
    leadId: string,
    note: string,
    followUpAt?: string
  ) => {
    await addDiscussion(leadId, { note, follow_up_at: followUpAt });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">LeadFlow</h1>
              <p className="text-sm text-gray-600 mt-1">
                Lead Management System
              </p>
            </div>
            <button
              onClick={() => setShowAddModal(true)}
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <svg
                className="w-5 h-5 mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 4v16m8-8H4"
                />
              </svg>
              Add Lead
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Filter Bar */}
        <FilterBar onFilterChange={handleFilterChange} disabled={loading} />

        {/* Lead List */}
        <LeadList
          leads={leads}
          loading={loading}
          error={error}
          onLeadClick={(lead) => setSelectedLead(lead)}
        />
      </main>

      {/* Add Lead Modal */}
      <AddLeadModal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        onSubmit={handleCreateLead}
      />

      {/* Timeline Dialog */}
      <TimelineDialog
        lead={selectedLead}
        onClose={() => setSelectedLead(null)}
        onStatusChange={handleStatusChange}
        onDiscussionAdded={handleAddDiscussion}
      />
    </div>
  );
}
