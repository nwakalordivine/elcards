from elcards_backend.db import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, func
from datetime import datetime, timezone
from uuid import UUID, uuid4


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, server_default=uuid4)
    username: Mapped[str] = mapped_column(String(255), index=True)
    email: Mapped[str] = mapped_column(String(255), index=True)
    password_hash = Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(datetime.now(timezone=True)), server_default=func.now()
    )