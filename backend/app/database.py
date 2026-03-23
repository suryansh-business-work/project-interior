from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

client: AsyncIOMotorClient = None
db = None


async def connect_to_mongo():
    global client, db
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]

    await db.users.create_index("email", unique=True)
    await db.projects.create_index("user_id")
    await db.chat_messages.create_index([("project_id", 1), ("created_at", 1)])


async def close_mongo_connection():
    global client
    if client:
        client.close()


def get_database():
    return db
