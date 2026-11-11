# Who does a task: the difficulty score

Every task goes to the cheapest worker that will get it right the first time. A task done wrong by a
cheap worker costs more than doing it right once, so the score is about **getting it right**, not
about size alone. The thresholds are not fixed: they move with the results in `aider-log.md`
(see "Getting better over time").

## The four workers, cheapest first

| Tier | Worker | Costs | Best at |
|---|---|---|---|
| A | Aider alone (Qwen 2.5 Coder 14B) | nothing | A small, exact change in one file whose result is easy to see |
| B | Aider with a work order | a little Claude to write the order and its test | Routine functions in a design Claude already made |
| C | Claude, lighter model (`/model sonnet`) | less of the weekly limit | Ordinary features and fixes across a few files |
| D | Claude, strongest model (the default) | the most | Research, design, engine logic, hard bugs, review |

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
| 0 to 2 | **A** Aider alone |
| 3 to 4 | **B** Aider with a work order (Claude writes the order and the test first) |
| 5 to 7 | **C** Claude, lighter model |
| 8 to 12 | **D** Claude, strongest model |

**Always D, whatever the score:** research; the owner's decisions; the spec and the skeleton of a
phase; reviewing Aider's work; a bug whose cause is unknown; anything touching saving, loading or
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

- **The owner:** ask either tool "score this with ROUTING.md: <task>". Aider scores for free. Then
  give the task to the tier it lands on. For tier C, type `/model sonnet` in Claude first, and
  `/model default` after.
- **Claude, writing work orders:** score every task in a phase's TASKS.md and mark it `[Aider]`
  (tier A or B) or `[Claude]` (C or D). Split a task that scores 5 or more when the pieces would
  each score 4 or less: that moves work to the free tiers.
- **Claude, given a request:** if it would score 0 to 2, say so in one line ("Aider could do this
  for free") and do it anyway unless the owner prefers to switch.

## Getting better over time

`aider-log.md` records every task Aider did: its score and what happened. In the review (the
review-aider skill), Claude adds one row per task. After each phase, Claude reads the rows since the
last calibration and adjusts:

| What the log shows for a total score | Change |
|---|---|
| 80% or more passed the first time, over 5 tasks or more | That score moves one tier cheaper (for example 5 becomes B) |
| under 50% passed without Claude's fix | That score moves one tier dearer |
| one question keeps marking the failures | Raise its points, or add the case to "Never A" |

Each change goes in the history below, with the date and the rows behind it. A new local model (a
bigger Qwen, say) starts the evidence over: note it in the history and recalibrate.

## Thresholds history

| Date | Change | Evidence |
|---|---|---|
| 2026-11-11 | First version: A 0-2, B 3-4, C 5-7, D 8-12 | None yet: starting estimates |
