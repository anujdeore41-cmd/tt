from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class College(Base):
    __tablename__ = "college"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), default="")
    department_name: Mapped[str] = mapped_column(String(255), default="")
    academic_year_label: Mapped[str] = mapped_column(String(64), default="")   # e.g. "2024-25"
    semester_label: Mapped[str] = mapped_column(String(64), default="")        # e.g. "Odd Semester"
    timezone: Mapped[str] = mapped_column(String(64), default="Asia/Kolkata")
    contact_email: Mapped[str] = mapped_column(String(255), default="")
    department_email: Mapped[str] = mapped_column(String(255), default="")
    setup_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    # wizard progress: {step_key: true}
    setup_progress: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
