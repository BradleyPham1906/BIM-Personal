#!/usr/bin/env python3
"""Tell Claude, at the start of every session, about Aider work nobody has reviewed yet.

Run by the SessionStart hook in .claude/settings.json. Standard library only. It looks for:
  - uncommitted changes in the working copy (Aider leaves its edits uncommitted: .aider.conf.yml
    has auto-commits off), with what the owner last asked Aider (.aider.chat.history.md);
  - aider/* branches, local or on GitHub, not yet merged into main.
If there is any, it prints a JSON hook reply: a line for the owner, and instructions for Claude to
run the review-aider skill. If there is none, or git fails, it prints nothing. It never changes
anything and never runs tests.
"""
import json
import os
import subprocess
import sys

ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HISTORY = os.path.join(ROOT, ".aider.chat.history.md")


def git(*args, timeout=15):
    out = subprocess.run(["git"] + list(args), cwd=ROOT, capture_output=True, text=True,
                         encoding="utf-8", errors="replace", timeout=timeout)
    if out.returncode != 0:
        raise RuntimeError(out.stderr.strip())
    return out.stdout


def uncommitted():
    return [l[3:] for l in git("status", "--porcelain").splitlines() if l.strip()]


def unmerged_aider_branches():
    try:
        git("fetch", "-q", "origin", timeout=20)
    except Exception:
        pass  # offline: use what is known
    try:
        base = git("rev-parse", "--verify", "-q", "origin/main").strip() and "origin/main"
    except RuntimeError:
        base = "main"
    names = git("branch", "-a", "--no-merged", base, "--format=%(refname:short)").split()
    found = []
    for n in names:
        short = n[len("origin/"):] if n.startswith("origin/") else n
        if short.startswith("aider/") and short not in found:
            found.append(short)
    return found


def last_aider_requests(limit=8):
    """The owner's requests (lines '#### ...') in the last Aider session, and when it started."""
    if not os.path.isfile(HISTORY):
        return None, []
    with open(HISTORY, encoding="utf-8", errors="replace") as fh:
        text = fh.read()
    marker = "# aider chat started at "
    i = text.rfind(marker)
    if i < 0:
        return None, []
    session = text[i:]
    started = session[len(marker):].splitlines()[0].strip()
    asks = [l[5:].strip() for l in session.splitlines() if l.startswith("#### ")]
    asks = [a for a in asks if a and not a.startswith("/")]
    return started, asks[-limit:]


def main():
    try:
        changed = uncommitted()
        branches = unmerged_aider_branches()
    except Exception:
        return 0
    if not changed and not branches:
        return 0
    started, asks = last_aider_requests()
    lines = ["Unreviewed Aider work in this repo (tools/pending_aider.py):"]
    if changed:
        lines.append("- Uncommitted changes on branch %s: %s" % (
            git("branch", "--show-current").strip() or "(detached)",
            ", ".join(changed[:15]) + (" ..." if len(changed) > 15 else "")))
    if branches:
        lines.append("- aider/* branches not merged into main: " + ", ".join(branches))
    if started:
        lines.append("- Last Aider session started %s. What the owner asked Aider:" % started)
        lines.extend("    * " + a[:300] for a in asks) if asks else lines.append("    (no requests recorded)")
    lines.append("Before anything else this session, run the review-aider skill "
                 "(.claude/skills/review-aider/SKILL.md) on this work, then tell the owner the result "
                 "in plain words. The owner does not read code.")
    n = len(branches) + (1 if changed else 0)
    reply = {
        "systemMessage": "Found %d piece%s of Aider work to review; Claude will check it first." % (n, "" if n == 1 else "s"),
        "hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "\n".join(lines)},
    }
    sys.stdout.write(json.dumps(reply))
    return 0


if __name__ == "__main__":
    sys.exit(main())
