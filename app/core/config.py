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

