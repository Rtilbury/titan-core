from __future__ import annotations

import time
from typing import Optional, Dict, Any, List

from fastapi import APIRouter
from pydantic import BaseModel, Field


API_VERSION = "1.0.0"

router = APIRouter(
    prefix="",
    tags=["support-v1"],
)


# --------------------------------------------------------------------
# Shared response envelope (same style as core_v1)
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
            "source": "titan-core-support-v1",
        },
    }


# --------------------------------------------------------------------
# Simple internal knowledge base
# (no external AI calls, everything is deterministic and safe)
# --------------------------------------------------------------------


class FAQItem(BaseModel):
    id: str
    title: str
    tags: List[str]
    endpoint: Optional[str] = None
    answer: str
    example_request: Optional[Dict[str, Any]] = None
    example_response_hint: Optional[str] = None


FAQ_ITEMS: List[FAQItem] = [
    FAQItem(
        id="start-session",
        title="How do I start a Titan-X session?",
        tags=["start", "session", "begin", "initialise", "init"],
        endpoint="/v1/start",
        answer=(
            "To start a Titan-X Core session, send a POST request to /v1/start with "
            "a JSON body containing at least a non-empty 'session_id'. "
            "You can also pass an optional 'user_id' and 'metadata' dictionary."
        ),
        example_request={
            "method": "POST",
            "url": "/v1/start",
            "body": {
                "session_id": "demo-session-1",
                "user_id": "user-123",
                "metadata": {"source": "docs-example"},
            },
        },
        example_response_hint="Look for ok=true and event='session_started'.",
    ),
    FAQItem(
        id="record-event",
        title="How do I record behavioural events?",
        tags=["event", "record", "metrics", "signals", "friction", "hesitation", "pace"],
        endpoint="/v1/event",
        answer=(
            "Use POST /v1/event to record behavioural signals for an existing session. "
            "You must provide 'session_id', 'event_type', and 'timestamp'. "
            "You can optionally include 'friction', 'hesitation', and 'pace' scores "
            "plus a 'context' object (page, element, extra). "
            "Titan-Core will update the rolling averages for that session."
        ),
        example_request={
            "method": "POST",
            "url": "/v1/event",
            "body": {
                "session_id": "demo-session-1",
                "event_type": "focus_shift",
                "timestamp": 1710000000.0,
                "friction": 0.31,
                "hesitation": 0.45,
                "pace": 0.82,
                "context": {
                    "page": "dashboard",
                    "element": "hero-cta",
                    "extra": {"notes": "first click"},
                },
            },
        },
        example_response_hint=(
            "Data will contain 'events_count', 'average_friction', "
            "'average_hesitation', and 'average_pace'."
        ),
    ),
    FAQItem(
        id="end-session",
        title="How do I end a session and get a summary?",
        tags=["end", "finish", "close", "summary"],
        endpoint="/v1/end",
        answer=(
            "To close a session and optionally retrieve summary metrics, "
            "call POST /v1/end with 'session_id' and, optionally, "
            "'include_summary' (default is true). "
            "If the session exists, Titan-Core will return final averages for "
            "friction, hesitation, and pace."
        ),
        example_request={
            "method": "POST",
            "url": "/v1/end",
            "body": {
                "session_id": "demo-session-1",
                "include_summary": True,
            },
        },
        example_response_hint=(
            "If include_summary=true, data.summary will mirror the rolling metrics "
            "you saw from /v1/event."
        ),
    ),
    FAQItem(
        id="health-status",
        title="What are /health and /status for?",
        tags=["health", "status", "ping", "uptime"],
        endpoint="/health",
        answer=(
            "GET /health is a lightweight endpoint for uptime checks. "
            "Use it from your monitoring to confirm Titan-Core is reachable. "
            "GET /status returns basic service metadata such as service name "
            "and version, which is useful when debugging deployments."
        ),
        example_request={
            "method": "GET",
            "url": "/health",
        },
        example_response_hint="Expect ok=true if the service is running.",
    ),
]


def _normalize(text: str) -> List[str]:
    return [t for t in text.lower().replace("/", " ").replace("_", " ").split() if t]


def _score_faq_match(question: str, faq: FAQItem, endpoint: Optional[str]) -> int:
    score = 0
    q_tokens = set(_normalize(question))

    # Tag overlap
    for tag in faq.tags:
        if tag in q_tokens:
            score += 2

    # Endpoint hint
    if endpoint and faq.endpoint and endpoint.strip() == faq.endpoint:
        score += 4

    # Direct word overlap with title
    for token in _normalize(faq.title):
        if token in q_tokens:
            score += 1

    return score


def find_best_faq_match(
    question: str,
    endpoint: Optional[str] = None,
) -> Optional[FAQItem]:
    best_item: Optional[FAQItem] = None
    best_score = 0

    for item in FAQ_ITEMS:
        s = _score_faq_match(question, item, endpoint)
        if s > best_score:
            best_item = item
            best_score = s

    # Require at least a minimal score, otherwise we fall back to generic help
    if best_score < 2:
        return None
    return best_item


# --------------------------------------------------------------------
# Error explanation helpers
# --------------------------------------------------------------------


def explain_error(error_message: str) -> Dict[str, Any]:
    text = error_message.lower()
    explanation = "General error. Check your request body and headers."
    hints: List[str] = []

    if "422" in text or "unprocessable entity" in text:
        explanation = (
            "HTTP 422 Unprocessable Entity. "
            "This usually means your JSON body does not match the schema "
            "expected by the endpoint (missing fields, wrong types, etc.)."
        )
        hints.append("Verify all required fields are present and have the right types.")

    if "400" in text:
        explanation = (
            "HTTP 400 Bad Request. "
            "The server could not understand your request. "
            "Check JSON formatting and any query parameters."
        )

    if "401" in text or "unauthorized" in text:
        explanation = (
            "HTTP 401 Unauthorized. "
            "This typically indicates missing or invalid authentication. "
            "Titan-Core v1 does not require auth by default, so this may come "
            "from your own gateway or proxy."
        )

    if "session" in text and "not found" in text:
        hints.append(
            "Make sure you call /v1/start before sending /v1/event or /v1/end "
            "for a given session_id."
        )

    return {
        "explanation": explanation,
        "hints": hints,
    }


# --------------------------------------------------------------------
# Pydantic models
# --------------------------------------------------------------------


class SupportRequest(BaseModel):
    question: str = Field(
        ...,
        description="Free-form question about using Titan-Core.",
    )
    endpoint: Optional[str] = Field(
        default=None,
        description="Optional endpoint you are working with (e.g. /v1/event).",
    )
    error_message: Optional[str] = Field(
        default=None,
        description="Optional error text you want explained.",
    )
    include_examples: bool = Field(
        default=True,
        description="Whether to include example request bodies when relevant.",
    )


class SupportAnswer(BaseModel):
    answer: str
    topic_id: Optional[str] = None
    endpoint: Optional[str] = None
    example_request: Optional[Dict[str, Any]] = None
    example_response_hint: Optional[str] = None
    error_explanation: Optional[Dict[str, Any]] = None
    suggested_next_action: Optional[str] = None


# --------------------------------------------------------------------
# Endpoint
# --------------------------------------------------------------------


@router.post("/v1/support/ask")
async def ask_support(payload: SupportRequest) -> Dict[str, Any]:
    """
    Lightweight, deterministic support helper for Titan-Core v1.
    Answers questions based on a small internal FAQ, and can optionally
    give friendly explanations for common error messages.
    """
    faq_item = find_best_faq_match(payload.question, payload.endpoint)

    # Base answer
    if faq_item:
        answer_text = faq_item.answer
        suggested_next_action = "Try the example request against your running Titan-Core instance."
        example_req = faq_item.example_request if payload.include_examples else None
        example_hint = faq_item.example_response_hint
    else:
        answer_text = (
            "I couldn't match your question to a specific topic. "
            "Make sure you include which endpoint you're using (e.g. /v1/start, /v1/event, /v1/end) "
            "and what you're trying to achieve."
        )
        suggested_next_action = (
            "Rephrase your question including the endpoint and whether you're starting, "
            "recording, or ending a session."
        )
        example_req = None
        example_hint = None

    error_info: Optional[Dict[str, Any]] = None
    if payload.error_message:
        error_info = explain_error(payload.error_message)

    support_answer = SupportAnswer(
        answer=answer_text,
        topic_id=faq_item.id if faq_item else None,
        endpoint=faq_item.endpoint if faq_item else payload.endpoint,
        example_request=example_req,
        example_response_hint=example_hint,
        error_explanation=error_info,
        suggested_next_action=suggested_next_action,
    )

    return make_response(
        ok=True,
        event="support_answer",
        data=support_answer.dict(),
        msg=None,
    )
