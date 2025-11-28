# Data Sources and Vector Database Recommendations

## Data Sources Supported

The system currently supports three primary data source types:

### 1. **Web URLs** (via WebScraperTool)
- Job board postings (Indeed, LinkedIn, Glassdoor, etc.)
- Company career pages
- LinkedIn candidate profiles
- Personal portfolio websites

**Implementation**: `src/tools/web_scraper.py`
- Uses `requests` and `BeautifulSoup` for HTML parsing
- Handles common web scraping challenges (JavaScript rendering may require Selenium/Playwright for SPAs)

**Example**:
```python
result = workflow.execute({
    "job_source": "https://company.com/careers/software-engineer",
    "candidate_source": "https://linkedin.com/in/john-doe"
})
```

### 2. **File Paths** (via FileReaderTool)
- Text files (.txt, .md)
- PDF resumes (.pdf) - requires PyPDF2
- Word documents (.docx) - requires python-docx
- JSON files (can be added)

**Implementation**: `src/tools/file_reader.py`
- Supports multiple file formats
- Handles encoding issues

**Example**:
```python
result = workflow.execute({
    "job_source": "./data/jobs/engineer.txt",
    "candidate_source": "./data/resumes/candidate.pdf"
})
```

### 3. **Direct Content** (via context parameters)
- Pre-extracted text
- API responses
- Database content
- Clipboard content

**Example**:
```python
result = workflow.execute({
    "job_content": "Full job description text...",
    "candidate_content": "Full resume text..."
})
```

## Recommended Vector Database Options

### Option 1: **ChromaDB** (Recommended for Development/Testing)
**Best for**: Local development, testing, small to medium datasets

**Pros**:
- Easy setup (no API keys needed)
- Local storage (privacy-friendly)
- Simple Python API
- Good for prototyping

**Cons**:
- Not suitable for production scale
- Limited cloud features

**Setup**:
```python
from src.tools.vector_db_storage import VectorDBStorageTool

vector_db = VectorDBStorageTool(
    provider="chroma",
    connection_params={"persist_directory": "./chroma_db"}
)
```

**Installation**:
```bash
pip install chromadb
```

### Option 2: **Pinecone** (Recommended for Production)
**Best for**: Production deployments, large-scale applications, cloud-native

**Pros**:
- Fully managed cloud service
- Excellent scalability
- Built-in metadata filtering
- Production-ready

**Cons**:
- Requires API key and account
- Costs scale with usage
- Less control over infrastructure

**Setup**:
```python
vector_db = VectorDBStorageTool(
    provider="pinecone",
    connection_params={
        "api_key": os.getenv("PINECONE_API_KEY"),
        "environment": "us-east1-gcp",  # or your preferred region
        "index_name": "jobmatch"
    }
)
```

**Installation**:
```bash
pip install pinecone-client
```

**Getting Started**:
1. Sign up at https://www.pinecone.io/
2. Create an index (recommended dimensions: 1536 for OpenAI embeddings)
3. Get your API key and environment name

### Option 3: **Weaviate** (Recommended for Self-Hosted)
**Best for**: Self-hosted deployments, full control, enterprise

**Pros**:
- Open source
- Self-hostable (full control)
- Advanced querying capabilities
- GraphQL API

**Cons**:
- Requires infrastructure management
- More complex setup
- Steeper learning curve

**Setup**:
```python
vector_db = VectorDBStorageTool(
    provider="weaviate",
    connection_params={"url": "http://localhost:8080"}  # or your Weaviate URL
)
```

**Installation**:
```bash
pip install weaviate-client
```

**Getting Started**:
1. Run Weaviate via Docker: `docker run -p 8080:8080 semitechnologies/weaviate`
2. Or use Weaviate Cloud Services

## Recommendation by Use Case

### **Development/Testing**
→ **ChromaDB**
- Quick setup
- No external dependencies
- Perfect for prototyping

### **Production (Cloud)**
→ **Pinecone**
- Managed service
- Scalable
- Production-ready

### **Production (Self-Hosted)**
→ **Weaviate**
- Full control
- Enterprise features
- Open source

## Adding Custom Data Sources

You can easily add custom data sources by creating new tools:

```python
from src.tools.base_tool import BaseTool

class LinkedInAPITool(BaseTool):
    """Tool for fetching LinkedIn profiles via API."""
    
    name = "linkedin_api"
    description = "Fetches LinkedIn profiles using LinkedIn API"
    
    def execute(self, profile_id: str, **kwargs):
        # Your implementation
        pass

class ATSIntegrationTool(BaseTool):
    """Tool for integrating with ATS systems."""
    
    name = "ats_integration"
    description = "Fetches job descriptions from ATS systems"
    
    def execute(self, ats_name: str, job_id: str, **kwargs):
        # Your implementation
        pass
```

Then add to the Data Ingestion Agent:
```python
ingestion_agent = DataIngestionAgent(
    job_analyzer=job_analyzer,
    candidate_analyzer=candidate_analyzer,
    tools=[web_scraper, file_reader, vector_db, linkedin_api, ats_tool]
)
```

## Data Source Priority Recommendations

1. **For Job Descriptions**:
   - Primary: Company career pages (most accurate)
   - Secondary: Job boards (Indeed, LinkedIn)
   - Tertiary: ATS exports

2. **For Candidate Profiles**:
   - Primary: LinkedIn profiles (structured, comprehensive)
   - Secondary: Resume files (PDF/DOCX)
   - Tertiary: Application forms

## Next Steps

1. **Choose your vector database** based on your use case
2. **Set up API keys** if using cloud services
3. **Test with sample data** from your preferred sources
4. **Implement custom tools** for any specialized data sources
5. **Set up monitoring** for data ingestion quality

## Questions?

- **Data source integration**: See `src/tools/` directory
- **Vector DB setup**: See `src/tools/vector_db_storage.py`
- **Custom tool creation**: See `src/tools/base_tool.py`

