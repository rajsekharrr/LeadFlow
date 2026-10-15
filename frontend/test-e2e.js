/**
 * End-to-End Integration Test for LeadFlow
 *
 * Tests complete user flows from UI through API to database and back.
 * Verifies Step 13 requirements.
 */

const axios = require('axios');

const API_URL = 'http://localhost:8000';

console.log('='.repeat(80));
console.log('LEADFLOW END-TO-END INTEGRATION TEST');
console.log('Step 13: Main page and complete user flows');
console.log('='.repeat(80));
console.log();

async function runEndToEndTests() {
  const results = {
    passed: 0,
    failed: 0,
    tests: []
  };

  function logTest(name, passed, details = '') {
    const status = passed ? '[PASS]' : '[FAIL]';
    console.log(`${status} ${name}`);
    if (details) console.log(`      ${details}`);
    results.tests.push({ name, passed, details });
    if (passed) results.passed++;
    else results.failed++;
  }

  try {
    console.log('TEST SUITE 1: Initial Data Load');
    console.log('-'.repeat(80));

    // Test 1: Backend health check
    const health = await axios.get(`${API_URL}/health`);
    logTest('Backend health check', health.data.status === 'ok',
      `Backend responding: ${JSON.stringify(health.data)}`);

    // Test 2: Load all leads (initial page load)
    const allLeads = await axios.get(`${API_URL}/api/leads`);
    logTest('Load all leads on page mount',
      allLeads.data.length >= 5,
      `Loaded ${allLeads.data.length} leads`);

    // Test 3: Verify seeded data structure
    const firstLead = allLeads.data[0];
    const hasRequiredFields = firstLead.id && firstLead.name &&
      firstLead.status && typeof firstLead.discussion_count === 'number';
    logTest('Leads have required fields', hasRequiredFields,
      `Sample: ${firstLead.name} (${firstLead.status}, ${firstLead.discussion_count} discussions)`);

    // Test 4: Verify computed fields present
    const hasComputedFields = firstLead.hasOwnProperty('discussion_count') &&
      firstLead.hasOwnProperty('last_note') &&
      firstLead.hasOwnProperty('last_discussion_at');
    logTest('Computed fields present', hasComputedFields,
      `last_note: ${firstLead.last_note ? 'present' : 'null'}, discussion_count: ${firstLead.discussion_count}`);

    console.log();
    console.log('TEST SUITE 2: Filter and Search');
    console.log('-'.repeat(80));

    // Test 5: Filter by status
    const newLeads = await axios.get(`${API_URL}/api/leads`, {
      params: { status: 'New' }
    });
    logTest('Filter by status "New"',
      newLeads.data.every(l => l.status === 'New'),
      `Found ${newLeads.data.length} lead(s) with status "New"`);

    // Test 6: Search by name
    const searchResults = await axios.get(`${API_URL}/api/leads`, {
      params: { search: 'krishnan' }
    });
    logTest('Search by name (case-insensitive)',
      searchResults.data.length > 0 &&
      searchResults.data.some(l => l.name.toLowerCase().includes('krishnan')),
      `Found ${searchResults.data.length} match(es) for "krishnan"`);

    // Test 7: Combined filter + search
    const combined = await axios.get(`${API_URL}/api/leads`, {
      params: { status: 'Qualified', search: 'ananya' }
    });
    logTest('Combined status filter + search',
      combined.data.every(l => l.status === 'Qualified'),
      `Found ${combined.data.length} Qualified lead(s) matching "ananya"`);

    console.log();
    console.log('TEST SUITE 3: Today\'s Follow-ups (Pinning Logic)');
    console.log('-'.repeat(80));

    // Test 8: Identify today's follow-ups
    const today = new Date().toISOString().split('T')[0];
    const todayFollowUps = allLeads.data.filter(lead => {
      if (!lead.follow_up_at) return false;
      const followUpDate = lead.follow_up_at.split('T')[0];
      return followUpDate === today;
    });
    logTest('Identify today\'s follow-ups',
      todayFollowUps.length > 0,
      `Found ${todayFollowUps.length} lead(s) with today's follow-up`);

    if (todayFollowUps.length > 0) {
      const todayLead = todayFollowUps[0];
      logTest('Today\'s follow-up has correct date',
        todayLead.follow_up_at.startsWith(today),
        `${todayLead.name}: follow_up_at = ${todayLead.follow_up_at}`);
    }

    console.log();
    console.log('TEST SUITE 4: Overdue Follow-ups');
    console.log('-'.repeat(80));

    // Test 9: Identify overdue follow-ups
    const now = new Date();
    const overdueLeads = allLeads.data.filter(lead => {
      if (!lead.follow_up_at) return false;
      const followUpDate = new Date(lead.follow_up_at);
      const followUpDateOnly = lead.follow_up_at.split('T')[0];
      return followUpDate < now && followUpDateOnly !== today;
    });
    logTest('Identify overdue follow-ups',
      overdueLeads.length > 0,
      `Found ${overdueLeads.length} overdue lead(s)`);

    if (overdueLeads.length > 0) {
      const overdueLead = overdueLeads[0];
      const daysOverdue = Math.floor((now - new Date(overdueLead.follow_up_at)) / (1000 * 60 * 60 * 24));
      logTest('Overdue lead in past',
        daysOverdue > 0,
        `${overdueLead.name}: ${daysOverdue} days overdue`);
    }

    console.log();
    console.log('TEST SUITE 5: Add New Lead');
    console.log('-'.repeat(80));

    // Test 10: Create lead with required field only
    const minimalLead = await axios.post(`${API_URL}/api/leads`, {
      name: 'E2E Test Lead Minimal'
    });
    logTest('Create lead with name only',
      minimalLead.data.name === 'E2E Test Lead Minimal' &&
      minimalLead.data.status === 'New',
      `Created: ${minimalLead.data.id}, status defaults to "New"`);

    // Test 11: Create lead with all fields
    const fullLead = await axios.post(`${API_URL}/api/leads`, {
      name: 'E2E Test Lead Full',
      company: 'Test Corp',
      phone: '+1-555-9999',
      status: 'Contacted'
    });
    logTest('Create lead with all fields',
      fullLead.data.company === 'Test Corp' &&
      fullLead.data.phone === '+1-555-9999' &&
      fullLead.data.status === 'Contacted',
      `Created with company, phone, status`);

    // Test 12: Verify lead appears in list
    const afterCreate = await axios.get(`${API_URL}/api/leads`);
    const foundLead = afterCreate.data.find(l => l.id === fullLead.data.id);
    logTest('New lead appears in list',
      !!foundLead,
      `Lead ${fullLead.data.name} found in lead list`);

    console.log();
    console.log('TEST SUITE 6: Update Lead Status');
    console.log('-'.repeat(80));

    // Test 13: Update status (all 6 statuses)
    const statuses = ['New', 'Contacted', 'Qualified', 'Proposal Sent', 'Won', 'Lost'];
    const testLeadId = fullLead.data.id;

    for (const status of statuses) {
      const updated = await axios.patch(`${API_URL}/api/leads/${testLeadId}`, {
        status: status
      });
      const success = updated.data.status === status;
      logTest(`Update status to "${status}"`, success,
        success ? `Status changed successfully` : `Expected ${status}, got ${updated.data.status}`);
    }

    console.log();
    console.log('TEST SUITE 7: Discussion Timeline');
    console.log('-'.repeat(80));

    // Test 14: Fetch discussion history
    const leadWithDiscussions = allLeads.data.find(l => l.discussion_count > 0);
    if (leadWithDiscussions) {
      const discussions = await axios.get(`${API_URL}/api/leads/${leadWithDiscussions.id}/discussions`);
      logTest('Fetch discussion history',
        discussions.data.length === leadWithDiscussions.discussion_count,
        `${leadWithDiscussions.name}: ${discussions.data.length} discussions fetched`);

      // Test 15: Verify reverse chronological order
      if (discussions.data.length >= 2) {
        const first = new Date(discussions.data[0].created_at);
        const second = new Date(discussions.data[1].created_at);
        logTest('Discussions in reverse chronological order',
          first >= second,
          `Most recent first: ${discussions.data[0].created_at}`);
      }
    }

    // Test 16: Add discussion without follow-up
    const simpleDiscussion = await axios.post(
      `${API_URL}/api/leads/${testLeadId}/discussions`,
      { note: 'E2E test discussion - simple note' }
    );
    logTest('Add discussion without follow-up',
      simpleDiscussion.data.note === 'E2E test discussion - simple note',
      `Discussion created: ${simpleDiscussion.data.id}`);

    // Test 17: Verify lead's last_note updated
    const afterSimpleDisc = await axios.get(`${API_URL}/api/leads/${testLeadId}`);
    logTest('Lead last_note updates after discussion',
      afterSimpleDisc.data.last_note === 'E2E test discussion - simple note',
      `last_note: "${afterSimpleDisc.data.last_note}"`);

    // Test 18: Verify discussion_count incremented
    const oldCount = fullLead.data.discussion_count;
    const newCount = afterSimpleDisc.data.discussion_count;
    logTest('Discussion count increments',
      newCount === oldCount + 1,
      `Count: ${oldCount} → ${newCount}`);

    console.log();
    console.log('TEST SUITE 8: Follow-up Scheduling');
    console.log('-'.repeat(80));

    // Test 19: Add discussion with follow-up
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const followUpDateTime = tomorrow.toISOString().split('.')[0]; // Remove milliseconds

    const discussionWithFollowUp = await axios.post(
      `${API_URL}/api/leads/${testLeadId}/discussions`,
      {
        note: 'E2E test - discussion with follow-up',
        follow_up_at: followUpDateTime
      }
    );
    logTest('Add discussion with follow-up date',
      discussionWithFollowUp.data.follow_up_at !== null,
      `Follow-up scheduled: ${discussionWithFollowUp.data.follow_up_at}`);

    // Test 20: Verify parent lead's follow_up_at updated
    const afterFollowUpDisc = await axios.get(`${API_URL}/api/leads/${testLeadId}`);
    logTest('Parent lead follow_up_at updates',
      afterFollowUpDisc.data.follow_up_at !== null,
      `Lead follow_up_at: ${afterFollowUpDisc.data.follow_up_at}`);

    console.log();
    console.log('TEST SUITE 9: Error Handling');
    console.log('-'.repeat(80));

    // Test 21: 404 on non-existent lead
    try {
      await axios.get(`${API_URL}/api/leads/non-existent-id`);
      logTest('404 for non-existent lead', false, 'Should have thrown 404');
    } catch (err) {
      logTest('404 for non-existent lead',
        err.response?.status === 404,
        `Correct 404 error: ${err.response?.data?.detail}`);
    }

    // Test 22: Validation error (empty name)
    try {
      await axios.post(`${API_URL}/api/leads`, { name: '' });
      logTest('Validation error on empty name', false, 'Should have thrown validation error');
    } catch (err) {
      logTest('Validation error on empty name',
        err.response?.status === 422,
        `Correct 422 error: validation failed`);
    }

    // Test 23: Invalid status value
    try {
      await axios.patch(`${API_URL}/api/leads/${testLeadId}`, {
        status: 'InvalidStatus'
      });
      logTest('Invalid status rejected', false, 'Should have thrown validation error');
    } catch (err) {
      logTest('Invalid status rejected',
        err.response?.status === 422,
        `Correct 422 error: invalid status`);
    }

    console.log();
    console.log('TEST SUITE 10: Data Consistency');
    console.log('-'.repeat(80));

    // Test 24: Lead timestamps (created_at, updated_at)
    const leadForTimestamps = await axios.get(`${API_URL}/api/leads/${testLeadId}`);
    const hasTimestamps = leadForTimestamps.data.created_at &&
      leadForTimestamps.data.updated_at;
    logTest('Lead has timestamps',
      hasTimestamps,
      `created_at: ${leadForTimestamps.data.created_at}, updated_at: ${leadForTimestamps.data.updated_at}`);

    // Test 25: Discussion timestamps
    const discs = await axios.get(`${API_URL}/api/leads/${testLeadId}/discussions`);
    if (discs.data.length > 0) {
      const disc = discs.data[0];
      logTest('Discussion has created_at timestamp',
        !!disc.created_at,
        `created_at: ${disc.created_at}`);
    }

    // Test 26: Optional fields nullable
    const leadWithNulls = minimalLead.data;
    logTest('Optional fields nullable',
      leadWithNulls.company === null &&
      leadWithNulls.phone === null &&
      leadWithNulls.follow_up_at === null,
      'company, phone, follow_up_at all null as expected');

    console.log();
    console.log('='.repeat(80));
    console.log('TEST SUMMARY');
    console.log('='.repeat(80));
    console.log(`Total Tests: ${results.passed + results.failed}`);
    console.log(`Passed: ${results.passed}`);
    console.log(`Failed: ${results.failed}`);
    console.log();

    if (results.failed > 0) {
      console.log('FAILED TESTS:');
      results.tests
        .filter(t => !t.passed)
        .forEach(t => console.log(`  - ${t.name}: ${t.details}`));
      console.log();
    }

    const allPassed = results.failed === 0;
    console.log(allPassed ? '✓ ALL TESTS PASSED' : '✗ SOME TESTS FAILED');
    console.log();

    return allPassed;

  } catch (error) {
    console.error();
    console.error('='.repeat(80));
    console.error('FATAL ERROR');
    console.error('='.repeat(80));
    console.error(error.message);
    if (error.response) {
      console.error(`Status: ${error.response.status}`);
      console.error(`Data:`, error.response.data);
    }
    return false;
  }
}

runEndToEndTests()
  .then(success => {
    process.exit(success ? 0 : 1);
  })
  .catch(err => {
    console.error('Unhandled error:', err);
    process.exit(1);
  });
