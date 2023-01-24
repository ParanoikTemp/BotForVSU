from typing import Sequence
from schedules.exceptions import ScheduleParseException
from schedules.file_schedule_parser import ScheduleParseResult, FileScheduleParser as __FileScheduleParser
from openpyxl import Workbook, load_workbook
from openpyxl.worksheet.worksheet import Worksheet
from schedules.openpyxl.exceptions import ExcelScheduleParseException
from schedules.models import *
from numpy import ndarray
from datetime import datetime
import re
from schedules.openpyxl.extension import ZeroBasedCellIndex, build_cells_matrix, enumerate_cell_ranges


class FileScheduleParser(__FileScheduleParser):
    COURSE_ROW_INDEX = 0
    COURSE_COLUMN_INDEX = 0
    TIME_ROW_INDEX = 2
    TIME_COLUMN_INDEX = 1
    WEEKDAY_ROW_INDEX = 2
    WEEKDAY_COLUMN_INDEX = 0
    LESSON_ROW_INDEX = 2
    LESSON_COLUMN_INDEX = 2
    DIRECTION_ROW_INDEX = 1
    GROUP_COLUMN_ROW = 0
    GROUP_COLUMN_INDEX = 2

    def parse(self, filename: str) -> ScheduleParseResult:
        workbook = self._read_workbook(filename)

        schedule, exceptions = [], []
        for sheet in workbook.worksheets:
            sheet_schedule, sheet_exceptions = self._parse_sheet(sheet)
            schedule += sheet_schedule
            exceptions += sheet_exceptions

        return ScheduleParseResult(schedule, exceptions)

    def _read_workbook(self, filename: str) -> Workbook:
        return load_workbook(filename, read_only=True)

    def _parse_sheet(self, sheet: Worksheet) -> tuple[Sequence[ScheduleEntry], Sequence[ScheduleParseException]]:
        cells_matrix = build_cells_matrix(sheet)

        time_table = ndarray(cells_matrix.shape, dtype=object)
        errors = []
        for cell_range in enumerate_cell_ranges(cells_matrix):
            cell_range = [*sorted(cell_range)]

            try:
                entity = self._parse_entity(cells_matrix, cell_range)

                if entity is None:
                    continue

                for i, j in cell_range:
                    time_table[i][j] = entity
            except ExcelScheduleParseException as ex:
                errors.append(ex)
            except ScheduleParseException as ex:
                i, j = cell_range[0]
                errors.append(ExcelScheduleParseException(
                    ex.message, sheet.title, i, j))

        self._fix_time_gaps(time_table)

        return self._get_schedule_entries(time_table), errors

    def _parse_entity(self, cells_matrix: ndarray, cell_range: Sequence[ZeroBasedCellIndex]) -> Course | WeekDay | Time | Group | Lesson | None:
        value = self._build_value_in_cell_range(cells_matrix, cell_range)

        if not value:
            return None

        i, j = cell_range[0]

        # Parse course number
        if i in (FileScheduleParser.COURSE_ROW_INDEX, FileScheduleParser.DIRECTION_ROW_INDEX) and j in (FileScheduleParser.COURSE_COLUMN_INDEX, FileScheduleParser.TIME_COLUMN_INDEX):
            return self._parse_course(value)

        # Parse week day
        if i >= FileScheduleParser.WEEKDAY_ROW_INDEX and j == FileScheduleParser.WEEKDAY_COLUMN_INDEX:
            return self._parse_week_day(value)

        # Parse time
        if i >= FileScheduleParser.TIME_ROW_INDEX and j == FileScheduleParser.TIME_COLUMN_INDEX:
            return self._parse_time(value)

        # Parse group
        if i in (FileScheduleParser.GROUP_COLUMN_ROW, FileScheduleParser.DIRECTION_ROW_INDEX) and j >= FileScheduleParser.GROUP_COLUMN_INDEX:
            return self._parse_group(value)

        # Parse lessom
        if i >= FileScheduleParser.LESSON_ROW_INDEX and j >= FileScheduleParser.LESSON_COLUMN_INDEX:
            return self._parse_lesson(value)

        # Unknown value
        raise ScheduleParseException(
            f'The value "{value}" does not belong to any of the groups.')

    def _build_value_in_cell_range(self, cells_matrix: ndarray, cell_range: Sequence[ZeroBasedCellIndex]) -> str:
        prev_i = None
        str_parts = []

        for i, j in cell_range:
            if i != prev_i:
                prev_i = i
                separator = ' ' if prev_i is None else '\n'
            else:
                separator = ' '

            value = cells_matrix[i][j].value

            if value is not None:
                value = str(value).strip()

            if value:
                str_parts += [f'{value}{separator}']

        return ''.join(str_parts).strip()

    def _parse_course(self, value: str) -> Course:
        try:
            NUMBER_PATTERN = re.compile(r'\d+')
            match = NUMBER_PATTERN.search(value)

            return Course(ScienceDegree.BACHELOR, int(match[0])) if match else Course(ScienceDegree.MASTER)
        except:
            raise ScheduleParseException(
                f'The value "{value}" can\'t parsed be as course.')

    def _parse_week_day(self, value: str) -> WeekDay:
        try:
            WEEK_DAYS_MAPPER = {
                'ПОНЕДЕЛЬНИК': WeekDay.MONDAY,
                'ВТОРНИК': WeekDay.TUESDAY,
                'СРЕДА': WeekDay.WEDNESDAY,
                'ЧЕТВЕРГ': WeekDay.THURSDAY,
                'ПЯТНИЦА': WeekDay.FRIDAY,
                'СУББОТА': WeekDay.SATURDAY,
                'ВОСКРЕСЕНЬЕ': WeekDay.SUNDAY
            }
            return WEEK_DAYS_MAPPER[value.upper()]
        except:
            raise ScheduleParseException(
                f'The value "{value}" can\'t be parsed as week day.')

    def _parse_time(self, value) -> Time:
        try:
            parts = [datetime.strptime(part, '%H.%M').time()
                     for part in value.split('-')]
            return Time(parts[0], parts[1])
        except:
            raise ScheduleParseException(
                f'The value "{value}" can\'t parsed be as time.')

    def _parse_group(self, value) -> Group:
        try:
            BACHELOR_PATTERN = re.compile(r'(\d+).*?\d+\s*?ч(.*)', re.S)
            match = BACHELOR_PATTERN.search(value)

            if match:
                return Group(match[2].strip(), int(match[1]))

            MASTER_PATTERN = re.compile(r'(\d+)гр?\s*(\w*)')
            match = MASTER_PATTERN.search(value)

            if match:
                return Group(match[2].strip(), int(match[1]))
        except:
            raise ScheduleParseException(
                f'The value "{value}" can\'t parsed be as group.')

        raise ScheduleParseException(
            f'The value "{value}" can\'t parsed be as group.')

    def _parse_lesson(self, value: str) -> Lesson:
        try:
            MULTISPACE_PATTERN = re.compile(r'\s+', re.S)
            LOCATION_PATTERN = re.compile(r'дист\.?|\d+[Пп]?', re.S)
            match = LOCATION_PATTERN.search(value)

            if match:
                location_starts, location_ends = match.regs[0]

                location = self._parse_location(match[0])
                subject = MULTISPACE_PATTERN.sub(
                    ' ', value[0:location_starts]).strip()
                teacher = value[location_ends +
                                  1:].replace('\n', '').replace(' ', '')

                return Lesson(Subject(subject), Teacher(teacher), location)

            KNOWN_LESSONS = {
                'физ культура',
                'физическая культура',
                'военная подготовка'
            }
            lesson = MULTISPACE_PATTERN.sub(
                ' ', value.replace('\n', ' ')).lower()

            if lesson in KNOWN_LESSONS:
                return Lesson(Subject(lesson.title()))
        except:
            raise ScheduleParseException(
                f'The value "{value}" can\'t parsed be as lesson.')

        raise ScheduleParseException(
            f'The value "{value}" can\'t parsed be as lesson.')

    def _parse_location(self, value: str) -> Location:
        try:
            value = value.upper()

            annex = 'П' in value
            remote = 'ДИСТ' in value
            try:
                number = int(value.replace('П', ''))
            except:
                number = None

            return Location(annex, remote, number)
        except:
            raise ScheduleParseException(
                f'The value "{value}" can\'t parsed be as location.')

    def _fix_time_gaps(self, time_table: ndarray) -> None:
        prev_value = None
        for i in range(FileScheduleParser.TIME_ROW_INDEX, time_table.shape[0]):
            value = time_table[i][FileScheduleParser.TIME_COLUMN_INDEX]

            if value is None:
                time_table[i][FileScheduleParser.TIME_COLUMN_INDEX] = prev_value
            else:
                prev_value = value

    def _get_schedule_entries(self, time_table: ndarray) -> Sequence[ScheduleEntry]:
        COURSE = time_table[FileScheduleParser.COURSE_ROW_INDEX][FileScheduleParser.COURSE_COLUMN_INDEX]
        WEEKDAY = time_table[FileScheduleParser.WEEKDAY_ROW_INDEX][FileScheduleParser.WEEKDAY_COLUMN_INDEX]

        entries = []
        for i in range(FileScheduleParser.LESSON_ROW_INDEX, time_table.shape[0]):
            for j in range(FileScheduleParser.LESSON_COLUMN_INDEX, time_table.shape[1]):
                lesson = time_table[i][j]

                if lesson is None:
                    continue

                group = time_table[FileScheduleParser.GROUP_COLUMN_ROW][j]
                time = time_table[i][FileScheduleParser.TIME_COLUMN_INDEX]
                type_of_week = TypeOfWeek.NUMERATOR if i % 2 == 0 else TypeOfWeek.DENOMINATOR
                subgroup = SubGroup.FIRST if j % 2 == 0 else SubGroup.SECOND

                entries.append(ScheduleEntry(
                    COURSE, group, time, WEEKDAY, lesson, type_of_week, subgroup))

        return entries
