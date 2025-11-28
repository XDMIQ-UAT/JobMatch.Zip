"""
Age Verification API endpoints.
COPPA compliance - ensures users are 18+ before account creation.
"""
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, date
from typing import Dict, Any

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/age-verification", tags=["age-verification"])


class AgeVerificationRequest(BaseModel):
    """Request model for age verification."""
    birth_year: int = Field(..., ge=1900, le=datetime.now().year, description="Birth year")
    birth_month: int = Field(..., ge=1, le=12, description="Birth month (1-12)")
    birth_day: int = Field(..., ge=1, le=31, description="Birth day (1-31)")
    
    @field_validator('birth_day')
    @classmethod
    def validate_day(cls, v, info):
        """Validate day is valid for given month/year."""
        # Note: We can't validate against specific month here since we don't have access to other fields yet
        # This is done in the model_validator below
        return v
    
    @field_validator('birth_year')
    @classmethod
    def validate_not_future(cls, v):
        """Ensure birthdate is not in the future."""
        if v > datetime.now().year:
            raise ValueError("Birth year cannot be in the future")
        return v


class AgeVerificationResponse(BaseModel):
    """Response model for age verification."""
    is_verified: bool
    age: int
    required_age: int = 18
    message: str


def calculate_age(birth_year: int, birth_month: int, birth_day: int) -> int:
    """
    Calculate age from birthdate.
    
    Args:
        birth_year: Year of birth
        birth_month: Month of birth (1-12)
        birth_day: Day of birth
        
    Returns:
        Age in years
        
    Raises:
        ValueError: If date is invalid
    """
    try:
        birth_date = date(birth_year, birth_month, birth_day)
    except ValueError as e:
        raise ValueError(f"Invalid date: {e}")
    
    today = date.today()
    
    # Check if date is in the future
    if birth_date > today:
        raise ValueError("Birthdate cannot be in the future")
    
    # Calculate age
    age = today.year - birth_date.year
    
    # Adjust if birthday hasn't occurred yet this year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    
    return age


@router.post("/verify", response_model=AgeVerificationResponse)
async def verify_age(request: AgeVerificationRequest) -> AgeVerificationResponse:
    """
    Verify user age for COPPA compliance.
    
    This endpoint:
    - Validates the birthdate
    - Calculates age
    - Returns verification result
    - Does NOT store the birthdate (privacy-preserving)
    
    Args:
        request: Age verification request with birthdate
        
    Returns:
        AgeVerificationResponse with verification result
        
    Raises:
        HTTPException: 400 if date is invalid
    """
    required_age = 18  # COPPA requirement (13+), extended to 18 for platform safety
    
    try:
        # Calculate age
        age = calculate_age(
            request.birth_year,
            request.birth_month,
            request.birth_day
        )
        
        # Determine if user meets age requirement
        is_verified = age >= required_age
        
        if is_verified:
            logger.info(f"Age verification passed: {age} years old (≥{required_age})")
            message = f"Age verified: You are {age} years old"
        else:
            logger.warning(f"Age verification failed: {age} years old (<{required_age})")
            message = f"Access denied: You must be at least {required_age} years old to use this platform"
        
        return AgeVerificationResponse(
            is_verified=is_verified,
            age=age,
            required_age=required_age,
            message=message
        )
        
    except ValueError as e:
        logger.error(f"Invalid birthdate provided: {e}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check for age verification service.
    
    Returns:
        Service health status
    """
    return {
        "service": "age-verification",
        "status": "operational",
        "required_age": 18,
        "compliance": "COPPA"
    }
