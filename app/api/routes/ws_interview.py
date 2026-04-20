import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from jose import JWTError, jwt

from app.core.database import SessionLocal
from app.crud import answer as answer_crud
from app.crud import cv as cv_crud
from app.crud import interview as interview_crud
from app.crud import question as question_crud
from app.services.ai_service import AIService
import os
# Reuse the same secret / algorithm used by the REST auth layer.
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

router = APIRouter()


# ── helpers ───────────────────────────────────────────────────────────────────

def _authenticate(token: str) -> int | None:
    """Decode a JWT and return the user_id, or None on failure."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("user_id")
    except JWTError:
        return None


def _build_history(db, interview_id: int) -> list[dict]:
    """Build the Q/A history list for an interview (same logic as REST route)."""
    history: list[dict] = []
    questions = question_crud.get_questions_for_interview(db, interview_id)
    for question in questions:
        answer = answer_crud.get_answer_by_question_id(db, question.id)
        if answer and answer.answer_text:
            history.append({"question": question.text, "answer": answer.answer_text})
    return history


# ── WebSocket endpoint ────────────────────────────────────────────────────────

@router.websocket("/ws/interview")
async def interview_ws(websocket: WebSocket):
    # ---------- authenticate via query-param token ----------
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001, reason="Missing token")
        return

    user_id = _authenticate(token)
    if user_id is None:
        await websocket.close(code=4001, reason="Invalid token")
        return

    await websocket.accept()

    db = SessionLocal()
    interview = None
    cv_text = ""

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "detail": "Invalid JSON"})
                continue

            msg_type = msg.get("type")

            # ────────── START ──────────
            if msg_type == "start":
                cv_id = msg.get("cv_id")
                role = msg.get("role")

                cv = cv_crud.get_cv_by_id(db, cv_id)
                if not cv or cv.user_id != user_id:
                    await websocket.send_json({"type": "error", "detail": "CV not found"})
                    continue

                cv_text = (cv.extracted_data or {}).get("text", "")
                if not cv_text.strip():
                    await websocket.send_json({"type": "error", "detail": "CV has no extracted text"})
                    continue

                interview = await asyncio.to_thread(
                    interview_crud.create_interview, db, user_id, cv.id, role
                )

                # Stream the first question
                await websocket.send_json({"type": "question_started"})

                prompt = _build_initial_prompt(cv_text, role)
                full_question = await _stream_to_client(websocket, prompt)

                await asyncio.to_thread(
                    question_crud.create_question, db, interview.id, full_question
                )

                await websocket.send_json({
                    "type": "question_complete",
                    "text": full_question,
                    "interview_id": interview.id,
                    "powered_by": AIService.get_last_provider(),
                })

            # ────────── ANSWER ──────────
            elif msg_type == "answer":
                if not interview:
                    await websocket.send_json({"type": "error", "detail": "Interview not started"})
                    continue

                answer_text = (msg.get("text") or "").strip()
                if not answer_text:
                    await websocket.send_json({"type": "error", "detail": "Empty answer"})
                    continue

                # Save the answer
                latest_q = await asyncio.to_thread(
                    question_crud.get_latest_question, db, interview.id
                )
                if not latest_q:
                    await websocket.send_json({"type": "error", "detail": "No active question"})
                    continue

                existing = await asyncio.to_thread(
                    answer_crud.get_answer_by_question_id, db, latest_q.id
                )
                if existing:
                    await websocket.send_json({"type": "error", "detail": "Already answered"})
                    continue

                await asyncio.to_thread(
                    answer_crud.create_answer, db, latest_q.id, answer_text
                )

                # Build history and stream the follow-up question
                history = await asyncio.to_thread(_build_history, db, interview.id)
                role = interview.role

                await websocket.send_json({"type": "question_started"})

                prompt = _build_followup_prompt(cv_text, history, role)
                full_question = await _stream_to_client(websocket, prompt)

                await asyncio.to_thread(
                    question_crud.create_question, db, interview.id, full_question
                )

                await websocket.send_json({
                    "type": "question_complete",
                    "text": full_question,
                    "interview_id": interview.id,
                    "powered_by": AIService.get_last_provider(),
                })

            # ────────── EXIT ──────────
            elif msg_type == "exit":
                if not interview:
                    await websocket.send_json({"type": "error", "detail": "Interview not started"})
                    continue

                history = await asyncio.to_thread(_build_history, db, interview.id)
                if not history:
                    await websocket.send_json({"type": "error", "detail": "No answers to evaluate"})
                    continue

                await websocket.send_json({"type": "evaluating"})

                result = await asyncio.to_thread(
                    AIService.evaluate_interview_session,
                    cv_text=cv_text,
                    history=history,
                    role=interview.role,
                )

                await asyncio.to_thread(
                    interview_crud.finalize_interview,
                    db,
                    interview,
                    final_score=result.get("overall_score"),
                    final_feedback=result.get("summary"),
                )

                await websocket.send_json({
                    "type": "result",
                    "data": result,
                    "powered_by": AIService.get_last_provider(),
                })
                # Interview complete — close gracefully
                await websocket.close()
                break

            else:
                await websocket.send_json({"type": "error", "detail": f"Unknown type: {msg_type}"})

    except WebSocketDisconnect:
        pass  # Client disconnected — nothing to do
    except Exception as exc:
        try:
            await websocket.send_json({"type": "error", "detail": str(exc)})
        except Exception:
            pass
    finally:
        db.close()


# ── Prompt builders (mirror AIService but return raw prompts for streaming) ──

def _build_initial_prompt(cv_text: str, role: str | None) -> str:
    role_hint = role.strip() if role else "the candidate's likely target role"
    return f"""You are a professional interviewer.

Generate exactly ONE concise interview question based on this CV for {role_hint}.
The question should be specific to the candidate's profile and experience.
Return only the question text. Do not return JSON, numbering, or explanation.

CV:
{cv_text}
"""


def _build_followup_prompt(cv_text: str, history: list[dict], role: str | None) -> str:
    role_hint = role.strip() if role else "the candidate's likely target role"
    history_text = "\n".join(
        [
            f"Q{i + 1}: {item.get('question', '').strip()}\nA{i + 1}: {item.get('answer', '').strip()}"
            for i, item in enumerate(history)
        ]
    )
    return f"""You are a professional interviewer running a live interview for {role_hint}.

Use the candidate CV and previous Q/A turns to generate exactly ONE next follow-up question.
The question should probe depth, clarify weak points, or go deeper into relevant experience.
Do not repeat previous questions.
Return only the question text. Do not return JSON, numbering, or explanation.

CV:
{cv_text}

Interview so far:
{history_text}
"""


async def _stream_to_client(websocket: WebSocket, prompt: str) -> str:
    """Stream tokens from AIService to the WebSocket client, return full text."""
    full_text = ""

    def _generate():
        return list(AIService.stream_model(prompt))

    tokens = await asyncio.to_thread(_generate)
    for token in tokens:
        full_text += token
        await websocket.send_json({"type": "token", "text": token})

    return full_text.strip().strip('"').strip()
