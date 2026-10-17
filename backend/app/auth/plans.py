"""Subscription plans: one source for prices, features and which views a plan unlocks.

Basic unlocks the General view; Pro unlocks General and Expert. Payments are not connected yet:
BILLING_MODE=demo switches the plan at once (no payment taken, for demos), BILLING_MODE=off refuses.
A payment provider plugs in at `checkout()` (return a hosted checkout URL instead of switching).
"""
from __future__ import annotations

from ..config import settings

PLANS = [
    {"id": "basic", "name": "Basic", "price_usd": 10, "interval": "month", "views": ["general"],
     "tagline": "The one-page assessment for sales and project leads.",
     "features": ["General view: one-page summary of every assessment",
                  "Problems found in the request and what to test first",
                  "Questions to ask the customer",
                  "First experiment and next step with AFS",
                  "Markdown export of each assessment",
                  "Saved enquiries and run history in your account"]},
    {"id": "pro", "name": "Pro", "price_usd": 30, "interval": "month", "views": ["general", "expert"],
     "highlight": True, "tagline": "The full engineering workbench behind every answer.",
     "features": ["Everything in Basic",
                  "Expert view: the full technical report",
                  "Method comparison matrix",
                  "Evidence with the source page and quote highlighted",
                  "Verification and quality checks for every claim",
                  "Model trace and council records"]},
]
DEFAULT_TIER = "basic"
_LEGACY = {"free": "basic", "expert": "pro"}       # tier names used before the pricing page existed


def plan(plan_id: str) -> dict | None:
    return next((p for p in PLANS if p["id"] == plan_id), None)


def tier_of(user: dict | None) -> str:
    raw = (user or {}).get("subscription_tier") or DEFAULT_TIER
    raw = _LEGACY.get(raw, raw)
    return raw if plan(raw) else DEFAULT_TIER


def views_for(user: dict | None) -> list[str]:
    return list(plan(tier_of(user))["views"])


def can_view(user: dict | None, view: str) -> bool:
    return view in views_for(user)


def public() -> dict:
    return {"plans": PLANS, "currency": "USD", "billing_mode": settings.billing_mode}
