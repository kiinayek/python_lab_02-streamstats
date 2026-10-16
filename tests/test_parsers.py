from datetime import datetime

import pytest

from streamstats.analysis import ini_stat, top_sources, update_stat
from streamstats.errors import InvalidEventError, InvalidTimestampError
from streamstats.parsers import make_event
from streamstats.readers import read_file


def test_valid_event():
    """Проверка создания корректного события"""
    raw = {
        "timestamp": "2026-10-13T10:00:00",
        "level": "INFO",
        "source": "server",
        "message": "Запуск"
    }

    event = make_event(raw, 1)

    assert event["level"] == "INFO"
    assert event["source"] == "server"
    assert event["message"] == "Запуск"
    assert event["timestamp"].isoformat() == "2026-10-13T10:00:00"


def test_invalid_level():
    """Проверка обработки некорректного уровня события"""
    raw = {
        "timestamp": "2026-10-13T10:00:00",
        "level": "WRONG",
        "source": "server",
        "message": "Ошибка"
    }

    with pytest.raises(InvalidEventError):
        make_event(raw, 2)


def test_invalid_timestamp():
    """Проверка обработки некорректных дата/время"""
    raw = {
        "timestamp": "not-a-date",
        "level": "INFO",
        "source": "server",
        "message": "Ошибка"
    }

    with pytest.raises(InvalidTimestampError):
        make_event(raw, 3)


def test_invalid_source():
    """Проверка обработки некорректного источника события"""
    raw = {
        "timestamp": "2026-10-13T10:00:00",
        "level": "INFO",
        "source": "",
        "message": "Запуск"
    }

    with pytest.raises(InvalidEventError):
        make_event(raw, 4)


def test_invalid_message():
    """Проверка обработки некорректного сообщения события"""
    raw = {
        "timestamp": "2026-10-13T10:00:00",
        "level": "INFO",
        "source": "server",
        "message": None
    }

    with pytest.raises(InvalidEventError):
        make_event(raw, 5)


def test_invalid_json_obj():
    """Проверка обработки некорректного JSON объекта"""
    raw = "im a json"

    with pytest.raises(InvalidEventError):
        make_event(raw, 6)


def test_read_csv(tmp_path):
    """Проверка чтения корректных событий из CSV файла"""
    file = tmp_path / "events.csv"
    file.write_text(
        "timestamp,level,source,message\n"
        "2026-10-13T10:00:00,INFO,server,Запуск\n"
        "2026-10-13T10:05:00,ERROR,database,Ошибка\n",
        encoding="utf-8"
    )

    stat = ini_stat()
    events = list(read_file("csv", str(file), False, stat))

    assert len(events) == 2
    assert events[0]["level"] == "INFO"
    assert events[0]["source"] == "server"
    assert events[1]["level"] == "ERROR"
    assert events[1]["source"] == "database"


def test_read_jsonl(tmp_path):
    """Проверка чтения корректных событий из JSONL файла"""
    file = tmp_path / "events.jsonl"
    file.write_text(
        '{"timestamp":"2026-10-13T10:00:00","level":"INFO",'
        '"source":"server","message":"Запуск"}\n'
        '{"timestamp":"2026-10-13T10:05:00","level":"ERROR",'
        '"source":"database","message":"Ошибка"}\n',
        encoding="utf-8"
    )

    stat = ini_stat()
    events = list(read_file("jsonl", str(file), False, stat))

    assert len(events) == 2
    assert events[0]["level"] == "INFO"
    assert events[0]["source"] == "server"
    assert events[1]["level"] == "ERROR"
    assert events[1]["source"] == "database"


def test_invalid_csv_without_skip(tmp_path):
    """Проверка ошибки при некорректной строке CSV без пропуска"""
    file = tmp_path / "bad.csv"
    file.write_text(
        "timestamp,level,source,message\n"
        "2026-10-13T10:00:00,INFO,server,Запуск\n"
        "2026-10-13T10:05:00,WRONG,server,Ошибка\n",
        encoding="utf-8"
    )

    stat = ini_stat()

    with pytest.raises(InvalidEventError):
        list(read_file("csv", str(file), False, stat))


def test_invalid_csv_with_skip(tmp_path):
    """Проверка пропуска некорректной строки CSV"""
    file = tmp_path / "bad.csv"
    file.write_text(
        "timestamp,level,source,message\n"
        "2026-10-13T10:00:00,INFO,server,Запуск\n"
        "2026-10-13T10:05:00,WRONG,server,Ошибка\n"
        "2026-10-13T10:10:00,ERROR,database,Сбой\n",
        encoding="utf-8"
    )

    stat = ini_stat()

    events = list(read_file("csv", str(file), True, stat))

    assert len(events) == 2
    assert stat["skipped"] == 1


def test_invalid_jsonl_without_skip(tmp_path):
    """Проверка ошибки при некорректной строке JSONL без пропуска"""
    file = tmp_path / "bad.jsonl"
    file.write_text(
        '{"timestamp":"2026-10-13T10:00:00","level":"INFO",'
        '"source":"server","message":"Запуск"}\n'
        '{"timestamp":"2026-10-13T10:05:00","level":"ERROR",'
        '"source":"server","message":"Ошибка"\n',
        encoding="utf-8"
    )

    stat = ini_stat()

    with pytest.raises(InvalidEventError):
        list(read_file("jsonl", str(file), False, stat))


def test_invalid_jsonl_with_skip(tmp_path):
    """Проверка пропуска некорректной строки JSONL"""
    file = tmp_path / "bad.jsonl"
    file.write_text(
        '{"timestamp":"2026-10-13T10:00:00","level":"INFO",'
        '"source":"server","message":"Запуск"}\n'
        '{"timestamp":"2026-10-13T10:05:00","level":"ERROR",'
        '"source":"server","message":"Ошибка"\n'
        '{"timestamp":"2026-10-13T10:10:00","level":"WARNING",'
        '"source":"database","message":"Предупреждение"}\n',
        encoding="utf-8"
    )

    stat = ini_stat()

    events = list(read_file("jsonl", str(file), True, stat))

    assert len(events) == 2
    assert stat["skipped"] == 1


def test_empty_csv(tmp_path):
    """Проверка обработки пустого CSV файла"""
    file = tmp_path / "empty.csv"
    file.write_text("", encoding="utf-8")

    stat = ini_stat()

    events = list(read_file("csv", str(file), False, stat))

    assert events == []
    assert stat["skipped"] == 0


def test_empty_jsonl(tmp_path):
    """Проверка обработки пустого JSONL файла"""
    file = tmp_path / "empty.jsonl"
    file.write_text("", encoding="utf-8")

    stat = ini_stat()

    events = list(read_file("jsonl", str(file), False, stat))

    assert events == []
    assert stat["skipped"] == 0


def test_csv_and_jsonl_same_stats(tmp_path):
    """Проверка совпадения статистики для одинаковых CSV и JSONL файлов"""
    csv_file = tmp_path / "events.csv"
    jsonl_file = tmp_path / "events.jsonl"

    csv_file.write_text(
        "timestamp,level,source,message\n"
        "2026-10-13T10:00:00,INFO,server,Запуск\n"
        "2026-10-13T10:05:00,ERROR,database,Ошибка\n",
        encoding="utf-8"
    )

    jsonl_file.write_text(
        '{"timestamp":"2026-10-13T10:00:00","level":"INFO",'
        '"source":"server","message":"Запуск"}\n'
        '{"timestamp":"2026-10-13T10:05:00","level":"ERROR",'
        '"source":"database","message":"Ошибка"}\n',
        encoding="utf-8"
    )

    stat_csv = ini_stat()
    events_csv = read_file("csv", str(csv_file), False, stat_csv)
    update_stat(events_csv, stat_csv)

    stat_jsonl = ini_stat()
    events_jsonl = read_file("jsonl", str(jsonl_file), False, stat_jsonl)
    update_stat(events_jsonl, stat_jsonl)

    assert stat_csv == stat_jsonl


def test_top_sources():
    """Проверка определения топ-N источников ошибок"""
    stat = ini_stat()

    stat["error_sources"] = {
        "server": 3,
        "database": 5,
        "api": 2,
        "auth": 5,
        "cache": 1,
        "worker": 4,
        "frontend": 2
    }

    result = top_sources(stat)

    assert result == {
        "auth": 5,
        "database": 5,
        "worker": 4,
        "server": 3,
        "api": 2
    }


def test_first_and_last_timestamp():
    """Проверка определения первой и последней временной метки"""
    stat = ini_stat()

    events = [
        {
            "timestamp": datetime.fromisoformat("2026-10-13T12:00:00"),
            "level": "INFO",
            "source": "server",
            "message": "Третье"
        },
        {
            "timestamp": datetime.fromisoformat("2026-10-13T10:00:00"),
            "level": "ERROR",
            "source": "database",
            "message": "Первое"
        },
        {
            "timestamp": datetime.fromisoformat("2026-10-13T11:00:00"),
            "level": "WARNING",
            "source": "server",
            "message": "Второе"
        }
    ]

    update_stat(events, stat)

    assert stat["first_timestamp"] == datetime.fromisoformat(
        "2026-10-13T10:00:00"
    )
    assert stat["last_timestamp"] == datetime.fromisoformat(
        "2026-10-13T12:00:00"
    )


