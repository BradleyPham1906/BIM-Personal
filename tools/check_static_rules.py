#!/usr/bin/env python3
"""Reject duplicate assignments to the engine's public test hooks."""
import argparse
from collections import defaultdict
from pathlib import Path
import sys

from jslex import lex


ROOT = Path(__file__).resolve().parents[1]


def hook_assignments(root):
    seen = defaultdict(list)
    files = sorted(path for path in root.rglob("*.js") if "vendor" not in path.parts)
    if not files:
        raise ValueError("no JavaScript files found under %s" % root)
    for path in files:
        code = path.read_text(encoding="utf-8")
        tokens = [(kind, code[start:end], start) for kind, start, end in lex(code)]
        for i in range(len(tokens) - 3):
            window, dot, name, equals = tokens[i:i + 4]
            if (window[0] == "word" and window[1] == "window" and
                    dot[0] == "punct" and dot[1] == "." and
                    name[0] == "word" and name[1].startswith("__a3d") and
                    equals[0] == "punct" and equals[1] == "="):
                line = code.count("\n", 0, name[2]) + 1
                seen[name[1]].append((path, line))
    return seen


def check(root):
    errors = []
    seen = hook_assignments(root)
    for name, locations in sorted(seen.items()):
        if len(locations) < 2:
            continue
        first_path, first_line = locations[0]
        for path, line in locations[1:]:
            errors.append(
                "duplicate test hook window.%s: %s:%d and %s:%d; keep one definition"
                % (name, first_path, first_line, path, line)
            )
    return errors, sum(len(locations) for locations in seen.values())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT / "src" / "js",
                        help="JavaScript source root (defaults to src/js)")
    args = parser.parse_args()
    root = args.root.resolve()
    if not root.is_dir():
        parser.error("source root does not exist: %s" % root)
    try:
        errors, count = check(root)
    except (OSError, UnicodeError, ValueError) as err:
        print("static rules: %s" % err, file=sys.stderr)
        return 2
    if errors:
        for error in errors:
            print("static rules: " + error, file=sys.stderr)
        return 1
    noun = "assignment" if count == 1 else "assignments"
    print("static rules: %d test-hook %s, no duplicates" % (count, noun))
    return 0


if __name__ == "__main__":
    sys.exit(main())
