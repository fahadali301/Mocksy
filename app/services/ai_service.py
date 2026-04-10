import requests
import json
import re
import os

USE_GROQ = False

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.1-8b-instant"


class AIService:
    OLLAMA_URL = "http://localhost:11434/api/generate"
    MODEL = "llama3"
    last_provider = None  # Tracks "groq" or "ollama"

    @staticmethod
    def _extract_json(text: str):
        """Extract JSON from response, handling Markdown code blocks and whitespace."""
        text = text.strip()

        # Try to extract JSON from a Markdown code block: ```json ... ```
        match = re.search(r'```(?:json)?\s*([\s\S]*?)```', text)
        if match:
            text = match.group(1).strip()

        # Try to extract JSON from curly braces or square brackets
        # Find the first { or [ and the last } or ]
        start_idx = -1
        start_char = None
        for i, char in enumerate(text):
            if char in ('{', '['):
                start_idx = i
                start_char = char
                break

        if start_idx >= 0:
            end_char = '}' if start_char == '{' else ']'
            end_idx = text.rfind(end_char)
            if end_idx > start_idx:
                text = text[start_idx:end_idx + 1]

        return json.loads(text)

    @staticmethod
    def generate_questions(cv_text: str) -> list:
        if not cv_text or not cv_text.strip():
            raise ValueError("CV text is empty. Cannot generate questions.")

        prompt = f"""
You are a professional interviewer.

Based on the following CV, generate 5 interview questions.

Focus on:
- Skills
- Experience
- Projects

Return ONLY a JSON list like:
["Q1", "Q2", "Q3", "Q4", "Q5"]

CV:
{cv_text}
"""

        data = AIService._call_model(prompt)
        try:
            questions = AIService._extract_json(data)
            return questions
        except Exception as e:
            raise Exception(f"Failed to parse AI questions: {str(e)[:100]}")

    @staticmethod
    def generate_initial_question(cv_text: str, role: str | None = None) -> str:
        if not cv_text or not cv_text.strip():
            raise ValueError("CV text is empty. Cannot generate interview question.")

        role_hint = role.strip() if role else "the candidate's likely target role"
        prompt = f"""
You are a professional interviewer.

Generate exactly ONE concise interview question based on this CV for {role_hint}.
The question should be specific to the candidate's profile and experience.
Return only the question text. Do not return JSON, numbering, or explanation.

CV:
{cv_text}
"""
        question = AIService._call_model(prompt).strip()
        return question.strip('"').strip()

    @staticmethod
    def generate_followup_question(cv_text: str, history: list[dict], role: str | None = None) -> str:
        if not cv_text or not cv_text.strip():
            raise ValueError("CV text is empty. Cannot generate follow-up question.")
        if not history:
            return AIService.generate_initial_question(cv_text, role)

        role_hint = role.strip() if role else "the candidate's likely target role"
        history_text = "\n".join(
            [
                f"Q{i + 1}: {item.get('question', '').strip()}\nA{i + 1}: {item.get('answer', '').strip()}"
                for i, item in enumerate(history)
            ]
        )
        prompt = f"""
You are a professional interviewer running a live interview for {role_hint}.

Use the candidate CV and previous Q/A turns to generate exactly ONE next follow-up question.
The question should probe depth, clarify weak points, or go deeper into relevant experience.
Do not repeat previous questions.
Return only the question text. Do not return JSON, numbering, or explanation.

CV:
{cv_text}

Interview so far:
{history_text}
"""
        question = AIService._call_model(prompt).strip()
        return question.strip('"').strip()

    @staticmethod
    def evaluate_interview_session(cv_text: str, history: list[dict], role: str | None = None) -> dict:
        if not history:
            raise ValueError("Cannot evaluate interview without answers.")

        role_hint = role.strip() if role else "the candidate's likely target role"
        history_text = "\n".join(
            [
                f"Q{i + 1}: {item.get('question', '').strip()}\nA{i + 1}: {item.get('answer', '').strip()}"
                for i, item in enumerate(history)
            ]
        )
        prompt = f"""
You are a strict technical interviewer.

Evaluate the candidate's overall interview performance for {role_hint}, using:
- CV context
- all question/answer turns

Return ONLY JSON in this exact shape:
{{
  "overall_score": 0-10,
  "summary": "short final summary",
  "strengths": ["point 1", "point 2"],
  "improvements": ["point 1", "point 2"]
}}

CV:
{cv_text}

Interview Transcript:
{history_text}
"""

        data = AIService._call_model(prompt)
        try:
            return AIService._extract_json(data)
        except Exception as e:
            raise Exception(f"Failed to parse AI final evaluation: {str(e)[:100]}")

    # 🔥 NEW: Evaluate Answer
    @staticmethod
    def evaluate_answer(question: str, answer: str) -> dict:

        if not answer or not answer.strip():
            raise ValueError("Answer is empty")

        prompt = f"""
You are a strict technical interviewer.

Question:
{question}

Candidate Answer:
{answer}

Evaluate:
- correctness
- completeness
- clarity

Return ONLY JSON like:
{{
  "score": 0-10,
  "feedback": "short feedback",
  "correct": true/false
}}
"""

        data = AIService._call_model(prompt)
        try:
            return AIService._extract_json(data)
        except Exception as e:
            raise Exception(f"Failed to parse AI evaluation: {str(e)[:100]}")

    # 🔥 COMMON METHOD (clean code)
    @staticmethod
    def _call_model(prompt: str) -> str:
        if USE_GROQ:
            AIService.last_provider = "groq"
            return AIService._call_groq(prompt)
        else:
            AIService.last_provider = "ollama"
            return AIService._call_ollama(prompt)

    @staticmethod
    def get_last_provider() -> str:
        """Returns which provider served the last response: 'groq' or 'ollama'."""
        return AIService.last_provider or "unknown"

    @staticmethod
    def _call_ollama(prompt: str) -> str:

        try:
            response = requests.post(
                AIService.OLLAMA_URL,
                json={
                    "model": AIService.MODEL,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=12220
            )

            if response.status_code != 200:
                raise Exception(f"AI model failed: {response.status_code}")

            data = response.json()

            if "response" not in data or not data["response"].strip():
                raise Exception("Empty AI response")

            return data["response"]

        except requests.exceptions.RequestException as e:
            raise Exception(f"AI connection failed: {str(e)}")

    @staticmethod
    def _call_groq(prompt: str) -> str:

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": GROQ_MODEL,
            "messages": [
                {"role": "system", "content": "You are a professional interviewer."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }

        response = requests.post(GROQ_URL, headers=headers, json=payload)

        if response.status_code != 200:
            raise Exception(response.text)

        return response.json()["choices"][0]["message"]["content"]

    @staticmethod
    def stream_model(prompt: str):

        if USE_GROQ:
            yield from AIService._stream_groq(prompt)
        else:
            yield from AIService._stream_ollama(prompt)

    @staticmethod
    def _stream_groq(prompt: str):

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": GROQ_MODEL,
            "messages": [
                {"role": "system", "content": "You are a professional interviewer."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "stream": True
        }

        with requests.post(GROQ_URL, headers=headers, json=payload, stream=True) as r:
            for line in r.iter_lines():
                if line:
                    decoded = line.decode("utf-8")

                    if decoded.startswith("data: "):
                        data = decoded.replace("data: ", "")

                        if data == "[DONE]":
                            break

                        try:
                            json_data = json.loads(data)
                            delta = json_data["choices"][0]["delta"].get("content", "")
                            if delta:
                                yield delta
                        except:
                            continue

    @staticmethod
    def _stream_ollama(prompt: str):

        payload = {
            "model": AIService.MODEL,
            "prompt": prompt,
            "stream": True
        }

        with requests.post(AIService.OLLAMA_URL, json=payload, stream=True) as r:
            for line in r.iter_lines():
                if line:
                    data = json.loads(line.decode("utf-8"))
                    if "response" in data:
                        yield data["response"]