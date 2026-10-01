from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, UniqueConstraint, Boolean, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Room(Base):
    __tablename__ = "rooms"
    __table_args__ = (UniqueConstraint("room_number", name="uq_room_number"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    room_number: Mapped[str] = mapped_column(String(32), index=True)
    room_name: Mapped[str] = mapped_column(String(128), default="")
    building: Mapped[str] = mapped_column(String(64), default="")
    floor: Mapped[str] = mapped_column(String(32), default="")
    capacity: Mapped[int] = mapped_column(Integer, default=60)
    room_type: Mapped[str] = mapped_column(String(24), default="CLASSROOM")  # CLASSROOM/SMART_CLASSROOM/SEMINAR_HALL/TUTORIAL_ROOM/OTHER
    equipment: Mapped[str] = mapped_column(String(255), default="")
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[str] = mapped_column(String(16), default="ACTIVE")
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Laboratory(Base):
    __tablename__ = "laboratories"
    __table_args__ = (UniqueConstraint("lab_number", name="uq_lab_number"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    lab_number: Mapped[str] = mapped_column(String(32), index=True)
    lab_name: Mapped[str] = mapped_column(String(128), default="")
    building: Mapped[str] = mapped_column(String(64), default="")
    floor: Mapped[str] = mapped_column(String(32), default="")
    capacity: Mapped[int] = mapped_column(Integer, default=30)
    equipment: Mapped[str] = mapped_column(String(255), default="")
    software: Mapped[str] = mapped_column(String(255), default="")
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[str] = mapped_column(String(16), default="ACTIVE")
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PracticalBatch(Base):
    __tablename__ = "practical_batches"
    __table_args__ = (UniqueConstraint("division_id", "name", name="uq_batch_name_per_division"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    division_id: Mapped[int] = mapped_column(ForeignKey("divisions.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(64))  # e.g. "A1", "A2"
    capacity: Mapped[int] = mapped_column(Integer, default=30)
    faculty_id: Mapped[int | None] = mapped_column(ForeignKey("faculty.id", ondelete="SET NULL"), nullable=True)
    laboratory_id: Mapped[int | None] = mapped_column(ForeignKey("laboratories.id", ondelete="SET NULL"), nullable=True)
    status: Mapped[str] = mapped_column(String(16), default="ACTIVE")
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    division: Mapped["Division"] = relationship("Division", lazy="selectin")


Index("ix_rooms_type_capacity", Room.room_type, Room.capacity)
