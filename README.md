# LeadFlow

Single-screen Lead Management tool built with FastAPI + SQLite (backend) and Next.js + Tailwind (frontend).

## Overview

LeadFlow is a lightweight CRM designed for sales representatives to manage leads efficiently. Track leads, view discussion history, schedule follow-ups, and update status—all from a single screen without navigation.

## Features

- **Lead list** with status badges, last note, and time-since-last-activity
- **Today's follow-ups** pinned at top with blue visual indicator
- **Overdue follow-ups** highlighted in red
- **Filter by status** + **search by name/company** (debounced)
- **Timeline dialog** with full discussion history in reverse chronological order
- **Add discussions** with optional follow-up date and time
- **Status updates** from within the timeline dialog
- **Add new leads** with optional company and phone fields
- **Optimistic UI updates** for instant feedback

## Tech Stack

### Backend
- **FastAPI** 0.115.0 - Modern Python web framework with auto-generated API docs
- **SQLAlchemy** 2.0.35 - ORM for database operations
- **Pydantic** 2.9.2 - Data validation and serialization
- **SQLite** - Zero-config database (swap to PostgreSQL by changing DATABASE_URL)
- **Uvicorn** 0.30.6 - ASGI server

### Frontend
- **Next.js** 14 - React framework with App Router
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first styling
- **Axios** - HTTP client
- **date-fns** - Date manipulation and formatting

## Architecture

### Request Flow
1. **Browser** → User clicks "Add Discussion" in TimelineDialog
2. **Component** → Calls `onDiscussionAdded(leadId, note, followUpAt)`
3. **Page Handler** → Passes to `addDiscussion()` from useLeads hook
4. **Hook (Optimistic Update)** → Immediately updates UI (last_note, discussion_count)
5. **API Client** → POST `/api/leads/{id}/discussions`
6. **FastAPI Router** → Validates request with Pydantic
7. **CRUD Layer** → Creates discussion + updates parent lead (atomic transaction)
8. **SQLite Database** → Commits both operations
9. **API Response** → Returns 201 Created with discussion data
10. **Component Refresh** → TimelineDialog refetches discussions, shows new note at top

**Perceived latency: 0ms** (thanks to optimistic update in step 4)

### State Management
- All lead data lives in **`useLeads` custom hook** (single source of truth)
- **Optimistic updates** for instant UI feedback
- **Automatic rollback** on API errors
- **No prop drilling** - components call hook directly

### Key Design Decisions
- **SQLite for development** - Zero configuration, portable, swap to PostgreSQL via env var only
- **Hook-only state** - No Redux/Zustand/Context needed for this scope
- **Single-screen app** - Dialog overlays instead of routes preserve scroll position
- **Computed fields** - Backend assembles last_note, discussion_count on read
- **Debounced search** - 300ms delay prevents excessive API calls

## Prerequisites

- **Python 3.11+**
- **Node.js 18+** and npm
- **Git**

## Quick Start

### 1. Clone Repository

```bash
git clone <repository-url>
cd leadflow
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (or copy from .env.example)
# DATABASE_URL=sqlite:///./leadflow.db
# CORS_ORIGINS=http://localhost:3000

# Seed database with sample data
python seed.py

# Start backend server
uvicorn app.main:app --reload --port 8000
```

Backend will be available at **http://localhost:8000**

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start frontend development server
npm run dev
```

Frontend will be available at **http://localhost:3000**

### 4. Open Application

Navigate to **http://localhost:3000** in your browser.

## Environment Variables

### Backend (.env)

```env
DATABASE_URL=sqlite:///./leadflow.db
CORS_ORIGINS=http://localhost:3000
```

**To use PostgreSQL instead:**
```env
DATABASE_URL=postgresql://user:password@localhost:5432/leadflow
CORS_ORIGINS=http://localhost:3000
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## API Documentation

FastAPI auto-generates interactive API documentation:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Database Schema

### Leads Table
- `id` (UUID, primary key)
- `name` (text, required)
- `company` (text, optional)
- `phone` (text, optional)
- `status` (text, required, default: "New")
- `follow_up_at` (datetime, optional)
- `created_at` (datetime, auto)
- `updated_at` (datetime, auto)

### Discussions Table
- `id` (UUID, primary key)
- `lead_id` (UUID, foreign key → leads.id, cascade delete)
- `note` (text, required)
- `follow_up_at` (datetime, optional)
- `created_at` (datetime, auto)

## Seed Data

The `seed.py` script creates 5 sample leads:

1. **Ananya Krishnan** (Zerodha) - Qualified, 3 discussions, today's follow-up
2. **Rohan Mehta** (Angel One) - Proposal Sent, 3 discussions, overdue follow-up
3. **Priya Desai** (Motilal Oswal) - Contacted, 2 discussions
4. **Karan Bhatia** (HDFC Securities) - Won, 2 discussions
5. **Sneha Iyer** - New, no discussions

Run `python seed.py` to reset the database with sample data.

## Project Structure

```
leadflow/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app, CORS, startup
│   │   ├── database.py       # SQLAlchemy setup, session
│   │   ├── models.py         # ORM models (Lead, Discussion)
│   │   ├── schemas.py        # Pydantic schemas
│   │   ├── crud.py           # Database operations
│   │   └── routers/
│   │       ├── leads.py      # Lead endpoints
│   │       └── discussions.py # Discussion endpoints
│   ├── requirements.txt      # Python dependencies
│   ├── seed.py              # Database seed script
│   └── .env                 # Environment config (not in git)
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx   # Root layout
│   │   │   └── page.tsx     # Main app page
│   │   ├── components/
│   │   │   ├── StatusBadge.tsx
│   │   │   ├── FilterBar.tsx
│   │   │   ├── LeadCard.tsx
│   │   │   ├── LeadList.tsx
│   │   │   ├── AddLeadModal.tsx
│   │   │   └── TimelineDialog.tsx
│   │   ├── hooks/
│   │   │   └── useLeads.ts  # Lead state management hook
│   │   ├── lib/
│   │   │   └── api.ts       # Axios API client
│   │   └── types/
│   │       └── lead.ts      # TypeScript interfaces
│   ├── package.json
│   └── .env.local           # Environment config (not in git)
│
└── README.md
```

## Development Commands

### Backend

```bash
# Start server
uvicorn app.main:app --reload --port 8000

# Reset database with seed data
python seed.py

# Run with different database
DATABASE_URL=postgresql://... uvicorn app.main:app
```

### Frontend

```bash
# Development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Type check
npx tsc --noEmit

# Lint
npm run lint
```

## Testing

### Backend
API tested via end-to-end integration tests that exercise complete user flows.

### Frontend
```bash
cd frontend
node test-e2e.js  # Requires both servers running
```

Test coverage: 32 comprehensive tests covering data load, filtering, search, CRUD operations, error handling, and data consistency.

## Key Features Explained

### Pinning Logic (Today's Follow-ups)
Leads with `follow_up_at` date matching today are automatically pinned to the top of the list with a blue left border and pin icon. Client-side filtering using `isToday()` from date-fns.

### Overdue Highlighting
Leads with `follow_up_at` in the past (excluding today) show a red left border and "Overdue" label. Client-side logic using `isPast()` from date-fns.

### Optimistic Updates
When adding discussions or updating status, the UI updates immediately before the API responds. If the API call fails, changes automatically roll back. This provides instant feedback with zero perceived latency.

### Debounced Search
Search input waits 300ms after the user stops typing before triggering an API call. This prevents excessive requests while maintaining responsive UX.

### Computed Fields
The backend assembles `last_note`, `last_discussion_at`, and `discussion_count` when fetching leads. These fields are not stored in the database—they're computed from the discussions table on each request.

### Single-Screen Design
The entire application is one Next.js route. The timeline dialog and add-lead modal are conditional renders (not routes), which preserves the user's scroll position and filter state.

## Troubleshooting

**Backend won't start:**
- Check Python version: `python --version` (need 3.11+)
- Verify dependencies installed: `pip list`
- Check port 8000 not in use: `lsof -i :8000` or `netstat -ano | findstr :8000`

**Frontend won't start:**
- Check Node version: `node --version` (need 18+)
- Verify dependencies installed: `npm list`
- Check `.env.local` exists with `NEXT_PUBLIC_API_URL`
- Check port 3000 not in use

**CORS errors:**
- Verify backend `CORS_ORIGINS` includes frontend URL
- Check frontend is making requests to correct backend URL
- Restart backend after changing CORS settings

**Database locked:**
- SQLite doesn't handle high concurrency well
- For production, use PostgreSQL
- Temporary fix: restart backend

## Production Deployment

### Backend
1. Set `DATABASE_URL` to PostgreSQL connection string
2. Disable auto-reload: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
3. Use production ASGI server like Gunicorn with Uvicorn workers
4. Set appropriate `CORS_ORIGINS` for your frontend domain

### Frontend
1. Update `.env.local` with production API URL
2. Build: `npm run build`
3. Deploy to Vercel/Netlify or serve with `npm start`

## License

This project was built as a coding assessment.

## Tech Decisions Deep Dive

**Why SQLite?**
Zero-config portability for assessment. Any reviewer can clone and run it immediately. Swapping to PostgreSQL is a single environment variable change—no code changes needed.

**Why custom hook instead of React Query?**
Specification excludes external state management libraries. Custom hook demonstrates React patterns (useState, useCallback, useEffect) and keeps dependencies minimal.

**Why single-screen?**
Spec requirement. Keeps state management simple, preserves user's scroll position, and demonstrates conditional rendering patterns instead of routing.

**Why optimistic updates?**
Provides instant feedback. Users see changes immediately, then the hook rolls back if the API fails. Creates a native-app feel in a web app.

**Why computed fields?**
Keeps database normalized while providing convenient read-time aggregations. Backend assembles them on each request from the discussions table.
