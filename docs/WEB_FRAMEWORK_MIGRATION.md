# Web Framework Migration: Next.js → Vite + React Router

## Overview

This document describes the migration from Next.js to Vite + React Router for all web frontend interfaces in the JobMatch platform.

## Migration Date
**December 19, 2024**

## Reason for Migration

Next.js was causing significant complexity and issues:
- Routing conflicts and 404 errors
- Build cache problems
- Complex file-based routing conventions
- Slower development experience

**Solution:** Migrated to Vite + React Router for:
- ✅ Faster development (instant HMR)
- ✅ Simpler routing (standard React patterns)
- ✅ Better control and less "magic"
- ✅ Faster builds

## Current Technology Stack

- **Vite** (`^5.4.21`) - Build tool and dev server
- **React Router** (`^7.9.6`) - Client-side routing
- **React** (`^18.2.0`) - UI library
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling

## Architecture Changes

### Routing

**Before (Next.js):**
- File-based routing in `app/` or `pages/` directories
- Automatic route generation
- Server Components vs Client Components

**After (Vite + React Router):**
- Explicit route definitions in `src/App.tsx`
- Standard React components (all client-side)
- Programmatic navigation with hooks

### File Structure

```
frontend/
├── src/
│   ├── pages/          # Page components
│   ├── components/     # Reusable components
│   ├── App.tsx         # Route definitions
│   └── main.tsx        # Entry point
├── index.html          # HTML entry
├── vite.config.ts      # Vite configuration
└── package.json
```

## Migration Guide

See `.cursor/agents/WEB_FRAMEWORK_MIGRATION.md` for detailed migration patterns and examples.

## Key Files

- `frontend/vite.config.ts` - Vite configuration
- `frontend/src/App.tsx` - Route definitions
- `frontend/src/main.tsx` - Application entry point
- `frontend/package.json` - Dependencies and scripts

## Development Commands

```bash
npm run dev      # Start Vite dev server (port 3000)
npm run build    # Build for production
npm run preview  # Preview production build
```

## Notes

- All web interfaces must use Vite + React Router
- No Next.js code should remain in the codebase
- New features should follow Vite + React Router patterns

