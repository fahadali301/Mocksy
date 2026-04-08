import requests


class AIService:
    OLLAMA_URL = "http://localhost:11434/api/generate"

    @staticmethod
    def generate_questions(cv_text: str) -> str:

        # ✅ Check: CV text empty ya None
        if not cv_text or not cv_text.strip():
            raise ValueError("CV text is empty. Cannot generate questions.")

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

        try:
            response = requests.post(
                AIService.OLLAMA_URL,
                json={
                    "model": "llama3",
                    "prompt": prompt,
                    "stream": False
                },
                timeout=1220
            )

            if response.status_code != 200:
                raise Exception(f"AI model failed with status {response.status_code}")

            data = response.json()

            # ✅ Safety check
            if "response" not in data or not data["response"].strip():
                raise Exception("AI returned empty response")

            return data["response"]

        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to connect to AI model: {str(e)}")