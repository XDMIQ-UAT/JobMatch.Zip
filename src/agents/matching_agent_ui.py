"""
UI Schema Implementation for Matching Agent
"""

from typing import Dict, Any
from src.agents.matching_agent import MatchingAgent
from src.agents.ui_schema_mixin import UISchemaMixin
from src.schemas.ui_schema import UISchemaBuilder


class MatchingAgentUI(MatchingAgent, UISchemaMixin):
    """Matching Agent with UI schema support."""
    
    def _build_ui_components(
        self,
        builder: UISchemaBuilder,
        state: Dict[str, Any]
    ) -> None:
        """Build UI components for matching results."""
        last_match = state.get("last_match")
        match_count = state.get("match_count", 0)
        avg_score = state.get("average_match_score", 0.0)
        
        # Header
        builder.addComponent({
            "id": "header",
            "type": "text",
            "props": {
                "content": "Job Matching Agent",
                "fontSize": "24px",
                "fontWeight": "bold"
            }
        })
        
        # Stats
        builder.addComponent({
            "id": "stats",
            "type": "card",
            "children": [
                {
                    "id": "match-count",
                    "type": "text",
                    "props": {
                        "content": f"Total Matches: {match_count}",
                        "fontSize": "14px"
                    }
                },
                {
                    "id": "avg-score",
                    "type": "text",
                    "props": {
                        "content": f"Average Score: {avg_score:.1%}",
                        "fontSize": "14px"
                    }
                }
            ]
        })
        
        # Last match result
        if last_match:
            match_score = last_match.get("match_score", 0.0)
            recommendation = last_match.get("recommendation", "review")
            
            # Match score with progress bar
            builder.addComponent({
                "id": "match-score",
                "type": "card",
                "children": [
                    {
                        "id": "score-label",
                        "type": "text",
                        "props": {
                            "content": "Match Score",
                            "fontSize": "16px",
                            "fontWeight": "600"
                        }
                    },
                    {
                        "id": "score-progress",
                        "type": "progress",
                        "bind": "last_match.match_score",
                        "props": {
                            "value": int(match_score * 100),
                            "max": 100,
                            "label": f"{match_score:.1%}",
                            "showPercentage": True,
                            "color": "success" if match_score >= 0.7 else "warning" if match_score >= 0.5 else "error"
                        }
                    }
                ]
            })
            
            # Recommendation badge
            rec_color = {
                "proceed": "success",
                "review": "warning",
                "reject": "error"
            }.get(recommendation, "default")
            
            builder.addComponent({
                "id": "recommendation",
                "type": "badge",
                "props": {
                    "label": recommendation.upper(),
                    "color": rec_color
                }
            })
            
            # Strengths
            strengths = last_match.get("strengths", [])
            if strengths:
                builder.addComponent({
                    "id": "strengths",
                    "type": "card",
                    "props": {
                        "title": "Strengths"
                    },
                    "children": [
                        {
                            "id": "strengths-list",
                            "type": "text",
                            "props": {
                                "content": "\n".join(f"• {s}" for s in strengths[:5]),
                                "fontSize": "14px"
                            }
                        }
                    ]
                })
            
            # Gaps
            gaps = last_match.get("gaps", [])
            if gaps:
                builder.addComponent({
                    "id": "gaps",
                    "type": "card",
                    "props": {
                        "title": "Gaps"
                    },
                    "children": [
                        {
                            "id": "gaps-list",
                            "type": "text",
                            "props": {
                                "content": "\n".join(f"• {g}" for g in gaps[:5]),
                                "fontSize": "14px",
                                "color": "#d32f2f"
                            }
                        }
                    ]
                })
            
            # Bias considerations
            bias_considerations = last_match.get("bias_considerations", "")
            if bias_considerations:
                builder.addComponent({
                    "id": "bias-info",
                    "type": "alert",
                    "props": {
                        "severity": "info",
                        "message": bias_considerations[:200] + "..." if len(bias_considerations) > 200 else bias_considerations
                    }
                })
    
    def _build_ui_actions(self, builder: UISchemaBuilder) -> None:
        """Build UI actions."""
        builder.addAction({
            "id": "match",
            "label": "Run Matching",
            "type": "button",
            "endpoint": f"/api/agents/{self.agent_id}/match",
            "method": "POST"
        })

