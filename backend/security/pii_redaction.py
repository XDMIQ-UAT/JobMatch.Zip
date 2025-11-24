"""
PII Redaction Utilities for Safe Logging.
Provides functions to redact or hash PII before logging.
"""
import re
import hashlib
from typing import Optional


def redact_email(email: str) -> str:
    """
    Redact email address for safe logging.
    
    Examples:
        user@example.com -> u***@e***.com
        john.doe@company.org -> j***@c***.org
    
    Args:
        email: Email address to redact
        
    Returns:
        Redacted email address
    """
    if not email or '@' not in email:
        return "***@***.***"
    
    try:
        local, domain = email.split('@', 1)
        domain_parts = domain.split('.', 1)
        
        # Show first character of local and domain
        local_redacted = f"{local[0]}***" if local else "***"
        domain_redacted = f"{domain_parts[0][0]}***" if domain_parts else "***"
        domain_ext = domain_parts[1] if len(domain_parts) > 1 else "com"
        
        return f"{local_redacted}@{domain_redacted}.{domain_ext}"
    except (IndexError, AttributeError):
        return "***@***.***"


def redact_phone(phone: str) -> str:
    """
    Redact phone number for safe logging.
    
    Examples:
        +1-555-123-4567 -> ***-***-4567
        (555) 123-4567 -> ***-***-4567
        5551234567 -> ***-***-4567
    
    Args:
        phone: Phone number to redact
        
    Returns:
        Redacted phone number showing only last 4 digits
    """
    if not phone:
        return "***-***-****"
    
    # Extract only digits
    digits = re.sub(r'\D', '', phone)
    
    if len(digits) >= 4:
        return f"***-***-{digits[-4:]}"
    elif len(digits) > 0:
        return f"***-***-{digits}"
    else:
        return "***-***-****"


def hash_pii(pii: str, prefix: str = "") -> str:
    """
    Hash PII for logging (one-way hash, cannot be reversed).
    
    Useful when you need to correlate log entries without exposing actual PII.
    
    Examples:
        hash_pii("user@example.com") -> "a1b2c3d4e5f6g7h8"
        hash_pii("+1-555-123-4567", "phone") -> "phone_i9j0k1l2m3n4o5p6"
    
    Args:
        pii: PII value to hash
        prefix: Optional prefix to add to hash (e.g., "email", "phone")
        
    Returns:
        SHA256 hash (first 16 chars) with optional prefix
    """
    if not pii:
        return f"{prefix}_" + "0" * 16 if prefix else "0" * 16
    
    # SHA256 hash for cryptographic security
    hash_hex = hashlib.sha256(pii.encode('utf-8')).hexdigest()[:16]
    
    return f"{prefix}_{hash_hex}" if prefix else hash_hex


def redact_anonymous_id(anonymous_id: str, show_chars: int = 8) -> str:
    """
    Partially redact anonymous ID for logging.
    
    Shows first N characters to help debugging while maintaining privacy.
    
    Examples:
        redact_anonymous_id("anon_abc123xyz789def456") -> "anon_abc***"
        redact_anonymous_id("user_12345678901234567890", 12) -> "user_1234567***"
    
    Args:
        anonymous_id: Anonymous user ID to redact
        show_chars: Number of characters to show (default: 8)
        
    Returns:
        Partially redacted anonymous ID
    """
    if not anonymous_id:
        return "***"
    
    if len(anonymous_id) <= show_chars:
        return anonymous_id
    
    return f"{anonymous_id[:show_chars]}***"


def redact_token(token: str, show_chars: int = 6) -> str:
    """
    Redact authentication token for logging.
    
    Shows first few characters to help identify token in logs.
    
    Examples:
        redact_token("abc123xyz789def456ghi") -> "abc123***"
        redact_token("short") -> "short"
    
    Args:
        token: Token to redact
        show_chars: Number of characters to show (default: 6)
        
    Returns:
        Partially redacted token
    """
    if not token:
        return "***"
    
    if len(token) <= show_chars:
        return token
    
    return f"{token[:show_chars]}***"


def redact_ip_address(ip: str) -> str:
    """
    Redact IP address for logging.
    
    Shows first 2 octets for IPv4, first 2 groups for IPv6.
    
    Examples:
        IPv4: 192.168.1.100 -> 192.168.*.*
        IPv6: 2001:0db8:85a3:0000:0000:8a2e:0370:7334 -> 2001:0db8:*:*:*:*:*:*
    
    Args:
        ip: IP address to redact
        
    Returns:
        Partially redacted IP address
    """
    if not ip:
        return "*.*.*.*"
    
    # IPv4
    if '.' in ip and ':' not in ip:
        parts = ip.split('.')
        if len(parts) == 4:
            return f"{parts[0]}.{parts[1]}.*.*"
        return "*.*.*.*"
    
    # IPv6
    elif ':' in ip:
        parts = ip.split(':')
        if len(parts) >= 2:
            return f"{parts[0]}:{parts[1]}:*:*:*:*:*:*"
        return "*:*:*:*:*:*:*:*"
    
    return "*.*.*.*"


def safe_log_dict(data: dict, redact_keys: Optional[list] = None) -> dict:
    """
    Create a safe copy of dictionary for logging by redacting sensitive keys.
    
    Default redacted keys: email, phone, password, token, secret, api_key, ip
    
    Examples:
        safe_log_dict({"email": "user@example.com", "name": "John"})
        -> {"email": "u***@e***.com", "name": "John"}
    
    Args:
        data: Dictionary to redact
        redact_keys: List of keys to redact (optional, uses defaults if None)
        
    Returns:
        Dictionary with redacted values
    """
    if redact_keys is None:
        redact_keys = [
            'email', 'phone', 'password', 'token', 'secret', 'api_key', 
            'access_token', 'refresh_token', 'ip', 'ip_address', 'ssn',
            'credit_card', 'card_number', 'cvv', 'phone_number'
        ]
    
    safe_data = {}
    for key, value in data.items():
        key_lower = key.lower()
        
        # Check if key should be redacted
        should_redact = any(redact_key in key_lower for redact_key in redact_keys)
        
        if should_redact:
            if 'email' in key_lower:
                safe_data[key] = redact_email(str(value))
            elif 'phone' in key_lower:
                safe_data[key] = redact_phone(str(value))
            elif 'ip' in key_lower:
                safe_data[key] = redact_ip_address(str(value))
            elif 'token' in key_lower:
                safe_data[key] = redact_token(str(value))
            else:
                safe_data[key] = "***REDACTED***"
        else:
            safe_data[key] = value
    
    return safe_data


# Convenience exports for common use cases
__all__ = [
    'redact_email',
    'redact_phone',
    'hash_pii',
    'redact_anonymous_id',
    'redact_token',
    'redact_ip_address',
    'safe_log_dict',
]
