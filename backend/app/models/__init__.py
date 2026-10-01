from app.models.user import User, Role, UserRole
from app.models.college import College
from app.models.academic import AcademicYear, Semester, Division
from app.models.subject import Subject, SubjectCreditRule, SubjectDivision, FacultySubject
from app.models.faculty import Faculty, FacultyDesignation, FacultyAvailability
from app.models.room import Room, Laboratory, PracticalBatch
from app.models.schedule import WorkingDay, ScheduleConfiguration, Break, TimeSlot
from app.models.timetable import (
    TimetableVersion, TimetableEntry, TimetableGenerationJob, TimetableConflict, TimetableChange,
)
from app.models.absence import FacultyAbsence, AffectedLecture
from app.models.substitute import SubstituteRequest, SubstituteResponse
from app.models.misc import Notification, NotificationPreference, AuditLog, Setting
from app.models.misc import Attachment, EmailLog, TimetableQuery

__all__ = [
    "User", "Role", "UserRole",
    "College",
    "AcademicYear", "Semester", "Division",
    "Subject", "SubjectCreditRule", "SubjectDivision", "FacultySubject",
    "Faculty", "FacultyDesignation", "FacultyAvailability",
    "Room", "Laboratory", "PracticalBatch",
    "WorkingDay", "ScheduleConfiguration", "Break", "TimeSlot",
    "TimetableVersion", "TimetableEntry", "TimetableGenerationJob", "TimetableConflict", "TimetableChange",
    "FacultyAbsence", "AffectedLecture",
    "SubstituteRequest", "SubstituteResponse",
    "Notification", "NotificationPreference", "AuditLog", "Setting",
    "Attachment", "EmailLog", "TimetableQuery",
]