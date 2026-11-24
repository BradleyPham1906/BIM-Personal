#!/usr/bin/env python3
"""Carry unshipped work between the owner's machines (MacBook, the Beelink at home, the office PC).

Only tools/gate.py ship puts work on main. Work that is not shipped yet lives on one machine, where the
next machine cannot see it and may redo it. `park` puts it on the branch wip/park on GitHub and leaves this
machine clean; `resume` on the next machine brings it back as uncommitted changes on top of main.

    python3 tools/handoff.py park      before leaving a machine with unshipped work (Windows: python)
    python3 tools/handoff.py resume    on the next machine, before starting work
    python3 tools/handoff.py status    is anything parked?

One parking slot: park refuses while something is parked (resume it first). Nothing is lost locally either:
park keeps a copy at refs/parked/last. Standard library only.
"""
import datetime
import os
import platform
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRANCH = "wip/park"


def git(*args, check=True):
    r = subprocess.run(["git"] + list(args), cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    if check and r.returncode:
        raise SystemExit("handoff: git %s failed: %s" % (" ".join(args), (r.stderr or r.stdout).strip()))
    return r.stdout.strip()


def parked():
    """The parked commit on GitHub, or None."""
    out = git("ls-remote", "--heads", "origin", BRANCH, check=False)
    return out.split()[0] if out else None


def dirty():
    return [l for l in git("status", "--porcelain").splitlines() if l.strip()]


def park():
    if git("rev-parse", "--abbrev-ref", "HEAD") != "main":
        raise SystemExit("handoff: not on main; park only from main")
    git("fetch", "-q", "origin", "main")
    if parked():
        raise SystemExit("handoff: work is already parked on %s. Run `resume` first, ship it, then park again." % BRANCH)
    ahead = git("rev-list", "--count", "origin/main..HEAD")
    if not dirty() and ahead == "0":
        print("handoff: nothing to park; this machine has no unshipped work")
        return 0
    start = git("rev-parse", "HEAD")
    git("add", "-A")
    git("commit", "-q", "--no-verify", "-m", "park: unshipped work from %s, %s" % (
        platform.node() or "a machine", datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
    commit = git("rev-parse", "HEAD")
    git("update-ref", "refs/parked/last", commit)
    git("reset", "-q", "--mixed", start)  # this machine's tree is as it was until the push is proven
    for _ in range(4):
        if subprocess.run(["git", "push", "-q", "origin", "%s:refs/heads/%s" % (commit, BRANCH)], cwd=ROOT).returncode == 0:
            break
    if parked() != commit:
        raise SystemExit("handoff: push failed; nothing changed on this machine (a copy is at refs/parked/last)")
    git("reset", "-q", "--hard", "origin/main")
    git("clean", "-q", "-fd", "--", "src", "tests", "docs/work-orders")
    print("handoff: parked on %s (%s commit(s) and the uncommitted changes); this machine is clean at origin/main."
          % (BRANCH, ahead))
    print("         On the next machine: python3 tools/handoff.py resume   (Windows: python tools/handoff.py resume)")
    return 0


def resume():
    commit = parked()
    if not commit:
        print("handoff: nothing parked")
        return 0
    if git("rev-parse", "--abbrev-ref", "HEAD") != "main":
        raise SystemExit("handoff: not on main; resume only onto main")
    if [l for l in dirty() if not l.endswith("canvas_v10.html")]:
        raise SystemExit("handoff: this machine has unshipped changes of its own, and other work is parked. "
                         "Report to the owner; change nothing.")
    git("checkout", "-q", "--", "canvas_v10.html", check=False)
    git("fetch", "-q", "origin", "main", BRANCH)
    if subprocess.run(["git", "merge", "-q", "--ff-only", "origin/main"], cwd=ROOT).returncode:
        raise SystemExit("handoff: local main has commits origin/main does not; report to the owner")
    r = subprocess.run(["git", "merge", "--squash", "--no-commit", commit], cwd=ROOT, capture_output=True, text=True)
    git("reset", "-q")  # leave everything uncommitted, as the gate expects
    if r.returncode:
        print(r.stdout + r.stderr)
        raise SystemExit("handoff: the parked work conflicts with main; files with <<<<<<< need the owner. "
                         "wip/park is kept on GitHub.")
    git("push", "-q", "origin", "--delete", BRANCH)
    print("handoff: resumed the parked work as uncommitted changes on main; %s deleted. Ship one phase at a time."
          % BRANCH)
    print(git("status", "--short"))
    return 0


def main(argv):
    action = argv[0] if argv else "status"
    if action == "park":
        return park()
    if action == "resume":
        return resume()
    if action == "status":
        c = parked()
        print("handoff: %s" % ("work is parked on %s (%s); run resume" % (BRANCH, c[:7]) if c else "nothing parked"))
        return 0
    raise SystemExit(__doc__)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
