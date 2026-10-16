from datetime import datetime

from .errors import InvalidEventError, InvalidTimestampError


def make_event(raw: dict[str, str], line_number: int) -> dict:

    if not isinstance(raw, dict):
        raise InvalidEventError(
            f"Некорректное событие в строке {line_number}"
        )

    timestamp_raw = raw.get("timestamp") 
    level_raw = raw.get("level") 
    source_raw = raw.get("source")
    message_raw = raw.get("message")

    if not isinstance(timestamp_raw, str) or not timestamp_raw:
        raise InvalidTimestampError(f"Некорректная дата/время в строке {line_number}")

    if not isinstance(level_raw, str) or not level_raw or \
        level_raw not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        raise InvalidEventError(f"Некорректный уровень в строке {line_number}")

    if not isinstance(source_raw, str) or not source_raw:
        raise InvalidEventError(f"Некорректный источник в строке {line_number}")
    
    if not isinstance(message_raw, str):
        raise InvalidEventError(f"Некорректное сообщение в строке {line_number}")

    try:
        timestamp = datetime.fromisoformat(timestamp_raw)
    except ValueError:
        raise InvalidTimestampError(f"Неверный формат записи времени в строке {line_number}")

    return {'timestamp': timestamp,
            'level': level_raw,
            'source': source_raw,
            'message': message_raw} 
