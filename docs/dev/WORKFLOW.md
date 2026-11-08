# The daily routine: Claude Code, the cloud, Bionic

The owner works with three tools on this repository (2026-11-08). No tool remembers another's session:
the repository is the memory. Git carries the work between them, and `docs/dev/PIPELINE.md` says
where the project stands.

## The whole routine

    open the tool  ->  /start  ->  work  ->  /finish

`/start` and `/finish` are this repository's own commands (`.claude/skills/start/`, `.claude/skills/finish/`).
They work in Claude Code on the PC and in a cloud session. The owner only has to remember those two
words; Claude does the steps and says what it found.

## Who does what

| Tool | Where | For |
|---|---|---|
| Claude Code, local | `C:\World-BIM-platform\BIM-Personal`, run `claude` in PowerShell | The main workbench: phases, features, bugs, build and tests, PRs. Sends bulk work to Qwen. |
| Claude Code, cloud | The Claude app or claude.ai/code | Work away from the PC, research, watching PRs and fixing CI, a second task in parallel. |
| Bionic | The PC | Quick edits by hand, questions about the code, private or offline work. Free. |
| Qwen 2.5 Coder 14B | Bionic's local server, `http://localhost:1235/v1` | The subcontractor local Claude sends bulk work to. Only reachable from the PC. |

Local and cloud Claude share one usage limit (`/usage` shows it). Bionic and Qwen do not use it.

## The four rules

1. **One branch, one tool.** Two tools never work on the same branch at the same time.
2. **Push before switching** between the PC and the cloud: they see each other only through GitHub.
3. **Pull before starting** on the PC, so no work is done on an old copy.
4. **The repo is the memory.** What the next session needs goes in `PIPELINE.md`, the code, or the PR.

## Switching

- **Leaving the PC mid-task:** `/finish` (it pushes the branch). In the cloud: "continue on branch X".
- **A Bionic edit:** work on its own branch (`bionic/<task>`), commit, push. Then in either Claude:
  "review the diff on branch X against main" before the PR is merged.
- **Two tasks at once:** the second one in the cloud, on its own branch.

## Bionic: paste this at the start of a session

Bionic does not read `CLAUDE.md` on its own. Paste:

> This repo's rules: edit only `src/`, never `canvas_v10.html` (it is built). Never edit the import and
> export lines at the top and bottom of `src/js/engine/**` files. ES5 JavaScript, no dependencies, no
> emojis. Work on a branch named `bionic/<task>`, never on `main`. After an edit run
> `python3 tools/build_app.py`, `npm run check` and `npm test`, and commit `canvas_v10.html` with the
> change. If the task does not fit the code as described, stop and say what is different.

## This PC's setup (2026-11-08)

Git 2.56, Node 26, Python 3.13 (with a `python3.exe` copy beside `python.exe`), TypeScript 5.9.3
installed globally (the module check needs it), PowerShell execution policy `RemoteSigned` for the user.
The clone has `core.autocrlf false` and `core.eol lf`: a CRLF checkout fails every unit test.
