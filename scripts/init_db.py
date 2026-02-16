import asyncio
import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.core.database import init_db

async def run_init_db():
    print("Initializing database...")
    await init_db()
    print("Database initialized.")

if __name__ == "__main__":
    asyncio.run(run_init_db())
