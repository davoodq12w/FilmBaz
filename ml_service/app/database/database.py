from sqlalchemy.ext.asyncio import create_async_engine
from ..configs.settings import settings

# use async engine to working on tasks simultaneously.
engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True)
