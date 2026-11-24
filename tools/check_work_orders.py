#!/usr/bin/env python3
"""Check that every open [Cline] work order can pass the gate's scope rules before Cline starts it.

The gate refuses a task that names no src/ file, no test, or a protected path; finding that only at ship time
costs Cline a whole phase (V216/V217, 2026-11-24). This runs in `npm run check`, so CI fails on Claude's spec instead.

    python3 tools/check_work_orders.py            every phase
    python3 tools/check_work_orders.py v216 v217  only these
Standard library only.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gate  # noqa: E402

WO = os.path.join(gate.ROOT, "docs", "work-orders")


def open_cline_ids(phase):
    d = os.path.join(WO, phase)
    ids = []
    for name in sorted(os.listdir(d)):
        if name.startswith("TASKS") and name.endswith(".md"):
            for line in open(os.path.join(d, name), encoding="utf-8").read().splitlines():
                m = gate.HEADING.match(line)
                if m and m.group(1) == " " and m.group(3) == "Cline":
                    ids.append(m.group(2))
    return ids


def problems(phase):
    ids = open_cline_ids(phase)
    if not ids:
        return []
    out = []
    for t in gate.find_tasks(phase, ids):
        scope = gate.task_scope(t)
        where = "%s %s" % (phase, t["id"])
        if not scope["src"]:
            out.append("%s: names no src/ file (add `- **Files:** `src/...``)" % where)
        if not scope["tests"]:
            out.append("%s: names no test file" % where)
        for p in scope["src"]:
            if gate.is_protected(p):
                out.append("%s: names %s, a protected path; add it to PROTECTED_EXEMPT in tools/gate.py if it is "
                           "a pure file scaffolded for Cline, or make the task [Claude]" % (where, p))
        for p in scope["tests"]:
            if not os.path.exists(os.path.join(gate.ROOT, p)):
                out.append("%s: its test %s does not exist" % (where, p))
    return out


def main(argv):
    phases = argv or sorted(n for n in os.listdir(WO) if re.match(r"v\d", n) and os.path.isdir(os.path.join(WO, n)))
    found = []
    for phase in phases:
        found += problems(phase)
    for p in found:
        print("work orders: " + p)
    print("work orders: %d open [Cline] problem(s) in %d phase(s)" % (len(found), len(phases)))
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
