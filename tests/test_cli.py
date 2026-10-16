import json

import pytest

from streamstats.__main__ import main
from streamstats.analysis import ini_stat
from streamstats.errors import InvalidEventError, InvalidTimestampError
from streamstats.readers import read_file


def test_cli_make_report(tmp_path):
    input_file = tmp_path / "events.csv"
    output_file = tmp_path / "report.json"

    input_file.write_text(
        "timestamp,level,source,message\n"
        "2026-10-13T10:00:00,INFO,server,Запуск\n"
        "2026-10-13T10:05:00,ERROR,database,Ошибка\n",
        encoding="utf-8"
    )

    result = main([
        "analyze",
        str(input_file),
        "--format",
        "csv",
        "--output",
        str(output_file)
    ])

    assert result == 0
    assert output_file.exists()

    report = json.loads(output_file.read_text(encoding="utf-8"))

    assert report["total"] == 2
    assert report["levels"]["INFO"] == 1
    assert report["levels"]["ERROR"] == 1


def test_cli_two_files(tmp_path):
    first_file = tmp_path / "first.csv"
    second_file = tmp_path / "second.csv"
    output_file = tmp_path / "report.json"

    first_file.write_text(
        "timestamp,level,source,message\n"
        "2026-10-13T10:00:00,INFO,server,Запуск\n",
        encoding="utf-8"
    )

    second_file.write_text(
        "timestamp,level,source,message\n"
        "2026-10-13T10:05:00,ERROR,database,Ошибка\n",
        encoding="utf-8"
    )

    result = main([
        "analyze",
        str(first_file),
        str(second_file),
        "--format",
        "csv",
        "--output",
        str(output_file)
    ])

    assert result == 0

    report = json.loads(output_file.read_text(encoding="utf-8"))

    assert report["total"] == 2
    assert report["levels"]["INFO"] == 1
    assert report["levels"]["ERROR"] == 1


def test_cli_skip_invalid(tmp_path):
    input_file = tmp_path / "bad.csv"
    output_file = tmp_path / "report.json"

    input_file.write_text(
        "timestamp,level,source,message\n"
        "2026-10-13T10:00:00,INFO,server,Запуск\n"
        "2026-10-13T10:05:00,WRONG,server,Ошибка\n"
        "2026-10-13T10:10:00,ERROR,database,Сбой\n",
        encoding="utf-8"
    )

    result = main([
        "analyze",
        str(input_file),
        "--format",
        "csv",
        "--output",
        str(output_file),
        "--skip-invalid"
    ])

    assert result == 0

    report = json.loads(output_file.read_text(encoding="utf-8"))

    assert report["total"] == 2
    assert report["skipped"] == 1


def test_cli_invalid_without_skip(tmp_path):
    input_file = tmp_path / "bad.csv"
    output_file = tmp_path / "report.json"

    input_file.write_text(
        "timestamp,level,source,message\n"
        "2026-10-13T10:00:00,INFO,server,Запуск\n"
        "2026-10-13T10:05:00,WRONG,server,Ошибка\n",
        encoding="utf-8"
    )

    result = main([
        "analyze",
        str(input_file),
        "--format",
        "csv",
        "--output",
        str(output_file)
    ])

    assert result == 2
    assert not output_file.exists()


def test_invalid_jsonl_line_number(tmp_path):
    file = tmp_path / "bad.jsonl"

    valid_line = (
        '{"timestamp":"2026-10-13T10:00:00","level":"INFO",'
        '"source":"server","message":"Запуск"}\n'
    )

    file.write_text(
        valid_line * 6
        + '{"timestamp":"2026-10-13T10:05:00","level":"ERROR",'
          '"source":"server","message":"Ошибка"\n',
        encoding="utf-8"
    )

    stat = ini_stat()

    with pytest.raises(InvalidEventError, match="7"):
        list(read_file("jsonl", str(file), False, stat))


def test_invalid_timestamp_line_number(tmp_path):
    file = tmp_path / "bad.jsonl"

    file.write_text(
        '{"timestamp":"2026-10-13T10:00:00","level":"INFO",'
        '"source":"server","message":"Запуск"}\n'
        '{"timestamp":"not-a-date","level":"ERROR",'
        '"source":"server","message":"Ошибка"}\n',
        encoding="utf-8"
    )

    stat = ini_stat()

    with pytest.raises(
        InvalidTimestampError,
        match=r"времени.*2"
    ):
        list(read_file("jsonl", str(file), False, stat))


def test_cli_unicode(tmp_path):
    input_file = tmp_path / "events.csv"
    output_file = tmp_path / "report.json"

    input_file.write_text(
        "timestamp,level,source,message\n"
        "2026-10-13T10:00:00,INFO,сервер,Запуск программы\n",
        encoding="utf-8"
    )

    result = main([
        "analyze",
        str(input_file),
        "--format",
        "csv",
        "--output",
        str(output_file)
    ])

    assert result == 0

    report = json.loads(
        output_file.read_text(encoding="utf-8")
    )

    assert "сервер" in report["sources"]


def test_cli_empty_file(tmp_path):
    input_file = tmp_path / "empty.csv"
    output_file = tmp_path / "report.json"

    input_file.write_text("", encoding="utf-8")

    result = main([
        "analyze",
        str(input_file),
        "--format",
        "csv",
        "--output",
        str(output_file)
    ])

    assert result == 0

    report = json.loads(
        output_file.read_text(encoding="utf-8")
    )

    assert report["total"] == 0
    assert report["levels"] == {}
    assert report["sources"] == {}
    assert report["top_sources"] == {}
    assert report["first_timestamp"] is None
    assert report["last_timestamp"] is None
    assert report["skipped"] == 0 