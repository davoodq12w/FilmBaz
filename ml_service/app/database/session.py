from sqlalchemy.ext.asyncio import async_sessionmaker
from .database import engine

SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
