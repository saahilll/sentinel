import asyncio
import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.core.database import init_db, engine
from app.auth.models.user import User
from sqlmodel import SQLModel

async def reset_db():
    print("Resetting database...")
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)
    print("Database reset.")

if __name__ == "__main__":
    asyncio.run(reset_db())
