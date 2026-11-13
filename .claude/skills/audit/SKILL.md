---
name: audit
description: Audit work orders that Cline shipped to main through tools/gate.py. Use when the owner types /audit, when /start finds open rows in a GATE-LOG.md, or before Claude writes the next phase's work orders.
---

# /audit

The gate (`tools/gate.py`) proves scope, the build contract and the tests; it cannot prove the code is
what the research meant. This is that second look, done in batches after the fact, never blocking Cline.

1. Find what is open: `grep -n "| open |" docs/work-orders/*/GATE-LOG.md` and
   `git log --grep "^Gate: pass" --format="%h %s" origin/main -30`. Nothing open: say so and stop.
2. For each phase with open rows, read the shipped diff once per task
   (`git show <commit> -- src/ tests/ docs/work-orders/`), the task block and its SPEC part.
   Rows whose local model said `concern` first.
3. Check what the gate cannot: the behaviour matches SPEC and the research (not only the tests); edge
   cases the tests miss; names and comments in the app's style; nothing that will hurt the next task.
4. Each row gets one verdict in its Audit column: `ok`, `fixed <commit>` or `reopened`.
   - Small fix: make it on a `claude/` branch, with a unit test for any logic changed, and open a draft PR.
   - A gap in the work order itself (a missing case, a vague rule): fix the spec and the tests, so the
     next tasks benefit; note it in `docs/work-orders/ROUTING.md`'s record if it changes a score.
   - Wrong in a way that matters: `reopened`, the task's checkbox back to `[ ]`, and a line in TASKS saying why.
5. Keep the record of first-pass outcomes (ROUTING.md "Getting better over time"): count `ok` against
   `fixed`/`reopened` per score, so the thresholds move with evidence.
6. Report: tasks audited, how many ok, fixed, reopened, and the PR link if any.
