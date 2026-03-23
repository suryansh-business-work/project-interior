from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from contextlib import asynccontextmanager

from app.config import settings
from app.database import connect_to_mongo, close_mongo_connection
from app.routes import auth, projects, chat, styles
from ml.predictor import StylePredictor


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    print("Connected to MongoDB")

    # Load ML model
    predictor = StylePredictor.get_instance()
    loaded = predictor.load_model()
    if loaded:
        print("ML model loaded successfully")
    else:
        print("ML model not found - running without predictions")

    yield

    # Shutdown
    await close_mongo_connection()
    print("Disconnected from MongoDB")


app = FastAPI(
    title="Interior Design SaaS API",
    description="AI-powered interior design platform with style detection and design recommendations",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for uploads
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Routes
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(chat.router)
app.include_router(styles.router)


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "Interior Design SaaS"}
