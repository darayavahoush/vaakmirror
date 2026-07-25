from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import AssignmentStatus, Child, ExerciseAssignment, ExerciseTemplate
from app.schemas import AssignmentStatusUpdate, ExerciseAssignmentOut, ExerciseTemplateOut

router = APIRouter(tags=["exercises"])


@router.get("/exercises", response_model=list[ExerciseTemplateOut])
def list_exercise_library(db: Session = Depends(get_db)):
    return db.query(ExerciseTemplate).all()


@router.get("/children/{child_id}/exercises", response_model=list[ExerciseAssignmentOut])
def list_child_exercises(child_id: int, db: Session = Depends(get_db)):
    return (
        db.query(ExerciseAssignment)
        .options(joinedload(ExerciseAssignment.exercise))
        .filter(ExerciseAssignment.child_id == child_id)
        .order_by(ExerciseAssignment.assigned_at.desc())
        .all()
    )


@router.post("/children/{child_id}/exercises/{exercise_id}/assign", response_model=ExerciseAssignmentOut)
def assign_exercise(child_id: int, exercise_id: int, db: Session = Depends(get_db)):
    child = db.query(Child).get(child_id)
    if not child:
        raise HTTPException(status_code=404, detail="Child not found")
    exercise = db.query(ExerciseTemplate).get(exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")

    existing = (
        db.query(ExerciseAssignment)
        .filter(
            ExerciseAssignment.child_id == child_id,
            ExerciseAssignment.exercise_id == exercise_id,
            ExerciseAssignment.status != AssignmentStatus.completed,
        )
        .first()
    )
    if existing:
        return existing

    assignment = ExerciseAssignment(child_id=child_id, exercise_id=exercise_id)
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment


@router.patch("/exercise-assignments/{assignment_id}", response_model=ExerciseAssignmentOut)
def update_assignment_status(assignment_id: int, payload: AssignmentStatusUpdate, db: Session = Depends(get_db)):
    assignment = db.query(ExerciseAssignment).get(assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    assignment.status = payload.status
    if payload.status == AssignmentStatus.completed:
        assignment.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(assignment)
    return assignment
