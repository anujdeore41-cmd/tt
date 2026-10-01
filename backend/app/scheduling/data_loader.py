"""Loads every piece of scheduling data from PostgreSQL. The engine never
uses hard-coded data — everything comes from the database."""
from dataclasses import dataclass, field
from datetime import time as dtime

from sqlalchemy.orm import Session

from app.models import (
    WorkingDay, ScheduleConfiguration, TimeSlot, Break,
    AcademicYear, Division, Subject, FacultySubject, Faculty, FacultyAvailability,
    Room, Laboratory, PracticalBatch,
)


@dataclass
class SessionSpec:
    index: int
    division_id: int
    academic_year_id: int
    subject_id: int
    session_type: str           # LECTURE / PRACTICAL / TUTORIAL / ...
    batch_id: int | None        # set for batched practical sessions
    students: int               # expected attendees
    span: int                   # number of consecutive teaching slots occupied
    allowed_faculty: list[int] = field(default_factory=list)
    needs_lab: bool = False
    preferred_room_id: int | None = None
    preferred_laboratory_id: int | None = None


@dataclass
class SchedulingData:
    config: ScheduleConfiguration
    working_days: list[str]                 # ordered day codes e.g. ["MON","TUE",...]
    slots: list[TimeSlot]                   # ordered teaching slots (the daily pattern)
    all_slots: list[TimeSlot]               # every slot including breaks (for reference)
    divisions: list[Division]
    academic_years: dict[int, AcademicYear]
    sessions: list[SessionSpec]
    faculty: list[Faculty]
    rooms: list[Room]
    labs: list[Laboratory]
    availability: dict[int, dict[str, list[tuple[dtime, dtime]]]]  # fac_id -> day -> windows
    batch_map: dict[int, PracticalBatch]
    division_map: dict[int, Division]
    subject_map: dict[int, Subject]
    faculty_map: dict[int, Faculty]
    room_map: dict[int, Room]
    lab_map: dict[int, Laboratory]
    lectures_per_slot: int = 60  # minutes per teaching slot


def load_scheduling_data(db: Session, academic_year_id: int | None = None) -> SchedulingData:
    config = db.query(ScheduleConfiguration).first()
    if config is None:
        raise ValueError("Schedule configuration is missing")

    working_day_rows = db.query(WorkingDay).filter(WorkingDay.is_working == True).order_by(WorkingDay.sequence).all()  # noqa: E712
    working_days = [wd.day_of_week for wd in working_day_rows]

    all_slots = db.query(TimeSlot).order_by(TimeSlot.sequence).all()
    slots = [s for s in all_slots if s.is_teaching_period]

    year_q = db.query(AcademicYear).filter(AcademicYear.status == "ACTIVE")
    if academic_year_id:
        year_q = year_q.filter(AcademicYear.id == academic_year_id)
    years = year_q.all()
    year_ids = [y.id for y in years]
    divisions = db.query(Division).filter(
        Division.status == "ACTIVE", Division.academic_year_id.in_(year_ids)
    ).order_by(Division.academic_year_id, Division.name).all() if year_ids else []

    division_map = {d.id: d for d in divisions}
    subject_rows = db.query(Subject).filter(Subject.status == "ACTIVE").all()
    subject_map = {s.id: s for s in subject_rows}

    # faculty eligibility map: subject_id -> [faculty_ids]
    eligibility_rows = db.query(FacultySubject).all()
    subject_faculty: dict[int, list[int]] = {}
    for row in eligibility_rows:
        subject_faculty.setdefault(row.subject_id, []).append(row.faculty_id)

    faculty_rows = db.query(Faculty).filter(Faculty.status == "ACTIVE").all()
    faculty_map = {f.id: f for f in faculty_rows}

    availability: dict[int, dict[str, list[tuple[dtime, dtime]]]] = {}
    for av in db.query(FacultyAvailability).filter(FacultyAvailability.is_available == True).all():  # noqa: E712
        availability.setdefault(av.faculty_id, {}).setdefault(av.day_of_week, []).append(
            (av.start_time, av.end_time)
        )

    rooms = db.query(Room).filter(Room.status == "ACTIVE", Room.is_available == True).order_by(Room.room_number).all()  # noqa: E712
    labs = db.query(Laboratory).filter(Laboratory.status == "ACTIVE", Laboratory.is_available == True).order_by(Laboratory.lab_number).all()  # noqa: E712
    room_map = {r.id: r for r in rooms}
    lab_map = {l.id: l for l in labs}

    batch_rows = db.query(PracticalBatch).filter(PracticalBatch.status == "ACTIVE").all()
    batch_map = {b.id: b for b in batch_rows}
    batches_by_division: dict[int, list[PracticalBatch]] = {}
    for b in batch_rows:
        if b.division_id in division_map:
            batches_by_division.setdefault(b.division_id, []).append(b)

    default_capacity = 60
    lectures_per_slot = config.lecture_duration_minutes or 60

    sessions: list[SessionSpec] = []
    idx = 0
    for division in divisions:
        div_subjects = [s for s in subject_rows
                        if any(d.id == division.id for d in s.divisions)]
        students = division.capacity or default_capacity
        for subject in div_subjects:
            elig = [fid for fid in subject_faculty.get(subject.id, []) if fid in faculty_map]
            needs_lab = subject.subject_type == "PRACTICAL"
            span = 1
            if needs_lab:
                dur = subject.practical_duration_minutes or config.default_practical_duration_minutes or lectures_per_slot
                span = max(1, -(-dur // lectures_per_slot))  # ceil division

            batches_for_subject = []
            if needs_lab and (subject.practical_batches_count or 0) > 1:
                db_batches = batches_by_division.get(division.id, [])
                batches_for_subject = db_batches[: subject.practical_batches_count]

            if batches_for_subject:
                # one session group per batch; each batch attends its own sessions
                for batch in batches_for_subject:
                    for _ in range(subject.weekly_required_sessions):
                        sessions.append(SessionSpec(
                            index=idx, division_id=division.id, academic_year_id=division.academic_year_id,
                            subject_id=subject.id, session_type="PRACTICAL", batch_id=batch.id,
                            students=batch.capacity or students, span=span, allowed_faculty=elig,
                            needs_lab=True,
                            preferred_laboratory_id=subject.preferred_laboratory_id or batch.laboratory_id,
                        ))
                        idx += 1
            else:
                for _ in range(subject.weekly_required_sessions):
                    sessions.append(SessionSpec(
                        index=idx, division_id=division.id, academic_year_id=division.academic_year_id,
                        subject_id=subject.id, session_type=subject.subject_type, batch_id=None,
                        students=students, span=span, allowed_faculty=elig, needs_lab=needs_lab,
                        preferred_room_id=subject.preferred_room_id,
                        preferred_laboratory_id=subject.preferred_laboratory_id,
                    ))
                    idx += 1

    return SchedulingData(
        config=config, working_days=working_days, slots=slots, all_slots=all_slots,
        divisions=divisions, academic_years={y.id: y for y in years},
        sessions=sessions, faculty=faculty_rows, rooms=rooms, labs=labs,
        availability=availability, batch_map=batch_map, division_map=division_map,
        subject_map=subject_map, faculty_map=faculty_map, room_map=room_map, lab_map=lab_map,
        lectures_per_slot=lectures_per_slot,
    )
