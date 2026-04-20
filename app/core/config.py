import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:123@localhost:5432/mocksy")

# JWT
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

# App
DEBUG = os.getenv("DEBUG", "True").lower() == "true"


def validate_environment() -> list[str]:
    errors: list[str] = []

    if not os.getenv("DATABASE_URL"):
        errors.append("DATABASE_URL is required.")
    if not os.getenv("SECRET_KEY"):
        errors.append("SECRET_KEY is required.")

    groq_enabled = os.getenv("GROQ_ENABLED", "true").lower() == "true"
    if groq_enabled and not os.getenv("GROQ_API_KEY"):
        errors.append("GROQ_API_KEY is required when GROQ_ENABLED is true.")

    return errors
