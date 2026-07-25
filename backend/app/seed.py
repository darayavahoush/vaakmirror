"""
Run once after setting up Postgres:

    python -m app.seed

Creates all tables (via SQLAlchemy metadata, no Alembic migration system
set up yet — fine for a project at this stage; worth introducing Alembic
once the schema needs to evolve without dropping data) and seeds the
exercise library plus one demo child so the dashboard isn't empty on first
run.
"""

from app.database import Base, SessionLocal, engine
from app.models import Child, ExerciseTemplate

EXERCISE_LIBRARY = [
    dict(
        title="Breath-stream & Lip-friction Drills",
        description="Guided breath control and lip-shaping drills to build the airflow precision fricative sounds need.",
        duration_label="4 min",
        target_categories=["Fricative"],
    ),
    dict(
        title="Tongue-tip Elevation & Alveolar Tapping",
        description="Tongue-tip lift and tapping practice against the alveolar ridge, building range for t/d/s/z/n/l sounds.",
        duration_label="5 min",
        target_categories=["Alveolar", "Plosive"],
    ),
    dict(
        title="Humming to Voiced-sound Bridge",
        description="Hums transition into voiced consonants to build vocal cord engagement for voiced sound pairs.",
        duration_label="3 min",
        target_categories=["Voiced"],
    ),
    dict(
        title="Cheek & Jaw Warm-up Massage",
        description="A gentle warm-up massage sequence for cheeks and jaw, used at the start of any session.",
        duration_label="3 min",
        target_categories=["General"],
    ),
    dict(
        title="Lip Rounding for Sh / Ch / J",
        description="Practice rounding and forward lip projection needed for post-alveolar sounds.",
        duration_label="4 min",
        target_categories=["Post-alveolar", "Affricate"],
    ),
]


def run():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        if db.query(ExerciseTemplate).count() == 0:
            db.add_all([ExerciseTemplate(**e) for e in EXERCISE_LIBRARY])
            print(f"Seeded {len(EXERCISE_LIBRARY)} exercise templates.")

        if db.query(Child).count() == 0:
            db.add(Child(name="Demo Child", age=6))
            print("Seeded one demo child (id will be 1).")

        db.commit()
    finally:
        db.close()

    print("Done.")


if __name__ == "__main__":
    run()
