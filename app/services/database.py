import ssl
from typing import AsyncGenerator

from dotenv import load_dotenv
import os
import logging

from sqlalchemy import event, Engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base


# Load environment variables from .env
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
ssl_context = ssl.create_default_context()

logger = logging.getLogger(__name__)

engine = create_async_engine(
    DATABASE_URL,
    echo=False,           # false = disable SQLAlchemy's default query logging (handled by event listeners)
    pool_size=5,          # number of connections maintained in the pool (5 for local development)
    max_overflow=10,      # additional temporary connections if needed (10 for local development)
    connect_args={"ssl": ssl_context}
)

@event.listens_for(engine.sync_engine, "connect")
def on_connect(dbapi_connection, connection_record):
    logger.info("New DBAPI connection created: %s", dbapi_connection)
    # Use the sync cursor API to execute a test query
    cursor = dbapi_connection.cursor()
    cursor.execute("SELECT 'Connected successfully' AS message")
    result = cursor.fetchone()[0]
    logger.info("DB connection test message: %s", result)

# Attach event listener: log before executing any SQL statement
@event.listens_for(Engine, "before_execute")
def before_execute(conn, clauseelement, multiparams, params, execution_options):
    logger.info("Before execute: %s", clauseelement)

# Create the async session factory
# Note: normal AsyncSession is for a single asynchronous database session
AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False
)

# Base class for ORM models
Base = declarative_base()

# Get an async session for each request
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
