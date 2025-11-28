"""
Matching Agent

Skilled job matching expert that determines match quality between job descriptions
and candidate profiles, taking bias detection into account.
"""

from typing import Dict, Any, List, Optional
from src.agents.base_agent import BaseAgent
from src.models import LanguageModel, EmbeddingModel


class MatchingAgent(BaseAgent):
    """
    Determines match quality between job descriptions and candidate profiles.
    
    Output format:
    {
        'match_score': float,  # 0.0 to 1.0
        'reasoning': str,
        'recommendation': str,  # 'proceed', 'review', 'reject'
        'strengths': List[str],
        'gaps': List[str],
        'bias_considerations': str
    }
    """
    
    def __init__(
        self,
        llm: LanguageModel,
        embedding_model: Optional[EmbeddingModel] = None,
        agent_id: Optional[str] = None,
        name: Optional[str] = None
    ):
        super().__init__(
            agent_id=agent_id,
            name=name or "Matching Agent",
            description="Job matching expert with bias awareness",
            capabilities=["matching", "scoring", "recommendation"]
        )
        self.llm = llm
        self.embedding_model = embedding_model
        self.system_prompt = """You are a skilled job matching expert. You will receive JSON output from 
the Job Description Analyzer, Candidate Profile Analyzer, and Bias Detection Agent.

Your goal is to determine the degree of match between the job description and the candidate profile, 
taking into account the identified biases and mitigation strategies.

Output should be a JSON object with the following keys:
- 'match_score': A numerical score between 0 and 1 representing the match quality
- 'reasoning': A detailed explanation of the match score, including:
  - Factors considered (skills, experience, education, etc.)
  - How biases were addressed in the scoring
  - Weight given to different factors
- 'recommendation': One of 'proceed', 'review', or 'reject'
  - 'proceed': Strong match, proceed with candidate
  - 'review': Moderate match or bias concerns, requires human review
  - 'reject': Poor match or significant bias issues
- 'strengths': List of candidate strengths for this role
- 'gaps': List of gaps between candidate and job requirements
- 'bias_considerations': Explanation of how bias detection influenced the match score

Be fair and unbiased in your assessment. Consider both technical fit and potential for growth."""
    
    def perceive(self, environment: Dict[str, Any]) -> Dict[str, Any]:
        """Extract analyses from environment."""
        job_analysis = environment.get("job_analysis")
        candidate_analysis = environment.get("candidate_analysis")
        bias_analysis = environment.get("bias_analysis")
        
        if not job_analysis or not candidate_analysis:
            raise ValueError("Both job_analysis and candidate_analysis are required")
        
        return {
            "job_analysis": job_analysis,
            "candidate_analysis": candidate_analysis,
            "bias_analysis": bias_analysis,
            "timestamp": self.created_at.isoformat()
        }
    
    def decide(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """Decide on matching approach."""
        job_analysis = perception["job_analysis"]
        candidate_analysis = perception["candidate_analysis"]
        bias_analysis = perception.get("bias_analysis")
        
        # Calculate basic similarity metrics
        job_skills = set(job_analysis.get("required_skills", []))
        candidate_skills = set(candidate_analysis.get("skills", []))
        skill_overlap = len(job_skills & candidate_skills)
        skill_total = len(job_skills)
        
        # Experience level matching
        job_exp_level = job_analysis.get("experience_level", "").lower()
        candidate_exp_years = candidate_analysis.get("experience_years", 0)
        
        return {
            "job_analysis": job_analysis,
            "candidate_analysis": candidate_analysis,
            "bias_analysis": bias_analysis,
            "preliminary_metrics": {
                "skill_overlap": skill_overlap,
                "skill_total": skill_total,
                "skill_match_ratio": skill_overlap / skill_total if skill_total > 0 else 0,
                "candidate_exp_years": candidate_exp_years,
                "job_exp_level": job_exp_level
            }
        }
    
    def act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Execute matching using LLM and optionally embeddings."""
        job_analysis = decision["job_analysis"]
        candidate_analysis = decision["candidate_analysis"]
        bias_analysis = decision.get("bias_analysis")
        preliminary_metrics = decision["preliminary_metrics"]
        
        # Optionally calculate embedding similarity
        embedding_similarity = None
        if self.embedding_model:
            try:
                job_text = f"{job_analysis.get('title', '')} {' '.join(job_analysis.get('required_skills', []))}"
                candidate_text = f"{candidate_analysis.get('summary', '')} {' '.join(candidate_analysis.get('skills', []))}"
                
                job_embedding = self.embedding_model.embed(job_text)
                candidate_embedding = self.embedding_model.embed(candidate_text)
                
                # Calculate cosine similarity
                import numpy as np
                similarity = np.dot(job_embedding, candidate_embedding) / (
                    np.linalg.norm(job_embedding) * np.linalg.norm(candidate_embedding)
                )
                embedding_similarity = float(similarity)
            except Exception as e:
                # If embedding fails, continue without it
                pass
        
        # Construct context for LLM
        context_parts = [
            f"Job Description Analysis:\n{self._format_analysis(job_analysis)}",
            f"\nCandidate Profile Analysis:\n{self._format_analysis(candidate_analysis)}"
        ]
        
        if bias_analysis:
            context_parts.append(f"\nBias Analysis:\n{self._format_bias_analysis(bias_analysis)}")
        
        context_parts.append(f"\nPreliminary Metrics:\n{self._format_metrics(preliminary_metrics)}")
        
        if embedding_similarity is not None:
            context_parts.append(f"\nEmbedding Similarity Score: {embedding_similarity:.3f}")
        
        context = "\n".join(context_parts)
        
        # Construct the prompt
        user_prompt = f"""Analyze the match between the job description and candidate profile:

{context}

Provide your matching assessment as a JSON object with the keys: match_score, reasoning, 
recommendation, strengths, gaps, and bias_considerations."""
        
        # Call LLM
        response = self.llm.generate(
            prompt=user_prompt,
            system_prompt=self.system_prompt,
            temperature=0.3,
            response_format="json"
        )
        
        # Parse response
        try:
            import json
            match_result = json.loads(response)
        except json.JSONDecodeError:
            # Fallback: try to extract JSON from markdown code blocks
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                match_result = json.loads(json_match.group(1))
            else:
                raise ValueError(f"Failed to parse LLM response as JSON: {response}")
        
        # Validate and normalize match_score
        match_score = match_result.get("match_score", 0.0)
        if isinstance(match_score, str):
            try:
                match_score = float(match_score)
            except ValueError:
                match_score = 0.0
        match_score = max(0.0, min(1.0, float(match_score)))
        match_result["match_score"] = match_score
        
        # Validate recommendation
        recommendation = match_result.get("recommendation", "review").lower()
        if recommendation not in ["proceed", "review", "reject"]:
            recommendation = "review"
        match_result["recommendation"] = recommendation
        
        # Ensure lists exist
        for key in ["strengths", "gaps"]:
            if key not in match_result or not isinstance(match_result[key], list):
                match_result[key] = []
        
        # Add embedding similarity if available
        if embedding_similarity is not None:
            match_result["embedding_similarity"] = embedding_similarity
        
        # Update agent state
        self.update_state({
            "last_match": match_result,
            "match_count": self.state.get("match_count", 0) + 1,
            "average_match_score": (
                (self.state.get("average_match_score", 0.0) * 
                 (self.state.get("match_count", 0)) + match_score) / 
                (self.state.get("match_count", 0) + 1)
            )
        })
        
        return {
            "status": "success",
            "match_result": match_result,
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
    
    def _format_bias_analysis(self, bias_analysis: Dict[str, Any]) -> str:
        """Format bias analysis for LLM context."""
        lines = [
            f"Severity Level: {bias_analysis.get('severity_level', 'unknown')}",
            f"Potential Biases: {len(bias_analysis.get('potential_biases', []))}",
            f"Mitigation Strategies: {', '.join(bias_analysis.get('mitigation_strategies', []))}",
            f"Reasoning: {bias_analysis.get('reasoning', '')}"
        ]
        return "\n".join(lines)
    
    def _format_metrics(self, metrics: Dict[str, Any]) -> str:
        """Format preliminary metrics for LLM context."""
        lines = []
        for key, value in metrics.items():
            lines.append(f"{key}: {value}")
        return "\n".join(lines)

