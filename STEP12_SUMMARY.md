# Step 12: Frontend Components - Summary

## Files Created

### Components (in build order)

1. **`src/components/StatusBadge.tsx`** (35 lines)
   - Pure presentational component
   - Color-coded status pills
   - Static color map

2. **`src/components/FilterBar.tsx`** (98 lines)
   - Status dropdown filter
   - Search input with debounce
   - Clear filters button

3. **`src/components/LeadCard.tsx`** (128 lines)
   - Single lead display
   - Visual indicators (pinned, overdue)
   - Last note and time ago

4. **`src/components/LeadList.tsx`** (163 lines)
   - Lead list container
   - Pinning logic (today's follow-ups)
   - Loading, error, empty states

5. **`src/components/AddLeadModal.tsx`** (213 lines)
   - Create lead form
   - Form validation
   - Modal overlay

6. **`src/components/TimelineDialog.tsx`** (323 lines)
   - Discussion history
   - Add discussion form
   - Status change dropdown
   - Most complex component

### Updated Files

- **`src/app/page.tsx`** - Main app page wiring all components

## Component Architecture

### Build Order (Dependency Tree)

```
StatusBadge (no dependencies)
    ↓
LeadCard (uses StatusBadge)
    ↓
LeadList (uses LeadCard)
    ↓
FilterBar (independent)
AddLeadModal (independent)
TimelineDialog (uses StatusBadge)
    ↓
page.tsx (uses all components)
```

**Why this order:**
- Build leaf components first (StatusBadge)
- Components ready when needed by others
- No circular dependencies
- Each component tested before next

## Component Details

### 1. StatusBadge

**Purpose:** Display lead status with color coding

**Props:**
```typescript
interface StatusBadgeProps {
  status: LeadStatus;
}
```

**Features:**
- Pure function (no state)
- Static color map
- Consistent styling

**Color Map:**
```typescript
const STATUS_COLORS = {
  New: "bg-blue-100 text-blue-800",
  Contacted: "bg-purple-100 text-purple-800",
  Qualified: "bg-green-100 text-green-800",
  "Proposal Sent": "bg-yellow-100 text-yellow-800",
  Won: "bg-emerald-100 text-emerald-800",
  Lost: "bg-gray-100 text-gray-800",
};
```

**Why pure function:**
- No side effects
- Easy to test
- Predictable output
- Can be memoized

### 2. FilterBar

**Purpose:** Status and search filtering controls

**Props:**
```typescript
interface FilterBarProps {
  onFilterChange: (filters: { status?: LeadStatus; search?: string }) => void;
  disabled?: boolean;
}
```

**Features:**
- Status dropdown (all statuses + "All")
- Search input with 300ms debounce
- Clear filters button
- Disabled state during loading

**Debounce Implementation:**
```typescript
useEffect(() => {
  const timer = setTimeout(() => {
    onFilterChange(filters);
  }, 300);
  
  return () => clearTimeout(timer); // Cleanup
}, [status, searchInput]);
```

**Why debounce:**
- Typing "tech" = 4 keystrokes
- Without debounce = 4 API calls
- With debounce = 1 API call (300ms after last keystroke)
- Better performance, less server load

### 3. LeadCard

**Purpose:** Display single lead with all relevant info

**Props:**
```typescript
interface LeadCardProps {
  lead: Lead;
  onClick: () => void;
  isPinned?: boolean;
}
```

**Features:**
- Name, company, phone
- Status badge
- Last discussion note (truncated to 2 lines)
- Discussion count
- Time since last activity
- Follow-up indicator

**Visual Indicators:**
```typescript
// Blue left border + pin icon
isPinned ? "border-l-blue-500 border-l-4"

// Red left border
isOverdue ? "border-l-red-500 border-l-4"

// Normal gray border
: "border-gray-200"
```

**Date Logic:**
```typescript
// Check if overdue
const isOverdue = lead.follow_up_at &&
  !isToday(parseISO(lead.follow_up_at)) &&
  isPast(parseISO(lead.follow_up_at));
```

**Truncation:**
- `truncate` class for name (single line)
- `line-clamp-2` for note (2 lines with ellipsis)

### 4. LeadList

**Purpose:** Container with pinning logic

**Props:**
```typescript
interface LeadListProps {
  leads: Lead[];
  loading: boolean;
  error: string | null;
  onLeadClick: (lead: Lead) => void;
}
```

**Features:**
- Pins today's follow-ups to top
- Section headers ("Follow up today", "All Leads")
- Loading spinner
- Error message
- Empty state

**Pinning Logic:**
```typescript
// Separate pinned and regular
const pinnedLeads = leads.filter(lead =>
  lead.follow_up_at && isToday(parseISO(lead.follow_up_at))
);

const regularLeads = leads.filter(lead =>
  !lead.follow_up_at || !isToday(parseISO(lead.follow_up_at))
);

// Render pinned first, then regular
```

**Why client-side pinning:**
- Backend returns leads in creation order
- Client determines "today" based on user's timezone
- Pinning logic flexible without backend changes

**States:**
1. **Loading:** Spinner with "Loading leads..."
2. **Error:** Red border, error icon, message
3. **Empty:** Empty state icon, "No leads found"
4. **Success:** Pinned section + Regular section

### 5. AddLeadModal

**Purpose:** Create new lead form

**Props:**
```typescript
interface AddLeadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: CreateLeadRequest) => Promise<void>;
}
```

**Features:**
- Name field (required)
- Company field (optional)
- Phone field (optional)
- Status dropdown (defaults to "New")
- Form validation
- Loading state during submission
- Error display

**Modal Structure:**
```
Fixed overlay (z-50)
  ├─ Backdrop (dark overlay, closes on click)
  └─ Modal card (centered)
      ├─ Header (title + close button)
      ├─ Error message (if any)
      ├─ Form fields
      └─ Actions (Cancel + Create)
```

**Validation:**
- Name required (trim whitespace)
- Submit button disabled if name empty
- Submit button disabled during loading

**Form Reset:**
- On successful creation
- On modal close
- Clears error state

### 6. TimelineDialog

**Purpose:** Discussion history and new note form

**Props:**
```typescript
interface TimelineDialogProps {
  lead: Lead | null;
  onClose: () => void;
  onStatusChange: (leadId: string, status: LeadStatus) => Promise<void>;
  onDiscussionAdded: (leadId: string, note: string, followUpAt?: string) => Promise<void>;
}
```

**Features:**
- Lead details header
- Status change dropdown
- Add discussion form
  - Note textarea (required)
  - Follow-up date picker (optional)
  - Follow-up time picker (optional)
- Discussion timeline (reverse chronological)
- Loading states
- Error handling

**Data Fetching:**
```typescript
useEffect(() => {
  if (!lead) return;
  
  async function fetchDiscussions() {
    const data = await getDiscussions(lead.id);
    setDiscussions(data);
  }
  
  fetchDiscussions();
}, [lead]); // Refetch when lead changes
```

**Why separate discussion fetch:**
- Lead list only shows summary (last_note, count)
- Full discussion history fetched on demand
- Reduces initial page load
- Each lead's discussions independent

**Discussion Display:**
- Reverse chronological order (newest first)
- Relative time ("5 days ago")
- Absolute timestamp (hover/secondary)
- Follow-up date highlighted in blue

**Form Handling:**
```typescript
// Combine date + time
if (followUpDate && followUpTime) {
  followUpAt = `${followUpDate}T${followUpTime}:00`;
}

// Call parent handler (updates useLeads)
await onDiscussionAdded(lead.id, note, followUpAt);

// Refresh local discussions
const updated = await getDiscussions(lead.id);
setDiscussions(updated);
```

## Data Flow

### Component Hierarchy

```
page.tsx (main app)
  ├─ useLeads() hook
  ├─ FilterBar
  │   └─ onFilterChange → fetchLeads(filters)
  ├─ LeadList
  │   ├─ leads, loading, error from hook
  │   └─ onLeadClick → setSelectedLead(lead)
  ├─ AddLeadModal
  │   ├─ isOpen = showAddModal state
  │   └─ onSubmit → addLead(data)
  └─ TimelineDialog
      ├─ lead = selectedLead state
      ├─ onStatusChange → updateLeadStatus()
      └─ onDiscussionAdded → addDiscussion()
```

### State Management

**Global State (useLeads hook):**
- `leads` - Array of all leads
- `loading` - Fetch in progress
- `error` - Error message

**Page-Level State:**
- `showAddModal` - AddLeadModal visibility
- `selectedLead` - TimelineDialog lead (null = closed)

**Component-Level State:**
- FilterBar: `status`, `searchInput`
- AddLeadModal: form fields, `loading`, `error`
- TimelineDialog: `discussions`, form fields, `loading`, `error`

### Data Flow Examples

**Filter leads:**
1. User types in search → FilterBar state updates
2. After 300ms debounce → onFilterChange callback
3. page.tsx calls fetchLeads(filters)
4. useLeads updates leads array
5. LeadList re-renders with filtered leads

**Create lead:**
1. User clicks "Add Lead" → page.tsx sets showAddModal = true
2. AddLeadModal renders
3. User fills form, clicks "Create"
4. onSubmit → page.tsx calls addLead(data)
5. useLeads prepends lead to array (optimistic)
6. LeadList re-renders with new lead at top
7. Modal closes

**Add discussion:**
1. User clicks lead card → page.tsx sets selectedLead
2. TimelineDialog renders, fetches discussions
3. User adds note with follow-up → onDiscussionAdded
4. page.tsx calls addDiscussion() from hook
5. useLeads updates lead's last_note, discussion_count, follow_up_at
6. TimelineDialog refetches discussions
7. LeadCard shows updated note immediately
8. If follow-up is today → lead moves to pinned section

## Visual Design

### Color Palette

**Status Colors:**
- New: Blue (bg-blue-100/text-blue-800)
- Contacted: Purple
- Qualified: Green
- Proposal Sent: Yellow
- Won: Emerald
- Lost: Gray

**Indicators:**
- Pinned: Blue left border + pin icon
- Overdue: Red left border + "Overdue" text
- Today: "Today" in blue

**UI Elements:**
- Primary action: Blue (bg-blue-600)
- Secondary action: White with gray border
- Error: Red (bg-red-50/border-red-200)
- Success: Green

### Responsive Design

**Breakpoints (Tailwind):**
- Mobile: Default (< 640px)
- Tablet: `sm:` (≥ 640px)
- Desktop: `lg:` (≥ 1024px)

**Adaptations:**
- FilterBar: Stack vertically on mobile, horizontal on tablet+
- LeadCard: Single column always (optimized for mobile)
- TimelineDialog: Full width on mobile, max-w-4xl on desktop
- Header: Stack on mobile, flex on desktop

### Accessibility

**Implemented:**
- Semantic HTML (header, main, form)
- Label for every input (htmlFor + id)
- Button types specified (type="submit", type="button")
- Disabled states with cursor-not-allowed
- Focus rings (focus:ring-blue-500)
- Alt text for icons (aria-hidden for decorative)

**Could improve:**
- ARIA labels for icon-only buttons
- Screen reader announcements for loading states
- Keyboard shortcuts (Esc to close modals)
- Focus trap in modals

## TypeScript Integration

### Type Safety Benefits

**Compile-time errors:**
```typescript
// Wrong status
<StatusBadge status="Open" /> // ✗ Error

// Missing required prop
<LeadCard lead={lead} /> // ✗ Error: onClick required

// Wrong callback signature
onFilterChange: (filters: string) => {} // ✗ Error
```

**Autocomplete:**
- IDE suggests all Lead fields
- Props autocomplete when typing
- Function signatures shown in tooltips

### Interface Reuse

**From shared types:**
```typescript
import type { Lead, LeadStatus } from "@/types/lead";
```

**Component-specific:**
```typescript
interface LeadCardProps {
  lead: Lead;  // Reuse
  onClick: () => void;  // Component-specific
  isPinned?: boolean;  // Component-specific
}
```

## Performance Considerations

### Optimizations Implemented

**1. Debounced Search**
- 300ms delay prevents excessive API calls
- User types 10 characters = 1 API call (not 10)

**2. useCallback in useLeads**
- Functions memoized
- Prevents child re-renders

**3. Conditional Rendering**
- Modals only render when open
- Discussions only fetch when dialog opens

**4. Pure Components**
- StatusBadge is pure
- Can be memoized with React.memo if needed

### Potential Improvements

**Not implemented (not required):**
- React.memo on LeadCard (prevent unnecessary re-renders)
- Virtual scrolling for large lead lists
- Pagination or infinite scroll
- Image optimization (no images used)
- Code splitting (Next.js handles automatically)

## Testing Verification

### Manual Testing Checklist

✓ **StatusBadge** - All 6 statuses display with correct colors  
✓ **FilterBar** - Status filter works, search debounces  
✓ **LeadCard** - All fields display, overdue highlighted in red  
✓ **LeadList** - Today's follow-ups pinned to top  
✓ **AddLeadModal** - Form validation, creates lead  
✓ **TimelineDialog** - Discussions load, new notes save  
✓ **TypeScript** - No compilation errors  
✓ **Frontend** - Starts without errors  
✓ **Backend** - API responding  

### Component Behavior Verified

✓ Pinning logic works (today's follow-ups at top)  
✓ Overdue follow-ups show red border  
✓ Search debounces correctly (300ms)  
✓ Modal closes on backdrop click  
✓ Form validation prevents empty name  
✓ Discussions display reverse chronological  
✓ Status change updates immediately  
✓ Discussion with follow-up updates lead  
✓ Loading spinners show during API calls  
✓ Error messages display correctly  
✓ Empty states render appropriately  

## Common Patterns Used

### React Patterns

**1. Controlled Components**
```typescript
<input
  value={name}
  onChange={(e) => setName(e.target.value)}
/>
```

**2. Conditional Rendering**
```typescript
{loading && <Spinner />}
{error && <ErrorMessage />}
{leads.length === 0 && <EmptyState />}
```

**3. Event Handlers**
```typescript
const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  // Handle form submission
};
```

**4. Cleanup in useEffect**
```typescript
useEffect(() => {
  const timer = setTimeout(...);
  return () => clearTimeout(timer); // Cleanup
}, [deps]);
```

### Tailwind Patterns

**1. Responsive Classes**
```typescript
className="flex flex-col sm:flex-row"
// Stack on mobile, horizontal on tablet+
```

**2. State Variants**
```typescript
className="hover:bg-gray-50 disabled:opacity-50"
```

**3. Utility Composition**
```typescript
className="rounded-lg shadow-sm border border-gray-200 p-4"
```

## Next Steps (Step 13)

Step 12 created all components. Step 13 (already complete) updated page.tsx to wire them together. The app is now fully functional!

Remaining: Step 14 - Write README with setup instructions

## Unresolved Issues

**None.** All components complete and verified:
- All 6 components built in correct order
- TypeScript compiles without errors
- Frontend starts successfully
- All features functional (verified manually)
- Visual indicators working (pinning, overdue)
- Forms validate correctly
- API integration working
- Responsive design implemented
- Accessibility basics covered

Application is feature-complete and ready for final documentation (README).
