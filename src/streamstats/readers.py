import csv
import json
import logging
from collections.abc import Iterator

from .errors import (
    InvalidEventError,
    InvalidTimestampError,
    UnsupportedFormatError,
)
from .parsers import make_event

logger = logging.getLogger(__name__)

def read_file(fileformat: str, filename: str, skip_invalid: bool, stat: dict) -> Iterator[dict]:
    with open(filename, encoding="utf-8", newline="") as file:

        if fileformat == "csv":
            reader = csv.DictReader(file)

            for line_num, raw in enumerate(reader, start=2):
                try:
                    yield make_event(raw, line_num)

                except (InvalidEventError, InvalidTimestampError):
                    if skip_invalid:
                        logger.warning(
                            "Пропущена некорректная строка %s в файле %s",
                            line_num,
                            filename
                        )
                        stat["skipped"] += 1
                        continue
                    raise

        elif fileformat == "jsonl":
            for line_num, line in enumerate(file, start=1):
                try:
                    raw = json.loads(line)
                    yield make_event(raw, line_num)
                    
                except json.JSONDecodeError:
                    if skip_invalid:
                        logger.warning(
                            "Пропущена некорректная строка %s в файле %s",
                            line_num,
                            filename
                        )
                        stat["skipped"] += 1
                        continue
                    raise InvalidEventError(f"Некорректный JSON в строке {line_num}")  
                
                except (InvalidEventError, InvalidTimestampError):
                    if skip_invalid:
                        logger.warning(
                            "Пропущена некорректная строка %s в файле %s",
                            line_num,
                            filename
                        )
                        stat["skipped"] += 1
                        continue
                    raise  

        else:
            raise UnsupportedFormatError(f"Неподдерживаемый формат {fileformat}")