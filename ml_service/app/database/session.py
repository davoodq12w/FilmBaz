from sqlalchemy.ext.asyncio import async_sessionmaker
from .database import engine

# create an async session to connect to DataBase.
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_session():
    """
    Async generator that yields a NEW database session per call.
    The session is automatically closed after use (via async context manager).
    Intended to be used as a FastAPI dependency.
    """
    async with SessionLocal() as session:
        yield session
