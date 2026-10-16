class StreamStatsError(Exception):
    """Базовый класс исключений"""


class UnsupportedFormatError(StreamStatsError):
    """Неподдерживаемый формат файла"""

class InvalidEventError(StreamStatsError):
    """Некорректное событие"""

class InvalidTimestampError(StreamStatsError):
    """Некорректные дата/время"""

class CLIConfigurationError(StreamStatsError):
    """Ошибки конфигурации командной строки"""

