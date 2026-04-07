from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.auth import hash_password

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, name: str, email: str, password: str):
    user = User(
        name=name,
        email=email,
        password=hash_password(password)
    )
    existing = get_user_by_email(db, user.email)

    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    db.add(user)
    db.commit()
    db.refresh(user)
    return user