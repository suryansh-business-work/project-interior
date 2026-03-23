from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId


class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, _info=None):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return str(v)


# ---- Auth Models ----
class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ---- Project Models ----
class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    user_id: str
    site_plan_url: Optional[str] = None
    detected_style: Optional[str] = None
    style_confidence: Optional[float] = None
    style_probabilities: Optional[dict] = None
    created_at: datetime
    updated_at: datetime


# ---- Chat Models ----
class ChatMessageCreate(BaseModel):
    message: str = Field(..., min_length=1)


class ChatMessageResponse(BaseModel):
    id: str
    project_id: str
    role: str  # "user" or "assistant"
    message: str
    image_url: Optional[str] = None
    design_suggestions: Optional[List[dict]] = None
    created_at: datetime


# ---- Design Models ----
class StylePrediction(BaseModel):
    style: str
    confidence: float
    top_styles: List[dict]


class DesignSuggestion(BaseModel):
    category: str
    suggestion: str
    style: str
    reference_images: Optional[List[str]] = None
