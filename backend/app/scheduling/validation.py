"""Schedule configuration validation — run before timetable generation."""
from sqlalchemy.orm import Session

from app.models import (
    College, WorkingDay, ScheduleConfiguration, TimeSlot, Break,
    AcademicYear, Division, Subject, Faculty, FacultySubject, FacultyAvailability,
    Room, Laboratory, PracticalBatch, SubjectCreditRule,
)


def get_schedule_config(db: Session) -> ScheduleConfiguration | None:
    return db.query(ScheduleConfiguration).first()


def get_college(db: Session) -> College | None:
    return db.query(College).first()


def validate_schedule_config(db: Session) -> list[dict]:
    """Validate timing/break configuration in detail."""
    issues: list[dict] = []
    config = get_schedule_config(db)

    working_days = db.query(WorkingDay).filter(WorkingDay.is_working == True).all()  # noqa: E712
    if not working_days:
        issues.append({
            "code": "NO_WORKING_DAYS", "severity": "ERROR",
            "message": "No working days have been configured.",
            "fix_hint": "settings/working-days",
        })
    if config and config.working_days_count != len(working_days):
        issues.append({
            "code": "WORKING_DAYS_MISMATCH", "severity": "ERROR",
            "message": f"Configured working day count ({config.working_days_count}) does not match "
                       f"the number of selected days ({len(working_days)}).",
            "fix_hint": "settings/working-days",
        })

    if config is None:
        issues.append({
            "code": "NO_SCHEDULE_CONFIG", "severity": "ERROR",
            "message": "Schedule configuration is missing (college hours and lecture duration).",
            "fix_hint": "settings/time-slots",
        })
        return issues

    if config.college_start_time is None or config.college_end_time is None:
        issues.append({
            "code": "MISSING_COLLEGE_HOURS", "severity": "ERROR",
            "message": "College start time and end time must be set.",
            "fix_hint": "settings/time-slots",
        })
    elif config.college_end_time <= config.college_start_time:
        issues.append({
            "code": "INVALID_COLLEGE_HOURS", "severity": "ERROR",
            "message": "College end time must be after the start time.",
            "fix_hint": "settings/time-slots",
        })

    if config.lecture_duration_minutes is None or config.lecture_duration_minutes <= 0:
        issues.append({
            "code": "INVALID_LECTURE_DURATION", "severity": "ERROR",
            "message": "Standard lecture duration must be greater than 0.",
            "fix_hint": "settings/time-slots",
        })

    breaks = db.query(Break).all()
    for brk in breaks:
        if brk.duration_minutes <= 0:
            issues.append({
                "code": "INVALID_BREAK_DURATION", "severity": "ERROR",
                "message": f"Break '{brk.name}' has a duration of {brk.duration_minutes} minutes; it must be > 0.",
                "fix_hint": "settings/breaks",
            })

    if config.college_start_time and config.college_end_time and config.lecture_duration_minutes:
        from app.services.time_slots import generate_slot_preview
        brk_dicts = [{"name": b.name, "duration_minutes": b.duration_minutes,
                      "after_lectures": b.after_lectures, "sequence": b.sequence, "break_kind": b.break_kind}
                     for b in breaks]
        slots, all_placed = generate_slot_preview(
            config.college_start_time, config.college_end_time, config.lecture_duration_minutes, brk_dicts
        )
        teaching = [s for s in slots if s["is_teaching_period"]]
        if not teaching:
            issues.append({
                "code": "NO_TEACHING_PERIODS", "severity": "ERROR",
                "message": "The configured hours and breaks produce no teaching periods.",
                "fix_hint": "settings/time-slots",
            })
        if not all_placed:
            issues.append({
                "code": "BREAK_POSITION_INVALID", "severity": "ERROR",
                "message": "One or more breaks occur after the last lecture of the day and can never be placed.",
                "fix_hint": "settings/breaks",
            })
    return issues


def validate_readiness(db: Session) -> list[dict]:
    """Full pre-generation checklist. Returns a list of issues
    ({code, severity, message, fix_hint})."""
    issues = validate_schedule_config(db)

    college = get_college(db)
    if college is None or not college.name:
        issues.append({
            "code": "NO_COLLEGE", "severity": "ERROR",
            "message": "College information has not been configured.",
            "fix_hint": "setup/college",
        })

    years = db.query(AcademicYear).filter(AcademicYear.status == "ACTIVE").all()
    if not years:
        issues.append({
            "code": "NO_ACADEMIC_YEARS", "severity": "ERROR",
            "message": "No academic years have been configured.",
            "fix_hint": "academic/academic-years",
        })

    divisions = db.query(Division).filter(Division.status == "ACTIVE").all()
    if not divisions:
        issues.append({
            "code": "NO_DIVISIONS", "severity": "ERROR",
            "message": "No divisions have been configured.",
            "fix_hint": "academic/divisions",
        })

    subjects = db.query(Subject).filter(Subject.status == "ACTIVE").all()
    if not subjects:
        issues.append({
            "code": "NO_SUBJECTS", "severity": "ERROR",
            "message": "No subjects have been configured.",
            "fix_hint": "academic/subjects",
        })
    else:
        no_divisions = [s.name for s in subjects if not s.divisions]
        if no_divisions:
            issues.append({
                "code": "SUBJECTS_WITHOUT_DIVISIONS", "severity": "ERROR",
                "message": f"{len(no_divisions)} subject(s) are not assigned to any division: "
                           f"{', '.join(no_divisions[:5])}{'…' if len(no_divisions) > 5 else ''}.",
                "fix_hint": "academic/subjects",
            })
        no_faculty = [s.name for s in subjects if not s.eligible_faculty]
        if no_faculty:
            issues.append({
                "code": "SUBJECTS_WITHOUT_FACULTY", "severity": "ERROR",
                "message": f"{len(no_faculty)} subject(s) do not have eligible faculty assigned: "
                           f"{', '.join(no_faculty[:5])}{'…' if len(no_faculty) > 5 else ''}.",
                "fix_hint": "faculty/faculty-list",
            })

    rules = db.query(SubjectCreditRule).count()
    if rules == 0:
        issues.append({
            "code": "NO_CREDIT_RULES", "severity": "WARNING",
            "message": "No credit rules configured; weekly sessions rely on per-subject values.",
            "fix_hint": "academic/credits",
        })

    faculty = db.query(Faculty).filter(Faculty.status == "ACTIVE").all()
    if not faculty:
        issues.append({
            "code": "NO_FACULTY", "severity": "ERROR",
            "message": "No faculty members have been configured.",
            "fix_hint": "faculty/faculty-list",
        })

    rooms = db.query(Room).filter(Room.status == "ACTIVE", Room.is_available == True).all()  # noqa: E712
    if not rooms:
        issues.append({
            "code": "NO_ROOMS", "severity": "ERROR",
            "message": "No available classrooms have been configured.",
            "fix_hint": "resources/classrooms",
        })

    labs = db.query(Laboratory).filter(Laboratory.status == "ACTIVE", Laboratory.is_available == True).all()  # noqa: E712
    practical_subjects = [s for s in subjects if s.subject_type == "PRACTICAL"]
    if practical_subjects and not labs:
        issues.append({
            "code": "NO_LABS", "severity": "ERROR",
            "message": f"{len(practical_subjects)} practical subject(s) exist but no laboratories are configured.",
            "fix_hint": "resources/laboratories",
        })

    # Faculty availability: warn when a faculty has no availability rows at all
    if faculty:
        avail_faculty_ids = {row.faculty_id for row in db.query(FacultyAvailability.faculty_id).distinct()}
        missing = [f.name for f in faculty if f.id not in avail_faculty_ids]
        if missing:
            issues.append({
                "code": "FACULTY_WITHOUT_AVAILABILITY", "severity": "WARNING",
                "message": f"{len(missing)} faculty member(s) have no availability set: "
                           f"{', '.join(missing[:5])}{'…' if len(missing) > 5 else ''}. "
                           "They will be treated as unavailable for all periods.",
                "fix_hint": "faculty/faculty-availability",
            })

    batches_needed = [s for s in practical_subjects if (s.practical_batches_count or 0) > 1]
    if batches_needed:
        batch_divisions = {b.division_id for b in db.query(PracticalBatch).all()}
        missing_batches = []
        for s in batches_needed:
            for d in s.divisions:
                if d.id not in batch_divisions:
                    missing_batches.append(f"{s.name} / {d.name}")
        if missing_batches:
            issues.append({
                "code": "MISSING_PRACTICAL_BATCHES", "severity": "ERROR",
                "message": f"Practical batches missing for: {', '.join(missing_batches[:5])}"
                           f"{'…' if len(missing_batches) > 5 else ''}.",
                "fix_hint": "academic/practical-batches",
            })

    slots = db.query(TimeSlot).filter(TimeSlot.is_teaching_period == True).count()  # noqa: E712
    if slots == 0:
        issues.append({
            "code": "NO_TIME_SLOTS", "severity": "ERROR",
            "message": "Time slots have not been generated from the schedule configuration.",
            "fix_hint": "settings/time-slots",
        })

    return issues
