# Agentic AI Project Structure

This document describes the agentic AI system structure that has been set up in this project.

## Directory Structure

```
.
├── src/                    # Core application code
│   ├── agents/            # Agent behaviors and types
│   ├── tools/             # Agent-callable tools
│   ├── workflows/         # Predefined sequences of agent interactions
│   ├── models/            # Language models, embeddings, and prompt management
│   ├── api/               # RESTful API endpoints and WebSocket handlers
│   ├── cognition/         # Cognitive processes enabling intelligent agent behavior
│   ├── execution/         # Operational execution of planned tasks
│   ├── auth/              # Security and authentication mechanisms
│   └── crew.py            # CrewAI integration entry point
├── config/                 # Application configuration and environment settings
│   ├── .env.example       # Environment variables template
│   ├── dev.py             # Development configuration
│   └── prod.py            # Production configuration
├── data/                   # Persistent runtime data
│   ├── state/             # Agent and workflow state
│   └── knowledge_bases/    # Knowledge base storage
├── deployment/             # Infrastructure-as-Code and deployment configurations
├── evaluation/             # Tools for benchmarking, testing, and performance profiling
├── providers/              # Clients for external services and third-party APIs
├── utils/                  # Shared utilities, exceptions, logging, retry mechanisms
├── docs/                   # Project documentation (existing)
├── scripts/                # CLI and CI/CD scripts (existing)
├── tests/                  # Test code (existing)
└── logs/                   # Application log files (existing)
```

## Key Components

### Agents (`src/agents/`)

Agents are autonomous entities that can perceive their environment, make decisions, and take actions.

- **BaseAgent**: Abstract base class for all agents
- **Agent Protocol**: Interface definition for agent implementations
- See `src/agents/README.md` for details

### Tools (`src/tools/`)

Tools provide capabilities that agents can use to interact with the environment.

- **BaseTool**: Abstract base class for all tools
- **Tool Protocol**: Interface definition for tool implementations
- See `src/tools/README.md` for details

### Workflows (`src/workflows/`)

Workflows orchestrate multiple agents to accomplish complex tasks.

- **BaseWorkflow**: Abstract base class for all workflows
- **Workflow Protocol**: Interface definition for workflow implementations
- See `src/workflows/README.md` for details

### Models (`src/models/`)

Language models, embeddings, and prompt management.

- **LanguageModel Protocol**: Interface for LLM providers
- **EmbeddingModel Protocol**: Interface for embedding models
- Prompt templates and management utilities

### Configuration (`config/`)

Environment-specific configuration management.

- `.env.example`: Template for environment variables
- `dev.py`: Development environment settings
- `prod.py`: Production environment settings

### Utilities (`utils/`)

Shared utilities and helpers.

- **exceptions.py**: Custom exception classes
- **logger.py**: Logging configuration utilities
- **retry.py**: Retry mechanisms for handling transient failures

## Getting Started

1. **Set up environment variables**:
   ```bash
   cp config/.env.example config/.env
   # Edit config/.env with your values
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt  # If you create one
   ```

3. **Create your first agent**:
   ```python
   from src.agents.base_agent import BaseAgent
   
   class MyAgent(BaseAgent):
       def perceive(self, environment):
           # Your perception logic
           pass
       
       def decide(self, perception):
           # Your decision logic
           pass
       
       def act(self, decision):
           # Your action logic
           pass
   ```

4. **Create your first tool**:
   ```python
   from src.tools.base_tool import BaseTool
   
   class MyTool(BaseTool):
       name = "my_tool"
       description = "Does something useful"
       
       def execute(self, **kwargs):
           # Your tool logic
           pass
   ```

5. **Create your first workflow**:
   ```python
   from src.workflows.base_workflow import BaseWorkflow
   
   class MyWorkflow(BaseWorkflow):
       def execute(self, context):
           # Your workflow logic
           pass
   ```

## Integration with Existing Project

This agentic AI structure is designed to work alongside the existing JobMatch AI project:

- **Backend Integration**: The `src/api/` module can integrate with the existing FastAPI backend
- **Agent System**: The new agent system complements the existing `.cursor/agents/` configuration
- **Shared Resources**: Uses existing `data/`, `logs/`, `docs/`, and `tests/` directories

## Next Steps

1. Implement specific agents for your use cases
2. Create tools for agent capabilities
3. Define workflows for complex tasks
4. Set up API endpoints in `src/api/`
5. Configure authentication in `src/auth/`
6. Add evaluation benchmarks in `evaluation/`
7. Set up deployment configurations in `deployment/`

## References

- [CrewAI Documentation](https://docs.crewai.com/)
- [LangChain Documentation](https://python.langchain.com/)
- Project-specific agent configurations: `.cursor/agents/`

