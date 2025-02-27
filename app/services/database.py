# https://docs.sqlalchemy.org/en/20/tutorial/index.html
# https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
import logging

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

import os

from sqlalchemy.orm import declarative_base

# Load DATABASE_URL from .env or default to local PostgreSQL
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_size=5,
    max_overflow=10
)

# Create an async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False
)

# Base class for SQLAlchemy models
Base = declarative_base()


# Dependency to get an async session for each request
async def get_db():
    logging.info("get_db() was called")
    async with AsyncSessionLocal() as session:
        yield session
        logging.info("get_db() session closed")
