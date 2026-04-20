from sqlalchemy.orm import Session

from app.models.interview import Interview


def create_interview(db: Session, user_id: int, cv_id: int, role: str | None = None) -> Interview:
    interview = Interview(user_id=user_id, cv_id=cv_id, role=role, status="active")
    db.add(interview)
    db.commit()
    db.refresh(interview)
    return interview


def get_user_interview(db: Session, interview_id: int, user_id: int) -> Interview | None:
    return (
        db.query(Interview)
        .filter(Interview.id == interview_id, Interview.user_id == user_id)
        .first()
    )


def finalize_interview(
    db: Session,
    interview: Interview,
    final_score: int | None,
    final_feedback: str | None,
) -> Interview:
    interview.status = "completed"
    interview.final_score = final_score
    interview.final_feedback = final_feedback
    db.commit()
    db.refresh(interview)
    return interview

