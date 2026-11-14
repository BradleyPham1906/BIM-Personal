#!/usr/bin/env python3
"""The work-order gate: the review Claude used to do by hand, as checks a script can run.

Cline (or the owner) runs it after finishing a [Cline] work order. `check` only reports; `ship` checks,
ticks the task, logs it, commits, merges origin/main and pushes main. Claude audits shipped work later,
in batches (.claude/skills/audit), instead of blocking every task.

    python3 tools/gate.py check v175c WO-01            report only (rebuilds canvas_v10.html, nothing else)
    python3 tools/gate.py ship  v175c WO-01 WO-02      gate, tick, log, commit, merge, push main
    python3 tools/gate.py ship  v175c WO-01 --dry-run  everything but the commit and the push

What it proves (any failure stops it; nothing is pushed):
  1. the task is a [Cline] task in docs/work-orders/<phase>/TASKS*.md, still open;
  2. scope: every changed file is one the task names (src/ files and the tests it names), its phase's
     TASKS file (checkboxes only), or canvas_v10.html; nothing in the protected paths;
  3. tests are the oracle: a test file may only gain lines, never lose them; SPEC files are untouched;
  4. the build contract on added src/ lines: ES5, no emojis, no WO- stubs, no import/export edits,
     no debugger, no bim* name that is declared nowhere in src/ (an invented name);
  5. size: added src/ lines within the task's budget (`- **Budget:** N`, default 120 per task);
  6. node --check on each changed .js; the task's own tests (at least one ran, none failed);
     npm test; npm run check (canvas_v10.html current, modules current, embedded Python, guide).
Then, advisory unless --strict-llm: the local model reads the task and the diff and answers
PASS or CONCERN; a CONCERN is logged and flagged for Claude's audit.
Standard library only.
"""
import argparse
import datetime
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

PROTECTED = ("src/js/engine/core/", "src/js/engine/render/rendered-core.js", "src/js/engine/history/",
             "src/js/engine/_begin.js", "src/js/engine/_end.js", "src/js/vendor/", "src/index.html",
             "tools/", ".github/", "runtime/", "vendor/", "tests/unit/helpers/", "tests/fixtures/",
             ".clinerules/", ".claude/", "CLAUDE.md", "package.json", "docs/dev/")
HEADING = re.compile(r"^## \[( |x|skipped)\] ((?:WO|T)-\d+) \[(Cline|Claude)\] (.*)$")
TICK = re.compile(r"^(## )\[( |x|skipped)\]")
ES6 = [(re.compile(r"\b(let|const)\s+[A-Za-z_$\[{]"), "let/const"), (re.compile(r"=>"), "arrow function"),
       (re.compile(r"^\s*class\s|\bclass\s+[A-Za-z_$]+\s*(\{|extends)"), "class"), (re.compile(r"`"), "template string"),
       (re.compile(r"\.\.\.[A-Za-z_$\[]"), "spread"), (re.compile(r"\basync\s+function\b|\bawait\s"), "async/await")]
BAD = [(re.compile(r"throw\s+new\s+Error\(\s*['\"]WO-"), "WO- throw stub"), (re.compile(r"\bdebugger\b"), "debugger"),
       (re.compile(r"[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F]"), "emoji")]
NAME_CALL = re.compile(r"\b(bim[A-Za-z0-9_]*)\s*\(")
DEFAULT_BUDGET = 120


class Gate(object):
    def __init__(self, verbose=True):
        self.fails, self.warns, self.notes, self.verbose = [], [], [], verbose

    def fail(self, msg):
        self.fails.append(msg)
        print("  FAIL " + msg)

    def warn(self, msg):
        self.warns.append(msg)
        print("  warn " + msg)

    def ok(self, msg):
        self.notes.append(msg)
        print("  ok   " + msg)


def git(*args, check=True):
    r = subprocess.run(["git"] + list(args), cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    if check and r.returncode:
        raise SystemExit("gate: git %s failed: %s" % (" ".join(args), (r.stderr or r.stdout).strip()))
    return r.stdout


def run(cmd, label, gate, tail=12):
    exe = shutil.which(cmd[0]) or cmd[0]
    r = subprocess.run([exe] + cmd[1:], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    out = (r.stdout or "") + (r.stderr or "")
    if r.returncode:
        gate.fail("%s exited %d:" % (label, r.returncode))
        lines = [l for l in out.splitlines() if re.search(r"not ok|fail|error|Error|assert|expected|actual", l)]
        for l in (lines or out.splitlines())[-tail:]:
            print("       " + l)
    else:
        gate.ok(label)
    return r.returncode, out


# ---------- the work order ----------

def find_tasks(phase, ids):
    d = os.path.join(ROOT, "docs", "work-orders", phase)
    if not os.path.isdir(d):
        raise SystemExit("gate: no folder docs/work-orders/%s" % phase)
    found = {}
    for name in sorted(os.listdir(d)):
        if not (name.startswith("TASKS") and name.endswith(".md")):
            continue
        rel = "docs/work-orders/%s/%s" % (phase, name)
        lines = open(os.path.join(d, name), encoding="utf-8").read().splitlines()
        first = next((i for i, l in enumerate(lines) if l.startswith("## ")), len(lines))
        preamble = "\n".join(lines[:first])
        for i, l in enumerate(lines):
            m = HEADING.match(l)
            if m and m.group(2) in ids and m.group(2) in found:
                raise SystemExit("gate: %s is in two TASKS files of %s; give the ids a unique prefix" % (m.group(2), phase))
            if m and m.group(2) in ids:
                j = i + 1
                while j < len(lines) and not lines[j].startswith("## "):
                    j += 1
                found[m.group(2)] = {"id": m.group(2), "state": m.group(1), "who": m.group(3), "title": m.group(4),
                                     "file": rel, "line": i, "block": "\n".join(lines[i:j]).rstrip("- \n"),
                                     "preamble": preamble}
    missing = [i for i in ids if i not in found]
    if missing:
        raise SystemExit("gate: %s not found in docs/work-orders/%s/TASKS*.md" % (", ".join(missing), phase))
    return [found[i] for i in ids]


def paths_in(text):
    """Repo paths in backticks, leaving out those named as off limits ("do not change `x.js`")."""
    text = re.sub(r"(?i)\b(do not|don't|never|not)\b[^.;\n]*", "", text)
    out = []
    for tok in re.findall(r"`([^`\s]+)`", text):
        tok = tok.strip()
        if not re.search(r"\.(js|mjs|css|html|py|json)$", tok) or tok == "canvas_v10.html":
            continue
        cands = [c for c in (tok, "src/js/engine/" + tok, "src/" + tok) if os.path.exists(os.path.join(ROOT, c))]
        if not cands and tok.startswith(("src/", "tests/")):
            cands = [tok]  # a new file the task creates
        if cands and cands[0].startswith(("src/", "tests/", "docs/work-orders/")):
            out.append(cands[0])
    return out


def task_scope(t):
    explicit = re.search(r"^\s*-\s*\*\*Files:\*\*\s*(.+)$", t["block"], re.M)
    named = paths_in(explicit.group(1)) if explicit else paths_in(t["block"]) or paths_in(t["preamble"])
    tests = [p for p in named if p.endswith(".test.mjs")]
    if not tests:
        tests = [p for p in paths_in(t["preamble"]) if p.endswith(".test.mjs")]
    srcs = [p for p in named if p.startswith("src/")]
    budget = re.search(r"\*\*Budget:\*\*\s*(\d+)", t["block"])
    names = set(re.findall(r"`(bim[A-Za-z0-9_]*)", t["block"]))
    return {"src": srcs, "tests": tests, "budget": int(budget.group(1)) if budget else DEFAULT_BUDGET, "names": names}


# ---------- the diff ----------

def base_commit():
    git("fetch", "-q", "origin", "main", check=False)
    for ref in ("origin/main", "main"):
        b = git("merge-base", "HEAD", ref, check=False).strip()
        if b:
            return b
    raise SystemExit("gate: cannot find a base (no origin/main)")


def changed_files(base):
    names = set(git("diff", "--name-only", base).split())
    names |= set(git("ls-files", "--others", "--exclude-standard").split())
    return sorted(n for n in names if n)


def file_diff(base, path):
    """(added lines, removed lines) of PATH since BASE, the working tree included."""
    if path in git("ls-files", "--others", "--exclude-standard").split():
        return open(os.path.join(ROOT, path), encoding="utf-8", errors="replace").read().splitlines(), []
    added, removed = [], []
    for l in git("diff", "-U0", base, "--", path).splitlines():
        if l.startswith("+") and not l.startswith("+++"):
            added.append(l[1:])
        elif l.startswith("-") and not l.startswith("---"):
            removed.append(l[1:])
    return added, removed


def declared_names():
    names = set()
    pat = re.compile(r"\bfunction\s+(bim[A-Za-z0-9_]*)|\bvar\s+(bim[A-Za-z0-9_]*)\s*=")
    for d, _, files in os.walk(os.path.join(ROOT, "src", "js")):
        for f in files:
            if f.endswith(".js"):
                for m in pat.finditer(open(os.path.join(d, f), encoding="utf-8", errors="replace").read()):
                    names.add(m.group(1) or m.group(2))
    return names


# ---------- the checks ----------

def check(phase, ids, gate, llm=True, strict_llm=False):
    tasks = find_tasks(phase, ids)
    print("gate: %s %s" % (phase, ", ".join(t["id"] + " " + t["title"] for t in tasks)))
    for t in tasks:
        if t["who"] != "Cline":
            gate.fail("%s is a [%s] task; only [Cline] tasks go through the gate" % (t["id"], t["who"]))
        if t["state"] == "skipped":
            gate.fail("%s is marked skipped (left for Claude)" % t["id"])
    scopes = [task_scope(t) for t in tasks]
    allowed_src = set(p for s in scopes for p in s["src"])
    allowed_tests = set(p for s in scopes for p in s["tests"])
    task_files = set(t["file"] for t in tasks)
    if not allowed_src:
        gate.fail("the task names no src/ file; add `- **Files:** `src/...`` to its block")
    base = base_commit()
    files = changed_files(base)
    if not files:
        gate.fail("nothing changed since origin/main")
    added_src = 0
    js = []
    for f in files:
        added, removed = file_diff(base, f)
        if f == "canvas_v10.html":
            continue
        if f.startswith(PROTECTED):
            gate.fail("%s is a protected path (Claude's)" % f)
            continue
        if f in task_files or f == "docs/work-orders/%s/GATE-LOG.md" % phase:
            if f in task_files and sorted(TICK.sub(r"\1[]", l) for l in added) != sorted(TICK.sub(r"\1[]", l) for l in removed):
                gate.fail("%s: only checkboxes may change in a TASKS file" % f)
            continue
        if f in allowed_tests or f.endswith(".test.mjs"):
            if f not in allowed_tests:
                gate.fail("%s: a test file the task does not name" % f)
            elif [l for l in removed if l.strip()]:
                gate.fail("%s: %d test line(s) removed or changed; tests may only be added" % (f, len(removed)))
            continue
        if re.search(r"/SPEC[^/]*\.md$", f):
            gate.fail("%s: the spec is Claude's" % f)
            continue
        if f not in allowed_src:
            gate.fail("%s is outside the task's scope (allowed: %s)" % (f, ", ".join(sorted(allowed_src)) or "none"))
            continue
        if f.endswith(".js"):
            js.append(f)
        added_src += len([l for l in added if l.strip()])
        if [l for l in added + removed if re.match(r"\s*(import\s|export\s*\{)", l)]:
            gate.fail("%s: import/export lines changed (npm run modules writes them; Claude's)" % f)
        known = None
        for l in added:
            code = re.sub(r"'(?:\\.|[^'\\])*'|\"(?:\\.|[^\"\\])*\"|/\*.*?\*/|//.*$", "''", l)
            if code.strip().startswith(("*", "/*")):
                code = ""
            for rx, what in BAD:
                if rx.search(l):
                    gate.fail("%s: %s: %s" % (f, what, l.strip()[:90]))
            if f.endswith(".js"):
                for rx, what in ES6:
                    if rx.search(code):
                        gate.fail("%s: not ES5 (%s): %s" % (f, what, l.strip()[:90]))
                for name in NAME_CALL.findall(code):
                    known = known if known is not None else declared_names()
                    if name not in known:
                        gate.fail("%s: calls %s, declared nowhere in src/ (invented?)" % (f, name))
    budget = sum(s["budget"] for s in scopes)
    if added_src > budget:
        gate.fail("%d src lines added, over the budget of %d; split the task or ask Claude" % (added_src, budget))
    elif not gate.fails:
        gate.ok("scope and contract: %d file(s), %d src line(s) added (budget %d)" % (len(files), added_src, budget))
    if gate.fails:
        return tasks, None
    for f in js:
        run(["node", "--check", f], "node --check " + f, gate)
    for tf in sorted(allowed_tests):
        code, out = run(["node", "--test", "--test-reporter=tap", "--test-name-pattern=" + "|".join(ids), tf], "task tests " + tf, gate)
        # a skipped case ("ok 3 - WO-09 ... # SKIP") did not run
        ran = re.findall(r"^\s*ok \d+ - (?:%s)\b(?![^\n]*# SKIP)" % "|".join(ids), out, re.M)
        if not code and not ran:
            gate.fail("%s: no test named %s ran; the gate needs the task's own tests" % (tf, "/".join(ids)))
    if not allowed_tests:
        gate.fail("the task names no test file; Claude must give every [Cline] task a test")
    run(["npm", "test"], "npm test", gate)
    run(["npm", "run", "check"], "npm run check (if canvas_v10.html is stale: python3 tools/build_app.py)", gate)
    verdict = None
    if llm and not gate.fails:
        verdict = llm_review(tasks, base, [f for f in files if f in allowed_src or f in allowed_tests], gate, strict_llm)
    return tasks, verdict


def llm_review(tasks, base, files, gate, strict):
    try:
        import local_llm
    except ImportError:
        gate.warn("local model review skipped (tools/local_llm.py missing)")
        return "skipped"
    diff = git("diff", base, "--", *files) if files else ""
    for f in git("ls-files", "--others", "--exclude-standard", "--", *files).split():
        diff += "\n+++ new file %s\n%s" % (f, open(os.path.join(ROOT, f), encoding="utf-8").read())
    prompt = ("You review one change to an ES5 browser CAD app (libraries only through adapters). The tests already pass. "
              "Look only for: behaviour the task asks for that the code misses (an edge case listed and not handled), "
              "code that does more than the task, names not listed under 'May use', changed behaviour of existing code. "
              "Answer with a first line exactly 'VERDICT: PASS' or 'VERDICT: CONCERN', then at most 5 short bullets "
              "naming line and reason. Do not suggest style changes.\n\nTHE TASK\n"
              + "\n\n".join(t["block"] for t in tasks) + "\n\nTHE DIFF\n" + diff[:28000])
    try:
        reply = local_llm.request(local_llm.DEFAULT_URL.rstrip("/") + "/chat/completions", {
            "model": local_llm.DEFAULT_MODEL, "temperature": 0, "max_tokens": 600, "stream": False,
            "messages": [{"role": "system", "content": local_llm.DEFAULT_SYSTEM}, {"role": "user", "content": prompt}]},
            timeout=300)["choices"][0]["message"]["content"].strip()
    except Exception as e:  # unreachable model: the deterministic gate still stands
        gate.warn("local model review skipped (%s)" % str(e)[:80])
        return "skipped"
    concern = not re.match(r"\s*VERDICT:\s*PASS", reply, re.I)
    print("  llm  " + reply.replace("\n", "\n       "))
    if concern and strict:
        gate.fail("the local model raised a concern (--strict-llm)")
    elif concern:
        gate.warn("the local model raised a concern; shipped but flagged for Claude's audit")
    return ("concern: " + " / ".join(l.strip("-* ") for l in reply.splitlines()[1:4])) if concern else "pass"


# ---------- shipping ----------

def tick(tasks):
    for t in tasks:
        p = os.path.join(ROOT, t["file"])
        lines = open(p, encoding="utf-8").read().split("\n")
        lines[t["line"]] = TICK.sub(r"\1[x]", lines[t["line"]], count=1)
        open(p, "w", encoding="utf-8", newline="\n").write("\n".join(lines))


def log(phase, tasks, gate, verdict):
    p = os.path.join(ROOT, "docs", "work-orders", phase, "GATE-LOG.md")
    if not os.path.exists(p):
        open(p, "w", encoding="utf-8", newline="\n").write(
            "# %s gate log\n\nWritten by `tools/gate.py ship`. Claude's audit marks each row (`/audit`).\n\n"
            "| Date | Tasks | Checks | Local model | Audit |\n|---|---|---|---|---|\n" % phase)
    row = "| %s | %s | %d passed%s | %s | open |\n" % (
        datetime.date.today().isoformat(), ", ".join(t["id"] for t in tasks), len(gate.notes),
        ", %d warning(s)" % len(gate.warns) if gate.warns else "", (verdict or "skipped").replace("|", "/")[:160])
    open(p, "a", encoding="utf-8", newline="\n").write(row)


def push_main():
    for i in range(4):
        r = subprocess.run(["git", "push", "origin", "main"], cwd=ROOT, capture_output=True, text=True)
        if not r.returncode:
            return True
        print("  push failed (%s), retry %d" % (r.stderr.strip()[:120], i + 1))
        subprocess.run(["git", "fetch", "-q", "origin", "main"], cwd=ROOT)
        if not merge_origin():
            return False
    return False


def merge_origin():
    """Merge origin/main into main without rewriting anything; a conflict only in canvas_v10.html is rebuilt."""
    if git("rev-list", "--count", "HEAD..origin/main").strip() == "0":
        return True
    r = subprocess.run(["git", "merge", "--no-edit", "origin/main"], cwd=ROOT, capture_output=True, text=True)
    if r.returncode:
        conflicts = git("diff", "--name-only", "--diff-filter=U").split()
        if conflicts != ["canvas_v10.html"]:
            git("merge", "--abort", check=False)
            print("gate: merging origin/main conflicts in %s; left for Claude, nothing pushed" % ", ".join(conflicts))
            return False
        git("checkout", "--theirs", "canvas_v10.html")
    g = Gate()
    run([sys.executable, "tools/build_app.py"], "rebuild canvas_v10.html after the merge", g)
    run(["npm", "test"], "npm test after the merge", g)
    run(["npm", "run", "check"], "npm run check after the merge", g)
    if g.fails:
        if os.path.exists(os.path.join(ROOT, ".git", "MERGE_HEAD")):
            git("merge", "--abort", check=False)
        else:
            git("reset", "-q", "--merge", "ORIG_HEAD", check=False)
        print("gate: main fails after merging origin/main; the merge was undone (your commit stays), "
              "nothing pushed, left for Claude")
        return False
    git("add", "canvas_v10.html")
    if git("status", "--porcelain").strip():
        git("commit", "--no-edit", "-q") if os.path.exists(os.path.join(ROOT, ".git", "MERGE_HEAD")) else \
            git("commit", "-q", "-m", "Rebuild canvas_v10.html after merging origin/main")
    return True


def rebuild_if_needed():
    """canvas_v10.html is generated: rebuild it when src/ differs from origin/main, so the check sees it current."""
    if git("diff", "--name-only", "origin/main", "--", "src/", check=False).strip() or \
            git("ls-files", "--others", "--exclude-standard", "--", "src/").strip():
        subprocess.run([sys.executable, "tools/build_app.py"], cwd=ROOT, capture_output=True)


def ship(args):
    branch = git("rev-parse", "--abbrev-ref", "HEAD").strip()
    if branch != "main" and not args.dry_run:
        raise SystemExit("gate: ship runs on main (this is %s)" % branch)
    if os.path.exists(os.path.join(ROOT, ".git", "MERGE_HEAD")):
        raise SystemExit("gate: a merge is in progress; finish or abort it first")
    rebuild_if_needed()
    gate = Gate()
    tasks, verdict = check(args.phase, args.ids, gate, llm=not args.no_llm, strict_llm=args.strict_llm)
    if gate.fails:
        print("\ngate: FAILED (%d). Nothing committed or pushed. Fix and run again (two attempts), then report." % len(gate.fails))
        return 1
    tick(tasks)
    log(args.phase, tasks, gate, verdict)
    if args.dry_run:
        print("\ngate: PASSED (dry run). TASKS ticked and GATE-LOG written; not committed or pushed.")
        return 0
    git("add", "-A")
    title = "; ".join("%s %s" % (t["id"], re.sub(r"`", "", t["title"])[:60]) for t in tasks)
    git("commit", "-q", "-m", "%s %s (gate passed)\n\n%s\n\nGate: pass\nGate-LLM: %s" % (
        args.phase, title, "\n".join("- " + n for n in gate.notes), (verdict or "skipped")[:200]))
    if not merge_origin():
        return 1
    if not push_main():
        print("gate: push failed; the commit is local on main. Report it.")
        return 1
    print("\ngate: SHIPPED %s to main (%s). CI runs on the push; Claude audits it later." % (
        ", ".join(args.ids), git("rev-parse", "--short", "HEAD").strip()))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("action", choices=["check", "ship"])
    ap.add_argument("phase", help="the folder under docs/work-orders, e.g. v175c")
    ap.add_argument("ids", nargs="+", help="the task ids, e.g. WO-01 WO-02")
    ap.add_argument("--no-llm", action="store_true", help="skip the local model's advisory review")
    ap.add_argument("--strict-llm", action="store_true", help="a local-model CONCERN fails the gate")
    ap.add_argument("--dry-run", action="store_true", help="ship: tick and log, but do not commit or push")
    args = ap.parse_args()
    if args.action == "ship":
        return ship(args)
    rebuild_if_needed()
    gate = Gate()
    check(args.phase, args.ids, gate, llm=not args.no_llm, strict_llm=args.strict_llm)
    print("\ngate: %s (%d failed, %d warning(s))" % ("FAILED" if gate.fails else "PASSED", len(gate.fails), len(gate.warns)))
    return 1 if gate.fails else 0


if __name__ == "__main__":
    sys.exit(main())
