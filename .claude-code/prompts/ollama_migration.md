# Ollama Migration Prompt Template

## Context

Migrating from OpenAI API to Ollama (llama3.2) for cost-free, local-only development.

## Pattern

Reference: `backend/llm/ollama_client.py`, `docker-compose.yml` (ollama service)

## Migration Steps

### 1. Replace OpenAI Client

**Before:**
```python
from openai import OpenAI
client = OpenAI(api_key=settings.OPENAI_API_KEY)
response = client.chat.completions.create(...)
```

**After:**
```python
from ollama import Client
client = Client(host=settings.OLLAMA_BASE_URL)
response = client.chat(model='llama3.2', messages=[...])
```

### 2. Update Configuration

```python
# backend/config.py
OLLAMA_BASE_URL: str = "http://ollama:11434"
OLLAMA_MODEL: str = "llama3.2"
```

### 3. Docker Compose Integration

```yaml
services:
  ollama:
    image: ollama/ollama:latest
    volumes:
      - ollama_data:/root/.ollama
    ports:
      - "11434:11434"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
```

### 4. Model Pull Script

```bash
# Pull llama3.2 on container start
docker compose exec ollama ollama pull llama3.2
```

## Files to Update

- `backend/ai/matching_engine.py`
- `backend/assessment/xdmiq_assessment.py`
- `backend/ai/articulation_assistant.py`
- `backend/ai/moderation.py`
- `backend/ai/bias_detector.py`
- `backend/config.py`
- `docker-compose.yml`

## Constraints

- MUST work offline (no external API calls)
- MUST use llama3.2 model (user preference)
- MUST maintain same API interface (abstract LLM client)
- MUST support fallback if Ollama unavailable

## Testing

```python
def test_ollama_connection():
    """Verify Ollama is accessible and llama3.2 is available."""
    client = Client(host="http://localhost:11434")
    models = client.list()
    assert "llama3.2" in [m["name"] for m in models["models"]]
```

## Benefits

- Zero API costs
- Local-only development
- Data privacy (no external API calls)
- Faster iteration (no rate limits)

