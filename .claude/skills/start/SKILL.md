---
name: start
description: The owner's start-of-session routine for this repo. Use when the owner types /start or says they are starting work.
---

# /start

The routine is in `docs/dev/WORKFLOW.md`. Do these steps, then report in a few lines. Run no tests
(CLAUDE.md, Rule #1).

1. `git status` and `git branch --show-current`. If there are uncommitted changes, say so and stop:
   ask whether to commit, stash or keep them. Never discard them.
2. `git fetch origin`. Then:
   - On `main`: `git pull`.
   - On another branch: say how far it is behind `origin/main`, and ask whether to keep working on it
     or start from `main`. In a cloud session, stay on the branch the session was given.
3. Read the row marked **Start here** in `docs/dev/PIPELINE.md`, and the handoff notes beside it if any.
4. On the PC only: check whether Qwen is reachable (`http://localhost:1235/v1/models`). One line: up or
   not. If not, say "Bionic's Local API server is off" and carry on; it is not needed to start.
5. Report: the branch, whether it is current, what is next per PIPELINE.md, Qwen up or not. Then ask
   what the owner wants to work on, suggesting the next phase.
