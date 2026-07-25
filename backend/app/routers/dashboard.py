from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import Integer, cast, func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Attempt, AttemptOutcome, Child, ExerciseTemplate, GameSession
from app.schemas import CategoryAccuracy, DashboardOut, FlaggedGap, WeeklyPoint

router = APIRouter(tags=["dashboard"])

SUCCESS_OUTCOMES = (AttemptOutcome.passed, AttemptOutcome.caught)
MIN_ATTEMPTS_FOR_GAP = 5
GAP_THRESHOLD = 55.0


def _success_flag():
    """1/0 per row depending on whether the attempt succeeded — lets us sum
    it directly instead of doing a second filtered count query."""
    return cast(Attempt.outcome.in_(SUCCESS_OUTCOMES), Integer)


def _accuracy_by(db: Session, child_id: int, column) -> list[CategoryAccuracy]:
    rows = (
        db.query(
            column.label("category"),
            func.count(Attempt.id).label("attempts"),
            func.sum(_success_flag()).label("successes"),
        )
        .join(GameSession, Attempt.session_id == GameSession.id)
        .filter(GameSession.child_id == child_id, column.isnot(None))
        .group_by(column)
        .all()
    )
    out = []
    for r in rows:
        attempts = r.attempts or 0
        successes = r.successes or 0
        accuracy = round((successes / attempts) * 100, 1) if attempts else 0.0
        out.append(CategoryAccuracy(category=r.category, accuracy=accuracy, attempts=attempts))
    return sorted(out, key=lambda c: c.accuracy)


@router.get("/children/{child_id}/dashboard", response_model=DashboardOut)
def get_dashboard(child_id: int, db: Session = Depends(get_db)):
    child = db.query(Child).get(child_id)
    if not child:
        raise HTTPException(status_code=404, detail="Child not found")

    sessions_count = db.query(GameSession).filter(GameSession.child_id == child_id).count()

    manner_accuracy = _accuracy_by(db, child_id, Attempt.manner)
    place_accuracy = _accuracy_by(db, child_id, Attempt.place)
    voicing_accuracy = _accuracy_by(db, child_id, Attempt.voicing)

    # Weekly overall accuracy trend, most recent 6 weeks that have data.
    weekly_rows = (
        db.query(
            func.date_trunc("week", Attempt.created_at).label("week"),
            func.count(Attempt.id).label("attempts"),
            func.sum(_success_flag()).label("successes"),
        )
        .join(GameSession, Attempt.session_id == GameSession.id)
        .filter(GameSession.child_id == child_id)
        .group_by("week")
        .order_by("week")
        .all()
    )
    progress_over_time = [
        WeeklyPoint(
            week=row.week.strftime("Wk of %b %-d") if row.week else "\u2014",
            accuracy=round((row.successes / row.attempts) * 100, 1) if row.attempts else 0.0,
            attempts=row.attempts or 0,
        )
        for row in weekly_rows[-6:]
    ]

    # Flag categories with enough data to mean something and accuracy below
    # the threshold — this is what turns raw logs into "here's what to work
    # on" instead of just a wall of numbers.
    exercises = db.query(ExerciseTemplate).all()
    candidates = (
        [(c, "Manner") for c in manner_accuracy]
        + [(c, "Place") for c in place_accuracy]
        + [(c, "Voicing") for c in voicing_accuracy]
    )

    flagged: list[FlaggedGap] = []
    for cat, dimension in candidates:
        if cat.attempts < MIN_ATTEMPTS_FOR_GAP or cat.accuracy >= GAP_THRESHOLD:
            continue
        severity = "high" if cat.accuracy < 35 else "medium" if cat.accuracy < 50 else "low"
        matching_exercise = next(
            (e for e in exercises if cat.category in (e.target_categories or [])), None
        )
        flagged.append(
            FlaggedGap(
                id=f"gap-{dimension.lower()}-{cat.category.lower()}",
                title=f"{cat.category} ({dimension.lower()})",
                detail=(
                    f"{cat.accuracy:.0f}% accuracy across {cat.attempts} attempts \u2014 "
                    f"below the level where this is likely just normal variation."
                ),
                severity=severity,
                assigned_exercise=matching_exercise.title if matching_exercise else None,
            )
        )
    flagged.sort(key=lambda g: {"high": 0, "medium": 1, "low": 2}[g.severity])

    return DashboardOut(
        child=child,
        sessions_count=sessions_count,
        manner_accuracy=manner_accuracy,
        place_accuracy=place_accuracy,
        voicing_accuracy=voicing_accuracy,
        progress_over_time=progress_over_time,
        flagged_gaps=flagged[:3],
    )
