# Email Integration Guide
## Where to Add Email Triggers in the User Journey

This guide shows where to integrate email triggers in the codebase to implement the onboarding email communication plan.

---

## Email Trigger Points

### 1. Welcome Email
**Trigger:** User signs up/authenticates  
**Method:** `emailService.sendWelcomeEmail()`  
**Location:** After successful authentication

**Files to Update:**
- `backend/api/auth.ts` - After social auth success
- `backend/api/social_auth.py` - After email verification
- `frontend/app/assessment/page.tsx` - After authentication success

**Example Integration:**
```typescript
// After successful authentication
await emailService.sendWelcomeEmail(
  userEmail,
  anonymousId,
  `${baseUrl}/assess`
);
```

---

### 2. Getting Started Reminder
**Trigger:** 2 hours after signup (if assessment not started)  
**Method:** `emailService.sendGettingStartedReminder()`  
**Location:** Scheduled job/background task

**Files to Create/Update:**
- Create: `backend/jobs/email-scheduler.ts` or similar
- Update: Background job system to check user signup time

**Example Integration:**
```typescript
// In scheduled job
const usersNeedingReminder = await getUsersSignedUp2HoursAgo();
for (const user of usersNeedingReminder) {
  if (!user.assessment_started) {
    await emailService.sendGettingStartedReminder(
      user.email,
      user.anonymous_id,
      `${baseUrl}/assess`
    );
  }
}
```

---

### 3. Assessment Started Tracking
**Trigger:** User starts assessment  
**Location:** Assessment page load/start

**Files to Update:**
- `frontend/src/app/assess/page.tsx` - When user clicks "Let's start"
- `frontend/app/assessment/page.tsx` - When assessment begins

**Action:** Track assessment start time in database (for reminder email)

---

### 4. Assessment Reminder
**Trigger:** 24 hours after assessment started (if not completed)  
**Method:** `emailService.sendAssessmentReminder()`  
**Location:** Scheduled job/background task

**Files to Create/Update:**
- Create: `backend/jobs/email-scheduler.ts` or similar
- Update: Background job system

**Example Integration:**
```typescript
// In scheduled job
const incompleteAssessments = await getIncompleteAssessmentsStarted24HoursAgo();
for (const assessment of incompleteAssessments) {
  await emailService.sendAssessmentReminder(
    assessment.user.email,
    assessment.user.anonymous_id,
    `${baseUrl}/assess?session=${assessment.session_id}`
  );
}
```

---

### 5. Assessment Complete Email
**Trigger:** User completes assessment  
**Method:** `emailService.sendAssessmentCompleteEmail()`  
**Location:** After assessment submission

**Files to Update:**
- `frontend/src/app/assess/page.tsx` - In `submitAssessment()` function
- `backend/api/assessment.py` - After assessment processing

**Example Integration:**
```typescript
// After assessment submission
await emailService.sendAssessmentCompleteEmail(
  userEmail,
  anonymousId,
  `${baseUrl}/profile?id=${anonymousId}`
);
```

---

### 6. First Match Notification
**Trigger:** User receives their first match  
**Method:** `emailService.sendFirstMatchEmail()`  
**Location:** When match is created and approved

**Files to Update:**
- `backend/api/matching.py` or similar - After match creation
- Match approval workflow

**Example Integration:**
```typescript
// After match is approved
if (isUserFirstMatch(userId)) {
  await emailService.sendFirstMatchEmail(
    userEmail,
    anonymousId,
    `${baseUrl}/matches/${matchId}`,
    matchDetails
  );
}
```

---

## Database Schema Requirements

### User Email Tracking Table
```sql
CREATE TABLE user_email_tracking (
  id SERIAL PRIMARY KEY,
  user_id VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL,
  anonymous_id VARCHAR(255) NOT NULL,
  signup_time TIMESTAMP NOT NULL,
  assessment_started_at TIMESTAMP,
  assessment_completed_at TIMESTAMP,
  welcome_email_sent BOOLEAN DEFAULT FALSE,
  getting_started_email_sent BOOLEAN DEFAULT FALSE,
  assessment_reminder_sent BOOLEAN DEFAULT FALSE,
  assessment_complete_email_sent BOOLEAN DEFAULT FALSE,
  first_match_email_sent BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## Background Job Setup

### Email Scheduler Job
Create a scheduled job that runs every hour to:
1. Check for users needing "Getting Started" reminder (2 hours after signup)
2. Check for users needing assessment reminder (24 hours after start)
3. Check for other time-based email triggers

**Recommended Tools:**
- Node.js: `node-cron` or `bull` (Redis-based job queue)
- Python: `celery` or `APScheduler`
- Cloud: AWS EventBridge, Google Cloud Scheduler

---

## Environment Variables

Add to `.env`:
```bash
FRONTEND_URL=https://jobmatch.zip
SES_FROM_EMAIL=admin@futurelink.zip
EMAIL_ENABLED=true
```

---

## Testing Checklist

- [ ] Welcome email sends after signup
- [ ] Getting started reminder sends after 2 hours
- [ ] Assessment reminder sends after 24 hours
- [ ] Assessment complete email sends after completion
- [ ] First match email sends when match is created
- [ ] All emails are mobile-responsive
- [ ] Unsubscribe links work correctly
- [ ] Email tracking prevents duplicate sends
- [ ] Error handling for failed email sends

---

## Next Steps

1. **Implement Database Schema** - Add email tracking table
2. **Add Email Triggers** - Update user journey code with email calls
3. **Set Up Background Jobs** - Create scheduler for time-based emails
4. **Test Email Flow** - Test each email trigger end-to-end
5. **Monitor Metrics** - Track email open rates and engagement

---

## Change Management Notes

**Status:** 📋 Implementation Guide Created  
**Next Actions:**
- Change Management Agent should track implementation progress
- Development team should integrate email triggers
- QA should test email flow
- Monitor email delivery and engagement metrics

**Agent Responsibility:** Change Management Agent should ensure email triggers are properly integrated and monitor email delivery success rates.




