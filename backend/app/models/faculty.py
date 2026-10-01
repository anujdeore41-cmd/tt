from datetime import datetime, time
from sqlalchemy import String, Integer, DateTime, ForeignKey, UniqueConstraint, Boolean, Time, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class FacultyDesignation(Base):
    __tablename__ = "faculty_designations"
    __table_args__ = (UniqueConstraint("name", name="uq_designation_name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), index=True)
    description: Mapped[str] = mapped_column(String(255), default="")
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Faculty(Base):
    __tablename__ = "faculty"

    id: Mapped[int] = mapped_column(primary_key=True)
    faculty_code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    phone: Mapped[str] = mapped_column(String(32), default="")
    department: Mapped[str] = mapped_column(String(128), default="")
    designation_id: Mapped[int | None] = mapped_column(ForeignKey("faculty_designations.id", ondelete="SET NULL"), nullable=True)
    max_weekly_hours: Mapped[int] = mapped_column(Integer, default=20)
    min_weekly_hours: Mapped[int] = mapped_column(Integer, default=0)
    preferred_working_hours: Mapped[str] = mapped_column(String(64), default="")  # e.g. "Morning (08:30-12:30)"
    can_take_theory: Mapped[bool] = mapped_column(Boolean, default=True)
    can_take_practical: Mapped[bool] = mapped_column(Boolean, default=False)
    substitute_eligible: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[str] = mapped_column(String(16), default="ACTIVE")  # ACTIVE / INACTIVE / ON_LEAVE
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    designation: Mapped["FacultyDesignation | None"] = relationship(lazy="selectin")
    subjects: Mapped[list["Subject"]] = relationship(
        "Subject", secondary="faculty_subjects", lazy="selectin", viewonly=True
    )


class FacultyAvailability(Base):
    """Available time windows per faculty per weekday. The scheduling engine
    checks each time slot against these windows (slot must fit inside an
    available window)."""
    __tablename__ = "faculty_availability"
    __table_args__ = (
        UniqueConstraint("faculty_id", "day_of_week", "start_time", "end_time", name="uq_faculty_availability"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    faculty_id: Mapped[int] = mapped_column(ForeignKey("faculty.id", ondelete="CASCADE"), index=True)
    day_of_week: Mapped[str] = mapped_column(String(3), index=True)  # MON..SUN
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


Index("ix_faculty_dept_status", Faculty.department, Faculty.status)
