from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, UniqueConstraint, Boolean, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Subject(Base):
    __tablename__ = "subjects"
    __table_args__ = (UniqueConstraint("code", name="uq_subject_code"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(32), index=True)
    name: Mapped[str] = mapped_column(String(255))
    subject_type: Mapped[str] = mapped_column(String(16), default="THEORY")  # THEORY/PRACTICAL/TUTORIAL/SEMINAR/PROJECT/OTHER
    credits: Mapped[int] = mapped_column(Integer, default=1)
    weekly_required_sessions: Mapped[int] = mapped_column(Integer, default=1)  # per division (per batch for batched practicals)
    practical_duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    practical_batches_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    preferred_room_id: Mapped[int | None] = mapped_column(ForeignKey("rooms.id", ondelete="SET NULL"), nullable=True)
    preferred_laboratory_id: Mapped[int | None] = mapped_column(ForeignKey("laboratories.id", ondelete="SET NULL"), nullable=True)
    academic_year_id: Mapped[int] = mapped_column(ForeignKey("academic_years.id", ondelete="CASCADE"), index=True)
    status: Mapped[str] = mapped_column(String(16), default="ACTIVE")
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    divisions: Mapped[list["Division"]] = relationship(
        "Division", secondary="subject_divisions", lazy="selectin"
    )
    eligible_faculty: Mapped[list["Faculty"]] = relationship(
        "Faculty", secondary="faculty_subjects", lazy="selectin"
    )


class SubjectCreditRule(Base):
    __tablename__ = "subject_credit_rules"
    __table_args__ = (UniqueConstraint("credits", name="uq_credit_rule"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    credits: Mapped[int] = mapped_column(Integer, unique=True)
    weekly_hours: Mapped[int] = mapped_column(Integer)  # sessions per week suggested for this credit value
    label: Mapped[str] = mapped_column(String(128), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SubjectDivision(Base):
    __tablename__ = "subject_divisions"
    __table_args__ = (UniqueConstraint("subject_id", "division_id", name="uq_subject_division"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"), index=True)
    division_id: Mapped[int] = mapped_column(ForeignKey("divisions.id", ondelete="CASCADE"), index=True)


class FacultySubject(Base):
    """Faculty <-> Subject eligibility (many-to-many)."""
    __tablename__ = "faculty_subjects"
    __table_args__ = (UniqueConstraint("faculty_id", "subject_id", name="uq_faculty_subject"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    faculty_id: Mapped[int] = mapped_column(ForeignKey("faculty.id", ondelete="CASCADE"), index=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


Index("ix_subjects_year_type", Subject.academic_year_id, Subject.subject_type)
