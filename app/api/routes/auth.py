from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import verify_password, create_token
from app.crud.user import get_user_by_email, create_user
from app.schemas.user import Token, UserCreateSchema, UserLogin, UserResponseSchema

router = APIRouter(prefix="/auth", tags=["Auth"])



@router.post("/register", response_model=UserResponseSchema)
def register(user: UserCreateSchema, db: Session = Depends(get_db)):
    return create_user(db, user.name, user.email, user.password)

@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, user.email)

    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token({"sub": db_user.email, "user_id": db_user.id})

    return {"access_token": token, "token_type": "bearer"}

