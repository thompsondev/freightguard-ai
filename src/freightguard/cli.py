"""Command-line interface for extraction and offline validation."""

import argparse
import json
import sys
from pathlib import Path

from pydantic import ValidationError

from freightguard.io import read_document
from freightguard.models import FreightDocument
from freightguard.parser import DocumentParsingError, OpenAIFreightParser
from freightguard.workflow import process_document


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="freightguard",
        description="Extract freight data and run explainable operational checks.",
    )
    subcommands = parser.add_subparsers(dest="command", required=True)

    process = subcommands.add_parser("process", help="Parse a text or PDF document with OpenAI")
    process.add_argument("document", type=Path)
    process.add_argument("--model", help="Override OPENAI_MODEL")

    validate = subcommands.add_parser("validate", help="Run rules against extracted JSON")
    validate.add_argument("document", type=Path)
    return parser


def _print_result(document: FreightDocument) -> None:
    result = process_document(document)
    print(result.model_dump_json(indent=2))


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "process":
            raw_text = read_document(args.document)
            document = OpenAIFreightParser(model=args.model).parse(raw_text)
        else:
            payload = json.loads(args.document.read_text(encoding="utf-8"))
            document = FreightDocument.model_validate(payload)
        _print_result(document)
        return 0
    except (DocumentParsingError, FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
    except ValidationError as exc:
        print(f"error: extracted data does not match the schema\n{exc}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

