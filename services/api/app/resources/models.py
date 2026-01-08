from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class ProfileResource(BaseModel):
    """Canonical onboarding profile resource.

    This is the source of truth for agent-visible fields and UI generation.
    """

    firstName: str = Field(default="", description="Given name")
    lastName: str = Field(default="", description="Family name")
    email: str = Field(default="", description="Email address")
    phone: str = Field(default="", description="Phone number")

    goals: str = Field(default="", description="High level training goals")
    experience: str = Field(default="", description="Training experience level")
    constraints: str = Field(default="", description="Schedule/time constraints")
    equipment: str = Field(default="", description="Equipment access")
    injuriesOrRiskFlags: str = Field(default="", description="Injuries and risk flags")
    dietPrefs: str = Field(default="", description="Diet preferences")

    metrics: "ProfileMetrics" = Field(default_factory=lambda: ProfileMetrics())


class ProfileMetrics(BaseModel):
    age: str = Field(default="", description="Age")
    height: str = Field(default="", description="Height")
    weight: str = Field(default="", description="Body weight")


class GoalResource(BaseModel):
    type: Literal["body_weight", "strength", "conditioning", "performance", "other"] = Field(
        description="Goal category"
    )
    title: str = Field(description="Short label")
    targetDate: Optional[str] = Field(default=None, description="Target date (YYYY-MM-DD)")
    status: Literal["active", "paused", "completed", "canceled"] = Field(
        default="active", description="Goal status"
    )


class NoteResource(BaseModel):
    type: Literal["restriction", "preference", "equipment", "injury", "general"] = Field(
        description="Note category"
    )
    title: Optional[str] = Field(default=None, description="Optional title")
    bodyMd: str = Field(description="Markdown content")
