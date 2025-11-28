"""
Agents Module

This module defines agent behaviors and types. Agents are autonomous entities
that can perceive their environment, make decisions, and take actions to achieve goals.

Key Concepts:
- Agent Types: Different agent archetypes (e.g., task-oriented, conversational, tool-using)
- Agent Behaviors: Decision-making logic and action selection
- Agent Communication: Inter-agent messaging and coordination
"""

from typing import Protocol, Any, Dict, List, Optional

class Agent(Protocol):
    """Base protocol for all agents."""
    
    def perceive(self, environment: Dict[str, Any]) -> Dict[str, Any]:
        """Perceive the current environment state."""
        ...
    
    def decide(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """Make a decision based on perception."""
        ...
    
    def act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an action based on decision."""
        ...

# Export all agents
from src.agents.base_agent import BaseAgent
from src.agents.job_description_analyzer import JobDescriptionAnalyzerAgent
from src.agents.candidate_profile_analyzer import CandidateProfileAnalyzerAgent
from src.agents.bias_detection_agent import BiasDetectionAgent
from src.agents.matching_agent import MatchingAgent
from src.agents.data_ingestion_agent import DataIngestionAgent

__all__ = [
    "Agent",
    "BaseAgent",
    "JobDescriptionAnalyzerAgent",
    "CandidateProfileAnalyzerAgent",
    "BiasDetectionAgent",
    "MatchingAgent",
    "DataIngestionAgent",
]

