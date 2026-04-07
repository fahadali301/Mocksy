from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import os, shutil
from app.core.database import get_db
 # JWT middleware
import crud.cv as cv_crud
from crud.auth import get_current_user

router = APIRouter(prefix="/cv", tags=["CV"])
UPLOAD_DIR = "uploads/cvs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_cv(file: UploadFile = File(...), db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Save file
    file_path = os.path.join(UPLOAD_DIR, f"{current_user}_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)


    cv = cv_crud.create_cv(db=db, user_id=current_user, file_path=file_path)

    return {"id": cv.id, "file_path": cv.file_path}