# AI Job Match Chat - Subscriber Feature Documentation

## Overview
The AI Job Match Chat is a personalized conversational assistant exclusively for subscribed users, powered by OpenRouter and focused solely on job matching.

## Feature Access

**URL:** http://localhost:3000/dashboard

**Requirements:**
- Active subscription (currently set to `true` for testing)
- Anonymous or authenticated session

## What It Does

The AI Job Match Chat provides:
- **Personalized job search assistance** through natural conversation
- **Job discovery** based on user skills, preferences, and location
- **Clarifying questions** to better understand user needs
- **Market insights** relevant to the user's search

## What It Does NOT Do

To maintain focus and OpenRouter credit efficiency:
- ❌ **NO interview preparation** advice
- ❌ **NO resume writing** or review
- ❌ **NO career coaching** beyond job matching
- ❌ **NO generic career advice**

## Architecture

### Frontend Component
**File:** `frontend/src/components/JobMatchChat.tsx`

**Features:**
- Real-time chat interface with message history
- Auto-scroll to latest messages
- Loading states with animated indicators
- Example prompts for new users
- Keyboard shortcuts (Enter to send, Shift+Enter for new line)
- Subscriber badge display

**Props:**
```typescript
interface JobMatchChatProps {
  userId?: string;
  anonymousId?: string;
  userProfile?: {
    skills?: string[];
    preferences?: string;
    location?: string;
  };
  onJobMatch?: (jobId: string) => void;
  className?: string;
}
```

### Backend API Endpoint
**File:** `backend/api/chat.py`

**Endpoint:** `POST /api/chat/job-match`

**Request:**
```json
{
  "message": "I'm looking for remote Python developer roles",
  "context": {
    "userId": "anonymous-123",
    "skills": ["Python", "FastAPI", "React"],
    "preferences": "remote",
    "location": "San Francisco"
  },
  "conversationHistory": [
    {"role": "user", "content": "Previous message"},
    {"role": "assistant", "content": "Previous response"}
  ]
}
```

**Response:**
```json
{
  "message": "Based on your Python and FastAPI skills...",
  "suggestedJobs": ["job-id-1", "job-id-2"],
  "provider": "openrouter",
  "model": "anthropic/claude-3.5-sonnet"
}
```

### System Prompt

The AI is constrained by a focused system prompt that:
1. Includes user profile (skills, location, preferences)
2. Defines clear responsibilities (job matching only)
3. Sets explicit restrictions (no interview prep/resume help)
4. Instructs redirection of off-topic questions

**Key Sections:**
- User Profile context
- Responsibilities (4 core tasks)
- Important Restrictions (5 clear boundaries)
- Goal statement

## User Flow

### 1. Access Dashboard
```
User visits /dashboard
  ↓
System checks subscription status
  ↓
If subscribed → Show chat interface
If not → Show subscription CTA
```

### 2. Chat Interaction
```
User types message
  ↓
Frontend sends to /api/chat/job-match with:
  - User message
  - Context (skills, location, preferences)
  - Last 10 messages for conversation continuity
  ↓
Backend:
  - Builds system prompt with user profile
  - Adds conversation history
  - Calls OpenRouter LLM
  - Returns AI response
  ↓
Frontend displays response with:
  - AI avatar and name
  - Formatted message
  - Timestamp
```

### 3. Job Suggestions
```
If AI suggests specific jobs
  ↓
Backend returns job IDs in response
  ↓
Frontend calls onJobMatch callback
  ↓
User can view job details or save to favorites
```

## Example Conversations

### Good: Job Search Help
```
User: "I'm looking for remote software engineering roles"
AI: "Great! With your Python, FastAPI, and React skills, you're 
     well-positioned for full-stack roles. Are you interested in:
     - Startup environments
     - Enterprise companies
     - Specific industries like fintech or healthcare?"

User: "Preferably fintech startups"
AI: "Excellent choice! Fintech startups often value your skill set.
     I'll look for remote positions that match. Are you open to:
     - Crypto/blockchain companies
     - Payment processing platforms
     - Investment/trading tech?"
```

### Boundary Enforcement
```
User: "Can you review my resume?"
AI: "I focus specifically on matching you with job opportunities. 
     For resume help, I'd recommend professional resume services. 
     
     What I can help with is understanding what roles match your 
     background. Would you like to tell me about your experience 
     so I can suggest relevant positions?"
```

## Configuration

### Environment Variables

**Backend (`docker-compose.yml`):**
```yaml
- LLM_PROVIDER=openrouter
- OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
- LLM_MODEL=anthropic/claude-3.5-sonnet
```

**Frontend:**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Subscription Status

Currently hardcoded for testing:
```typescript
const [isSubscribed, setIsSubscribed] = useState(true);
```

**TODO:** Implement actual subscription check via backend API

## Testing

### Manual Testing

1. **Access Chat:**
   ```
   Navigate to http://localhost:3000/dashboard
   ```

2. **Test Job Matching Questions:**
   - "Show me remote developer roles"
   - "What entry-level positions are available?"
   - "I want to work in AI/ML"

3. **Test Boundary Enforcement:**
   - "Can you help with my resume?"
   - "How do I prepare for interviews?"
   - "Should I negotiate salary?"

4. **Verify Context Awareness:**
   - Check that AI references user's skills
   - Verify location/preferences are considered
   - Confirm conversation history is maintained

### API Testing

**Test Chat Endpoint:**
```bash
curl -X POST http://localhost:8000/api/chat/job-match \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I'\''m looking for Python roles",
    "context": {
      "userId": "test-123",
      "skills": ["Python", "Django"],
      "preferences": "remote",
      "location": "New York"
    }
  }'
```

**Expected Response:**
```json
{
  "message": "Based on your Python and Django experience...",
  "suggestedJobs": null,
  "provider": "openrouter",
  "model": "anthropic/claude-3.5-sonnet"
}
```

## OpenRouter Credits

### Usage Tracking

Each conversation consumes OpenRouter credits based on:
- **Model:** claude-3.5-sonnet (higher quality, moderate cost)
- **Context size:** User profile + last 10 messages
- **Response length:** Max 500 tokens per response

### Cost Optimization

1. **Conversation History:** Limited to last 10 messages
2. **Max Tokens:** Capped at 500 per response
3. **System Prompt:** Concise but comprehensive
4. **Focus:** Restricting scope reduces unnecessary back-and-forth

### Estimated Costs

Per conversation (rough estimates):
- **Input tokens:** ~300-500 tokens (prompt + history)
- **Output tokens:** ~200-500 tokens (response)
- **Total per message:** ~500-1000 tokens

**Note:** Actual costs vary by model and conversation length. Monitor OpenRouter dashboard for precise usage.

## Future Enhancements

### Phase 2
- [ ] Actual subscription verification via backend
- [ ] Job database integration for real suggestions
- [ ] Save conversation history to database
- [ ] Export conversation to PDF

### Phase 3
- [ ] Canvas layer for accessibility (as mentioned in requirements)
- [ ] Voice input/output for hands-free interaction
- [ ] Multi-language support
- [ ] Advanced filters in chat (salary range, company size, etc.)

### Phase 4
- [ ] Integration with job application tracking
- [ ] Email/SMS notifications for matches
- [ ] Scheduled check-ins with users
- [ ] Analytics dashboard for admins

## Troubleshooting

### Chat Not Working

**Issue:** Frontend shows error message

**Checks:**
1. Verify backend is running: `docker ps | grep backend`
2. Check OpenRouter API key is set: `docker exec jobmatch-backend env | grep OPENROUTER`
3. View backend logs: `docker logs jobmatch-backend`

### OpenRouter API Errors

**Issue:** 401 Unauthorized

**Solution:** Verify `OPENROUTER_API_KEY` in `.env` file

**Issue:** 429 Rate Limited

**Solution:** OpenRouter rate limits hit. Wait or upgrade plan.

### AI Responses Off-Topic

**Issue:** AI provides resume/interview advice

**Solution:** System prompt may need strengthening. Update prompt in `backend/api/chat.py` to be more explicit.

## Deployment Checklist

- [x] JobMatchChat component created
- [x] Backend API endpoint implemented
- [x] Dashboard page created
- [x] System prompt configured
- [x] Docker containers rebuilt
- [x] Services restarted
- [ ] OpenRouter API key configured
- [ ] Subscription system integrated
- [ ] Job database connected
- [ ] Production testing completed

## Support & Maintenance

**Owner:** Development Team  
**Last Updated:** November 24, 2025  
**Version:** 1.0.0

For issues or questions:
1. Check backend logs: `docker logs jobmatch-backend`
2. Check frontend console for errors
3. Verify OpenRouter dashboard for API issues
4. Review conversation history for context problems

---

**Note:** This feature is currently in beta for subscribed users. Canvas accessibility layer will be added in future update as specified in requirements.
