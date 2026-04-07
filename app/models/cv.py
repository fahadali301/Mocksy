from sqlalchemy import Column, Integer, ForeignKey, String, JSON
from app.core.database import Base

class CV(Base):
    __tablename__ = "cvs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    file_path = Column(String)
    extracted_data = Column(JSON)