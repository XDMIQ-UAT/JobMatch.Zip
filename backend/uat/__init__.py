"""
UAT Testing Platform Module

Provides anonymous, secure testing environment for high-risk UI scenarios
with personal data sanitization and compensation tracking.
"""

from .sanitization import DataSanitizer, AnonymityScore
from .anonymity import AnonymousIDGenerator, ZeroKnowledgeProof
from .scenarios import ScenarioManager, HighRiskVault
from .compensation import CompensationManager, PaymentProcessor

__all__ = [
    "DataSanitizer",
    "AnonymityScore",
    "AnonymousIDGenerator",
    "ZeroKnowledgeProof",
    "ScenarioManager",
    "HighRiskVault",
    "CompensationManager",
    "PaymentProcessor",
]
