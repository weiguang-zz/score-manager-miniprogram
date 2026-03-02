from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="admin")
    admin_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    members: Mapped[list["Member"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    staff: Mapped[list["User"]] = relationship(back_populates="admin", foreign_keys="User.admin_id")
    admin: Mapped[Optional["User"]] = relationship(back_populates="staff", remote_side=[id], foreign_keys=[admin_id])


class Member(Base):
    __tablename__ = "members"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="members")
    records: Mapped[list["ScoreRecord"]] = relationship(back_populates="member", cascade="all, delete-orphan", order_by="ScoreRecord.created_at.desc()")


class LiveRoom(Base):
    __tablename__ = "live_rooms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship()
    records: Mapped[list["ScoreRecord"]] = relationship(back_populates="room")


class ScoreRecord(Base):
    __tablename__ = "score_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    member_id: Mapped[int] = mapped_column(Integer, ForeignKey("members.id"), nullable=False)
    change_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str] = mapped_column(String(200), nullable=False, default="")
    balance_after: Mapped[int] = mapped_column(Integer, nullable=False)
    operator_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    operator_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    room_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("live_rooms.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    member: Mapped["Member"] = relationship(back_populates="records")
    room: Mapped[Optional["LiveRoom"]] = relationship(back_populates="records")
