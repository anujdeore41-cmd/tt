from datetime import datetime, time
from sqlalchemy import String, Integer, DateTime, ForeignKey, UniqueConstraint, Boolean, Time, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class WorkingDay(Base):
    __tablename__ = "working_days"
    __table_args__ = (UniqueConstraint("day_of_week", name="uq_working_day"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    day_of_week: Mapped[str] = mapped_column(String(3), unique=True, index=True)  # MON..SUN
    day_number: Mapped[int] = mapped_column(Integer)  # 0=Monday..6=Sunday (python weekday)
    is_working: Mapped[bool] = mapped_column(Boolean, default=False)
    sequence: Mapped[int] = mapped_column(Integer, default=0)  # display order
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ScheduleConfiguration(Base):
    """Singleton row holding the college's schedule configuration."""
    __tablename__ = "schedule_configuration"

    id: Mapped[int] = mapped_column(primary_key=True)
    working_days_count: Mapped[int] = mapped_column(Integer, default=0)
    college_start_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    college_end_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    lecture_duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    lecture_duration_custom: Mapped[bool] = mapped_column(Boolean, default=False)
    default_practical_duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # --- configurable scheduling rules ---
    max_lectures_per_day_per_division: Mapped[int] = mapped_column(Integer, default=8)
    same_faculty_division_day_penalty: Mapped[int] = mapped_column(Integer, default=100)
    same_subject_division_day_penalty: Mapped[int] = mapped_column(Integer, default=60)
    gap_penalty: Mapped[int] = mapped_column(Integer, default=30)
    consecutive_lecture_penalty: Mapped[int] = mapped_column(Integer, default=40)
    workload_balance_penalty: Mapped[int] = mapped_column(Integer, default=50)
    # --- communication rules ---
    query_window_minutes: Mapped[int] = mapped_column(Integer, default=60)
    notification_lead_minutes: Mapped[int] = mapped_column(Integer, default=0)
    # --- upload rules ---
    allowed_file_types: Mapped[list] = mapped_column(JSON, default=lambda: ["pdf", "doc", "docx", "ppt", "pptx", "xls", "xlsx", "txt", "png", "jpg", "jpeg"])
    max_upload_size_mb: Mapped[int] = mapped_column(Integer, default=10)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    breaks: Mapped[list["Break"]] = relationship(
        back_populates="schedule_configuration", cascade="all, delete-orphan",
        order_by="Break.sequence", lazy="selectin"
    )


class Break(Base):
    __tablename__ = "breaks"

    id: Mapped[int] = mapped_column(primary_key=True)
    schedule_configuration_id: Mapped[int] = mapped_column(
        ForeignKey("schedule_configuration.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(64))              # "Short Break", "Lunch Break"
    duration_minutes: Mapped[int] = mapped_column(Integer)     # > 0
    after_lectures: Mapped[int] = mapped_column(Integer)       # occurs after N lectures
    sequence: Mapped[int] = mapped_column(Integer, default=0)
    break_kind: Mapped[str] = mapped_column(String(8), default="BREAK")  # BREAK / LUNCH
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    schedule_configuration: Mapped["ScheduleConfiguration"] = relationship(back_populates="breaks")


class TimeSlot(Base):
    __tablename__ = "time_slots"

    id: Mapped[int] = mapped_column(primary_key=True)
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)
    sequence: Mapped[int] = mapped_column(Integer)  # 1..N in chronological order
    slot_type: Mapped[str] = mapped_column(String(16), default="LECTURE")  # LECTURE/PRACTICAL/BREAK/LUNCH
    is_teaching_period: Mapped[bool] = mapped_column(Boolean, default=True)
    break_id: Mapped[int | None] = mapped_column(ForeignKey("breaks.id", ondelete="SET NULL"), nullable=True)
    label: Mapped[str] = mapped_column(String(64), default="")  # "Lecture 1", "Short Break", "Lunch"
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
