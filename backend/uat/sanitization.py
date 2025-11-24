"""
Data Sanitization Engine for UAT Platform

Provides multi-layer PII protection:
- Pre-test: Scrub test data before display
- Real-time: Monitor for sensitive info sharing
- Post-test: Clean submitted feedback/screenshots
"""

import re
import hashlib
from typing import Dict, List, Any, Tuple
from datetime import datetime
from enum import Enum


class SanitizationLevel(Enum):
    """Levels of data sanitization"""
    NONE = 0
    BASIC = 1      # Remove obvious PII (emails, phones)
    MODERATE = 2   # Remove names, addresses, SSN
    HIGH = 3       # Remove all identifiable info
    PARANOID = 4   # Maximum scrubbing, even metadata


class PIIType(Enum):
    """Types of personally identifiable information"""
    EMAIL = "email"
    PHONE = "phone"
    SSN = "ssn"
    NAME = "name"
    ADDRESS = "address"
    CREDIT_CARD = "credit_card"
    IP_ADDRESS = "ip_address"
    BIOMETRIC = "biometric"
    MEDICAL = "medical"
    FINANCIAL = "financial"


class AnonymityScore:
    """Calculate and track anonymity score for test sessions"""
    
    def __init__(self):
        self.pii_detections: List[Dict[str, Any]] = []
        self.risk_events: List[Dict[str, Any]] = []
        
    def add_detection(self, pii_type: PIIType, confidence: float, context: str):
        """Record PII detection event"""
        self.pii_detections.append({
            "type": pii_type.value,
            "confidence": confidence,
            "context": context[:100],  # First 100 chars
            "timestamp": datetime.utcnow().isoformat()
        })
        
    def add_risk_event(self, event_type: str, severity: int, description: str):
        """Record anonymity risk event"""
        self.risk_events.append({
            "type": event_type,
            "severity": severity,
            "description": description,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    def calculate_score(self) -> float:
        """
        Calculate anonymity score (0-100)
        100 = perfectly anonymous
        0 = identity fully exposed
        """
        base_score = 100.0
        
        # Deduct for PII detections
        for detection in self.pii_detections:
            confidence = detection["confidence"]
            if detection["type"] in ["ssn", "credit_card", "biometric"]:
                base_score -= confidence * 20  # Critical PII
            elif detection["type"] in ["email", "phone", "name"]:
                base_score -= confidence * 10  # High-risk PII
            else:
                base_score -= confidence * 5   # Moderate PII
                
        # Deduct for risk events
        for event in self.risk_events:
            base_score -= event["severity"] * 3
            
        return max(0.0, min(100.0, base_score))
    
    def get_report(self) -> Dict[str, Any]:
        """Generate anonymity report"""
        return {
            "score": self.calculate_score(),
            "detections_count": len(self.pii_detections),
            "risk_events_count": len(self.risk_events),
            "detections": self.pii_detections,
            "risk_events": self.risk_events,
            "timestamp": datetime.utcnow().isoformat()
        }


class DataSanitizer:
    """Multi-layer PII scrubbing and anonymization"""
    
    # Regex patterns for PII detection
    PATTERNS = {
        PIIType.EMAIL: r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        PIIType.PHONE: r'\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b',
        PIIType.SSN: r'\b\d{3}-\d{2}-\d{4}\b',
        PIIType.CREDIT_CARD: r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
        PIIType.IP_ADDRESS: r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
    }
    
    def __init__(self, level: SanitizationLevel = SanitizationLevel.HIGH):
        self.level = level
        self.anonymity_score = AnonymityScore()
        self._replacement_cache = {}
        
    def _generate_replacement(self, pii_type: PIIType, original: str) -> str:
        """Generate consistent replacement for PII"""
        # Cache replacements for consistency
        cache_key = f"{pii_type.value}:{original}"
        if cache_key in self._replacement_cache:
            return self._replacement_cache[cache_key]
            
        # Generate anonymous replacement
        hash_val = hashlib.sha256(original.encode()).hexdigest()[:8]
        
        replacements = {
            PIIType.EMAIL: f"anon_{hash_val}@anonymous.test",
            PIIType.PHONE: f"555-{hash_val[:4]}-{hash_val[4:8]}",
            PIIType.SSN: f"XXX-XX-{hash_val[:4]}",
            PIIType.CREDIT_CARD: f"XXXX-XXXX-XXXX-{hash_val[:4]}",
            PIIType.IP_ADDRESS: f"10.0.{hash_val[:2]}.{hash_val[2:4]}",
        }
        
        replacement = replacements.get(pii_type, f"[REDACTED_{pii_type.value.upper()}]")
        self._replacement_cache[cache_key] = replacement
        return replacement
        
    def _detect_and_replace(self, text: str, pii_type: PIIType) -> Tuple[str, int]:
        """Detect and replace PII in text"""
        pattern = self.PATTERNS.get(pii_type)
        if not pattern:
            return text, 0
            
        matches = list(re.finditer(pattern, text))
        count = len(matches)
        
        # Record detections
        for match in matches:
            self.anonymity_score.add_detection(
                pii_type=pii_type,
                confidence=0.9,  # High confidence for regex matches
                context=text[max(0, match.start()-20):match.end()+20]
            )
        
        # Replace matches
        for match in reversed(matches):  # Reverse to maintain positions
            original = match.group(0)
            replacement = self._generate_replacement(pii_type, original)
            text = text[:match.start()] + replacement + text[match.end():]
            
        return text, count
        
    def sanitize_text(self, text: str) -> Dict[str, Any]:
        """
        Sanitize text content based on configured level
        
        Returns:
            {
                "sanitized": cleaned text,
                "detections": count by type,
                "anonymity_score": current score
            }
        """
        if self.level == SanitizationLevel.NONE:
            return {"sanitized": text, "detections": {}, "anonymity_score": 100.0}
            
        sanitized = text
        detections = {}
        
        # Apply sanitization based on level
        if self.level >= SanitizationLevel.BASIC:
            sanitized, count = self._detect_and_replace(sanitized, PIIType.EMAIL)
            if count > 0:
                detections[PIIType.EMAIL.value] = count
                
            sanitized, count = self._detect_and_replace(sanitized, PIIType.PHONE)
            if count > 0:
                detections[PIIType.PHONE.value] = count
                
        if self.level >= SanitizationLevel.MODERATE:
            sanitized, count = self._detect_and_replace(sanitized, PIIType.SSN)
            if count > 0:
                detections[PIIType.SSN.value] = count
                
            sanitized, count = self._detect_and_replace(sanitized, PIIType.CREDIT_CARD)
            if count > 0:
                detections[PIIType.CREDIT_CARD.value] = count
                
        if self.level >= SanitizationLevel.HIGH:
            sanitized, count = self._detect_and_replace(sanitized, PIIType.IP_ADDRESS)
            if count > 0:
                detections[PIIType.IP_ADDRESS.value] = count
                
        return {
            "sanitized": sanitized,
            "detections": detections,
            "anonymity_score": self.anonymity_score.calculate_score(),
            "original_length": len(text),
            "sanitized_length": len(sanitized)
        }
        
    def sanitize_dict(self, data: Dict[str, Any], 
                     exclude_keys: List[str] = None) -> Dict[str, Any]:
        """
        Recursively sanitize dictionary data
        
        Args:
            data: Dictionary to sanitize
            exclude_keys: Keys to skip sanitization
        """
        exclude_keys = exclude_keys or []
        sanitized = {}
        
        for key, value in data.items():
            if key in exclude_keys:
                sanitized[key] = value
            elif isinstance(value, str):
                result = self.sanitize_text(value)
                sanitized[key] = result["sanitized"]
            elif isinstance(value, dict):
                sanitized[key] = self.sanitize_dict(value, exclude_keys)
            elif isinstance(value, list):
                sanitized[key] = [
                    self.sanitize_dict(item, exclude_keys) if isinstance(item, dict)
                    else self.sanitize_text(item)["sanitized"] if isinstance(item, str)
                    else item
                    for item in value
                ]
            else:
                sanitized[key] = value
                
        return sanitized
        
    def pre_test_sanitize(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize test data before displaying to tester"""
        return self.sanitize_dict(test_data, exclude_keys=["test_id", "scenario_id"])
        
    def post_test_sanitize(self, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize tester feedback after submission"""
        return self.sanitize_dict(feedback_data, exclude_keys=["tester_id", "session_id"])
        
    def real_time_monitor(self, input_text: str, threshold: float = 70.0) -> Dict[str, Any]:
        """
        Real-time monitoring of user input for PII leakage
        
        Args:
            input_text: Text to monitor
            threshold: Anonymity score threshold for alerts
            
        Returns:
            {
                "safe": bool,
                "warnings": list of warnings,
                "sanitized": cleaned text if unsafe
            }
        """
        result = self.sanitize_text(input_text)
        score = result["anonymity_score"]
        
        warnings = []
        if result["detections"]:
            for pii_type, count in result["detections"].items():
                warnings.append(f"Detected {count} {pii_type}(s) in input")
                
        safe = score >= threshold and len(warnings) == 0
        
        return {
            "safe": safe,
            "warnings": warnings,
            "sanitized": result["sanitized"] if not safe else input_text,
            "anonymity_score": score,
            "detections": result["detections"]
        }
        
    def get_anonymity_report(self) -> Dict[str, Any]:
        """Get full anonymity report for session"""
        return self.anonymity_score.get_report()
