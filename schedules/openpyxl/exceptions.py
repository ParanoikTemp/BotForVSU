from schedules.exceptions import ScheduleParseException
from dataclasses import dataclass


@dataclass(frozen=True)
class ExcelScheduleParseException(ScheduleParseException):
    sheet_name: str | None
    row_position: int | None
    column_position: int | None
