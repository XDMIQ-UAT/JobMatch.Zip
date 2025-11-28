"""
Zero-Knowledge Authentication API for JobMatch
Server NEVER sees unencrypted personal data or master passphrase
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List
import secrets
import hashlib
from datetime import datetime, timedelta
import json

router = APIRouter(prefix="/api/zk-auth", tags=["zero-knowledge-auth"])

# In-memory storage for MVP (use PostgreSQL in production)
USERS_DB = {}  # {email: {auth_hash, encrypted_profile, created_at}}
CAPABILITIES_DB = {}  # {user_id: capabilities}
SESSIONS_DB = {}  # {session_token: {user_id, email, expires_at}}


# Request/Response Models
class RegisterRequest(BaseModel):
    email: EmailStr
    auth_hash: str  # Derived from passphrase (PBKDF2)
    encrypted_profile: str  # Client-side encrypted blob
    capabilities: Dict[str, Any]  # Public data for matching


class LoginRequest(BaseModel):
    email: EmailStr
    auth_hash: str


class RegisterResponse(BaseModel):
    user_id: str
    session_token: str
    message: str


class LoginResponse(BaseModel):
    session_token: str
    encrypted_profile: str
    user_id: str


class VerifySessionResponse(BaseModel):
    valid: bool
    user_id: Optional[str] = None
    email: Optional[str] = None


class ProfileUpdateRequest(BaseModel):
    encrypted_profile: str
    capabilities: Dict[str, Any]


# Helper Functions
def generate_user_id() -> str:
    """Generate random user ID"""
    return f"usr_{secrets.token_hex(8)}"


def generate_session_token() -> str:
    """Generate random session token"""
    return f"tok_{secrets.token_hex(32)}"


def get_session_from_token(session_token: str) -> Optional[Dict]:
    """Get session data from token"""
    session = SESSIONS_DB.get(session_token)
    if not session:
        return None
    
    # Check if expired
    if datetime.utcnow() > session['expires_at']:
        del SESSIONS_DB[session_token]
        return None
    
    return session


async def verify_session_token(authorization: Optional[str] = Header(None)) -> Dict:
    """Dependency to verify session token"""
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    session_token = authorization.replace('Bearer ', '')
    session = get_session_from_token(session_token)
    
    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    return session


# Endpoints
@router.post("/register", response_model=RegisterResponse)
async def register(request: RegisterRequest):
    """
    Register new user with zero-knowledge architecture
    Server receives:
    - email (identifier only)
    - auth_hash (for login verification, not decryption)
    - encrypted_profile (unreadable blob)
    - capabilities (public data for matching, no PII)
    
    Server NEVER receives:
    - Master passphrase
    - Encryption key
    - Unencrypted personal data
    """
    
    # Check if email already exists
    if request.email in USERS_DB:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Validate capabilities contain no PII
    if _contains_potential_pii(request.capabilities):
        raise HTTPException(
            status_code=400, 
            detail="Capabilities should not contain personal information"
        )
    
    # Generate user ID
    user_id = generate_user_id()
    
    # Store user data (zero-knowledge)
    USERS_DB[request.email] = {
        'user_id': user_id,
        'auth_hash': request.auth_hash,
        'encrypted_profile': request.encrypted_profile,  # Server can't decrypt
        'created_at': datetime.utcnow().isoformat()
    }
    
    # Store capabilities separately (public, for matching)
    CAPABILITIES_DB[user_id] = {
        **request.capabilities,
        'user_id': user_id,
        'email': request.email  # Only for notification purposes
    }
    
    # Create session
    session_token = generate_session_token()
    SESSIONS_DB[session_token] = {
        'user_id': user_id,
        'email': request.email,
        'expires_at': datetime.utcnow() + timedelta(days=30)
    }
    
    return RegisterResponse(
        user_id=user_id,
        session_token=session_token,
        message="Registration successful. Your data is encrypted and only you can decrypt it."
    )


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Login with zero-knowledge authentication
    Server verifies auth_hash matches stored hash
    Returns encrypted profile that only client can decrypt
    """
    
    # Check if user exists
    user_data = USERS_DB.get(request.email)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Verify auth hash (constant-time comparison)
    if not secrets.compare_digest(user_data['auth_hash'], request.auth_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create new session
    session_token = generate_session_token()
    SESSIONS_DB[session_token] = {
        'user_id': user_data['user_id'],
        'email': request.email,
        'expires_at': datetime.utcnow() + timedelta(days=30)
    }
    
    return LoginResponse(
        session_token=session_token,
        encrypted_profile=user_data['encrypted_profile'],
        user_id=user_data['user_id']
    )


@router.get("/verify-session", response_model=VerifySessionResponse)
async def verify_session(session: Dict = Depends(verify_session_token)):
    """Verify if session token is still valid"""
    return VerifySessionResponse(
        valid=True,
        user_id=session['user_id'],
        email=session['email']
    )


@router.post("/update-profile")
async def update_profile(
    request: ProfileUpdateRequest,
    session: Dict = Depends(verify_session_token)
):
    """
    Update encrypted profile and capabilities
    Client sends new encrypted blob + updated capabilities
    """
    
    email = session['email']
    user_id = session['user_id']
    
    # Validate capabilities contain no PII
    if _contains_potential_pii(request.capabilities):
        raise HTTPException(
            status_code=400,
            detail="Capabilities should not contain personal information"
        )
    
    # Update encrypted profile
    USERS_DB[email]['encrypted_profile'] = request.encrypted_profile
    
    # Update capabilities
    CAPABILITIES_DB[user_id] = {
        **request.capabilities,
        'user_id': user_id,
        'email': email
    }
    
    return {
        "message": "Profile updated successfully",
        "encrypted": True
    }


@router.post("/logout")
async def logout(session: Dict = Depends(verify_session_token)):
    """Logout and invalidate session"""
    
    # Find and delete session token
    for token, sess in list(SESSIONS_DB.items()):
        if sess['user_id'] == session['user_id']:
            del SESSIONS_DB[token]
    
    return {"message": "Logged out successfully"}


@router.get("/profile")
async def get_profile(session: Dict = Depends(verify_session_token)):
    """
    Get user's encrypted profile
    Returns encrypted blob that only client can decrypt
    """
    
    email = session['email']
    user_data = USERS_DB.get(email)
    
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user_id": user_data['user_id'],
        "encrypted_profile": user_data['encrypted_profile'],
        "capabilities": CAPABILITIES_DB.get(user_data['user_id'], {})
    }


@router.delete("/account")
async def delete_account(session: Dict = Depends(verify_session_token)):
    """
    Delete user account and all associated data
    GDPR right to deletion
    """
    
    email = session['email']
    user_id = session['user_id']
    
    # Delete user data
    if email in USERS_DB:
        del USERS_DB[email]
    
    # Delete capabilities
    if user_id in CAPABILITIES_DB:
        del CAPABILITIES_DB[user_id]
    
    # Delete all sessions
    for token, sess in list(SESSIONS_DB.items()):
        if sess['user_id'] == user_id:
            del SESSIONS_DB[token]
    
    return {
        "message": "Account deleted successfully",
        "data_deleted": True
    }


# Helper: Detect potential PII in capabilities
def _contains_potential_pii(data: Dict) -> bool:
    """
    Check if capabilities contain potential PII
    Returns True if suspicious fields detected
    """
    
    PII_PATTERNS = [
        'name', 'first_name', 'last_name', 'full_name',
        'address', 'street', 'city', 'zip', 'postal',
        'phone', 'mobile', 'tel',
        'ssn', 'social_security',
        'dob', 'birth', 'birthday',
        'credit_card', 'passport', 'license'
    ]
    
    # Check keys
    for key in data.keys():
        key_lower = key.lower()
        for pattern in PII_PATTERNS:
            if pattern in key_lower:
                return True
    
    # Check string values for potential names/addresses
    for value in data.values():
        if isinstance(value, str):
            # If string contains multiple words with capitals (likely a name)
            words = value.split()
            if len(words) >= 2 and sum(1 for w in words if w and w[0].isupper()) >= 2:
                # Could be a name like "John Smith"
                # Allow certain technical terms that have capitals
                technical_terms = ['AI/ML', 'CI/CD', 'DevOps', 'GitHub', 'AWS', 'GCP']
                if value not in technical_terms:
                    return True
    
    return False


# Admin/Debug Endpoints (disable in production)
@router.get("/debug/stats")
async def debug_stats():
    """Debug endpoint to see database stats (disable in production)"""
    return {
        "total_users": len(USERS_DB),
        "total_sessions": len(SESSIONS_DB),
        "total_capabilities": len(CAPABILITIES_DB),
        "active_sessions": sum(
            1 for s in SESSIONS_DB.values() 
            if s['expires_at'] > datetime.utcnow()
        )
    }


@router.post("/debug/load-simulated-users")
async def load_simulated_users():
    """Load simulated users from testing/simulated_users.json"""
    import os
    
    json_path = os.path.join(os.path.dirname(__file__), '..', 'testing', 'simulated_users.json')
    
    if not os.path.exists(json_path):
        raise HTTPException(status_code=404, detail="Simulated users file not found")
    
    with open(json_path, 'r') as f:
        users = json.load(f)
    
    loaded = 0
    for user in users:
        if user['email'] not in USERS_DB:
            USERS_DB[user['email']] = {
                'user_id': user['user_id'],
                'auth_hash': user['auth_hash'],
                'encrypted_profile': user['encrypted_profile'],
                'created_at': user['created_at']
            }
            
            CAPABILITIES_DB[user['user_id']] = {
                **user['capabilities'],
                'user_id': user['user_id'],
                'email': user['email']
            }
            loaded += 1
    
    return {
        "message": f"Loaded {loaded} simulated users",
        "total_users": len(USERS_DB)
    }
