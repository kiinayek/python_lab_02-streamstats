from collections.abc import Iterable


def ini_stat() -> dict:
    """Создание словаря для хранения статистики"""
    return {
            "total": 0,
            "levels": {},
            "sources": {},
            "error_sources": {},
            "first_timestamp": None,
            "last_timestamp": None,
            "skipped": 0
        }


def update_stat(events: Iterable[dict], stat: dict) -> dict:
    """Обновление статистики на основе полученных событий"""
    for event in events:
        stat["total"] += 1

        level = event["level"]
        if level not in stat["levels"]:
            stat["levels"][level] = 1
        else:
            stat["levels"][level] += 1

        source = event["source"]
        if source not in stat["sources"]:
            stat["sources"][source] = 1
        else:
            stat["sources"][source] += 1

        if level in ["ERROR", "CRITICAL"]:
            if source not in stat["error_sources"]:
                stat["error_sources"][source] = 1
            else:
                stat["error_sources"][source] += 1

        if stat["first_timestamp"] is None or \
            event["timestamp"] < stat["first_timestamp"]:
            stat["first_timestamp"] = event["timestamp"]

        if stat["last_timestamp"] is None or \
              event["timestamp"] > stat["last_timestamp"]:
            stat["last_timestamp"] = event["timestamp"]

    return stat

def top_sources(stat: dict, n: int=5) -> dict:
    """Возвращает топ-N источников событий ERROR и CRITICAL"""
    result = dict(sorted(stat["error_sources"].items(), \
                          key=lambda x: (-x[1], x[0]))[:n])
    return result
    