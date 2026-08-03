from collections.abc import AsyncGenerator

from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.dialects.postgresql import UUID

import os
import uuid
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL=os.getenv("DATABASE_URL")


class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String)



engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


# this ensures my database table is up-to-date.
async def create_sync_table():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# this creates sessions such that we can securely communicate with our database.
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    with async_session_maker() as session:
        yield session