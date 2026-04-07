from sqlalchemy import Column, Integer, ForeignKey, String
from app.core.database import Base
class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"))
    text = Column(String)