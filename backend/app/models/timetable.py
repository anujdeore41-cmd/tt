from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, UniqueConstraint, JSON, Index, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TimetableVersion(Base):
    __tablename__ = "timetable_versions"

    id: Mapped[int] = mapped_column(primary_key=True)
    version_number: Mapped[int] = mapped_column(Integer, default=1)
    academic_year_id: Mapped[int | None] = mapped_column(ForeignKey("academic_years.id", ondelete="CASCADE"), index=True, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="DRAFT")  # DRAFT/GENERATED/UNDER_REVIEW/PUBLISHED/UPDATED/ARCHIVED
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    generation_job_id: Mapped[int | None] = mapped_column(ForeignKey("timetable_generation_jobs.id", ondelete="SET NULL"), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    reason: Mapped[str] = mapped_column(String(255), default="")
    stats: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    entries: Mapped[list["TimetableEntry"]] = relationship(
        back_populates="version", cascade="all, delete-orphan", lazy="noload"
    )


class TimetableEntry(Base):
    """One weekly recurring timetable cell. Substitution overrides for a
    specific date are stored as extra rows with effective_date set and
    recurring_entry_id pointing at the original row."""
    __tablename__ = "timetable_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    timetable_version_id: Mapped[int] = mapped_column(ForeignKey("timetable_versions.id", ondelete="CASCADE"), index=True)
    day_of_week: Mapped[str] = mapped_column(String(3), index=True)  # MON..SUN
    time_slot_id: Mapped[int] = mapped_column(ForeignKey("time_slots.id", ondelete="CASCADE"), index=True)
    academic_year_id: Mapped[int] = mapped_column(ForeignKey("academic_years.id", ondelete="CASCADE"), index=True)
    division_id: Mapped[int] = mapped_column(ForeignKey("divisions.id", ondelete="CASCADE"), index=True)
    subject_id: Mapped[int | None] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"), nullable=True)
    faculty_id: Mapped[int | None] = mapped_column(ForeignKey("faculty.id", ondelete="SET NULL"), nullable=True)
    room_id: Mapped[int | None] = mapped_column(ForeignKey("rooms.id", ondelete="SET NULL"), nullable=True)
    laboratory_id: Mapped[int | None] = mapped_column(ForeignKey("laboratories.id", ondelete="SET NULL"), nullable=True)
    batch_id: Mapped[int | None] = mapped_column(ForeignKey("practical_batches.id", ondelete="SET NULL"), nullable=True)
    session_type: Mapped[str] = mapped_column(String(16), default="LECTURE")  # LECTURE/PRACTICAL/TUTORIAL/SEMINAR/PROJECT/OTHER
    is_substitute_override: Mapped[bool] = mapped_column(Boolean, default=False)
    effective_date = mapped_column(DateTime, nullable=True)  # set only on substitution overrides
    recurring_entry_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    notes: Mapped[str] = mapped_column(String(500), default="")
    status: Mapped[str] = mapped_column(String(16), default="ACTIVE")  # ACTIVE / CANCELLED
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    version: Mapped["TimetableVersion"] = relationship(back_populates="entries")


class TimetableGenerationJob(Base):
    __tablename__ = "timetable_generation_jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    academic_year_id: Mapped[int | None] = mapped_column(index=True, nullable=True)
    status: Mapped[str] = mapped_column(String(16), default="PENDING")  # PENDING/RUNNING/COMPLETED/FAILED
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    required_sessions: Mapped[int] = mapped_column(Integer, default=0)
    scheduled_sessions: Mapped[int] = mapped_column(Integer, default=0)
    unscheduled_sessions: Mapped[int] = mapped_column(Integer, default=0)
    # {stages: [{name, started_at, finished_at, detail}], stats: {...},
    #  conflicts: [...], unscheduled: [{reason, count, sessions: [...]}], suggestions: [...]}
    result: Mapped[dict] = mapped_column(JSON, default=dict)
    error: Mapped[str] = mapped_column(String(2000), default="")
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class TimetableConflict(Base):
    __tablename__ = "timetable_conflicts"

    id: Mapped[int] = mapped_column(primary_key=True)
    timetable_version_id: Mapped[int | None] = mapped_column(ForeignKey("timetable_versions.id", ondelete="CASCADE"), index=True, nullable=True)
    generation_job_id: Mapped[int | None] = mapped_column(index=True, nullable=True)
    conflict_type: Mapped[str] = mapped_column(String(32), index=True)  # FACULTY_CONFLICT/ROOM_CONFLICT/LAB_CONFLICT/DIVISION_CONFLICT/CAPACITY_CONFLICT/AVAILABILITY_CONFLICT/ELIGIBILITY_CONFLICT/WEEKLY_HOURS_CONFLICT/PRACTICAL_BATCH_CONFLICT
    severity: Mapped[str] = mapped_column(String(16), default="WARNING")  # CRITICAL/WARNING/INFORMATION
    description: Mapped[str] = mapped_column(String(500), default="")
    day_of_week: Mapped[str | None] = mapped_column(String(3), nullable=True)
    time_slot_id: Mapped[int | None] = mapped_column(nullable=True)
    faculty_id: Mapped[int | None] = mapped_column(nullable=True)
    room_id: Mapped[int | None] = mapped_column(nullable=True)
    laboratory_id: Mapped[int | None] = mapped_column(nullable=True)
    division_id: Mapped[int | None] = mapped_column(nullable=True)
    subject_id: Mapped[int | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String(16), default="OPEN")  # OPEN/RESOLVED/IGNORED
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class TimetableChange(Base):
    """Record of what exactly changed in an entry (smart modification)."""
    __tablename__ = "timetable_changes"

    id: Mapped[int] = mapped_column(primary_key=True)
    timetable_version_id: Mapped[int] = mapped_column(ForeignKey("timetable_versions.id", ondelete="CASCADE"), index=True)
    timetable_entry_id: Mapped[int] = mapped_column(index=True)
    changes: Mapped[dict] = mapped_column(JSON, default=dict)  # {field: {old: ..., new: ...}}
    reason: Mapped[str] = mapped_column(String(255), default="")
    change_kind: Mapped[str] = mapped_column(String(24), default="MANUAL")  # MANUAL/LOCAL_RESCHEDULE/PARTIAL_REGENERATION
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


Index("ix_entries_version_day_slot", TimetableEntry.timetable_version_id, TimetableEntry.day_of_week, TimetableEntry.time_slot_id)
Index("ix_entries_faculty", TimetableEntry.faculty_id)
Index("ix_entries_division", TimetableEntry.division_id)
