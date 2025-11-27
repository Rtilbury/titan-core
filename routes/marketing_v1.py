from __future__ import annotations

import time
from typing import Optional, Dict, Any, List

from fastapi import APIRouter
from pydantic import BaseModel, Field


API_VERSION = "1.0.0"

router = APIRouter(
    prefix="",
    tags=["marketing-v1"],
)


# --------------------------------------------------------------------
# Shared response envelope (same style as core/support)
# --------------------------------------------------------------------


def make_response(
    *,
    ok: bool,
    event: Optional[str],
    data: Optional[Dict[str, Any]] = None,
    msg: Optional[str] = None,
) -> Dict[str, Any]:
    return {
        "ok": ok,
        "event": event,
        "data": data or {},
        "msg": msg,
        "meta": {
            "version": API_VERSION,
            "timestamp": time.time(),
            "source": "titan-core-marketing-v1",
        },
    }


# --------------------------------------------------------------------
# Simple deterministic template engine (no external AI)
# --------------------------------------------------------------------


SUPPORTED_USE_CASES = {
    "landing_headline",
    "feature_blurb",
    "dev_portal_intro",
    "changelog_snippet",
    "email_invite",
}


SUPPORTED_TONES = {
    "neutral",
    "friendly",
    "technical",
}


SUPPORTED_AUDIENCES = {
    "developer",
    "cto",
    "product",
}


def _base_product_name(product_name: Optional[str]) -> str:
    return product_name or "Titan-Core"


def _landing_headline(product_name: str, audience: str, tone: str) -> str:
    if audience == "developer":
        if tone == "technical":
            return f"{product_name}: behavioural telemetry for real-time product decisions."
        elif tone == "friendly":
            return f"{product_name}: understand user behaviour without drowning in analytics."
        else:
            return f"{product_name}: a lightweight behavioural engine for modern apps."
    if audience == "cto":
        return f"{product_name}: a low-friction way to add behavioural intelligence to your stack."
    if audience == "product":
        return f"{product_name}: see how users actually move through your product, in real time."
    return f"{product_name}: lightweight behavioural intelligence for your product."


def _feature_blurb(product_name: str, audience: str, tone: str) -> str:
    base = (
        f"{product_name} tracks simple signals like friction, hesitation and pace per session, "
        "then returns clean, low-noise metrics you can plug into experiments, onboarding flows "
        "or internal dashboards."
    )
    if tone == "technical":
        extra = (
            " The API is stateless on the client side, with a small set of "
            "endpoints that are easy to wrap in any backend or workflow tool."
        )
    elif tone == "friendly":
        extra = (
            " You send a few numbers per event, and it gives you rolling summaries "
            "that are easy for teams to talk about and act on."
        )
    else:
        extra = (
            " It’s designed to be simple to adopt, without forcing you to rethink your stack."
        )
    return base + extra


def _dev_portal_intro(product_name: str, tone: str) -> str:
    if tone == "technical":
        return (
            f"{product_name} is a small FastAPI service with three core endpoints: start, event "
            "and end. You POST a session_id and a few numeric signals, and it returns rolling "
            "behavioural metrics you can feed into your own decision logic."
        )
    return (
        f"{product_name} gives you a focused set of APIs so you can start capturing behavioural "
        "signals in minutes, not weeks."
    )


def _changelog_snippet(product_name: str) -> str:
    return (
        f"Added {product_name} v1 as a lightweight behavioural engine. "
        "It exposes /v1/start, /v1/event and /v1/end, and returns rolling averages for key signals "
        "like friction, hesitation and pace."
    )


def _email_invite(product_name: str, audience: str, tone: str) -> str:
    greeting = "Hi there,"
    if audience == "developer":
        greeting = "Hey,"
    elif audience == "cto":
        greeting = "Hi,"

    body = (
        f"{greeting}\n\n"
        f"We've been working on {product_name}, a small behavioural engine you can drop into an "
        "existing product to capture simple signals like friction, hesitation and pace per session.\n\n"
        "It’s intentionally low resolution: just enough signal to inform decisions, without adding "
        "a heavy analytics layer.\n\n"
    )

    if tone == "technical":
        body += (
            "The API surface is three main endpoints (start, event, end) and the responses are "
            "designed to be easy to log, chart or feed into feature flags.\n\n"
        )
    else:
        body += (
            "If you’re curious, we can share a Postman collection and a short walkthrough showing "
            "how teams plug it into onboarding and feature experiments.\n\n"
        )

    body += "If this sounds useful, reply and I’ll send over the details.\n"
    body += "\nBest,\nRuss"
    return body


def generate_marketing_copy(
    *,
    use_case: str,
    audience: str,
    tone: str,
    product_name: Optional[str],
) -> Dict[str, Any]:
    product_name = _base_product_name(product_name)

    primary: str

    if use_case == "landing_headline":
        primary = _landing_headline(product_name, audience, tone)
    elif use_case == "feature_blurb":
        primary = _feature_blurb(product_name, audience, tone)
    elif use_case == "dev_portal_intro":
        primary = _dev_portal_intro(product_name, tone)
    elif use_case == "changelog_snippet":
        primary = _changelog_snippet(product_name)
    elif use_case == "email_invite":
        primary = _email_invite(product_name, audience, tone)
    else:
        primary = (
            f"{product_name} is a lightweight behavioural engine. "
            "Use it to track friction, hesitation and pace per session."
        )

    # Variants: simple deterministic rephrases
    variants: List[str] = []

    if use_case == "landing_headline":
        variants.append(
            f"Add behavioural intelligence to your product with {product_name}."
        )
        variants.append(
            f"{product_name} helps you see where users slow down, hesitate and drop off."
        )

    if use_case == "feature_blurb":
        variants.append(
            "Capture a few numeric signals per event and get back rolling metrics you can plug into experiments."
        )

    if use_case == "dev_portal_intro":
        variants.append(
            f"{product_name} focuses on a small, predictable API surface so you can integrate it quickly."
        )

    if use_case == "changelog_snippet":
        variants.append(
            "Introduced a dedicated behavioural engine service, keeping core product logic separate from telemetry."
        )

    if use_case == "email_invite":
        variants.append(
            "I can share a quick Postman collection if you’d like to see how it works in practice."
        )

    return {
        "primary": primary,
        "variants": variants,
        "use_case": use_case,
        "audience": audience,
        "tone": tone,
        "product_name": product_name,
    }


# --------------------------------------------------------------------
# Pydantic models & endpoint
# --------------------------------------------------------------------


class MarketingRequest(BaseModel):
    use_case: str = Field(
        ...,
        description=f"One of: {', '.join(sorted(SUPPORTED_USE_CASES))}",
    )
    audience: str = Field(
        ...,
        description=f"One of: {', '.join(sorted(SUPPORTED_AUDIENCES))}",
    )
    tone: str = Field(
        default="neutral",
        description=f"One of: {', '.join(sorted(SUPPORTED_TONES))}",
    )
    product_name: Optional[str] = Field(
        default=None,
        description="Override product name (defaults to 'Titan-Core').",
    )
    include_variants: bool = Field(
        default=True,
        description="If false, variants list will be empty.",
    )


class MarketingCopy(BaseModel):
    primary: str
    variants: List[str]
    use_case: str
    audience: str
    tone: str
    product_name: str


@router.post("/v1/marketing/generate")
async def generate_marketing(payload: MarketingRequest) -> Dict[str, Any]:
    """
    Deterministic marketing helper for Titan-Core.

    Produces short, focused copy for developer-facing contexts like
    landing pages, feature blurbs, dev portals and emails. There are no
    external AI calls: everything is template-driven and safe to expose
    in a public repository.
    """
    if payload.use_case not in SUPPORTED_USE_CASES:
        return make_response(
            ok=False,
            event="marketing_error",
            msg=(
                f"Unsupported use_case '{payload.use_case}'. "
                f"Supported: {', '.join(sorted(SUPPORTED_USE_CASES))}."
            ),
            data={},
        )

    if payload.audience not in SUPPORTED_AUDIENCES:
        return make_response(
            ok=False,
            event="marketing_error",
            msg=(
                f"Unsupported audience '{payload.audience}'. "
                f"Supported: {', '.join(sorted(SUPPORTED_AUDIENCES))}."
            ),
            data={},
        )

    if payload.tone not in SUPPORTED_TONES:
        return make_response(
            ok=False,
            event="marketing_error",
            msg=(
                f"Unsupported tone '{payload.tone}'. "
                f"Supported: {', '.join(sorted(SUPPORTED_TONES))}."
            ),
            data={},
        )

    raw = generate_marketing_copy(
        use_case=payload.use_case,
        audience=payload.audience,
        tone=payload.tone,
        product_name=payload.product_name,
    )

    if not payload.include_variants:
        raw["variants"] = []

    mc = MarketingCopy(**raw)

    return make_response(
        ok=True,
        event="marketing_copy",
        data=mc.dict(),
        msg=None,
    )
