from sqlalchemy.orm import Session
from typing import cast

from app.models.answer import Answer


def create_answer(db: Session, question_id: int, answer_text: str, score: int = 0) -> Answer:
    answer = Answer(question_id=question_id, answer_text=answer_text, score=score)
    db.add(answer)
    db.commit()
    db.refresh(answer)
    return answer


def get_answer_by_question_id(db: Session, question_id: int) -> Answer | None:
    answer = db.query(Answer).filter(Answer.question_id == question_id).first()
    return cast(Answer | None, answer)


