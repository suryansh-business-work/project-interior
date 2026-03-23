from fastapi import APIRouter, Depends
from app.auth import get_current_user
from app.config import STYLE_CLASSES
from ml.predictor import get_style_description, DESIGN_KNOWLEDGE

router = APIRouter(prefix="/api/styles", tags=["Styles"])


@router.get("/")
async def list_styles(current_user: dict = Depends(get_current_user)):
    """Get all available interior design styles with descriptions."""
    styles = []
    for style in STYLE_CLASSES:
        info = DESIGN_KNOWLEDGE.get(style, {})
        styles.append({
            "name": style,
            "display_name": style.replace("-", " ").title(),
            "description": get_style_description(style),
            "colors": info.get("colors", []),
            "materials": info.get("materials", []),
            "preview_tip": info.get("tips", "")
        })
    return {"styles": styles, "total": len(styles)}
