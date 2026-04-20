from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import os
import uuid

from app.core.database import get_db
from app.services.cv_parser import CVParserService
import app.crud.cv as cv_crud
from app.crud.auth import get_current_user

router = APIRouter(prefix="/cv", tags=["CV"])

UPLOAD_DIR = "uploads/cvs"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_cv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # ✅ Validate file type
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # ✅ Generate unique filename (avoid overwrite)
    unique_filename = f"{current_user}_{uuid.uuid4().hex}.pdf"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    # ✅ Save file
    try:
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to save file")

    # ✅ Extract text using parser service
    try:
        extracted_text = CVParserService.extract_text(file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # ✅ Save CV in DB (with extracted text)
    cv = cv_crud.create_cv(
        db=db,
        user_id=current_user,
        file_path=file_path,
        extracted_data={"text": extracted_text}
    )

    return {
        "id": cv.id,
        "file_path": cv.file_path,
        "text_preview": extracted_text[:300],
        "message": "CV uploaded and parsed. Start interview to get AI questions."
    }


@router.get("/")
def list_cvs(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    cvs = cv_crud.get_user_cvs(db, current_user)
    return [
        {
            "id": cv.id,
            "file_path": cv.file_path,
            "text_preview": (cv.extracted_data or {}).get("text", "")[:300],
        }
        for cv in cvs
    ]