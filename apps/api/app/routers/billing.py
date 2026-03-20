from __future__ import annotations

import uuid
from typing import List, Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User

logger = structlog.get_logger(__name__)
router = APIRouter()


class BillingPortalResponse(BaseModel):
    portal_url: str


class CheckoutSessionResponse(BaseModel):
    checkout_url: str
    session_id: str


@router.post("/checkout", response_model=CheckoutSessionResponse, summary="Create Stripe checkout session")
async def create_checkout_session(
    price_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CheckoutSessionResponse:
    import stripe

    stripe.api_key = settings.STRIPE_SECRET_KEY
    session = stripe.checkout.Session.create(
        customer_email=current_user.email,
        line_items=[{"price": price_id, "quantity": 1}],
        mode="subscription",
        success_url="https://app.talentora.ai/billing/success?session_id={CHECKOUT_SESSION_ID}",
        cancel_url="https://app.talentora.ai/billing/cancel",
        metadata={"workspace_id": str(current_user.workspace_id), "user_id": str(current_user.id)},
    )
    return CheckoutSessionResponse(checkout_url=session.url, session_id=session.id)


@router.post("/portal", response_model=BillingPortalResponse, summary="Create Stripe billing portal session")
async def billing_portal(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BillingPortalResponse:
    import stripe
    from sqlalchemy import select
    from app.models.user import Workspace

    stripe.api_key = settings.STRIPE_SECRET_KEY

    stmt = select(Workspace).where(Workspace.id == current_user.workspace_id)
    result = await db.execute(stmt)
    workspace = result.scalar_one_or_none()
    if not workspace or not workspace.stripe_customer_id:
        raise HTTPException(status_code=400, detail="No active subscription found")

    session = stripe.billing_portal.Session.create(
        customer=workspace.stripe_customer_id,
        return_url="https://app.talentora.ai/settings/billing",
    )
    return BillingPortalResponse(portal_url=session.url)


@router.post("/webhook", include_in_schema=False)
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)) -> dict:
    import stripe

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    event_type = event["type"]
    logger.info("Stripe webhook received", event_type=event_type)

    if event_type == "checkout.session.completed":
        _session = event["data"]["object"]
        # TODO: provision subscription, update workspace tier
    elif event_type in ("customer.subscription.updated", "customer.subscription.deleted"):
        # TODO: update workspace subscription status
        pass

    return {"received": True}
