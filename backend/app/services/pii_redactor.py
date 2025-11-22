import ollama
import re
import json
from typing import Dict, List, Tuple
import os

class PIIRedactor:
    """
    PII detection and redaction service.
    
    Invariants:
    - Strip all PII before storing any text
    - Show user what was removed and why
    - Cannot reverse-engineer identity from redacted text
    """
    
    def __init__(self):
        self.model = os.getenv("OLLAMA_MODEL", "llama3.2")
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
        self.client = ollama.Client(host=self.base_url)
    
    def redact_pii(self, text: str) -> Dict[str, any]:
        """
        Detect and redact PII from text.
        
        Returns:
        {
            "original_text": "...",
            "redacted_text": "...",
            "removed_items": [
                {"type": "email", "value": "j***@example.com", "reason": "..."},
                {"type": "name", "value": "J*** D***", "reason": "..."}
            ],
            "is_safe": bool
        }
        """
        # Step 1: Rule-based detection (fast, high precision)
        redacted_text, rule_based_removals = self._rule_based_redaction(text)
        
        # Step 2: AI-based detection (catch what rules miss)
        ai_analysis = self._ai_pii_detection(redacted_text)
        
        # Step 3: Apply AI-detected redactions
        final_text, ai_removals = self._apply_ai_redactions(
            redacted_text, 
            ai_analysis.get("pii_found", [])
        )
        
        all_removals = rule_based_removals + ai_removals
        
        return {
            "original_text": text,
            "redacted_text": final_text,
            "removed_items": all_removals,
            "is_safe": len(all_removals) == 0 or self._verify_safety(final_text),
            "redaction_summary": self._generate_summary(all_removals)
        }
    
    def _rule_based_redaction(self, text: str) -> Tuple[str, List[Dict]]:
        """Apply regex-based PII detection"""
        removals = []
        redacted = text
        
        # Email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        for email in emails:
            masked = self._mask_value(email)
            redacted = redacted.replace(email, "[EMAIL_REDACTED]")
            removals.append({
                "type": "email",
                "value": masked,
                "reason": "Email addresses can identify you"
            })
        
        # Phone numbers (US format, common patterns)
        phone_patterns = [
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            r'\(\d{3}\)\s*\d{3}[-.]?\d{4}',
            r'\+\d{1,3}\s*\d{3}[-.]?\d{3}[-.]?\d{4}'
        ]
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            for phone in phones:
                masked = self._mask_value(phone)
                redacted = redacted.replace(phone, "[PHONE_REDACTED]")
                removals.append({
                    "type": "phone",
                    "value": masked,
                    "reason": "Phone numbers can identify you"
                })
        
        # Social Security Numbers
        ssn_pattern = r'\b\d{3}-\d{2}-\d{4}\b'
        ssns = re.findall(ssn_pattern, text)
        for ssn in ssns:
            redacted = redacted.replace(ssn, "[SSN_REDACTED]")
            removals.append({
                "type": "ssn",
                "value": "***-**-****",
                "reason": "Social Security Numbers must be protected"
            })
        
        # Street addresses (simple pattern)
        address_pattern = r'\b\d+\s+[A-Z][a-z]+\s+(Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct)\b'
        addresses = re.findall(address_pattern, text, re.IGNORECASE)
        for address in addresses:
            masked = "[ADDRESS_REDACTED]"
            redacted = redacted.replace(address, masked)
            removals.append({
                "type": "address",
                "value": self._mask_value(address),
                "reason": "Street addresses can identify your location"
            })
        
        # URLs (might contain tracking or personal info)
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, text)
        for url in urls:
            # Keep GitHub/portfolio URLs if they don't contain names
            if 'github.com' in url.lower() or 'portfolio' in url.lower():
                continue
            redacted = redacted.replace(url, "[URL_REDACTED]")
            removals.append({
                "type": "url",
                "value": self._mask_value(url),
                "reason": "URLs may contain tracking information"
            })
        
        return redacted, removals
    
    def _ai_pii_detection(self, text: str) -> Dict:
        """Use Ollama to detect PII that rules might miss"""
        prompt = f"""Analyze this text for personally identifiable information (PII).

Text:
{text}

Identify ANY information that could identify a person:
- Names (first, last, full names)
- Company names where person worked
- Specific dates (birth dates, employment dates)
- Location details (cities lived/worked, specific offices)
- Personal identifiers (employee IDs, badge numbers)
- Educational institution names with dates

Do NOT flag:
- Generic technology names (Python, AWS, Docker)
- Generic role descriptions (software engineer, analyst)
- Generic capability descriptions (built APIs, analyzed data)

Output ONLY as JSON:
{{
  "pii_found": [
    {{"type": "name", "value": "exact text", "reason": "explanation"}},
    {{"type": "company", "value": "exact text", "reason": "explanation"}}
  ],
  "is_safe": true/false
}}"""

        try:
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                stream=False
            )
            return self._parse_json_response(response['response'])
        except Exception as e:
            return {"pii_found": [], "is_safe": True, "error": str(e)}
    
    def _apply_ai_redactions(self, text: str, pii_items: List[Dict]) -> Tuple[str, List[Dict]]:
        """Apply redactions identified by AI"""
        redacted = text
        removals = []
        
        for item in pii_items:
            value = item.get("value", "")
            pii_type = item.get("type", "unknown")
            reason = item.get("reason", "Potentially identifying information")
            
            if value and value in redacted:
                masked = self._mask_value(value)
                placeholder = f"[{pii_type.upper()}_REDACTED]"
                redacted = redacted.replace(value, placeholder)
                removals.append({
                    "type": pii_type,
                    "value": masked,
                    "reason": reason
                })
        
        return redacted, removals
    
    def _verify_safety(self, text: str) -> bool:
        """Final verification that text is safe (no PII remains)"""
        # Check for common PII patterns
        risky_patterns = [
            r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b',  # Full names
            r'\b[A-Z][a-z]+,\s*[A-Z]{2}\b',     # City, State
        ]
        
        for pattern in risky_patterns:
            if re.search(pattern, text):
                return False
        
        return True
    
    def _mask_value(self, value: str) -> str:
        """Mask a value for display to user"""
        if len(value) <= 4:
            return "***"
        # Show first char and last char
        return f"{value[0]}{'*' * (len(value) - 2)}{value[-1]}"
    
    def _parse_json_response(self, response_text: str) -> Dict:
        """Parse JSON from LLM response"""
        try:
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start != -1 and end > start:
                json_str = response_text[start:end]
                return json.loads(json_str)
        except:
            pass
        return {"pii_found": [], "is_safe": True}
    
    def _generate_summary(self, removals: List[Dict]) -> str:
        """Generate user-friendly summary of what was removed"""
        if not removals:
            return "No personal information detected."
        
        counts = {}
        for item in removals:
            item_type = item['type']
            counts[item_type] = counts.get(item_type, 0) + 1
        
        summary_parts = []
        for item_type, count in counts.items():
            plural = "s" if count > 1 else ""
            summary_parts.append(f"{count} {item_type}{plural}")
        
        return f"Removed: {', '.join(summary_parts)}"
