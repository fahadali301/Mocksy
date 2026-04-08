from sqlalchemy.orm import Session
from app.models.cv import CV

def create_cv(db: Session, user_id: int, file_path: str, extracted_data: dict):
    cv = CV(user_id=user_id, file_path=file_path, extracted_data=extracted_data)
    db.add(cv)
    db.commit()
    db.refresh(cv)
    return cv