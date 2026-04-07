from sqlalchemy.orm import Session
from app.models.cv import CV

def create_cv(db: Session, user_id: int, file_path: str):
    cv = CV(user_id=user_id, file_path=file_path, extracted_data={})
    db.add(cv)
    db.commit()
    db.refresh(cv)
    return cv