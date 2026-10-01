from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SubstituteRequest(Base):
    __tablename__ = "substitute_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    absence_id: Mapped[int | None] = mapped_column(ForeignKey("faculty_absences.id", ondelete="CASCADE"), nullable=True, index=True)
    affected_lecture_id: Mapped[int | None] = mapped_column(nullable=True)
    original_entry_id: Mapped[int | None] = mapped_column(ForeignKey("timetable_entries.id", ondelete="CASCADE"), nullable=True)
    absent_faculty_id: Mapped[int] = mapped_column(ForeignKey("faculty.id", ondelete="CASCADE"), index=True)
    substitute_faculty_id: Mapped[int | None] = mapped_column(ForeignKey("faculty.id", ondelete="SET NULL"), nullable=True, index=True)
    substitute_date = mapped_column(DateTime, index=True)
    time_slot_id: Mapped[int | None] = mapped_column(nullable=True)
    academic_year_id: Mapped[int | None] = mapped_column(nullable=True)
    division_id: Mapped[int | None] = mapped_column(nullable=True)
    subject_id: Mapped[int | None] = mapped_column(nullable=True)
    room_id: Mapped[int | None] = mapped_column(nullable=True)
    laboratory_id: Mapped[int | None] = mapped_column(nullable=True)
    batch_id: Mapped[int | None] = mapped_column(nullable=True)
    notes: Mapped[str] = mapped_column(Text, default="")
    assignment_instructions: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(16), default="PENDING")  # PENDING/SENT/DELIVERED/ACCEPTED/DECLINED/CANCELLED
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    responded_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class SubstituteResponse(Base):
    __tablename__ = "substitute_responses"

    id: Mapped[int] = mapped_column(primary_key=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("substitute_requests.id", ondelete="CASCADE"), index=True)
    faculty_id: Mapped[int] = mapped_column(ForeignKey("faculty.id", ondelete="CASCADE"), index=True)
    response: Mapped[str] = mapped_column(String(16))  # ACCEPTED / DECLINED
    comment: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
