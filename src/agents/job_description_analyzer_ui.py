"""
UI Schema Implementation for Job Description Analyzer Agent
"""

from typing import Dict, Any
from src.agents.job_description_analyzer import JobDescriptionAnalyzerAgent
from src.agents.ui_schema_mixin import UISchemaMixin
from src.schemas.ui_schema import UISchemaBuilder


class JobDescriptionAnalyzerAgentUI(JobDescriptionAnalyzerAgent, UISchemaMixin):
    """Job Description Analyzer Agent with UI schema support."""
    
    def _build_ui_components(
        self,
        builder: UISchemaBuilder,
        state: Dict[str, Any]
    ) -> None:
        """Build UI components for job description analysis."""
        last_analysis = state.get("last_analysis")
        analysis_count = state.get("analysis_count", 0)
        
        # Header
        builder.addComponent({
            "id": "header",
            "type": "text",
            "props": {
                "content": "Job Description Analyzer",
                "fontSize": "24px",
                "fontWeight": "bold"
            }
        })
        
        # Status badge
        status = "ready" if analysis_count == 0 else "analyzed"
        builder.addComponent({
            "id": "status-badge",
            "type": "badge",
            "props": {
                "label": status.upper(),
                "color": "success" if status == "analyzed" else "default"
            }
        })
        
        # Analysis count
        builder.addComponent({
            "id": "count",
            "type": "text",
            "props": {
                "content": f"Analyses performed: {analysis_count}",
                "fontSize": "14px",
                "color": "#666"
            }
        })
        
        # Show last analysis if available
        if last_analysis:
            # Title
            builder.addComponent({
                "id": "job-title",
                "type": "text",
                "props": {
                    "content": f"Title: {last_analysis.get('title', 'N/A')}",
                    "fontSize": "18px",
                    "fontWeight": "600"
                }
            })
            
            # Skills
            skills = last_analysis.get("required_skills", [])
            if skills:
                builder.addComponent({
                    "id": "skills",
                    "type": "card",
                    "props": {
                        "title": "Required Skills"
                    },
                    "children": [
                        {
                            "id": "skills-list",
                            "type": "text",
                            "props": {
                                "content": ", ".join(skills[:10]) + ("..." if len(skills) > 10 else ""),
                                "fontSize": "14px"
                            }
                        }
                    ]
                })
            
            # Experience level
            exp_level = last_analysis.get("experience_level", "N/A")
            builder.addComponent({
                "id": "experience",
                "type": "badge",
                "props": {
                    "label": f"Level: {exp_level}",
                    "color": "primary"
                }
            })
            
            # Ambiguities alert
            ambiguities = last_analysis.get("ambiguities", [])
            if ambiguities:
                builder.addComponent({
                    "id": "ambiguities",
                    "type": "alert",
                    "props": {
                        "severity": "warning",
                        "message": f"Found {len(ambiguities)} ambiguous aspects"
                    }
                })
    
    def _build_ui_actions(self, builder: UISchemaBuilder) -> None:
        """Build UI actions."""
        builder.addAction({
            "id": "analyze",
            "label": "Analyze Job Description",
            "type": "button",
            "endpoint": f"/api/agents/{self.agent_id}/analyze",
            "method": "POST"
        })

