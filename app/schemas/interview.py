from pydantic import BaseModel, Field


class InterviewStartRequest(BaseModel):
    cv_id: int
    role: str | None = None


class InterviewStartResponse(BaseModel):
    interview_id: int
    status: str
    next_question: str
    powered_by: str = "unknown"


class InterviewTurnRequest(BaseModel):
    interview_id: int
    answer: str


class InterviewEvaluationResult(BaseModel):
    overall_score: int | float | None = None
    summary: str = ""
    strengths: list[str] = Field(default_factory=list)
    improvements: list[str] = Field(default_factory=list)


class InterviewContinueResponse(BaseModel):
    interview_id: int
    status: str
    next_question: str
    powered_by: str = "unknown"


class InterviewExitResponse(BaseModel):
    interview_id: int
    status: str
    result: InterviewEvaluationResult
    powered_by: str = "unknown"

