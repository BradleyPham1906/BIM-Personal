---
paths:
  - "src/**"
  - "tests/**"
  - "tools/**"
  - "docs/work-orders/**"
---

# Aider-first implementation workflow

- For implementation tasks in this workspace, Cline coordinates and the MCP server named `aider` makes project-file changes.
- Use Aider's `edit_files` tool for existing files and `create_files` for new files. Do not edit project files with Cline's built-in editing tools or shell commands.
- For V175a, `[ ]` in `docs/work-orders/v175/TASKS.md` means open and `[x]` means done; there is no separate Aider checkbox UI. Never wait for the user to tick a task. If asked for the next task, take the first open `[Aider]` item from the top of the file. Preserve its listed order, including WO-06 before WO-05.
- If the user names a work order, do only that work order. Once it is identified, call the MCP server `aider`'s `edit_files` tool promptly, with the exact acceptance criteria, target file/function, and relevant constraints. Do not merely announce an intention to use Aider.
- Keep exploration focused. Read each required task/spec/source file at most once per task, and rely on content already in context. Do not reread files after context compaction or scan unrelated parts of the repository.
- If the `aider` MCP tool is missing, disconnected, or fails, stop after that failed attempt and tell the user. Do not keep rereading files, wait for a checkbox, or fall back to Cline editing.
- Do not start a separate Aider terminal session for a Cline task; Cline must invoke the connected MCP server.
- Follow `CLAUDE.md` startup instructions at the start of a fresh task. Follow `CLAUDE.md` and `docs/dev/CLAUDE_INSTRUCTIONS.md` for source, build, and testing requirements. Run only the checks required by those instructions; do not run browser checks or full regression unless requested.
- Follow `CLAUDE.md` and `docs/dev/CLAUDE_INSTRUCTIONS.md` for source, build, and testing requirements. Run only the checks required by those instructions; do not run browser checks or full regression unless requested.
- Cline may read, search, review diffs, and run required project checks. Build or test commands may generate their prescribed outputs, but do not use shell commands to make source edits.
- After each work order, report the work order completed, files changed, checks run, and anything unresolved.
