from sqlalchemy import Column, Integer, ForeignKey, String
from app.core.database import Base


class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey("questions.id"))
    answer_text = Column(String)
    score = Column(Integer)