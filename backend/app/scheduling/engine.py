"""CP-SAT based timetable generation engine.

Layer 1 (this file, initial slice): engine structure, assignment/result data
structures, candidate day/time-slot handling and basic helper methods.
Later layers add: model building, hard/soft constraints, staged solving,
unscheduled-session diagnosis and persistence.
"""
from dataclasses import dataclass, field
from datetime import datetime

from ortools.sat.python import cp_model

from app.scheduling.data_loader import SchedulingData, SessionSpec

# Room types acceptable for non-laboratory (theory/tutorial/...) sessions
THEORY_ROOM_TYPES = {"CLASSROOM", "SMART_CLASSROOM", "SEMINAR_HALL", "TUTORIAL_ROOM", "OTHER"}


@dataclass
class Assignment:
    """One chosen placement of a session in the solved timetable."""
    session_index: int
    day: str                 # MON..SUN
    slot_index: int          # index into data.slots (start slot)
    span: int                # consecutive teaching slots occupied
    faculty_id: int | None
    room_id: int | None
    laboratory_id: int | None


@dataclass
class EngineResult:
    assignments: list[Assignment] = field(default_factory=list)
    unscheduled: list[dict] = field(default_factory=list)   # filled by the diagnosis layer
    stats: dict = field(default_factory=dict)
    stages: list[dict] = field(default_factory=list)        # filled by the staged-execution layer
    solver_status: str = "UNKNOWN"
    objective_value: int = 0


class TimetableEngine:
    """Constraint-programming timetable generator.

    Reads everything from a SchedulingData snapshot loaded from PostgreSQL.
    Variable dictionaries (filled in the model-building layer):
      x[(i, d, j)]        session i assigned to day d starting at slot j
      f[(i, d, j, fac)]   faculty choice for that placement
      r[(i, d, j, res)]   room/laboratory choice for that placement
      unsched[i]          session i left unscheduled
    """

    def __init__(self, data: SchedulingData, time_limit: float = 30.0):
        self.data = data
        self.time_limit = time_limit
        self.model: cp_model.CpModel = cp_model.CpModel()
        self.x: dict = {}
        self.f: dict = {}
        self.r: dict = {}
        self.unsched: dict = {}
        self.solver: cp_model.CpSolver | None = None
        self._valid_start_cache: dict[int, list[int]] = {}

    # ------------------------------------------------------------------
    # Candidate day/time-slot handling
    # ------------------------------------------------------------------
    def _contiguous(self, j: int, span: int) -> bool:
        """True when slots j..j+span-1 are back-to-back teaching periods
        (no break in between) and all exist."""
        slots = self.data.slots
        if j < 0 or j + span > len(slots):
            return False
        for k in range(j, j + span - 1):
            if slots[k].end_time != slots[k + 1].start_time:
                return False
        return True

    def valid_starts(self, span: int) -> list[int]:
        """All slot indices at which a session spanning `span` teaching slots
        may start."""
        if span not in self._valid_start_cache:
            n = len(self.data.slots)
            self._valid_start_cache[span] = [j for j in range(n) if self._contiguous(j, span)]
        return self._valid_start_cache[span]

    def covered_slots(self, j: int, span: int) -> list[int]:
        """Slot indices occupied by a session starting at j with the given span."""
        return list(range(j, j + span))

    # ------------------------------------------------------------------
    # Basic candidate helper methods
    # ------------------------------------------------------------------
    def _slot_available(self, faculty_id: int, day: str, j: int) -> bool:
        """Faculty availability: the slot's time window must fit inside one of
        the faculty's available windows for that weekday. No availability
        configured -> treated as unavailable."""
        windows = self.data.availability.get(faculty_id, {}).get(day)
        if not windows:
            return False
        slot = self.data.slots[j]
        for start, end in windows:
            if start <= slot.start_time and slot.end_time <= end:
                return True
        return False

    def _faculty_ok_for_start(self, faculty_id: int, day: str, j: int, span: int) -> bool:
        return all(self._slot_available(faculty_id, day, k) for k in self.covered_slots(j, span))

    def _faculty_capable(self, faculty_id: int, session_type: str) -> bool:
        fac = self.data.faculty_map.get(faculty_id)
        if fac is None:
            return False
        if session_type == "PRACTICAL":
            return bool(fac.can_take_practical)
        return bool(fac.can_take_theory)

    def _resource_candidates(self, session: SessionSpec) -> list[int]:
        """Room/laboratory ids with sufficient capacity for this session."""
        if session.needs_lab:
            return [lab.id for lab in self.data.labs if lab.capacity >= session.students]
        return [room.id for room in self.data.rooms if room.capacity >= session.students]
