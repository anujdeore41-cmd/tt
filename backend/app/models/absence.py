from datetime import datetime
from sqlalchemy import String, Date, DateTime, ForeignKey, JSON, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class FacultyAbsence(Base):
    __tablename__ = "faculty_absences"

    id: Mapped[int] = mapped_column(primary_key=True)
    faculty_id: Mapped[int] = mapped_column(ForeignKey("faculty.id", ondelete="CASCADE"), index=True)
    absence_date = mapped_column(DateTime, index=True)  # the date the faculty is absent
    reason: Mapped[str] = mapped_column(String(64), default="OTHER")  # SICK_LEAVE/PERSONAL/OFFICIAL_DUTY/OTHER
    message: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(16), default="REPORTED")  # REPORTED/NOTIFIED/RESOLVED
    reported_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    affected_lectures: Mapped[list["AffectedLecture"]] = relationship(
        back_populates="absence", cascade="all, delete-orphan", lazy="noload"
    )


class AffectedLecture(Base):
    __tablename__ = "affected_lectures"

    id: Mapped[int] = mapped_column(primary_key=True)
    absence_id: Mapped[int] = mapped_column(ForeignKey("faculty_absences.id", ondelete="CASCADE"), index=True)
    timetable_entry_id: Mapped[int] = mapped_column(ForeignKey("timetable_entries.id", ondelete="CASCADE"), index=True)
    time_slot_id: Mapped[int | None] = mapped_column(nullable=True)
    day_of_week: Mapped[str | None] = mapped_column(String(3), nullable=True)
    academic_year_id: Mapped[int | None] = mapped_column(nullable=True)
    division_id: Mapped[int | None] = mapped_column(nullable=True)
    subject_id: Mapped[int | None] = mapped_column(nullable=True)
    room_id: Mapped[int | None] = mapped_column(nullable=True)
    laboratory_id: Mapped[int | None] = mapped_column(nullable=True)
    batch_id: Mapped[int | None] = mapped_column(nullable=True)
    session_type: Mapped[str] = mapped_column(String(16), default="LECTURE")
    substitute_request_id: Mapped[int | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    absence: Mapped["FacultyAbsence"] = relationship(back_populates="affected_lectures")
