# Who does a task: the difficulty score

Every task goes to the cheapest worker that will get it right the first time. A task done wrong by a
cheap worker costs more than doing it right once, so the score is about **getting it right**, not
about size alone. Cline with Nemotron 3.5 Super VL is the primary first-pass implementer; Aider is a
backup, not a separate default tier.

## The workers, cheapest first

| Tier | Worker | Costs | Best at |
|---|---|---|---|
| A | Cline alone (Nemotron 3.5 Super VL) | free model option | A small, exact change in one file whose result is easy to see |
| B | Cline with a work order | Claude time to write the order and its test | Bounded implementation tasks with explicit behavior and tests |
| C | Claude, lighter model (`/model sonnet`) | less of the weekly limit | Ordinary features and fixes across a few files |
| D | Claude, strongest model (the default) | the most | Research, design decisions, hard bugs, and review |

## Score the task: six questions, 0 to 2 points each

| Question | 0 | 1 | 2 |
|---|---|---|---|
| 1. How many files change? | one | two | three or more |
| 2. How much new logic? | under 40 lines | 40 to 150 | over 150 |
| 3. How much code must be understood first? | the names are given | a few functions must be found | a whole module, or how modules fit together |
| 4. How much judgment? | the exact result is stated | small choices | open design, or research |
| 5. How tricky is it? | text, style, data, simple conditions | loops over data, simple maths, UI events | geometry, undo/history, rendering, async, shared state, file formats |
| 6. How is it checked? | a unit test exists or will be written | seen in the app at a glance | hard to tell it is right |

**Total 0 to 12:**

| Total | Tier |
|---|---|
| 0 to 2 | **A** Cline alone |
| 3 to 4 | **B** Cline with a work order (Claude writes the order and the test first) |
| 5 to 7 | **C** Claude, lighter model |
| 8 to 12 | **D** Claude, strongest model |

**Always D, whatever the score:** research; the owner's decisions; the spec and task design of a
phase; reviewing Cline's work; a bug whose cause is unknown; anything touching saving, loading or
deleting the owner's files; security; the build tools and CI.

**Never A, whatever the score:** anything in `src/js/engine/core/`, `render/` or `history/`, and the
import/export lines (tier B at most, with a test).

## Examples

| Task | 1 | 2 | 3 | 4 | 5 | 6 | Total | Tier |
|---|---|---|---|---|---|---|---|---|
| Change a button's colour or a label's text | 0 | 0 | 0 | 0 | 0 | 1 | 1 | A |
| Explain what a file does | 0 | 0 | 1 | 0 | 0 | 0 | 1 | A |
| Fill in a work-order function that has its test | 0 | 0 | 0 | 0 | 1 | 0 | 1 | B (the order is Claude's) |
| Add a new field to the properties panel | 2 | 1 | 1 | 1 | 1 | 1 | 7 | C |
| A new drawing tool | 2 | 2 | 2 | 2 | 2 | 1 | 11 | D |
| "The wall disappears after undo" | 1 | 0 | 2 | 1 | 2 | 2 | 8 | D |

## How to use it

- **The owner:** ask Cline or Claude "score this with ROUTING.md: <task>". Then give the task to
  the tier it lands on. For tier C, type `/model sonnet` in Claude first, and
  `/model default` after.
- **Claude, writing work orders:** score every task in a phase's TASKS.md and mark it `[Cline]`
  (tier A or B) or `[Claude]` (C or D). For an owner-approved local prototype, a bounded and
  verifiable `[Cline]` task may still be used above tier B; split it into smaller tasks and keep
  research, open design, unknown-cause bugs, and safety-critical data changes with Claude. Split a
  task that scores 5 or more when the pieces would
  each score 4 or less: that moves work to the free tiers.
- **Aider fallback:** use only when Cline is unavailable or the owner asks. Aider's Qwen results
  are not evidence for Nemotron's calibration.
- **Claude, given a request:** if it would score 0 to 2, say so in one line ("Cline can do this
  with its free model option") and do it anyway unless the owner prefers to switch.

## Getting better over time

`aider-log.md` is the historical record of Aider fallback tasks. Do not infer Nemotron performance
from Aider's Qwen results. Before changing Cline's thresholds, record its first-pass outcomes and
Claude's fixes in a separate Cline-specific record, then review that evidence with the owner.

| What the log shows for a total score | Change |
|---|---|
| 80% or more passed the first time, over 5 tasks or more | That score moves one tier cheaper (for example 5 becomes B) |
| under 50% passed without Claude's fix | That score moves one tier dearer |
| one question keeps marking the failures | Raise its points, or add the case to "Never A" |

Each change goes in the history below, with the date and the rows behind it. Any model change starts
the evidence over: note it in the history and recalibrate.

## Thresholds history

| Date | Change | Evidence |
|---|---|---|
| 2026-11-11 | First version: A 0-2, B 3-4, C 5-7, D 8-12 | None yet: starting estimates |
| 2026-11-11 | Cline/Nemotron replaces Aider/Qwen as the A/B worker; calibration starts fresh | No Cline task history yet; Aider results remain historical |
