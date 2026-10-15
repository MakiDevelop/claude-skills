#!/usr/bin/env python3
"""Strict JSON/JSONL syntax checks; does not perform JSON Schema validation."""
import argparse
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import sys


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            # Do not echo a potentially sensitive key.
            raise ValueError("Duplicate object key")
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError("Nonstandard numeric constant")


def decimal_number(value):
    try:
        number = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError("Numeric exponent exceeds decimal parser range") from exc
    if not number.is_finite():
        raise ValueError("Nonfinite numeric value")
    return number


def parse(text):
    return json.loads(text, object_pairs_hook=unique_object,
                      parse_constant=reject_constant, parse_float=decimal_number)


def validate(path, jsonl=False):
    count = 0
    failures = []
    with Path(path).open(encoding="utf-8") as handle:
        records = enumerate(handle, 1) if jsonl else [(None, handle.read())]
        for physical_line, text in records:
            try:
                parse(text)
                count += 1
            except (ValueError, RecursionError) as exc:
                if isinstance(exc, json.JSONDecodeError):
                    failure = {"line": physical_line or exc.lineno, "column": exc.colno,
                               "error": exc.msg}
                else:
                    failure = {"line": physical_line,
                               "error": "Input too deeply nested" if isinstance(exc, RecursionError)
                                        else str(exc)}
                failures.append(failure)
                if len(failures) >= 20:
                    return {"valid": False, "checked_valid_records": count,
                            "errors": failures, "stopped_after": 20,
                            "schema": "not checked"}
    if jsonl and count == 0 and not failures:
        failures.append({"line": None, "error": "Empty JSONL input"})
    return {"valid": not failures, "checked_valid_records": count,
            "errors": failures, "schema": "not checked"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--jsonl", action="store_true")
    args = parser.parse_args()
    try:
        result = validate(args.input, args.jsonl)
    except (OSError, UnicodeError) as exc:
        print(json.dumps({"valid": False, "error": type(exc).__name__,
                          "schema": "not checked"}))
        return 1
    print(json.dumps(result))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
