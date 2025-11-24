"""
Stripe subscription management API routes.
Handles checkout sessions, webhooks, refunds, and subscription management.
"""
from fastapi import APIRouter, HTTPException, Request, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from typing import Optional
import stripe
import os
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/subscription", tags=["subscription"])

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_your-stripe-secret-key")

# Pricing configuration - $1/month accessible tier
MONTHLY_PRICE = 100  # $1.00 in cents
PRICE_PER_SEAT = 800000  # Legacy value, not used in current tier
MAX_SEATS = 1  # Single user subscription
TRIAL_PERIOD_DAYS = 0  # No trial period
MAX_RESUBSCRIPTIONS = 999  # Effectively unlimited
REFUND_PERIOD_DAYS = 14
CREDIT_PERIOD_DAYS = 60

# Stripe IDs ($1/month accessible tier)
PRODUCT_ID = "prod_TTufp6ZDcEoeeC"
PRICE_ID = "price_1SWwqbBObYs4DzR4HldYKqqe"


# Pydantic models
class CheckoutSessionRequest(BaseModel):
    email: EmailStr
    user_id: Optional[str] = None


class CancelSubscriptionRequest(BaseModel):
    subscription_id: str


class RefundRequest(BaseModel):
    subscription_id: str
    reason: Optional[str] = None


class CreditRequest(BaseModel):
    subscription_id: str
    reason: str
    email: EmailStr


@router.post("/create-checkout-session")
async def create_checkout_session(request: CheckoutSessionRequest):
    """
    Create a Stripe Checkout session for weekly subscription.
    Price: $47.90/week
    Max resubscriptions: 6
    """
    try:
        # Get or create customer
        customer = await get_or_create_customer(request.email, request.user_id)
        subscription_count = await get_customer_subscription_count(customer.id)

        if subscription_count >= MAX_RESUBSCRIPTIONS:
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "Maximum resubscription limit reached",
                    "message": f"You have reached the maximum of {MAX_RESUBSCRIPTIONS} resubscriptions. Please contact support."
                }
            )

        # Create checkout session
        session = stripe.checkout.Session.create(
            customer=customer.id,
            payment_method_types=["card"],
            line_items=[
                {
                    "price": PRICE_ID,  # Use pre-configured price with trial
                    "quantity": 1,
                }
            ],
            mode="subscription",
            success_url=f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/subscription/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/subscription/cancelled",
            metadata={
                "user_id": request.user_id or "",
                "subscription_number": str(subscription_count + 1),
            },
            subscription_data={
                "metadata": {
                    "user_id": request.user_id or "",
                    "subscription_number": str(subscription_count + 1),
                    "start_date": datetime.utcnow().isoformat(),
                }
            },
        )

        return {
            "session_id": session.id,
            "url": session.url,
            "subscription_count": subscription_count + 1,
            "max_subscriptions": MAX_RESUBSCRIPTIONS,
        }
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail={"error": str(e)})
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})


@router.get("/status/{customer_id}")
async def get_subscription_status(customer_id: str):
    """Get subscription status for a customer."""
    try:
        subscriptions = stripe.Subscription.list(
            customer=customer_id, status="all", limit=100
        )

        active_subscription = next(
            (sub for sub in subscriptions.data if sub.status in ["active", "trialing"]),
            None
        )

        subscription_count = len([
            sub for sub in subscriptions.data if sub.status != "canceled"
        ])

        return {
            "has_active_subscription": active_subscription is not None,
            "subscription": active_subscription,
            "subscription_count": subscription_count,
            "max_subscriptions": MAX_RESUBSCRIPTIONS,
            "can_resubscribe": subscription_count < MAX_RESUBSCRIPTIONS,
        }
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail={"error": str(e)})


@router.post("/cancel")
async def cancel_subscription(request: CancelSubscriptionRequest):
    """Cancel an active subscription."""
    try:
        subscription = stripe.Subscription.cancel(request.subscription_id)
        return {
            "success": True,
            "subscription": subscription,
            "message": "Subscription cancelled successfully"
        }
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail={"error": str(e)})


@router.post("/request-refund")
async def request_refund(request: RefundRequest):
    """
    Request a refund within 14 days of subscription.
    After 14 days, user must request credits instead.
    """
    try:
        subscription = stripe.Subscription.retrieve(request.subscription_id)
        subscription_start = datetime.fromtimestamp(subscription.created)
        days_since_start = (datetime.utcnow() - subscription_start).days

        # Check if within 14-day refund period
        if days_since_start > REFUND_PERIOD_DAYS:
            return JSONResponse(
                status_code=403,
                content={
                    "error": "Refund period expired",
                    "message": f"Refunds are only available within {REFUND_PERIOD_DAYS} days of subscription. You may be eligible for credits instead.",
                    "eligible_for_credits": days_since_start <= CREDIT_PERIOD_DAYS,
                }
            )

        # Get latest invoice
        invoices = stripe.Invoice.list(subscription=request.subscription_id, limit=1)
        if not invoices.data:
            raise HTTPException(status_code=404, detail={"error": "No invoices found"})

        invoice = invoices.data[0]
        if not invoice.payment_intent:
            raise HTTPException(status_code=400, detail={"error": "No payment found"})

        # Create refund
        refund = stripe.Refund.create(
            payment_intent=invoice.payment_intent,
            reason="requested_by_customer",
            metadata={
                "subscription_id": request.subscription_id,
                "customer_reason": request.reason or "No reason provided",
            },
        )

        # Cancel subscription
        stripe.Subscription.cancel(request.subscription_id)

        return {
            "success": True,
            "refund": refund,
            "message": "Refund processed successfully. Your subscription has been cancelled."
        }
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail={"error": str(e)})


@router.post("/request-credits")
async def request_credits(request: CreditRequest):
    """
    Request credits within 60 days (requires written correspondence).
    Credits must be manually reviewed by support team.
    """
    try:
        subscription = stripe.Subscription.retrieve(request.subscription_id)
        subscription_start = datetime.fromtimestamp(subscription.created)
        days_since_start = (datetime.utcnow() - subscription_start).days

        if days_since_start > CREDIT_PERIOD_DAYS:
            return JSONResponse(
                status_code=403,
                content={
                    "error": "Credit period expired",
                    "message": f"Credits are only available within {CREDIT_PERIOD_DAYS} days of subscription."
                }
            )

        # TODO: Store credit request in database and send email to support
        # For now, return success message
        return {
            "success": True,
            "message": "Credit request received. Our team will review and respond via email within 2 business days.",
            "request_details": {
                "subscription_id": request.subscription_id,
                "email": request.email,
                "reason": request.reason,
                "days_since_start": days_since_start,
            }
        }
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail={"error": str(e)})


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="stripe-signature")
):
    """
    Stripe webhook handler for subscription events.
    Configure this URL in your Stripe Dashboard: https://jobmatch.zip/api/subscription/webhook
    """
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    if not webhook_secret:
        raise HTTPException(status_code=500, detail={"error": "Webhook secret not configured"})

    payload = await request.body()

    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, webhook_secret
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"error": "Invalid payload"})
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail={"error": "Invalid signature"})

    # Handle the event
    event_type = event["type"]
    data = event["data"]["object"]

    if event_type == "checkout.session.completed":
        print(f"Checkout completed: {data['id']}")
        # TODO: Update user's subscription status in database

    elif event_type == "customer.subscription.created":
        print(f"Subscription created: {data['id']}")
        # TODO: Activate user's subscription features

    elif event_type == "customer.subscription.updated":
        print(f"Subscription updated: {data['id']}")
        # TODO: Update user's subscription status

    elif event_type == "customer.subscription.deleted":
        print(f"Subscription deleted: {data['id']}")
        # TODO: Deactivate user's subscription features

    elif event_type == "invoice.payment_succeeded":
        print(f"Payment succeeded: {data['id']}")
        # TODO: Send receipt email

    elif event_type == "invoice.payment_failed":
        print(f"Payment failed: {data['id']}")
        # TODO: Send payment failure notification

    else:
        print(f"Unhandled event type: {event_type}")

    return {"received": True}


# Helper functions
async def get_or_create_customer(email: str, user_id: Optional[str] = None):
    """Get existing customer or create new one."""
    customers = stripe.Customer.list(email=email, limit=1)
    
    if customers.data:
        return customers.data[0]
    
    return stripe.Customer.create(
        email=email,
        metadata={"user_id": user_id or ""}
    )


async def get_customer_subscription_count(customer_id: str) -> int:
    """Count total subscriptions for a customer."""
    subscriptions = stripe.Subscription.list(
        customer=customer_id, status="all", limit=100
    )
    return len(subscriptions.data)
