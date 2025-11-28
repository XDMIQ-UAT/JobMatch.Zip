"""
Data Ingestion Agent

Responsible for ingesting job descriptions and candidate profiles into structured format.
"""

from typing import Dict, Any, List, Optional
from src.agents.base_agent import BaseAgent
from src.tools import Tool


class DataIngestionAgent(BaseAgent):
    """
    Ingests job descriptions and candidate profiles into structured format.
    
    Coordinates with JobDescriptionAnalyzerAgent and CandidateProfileAnalyzerAgent
    to extract information and store it in a vector database.
    """
    
    def __init__(
        self,
        job_analyzer: BaseAgent,
        candidate_analyzer: BaseAgent,
        tools: Optional[List[Tool]] = None,
        agent_id: Optional[str] = None,
        name: Optional[str] = None
    ):
        super().__init__(
            agent_id=agent_id,
            name=name or "Data Ingestion Agent",
            description="Ingests job descriptions and candidate profiles into structured format",
            capabilities=["ingestion", "data_processing", "storage"]
        )
        self.job_analyzer = job_analyzer
        self.candidate_analyzer = candidate_analyzer
        self.tools = tools or []
        self._tool_map = {tool.name: tool for tool in self.tools}
    
    def perceive(self, environment: Dict[str, Any]) -> Dict[str, Any]:
        """Extract ingestion request from environment."""
        source = environment.get("source")  # URL, file path, or direct text
        content_type = environment.get("content_type")  # "job_description" or "candidate_profile"
        content = environment.get("content")  # Direct content (optional if source provided)
        
        if not source and not content:
            raise ValueError("Either source or content must be provided")
        
        if not content_type:
            raise ValueError("content_type must be 'job_description' or 'candidate_profile'")
        
        return {
            "source": source,
            "content_type": content_type,
            "content": content,
            "timestamp": self.created_at.isoformat()
        }
    
    def decide(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """Decide on ingestion approach."""
        source = perception["source"]
        content_type = perception["content_type"]
        content = perception.get("content")
        
        # Determine if we need to fetch content
        needs_fetch = source and not content
        
        # Determine which analyzer to use
        use_job_analyzer = content_type == "job_description"
        use_candidate_analyzer = content_type == "candidate_profile"
        
        # Determine which tool to use for fetching
        fetch_tool = None
        if needs_fetch:
            if source.startswith("http://") or source.startswith("https://"):
                fetch_tool = self._tool_map.get("web_scraper")
            elif "/" in source or "\\" in source:
                fetch_tool = self._tool_map.get("file_reader")
        
        return {
            "source": source,
            "content_type": content_type,
            "content": content,
            "needs_fetch": needs_fetch,
            "fetch_tool": fetch_tool.name if fetch_tool else None,
            "use_job_analyzer": use_job_analyzer,
            "use_candidate_analyzer": use_candidate_analyzer
        }
    
    def act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Execute data ingestion."""
        source = decision["source"]
        content_type = decision["content_type"]
        content = decision.get("content")
        needs_fetch = decision["needs_fetch"]
        fetch_tool_name = decision.get("fetch_tool")
        
        errors = []
        
        # Step 1: Fetch content if needed
        if needs_fetch:
            if fetch_tool_name:
                fetch_tool = self._tool_map.get(fetch_tool_name)
                if fetch_tool:
                    try:
                        content = fetch_tool.execute(source=source)
                        if isinstance(content, dict):
                            content = content.get("content", content.get("text", ""))
                    except Exception as e:
                        errors.append(f"Failed to fetch content: {str(e)}")
                        return {
                            "status": "error",
                            "errors": errors,
                            "agent_id": self.agent_id
                        }
                else:
                    errors.append(f"Tool '{fetch_tool_name}' not found")
            else:
                errors.append("No fetch tool available for source type")
        
        if not content:
            errors.append("No content available after fetch")
            return {
                "status": "error",
                "errors": errors,
                "agent_id": self.agent_id
            }
        
        # Step 2: Analyze content using appropriate analyzer
        analysis_result = None
        try:
            if decision["use_job_analyzer"]:
                analysis_result = self.job_analyzer.run({
                    "job_description": content,
                    "source": source
                })
            elif decision["use_candidate_analyzer"]:
                analysis_result = self.candidate_analyzer.run({
                    "candidate_profile": content,
                    "source": source
                })
        except Exception as e:
            errors.append(f"Failed to analyze content: {str(e)}")
            return {
                "status": "error",
                "errors": errors,
                "agent_id": self.agent_id
            }
        
        # Step 3: Store in vector database (if tool available)
        storage_result = None
        storage_tool = self._tool_map.get("vector_db_storage")
        if storage_tool:
            try:
                storage_result = storage_tool.execute(
                    content_type=content_type,
                    source=source,
                    analysis=analysis_result.get("analysis") if analysis_result else None,
                    raw_content=content
                )
            except Exception as e:
                errors.append(f"Failed to store in database: {str(e)}")
        
        # Update agent state
        self.update_state({
            "ingestion_count": self.state.get("ingestion_count", 0) + 1,
            "last_ingestion": {
                "content_type": content_type,
                "source": source,
                "timestamp": self.created_at.isoformat()
            }
        })
        
        return {
            "status": "success" if not errors else "partial_success",
            "content_type": content_type,
            "source": source,
            "analysis": analysis_result.get("analysis") if analysis_result else None,
            "storage_result": storage_result,
            "errors": errors,
            "agent_id": self.agent_id
        }

