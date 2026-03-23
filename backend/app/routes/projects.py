import os
import uuid
import aiofiles
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, status
from datetime import datetime, timezone
from typing import List
from bson import ObjectId
from app.models import ProjectCreate, ProjectResponse
from app.auth import get_current_user
from app.database import get_database
from app.config import settings
from ml.predictor import StylePredictor

router = APIRouter(prefix="/api/projects", tags=["Projects"])

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def _project_doc_to_response(doc: dict) -> ProjectResponse:
    return ProjectResponse(
        id=str(doc["_id"]),
        name=doc["name"],
        description=doc.get("description"),
        user_id=doc["user_id"],
        site_plan_url=doc.get("site_plan_url"),
        detected_style=doc.get("detected_style"),
        style_confidence=doc.get("style_confidence"),
        style_probabilities=doc.get("style_probabilities"),
        created_at=doc["created_at"],
        updated_at=doc["updated_at"]
    )


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(project: ProjectCreate, current_user: dict = Depends(get_current_user)):
    db = get_database()
    now = datetime.now(timezone.utc)

    project_doc = {
        "name": project.name,
        "description": project.description,
        "user_id": current_user["id"],
        "site_plan_url": None,
        "detected_style": None,
        "style_confidence": None,
        "style_probabilities": None,
        "created_at": now,
        "updated_at": now
    }

    result = await db.projects.insert_one(project_doc)
    project_doc["_id"] = result.inserted_id
    return _project_doc_to_response(project_doc)


@router.get("/", response_model=List[ProjectResponse])
async def list_projects(current_user: dict = Depends(get_current_user)):
    db = get_database()
    cursor = db.projects.find({"user_id": current_user["id"]}).sort("updated_at", -1)
    projects = await cursor.to_list(length=100)
    return [_project_doc_to_response(p) for p in projects]


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str, current_user: dict = Depends(get_current_user)):
    db = get_database()
    project = await db.projects.find_one({
        "_id": ObjectId(project_id),
        "user_id": current_user["id"]
    })
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return _project_doc_to_response(project)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: str, current_user: dict = Depends(get_current_user)):
    db = get_database()
    result = await db.projects.delete_one({
        "_id": ObjectId(project_id),
        "user_id": current_user["id"]
    })
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")

    # Also delete related chat messages
    await db.chat_messages.delete_many({"project_id": project_id})


@router.post("/{project_id}/upload-plan", response_model=ProjectResponse)
async def upload_site_plan(
    project_id: str,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    db = get_database()

    project = await db.projects.find_one({
        "_id": ObjectId(project_id),
        "user_id": current_user["id"]
    })
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Validate file extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"File type not allowed. Use: {', '.join(ALLOWED_EXTENSIONS)}")

    # Read and validate file size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Maximum 10MB.")

    # Save file
    upload_dir = os.path.join(settings.UPLOAD_DIR, current_user["id"])
    os.makedirs(upload_dir, exist_ok=True)

    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(upload_dir, filename)

    async with aiofiles.open(filepath, "wb") as f:
        await f.write(content)

    # Run style prediction
    predictor = StylePredictor.get_instance()
    prediction = predictor.predict(filepath)

    # Update project
    site_plan_url = f"/uploads/{current_user['id']}/{filename}"
    now = datetime.now(timezone.utc)

    await db.projects.update_one(
        {"_id": ObjectId(project_id)},
        {"$set": {
            "site_plan_url": site_plan_url,
            "detected_style": prediction["predicted_style"],
            "style_confidence": prediction["confidence"],
            "style_probabilities": {s["style"]: s["confidence"] for s in prediction["top_styles"]},
            "updated_at": now
        }}
    )

    updated = await db.projects.find_one({"_id": ObjectId(project_id)})
    return _project_doc_to_response(updated)
