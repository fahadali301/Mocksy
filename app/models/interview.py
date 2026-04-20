from sqlalchemy import Column, Integer, ForeignKey, String
from app.core.database import Base


class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    cv_id = Column(Integer, ForeignKey("cvs.id"))
    role = Column(String)
    status = Column(String, default="active", nullable=False)
    final_score = Column(Integer, nullable=True)
    final_feedback = Column(String, nullable=True)
