from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class Event:
    id: str
    ts: datetime
    type: str
    payload: Dict[str, Any]
    sessionId: Optional[str] = None


def project_state(events: List[Event]) -> Dict[str, Any]:
    """Reduce events into a materialized state snapshot.

    This is intentionally minimal for Phase 1 foundation. It can evolve as new
    event types are introduced.
    """

    state: Dict[str, Any] = {
        "profile": None,
        "plan": None,
        "workout": {"active": None, "sets": []},
        "chat": {"messages": []},
    }

    for ev in events:
        t = ev.type
        p = ev.payload

        # Profile lifecycle
        # - Canonical event name: ProfileSaved
        # - Backward-compat: UserOnboarded (older DB volumes / event history)
        if t in ("ProfileSaved", "UserOnboarded"):
            state["profile"] = p
        elif t == "ProfileDeleted":
            state["profile"] = None
        elif t == "PlanGenerated":
            state["plan"] = p
        elif t == "WorkoutStarted":
            state["workout"]["active"] = p
        elif t == "SetLogged":
            state["workout"]["sets"].append(p)
        elif t == "WorkoutCompleted":
            state["workout"]["active"] = None
        elif t == "ChatMessageSent":
            # payload: { role: "user"|"assistant", text: string, ... }
            state["chat"]["messages"].append(p)

    return state


def now_utc() -> datetime:
    return datetime.now(timezone.utc)
