from dotenv import load_dotenv; load_dotenv()
import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")

    # Example: postgresql://office_app:pass@127.0.0.1:5432/office_tasks
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # If you want to keep it truly public read-only:
    PUBLIC_READONLY = True