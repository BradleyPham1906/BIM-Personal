---
name: review-aider
description: Review, finish and hand over work the owner did with Aider (the local model). Use when the session-start notice reports unreviewed Aider work, when /start finds it, or when the owner says they used Aider.
---

# /review-aider

The owner does not read code. Aider (Qwen 2.5 Coder 14B, local) makes edits and leaves them
uncommitted; Claude is the reviewer who makes them safe. Report in plain words: what the change does
for the app, whether it is right, and what Claude fixed. No code in the report unless asked.

## 1. Find the work

- **Uncommitted changes:** `git status`, `git diff`. Read `.aider.chat.history.md` from the last
  `# aider chat started at` line: the `####` lines are what the owner asked for. If the changes are
  on `main` or on a branch for other work, move them to a new branch first:
  `git switch -c aider/<short-task-name>` (uncommitted changes come along). Never discard them.
- **An `aider/*` branch not merged into main:** `git switch aider/<task>`, `git diff origin/main...HEAD`.
- If the changes are clearly not Aider's (for example Claude's own unfinished work from a session
  that did not run /finish), say so and ask before treating them as Aider's.

## 2. Review against what was asked and the repo's rules

If the branch has work orders (`docs/work-orders/vNNN/TASKS.md`), review each task ticked `[x]`
against its work order and SPEC.md, do the `[Claude]` and `[skipped]` tasks, and finish only when
`grep -rn "WO-" src/` is empty and every test passes (`docs/work-orders/README.md`, step 7).

Check every changed line:
- Does it do what the owner asked (or its work order says), and nothing else? Undo unrelated edits.
- Names that do not exist: every function, variable and file it uses must be in the code
  (`grep -rn 'name' src/`). Small models invent them.
- The build contract: ES5 (no `let`, `const`, arrow functions, classes, template strings), no
  dependencies, no emojis, no placeholders or TODO stubs.
- Never hand-edited: `canvas_v10.html`, the generated `import`/`export` lines in
  `src/js/engine/**` (if they changed, restore them and run `npm run modules`), `src/js/vendor/`,
  `runtime/`, `vendor/`.
- Whole-file rewrites or large unrelated reformatting: restore the file and reapply only the change.

Fix what is wrong yourself. If the change cannot be made right (a wrong approach, or engine logic a
14B model should not have touched), say so plainly and offer to redo it properly.

## 3. Check it

Follow CLAUDE.md's Rule #1 table for the files changed (syntax check, `npm test`, `npm run modules`
when shared names changed). If anything under `src/` changed, rebuild: `python3 tools/build_app.py`.

## 4. Hand over

Commit (message starts `Aider: `, says what it does and what the review fixed), push, and open a PR
against `main` if none exists. Then tell the owner, in a few plain lines:
- what the change does in the app;
- the verdict: good as is, good after fixes (which, in one line each), or not usable (why);
- the PR link, and one question: "Merge it?" Merge only on a yes (`gh pr merge --merge`), after CI
  passes.

Do this for each piece of Aider work found, one at a time.
