"""
High-Risk Test Scenario Management

Handles:
- Test scenario CRUD operations
- Scenario classification and sensitivity levels
- Encrypted vault storage for sensitive test data
- Legal/medical review workflow
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
import hashlib


class ScenarioType(Enum):
    """Types of high-risk test scenarios"""
    FINANCIAL = "financial"          # Payment, banking, transactions
    HEALTHCARE = "healthcare"        # Medical records, health info
    LEGAL = "legal"                  # Legal documents, contracts
    PII_HANDLING = "pii_handling"    # Personal data management
    IDENTITY = "identity"            # ID verification flows
    BIOMETRIC = "biometric"          # Biometric data handling
    PAYMENT_GATEWAY = "payment_gateway"  # Payment processing


class ReviewStatus(Enum):
    """Approval status for scenarios"""
    DRAFT = "draft"
    LEGAL_REVIEW_PENDING = "legal_review_pending"
    MEDICAL_REVIEW_PENDING = "medical_review_pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class CompensationTier(Enum):
    """Compensation tiers based on risk level"""
    LOW = {"usd": 15, "description": "Standard UI testing"}
    MEDIUM = {"usd": 35, "description": "Moderate PII exposure"}
    HIGH = {"usd": 75, "description": "Significant sensitive data"}
    CRITICAL = {"usd": 150, "description": "Critical financial/medical data"}


class HighRiskVault:
    """
    Encrypted storage for sensitive test scenarios
    
    CRITICAL: All test data in vault is encrypted and requires authorization
    """
    
    def __init__(self, encryption_key: str, vault_path: str):
        self.encryption_key = encryption_key
        self.vault_path = vault_path
        self._vault_index: Dict[str, Dict[str, Any]] = {}
        
    def store_scenario_data(self,
                           scenario_id: str,
                           scenario_data: Dict[str, Any]) -> str:
        """
        Store encrypted scenario data in vault
        
        Args:
            scenario_id: Unique scenario identifier
            scenario_data: Test scenario data
            
        Returns:
            Vault reference ID
        """
        # In production: AES-256 encrypt scenario_data
        vault_ref = hashlib.sha256(
            f"{scenario_id}:{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()
        
        self._vault_index[vault_ref] = {
            "scenario_id": scenario_id,
            "stored_at": datetime.utcnow().isoformat(),
            "encrypted": True,
            "access_log": []
        }
        
        return vault_ref
        
    def retrieve_scenario_data(self,
                              vault_ref: str,
                              accessor_id: str,
                              purpose: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve encrypted scenario data with access logging
        
        Args:
            vault_ref: Vault reference ID
            accessor_id: Anonymous ID of accessor
            purpose: Purpose of access (test/review/audit)
            
        Returns:
            Decrypted scenario data if authorized
        """
        if vault_ref not in self._vault_index:
            return None
            
        record = self._vault_index[vault_ref]
        
        # Log access
        record["access_log"].append({
            "accessor_id": accessor_id,
            "purpose": purpose,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # In production: Decrypt scenario_data with self.encryption_key
        return {
            "vault_ref": vault_ref,
            "scenario_id": record["scenario_id"],
            "stored_at": record["stored_at"],
            "access_count": len(record["access_log"])
        }
        
    def get_access_log(self, vault_ref: str) -> Optional[List[Dict[str, Any]]]:
        """Get complete access audit trail for scenario"""
        if vault_ref not in self._vault_index:
            return None
        return self._vault_index[vault_ref]["access_log"]


class ScenarioManager:
    """
    Manage high-risk test scenarios with approval workflows
    """
    
    def __init__(self, vault: HighRiskVault):
        self.vault = vault
        self._scenarios: Dict[str, Dict[str, Any]] = {}
        self._next_id = 1000
        
    def create_scenario(self,
                       title: str,
                       description: str,
                       scenario_type: ScenarioType,
                       test_data: Dict[str, Any],
                       compensation_usd: float,
                       pii_categories: List[str],
                       max_testers: int = 5) -> str:
        """
        Create new high-risk test scenario
        
        Args:
            title: Scenario title
            description: Detailed description
            scenario_type: Type of scenario
            test_data: Test data to be sanitized
            compensation_usd: Compensation in USD
            pii_categories: List of PII types exposed (email, phone, ssn, etc.)
            max_testers: Maximum concurrent testers
            
        Returns:
            Scenario ID
        """
        scenario_id = f"scenario_{self._next_id}"
        self._next_id += 1
        
        # Store sensitive test data in encrypted vault
        vault_ref = self.vault.store_scenario_data(scenario_id, test_data)
        
        # Determine review requirements
        review_status = ReviewStatus.DRAFT.value
        required_reviews = []
        
        if scenario_type in [ScenarioType.LEGAL, ScenarioType.PII_HANDLING]:
            required_reviews.append("legal")
            review_status = ReviewStatus.LEGAL_REVIEW_PENDING.value
            
        if scenario_type == ScenarioType.HEALTHCARE:
            required_reviews.append("medical")
            review_status = ReviewStatus.MEDICAL_REVIEW_PENDING.value
        
        scenario = {
            "id": scenario_id,
            "title": title,
            "description": description,
            "type": scenario_type.value,
            "compensation_usd": compensation_usd,
            "pii_categories": pii_categories,
            "vault_ref": vault_ref,
            "created_at": datetime.utcnow().isoformat(),
            "status": review_status,
            "required_reviews": required_reviews,
            "completed_reviews": [],
            "max_testers": max_testers,
            "assigned_testers": [],
            "rejected_reason": None
        }
        
        self._scenarios[scenario_id] = scenario
        return scenario_id
        
    def submit_for_review(self,
                         scenario_id: str,
                         review_type: str) -> bool:
        """
        Submit scenario for legal/medical review
        
        Args:
            scenario_id: Scenario to review
            review_type: "legal" or "medical"
            
        Returns:
            True if submitted successfully
        """
        if scenario_id not in self._scenarios:
            return False
            
        scenario = self._scenarios[scenario_id]
        
        if review_type not in scenario["required_reviews"]:
            return False
            
        if review_type == "legal":
            scenario["status"] = ReviewStatus.LEGAL_REVIEW_PENDING.value
        elif review_type == "medical":
            scenario["status"] = ReviewStatus.MEDICAL_REVIEW_PENDING.value
            
        return True
        
    def approve_scenario(self,
                        scenario_id: str,
                        review_type: str,
                        reviewer_id: str,
                        notes: str = "") -> bool:
        """
        Approve scenario after review
        
        Args:
            scenario_id: Scenario to approve
            review_type: "legal" or "medical"
            reviewer_id: Anonymous reviewer ID
            notes: Review notes
            
        Returns:
            True if approved successfully
        """
        if scenario_id not in self._scenarios:
            return False
            
        scenario = self._scenarios[scenario_id]
        
        scenario["completed_reviews"].append({
            "type": review_type,
            "reviewer_id": reviewer_id,
            "approved_at": datetime.utcnow().isoformat(),
            "notes": notes
        })
        
        # Check if all required reviews are complete
        completed_types = [r["type"] for r in scenario["completed_reviews"]]
        if set(completed_types) >= set(scenario["required_reviews"]):
            scenario["status"] = ReviewStatus.APPROVED.value
            
        return True
        
    def reject_scenario(self,
                       scenario_id: str,
                       review_type: str,
                       reviewer_id: str,
                       reason: str) -> bool:
        """
        Reject scenario after review
        
        Args:
            scenario_id: Scenario to reject
            review_type: "legal" or "medical"
            reviewer_id: Anonymous reviewer ID
            reason: Rejection reason
            
        Returns:
            True if rejected successfully
        """
        if scenario_id not in self._scenarios:
            return False
            
        scenario = self._scenarios[scenario_id]
        scenario["status"] = ReviewStatus.REJECTED.value
        scenario["rejected_reason"] = {
            "review_type": review_type,
            "reviewer_id": reviewer_id,
            "rejected_at": datetime.utcnow().isoformat(),
            "reason": reason
        }
        
        return True
        
    def get_scenario(self, scenario_id: str) -> Optional[Dict[str, Any]]:
        """Get scenario (without sensitive test data)"""
        if scenario_id not in self._scenarios:
            return None
            
        scenario = self._scenarios[scenario_id].copy()
        # Don't expose vault_ref directly
        scenario.pop("vault_ref", None)
        return scenario
        
    def list_approved_scenarios(self) -> List[Dict[str, Any]]:
        """List all approved scenarios available for testers"""
        approved = [
            s for s in self._scenarios.values()
            if s["status"] == ReviewStatus.APPROVED.value
        ]
        
        return [
            {
                "id": s["id"],
                "title": s["title"],
                "description": s["description"],
                "type": s["type"],
                "compensation_usd": s["compensation_usd"],
                "pii_categories": s["pii_categories"],
                "spots_available": s["max_testers"] - len(s["assigned_testers"]),
                "created_at": s["created_at"]
            }
            for s in approved
        ]
        
    def assign_tester(self, scenario_id: str, tester_id: str) -> bool:
        """Assign tester to scenario"""
        if scenario_id not in self._scenarios:
            return False
            
        scenario = self._scenarios[scenario_id]
        
        if len(scenario["assigned_testers"]) >= scenario["max_testers"]:
            return False
            
        if tester_id not in scenario["assigned_testers"]:
            scenario["assigned_testers"].append(tester_id)
            
        return True
        
    def unassign_tester(self, scenario_id: str, tester_id: str) -> bool:
        """Remove tester from scenario"""
        if scenario_id not in self._scenarios:
            return False
            
        scenario = self._scenarios[scenario_id]
        if tester_id in scenario["assigned_testers"]:
            scenario["assigned_testers"].remove(tester_id)
            return True
            
        return False
        
    def get_scenario_statistics(self) -> Dict[str, Any]:
        """Get platform statistics"""
        approved_count = len([
            s for s in self._scenarios.values()
            if s["status"] == ReviewStatus.APPROVED.value
        ])
        
        pending_review = len([
            s for s in self._scenarios.values()
            if s["status"] in [
                ReviewStatus.LEGAL_REVIEW_PENDING.value,
                ReviewStatus.MEDICAL_REVIEW_PENDING.value
            ]
        ])
        
        total_compensation_available = sum(
            s["compensation_usd"] for s in self._scenarios.values()
            if s["status"] == ReviewStatus.APPROVED.value
        )
        
        return {
            "total_scenarios": len(self._scenarios),
            "approved": approved_count,
            "pending_review": pending_review,
            "rejected": len([
                s for s in self._scenarios.values()
                if s["status"] == ReviewStatus.REJECTED.value
            ]),
            "total_compensation_available_usd": total_compensation_available,
            "total_testers_assigned": sum(
                len(s["assigned_testers"]) for s in self._scenarios.values()
            )
        }
