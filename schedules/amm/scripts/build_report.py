from argparse import ONE_OR_MORE, ArgumentParser, Namespace
from dataclasses import dataclass
import sys
from typing import Callable, Sequence
from schedules.models import ScheduleEntry
from schedules.amm.file_schedule_parser import FileScheduleParser
from schedules.utils import groupby_key


@dataclass(frozen=True, eq=True)
class EntryPosition:
    week_day: str
    group: str
    time: str

    def __str__(self) -> str:
        return f'{", ".join([self.week_day, self.group, self.time])}'


def parse_arguments() -> Namespace:
    parser = ArgumentParser()

    parser.add_argument('-s', '--subject', help='Displays a grouping by subjects.', action='store_true')
    parser.add_argument('-t', '--teacher', help='Displays a grouping by teachers.', action='store_true')
    parser.add_argument('-l', '--location', help='Displays a grouping by locations.', action='store_true')
    parser.add_argument('-v', '--verbose', help='Displays all group entries instead of the first one.', action='store_true')
    parser.add_argument('files', metavar='file', nargs=ONE_OR_MORE)

    return parser.parse_args()


def get_position(entry: ScheduleEntry) -> EntryPosition:
    return EntryPosition(entry.week_day.value, f'{entry.group.number} {entry.group.short_name}', f'{entry.time.start:%H.%M}')


def print_group(entries: Sequence[ScheduleEntry], name: str, selector: Callable[[ScheduleEntry], str | None], verbose: bool = False) -> None:
    groups = groupby_key(selector, entries)
    if groups:
        print(f'{name}: ')
        for key, entries in groups.items():
            print(f'\t {key if key else "None"}:')
            positions = (get_position(e) for e in entries)
            for position in positions:
                print(f'\t \t {position}')
                if not verbose:
                    break


def print_report(schedule_parser: FileScheduleParser, filename: str, group_subject: bool, group_teacher: bool, group_location: bool, verbose: bool) -> None:
    parse_result = schedule_parser.parse(filename)

    if parse_result.exceptions:
        print('Exceptions:')
        for exception in parse_result.exceptions:
            print(f'\t {exception.message}')

    if group_subject:
        print_group(parse_result.schedule, 'Subjects', lambda x: x.lesson.subject.short_name, verbose)

    if group_teacher:
        print_group(parse_result.schedule, 'Teachers', lambda x: x.lesson.teacher.second_name if x.lesson.teacher else None, verbose)

    if group_location:
        print_group(parse_result.schedule, 'Locations', lambda x: str(x.lesson.location.number) if x.lesson.location else None, verbose)

    print()


def main(args: Namespace) -> None:
    schedule_parser = FileScheduleParser()

    for file in args.files:
        print(f'File "{file}":')
        print_report(schedule_parser, file, args.subject, args.teacher, args.location, args.verbose)


if __name__ == '__main__':
    sys.stdin.reconfigure(encoding='utf-8')  # type: ignore
    sys.stdout.reconfigure(encoding='utf-8')  # type: ignore
    main(parse_arguments())
