import argparse
import logging

from .analysis import ini_stat, update_stat
from .errors import CLIConfigurationError, StreamStatsError
from .readers import read_file
from .report import report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze_parser = subparsers.add_parser("analyze")
    analyze_parser.add_argument("input", nargs="+")
    analyze_parser.add_argument(
        "--format",
        choices = ["csv", "jsonl"],
        required=True
        )
    analyze_parser.add_argument(
        "--output",
        required=True
    )
    analyze_parser.add_argument(
        "--skip-invalid",
        action="store_true"
    )

    args = parser.parse_args(argv)

    if args.skip_invalid:
        logging.basicConfig(
            level=logging.WARNING,
            format="WARNING: %(message)s",
        )

    if args.command != "analyze":
        raise CLIConfigurationError(f"Неизвестная команда: {args.command}")
    
    stat = ini_stat()
    current_filename = None

    try:
        for filename in args.input:
            current_filename = filename
            events = read_file(
                args.format,
                filename,
                args.skip_invalid,
                stat)
            update_stat(events, stat)

        report(stat, args.output)

    except StreamStatsError as e:
        if current_filename is not None:
            print(f"ERROR: {current_filename}: {e}")
        else:
            print(f"ERROR: {e}")
        return 2
    
    return 0
    

if __name__ == "__main__":
    raise SystemExit(main())