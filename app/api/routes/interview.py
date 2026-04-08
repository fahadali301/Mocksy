from fastapi import APIRouter
from pydantic import BaseModel

from app.services.ai_service import AIService

router = APIRouter(prefix="/interview", tags=["Interview"])


class AnswerRequest(BaseModel):
	question: str
	answer: str


@router.post("/interview")
def evaluate_answer(payload: AnswerRequest):

	return AIService.evaluate_answer(payload.question, payload.answer)

