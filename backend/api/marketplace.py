"""
Marketplace API Endpoints.
Infrastructure for LLC/Solo Proprietor goods/services exchange.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from decimal import Decimal

from database.connection import get_db
from marketplace.product_listing import (
    create_listing_manager,
    ListingType,
    ListingStatus
)
from marketplace.payment_pipeline import (
    create_payment_pipeline,
    PaymentMethod,
    PaymentStatus
)

router = APIRouter(prefix="/api/marketplace", tags=["marketplace"])


class CreateListingRequest(BaseModel):
    """Request to create marketplace listing."""
    seller_id: str
    listing_type: str  # asset, capability, combined
    title: str
    description: str
    asset_details: Optional[Dict[str, Any]] = None
    capability_details: Optional[Dict[str, Any]] = None
    pricing: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None


class ListingResponse(BaseModel):
    """Response for marketplace listing."""
    listing_id: str
    seller_id: str
    listing_type: str
    title: str
    description: str
    valuation: Optional[Dict[str, Any]] = None
    status: str
    created_at: str


class CreateTransactionRequest(BaseModel):
    """Request to create transaction."""
    buyer_id: str
    seller_id: str
    listing_id: str
    amount: float
    payment_method: str


class TransactionResponse(BaseModel):
    """Response for transaction."""
    transaction_id: str
    buyer_id: str
    seller_id: str
    amount: float
    platform_fee: float
    seller_payout: float
    status: str
    created_at: str


@router.post("/listings", response_model=ListingResponse)
async def create_listing(
    request: CreateListingRequest,
    db: Session = Depends(get_db)
):
    """Create a marketplace listing (asset, capability, or combined)."""
    manager = create_listing_manager(db)
    
    try:
        listing_type = ListingType(request.listing_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid listing type")
    
    listing = manager.create_listing(
        seller_id=request.seller_id,
        listing_type=listing_type,
        title=request.title,
        description=request.description,
        asset_details=request.asset_details,
        capability_details=request.capability_details,
        pricing=request.pricing,
        metadata=request.meta_data
    )
    
    # Calculate valuation
    from database.models import CapabilityAssessment
    assessment = db.query(CapabilityAssessment).filter(
        CapabilityAssessment.user_id == request.seller_id,
        CapabilityAssessment.assessment_type == "xdmiq"
    ).order_by(CapabilityAssessment.created_at.desc()).first()
    
    xdmiq_score = None
    if assessment and assessment.results.get("xdmiq_score"):
        xdmiq_score = assessment.results["xdmiq_score"].get("overall_score")
    
    valuation = manager.calculate_listing_value(
        asset_details=request.asset_details,
        capability_details=request.capability_details,
        xdmiq_score=xdmiq_score
    )
    
    listing["valuation"] = valuation
    
    return ListingResponse(
        listing_id=listing["listing_id"],
        seller_id=listing["seller_id"],
        listing_type=listing["listing_type"],
        title=listing["title"],
        description=listing["description"],
        valuation=valuation,
        status=listing["status"],
        created_at=listing["created_at"]
    )


@router.get("/listings/{listing_id}", response_model=ListingResponse)
async def get_listing(
    listing_id: str,
    db: Session = Depends(get_db)
):
    """Get marketplace listing by ID."""
    # Would query database in production
    raise HTTPException(status_code=501, detail="Not yet implemented")


@router.get("/listings", response_model=List[ListingResponse])
async def list_listings(
    listing_type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List marketplace listings with filters."""
    # Would query database in production
    return []


@router.post("/transactions", response_model=TransactionResponse)
async def create_transaction(
    request: CreateTransactionRequest,
    db: Session = Depends(get_db)
):
    """Create a payment transaction."""
    pipeline = create_payment_pipeline(db)
    
    try:
        payment_method = PaymentMethod(request.payment_method)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payment method")
    
    transaction = pipeline.create_transaction(
        buyer_id=request.buyer_id,
        seller_id=request.seller_id,
        listing_id=request.listing_id,
        amount=Decimal(str(request.amount)),
        payment_method=payment_method
    )
    
    return TransactionResponse(
        transaction_id=transaction["transaction_id"],
        buyer_id=transaction["buyer_id"],
        seller_id=transaction["seller_id"],
        amount=transaction["amount"],
        platform_fee=transaction["platform_fee"],
        seller_payout=transaction["seller_payout"],
        status=transaction["status"],
        created_at=transaction["created_at"]
    )


@router.post("/transactions/{transaction_id}/process")
async def process_payment(
    transaction_id: str,
    payment_token: str,
    db: Session = Depends(get_db)
):
    """Process payment for transaction."""
    pipeline = create_payment_pipeline(db)
    
    result = pipeline.process_payment(
        transaction_id=transaction_id,
        payment_token=payment_token
    )
    
    return result


@router.get("/valuation/calculate")
async def calculate_valuation(
    asset_details: Optional[Dict[str, Any]] = None,
    capability_details: Optional[Dict[str, Any]] = None,
    xdmiq_score: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Calculate listing valuation based on assets and capabilities."""
    manager = create_listing_manager(db)
    
    valuation = manager.calculate_listing_value(
        asset_details=asset_details,
        capability_details=capability_details,
        xdmiq_score=xdmiq_score
    )
    
    return valuation

