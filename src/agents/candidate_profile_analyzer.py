"""
Candidate Profile Analyzer Agent

Expert in analyzing candidate resumes and profiles to extract relevant skills,
experience, and education for accurate matching.
"""

from typing import Dict, Any, List, Optional
from src.agents.base_agent import BaseAgent
from src.models import LanguageModel


class CandidateProfileAnalyzerAgent(BaseAgent):
    """
    Analyzes candidate profiles/resumes to extract structured information.
    
    Output format:
    {
        'skills': List[str],
        'experience_years': int,
        'education': List[Dict[str, str]],
        'summary': str,
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
            name=name or "Candidate Profile Analyzer",
            description="Expert in analyzing candidate resumes and profiles",
            capabilities=["nlp", "extraction", "analysis"]
        )
        self.llm = llm
        self.system_prompt = """You are an expert in analyzing candidate resumes and profiles to extract 
relevant skills, experience, and education. Your goal is to create a structured representation of a 
candidate's profile that can be used for accurate matching.

Output should be a JSON object with the following keys:
- 'skills': A list of technical and soft skills
- 'experience_years': Total years of relevant experience (as an integer)
- 'education': A list of education entries, each with 'degree', 'field', 'institution', 'year'
- 'summary': A brief professional summary
- 'keywords': A list of important keywords for matching
- 'ambiguities': A list of any ambiguous or unclear aspects of the profile

Be extremely thorough and consider edge cases. If the profile is ambiguous, flag it and explain the ambiguity."""
    
    def perceive(self, environment: Dict[str, Any]) -> Dict[str, Any]:
        """Extract candidate profile from environment."""
        candidate_profile = environment.get("candidate_profile", "")
        source = environment.get("source", "unknown")  # URL, file path, or direct text
        
        if not candidate_profile:
            raise ValueError("Candidate profile is required in environment")
        
        return {
            "candidate_profile": candidate_profile,
            "source": source,
            "timestamp": self.created_at.isoformat()
        }
    
    def decide(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """Decide on analysis approach based on candidate profile."""
        candidate_profile = perception["candidate_profile"]
        
        # Determine if we need to handle special cases
        is_resume_format = any(keyword in candidate_profile.lower() for keyword in 
                              ["education", "experience", "skills", "objective"])
        is_long = len(candidate_profile) > 5000
        
        return {
            "candidate_profile": candidate_profile,
            "analysis_strategy": {
                "is_resume_format": is_resume_format,
                "handle_long_text": is_long,
                "chunking_needed": is_long
            }
        }
    
    def act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Execute candidate profile analysis using LLM."""
        candidate_profile = decision["candidate_profile"]
        
        # Construct the prompt
        user_prompt = f"""Analyze the following candidate profile/resume and extract structured information:

{candidate_profile}

Provide your analysis as a JSON object with the keys: skills, experience_years, education, 
summary, keywords, and ambiguities."""
        
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
        required_keys = ['skills', 'experience_years', 'education', 'summary', 'keywords']
        for key in required_keys:
            if key not in analysis_result:
                if key == 'experience_years':
                    analysis_result[key] = 0
                elif key == 'summary':
                    analysis_result[key] = ""
                else:
                    analysis_result[key] = []
        
        if 'ambiguities' not in analysis_result:
            analysis_result['ambiguities'] = []
        
        # Ensure education is a list of dicts
        if isinstance(analysis_result.get('education'), str):
            analysis_result['education'] = []
        
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

