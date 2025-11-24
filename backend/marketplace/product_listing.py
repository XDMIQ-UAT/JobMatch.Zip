"""
Product/Service Listing System for Marketplace.
Supports both asset-based ("what we have") and capability-based ("what we can do") listings.
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
from sqlalchemy.orm import Session

from backend.database.models import AnonymousUser
from backend.resilience.state_management import StateManager, CheckpointType

logger = logging.getLogger(__name__)


class ListingType(str, Enum):
    """Types of marketplace listings."""
    ASSET = "asset"  # What we have (products, inventory)
    CAPABILITY = "capability"  # What we can do (services, skills)
    COMBINED = "combined"  # Both asset and capability


class ListingStatus(str, Enum):
    """Listing status."""
    DRAFT = "draft"
    ACTIVE = "active"
    SOLD = "sold"
    INACTIVE = "inactive"
    REMOVED = "removed"


class ProductListingManager:
    """Manages product/service listings in marketplace."""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.state_manager = StateManager(db_session)
    
    def create_listing(
        self,
        seller_id: str,
        listing_type: ListingType,
        title: str,
        description: str,
        pricing: Dict[str, Any],
        asset_details: Optional[Dict[str, Any]] = None,
        capability_details: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a marketplace listing.
        Supports both asset-based and capability-based listings.
        """
        listing_data = {
            "seller_id": seller_id,
            "listing_type": listing_type.value,
            "title": title,
            "description": description,
            "asset_details": asset_details or {},
            "capability_details": capability_details or {},
            "pricing": pricing,
            "status": ListingStatus.DRAFT.value,
            "created_at": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        
        # Create checkpoint
        checkpoint = self.state_manager.create_checkpoint(
            checkpoint_type=CheckpointType.SYSTEM,
            entity_id=f"listing_{seller_id}_{datetime.utcnow().timestamp()}",
            state_data=listing_data
        )
        
        listing_data["checkpoint_id"] = checkpoint.id
        listing_data["listing_id"] = f"lst_{checkpoint.id}"
        
        logger.info(f"Created {listing_type.value} listing for seller {seller_id[:8]}...")
        
        return listing_data
    
    def calculate_listing_value(
        self,
        asset_details: Optional[Dict[str, Any]],
        capability_details: Optional[Dict[str, Any]],
        xdmiq_score: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Calculate listing value based on both assets and capabilities.
        Similar to Western Auctions valuation model.
        """
        asset_value = 0
        capability_value = 0
        
        # Calculate asset value ("what we have")
        if asset_details:
            asset_value = self._calculate_asset_value(asset_details)
        
        # Calculate capability value ("what we can do")
        if capability_details:
            capability_value = self._calculate_capability_value(
                capability_details,
                xdmiq_score
            )
        
        # Combined value calculation
        total_value = asset_value + capability_value
        
        # If both present, add synergy bonus
        if asset_value > 0 and capability_value > 0:
            synergy_bonus = (asset_value + capability_value) * 0.1
            total_value += synergy_bonus
        
        return {
            "asset_value": asset_value,
            "capability_value": capability_value,
            "total_value": total_value,
            "value_breakdown": {
                "assets_percentage": (asset_value / total_value * 100) if total_value > 0 else 0,
                "capabilities_percentage": (capability_value / total_value * 100) if total_value > 0 else 0
            }
        }
    
    def _calculate_asset_value(self, asset_details: Dict[str, Any]) -> float:
        """Calculate value of assets/products."""
        # Base value from pricing
        base_price = asset_details.get("price", 0)
        
        # Condition multiplier
        condition = asset_details.get("condition", "new")
        condition_multipliers = {
            "new": 1.0,
            "like_new": 0.9,
            "excellent": 0.8,
            "good": 0.6,
            "fair": 0.4
        }
        condition_mult = condition_multipliers.get(condition, 0.5)
        
        # Quantity/value
        quantity = asset_details.get("quantity", 1)
        
        return base_price * condition_mult * quantity
    
    def _calculate_capability_value(
        self,
        capability_details: Dict[str, Any],
        xdmiq_score: Optional[int]
    ) -> float:
        """Calculate value of capabilities/services."""
        # Base hourly rate or project rate
        base_rate = capability_details.get("hourly_rate", 0) or capability_details.get("project_rate", 0)
        
        # XDMIQ score multiplier (if available)
        xdmiq_multiplier = 1.0
        if xdmiq_score:
            # Higher XDMIQ score = higher value
            xdmiq_multiplier = 0.5 + (xdmiq_score / 100) * 0.5  # 0.5x to 1.0x multiplier
        
        # Experience multiplier
        experience_years = capability_details.get("experience_years", 0)
        experience_multiplier = 1.0 + (experience_years * 0.1)  # 10% per year
        
        # Portfolio quality multiplier
        portfolio_quality = capability_details.get("portfolio_quality", "good")
        portfolio_multipliers = {
            "excellent": 1.2,
            "good": 1.0,
            "fair": 0.8
        }
        portfolio_mult = portfolio_multipliers.get(portfolio_quality, 1.0)
        
        return base_rate * xdmiq_multiplier * experience_multiplier * portfolio_mult


def create_listing_manager(db_session: Session) -> ProductListingManager:
    """Factory function to create listing manager."""
    return ProductListingManager(db_session)

