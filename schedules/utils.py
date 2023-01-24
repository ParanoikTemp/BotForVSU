from collections import defaultdict
from typing import Any, Callable, Iterable


def groupby_key(selector: Callable[[Any], Any], entries: Iterable[Any]) -> dict[Any, list[Any]]:
    result = defaultdict(list)

    for entry in entries:
        result[selector(entry)].append(entry)

    return result
