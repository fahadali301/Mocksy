import os

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

from app.api.routes.auth import router as auth_router
from app.api.routes.cv import router as cv_router
from app.api.routes.interview import router as interview_router
from app.api.routes.ws_interview import router as ws_router
from app.core.config import validate_environment

app = FastAPI(title="Mocksy API")

raw_origins = os.getenv("CORS_ORIGINS", "*")
cors_origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]
if not cors_origins:
    cors_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=cors_origins != ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(cv_router)
app.include_router(interview_router)
app.include_router(ws_router)


@app.on_event("startup")
def startup_validation() -> None:
    app.state.startup_issues = validate_environment()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.exception_handler(HTTPException)
async def http_exception_handler(_, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(_, __):
    return JSONResponse(
        status_code=503,
        content={"detail": "Database is temporarily unavailable. Please try again."},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(_, __):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error."},
    )


@app.get("/")
def root():
    startup_issues = getattr(app.state, "startup_issues", [])
    response = {"status": "ok", "message": "Mocksy API is running"}
    if startup_issues:
        response["status"] = "degraded"
        response["issues"] = startup_issues
    return response
