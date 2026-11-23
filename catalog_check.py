"""Compare named Python format fields across two flat JSON catalogs."""

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from string import Formatter

NAME = re.compile(r"[A-Za-z_][A-Za-z_0-9]*")
FORMATTER = Formatter()


def fields(message, depth=0):
    names = Counter()
    for _, name, spec, conversion in FORMATTER.parse(message):
        if name is None:
            continue
        if depth > 1 or not NAME.fullmatch(name) or conversion not in (None, "s", "r", "a"):
            raise ValueError("Expected a named Python format field such as {name}.")
        names[name] += 1
        if spec:
            names.update(fields(spec, depth + 1))
    return names


def compare(source, target):
    findings = []
    for key in sorted(source.keys() | target.keys()):
        if key not in target or key not in source:
            findings.append({"key": key, "kind": "missing" if key in source else "extra"})
            continue
        parsed = {}
        for side, message in (("source", source[key]), ("target", target[key])):
            try:
                parsed[side] = fields(message)
            except ValueError as exc:
                findings.append({"key": key, "kind": "invalid-format", "side": side, "detail": str(exc)})
        if len(parsed) == 2 and parsed["source"] != parsed["target"]:
            original, translation = parsed["source"], parsed["target"]
            findings.append({
                "key": key,
                "kind": "placeholders",
                "missing": sorted((original - translation).elements()),
                "extra": sorted((translation - original).elements()),
            })
    return findings


def require_unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key {key!r}.")
        result[key] = value
    return result


def load_catalog(path):
    catalog = json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=require_unique_pairs)
    if not isinstance(catalog, dict) or not all(isinstance(value, str) for value in catalog.values()):
        raise ValueError(f"{path}: expected one JSON object with string values.")
    return catalog


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("target", type=Path)
    args = parser.parse_args()
    try:
        findings = compare(load_catalog(args.source), load_catalog(args.target))
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(findings, indent=2))
    return int(bool(findings))


if __name__ == "__main__":
    raise SystemExit(main())
