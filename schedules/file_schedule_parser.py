from abc import ABC, abstractmethod
from schedules.models import ScheduleParseResult


class FileScheduleParser(ABC):
    @abstractmethod
    def parse(self, filename: str) -> ScheduleParseResult:
        pass
