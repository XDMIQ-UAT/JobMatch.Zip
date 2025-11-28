"""
UI Schema Implementation for Bias Detection Agent
"""

from typing import Dict, Any
from src.agents.bias_detection_agent import BiasDetectionAgent
from src.agents.ui_schema_mixin import UISchemaMixin
from src.schemas.ui_schema import UISchemaBuilder


class BiasDetectionAgentUI(BiasDetectionAgent, UISchemaMixin):
    """Bias Detection Agent with UI schema support."""
    
    def _build_ui_components(
        self,
        builder: UISchemaBuilder,
        state: Dict[str, Any]
    ) -> None:
        """Build UI components for bias detection."""
        last_bias_analysis = state.get("last_bias_analysis")
        bias_detection_count = state.get("bias_detection_count", 0)
        high_severity_count = state.get("high_severity_count", 0)
        
        # Header
        builder.addComponent({
            "id": "header",
            "type": "text",
            "props": {
                "content": "Bias Detection Agent",
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
                    "id": "detection-count",
                    "type": "text",
                    "props": {
                        "content": f"Analyses: {bias_detection_count}",
                        "fontSize": "14px"
                    }
                },
                {
                    "id": "high-severity",
                    "type": "text",
                    "props": {
                        "content": f"High Severity: {high_severity_count}",
                        "fontSize": "14px",
                        "color": "#d32f2f" if high_severity_count > 0 else "#666"
                    }
                }
            ]
        })
        
        # Last bias analysis
        if last_bias_analysis:
            severity = last_bias_analysis.get("severity_level", "low")
            potential_biases = last_bias_analysis.get("potential_biases", [])
            mitigation_strategies = last_bias_analysis.get("mitigation_strategies", [])
            
            # Severity badge
            severity_colors = {
                "high": "error",
                "medium": "warning",
                "low": "success"
            }
            
            builder.addComponent({
                "id": "severity",
                "type": "badge",
                "props": {
                    "label": f"Severity: {severity.upper()}",
                    "color": severity_colors.get(severity, "default")
                }
            })
            
            # Potential biases
            if potential_biases:
                bias_children = [
                    {
                        "id": f"bias-{idx}",
                        "type": "alert",
                        "props": {
                            "severity": "warning",
                            "message": f"[{bias.get('type', 'unknown').upper()}] {bias.get('description', '')[:100]}"
                        }
                    }
                    for idx, bias in enumerate(potential_biases[:5])
                ]
                builder.addComponent({
                    "id": "biases",
                    "type": "card",
                    "props": {
                        "title": f"Potential Biases ({len(potential_biases)})"
                    },
                    "children": bias_children
                })
            
            # Mitigation strategies
            if mitigation_strategies:
                builder.addComponent({
                    "id": "mitigations",
                    "type": "card",
                    "props": {
                        "title": "Mitigation Strategies"
                    },
                    "children": [
                        {
                            "id": "mitigations-list",
                            "type": "text",
                            "props": {
                                "content": "\n".join(f"• {s}" for s in mitigation_strategies[:5]),
                                "fontSize": "14px",
                                "color": "#2e7d32"
                            }
                        }
                    ]
                })
            
            # Reasoning
            reasoning = last_bias_analysis.get("reasoning", "")
            if reasoning:
                builder.addComponent({
                    "id": "reasoning",
                    "type": "card",
                    "props": {
                        "title": "Analysis Reasoning"
                    },
                    "children": [
                        {
                            "id": "reasoning-text",
                            "type": "text",
                            "props": {
                                "content": reasoning[:300] + "..." if len(reasoning) > 300 else reasoning,
                                "fontSize": "14px"
                            }
                        }
                    ]
                })
    
    def _build_ui_actions(self, builder: UISchemaBuilder) -> None:
        """Build UI actions."""
        builder.addAction({
            "id": "detect-bias",
            "label": "Detect Bias",
            "type": "button",
            "endpoint": f"/api/agents/{self.agent_id}/detect",
            "method": "POST"
        })

