# Web Framework Migration: Next.js → Vite + React Router

## ⚠️ IMPORTANT: All Web Interfaces Must Use Vite + React Router

**Date:** 2024-12-19  
**Status:** ✅ Migration Complete  
**Affected Areas:** All frontend web interfaces

---

## Migration Summary

We have **migrated from Next.js to Vite + React Router** for all web frontend interfaces.

### Why We Switched

- **Next.js was causing complexity** with routing, build issues, and cache problems
- **Vite is faster** - instant HMR, faster builds, simpler configuration
- **React Router is more straightforward** - standard React patterns, no file-based routing conventions
- **Better developer experience** - less magic, more control

---

## Current Stack

### ✅ What We Use Now

- **Vite** (`vite@^5.4.21`) - Build tool and dev server
- **React Router** (`react-router-dom@^7.9.6`) - Client-side routing
- **React** (`react@^18.2.0`) - UI library
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling

### ❌ What We DON'T Use Anymore

- ~~Next.js~~ - Removed completely
- ~~Next.js App Router~~ - Replaced with React Router
- ~~Next.js Pages Router~~ - Replaced with React Router
- ~~`next.config.js`~~ - Replaced with `vite.config.ts`
- ~~`pages/` directory~~ - Replaced with `src/pages/`
- ~~`app/` directory~~ - Replaced with `src/pages/`

---

## File Structure

### Before (Next.js)
```
frontend/
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   └── [routes]/
├── pages/
│   └── [routes]/
└── next.config.js
```

### After (Vite + React Router)
```
frontend/
├── src/
│   ├── pages/
│   │   ├── Home.tsx
│   │   ├── Assessment.tsx
│   │   ├── Matches.tsx
│   │   └── JobDetails.tsx
│   ├── components/
│   ├── App.tsx          # Routes defined here
│   └── main.tsx         # Entry point
├── index.html
├── vite.config.ts
└── package.json
```

---

## Key Differences

### 1. Routing

**Next.js (Old):**
```tsx
// File-based routing
// app/about/page.tsx → /about
// app/users/[id]/page.tsx → /users/:id
```

**React Router (New):**
```tsx
// src/App.tsx
import { Routes, Route } from 'react-router-dom'

<Routes>
  <Route path="/" element={<HomePage />} />
  <Route path="/matches" element={<MatchesPage />} />
  <Route path="/jobs/:jobId" element={<JobDetailsPage />} />
</Routes>
```

### 2. Entry Point

**Next.js (Old):**
- Automatic, handled by framework
- `app/layout.tsx` for root layout

**Vite (New):**
```tsx
// src/main.tsx
import { BrowserRouter } from 'react-router-dom'
import App from './App'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <BrowserRouter>
    <App />
  </BrowserRouter>
)
```

### 3. Configuration

**Next.js (Old):**
```js
// next.config.js
module.exports = {
  // Next.js config
}
```

**Vite (New):**
```ts
// vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': 'http://localhost:8000'
    }
  }
})
```

### 4. Imports

**Next.js (Old):**
```tsx
import Link from 'next/link'
import { useRouter } from 'next/navigation'
```

**React Router (New):**
```tsx
import { Link, useNavigate, useParams } from 'react-router-dom'
```

### 5. No More `'use client'` Directives

**Next.js (Old):**
```tsx
'use client'
export default function Component() { ... }
```

**Vite (New):**
```tsx
// No directive needed - all components are client-side
export default function Component() { ... }
```

---

## Development Commands

### Start Dev Server
```bash
npm run dev
# Runs Vite dev server on http://localhost:3000
```

### Build for Production
```bash
npm run build
# Outputs to dist/ directory
```

### Preview Production Build
```bash
npm run preview
```

---

## Migration Checklist for New Features

When creating new web interfaces, ensure:

- [ ] Use `src/pages/` for page components (not `app/` or `pages/`)
- [ ] Define routes in `src/App.tsx` using `<Route>` components
- [ ] Use `react-router-dom` imports (`Link`, `useNavigate`, `useParams`)
- [ ] No `'use client'` directives
- [ ] Use `vite.config.ts` for configuration (not `next.config.js`)
- [ ] Entry point is `src/main.tsx` (not Next.js automatic routing)
- [ ] Use standard React patterns (no Next.js-specific APIs)

---

## Common Patterns

### Navigation
```tsx
import { Link, useNavigate } from 'react-router-dom'

// Link component
<Link to="/matches">View Matches</Link>

// Programmatic navigation
const navigate = useNavigate()
navigate('/matches')
```

### Route Parameters
```tsx
import { useParams } from 'react-router-dom'

function JobDetailsPage() {
  const { jobId } = useParams<{ jobId: string }>()
  // Use jobId...
}
```

### Layout Component
```tsx
// src/components/Layout.tsx
export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen">
      <Header />
      <main>{children}</main>
      <Footer />
    </div>
  )
}

// src/App.tsx
<Layout>
  <Routes>
    {/* routes */}
  </Routes>
</Layout>
```

---

## Files to Update When Migrating

If you encounter Next.js code, update:

1. **Routing files:**
   - `app/**/page.tsx` → `src/pages/[Name].tsx`
   - `pages/**/*.tsx` → `src/pages/[Name].tsx`

2. **Imports:**
   - `next/link` → `react-router-dom` (Link)
   - `next/navigation` → `react-router-dom` (useNavigate, useParams)
   - `next/image` → Standard `<img>` or custom Image component

3. **Configuration:**
   - `next.config.js` → `vite.config.ts`
   - Remove Next.js-specific config

4. **Entry points:**
   - `app/layout.tsx` → `src/components/Layout.tsx`
   - `app/page.tsx` → `src/pages/Home.tsx`

---

## Current Routes

Active routes in the application:

- `/` - Home page
- `/assessment` - Assessment flow
- `/matches` - Browse job matches (1000 simulated opportunities)
- `/jobs/:jobId` - Job details page
- `/agents/demo` - Agent UI demo (legacy, may be removed)
- `/agents/:agentId` - Individual agent UI
- `/workflow/:workflowId` - Workflow UI

---

## Notes for Agents

### For Development Agents
- Always use Vite + React Router patterns
- Never create Next.js files (`app/`, `pages/`, `next.config.js`)
- Use `src/pages/` for new pages
- Add routes to `src/App.tsx`

### For Review Agents
- Flag any Next.js imports or patterns
- Ensure routes are defined in `App.tsx`
- Verify no `'use client'` directives

### For Documentation Agents
- Update any docs referencing Next.js
- Use Vite + React Router examples
- Document new routing patterns

---

## Questions?

If you encounter Next.js code or patterns:
1. Check this document
2. Look at existing migrated files (`src/pages/`, `src/App.tsx`)
3. Convert to Vite + React Router patterns
4. Update this document if you find new patterns

---

**Last Updated:** 2024-12-19  
**Maintained By:** Development Team  
**Related Files:**
- `frontend/vite.config.ts`
- `frontend/src/App.tsx`
- `frontend/src/main.tsx`
- `frontend/package.json`

