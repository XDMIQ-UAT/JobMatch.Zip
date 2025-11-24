"""
PII Scanner for User-Generated Content.
Detects personally identifiable information in text to prevent accidental disclosure.
"""
import re
from typing import Dict, List, Optional
from dataclasses import dataclass


# PII Detection Patterns
PII_PATTERNS = {
    'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    'phone_us': r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b',
    'phone_international': r'\+\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}',
    'ssn': r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b',
    'credit_card': r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',
    'ip_address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
    'url': r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)',
    'street_address': r'\b\d+\s+[A-Za-z0-9\s,]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Circle|Cir|Way)\b',
    'zip_code': r'\b\d{5}(?:-\d{4})?\b',
}


@dataclass
class PIIMatch:
    """Represents a detected PII match."""
    pii_type: str
    value: str
    start: int
    end: int
    context: str  # Surrounding text for context


@dataclass
class PIIScanResult:
    """Result of PII scanning."""
    has_pii: bool
    total_matches: int
    matches_by_type: Dict[str, int]
    detailed_matches: List[PIIMatch]
    risk_level: str  # "none", "low", "medium", "high", "critical"


class PIIScanner:
    """Scanner for detecting PII in text."""
    
    def __init__(self, patterns: Optional[Dict[str, str]] = None):
        """
        Initialize PII scanner.
        
        Args:
            patterns: Custom PII patterns (uses defaults if None)
        """
        self.patterns = patterns or PII_PATTERNS
        self.compiled_patterns = {
            pii_type: re.compile(pattern, re.IGNORECASE)
            for pii_type, pattern in self.patterns.items()
        }
    
    def scan(
        self,
        text: str,
        include_details: bool = False,
        context_chars: int = 20
    ) -> PIIScanResult:
        """
        Scan text for PII.
        
        Args:
            text: Text to scan
            include_details: Whether to include detailed match info
            context_chars: Number of chars to show before/after match
            
        Returns:
            PIIScanResult with findings
        """
        if not text:
            return PIIScanResult(
                has_pii=False,
                total_matches=0,
                matches_by_type={},
                detailed_matches=[],
                risk_level="none"
            )
        
        matches_by_type: Dict[str, int] = {}
        detailed_matches: List[PIIMatch] = []
        
        for pii_type, pattern in self.compiled_patterns.items():
            matches = pattern.finditer(text)
            count = 0
            
            for match in matches:
                count += 1
                
                if include_details:
                    # Extract context around match
                    start = max(0, match.start() - context_chars)
                    end = min(len(text), match.end() + context_chars)
                    context = text[start:end]
                    
                    detailed_matches.append(PIIMatch(
                        pii_type=pii_type,
                        value=match.group(),
                        start=match.start(),
                        end=match.end(),
                        context=context
                    ))
            
            if count > 0:
                matches_by_type[pii_type] = count
        
        total_matches = sum(matches_by_type.values())
        has_pii = total_matches > 0
        risk_level = self._calculate_risk_level(matches_by_type)
        
        return PIIScanResult(
            has_pii=has_pii,
            total_matches=total_matches,
            matches_by_type=matches_by_type,
            detailed_matches=detailed_matches,
            risk_level=risk_level
        )
    
    def _calculate_risk_level(self, matches_by_type: Dict[str, int]) -> str:
        """
        Calculate risk level based on PII types found.
        
        Risk levels:
        - none: No PII detected
        - low: URLs only (not strictly PII)
        - medium: Email addresses, phone numbers
        - high: Street addresses, zip codes
        - critical: SSN, credit cards, multiple high-risk PII types
        
        Args:
            matches_by_type: Dictionary of PII type counts
            
        Returns:
            Risk level string
        """
        if not matches_by_type:
            return "none"
        
        # Critical PII types
        critical_types = {'ssn', 'credit_card'}
        has_critical = any(pii_type in matches_by_type for pii_type in critical_types)
        
        if has_critical:
            return "critical"
        
        # High-risk PII types
        high_risk_types = {'street_address', 'zip_code'}
        has_high_risk = any(pii_type in matches_by_type for pii_type in high_risk_types)
        
        # Medium-risk PII types
        medium_risk_types = {'email', 'phone_us', 'phone_international', 'ip_address'}
        has_medium_risk = any(pii_type in matches_by_type for pii_type in medium_risk_types)
        
        # Multiple PII types increase risk
        num_types = len(matches_by_type)
        
        if has_high_risk or (has_medium_risk and num_types >= 3):
            return "high"
        elif has_medium_risk:
            return "medium"
        else:
            return "low"
    
    def redact_pii(self, text: str, placeholder: str = "[REDACTED]") -> str:
        """
        Redact all detected PII from text.
        
        Args:
            text: Text to redact
            placeholder: Placeholder text for redacted content
            
        Returns:
            Text with PII redacted
        """
        if not text:
            return text
        
        redacted = text
        offset = 0
        
        # Sort all matches by position
        all_matches = []
        for pii_type, pattern in self.compiled_patterns.items():
            for match in pattern.finditer(text):
                all_matches.append((match.start(), match.end(), pii_type))
        
        # Sort by start position
        all_matches.sort(key=lambda x: x[0])
        
        # Replace matches (working backwards to maintain positions)
        for start, end, pii_type in reversed(all_matches):
            redacted = redacted[:start] + f"{placeholder}_{pii_type.upper()}" + redacted[end:]
        
        return redacted
    
    def is_safe_for_public(self, text: str, allowed_types: Optional[List[str]] = None) -> bool:
        """
        Check if text is safe for public display.
        
        Args:
            text: Text to check
            allowed_types: PII types that are allowed (e.g., ["url"])
            
        Returns:
            True if safe for public display, False otherwise
        """
        if not text:
            return True
        
        allowed_types = allowed_types or ['url']
        result = self.scan(text)
        
        # Check if any non-allowed PII types were found
        for pii_type in result.matches_by_type.keys():
            if pii_type not in allowed_types:
                return False
        
        return True


# Convenience function for quick scanning
def scan_for_pii(text: str) -> Dict[str, int]:
    """
    Quick scan for PII in text.
    
    Args:
        text: Text to scan
        
    Returns:
        Dictionary of PII type counts
    """
    scanner = PIIScanner()
    result = scanner.scan(text)
    return result.matches_by_type


def has_sensitive_pii(text: str) -> bool:
    """
    Check if text contains sensitive PII (SSN, credit cards).
    
    Args:
        text: Text to check
        
    Returns:
        True if sensitive PII detected, False otherwise
    """
    scanner = PIIScanner()
    result = scanner.scan(text)
    return result.risk_level in ["high", "critical"]


# Export main classes and functions
__all__ = [
    'PIIScanner',
    'PIIScanResult',
    'PIIMatch',
    'scan_for_pii',
    'has_sensitive_pii',
]
