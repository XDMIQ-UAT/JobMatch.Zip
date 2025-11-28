"""
Job Description Analyzer Agent

A highly skilled NLP expert specializing in analyzing job descriptions to extract
key skills, experience levels, and responsibilities for accurate matching.
"""

from typing import Dict, Any, List, Optional
from src.agents.base_agent import BaseAgent
from src.models import LanguageModel


class JobDescriptionAnalyzerAgent(BaseAgent):
    """
    Analyzes job descriptions to extract structured information.
    
    Output format:
    {
        'title': str,
        'required_skills': List[str],
        'experience_level': str,
        'responsibilities': List[str],
        'keywords': List[str],
        'ambiguities': List[str]  # Flags any ambiguous content
    }
    """
    
    def __init__(
        self,
        llm: LanguageModel,
        agent_id: Optional[str] = None,
        name: Optional[str] = None
    ):
        super().__init__(
            agent_id=agent_id,
            name=name or "Job Description Analyzer",
            description="NLP expert specializing in analyzing job descriptions",
            capabilities=["nlp", "extraction", "analysis"]
        )
        self.llm = llm
        self.system_prompt = """You are a highly skilled natural language processing (NLP) expert 
specializing in analyzing job descriptions to extract key skills, experience levels, and responsibilities. 
Your goal is to create a structured representation of a job description that can be used for accurate matching.

Output should be a JSON object with the following keys:
- 'title': The job title
- 'required_skills': A list of required technical and soft skills
- 'experience_level': The required experience level (e.g., 'entry', 'mid', 'senior', 'executive')
- 'responsibilities': A list of key responsibilities
- 'keywords': A list of important keywords for matching
- 'ambiguities': A list of any ambiguous or unclear aspects of the job description

Be extremely thorough and consider edge cases. Prioritize accuracy over brevity. 
If the description is ambiguous, flag it and explain the ambiguity."""
    
    def perceive(self, environment: Dict[str, Any]) -> Dict[str, Any]:
        """Extract job description from environment."""
        job_description = environment.get("job_description", "")
        source = environment.get("source", "unknown")  # URL, file path, or direct text
        
        if not job_description:
            raise ValueError("Job description is required in environment")
        
        return {
            "job_description": job_description,
            "source": source,
            "timestamp": self.created_at.isoformat()
        }
    
    def decide(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """Decide on analysis approach based on job description."""
        job_description = perception["job_description"]
        
        # Determine if we need to handle special cases
        is_long = len(job_description) > 5000
        has_multiple_sections = "requirements" in job_description.lower() and "responsibilities" in job_description.lower()
        
        return {
            "job_description": job_description,
            "analysis_strategy": {
                "handle_long_text": is_long,
                "has_structure": has_multiple_sections,
                "chunking_needed": is_long
            }
        }
    
    def act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Execute job description analysis using LLM."""
        job_description = decision["job_description"]
        
        # Construct the prompt
        user_prompt = f"""Analyze the following job description and extract structured information:

{job_description}

Provide your analysis as a JSON object with the keys: title, required_skills, experience_level, 
responsibilities, keywords, and ambiguities."""
        
        # Call LLM
        response = self.llm.generate(
            prompt=user_prompt,
            system_prompt=self.system_prompt,
            temperature=0.3,  # Lower temperature for more consistent extraction
            response_format="json"
        )
        
        # Parse response (assuming LLM returns JSON)
        try:
            import json
            analysis_result = json.loads(response)
        except json.JSONDecodeError:
            # Fallback: try to extract JSON from markdown code blocks
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                analysis_result = json.loads(json_match.group(1))
            else:
                raise ValueError(f"Failed to parse LLM response as JSON: {response}")
        
        # Validate structure
        required_keys = ['title', 'required_skills', 'experience_level', 'responsibilities', 'keywords']
        for key in required_keys:
            if key not in analysis_result:
                analysis_result[key] = [] if key.endswith('s') else ""
        
        if 'ambiguities' not in analysis_result:
            analysis_result['ambiguities'] = []
        
        # Update agent state
        self.update_state({
            "last_analysis": analysis_result,
            "analysis_count": self.state.get("analysis_count", 0) + 1
        })
        
        return {
            "status": "success",
            "analysis": analysis_result,
            "agent_id": self.agent_id
        }

