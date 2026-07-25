from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Attempt, Child, GameSession
from app.schemas import AttemptCreate, AttemptOut, SessionCreate, SessionOut

router = APIRouter(tags=["sessions"])


@router.post("/children/{child_id}/sessions", response_model=SessionOut)
def create_session(child_id: int, payload: SessionCreate, db: Session = Depends(get_db)):
    child = db.query(Child).get(child_id)
    if not child:
        raise HTTPException(status_code=404, detail="Child not found")

    session = GameSession(child_id=child_id, game=payload.game)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.post("/sessions/{session_id}/attempts", response_model=AttemptOut)
def log_attempt(session_id: int, payload: AttemptCreate, db: Session = Depends(get_db)):
    session = db.query(GameSession).get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    attempt = Attempt(session_id=session_id, **payload.model_dump())
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return attempt


@router.patch("/sessions/{session_id}/end", response_model=SessionOut)
def end_session(session_id: int, db: Session = Depends(get_db)):
    session = db.query(GameSession).get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.ended_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(session)
    return session
