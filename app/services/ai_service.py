import requests
import json
import re


class AIService:
    OLLAMA_URL = "http://localhost:11434/api/generate"
    MODEL = "llama3"  # 🔥 llama3 ki jagah fast model use karo

    @staticmethod
    def _extract_json(text: str):
        """Extract JSON from response, handling markdown code blocks and whitespace."""
        text = text.strip()

        # Try to extract JSON from markdown code block: ```json ... ```
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