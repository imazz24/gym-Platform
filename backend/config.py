"""
Application configuration
"""
from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "admin")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "powerhouse_gym")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

    SECRET_KEY = os.getenv("SECRET_KEY", "powerhouse_gym_secret_key_2024")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    TOKEN_EXPIRE_HOURS = int(os.getenv("TOKEN_EXPIRE_HOURS", "24"))

    @property
    def DATABASE_URL(self):
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

config = Config()