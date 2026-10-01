from datetime import date, datetime
from sqlalchemy import String, Date, DateTime, ForeignKey, UniqueConstraint, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AcademicYear(Base):
    __tablename__ = "academic_years"
    __table_args__ = (UniqueConstraint("name", name="uq_academic_year_name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), index=True)  # e.g. "1st Year", "2nd Year"
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(16), default="ACTIVE")  # ACTIVE / INACTIVE / ARCHIVED
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    divisions: Mapped[list["Division"]] = relationship(back_populates="academic_year", lazy="selectin")
    semesters: Mapped[list["Semester"]] = relationship(back_populates="academic_year", lazy="selectin")


class Semester(Base):
    __tablename__ = "semesters"
    __table_args__ = (UniqueConstraint("academic_year_id", "name", name="uq_semester_name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    academic_year_id: Mapped[int] = mapped_column(ForeignKey("academic_years.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(64))
    number: Mapped[int] = mapped_column(default=1)
    status: Mapped[str] = mapped_column(String(16), default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    academic_year: Mapped["AcademicYear"] = relationship(back_populates="semesters")


class Division(Base):
    __tablename__ = "divisions"
    __table_args__ = (UniqueConstraint("academic_year_id", "name", name="uq_division_name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    academic_year_id: Mapped[int] = mapped_column(ForeignKey("academic_years.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(64), index=True)  # e.g. "Division A"
    capacity: Mapped[int | None] = mapped_column(nullable=True)  # student strength
    status: Mapped[str] = mapped_column(String(16), default="ACTIVE")
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    academic_year: Mapped["AcademicYear"] = relationship(back_populates="divisions")
