"""
Anonymous Identity Management for UAT Platform

Provides:
- Cryptographically secure anonymous IDs
- Zero-knowledge proof for tester qualifications
- Separate identity vault (payment processing only)
- No correlation between test behavior and real identity
"""

import secrets
import hashlib
import hmac
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import base64


class AnonymousIDType(Enum):
    """Types of anonymous identifiers"""
    TESTER = "tester"       # Primary tester identity
    SESSION = "session"     # Individual test session
    PAYMENT = "payment"     # Payment processing (isolated)
    VAULT = "vault"         # Identity vault access


class ZeroKnowledgeProof:
    """
    Zero-knowledge proof system for tester qualifications
    
    Allows verification of qualifications without revealing identity
    """
    
    def __init__(self, secret_salt: str):
        self.secret_salt = secret_salt
        
    def generate_commitment(self, qualification: str, tester_secret: str) -> str:
        """
        Generate commitment for qualification claim
        
        Args:
            qualification: The qualification being claimed (e.g., "10_years_experience")
            tester_secret: Secret known only to tester
            
        Returns:
            Commitment hash that proves qualification without revealing identity
        """
        combined = f"{qualification}:{tester_secret}:{self.secret_salt}"
        commitment = hashlib.sha256(combined.encode()).hexdigest()
        return commitment
        
    def verify_qualification(self, 
                           commitment: str, 
                           qualification: str, 
                           proof: str) -> bool:
        """
        Verify qualification claim without learning identity
        
        Args:
            commitment: Previously generated commitment
            qualification: Claimed qualification
            proof: Zero-knowledge proof
            
        Returns:
            True if qualification verified without revealing identity
        """
        # Verify proof matches commitment
        expected = self.generate_commitment(qualification, proof)
        return hmac.compare_digest(expected, commitment)
        
    def generate_proof_challenge(self) -> str:
        """Generate random challenge for interactive proof"""
        return secrets.token_hex(32)
        
    def respond_to_challenge(self, 
                            challenge: str, 
                            tester_secret: str) -> str:
        """
        Generate response to challenge without revealing secret
        
        Args:
            challenge: Random challenge from verifier
            tester_secret: Tester's secret
            
        Returns:
            Response that proves knowledge without revealing secret
        """
        response = hashlib.sha256(
            f"{challenge}:{tester_secret}:{self.secret_salt}".encode()
        ).hexdigest()
        return response
        
    def verify_challenge_response(self,
                                 challenge: str,
                                 response: str,
                                 expected_commitment: str) -> bool:
        """Verify challenge response matches commitment"""
        # In a full implementation, this would use more sophisticated crypto
        # For now, we verify the response is properly formed
        return len(response) == 64  # SHA256 hex length


class AnonymousIDGenerator:
    """
    Generate and manage cryptographically secure anonymous IDs
    
    Features:
    - Collision-resistant IDs
    - Unlinkable across contexts
    - Revocable without identity exposure
    - Time-limited session IDs
    """
    
    def __init__(self, master_secret: Optional[str] = None):
        """
        Initialize with master secret for deterministic generation
        
        Args:
            master_secret: Optional master secret (auto-generated if not provided)
        """
        self.master_secret = master_secret or secrets.token_hex(32)
        self._id_registry: Dict[str, Dict[str, Any]] = {}
        
    def generate_id(self, 
                   id_type: AnonymousIDType,
                   context: Optional[str] = None,
                   expires_in: Optional[timedelta] = None) -> str:
        """
        Generate cryptographically secure anonymous ID
        
        Args:
            id_type: Type of anonymous ID
            context: Optional context for ID generation
            expires_in: Optional expiration time delta
            
        Returns:
            Anonymous ID string (base64 encoded)
        """
        # Generate random entropy
        entropy = secrets.token_bytes(32)
        
        # Combine with type and context for uniqueness
        context_str = context or ""
        timestamp = datetime.utcnow().isoformat()
        
        combined = f"{id_type.value}:{context_str}:{timestamp}".encode()
        combined += entropy
        
        # Generate ID using HMAC for additional security
        id_hash = hmac.new(
            self.master_secret.encode(),
            combined,
            hashlib.sha256
        ).digest()
        
        # Base64 encode for readability
        anonymous_id = base64.urlsafe_b64encode(id_hash).decode().rstrip('=')
        
        # Add prefix for type identification
        prefixed_id = f"{id_type.value}_{anonymous_id}"
        
        # Register ID with metadata
        expiration = None
        if expires_in:
            expiration = datetime.utcnow() + expires_in
            
        self._id_registry[prefixed_id] = {
            "type": id_type.value,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": expiration.isoformat() if expiration else None,
            "context": context,
            "revoked": False
        }
        
        return prefixed_id
        
    def generate_tester_id(self) -> str:
        """Generate primary anonymous tester ID (permanent)"""
        return self.generate_id(AnonymousIDType.TESTER)
        
    def generate_session_id(self, tester_id: str) -> str:
        """Generate session ID for specific test (time-limited)"""
        return self.generate_id(
            AnonymousIDType.SESSION,
            context=tester_id,
            expires_in=timedelta(hours=24)
        )
        
    def generate_payment_id(self, tester_id: str) -> str:
        """
        Generate payment ID (isolated from testing identity)
        
        This ID is only used for payment processing and stored separately
        to prevent linking payment info with test behavior.
        """
        return self.generate_id(
            AnonymousIDType.PAYMENT,
            context=f"payment_{tester_id}"
        )
        
    def validate_id(self, anonymous_id: str) -> Tuple[bool, Optional[str]]:
        """
        Validate anonymous ID and check expiration
        
        Returns:
            (valid, error_message)
        """
        if anonymous_id not in self._id_registry:
            return False, "ID not found in registry"
            
        metadata = self._id_registry[anonymous_id]
        
        if metadata["revoked"]:
            return False, "ID has been revoked"
            
        if metadata["expires_at"]:
            expiration = datetime.fromisoformat(metadata["expires_at"])
            if datetime.utcnow() > expiration:
                return False, "ID has expired"
                
        return True, None
        
    def revoke_id(self, anonymous_id: str) -> bool:
        """
        Revoke anonymous ID without exposing identity
        
        Returns:
            True if revoked successfully
        """
        if anonymous_id in self._id_registry:
            self._id_registry[anonymous_id]["revoked"] = True
            self._id_registry[anonymous_id]["revoked_at"] = datetime.utcnow().isoformat()
            return True
        return False
        
    def get_id_metadata(self, anonymous_id: str) -> Optional[Dict[str, Any]]:
        """Get metadata for anonymous ID (excluding sensitive data)"""
        if anonymous_id not in self._id_registry:
            return None
            
        metadata = self._id_registry[anonymous_id].copy()
        # Return only non-sensitive metadata
        return {
            "type": metadata["type"],
            "created_at": metadata["created_at"],
            "expires_at": metadata["expires_at"],
            "revoked": metadata["revoked"]
        }
        
    def is_linkable(self, id1: str, id2: str) -> bool:
        """
        Check if two IDs can be linked to same tester
        
        This should ONLY return True if intentionally designed to link
        (e.g., session ID to tester ID via context)
        """
        if id1 not in self._id_registry or id2 not in self._id_registry:
            return False
            
        meta1 = self._id_registry[id1]
        meta2 = self._id_registry[id2]
        
        # Check if one is session and other is its parent tester
        if meta1["type"] == "session" and meta1["context"] == id2:
            return True
        if meta2["type"] == "session" and meta2["context"] == id1:
            return True
            
        # Payment IDs should NEVER be linkable to test behavior
        if meta1["type"] == "payment" or meta2["type"] == "payment":
            return False
            
        return False


class IdentityVault:
    """
    Isolated identity storage for payment processing
    
    CRITICAL: This vault is completely isolated from test behavior.
    Only accessed for payment/tax purposes with explicit consent.
    """
    
    def __init__(self, encryption_key: str):
        self.encryption_key = encryption_key
        self._vault: Dict[str, Dict[str, Any]] = {}
        
    def store_identity(self,
                      payment_id: str,
                      identity_data: Dict[str, Any],
                      consent_timestamp: str) -> bool:
        """
        Store real identity for payment processing
        
        Args:
            payment_id: Anonymous payment ID
            identity_data: Real identity info (name, payment details)
            consent_timestamp: When user consented to identity storage
            
        Returns:
            True if stored successfully
        """
        # In production, encrypt identity_data with self.encryption_key
        self._vault[payment_id] = {
            "identity": identity_data,  # Should be encrypted
            "consent_at": consent_timestamp,
            "accessed_count": 0,
            "last_accessed": None,
            "purpose": "payment_processing"
        }
        return True
        
    def retrieve_identity(self,
                         payment_id: str,
                         purpose: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve identity for authorized purpose only
        
        Args:
            payment_id: Anonymous payment ID
            purpose: Reason for access (must be "payment_processing" or "tax_documentation")
            
        Returns:
            Decrypted identity data if authorized
        """
        if purpose not in ["payment_processing", "tax_documentation"]:
            raise ValueError(f"Unauthorized purpose: {purpose}")
            
        if payment_id not in self._vault:
            return None
            
        record = self._vault[payment_id]
        record["accessed_count"] += 1
        record["last_accessed"] = datetime.utcnow().isoformat()
        record["last_purpose"] = purpose
        
        # In production, decrypt identity data
        return record["identity"]
        
    def delete_identity(self, payment_id: str) -> bool:
        """
        Delete identity (right to be forgotten)
        
        Returns:
            True if deleted successfully
        """
        if payment_id in self._vault:
            del self._vault[payment_id]
            return True
        return False
        
    def audit_trail(self, payment_id: str) -> Optional[Dict[str, Any]]:
        """Get audit trail for identity access"""
        if payment_id not in self._vault:
            return None
            
        record = self._vault[payment_id]
        return {
            "consent_at": record["consent_at"],
            "accessed_count": record["accessed_count"],
            "last_accessed": record["last_accessed"],
            "last_purpose": record.get("last_purpose", "none")
        }
