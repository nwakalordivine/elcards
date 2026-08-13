from elcards_backend.db import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, func, Uuid, Enum as SQLEnum
from datetime import datetime, timezone
from uuid import UUID, uuid4
import enum


class UserRole(str, enum.Enum):
    USER ="user"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    username: Mapped[str] = mapped_column(String(255), index=True, unique=True)
    email: Mapped[str] = mapped_column(String(255), index=True, unique=True)
    status: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole, name="user_role", values_callable=lambda e : [m.value for m in e]), 
        default=UserRole.USER, 
        server_default=UserRole.USER.value
        )
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )