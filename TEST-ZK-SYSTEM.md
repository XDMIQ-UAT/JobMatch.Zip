# Test Zero-Knowledge Authentication System

## Quick Start

### 1. Start Backend Server
```bash
cd E:\zip-jobmatch\backend
python -m uvicorn main:app --reload --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Application startup complete.
```

### 2. Start Frontend Server
Open a **NEW terminal** window:
```bash
cd E:\zip-jobmatch\frontend
npm run dev
```

**Expected output:**
```
▲ Next.js 14.x.x
- Local:        http://localhost:3000
```

### 3. Open Test Page
Navigate to: **http://localhost:3000/test-zk**

---

## Test Flow

### Step 1: Load Simulated Users
Click **"1. Load 100 Simulated Users"**

**What happens:**
- Backend generates 100 synthetic test users
- Each has encrypted profiles + public capabilities
- NO real personal information

**Expected result:**
```
✅ Loaded 100 simulated users
```

### Step 2: Register New User
Credentials are pre-filled:
- Email: `test@example.com`
- Passphrase: `TestPass123!@#`

Click **"2. Register (Zero-Knowledge)"**

**What happens (client-side only):**
1. Validates passphrase strength
2. Derives master key using PBKDF2 (100,000 iterations)
3. Generates authentication hash (1 iteration)
4. Separates private data from public capabilities
5. Encrypts private data with AES-256
6. Sends encrypted data + auth hash to server

**Expected result:**
```
✅ Registration successful! User ID: usr_xxxxx
🔑 Session token stored in localStorage
🔐 Encrypted profile stored (only YOU can decrypt it)
```

### Step 3: Login
Click **"3. Login (Decrypt Profile)"**

**What happens:**
1. Re-derives master key from passphrase
2. Re-generates auth hash
3. Server verifies auth hash
4. Returns encrypted profile (server can't read it)
5. Client decrypts profile using master key

**Expected result:**
```
✅ Login successful!
👤 Decrypted profile: {
  "name": "Test User",
  "bio": "Privacy-first developer testing zero-knowledge auth",
  "portfolio_url": "https://example.com/portfolio"
}
🔑 Session active
```

### Step 4: Find Matches
Click **"4. Find Matches (Capability-Based)"**

**What happens:**
- Backend searches for users with matching skills
- Returns only capabilities (NO names, emails, bios)
- Anonymous user IDs + match scores

**Expected result:**
```
✅ Found 5 matches!
(Note: No names, no emails, just capabilities)
```

You'll see cards showing:
- Anonymous user ID
- Match percentage
- Matched skills
- Experience level
- Availability type
- NO PERSONAL INFORMATION

### Step 5: Get Statistics
Click **"5. Get Anonymous Stats"**

**What happens:**
- Backend aggregates public data
- Returns statistics (no user-specific info)

**Expected result:**
```
✅ Stats (All anonymous):
👥 Total users: 101
🔥 Top skills: Python, JavaScript, React, TypeScript, Node.js
📊 Experience levels: {...}
```

---

## What to Verify

### ✅ Privacy Checks
1. **Passphrase never sent**: Check browser DevTools Network tab - search for "TestPass" - should find NOTHING
2. **Server can't decrypt**: Backend logs should show encrypted profiles like `"U2FsdGVkX1..."`
3. **Matching is blind**: Match results show skills/experience but NO names or emails
4. **Session persists**: Refresh page - session token still in localStorage

### ✅ Security Checks
1. **Wrong passphrase fails**: Change passphrase to `WrongPass123` and try login - should fail
2. **Encrypted data unreadable**: Open backend database (`users` table) - `encrypted_profile` column should be gibberish
3. **No PII in capabilities**: Check `capabilities` table - should only have skills, experience, rates (no names/emails)

### ✅ Functionality Checks
1. **Registration works**: New user created with session token
2. **Login works**: Can decrypt profile after login
3. **Matching works**: Returns relevant matches based on skills
4. **Stats work**: Aggregates data without revealing individuals

---

## Troubleshooting

### Backend won't start
**Error:** `ModuleNotFoundError: No module named 'crypto-js'`
- This is Python backend - `crypto-js` is frontend only
- Check for Python errors instead

**Error:** `Port 8000 already in use`
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or use different port
python -m uvicorn main:app --reload --port 8001
# Update frontend API_BASE to http://localhost:8001
```

### Frontend won't start
**Error:** `Module not found: Can't resolve '@/lib/zkCrypto'`
```bash
# Rebuild
cd E:\zip-jobmatch\frontend
npm install
npm run dev
```

**Error:** `Cannot find module 'crypto-js'`
```bash
npm install crypto-js @types/crypto-js
```

### CORS errors
**Error:** `Access to fetch blocked by CORS policy`
- Check backend CORS middleware in `main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### API endpoint not found
**Error:** `404 Not Found: /api/zk-auth/register`
- Check backend registered routes:
```bash
curl http://localhost:8000/docs
# Should show all API endpoints
```

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ CLIENT (Browser)                                            │
├─────────────────────────────────────────────────────────────┤
│ 1. User enters email + passphrase                           │
│ 2. PBKDF2(email + passphrase, 100K iterations) → Master Key │
│ 3. PBKDF2(Master Key + passphrase, 1 iteration) → Auth Hash │
│ 4. AES-256 encrypt private data with Master Key             │
│ 5. Send: { email, auth_hash, encrypted_profile }            │
│                                                             │
│ ⚠️ MASTER KEY NEVER LEAVES BROWSER                          │
│ ⚠️ PASSPHRASE NEVER SENT TO SERVER                          │
└──────────────────┬──────────────────────────────────────────┘
                   │ HTTPS
                   │ { auth_hash, encrypted_profile }
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ SERVER (FastAPI)                                            │
├─────────────────────────────────────────────────────────────┤
│ 1. Store auth_hash (for verification)                       │
│ 2. Store encrypted_profile (can't decrypt - no master key)  │
│ 3. Store capabilities (public, for matching)                │
│ 4. Return session token                                     │
│                                                             │
│ ⚠️ CANNOT DECRYPT PROFILES                                  │
│ ⚠️ CANNOT ACCESS PRIVATE DATA                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Next Steps After Testing

Once you verify everything works:

1. **Migrate real JobMatch forms** to use zero-knowledge encryption
2. **Replace existing auth** with ZK auth endpoints
3. **Update database schema** to match zero-knowledge design
4. **Add password recovery** (requires security questions or key escrow)
5. **Add multi-device sync** (encrypted profile syncs across devices)

---

## Questions?

If anything fails or you see unexpected behavior, check:
1. Browser console (F12) for frontend errors
2. Backend terminal for API errors
3. Network tab (F12) to see actual requests/responses

Ready to test! 🚀
