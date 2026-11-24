# The terminal: macOS (zsh) or Windows (PowerShell 5.1)

The owner works on three machines (2026-11-24): a MacBook, a Windows mini PC (Beelink) at home and a
Windows PC at the office. Before the first command, look at which one this is (the terminal's prompt, or
a path that starts with `/Users/` versus `C:\`), and write every command so it works in both shells:

- **One plain command per call**, run from the repository root. No `cd`, no `git -C <path>`: the terminal
  is already there. Never type the repository's path; it differs per machine.
- **Python:** `python3` on the Mac, `python` on Windows. The gate prints the right one in its messages.
- **No `&&` or `||`** (PowerShell 5.1 rejects them). Run the commands one after another.
- **No heredocs** (`<< 'EOF'`), and no `python -c "..."` or `node -e "..."` with code inline. PowerShell reads
  `[`, `]`, `$`, `{`, `}`, `@` and backticks itself, which is the "Missing type name after '['" error. To run a
  script, write it to a file with the editor tool and run the file.
- **Quote an argument that has brackets, braces, spaces or `$`** in single quotes, on both shells:
  `--test-name-pattern='WO-09'`, `'stash@{0}'`.
- **Edit files with the editor tool only**, never with shell commands (`echo >`, `sed`, `del`, `cmd /C`).
  After an edit, read the file's changed range once: a repeated edit that pastes the same function twice
  must be removed before the gate runs (it counts every added line against the task's budget).
- Use the search and read tools, not `head`, `tail`, `grep`, `cat` or `wc` (missing on Windows).

The commands a task needs (Mac shown; on Windows write `python` for `python3`):

    git status
    python3 tools/handoff.py status
    node --check src/js/engine/io/ifc-save.js
    node --test --test-name-pattern='WO-09' tests/unit/ifc-save.test.mjs
    npm test
    python3 tools/gate.py check v177 WO-09
    python3 tools/gate.py ship v177 WO-09
    python3 tools/handoff.py park

If a command still fails to parse after one retry, stop and report its exact text and the error. Do not switch
to another task or another file to get around it.
