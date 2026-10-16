import json

from .analysis import top_sources


def report(stat: dict, output: str) -> None:
    report = {
        "total": stat["total"],
        "levels": stat["levels"],
        "sources": stat["sources"],
        "top_sources": top_sources(stat),
        "first_timestamp": (
            stat["first_timestamp"].isoformat()
            if stat["first_timestamp"] is not None else None 
            ),
        "last_timestamp": (
            stat["last_timestamp"].isoformat()
            if stat["last_timestamp"] is not None
            else None 
            ),
        "skipped": stat["skipped"]
    }

    if output is None:
        print(json.dumps(report, ensure_ascii=False, indent=4))
    else:
        with open(output, "w", encoding="utf-8") as file:
            json.dump(report, file, ensure_ascii=False, indent=4)
    
