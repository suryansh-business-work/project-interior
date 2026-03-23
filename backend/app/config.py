import os
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "interior_design_saas"
    JWT_SECRET_KEY: str = "your-super-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    MODEL_PATH: str = "./ml/models/interior_style_classifier.pth"
    UPLOAD_DIR: str = "./uploads"
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    OPENAI_API_KEY: str = ""

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"


settings = Settings()

STYLE_CLASSES = [
    "asian", "coastal", "contemporary", "craftsman", "eclectic",
    "farmhouse", "french-country", "industrial", "mediterranean",
    "mid-century-modern", "modern", "rustic", "scandinavian",
    "shabby-chic-style", "southwestern", "traditional", "transitional",
    "tropical", "victorian"
]

NUM_CLASSES = len(STYLE_CLASSES)
