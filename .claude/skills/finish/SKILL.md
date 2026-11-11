---
name: finish
description: The owner's end-of-session routine for this repo. Use when the owner types /finish or says they are stopping or switching tools.
---

# /finish

The routine is in `docs/dev/WORKFLOW.md`. Do these steps, then report in a few lines.

1. `git status`. If nothing changed and nothing is unpushed, say so and stop.
2. If the branch is `main`, make a new branch for the work first (`claude/<task>` or `aider/<task>`).
   Never push to `main`.
3. Run only what CLAUDE.md's Rule #1 table asks for the files that changed. If anything under `src/`
   changed, rebuild with `python3 tools/build_app.py` so `canvas_v10.html` is current. On a failure,
   show only the failing lines and stop.
4. Update `docs/dev/PIPELINE.md`: where the work stands and the next step, in a line or two, beside the
   phase it belongs to. Skip if nothing about the project's state changed.
5. Commit with a clear message, and push with `git push -u origin <branch>`.
6. If no open PR exists for the branch, open one as a draft. Give the owner its link.
7. If a phase step happened (research started, a decision, a PR opened or merged), say that Notion is
   due an update per `docs/research/notion-sync.md`, and do it if the Notion connector works here.
8. Report: the branch, the commit, the PR link, and the one-line next step for the next session.
