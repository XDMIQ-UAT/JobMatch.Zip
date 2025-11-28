# Route Precedence Issue - Fix

## Problem
Next.js is routing `/agents/demo` to the dynamic route `/agents/[agentId]` instead of the static route `/agents/demo`.

## Why This Happens
In Next.js App Router, static routes should take precedence over dynamic routes, but:
1. The dev server may have cached the old route structure
2. The dynamic route is matching first
3. The static route isn't being recognized

## Solution Options

### Option 1: Restart Dev Server (Try First)
The dev server needs a full restart to recognize the static route:
```bash
# Stop server (Ctrl+C)
cd frontend
npm run dev
```

### Option 2: Use Different Path
Move demo to a different path that doesn't conflict:
- `/demo-agents` instead of `/agents/demo`
- `/agents-demo` instead of `/agents/demo`

### Option 3: Handle in Dynamic Route
Add special handling in `[agentId]/page.tsx`:
```typescript
if (agentId === 'demo') {
  // Redirect or render demo content
}
```

## Current Status
- ✅ Static route file exists: `app/agents/demo/page.tsx`
- ✅ Route is compiled: `.next/server/app/agents/demo/page.js`
- ❌ Next.js routing to dynamic route instead

## Next Step
**Restart the dev server completely** - this should fix the route precedence issue.

