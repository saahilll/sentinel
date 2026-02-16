import asyncio
import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.core.database import async_session_factory
from app.auth.repositories.token import TokenRepository
from app.auth.repositories.user import UserRepository
from app.auth.services.auth import AuthService

async def generate_magic_link():
    async with async_session_factory() as session:
        token_repo = TokenRepository(session)
        user_repo = UserRepository(session)
        auth_service = AuthService(user_repo, token_repo)
        
        email = "test@example.com"
        print(f"Generating token for {email}...")
        
        # We can use the repo directly to get the raw token since service consumes it
        # Actually auth_service.request_magic_link just creates it and 'sends' it.
        # But it doesn't return it.
        # So verifying the service works is hard if I can't see the log.
        # I will use the repo directly to create one for testing verification.
        
        raw_token = await token_repo.create_magic_link_token(email)
        print(f"TOKEN: {raw_token}")
        print(f"URL: http://localhost:3000/auth/verify?token={raw_token}&flow=signup")

if __name__ == "__main__":
    asyncio.run(generate_magic_link())
