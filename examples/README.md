# Examples

This directory contains example scripts demonstrating how to use the agentic AI system for unbiased job matching.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements-agentic-ai.txt
```

### 2. Set API Key

```bash
# For OpenAI
export OPENAI_API_KEY="your-key-here"

# OR for OpenRouter
export OPENROUTER_API_KEY="your-key-here"
```

### 3. Run Quick Start Demo

```bash
python examples/quick_start_demo.py
```

This will:
- Initialize all agents
- Run a sample job matching scenario
- Display detailed results including bias detection

## Example Scripts

### `quick_start_demo.py`
**Purpose**: Complete end-to-end demo with sample data

**Usage**:
```bash
python examples/quick_start_demo.py
```

**What it does**:
- Sets up all agents and tools
- Runs matching on sample job description and candidate profile
- Displays comprehensive results including:
  - Match score
  - Recommendation
  - Bias analysis
  - Strengths and gaps

### `custom_data_source_example.py`
**Purpose**: Shows how to create custom data source tools

**Usage**:
```python
from examples.custom_data_source_example import LinkedInAPITool, ATSIntegrationTool

# Create custom tools
linkedin_tool = LinkedInAPITool(api_key="your-key")
ats_tool = ATSIntegrationTool(ats_name="greenhouse")

# Use with Data Ingestion Agent
# (See script for full example)
```

**What it demonstrates**:
- Creating custom tools for LinkedIn API
- Creating custom tools for ATS integration
- Creating custom tools for database queries

### `vector_db_setup_examples.py`
**Purpose**: Demonstrates different vector database setups

**Usage**:
```bash
python examples/vector_db_setup_examples.py
```

**What it demonstrates**:
- ChromaDB setup (local)
- Pinecone setup (cloud)
- Weaviate setup (self-hosted)

## Customization Examples

### Using Different LLM Providers

```python
# OpenAI
from src.models.llm_providers import OpenAILanguageModel
llm = OpenAILanguageModel(model="gpt-4")

# OpenRouter (supports multiple models)
from src.models.llm_providers import OpenRouterLanguageModel
llm = OpenRouterLanguageModel(model="anthropic/claude-3.5-sonnet")
```

### Using Different Data Sources

```python
# From URL
result = workflow.execute({
    "job_source": "https://company.com/careers/job-123",
    "candidate_source": "https://linkedin.com/in/candidate"
})

# From files
result = workflow.execute({
    "job_source": "./data/jobs/engineer.txt",
    "candidate_source": "./data/resumes/candidate.pdf"
})

# Direct content
result = workflow.execute({
    "job_content": "Full job description...",
    "candidate_content": "Full resume text..."
})
```

### Customizing Agent Prompts

```python
# Modify system prompt
job_analyzer = JobDescriptionAnalyzerAgent(llm=llm)
job_analyzer.system_prompt = "Your custom prompt here..."
```

## Next Steps

1. **Run the quick start demo** to see the system in action
2. **Try with your own data** - modify the demo script with your job descriptions and resumes
3. **Customize agents** - adjust prompts for your specific use case
4. **Add custom tools** - integrate with your data sources
5. **Set up vector DB** - choose and configure your preferred vector database

## Troubleshooting

### API Key Issues
- Make sure your API key is set: `echo $OPENAI_API_KEY`
- Check API quotas and limits
- Try OpenRouter as an alternative

### Import Errors
- Install dependencies: `pip install -r requirements-agentic-ai.txt`
- Check Python version (3.8+ required)

### Vector DB Errors
- ChromaDB: No setup needed, works out of the box
- Pinecone: Requires API key and account
- Weaviate: Requires running instance (Docker)

## More Information

- **Full Guide**: See `UNBIASED_JOB_MATCHING_GUIDE.md`
- **Data Sources**: See `DATA_SOURCES_AND_VECTOR_DB.md`
- **Project Structure**: See `AGENTIC_AI_SETUP.md`

