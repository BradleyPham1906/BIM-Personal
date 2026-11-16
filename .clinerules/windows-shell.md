# The terminal here is Windows PowerShell 5.1, not bash

The commands in the TASKS files and in the `ship-task` skill run as written. Trouble starts only with bash syntax.

- **One plain command per call**, run from the repository root (`C:\World-BIM-platform\BIM-Personal`). No `cd`,
  no `git -C <path>`: the terminal is already there.
- **No `&&` or `||`.** Run the commands one after another, or join them with `;`.
- **No heredocs** (`<< 'EOF'`), and no `python -c "..."` or `node -e "..."` with code inline. PowerShell reads
  `[`, `]`, `$`, `{`, `}`, `@` and backticks itself, which is the "Missing type name after '['" error. To run a
  script, write it to a file with the editor tool and run the file.
- **Quote an argument that has brackets, spaces or `$`** in single quotes: `--test-name-pattern='WO-09'`.
- **Edit files with the editor tool only**, never with shell commands (`echo >`, `sed`, `del`, `cmd /C`).
  After an edit, read the file's changed range once: a repeated edit that pastes the same function twice
  must be removed before the gate runs (it counts every added line against the task's budget).
- `python` and `python3` both work. `head`, `tail`, `grep`, `cat -A`, `wc` do not: use the search and read tools.

The commands a task needs, all of which work here as written:

    git status
    node --check src/js/engine/io/ifc-save.js
    node --test --test-name-pattern='WO-09' tests/unit/ifc-save.test.mjs
    python tools/build_app.py
    npm test
    python tools/gate.py check v177 WO-09
    python tools/gate.py ship v177 WO-09

If a command still fails to parse after one retry, stop and report its exact text and the error. Do not switch
to another task or another file to get around it.
