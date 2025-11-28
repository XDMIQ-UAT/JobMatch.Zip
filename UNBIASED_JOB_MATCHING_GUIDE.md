# Unbiased Job Matching System - Implementation Guide

This document provides a comprehensive guide to using the agentic AI system for unbiased job matching.

## Overview

The system consists of 6 core agents working together:

1. **Job Description Analyzer** - Extracts structured information from job descriptions
2. **Candidate Profile Analyzer** - Extracts structured information from candidate profiles
3. **Data Ingestion Agent** - Handles ingestion from various sources
4. **Bias Detection Agent** (CRITICAL) - Identifies potential biases
5. **Matching Agent** - Determines match quality with bias awareness
6. **Workflow Orchestrator** - Coordinates the entire process

## Quick Start

### 1. Set Up Environment

```bash
# Install dependencies
pip install openai anthropic requests beautifulsoup4 pinecone-client

# Set environment variables
export OPENAI_API_KEY="your-key-here"
# OR
export OPENROUTER_API_KEY="your-key-here"
```

### 2. Initialize Agents

```python
from src.models.llm_providers import OpenAILanguageModel, OpenAIEmbeddingModel
from src.agents.job_description_analyzer import JobDescriptionAnalyzerAgent
from src.agents.candidate_profile_analyzer import CandidateProfileAnalyzerAgent
from src.agents.bias_detection_agent import BiasDetectionAgent
from src.agents.matching_agent import MatchingAgent
from src.agents.data_ingestion_agent import DataIngestionAgent
from src.tools.web_scraper import WebScraperTool
from src.tools.file_reader import FileReaderTool
from src.tools.vector_db_storage import VectorDBStorageTool
from src.workflows.job_matching_workflow import JobMatchingWorkflow

# Initialize LLM
llm = OpenAILanguageModel(model="gpt-4")
embedding_model = OpenAIEmbeddingModel()

# Initialize analyzers
job_analyzer = JobDescriptionAnalyzerAgent(llm=llm)
candidate_analyzer = CandidateProfileAnalyzerAgent(llm=llm)
bias_detector = BiasDetectionAgent(llm=llm)
matcher = MatchingAgent(llm=llm, embedding_model=embedding_model)

# Initialize tools
web_scraper = WebScraperTool()
file_reader = FileReaderTool()
vector_db = VectorDBStorageTool(provider="chroma")  # or "pinecone", "weaviate"

# Initialize data ingestion agent
ingestion_agent = DataIngestionAgent(
    job_analyzer=job_analyzer,
    candidate_analyzer=candidate_analyzer,
    tools=[web_scraper, file_reader, vector_db]
)

# Initialize workflow
workflow = JobMatchingWorkflow(
    data_ingestion_agent=ingestion_agent,
    job_analyzer=job_analyzer,
    candidate_analyzer=candidate_analyzer,
    bias_detection_agent=bias_detector,
    matching_agent=matcher
)
```

### 3. Run Matching

```python
# Example 1: Using URLs
result = workflow.execute({
    "job_source": "https://example.com/job-posting",
    "candidate_source": "https://example.com/candidate-profile"
})

# Example 2: Using direct content
result = workflow.execute({
    "job_content": "We are looking for a senior software engineer...",
    "candidate_content": "I have 10 years of experience in software development..."
})

# Example 3: Mixed (URL for job, content for candidate)
result = workflow.execute({
    "job_source": "https://example.com/job-posting",
    "candidate_content": "Resume content here..."
})
```

### 4. Interpret Results

```python
if result["status"] == "completed":
    final_rec = result["final_recommendation"]
    
    print(f"Match Score: {final_rec['match_score']:.2%}")
    print(f"Recommendation: {final_rec['recommendation']}")
    print(f"Bias Severity: {final_rec['bias_severity']}")
    
    print("\nStrengths:")
    for strength in final_rec['strengths']:
        print(f"  - {strength}")
    
    print("\nGaps:")
    for gap in final_rec['gaps']:
        print(f"  - {gap}")
    
    print(f"\nBias Considerations: {final_rec['bias_considerations']}")
```

## Data Sources

The system supports multiple data sources:

### 1. Web URLs
```python
result = workflow.execute({
    "job_source": "https://company.com/careers/job-123",
    "candidate_source": "https://linkedin.com/in/candidate"
})
```

### 2. File Paths
```python
result = workflow.execute({
    "job_source": "./data/job_descriptions/engineer.txt",
    "candidate_source": "./data/resumes/candidate.pdf"
})
```

### 3. Direct Content
```python
result = workflow.execute({
    "job_content": "Full job description text...",
    "candidate_content": "Full resume text..."
})
```

## Vector Database Options

### Option 1: ChromaDB (Local, Easy Setup)
```python
vector_db = VectorDBStorageTool(
    provider="chroma",
    connection_params={"persist_directory": "./chroma_db"}
)
```

### Option 2: Pinecone (Cloud, Scalable)
```python
vector_db = VectorDBStorageTool(
    provider="pinecone",
    connection_params={
        "api_key": "your-pinecone-key",
        "environment": "us-east1-gcp",
        "index_name": "jobmatch"
    }
)
```

### Option 3: Weaviate (Self-hosted or Cloud)
```python
vector_db = VectorDBStorageTool(
    provider="weaviate",
    connection_params={"url": "http://localhost:8080"}
)
```

## Bias Detection

The Bias Detection Agent identifies:

- **Gender bias**: Language that favors one gender
- **Age bias**: Requirements that exclude certain age groups
- **Disability bias**: Physical requirements that may be unnecessary
- **Cultural bias**: Language that excludes certain cultural backgrounds

### Example Bias Detection Output

```json
{
  "potential_biases": [
    {
      "type": "age",
      "description": "Requirement for 'recent graduate' may exclude experienced candidates",
      "location": "requirements section",
      "example": "Looking for recent graduates"
    }
  ],
  "severity_level": "medium",
  "mitigation_strategies": [
    "Focus on skills and competencies rather than graduation date",
    "Consider candidates with equivalent experience"
  ],
  "reasoning": "The requirement for recent graduates may unintentionally exclude..."
}
```

## Matching Score Interpretation

- **0.8 - 1.0**: Strong match, proceed with candidate
- **0.6 - 0.8**: Good match, may require review
- **0.4 - 0.6**: Moderate match, review recommended
- **0.0 - 0.4**: Poor match, likely reject

The recommendation also considers bias severity:
- **High bias severity**: May downgrade recommendation even with good match score
- **Low bias severity**: Normal scoring applies

## Iterative Refinement

### 1. Collect Feedback
Implement feedback loops to improve agent performance:

```python
# After matching, collect human feedback
feedback = {
    "match_id": result["workflow_id"],
    "human_review": "proceed",  # or "review", "reject"
    "human_score": 0.85,
    "comments": "Good match, but candidate lacks cloud experience"
}

# Store feedback for model improvement
```

### 2. Fine-tune Prompts
Adjust agent prompts based on performance:

```python
# Modify the system prompt in the agent
job_analyzer.system_prompt = "Your refined prompt here..."
```

### 3. Add Custom Tools
Extend functionality with custom tools:

```python
from src.tools.base_tool import BaseTool

class LinkedInScraperTool(BaseTool):
    name = "linkedin_scraper"
    description = "Scrapes LinkedIn profiles"
    
    def execute(self, profile_url: str, **kwargs):
        # Your implementation
        pass
```

## Best Practices

1. **Always run bias detection** - Never skip this step
2. **Review high-severity bias cases** - Human review recommended
3. **Store all analyses** - For auditing and improvement
4. **Monitor match scores** - Track distribution over time
5. **Regular audits** - Review system for bias patterns
6. **Explainability** - Always provide reasoning for matches

## Troubleshooting

### LLM API Errors
- Check API keys are set correctly
- Verify API quotas/limits
- Consider using OpenRouter as fallback

### Vector DB Errors
- Ensure database is running (for local instances)
- Check connection parameters
- Verify API keys (for cloud services)

### Parsing Errors
- Check input format (JSON parsing failures)
- Verify file encoding (UTF-8 recommended)
- Review agent prompts for clarity

## Next Steps

1. **Implement feedback collection** - Build system to collect human feedback
2. **Add more data sources** - Integrate with job boards, ATS systems
3. **Enhance bias detection** - Add more bias types and detection methods
4. **Build API endpoints** - Expose workflow via REST API
5. **Create evaluation suite** - Benchmark system performance
6. **Add monitoring** - Track system metrics and performance

## Questions?

For questions about:
- **Data sources**: See `src/tools/` directory
- **Agent customization**: See `src/agents/` directory
- **Workflow modification**: See `src/workflows/` directory
- **LLM providers**: See `src/models/llm_providers.py`

