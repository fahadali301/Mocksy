from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.auth import router as auth_router
from app.api.routes.cv import router as cv_router
from app.api.routes.interview import router as interview_router
from app.api.routes.ws_interview import router as ws_router
from app.core.database import Base, engine

# Import models so SQLAlchemy registers all tables on Base.metadata.
from app.models import answer, cv, interview, question, report, user  # noqa: F401

Base.metadata.create_all(bind=engine)

app = FastAPI()

# ✅ Add CORS middleware for React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(cv_router)
app.include_router(interview_router)
app.include_router(ws_router)
