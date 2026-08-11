from collections.abc import AsyncGenerator

from sqlalchemy import make_url
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)
from elcards_backend.settings import settings
from sqlalchemy.orm import DeclarativeBase


url = make_url(settings.database_url).set(
    drivername="postgresql+asyncpg",
    query={},
)


engine = create_async_engine(
    url,
    connect_args={"ssl": "require"},
    pool_size=5,
    max_overflow=5,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False,
)

SessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False
)


class Base(DeclarativeBase):
    """All ORM models will inherit from this."""


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with engine.begin() as session:
        yield session