from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone
from typing import List
import re
import logging
from bson import ObjectId
from openai import OpenAI
from app.models import ChatMessageCreate, ChatMessageResponse
from app.auth import get_current_user
from app.database import get_database
from app.config import settings
from ml.predictor import generate_design_suggestions, DESIGN_KNOWLEDGE
from ml.image_generator import generate_image

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/projects/{project_id}/chat", tags=["Chat"])

IMAGE_TRIGGER_PATTERNS = [
    r'\b(generate|create|make|draw|render|show|design|visuali[sz]e)\b.*\b(image|picture|photo|visual|render|illustration|concept|mockup|mood\s*board)\b',
    r'\b(image|picture|visual|render)\b.*\b(of|for|showing)\b',
    r'\b(what would|how would|can you show)\b.*\b(look like)\b',
    r'\bimage\b.*\b(bana|dikha|generate)\b',
    r'\b(bana|dikha|dikhao)\b.*\b(image|photo|picture|tasveer)\b',
]


def _get_openai_client() -> OpenAI:
    if not settings.OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    return OpenAI(api_key=settings.OPENAI_API_KEY)


def _msg_to_response(doc: dict) -> ChatMessageResponse:
    return ChatMessageResponse(
        id=str(doc["_id"]),
        project_id=doc["project_id"],
        role=doc["role"],
        message=doc["message"],
        image_url=doc.get("image_url"),
        design_suggestions=doc.get("design_suggestions"),
        created_at=doc["created_at"]
    )


def _build_system_prompt(project: dict) -> str:
    """Build OpenAI system prompt with project context."""
    detected_style = project.get("detected_style", "modern")
    confidence = project.get("style_confidence", 0)
    style_info = DESIGN_KNOWLEDGE.get(detected_style, DESIGN_KNOWLEDGE["modern"])
    has_plan = bool(project.get("site_plan_url"))

    system_prompt = (
        "You are an expert interior design AI assistant for a SaaS platform. "
        "You provide professional, detailed, and actionable interior design advice.\n\n"
        "Your expertise includes: color theory, spatial planning, furniture selection, "
        "material recommendations, lighting design, room layouts, and all major design styles.\n\n"
    )

    if has_plan:
        system_prompt += (
            f"CURRENT PROJECT CONTEXT:\n"
            f"- Project name: {project.get('name', 'Untitled')}\n"
            f"- Detected interior style: {detected_style} (confidence: {confidence:.1f}%)\n"
            f"- Style colors: {', '.join(style_info['colors'])}\n"
            f"- Style materials: {', '.join(style_info['materials'])}\n"
            f"- Style furniture: {', '.join(style_info['furniture'])}\n"
            f"- Style tips: {style_info['tips']}\n\n"
            "The user has uploaded a site plan/reference image that was analyzed by our ML model. "
            "Use the detected style as context but also respond to any specific user requests. "
            "If the user asks about a different style, help them with that too.\n\n"
        )
    else:
        system_prompt += (
            "The user has NOT uploaded a site plan yet. Encourage them to upload one "
            "for personalized style detection, but still help with general design questions.\n\n"
        )

    system_prompt += (
        "RESPONSE GUIDELINES:\n"
        "- Use markdown formatting (bold, lists, headings) for readability\n"
        "- Be specific with product names, color codes (hex when possible), and dimensions\n"
        "- Provide the 60-30-10 color rule when discussing palettes\n"
        "- Consider budget-friendly and premium options\n"
        "- Mention lighting (natural and artificial) in room designs\n"
        "- Keep responses concise but comprehensive (200-400 words)\n"
        "- Use Hindi/English mix if the user writes in Hindi\n\n"
        "IMAGE GENERATION:\n"
        "- You have a built-in Stable Diffusion AI model that can generate interior design images locally.\n"
        "- When the user asks to generate, create, show, or visualize a design image, "
        "the system will automatically generate one using the local model.\n"
        "- Do NOT say you cannot generate images. You CAN and WILL generate them.\n"
        "- When an image is being generated, describe the design concept you're creating "
        "with details about colors, furniture placement, lighting, and materials.\n"
        "- NEVER suggest using external tools like Pinterest, Google, SketchUp etc. for image generation. "
        "Your own model handles it.\n"
    )

    return system_prompt


async def _get_chat_history(db, project_id: str, limit: int = 20) -> List[dict]:
    """Get recent chat history for OpenAI context."""
    cursor = db.chat_messages.find(
        {"project_id": project_id}
    ).sort("created_at", -1).limit(limit)
    messages = await cursor.to_list(length=limit)
    messages.reverse()

    openai_messages = []
    for msg in messages:
        openai_messages.append({
            "role": msg["role"],
            "content": msg["message"]
        })
    return openai_messages


async def _generate_openai_response(project: dict, user_message: str, db, project_id: str) -> str:
    """Generate response using OpenAI GPT API."""
    client = _get_openai_client()

    system_prompt = _build_system_prompt(project)
    chat_history = await _get_chat_history(db, project_id)

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(chat_history)
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=1000,
        temperature=0.7,
    )

    return response.choices[0].message.content


def _should_generate_image(message: str) -> bool:
    """Check if user message is requesting image generation."""
    lower = message.lower()
    for pattern in IMAGE_TRIGGER_PATTERNS:
        if re.search(pattern, lower):
            return True
    return False


@router.get("/", response_model=List[ChatMessageResponse])
async def get_chat_messages(
    project_id: str,
    current_user: dict = Depends(get_current_user)
):
    db = get_database()

    project = await db.projects.find_one({
        "_id": ObjectId(project_id),
        "user_id": current_user["id"]
    })
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    cursor = db.chat_messages.find({"project_id": project_id}).sort("created_at", 1)
    messages = await cursor.to_list(length=500)
    return [_msg_to_response(m) for m in messages]


@router.post("/", response_model=ChatMessageResponse)
async def send_message(
    project_id: str,
    msg: ChatMessageCreate,
    current_user: dict = Depends(get_current_user)
):
    db = get_database()

    project = await db.projects.find_one({
        "_id": ObjectId(project_id),
        "user_id": current_user["id"]
    })
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    now = datetime.now(timezone.utc)

    # Save user message
    user_msg_doc = {
        "project_id": project_id,
        "role": "user",
        "message": msg.message,
        "image_url": None,
        "design_suggestions": None,
        "created_at": now
    }
    await db.chat_messages.insert_one(user_msg_doc)

    # Generate response using OpenAI
    try:
        ai_response = await _generate_openai_response(project, msg.message, db, project_id)
    except Exception as e:
        ai_response = (
            f"I'm having trouble connecting to the AI service right now. "
            f"Here's what I know about your **{project.get('detected_style', 'modern')}** style:\n\n"
        )
        style_info = DESIGN_KNOWLEDGE.get(project.get("detected_style", "modern"), DESIGN_KNOWLEDGE["modern"])
        ai_response += (
            f"**Colors:** {', '.join(style_info['colors'])}\n\n"
            f"**Materials:** {', '.join(style_info['materials'])}\n\n"
            f"**Furniture:** {', '.join(style_info['furniture'])}\n\n"
            f"**Tip:** {style_info['tips']}"
        )

    # Generate image if user asked for one (using local Stable Diffusion model)
    image_url = None
    if _should_generate_image(msg.message):
        detected_style = project.get("detected_style", "modern")
        style_info = DESIGN_KNOWLEDGE.get(detected_style, DESIGN_KNOWLEDGE["modern"])
        image_url = generate_image(
            style=detected_style,
            user_message=msg.message,
            style_info=style_info,
            save_dir=settings.UPLOAD_DIR,
        )
        if image_url:
            ai_response += "\n\n*Here's a design concept generated by our local AI model based on your request:*"

    # Generate structured suggestions
    detected_style = project.get("detected_style", "modern")
    suggestions = generate_design_suggestions(detected_style, msg.message)

    assistant_msg_doc = {
        "project_id": project_id,
        "role": "assistant",
        "message": ai_response,
        "image_url": image_url,
        "design_suggestions": suggestions,
        "created_at": datetime.now(timezone.utc)
    }
    result = await db.chat_messages.insert_one(assistant_msg_doc)
    assistant_msg_doc["_id"] = result.inserted_id

    return _msg_to_response(assistant_msg_doc)
