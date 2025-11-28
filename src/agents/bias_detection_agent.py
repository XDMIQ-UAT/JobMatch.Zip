"""
Bias Detection Agent

CRITICAL agent for identifying potential biases in job descriptions and candidate profiles
to ensure unbiased job matching.
"""

from typing import Dict, Any, List, Optional
from src.agents.base_agent import BaseAgent
from src.models import LanguageModel


class BiasDetectionAgent(BaseAgent):
    """
    Analyzes job descriptions and candidate profiles for potential biases.
    
    Output format:
    {
        'potential_biases': List[Dict[str, str]],  # Each with 'type', 'description', 'location'
        'severity_level': str,  # 'low', 'medium', 'high'
        'mitigation_strategies': List[str],
        'reasoning': str
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
            name=name or "Bias Detection Agent",
            description="Fairness and bias detection specialist",
            capabilities=["bias_detection", "fairness_analysis", "mitigation"]
        )
        self.llm = llm
        self.system_prompt = """You are a fairness and bias detection specialist. Your role is to analyze 
job descriptions and candidate profiles for potential biases related to gender, race, ethnicity, age, 
disability, or other protected characteristics.

You will receive JSON output from the Job Description Analyzer and/or Candidate Profile Analyzer. 

Output should be a JSON object with the following keys:
- 'potential_biases': A list of identified biases, each with:
  - 'type': The type of bias (e.g., 'gender', 'age', 'disability', 'cultural')
  - 'description': A detailed description of the bias
  - 'location': Where in the text the bias was found
  - 'example': The specific text that indicates bias
- 'severity_level': Overall severity ('low', 'medium', 'high')
- 'mitigation_strategies': A list of actionable suggestions to reduce bias
- 'reasoning': Detailed explanation of your assessment

Be as specific as possible and provide reasoning for your assessments. Prioritize identifying subtle biases 
that may not be immediately obvious. Consider both explicit and implicit bias indicators."""
    
    # Common bias indicators (can be expanded)
    BIAS_INDICATORS = {
        "gender": ["he/she", "salesman", "waitress", "manpower", "guys"],
        "age": ["recent graduate", "young", "energetic", "mature", "seasoned"],
        "disability": ["able-bodied", "must be able to", "physical requirements"],
        "cultural": ["native speaker", "must speak English", "cultural fit"]
    }
    
    def perceive(self, environment: Dict[str, Any]) -> Dict[str, Any]:
        """Extract job description and/or candidate profile analysis from environment."""
        job_analysis = environment.get("job_analysis")
        candidate_analysis = environment.get("candidate_analysis")
        
        if not job_analysis and not candidate_analysis:
            raise ValueError("At least one analysis (job or candidate) is required")
        
        return {
            "job_analysis": job_analysis,
            "candidate_analysis": candidate_analysis,
            "timestamp": self.created_at.isoformat()
        }
    
    def decide(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """Decide on bias detection approach."""
        job_analysis = perception.get("job_analysis")
        candidate_analysis = perception.get("candidate_analysis")
        
        # Determine what to analyze
        analyze_job = job_analysis is not None
        analyze_candidate = candidate_analysis is not None
        
        # Extract text for analysis
        texts_to_analyze = []
        if analyze_job:
            job_text = " ".join([
                job_analysis.get("title", ""),
                " ".join(job_analysis.get("required_skills", [])),
                " ".join(job_analysis.get("responsibilities", [])),
                " ".join(job_analysis.get("keywords", []))
            ])
            texts_to_analyze.append(("job", job_text))
        
        if analyze_candidate:
            candidate_text = " ".join([
                candidate_analysis.get("summary", ""),
                " ".join(candidate_analysis.get("skills", [])),
                " ".join(candidate_analysis.get("keywords", []))
            ])
            texts_to_analyze.append(("candidate", candidate_text))
        
        return {
            "texts_to_analyze": texts_to_analyze,
            "analyze_job": analyze_job,
            "analyze_candidate": analyze_candidate
        }
    
    def act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Execute bias detection using LLM."""
        texts_to_analyze = decision["texts_to_analyze"]
        analyze_job = decision["analyze_job"]
        analyze_candidate = decision["analyze_candidate"]
        
        # Construct context for LLM
        context_parts = []
        if analyze_job:
            job_analysis = decision.get("job_analysis") or {}
            context_parts.append(f"Job Description Analysis:\n{self._format_analysis(job_analysis)}")
        
        if analyze_candidate:
            candidate_analysis = decision.get("candidate_analysis") or {}
            context_parts.append(f"Candidate Profile Analysis:\n{self._format_analysis(candidate_analysis)}")
        
        context = "\n\n".join(context_parts)
        
        # Construct the prompt
        user_prompt = f"""Analyze the following job description and/or candidate profile analysis for potential biases:

{context}

Provide your bias analysis as a JSON object with the keys: potential_biases, severity_level, 
mitigation_strategies, and reasoning."""
        
        # Call LLM
        response = self.llm.generate(
            prompt=user_prompt,
            system_prompt=self.system_prompt,
            temperature=0.2,  # Very low temperature for consistent bias detection
            response_format="json"
        )
        
        # Parse response
        try:
            import json
            bias_result = json.loads(response)
        except json.JSONDecodeError:
            # Fallback: try to extract JSON from markdown code blocks
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                bias_result = json.loads(json_match.group(1))
            else:
                raise ValueError(f"Failed to parse LLM response as JSON: {response}")
        
        # Validate structure
        if 'potential_biases' not in bias_result:
            bias_result['potential_biases'] = []
        if 'severity_level' not in bias_result:
            bias_result['severity_level'] = 'low'
        if 'mitigation_strategies' not in bias_result:
            bias_result['mitigation_strategies'] = []
        if 'reasoning' not in bias_result:
            bias_result['reasoning'] = ""
        
        # Ensure severity_level is valid
        if bias_result['severity_level'] not in ['low', 'medium', 'high']:
            bias_result['severity_level'] = 'low'
        
        # Update agent state
        self.update_state({
            "last_bias_analysis": bias_result,
            "bias_detection_count": self.state.get("bias_detection_count", 0) + 1,
            "high_severity_count": self.state.get("high_severity_count", 0) + 
                                  (1 if bias_result['severity_level'] == 'high' else 0)
        })
        
        return {
            "status": "success",
            "bias_analysis": bias_result,
            "agent_id": self.agent_id
        }
    
    def _format_analysis(self, analysis: Dict[str, Any]) -> str:
        """Format analysis dictionary for LLM context."""
        lines = []
        for key, value in analysis.items():
            if key == 'ambiguities':
                continue
            if isinstance(value, list):
                lines.append(f"{key}: {', '.join(str(v) for v in value)}")
            else:
                lines.append(f"{key}: {value}")
        return "\n".join(lines)

