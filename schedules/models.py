from dataclasses import dataclass
from enum import Enum
from datetime import time
from typing import Sequence
from schedules.exceptions import ScheduleParseException


class ScienceDegree(Enum):
    BACHELOR = 'Bachelor'
    MASTER = 'Master'


class TypeOfWeek(Enum):
    NUMERATOR = 'Numerator'
    DENOMINATOR = 'Denominator'


class SubGroup(Enum):
    FIRST = 'First'
    SECOND = 'Second'


class WeekDay(Enum):
    MONDAY = 'Monday'
    TUESDAY = 'Tuesday'
    WEDNESDAY = 'Wednesday'
    THURSDAY = 'Thursday'
    FRIDAY = 'Friday'
    SATURDAY = 'Saturday'
    SUNDAY = 'Sunday'


@dataclass(frozen=True, eq=True)
class Course:
    science_degree: ScienceDegree
    number: int | None = None


@dataclass(frozen=True, eq=True)
class Group:
    short_name: str
    number: int
    direction_code: str | None = None
    full_name: str | None = None


@dataclass(frozen=True, eq=True)
class Subject:
    short_name: str
    full_name: str | None = None


@dataclass(frozen=True, eq=True)
class Teacher:
    second_name: str
    first_name: str | None = None
    middle_name: str | None = None


@dataclass(frozen=True, eq=True)
class Location:
    annex: bool
    remote: bool
    number: int | None = None


@dataclass(frozen=True, eq=True)
class Lesson:
    subject: Subject
    teacher: Teacher | None = None
    location: Location | None = None


@dataclass(frozen=True, eq=True)
class Time:
    start: time
    stop: time


@dataclass(frozen=True, eq=True)
class ScheduleEntry:
    course: Course
    group: Group
    time: Time
    week_day: WeekDay
    lesson: Lesson
    type_of_week: TypeOfWeek
    sub_group: SubGroup


@dataclass(frozen=True, eq=True)
class ScheduleParseResult:
    schedule: Sequence[ScheduleEntry]
    exceptions: Sequence[ScheduleParseException]
