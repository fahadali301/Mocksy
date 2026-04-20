from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import os
import uuid
from app.core.database import get_db
from app.services.cv_parser import CVParserService
import app.crud.cv as cv_crud
from app.crud.auth import get_current_user

router = APIRouter(prefix="/cv", tags=["CV"])

# ✅ FIXED: Use /tmp directory for Vercel serverless
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/tmp/uploads/cvs")


# ✅ FIXED: Create directory on-demand, not at module import
def ensure_upload_dir():
    """Create upload directory if it doesn't exist"""
    if not os.path.exists(UPLOAD_DIR):
        try:
            os.makedirs(UPLOAD_DIR, exist_ok=True)
        except OSError as e:
            # Log the error but don't crash
            print(f"Warning: Could not create upload directory: {e}")
    return UPLOAD_DIR


@router.post("/upload")
async def upload_cv(
        file: UploadFile = File(...),
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    # ✅ Ensure directory exists before upload
    upload_dir = ensure_upload_dir()

    # Validate file type
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Generate unique filename (avoid overwrite)
    unique_filename = f"{current_user}_{uuid.uuid4().hex}.pdf"
    file_path = os.path.join(upload_dir, unique_filename)

    # Save file
    try:
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Extract text using parser service
    try:
        extracted_text = CVParserService.extract_text(file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse CV: {str(e)}")

    # Save CV in DB (with extracted text)
    try:
        cv = cv_crud.create_cv(
            db=db,
            user_id=current_user,
            file_path=file_path,
            extracted_data={"text": extracted_text}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save CV to database: {str(e)}")

    return {
        "id": cv.id,
        "file_path": cv.file_path,
        "text_preview": extracted_text[:300] if extracted_text else "",
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