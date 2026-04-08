import requests


class AIService:

    OLLAMA_URL = "http://localhost:11434/api/generate"

    @staticmethod
    def generate_questions(cv_text: str) -> str:
        prompt = f"""
You are a professional interviewer.

Based on the following CV, generate 5 interview questions.

Focus on:
- Skills
- Experience
- Projects

CV:
{cv_text}

Return only questions in a numbered list.
"""

        response = requests.post(
            AIService.OLLAMA_URL,
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            }
        )

        if response.status_code != 200:
            raise Exception("AI model failed")

        return response.json()["response"]