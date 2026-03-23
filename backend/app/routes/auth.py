from fastapi import APIRouter, HTTPException, status
from datetime import datetime, timezone
from bson import ObjectId
from app.models import UserCreate, UserLogin, UserResponse, Token
from app.auth import hash_password, verify_password, create_access_token
from app.database import get_database

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    db = get_database()

    existing = await db.users.find_one({"email": user_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_doc = {
        "name": user_data.name,
        "email": user_data.email,
        "password": hash_password(user_data.password),
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }

    result = await db.users.insert_one(user_doc)
    user_id = str(result.inserted_id)

    access_token = create_access_token(data={"sub": user_id})

    return Token(
        access_token=access_token,
        user=UserResponse(
            id=user_id,
            name=user_data.name,
            email=user_data.email,
            created_at=user_doc["created_at"]
        )
    )


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    db = get_database()

    user = await db.users.find_one({"email": user_data.email})
    if not user or not verify_password(user_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user_id = str(user["_id"])
    access_token = create_access_token(data={"sub": user_id})

    return Token(
        access_token=access_token,
        user=UserResponse(
            id=user_id,
            name=user["name"],
            email=user["email"],
            created_at=user["created_at"]
        )
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = __import__("fastapi").Depends(__import__("app.auth", fromlist=["get_current_user"]).get_current_user)):
    return UserResponse(**current_user)
