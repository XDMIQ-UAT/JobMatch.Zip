"""
Job Matching Workflow

Orchestrates the entire job matching process from ingestion to final recommendation.
"""

from typing import Dict, Any, Optional, List
from src.workflows.base_workflow import BaseWorkflow
from src.agents.base_agent import BaseAgent
from src.utils.exceptions import WorkflowError


class JobMatchingWorkflow(BaseWorkflow):
    """
    Orchestrates the job matching process:
    1. Data Ingestion (job description and candidate profile)
    2. Job Description Analysis
    3. Candidate Profile Analysis
    4. Bias Detection
    5. Matching
    6. Final Recommendation
    """
    
    def __init__(
        self,
        data_ingestion_agent: BaseAgent,
        job_analyzer: BaseAgent,
        candidate_analyzer: BaseAgent,
        bias_detection_agent: BaseAgent,
        matching_agent: BaseAgent,
        workflow_id: Optional[str] = None,
        name: Optional[str] = None
    ):
        super().__init__(
            workflow_id=workflow_id,
            name=name or "Job Matching Workflow",
            description="Orchestrates the complete job matching process with bias detection"
        )
        self.data_ingestion_agent = data_ingestion_agent
        self.job_analyzer = job_analyzer
        self.candidate_analyzer = candidate_analyzer
        self.bias_detection_agent = bias_detection_agent
        self.matching_agent = matching_agent
        
        # Define workflow steps
        self.steps = [
            {"name": "ingest_job", "agent": "data_ingestion_agent", "type": "job_description"},
            {"name": "ingest_candidate", "agent": "data_ingestion_agent", "type": "candidate_profile"},
            {"name": "analyze_job", "agent": "job_analyzer"},
            {"name": "analyze_candidate", "agent": "candidate_analyzer"},
            {"name": "detect_bias", "agent": "bias_detection_agent"},
            {"name": "match", "agent": "matching_agent"},
            {"name": "finalize", "agent": None}  # Final step handled by workflow
        ]
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the complete job matching workflow.
        
        Expected context:
        - job_source: URL or file path for job description
        - candidate_source: URL or file path for candidate profile
        - job_content: (optional) Direct job description text
        - candidate_content: (optional) Direct candidate profile text
        
        Returns:
            Complete workflow result with all analyses and final recommendation
        """
        workflow_results = {
            "workflow_id": self.workflow_id,
            "status": "in_progress",
            "errors": [],
            "steps": {}
        }
        
        try:
            # Step 1: Ingest job description
            job_source = context.get("job_source")
            job_content = context.get("job_content")
            
            if not job_source and not job_content:
                raise WorkflowError("Either job_source or job_content must be provided")
            
            job_ingestion_result = self.data_ingestion_agent.run({
                "source": job_source,
                "content": job_content,
                "content_type": "job_description"
            })
            
            if job_ingestion_result.get("status") != "success":
                raise WorkflowError(f"Job ingestion failed: {job_ingestion_result.get('errors', [])}")
            
            workflow_results["steps"]["job_ingestion"] = job_ingestion_result
            job_analysis = job_ingestion_result.get("analysis")
            
            # Step 2: Ingest candidate profile
            candidate_source = context.get("candidate_source")
            candidate_content = context.get("candidate_content")
            
            if not candidate_source and not candidate_content:
                raise WorkflowError("Either candidate_source or candidate_content must be provided")
            
            candidate_ingestion_result = self.data_ingestion_agent.run({
                "source": candidate_source,
                "content": candidate_content,
                "content_type": "candidate_profile"
            })
            
            if candidate_ingestion_result.get("status") != "success":
                raise WorkflowError(f"Candidate ingestion failed: {candidate_ingestion_result.get('errors', [])}")
            
            workflow_results["steps"]["candidate_ingestion"] = candidate_ingestion_result
            candidate_analysis = candidate_ingestion_result.get("analysis")
            
            # Step 3: Analyze job description (if not already done)
            if not job_analysis:
                job_analysis_result = self.job_analyzer.run({
                    "job_description": job_content or job_ingestion_result.get("raw_content", ""),
                    "source": job_source
                })
                job_analysis = job_analysis_result.get("analysis")
                workflow_results["steps"]["job_analysis"] = job_analysis_result
            
            # Step 4: Analyze candidate profile (if not already done)
            if not candidate_analysis:
                candidate_analysis_result = self.candidate_analyzer.run({
                    "candidate_profile": candidate_content or candidate_ingestion_result.get("raw_content", ""),
                    "source": candidate_source
                })
                candidate_analysis = candidate_analysis_result.get("analysis")
                workflow_results["steps"]["candidate_analysis"] = candidate_analysis_result
            
            # Step 5: Detect bias
            bias_detection_result = self.bias_detection_agent.run({
                "job_analysis": job_analysis,
                "candidate_analysis": candidate_analysis
            })
            
            if bias_detection_result.get("status") != "success":
                workflow_results["errors"].append(f"Bias detection warning: {bias_detection_result.get('errors', [])}")
            
            workflow_results["steps"]["bias_detection"] = bias_detection_result
            bias_analysis = bias_detection_result.get("bias_analysis")
            
            # Step 6: Match
            matching_result = self.matching_agent.run({
                "job_analysis": job_analysis,
                "candidate_analysis": candidate_analysis,
                "bias_analysis": bias_analysis
            })
            
            if matching_result.get("status") != "success":
                raise WorkflowError(f"Matching failed: {matching_result.get('errors', [])}")
            
            workflow_results["steps"]["matching"] = matching_result
            match_result = matching_result.get("match_result")
            
            # Step 7: Finalize
            workflow_results["status"] = "completed"
            workflow_results["final_recommendation"] = {
                "match_score": match_result.get("match_score", 0.0),
                "recommendation": match_result.get("recommendation", "review"),
                "reasoning": match_result.get("reasoning", ""),
                "strengths": match_result.get("strengths", []),
                "gaps": match_result.get("gaps", []),
                "bias_considerations": match_result.get("bias_considerations", ""),
                "bias_severity": bias_analysis.get("severity_level", "low") if bias_analysis else "low"
            }
            
            # Add summary
            workflow_results["summary"] = self._generate_summary(workflow_results)
            
        except Exception as e:
            workflow_results["status"] = "error"
            workflow_results["errors"].append(str(e))
            workflow_results["error_message"] = str(e)
        
        return workflow_results
    
    def _generate_summary(self, results: Dict[str, Any]) -> str:
        """Generate a human-readable summary of the workflow results."""
        final_rec = results.get("final_recommendation", {})
        match_score = final_rec.get("match_score", 0.0)
        recommendation = final_rec.get("recommendation", "review")
        bias_severity = final_rec.get("bias_severity", "low")
        
        summary_parts = [
            f"Match Score: {match_score:.2%}",
            f"Recommendation: {recommendation.upper()}",
            f"Bias Severity: {bias_severity.upper()}"
        ]
        
        if final_rec.get("strengths"):
            summary_parts.append(f"Strengths: {len(final_rec['strengths'])} identified")
        
        if final_rec.get("gaps"):
            summary_parts.append(f"Gaps: {len(final_rec['gaps'])} identified")
        
        return " | ".join(summary_parts)

