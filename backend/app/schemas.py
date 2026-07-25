from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models import AssignmentStatus, AttemptOutcome, GameName


# --- Children ---


class ChildCreate(BaseModel):
    name: str
    age: Optional[int] = None


class ChildOut(BaseModel):
    id: int
    name: str
    age: Optional[int]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Sessions & attempts ---


class SessionCreate(BaseModel):
    game: GameName


class SessionOut(BaseModel):
    id: int
    child_id: int
    game: GameName
    started_at: datetime
    ended_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class AttemptCreate(BaseModel):
    sound_id: Optional[str] = None
    place: Optional[str] = None
    manner: Optional[str] = None
    voicing: Optional[str] = None
    outcome: AttemptOutcome
    score: Optional[float] = None


class AttemptOut(BaseModel):
    id: int
    session_id: int
    sound_id: Optional[str]
    place: Optional[str]
    manner: Optional[str]
    voicing: Optional[str]
    outcome: AttemptOutcome
    score: Optional[float]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Dashboard ---


class CategoryAccuracy(BaseModel):
    category: str
    accuracy: float
    attempts: int


class WeeklyPoint(BaseModel):
    week: str
    accuracy: float
    attempts: int


class FlaggedGap(BaseModel):
    id: str
    title: str
    detail: str
    severity: str  # 'high' | 'medium' | 'low'
    assigned_exercise: Optional[str] = None


class DashboardOut(BaseModel):
    child: ChildOut
    sessions_count: int
    manner_accuracy: list[CategoryAccuracy]
    place_accuracy: list[CategoryAccuracy]
    voicing_accuracy: list[CategoryAccuracy]
    progress_over_time: list[WeeklyPoint]
    flagged_gaps: list[FlaggedGap]


# --- Exercises ---


class ExerciseTemplateOut(BaseModel):
    id: int
    title: str
    description: str
    duration_label: str
    target_categories: list[str]

    model_config = ConfigDict(from_attributes=True)


class ExerciseAssignmentOut(BaseModel):
    id: int
    status: AssignmentStatus
    assigned_at: datetime
    completed_at: Optional[datetime]
    exercise: ExerciseTemplateOut

    model_config = ConfigDict(from_attributes=True)


class AssignmentStatusUpdate(BaseModel):
    status: AssignmentStatus
