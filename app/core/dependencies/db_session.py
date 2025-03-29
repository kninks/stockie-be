from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings.database import AsyncSessionLocal


# Get an async session for each request
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
