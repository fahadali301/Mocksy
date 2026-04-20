from sqlalchemy.orm import Session

from app.models.question import Question


def create_question(db: Session, interview_id: int, text: str) -> Question:
    question = Question(interview_id=interview_id, text=text)
    db.add(question)
    db.commit()
    db.refresh(question)
    return question


def get_questions_for_interview(db: Session, interview_id: int) -> list[Question]:
    return (
        db.query(Question)
        .filter(Question.interview_id == interview_id)
        .order_by(Question.id.asc())
        .all()
    )


def get_latest_question(db: Session, interview_id: int) -> Question | None:
    return (
        db.query(Question)
        .filter(Question.interview_id == interview_id)
        .order_by(Question.id.desc())
        .first()
    )

