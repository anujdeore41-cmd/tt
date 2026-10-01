"""Dynamic time-slot generation from working days, college hours, lecture
duration and break configuration. No period is ever hard-coded."""
from datetime import datetime, time, timedelta

from sqlalchemy.orm import Session

from app.models import ScheduleConfiguration, TimeSlot, Break, WorkingDay


def _add_minutes(t: time, minutes: int) -> time:
    dt = datetime(2000, 1, 1, t.hour, t.minute, t.second) + timedelta(minutes=minutes)
    return dt.time()


def generate_slot_preview(
    start_time: time,
    end_time: time,
    lecture_duration: int,
    breaks: list[dict],
) -> tuple[list[dict], bool]:
    """Compute the day's slot sequence. Returns (slots, all_breaks_placed).

    Each break dict needs: name, duration_minutes, after_lectures.
    """
    ordered = sorted(breaks, key=lambda b: (b["after_lectures"], b.get("sequence", 0)))
    slots: list[dict] = []
    t = start_time
    lecture_count = 0
    placed = [False] * len(ordered)

    while True:
        if _add_minutes(t, lecture_duration) > end_time or t >= end_time:
            break
        lecture_count += 1
        slots.append({
            "start_time": t,
            "end_time": _add_minutes(t, lecture_duration),
            "slot_type": "LECTURE",
            "is_teaching_period": True,
            "label": f"Lecture {lecture_count}",
        })
        t = _add_minutes(t, lecture_duration)

        for i, brk in enumerate(ordered):
            if not placed[i] and brk["after_lectures"] == lecture_count:
                dur = brk["duration_minutes"]
                if _add_minutes(t, dur) <= end_time:
                    slots.append({
                        "start_time": t,
                        "end_time": _add_minutes(t, dur),
                        "slot_type": brk.get("break_kind", "BREAK"),
                        "is_teaching_period": False,
                        "label": brk["name"],
                    })
                    t = _add_minutes(t, dur)
                    placed[i] = True
    return slots, all(placed)


def regenerate_time_slots(db: Session, config: ScheduleConfiguration) -> list[TimeSlot]:
    """Delete existing slots and regenerate from the current configuration."""
    db.query(TimeSlot).delete()
    db.flush()

    breaks = [
        {
            "name": b.name,
            "duration_minutes": b.duration_minutes,
            "after_lectures": b.after_lectures,
            "sequence": b.sequence,
            "break_kind": b.break_kind,
        }
        for b in config.breaks
    ]
    slot_dicts, _ = generate_slot_preview(
        config.college_start_time, config.college_end_time, config.lecture_duration_minutes, breaks
    )

    break_by_pos: dict[int, list[Break]] = {}
    for b in config.breaks:
        break_by_pos.setdefault(b.after_lectures, []).append(b)

    slots: list[TimeSlot] = []
    lecture_count = 0
    for sd in slot_dicts:
        if sd["slot_type"] == "LECTURE":
            lecture_count += 1
            slot = TimeSlot(
                start_time=sd["start_time"], end_time=sd["end_time"], sequence=lecture_count,
                slot_type="LECTURE", is_teaching_period=True, label=f"Lecture {lecture_count}",
            )
        else:
            brks = break_by_pos.get(lecture_count, [])
            brk = None
            for cand in brks:
                if cand.name == sd["label"]:
                    brk = cand
                    break
            slot = TimeSlot(
                start_time=sd["start_time"], end_time=sd["end_time"], sequence=lecture_count,
                slot_type=sd["slot_type"], is_teaching_period=False,
                break_id=brk.id if brk else None, label=sd["label"],
            )
        db.add(slot)
        slots.append(slot)
    db.flush()
    return slots
