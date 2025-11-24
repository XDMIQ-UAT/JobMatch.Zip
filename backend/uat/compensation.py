"""
Compensation & Payment System for UAT Platform

Handles:
- USD payment processing
- Bitcoin integration
- Escrow management
- Payment tracking with anonymity
- Tax documentation (optional, separate vault)
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
import hashlib


class PaymentMethod(Enum):
    """Supported payment methods"""
    USD_TRANSFER = "usd_transfer"    # Anonymous transfer services
    BITCOIN = "bitcoin"               # Cryptocurrency
    CRYPTO_GENERAL = "crypto_general" # Other cryptocurrencies


class PaymentStatus(Enum):
    """Payment status tracking"""
    PENDING = "pending"
    ESCROW = "escrow"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class TestCompletionStatus(Enum):
    """Test completion status"""
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"


class CompensationRecord:
    """Record of compensation for completed test"""
    
    def __init__(self,
                 session_id: str,
                 tester_id: str,
                 scenario_id: str,
                 amount_usd: float,
                 payment_method: PaymentMethod):
        self.session_id = session_id
        self.tester_id = tester_id
        self.scenario_id = scenario_id
        self.amount_usd = amount_usd
        self.payment_method = payment_method
        self.created_at = datetime.utcnow().isoformat()
        self.status = PaymentStatus.PENDING.value
        self.completion_status = TestCompletionStatus.IN_PROGRESS.value
        self.test_submission = None
        self.payment_details = {}
        self.completion_feedback = None
        
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Convert to dictionary (optionally excluding sensitive data)"""
        data = {
            "session_id": self.session_id,
            "scenario_id": self.scenario_id,
            "amount_usd": self.amount_usd,
            "payment_method": self.payment_method.value,
            "status": self.status,
            "completion_status": self.completion_status,
            "created_at": self.created_at
        }
        
        if include_sensitive:
            data.update({
                "tester_id": self.tester_id,
                "test_submission": self.test_submission,
                "payment_details": self.payment_details
            })
            
        return data


class CompensationManager:
    """
    Manage compensation for test completion
    
    Key principle: Separate compensation tracking from identity vault
    """
    
    def __init__(self):
        self._compensation_records: Dict[str, CompensationRecord] = {}
        self._escrow_accounts: Dict[str, Dict[str, Any]] = {}
        self._payment_ledger: List[Dict[str, Any]] = []
        
    def create_compensation_record(self,
                                   session_id: str,
                                   tester_id: str,
                                   scenario_id: str,
                                   amount_usd: float,
                                   payment_method: PaymentMethod) -> str:
        """
        Create new compensation record for test
        
        Args:
            session_id: Test session ID
            tester_id: Anonymous tester ID
            scenario_id: Test scenario ID
            amount_usd: Compensation amount
            payment_method: How to pay
            
        Returns:
            Compensation record ID
        """
        record_id = hashlib.sha256(
            f"{session_id}:{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:16]
        
        record = CompensationRecord(
            session_id=session_id,
            tester_id=tester_id,
            scenario_id=scenario_id,
            amount_usd=amount_usd,
            payment_method=payment_method
        )
        
        self._compensation_records[record_id] = record
        
        # Move to escrow
        self._escrow_accounts[record_id] = {
            "amount_usd": amount_usd,
            "escrowed_at": datetime.utcnow().isoformat(),
            "released": False
        }
        
        record.status = PaymentStatus.ESCROW.value
        
        return record_id
        
    def submit_test_completion(self,
                              record_id: str,
                              feedback: Dict[str, Any],
                              screenshots: Optional[List[str]] = None) -> bool:
        """
        Submit test completion with feedback
        
        Args:
            record_id: Compensation record ID
            feedback: Test feedback/results (should be pre-sanitized)
            screenshots: Optional sanitized screenshots
            
        Returns:
            True if submitted successfully
        """
        if record_id not in self._compensation_records:
            return False
            
        record = self._compensation_records[record_id]
        record.completion_status = TestCompletionStatus.SUBMITTED.value
        record.test_submission = {
            "submitted_at": datetime.utcnow().isoformat(),
            "feedback": feedback,
            "screenshots_count": len(screenshots) if screenshots else 0
        }
        
        return True
        
    def approve_test_completion(self,
                               record_id: str,
                               reviewer_id: str,
                               notes: str = "") -> bool:
        """
        Approve completed test and release escrow payment
        
        Args:
            record_id: Compensation record ID
            reviewer_id: Anonymous reviewer ID
            notes: Review notes
            
        Returns:
            True if approved successfully
        """
        if record_id not in self._compensation_records:
            return False
            
        record = self._compensation_records[record_id]
        record.completion_status = TestCompletionStatus.APPROVED.value
        
        # Release escrow
        if record_id in self._escrow_accounts:
            escrow = self._escrow_accounts[record_id]
            escrow["released"] = True
            escrow["released_at"] = datetime.utcnow().isoformat()
            escrow["released_by"] = reviewer_id
            
            # Move to payment ledger
            self._payment_ledger.append({
                "record_id": record_id,
                "session_id": record.session_id,
                "scenario_id": record.scenario_id,
                "amount_usd": record.amount_usd,
                "payment_method": record.payment_method.value,
                "status": PaymentStatus.COMPLETED.value,
                "approved_at": datetime.utcnow().isoformat(),
                "reviewer_notes": notes
            })
            
            record.status = PaymentStatus.COMPLETED.value
            
        return True
        
    def reject_test_completion(self,
                              record_id: str,
                              reviewer_id: str,
                              reason: str) -> bool:
        """
        Reject test completion and return escrow payment
        
        Args:
            record_id: Compensation record ID
            reviewer_id: Anonymous reviewer ID
            reason: Rejection reason
            
        Returns:
            True if rejected successfully
        """
        if record_id not in self._compensation_records:
            return False
            
        record = self._compensation_records[record_id]
        record.completion_status = TestCompletionStatus.REJECTED.value
        
        # Return escrow
        if record_id in self._escrow_accounts:
            escrow = self._escrow_accounts[record_id]
            escrow["returned"] = True
            escrow["returned_at"] = datetime.utcnow().isoformat()
            escrow["returned_by"] = reviewer_id
            escrow["reason"] = reason
            
            record.status = PaymentStatus.REFUNDED.value
            
        return True
        
    def process_payment(self,
                       record_id: str,
                       payment_address: str) -> bool:
        """
        Process actual payment to tester
        
        Args:
            record_id: Compensation record ID
            payment_address: Bitcoin wallet or payment service address
            
        Returns:
            True if payment initiated successfully
        """
        if record_id not in self._compensation_records:
            return False
            
        record = self._compensation_records[record_id]
        
        # Only process if test approved
        if record.status != PaymentStatus.COMPLETED.value:
            return False
            
        record.payment_details = {
            "payment_address": payment_address,  # Hashed in production
            "processed_at": datetime.utcnow().isoformat(),
            "method": record.payment_method.value
        }
        
        # Log payment (with anonymity preserved)
        self._payment_ledger.append({
            "record_id": record_id,
            "amount_usd": record.amount_usd,
            "payment_method": record.payment_method.value,
            "processed_at": datetime.utcnow().isoformat(),
            "tester_id_hash": hashlib.sha256(record.tester_id.encode()).hexdigest()[:8]
        })
        
        return True
        
    def get_tester_earnings(self, tester_id: str) -> Dict[str, Any]:
        """
        Get earnings summary for tester (anonymously)
        
        Args:
            tester_id: Anonymous tester ID
            
        Returns:
            Earnings summary
        """
        tester_records = [
            r for r in self._compensation_records.values()
            if r.tester_id == tester_id
        ]
        
        completed = [r for r in tester_records if r.status == PaymentStatus.COMPLETED.value]
        pending = [r for r in tester_records if r.status == PaymentStatus.ESCROW.value]
        
        return {
            "total_earned_usd": sum(r.amount_usd for r in completed),
            "pending_usd": sum(r.amount_usd for r in pending),
            "tests_completed": len([r for r in completed if r.completion_status == TestCompletionStatus.APPROVED.value]),
            "tests_in_progress": len([r for r in tester_records if r.completion_status == TestCompletionStatus.IN_PROGRESS.value]),
            "tests_submitted": len([r for r in tester_records if r.completion_status == TestCompletionStatus.SUBMITTED.value]),
            "history": [
                {
                    "scenario_id": r.scenario_id,
                    "amount_usd": r.amount_usd,
                    "status": r.status,
                    "completed_at": r.created_at
                }
                for r in sorted(tester_records, key=lambda x: x.created_at, reverse=True)
            ]
        }
        
    def get_platform_statistics(self) -> Dict[str, Any]:
        """Get platform-wide compensation statistics"""
        completed_payments = [
            r for r in self._compensation_records.values()
            if r.status == PaymentStatus.COMPLETED.value
        ]
        
        rejected = [
            r for r in self._compensation_records.values()
            if r.status == PaymentStatus.REFUNDED.value
        ]
        
        return {
            "total_tests_submitted": len([
                r for r in self._compensation_records.values()
                if r.completion_status in [
                    TestCompletionStatus.SUBMITTED.value,
                    TestCompletionStatus.APPROVED.value
                ]
            ]),
            "total_tests_approved": len([
                r for r in self._compensation_records.values()
                if r.completion_status == TestCompletionStatus.APPROVED.value
            ]),
            "total_tests_rejected": len(rejected),
            "total_paid_usd": sum(r.amount_usd for r in completed_payments),
            "total_in_escrow_usd": sum(
                r.amount_usd for r in self._compensation_records.values()
                if r.status == PaymentStatus.ESCROW.value
            ),
            "average_payment_usd": (
                sum(r.amount_usd for r in completed_payments) / len(completed_payments)
                if completed_payments else 0
            ),
            "payment_methods": {
                method: len([
                    r for r in completed_payments
                    if r.payment_method.value == method
                ])
                for method in [m.value for m in PaymentMethod]
            }
        }


class PaymentProcessor:
    """
    Process payments to testers via various methods
    
    Integrations needed:
    - USD transfer service (e.g., Wise, Stripe)
    - Bitcoin/crypto exchange
    """
    
    def __init__(self, usd_service_api_key: str, bitcoin_service_url: str):
        self.usd_service_api_key = usd_service_api_key
        self.bitcoin_service_url = bitcoin_service_url
        self._transaction_log: List[Dict[str, Any]] = []
        
    def process_usd_transfer(self,
                            amount_usd: float,
                            recipient_identifier: str) -> str:
        """
        Process USD transfer via anonymous service
        
        Args:
            amount_usd: Amount to transfer
            recipient_identifier: Anonymized recipient identifier
            
        Returns:
            Transaction ID
        """
        transaction_id = hashlib.sha256(
            f"{amount_usd}:{recipient_identifier}:{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:16]
        
        self._transaction_log.append({
            "transaction_id": transaction_id,
            "type": "usd_transfer",
            "amount_usd": amount_usd,
            "processed_at": datetime.utcnow().isoformat(),
            "recipient_hash": hashlib.sha256(recipient_identifier.encode()).hexdigest()[:8],
            "status": "initiated"
        })
        
        return transaction_id
        
    def process_bitcoin_transfer(self,
                                amount_usd: float,
                                btc_address: str,
                                current_btc_rate: float) -> str:
        """
        Process Bitcoin transfer
        
        Args:
            amount_usd: USD equivalent amount
            btc_address: Bitcoin wallet address (should be hashed)
            current_btc_rate: Current USD/BTC rate
            
        Returns:
            Transaction ID
        """
        btc_amount = amount_usd / current_btc_rate
        transaction_id = hashlib.sha256(
            f"{btc_amount}:{btc_address}:{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:16]
        
        self._transaction_log.append({
            "transaction_id": transaction_id,
            "type": "bitcoin_transfer",
            "amount_usd": amount_usd,
            "amount_btc": btc_amount,
            "processed_at": datetime.utcnow().isoformat(),
            "address_hash": hashlib.sha256(btc_address.encode()).hexdigest()[:8],
            "status": "initiated"
        })
        
        return transaction_id
        
    def get_transaction_status(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """Get status of payment transaction"""
        for tx in self._transaction_log:
            if tx["transaction_id"] == transaction_id:
                return tx.copy()
        return None
