# routes/core_v1.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Any, Dict, List

from fastapi import APIRouter
from pydantic import BaseModel
import statistics
import math
import time


router = APIRouter(
    prefix="",
    tags=["core-v1"],
)


API_VERSION = "1.0.0"


# =====================================================
# Titan Response Format v1 (TRF-1)
# =====================================================

def trf(
    *,
    ok: bool = True,
    session_id: Optional[str] = None,
    event: Optional[str] = None,
    data: Optional[Dict[str, Any]] = None,
    msg: Optional[str] = None,
):
    """Standardised response format for Titan Core v1."""
    return {
        "ok": ok,
        "session_id": session_id,
        "event": event,
        "data": data or {},
        "msg": msg,
        "meta": {
            "version": API_VERSION,
            "timestamp": time.time(),
        },
    }


# =====================================================
# Logging Layer v1 (safe, lightweight)
# =====================================================

def log(msg: str):
    """Simple safe logger."""
    print(f"[TITAN-CORE] {msg}")


# =====================================================
# Validation Layer v1
# =====================================================

def validate_session_id(session_id: Optional[str]):
    if session_id is None or not isinstance(session_id, str) or session_id.strip() == "":
        return "Invalid session_id: must be a non-empty string."
    return None


def validate_event_type(event_type: Optional[str]):
    if event_type is None or not isinstance(event_type, str) or event_type.strip() == "":
        return "Invalid event_type: must be a non-empty string."
    return None


def validate_timestamp(timestamp: Any):
    if not isinstance(timestamp, (int, float)):
        return "Invalid timestamp: must be a number."
    if timestamp < 0:
        return "Invalid timestamp: must be >= 0."
    if math.isnan(timestamp) or math.isinf(timestamp):
        return "Invalid timestamp: must be a finite number."
    return None


def validate_signal(name: str, value: Any):
    """Validate simple HALO float inputs."""
    if value is None:
        return None  # Optional field
    if not isinstance(value, (int, float)):
        return f"Invalid {name}: must be a number."
    if value < 0:
        return f"Invalid {name}: must be >= 0."
    if math.isnan(value) or math.isinf(value):
        return f"Invalid {name}: must be a finite number."
    return None


# =====================================================
# Internal HALO Engine (low-resolution v1)
# =====================================================

@dataclass
class HaloSessionState:
    session_id: str
    event_count: int = 0
    friction_values: List[float] = field(default_factory=list)
    hesitation_values: List[float] = field(default_factory=list)
    pace_values: List[float] = field(default_factory=list)

    def record(self, friction, hesitation, pace):
        self.event_count += 1

        if friction is not None:
            self.friction_values.append(friction)
        if hesitation is not None:
            self.hesitation_values.append(hesitation)
        if pace is not None:
            self.pace_values.append(pace)

    def summary(self) -> Dict[str, Optional[float]]:
        return {
            "events_count": self.event_count,
            "average_friction": statistics.mean(self.friction_values) if self.friction_values else None,
            "average_hesitation": statistics.mean(self.hesitation_values) if self.hesitation_values else None,
            "average_pace": statistics.mean(self.pace_values) if self.pace_values else None,
        }


class HaloEngine:
    def __init__(self):
        self.sessions: Dict[str, HaloSessionState] = {}

    def start(self, session_id: str):
        if session_id not in self.sessions:
            self.sessions[session_id] = HaloSessionState(session_id=session_id)

    def record_event(self, session_id, friction, hesitation, pace):
        if session_id not in self.sessions:
            self.start(session_id)

        state = self.sessions[session_id]
        state.record(friction, hesitation, pace)

        return state.summary()

    def end(self, session_id):
        if session_id not in self.sessions:
            return None
        return self.sessions[session_id].summary()


halo_engine = HaloEngine()


# =====================================================
# Pydantic Models
# =====================================================

class StartSessionRequest(BaseModel):
    session_id: str
    user_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class EventContext(BaseModel):
    page: Optional[str] = None
    element: Optional[str] = None
    extra: Optional[Dict[str, Any]] = None


class EventRequest(BaseModel):
    session_id: str
    event_type: str
    timestamp: float
    friction: Optional[float] = None
    hesitation: Optional[float] = None
    pace: Optional[float] = None
    context: Optional[EventContext] = None


class EndSessionRequest(BaseModel):
    session_id: str
    metadata: Optional[Dict[str, Any]] = None
    include_summary: bool = True


# =====================================================
# Core Endpoints (TRF-1 + Validation + Logging)
# =====================================================

@router.get("/health", operation_id="healthcheck_v1")
async def health():
    return trf(msg="ok")


@router.get("/status", operation_id="status_v1")
async def status():
    return trf(
        data={
            "service": "titan-x-core",
            "version": API_VERSION,
            "mode": "dev",
        }
    )


@router.post("/v1/start", operation_id="start_session_v1")
async def start_session(payload: StartSessionRequest):

    err = validate_session_id(payload.session_id)
    if err:
        return trf(ok=False, msg=err)

    halo_engine.start(payload.session_id)

    log(f"Session started: {payload.session_id}")

    return trf(
        session_id=payload.session_id,
        event="session_started",
        data={"user_id": payload.user_id},
    )


@router.post("/v1/event", operation_id="record_event_v1")
async def record_event(payload: EventRequest):

    err = validate_session_id(payload.session_id) \
        or validate_event_type(payload.event_type) \
        or validate_timestamp(payload.timestamp) \
        or validate_signal("friction", payload.friction) \
        or validate_signal("hesitation", payload.hesitation) \
        or validate_signal("pace", payload.pace)

    if err:
        return trf(ok=False, session_id=payload.session_id, event=payload.event_type, msg=err)

    rolling = halo_engine.record_event(
        session_id=payload.session_id,
        friction=payload.friction,
        hesitation=payload.hesitation,
        pace=payload.pace,
    )

    log(f"Event: {payload.event_type} | Session: {payload.session_id} | Count: {rolling['events_count']}")

    return trf(
        session_id=payload.session_id,
        event=payload.event_type,
        data=rolling,
    )


@router.post("/v1/end", operation_id="end_session_v1")
async def end_session(payload: EndSessionRequest):

    err = validate_session_id(payload.session_id)
    if err:
        return trf(ok=False, msg=err)

    summary = halo_engine.end(payload.session_id)

    if summary is None:
        return trf(ok=False, session_id=payload.session_id, msg="Session not found.")

    log(f"Session ended: {payload.session_id} | Total events: {summary['events_count']}")

    if not payload.include_summary:
        return trf(session_id=payload.session_id, event="session_ended")

    return trf(
        session_id=payload.session_id,
        event="session_ended",
        data=summary,
    )
