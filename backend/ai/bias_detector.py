"""
Bias Detection System.
Human-in-the-Loop: AI detects, humans review flagged content.
"""
import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from openai import OpenAI
from backend.config import settings

logger = logging.getLogger(__name__)


class BiasDetector:
    """Detects bias in content."""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
    
    def detect_bias(
        self,
        content: str,
        content_type: str = "job_posting"
    ) -> Dict[str, Any]:
        """
        Detect bias in content.
        Human-in-the-Loop: AI detects, humans review.
        """
        bias_result = self._analyze_bias(content, content_type)
        
        return {
            "bias_detected": bias_result.get("bias_detected", False),
            "bias_types": bias_result.get("bias_types", []),
            "details": bias_result.get("details", {}),
            "needs_human_review": bias_result.get("bias_detected", False)
        }
    
    def _analyze_bias(
        self,
        content: str,
        content_type: str
    ) -> Dict[str, Any]:
        """Use AI to analyze bias."""
        if not self.openai_client:
            return self._fallback_bias_analysis(content)
        
        try:
            prompt = f"""
            Analyze this {content_type} for bias:
            1. Credentialism (requiring degrees over capabilities)
            2. Classist assumptions
            3. Bias against LLC/independent contractors
            4. Ableist language
            5. Racial bias
            6. Gender discrimination
            
            Content: {content}
            
            Return JSON with bias_detected (boolean), bias_types (list), and details (object).
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You detect bias in job postings and content."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            # Parse response (simplified)
            return {
                "bias_detected": "bias" in response.choices[0].message.content.lower(),
                "bias_types": [],
                "details": {}
            }
        except Exception as e:
            logger.error(f"Bias detection failed: {e}")
            return self._fallback_bias_analysis(content)
    
    def _fallback_bias_analysis(self, content: str) -> Dict[str, Any]:
        """Fallback bias analysis."""
        credentialism_keywords = ["degree required", "phd", "masters required"]
        credentialism = any(kw in content.lower() for kw in credentialism_keywords)
        
        return {
            "bias_detected": credentialism,
            "bias_types": ["credentialism"] if credentialism else [],
            "details": {
                "credentialism": credentialism
            }
        }


def create_bias_detector(db_session: Session) -> BiasDetector:
    """Factory function to create bias detector."""
    return BiasDetector(db_session)


