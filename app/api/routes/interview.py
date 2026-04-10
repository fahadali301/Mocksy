from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud.auth import get_current_user
from app.crud import answer as answer_crud
from app.crud import cv as cv_crud
from app.crud import interview as interview_crud
from app.crud import question as question_crud
from app.schemas.interview import (
	InterviewContinueResponse,
	InterviewExitResponse,
	InterviewStartRequest,
	InterviewStartResponse,
	InterviewTurnRequest,
)
from app.services.ai_service import AIService

router = APIRouter(prefix="/interview", tags=["Interview"])


def _build_history(db: Session, interview_id: int) -> list[dict]:
	history: list[dict] = []
	questions = question_crud.get_questions_for_interview(db, interview_id)
	for question in questions:
		answer = answer_crud.get_answer_by_question_id(db, question.id)
		if answer and answer.answer_text:
			history.append({"question": question.text, "answer": answer.answer_text})
	return history


@router.post("/start", response_model=InterviewStartResponse)
def start_interview(
	payload: InterviewStartRequest,
	db: Session = Depends(get_db),
	current_user: int = Depends(get_current_user),
):
	cv = cv_crud.get_cv_by_id(db, payload.cv_id)
	if not cv or cv.user_id != current_user:
		raise HTTPException(status_code=404, detail="CV not found")

	cv_text = (cv.extracted_data or {}).get("text", "")
	if not cv_text.strip():
		raise HTTPException(status_code=400, detail="CV has no extracted text")

	interview = interview_crud.create_interview(
		db=db,
		user_id=current_user,
		cv_id=cv.id,
		role=payload.role,
	)

	try:
		next_question = AIService.generate_initial_question(cv_text=cv_text, role=payload.role)
	except Exception as exc:
		raise HTTPException(status_code=500, detail=str(exc))
	question_crud.create_question(db, interview.id, next_question)

	return {
		"interview_id": interview.id,
		"status": interview.status,
		"next_question": next_question,
		"powered_by": AIService.get_last_provider(),
	}


@router.post("/turn", response_model=InterviewContinueResponse | InterviewExitResponse)
def submit_turn(
	payload: InterviewTurnRequest,
	db: Session = Depends(get_db),
	current_user: int = Depends(get_current_user),
):
	interview = interview_crud.get_user_interview(db, payload.interview_id, current_user)
	if not interview:
		raise HTTPException(status_code=404, detail="Interview not found")

	if interview.status == "completed":
		raise HTTPException(status_code=400, detail="Interview is already completed")

	latest_question = question_crud.get_latest_question(db, interview.id)
	if not latest_question:
		raise HTTPException(status_code=400, detail="No active question found")

	if answer_crud.get_answer_by_question_id(db, latest_question.id):
		raise HTTPException(
			status_code=400,
			detail="Current question is already answered. Wait for next question.",
		)

	answer_text = payload.answer.strip()
	if not answer_text:
		raise HTTPException(status_code=400, detail="Answer cannot be empty")

	if answer_text.lower() == "exit":
		history = _build_history(db, interview.id)
		if not history:
			raise HTTPException(status_code=400, detail="No answers found to evaluate")

		cv = cv_crud.get_cv_by_id(db, interview.cv_id)
		cv_text = ((cv.extracted_data or {}) if cv else {}).get("text", "")

		try:
			final_result = AIService.evaluate_interview_session(
				cv_text=cv_text,
				history=history,
				role=interview.role,
			)
		except Exception as exc:
			raise HTTPException(status_code=500, detail=str(exc))
		interview_crud.finalize_interview(
			db,
			interview,
			final_score=final_result.get("overall_score"),
			final_feedback=final_result.get("summary"),
		)
		return {
			"interview_id": interview.id,
			"status": "completed",
			"result": final_result,
			"powered_by": AIService.get_last_provider(),
		}

	answer_crud.create_answer(db, latest_question.id, answer_text)

	cv = cv_crud.get_cv_by_id(db, interview.cv_id)
	cv_text = ((cv.extracted_data or {}) if cv else {}).get("text", "")
	history = _build_history(db, interview.id)
	try:
		next_question = AIService.generate_followup_question(
			cv_text=cv_text,
			history=history,
			role=interview.role,
		)
	except Exception as exc:
		raise HTTPException(status_code=500, detail=str(exc))
	question_crud.create_question(db, interview.id, next_question)

	return {
		"interview_id": interview.id,
		"status": "active",
		"next_question": next_question,
		"powered_by": AIService.get_last_provider(),
	}

