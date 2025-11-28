# Demo Page 404 - Troubleshooting

## Issue
`http://localhost:3000/agents/demo` returns 404

## File Structure ✅
- ✅ File exists: `frontend/app/agents/demo/page.tsx`
- ✅ Component exists: `frontend/src/components/agent/AgentUIRenderer.tsx`
- ✅ Schema exists: `frontend/src/schemas/ui-schema.ts`

## Possible Causes

### 1. Build Error Preventing Compilation
The build fails due to `app/test-zk/page.tsx` missing `@/lib/zkCrypto`. This might prevent Next.js from compiling other routes.

### 2. Import Path Issues
- `@/components/agent/AgentUIRenderer` should resolve to `src/components/agent/AgentUIRenderer.tsx` ✅
- `@/schemas/ui-schema` should resolve to `src/schemas/ui-schema.ts` ✅

### 3. Next.js Cache
- Cleared `.next` cache ✅
- Dev server may need restart

## Quick Fixes

### Option 1: Temporarily Disable test-zk Page
```bash
# Rename to prevent compilation
mv frontend/app/test-zk/page.tsx frontend/app/test-zk/page.tsx.disabled
```

### Option 2: Fix test-zk Import
Create the missing file or comment out the import.

### Option 3: Restart Dev Server
```bash
# Stop current dev server (Ctrl+C)
cd frontend
npm run dev
```

## Verification Steps

1. ✅ File exists at correct location
2. ✅ Components exist in src/
3. ⚠️ Route not compiling (checking...)
4. ⚠️ Dev server may need restart

## Next Steps

1. Fix or disable `test-zk/page.tsx` import error
2. Restart dev server
3. Clear `.next` cache
4. Test `/agents/demo` again

