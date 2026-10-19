# BIM-Personal: start here

A single-file, zero-dependency browser CAD/BIM app, `canvas_v10.html`, built phase by phase (V1 to
V166 so far), each phase verified by its own browser suite, deliberately broken builds its suite
must catch, and the full regression.

## In a new session

1. Read `PIPELINE.md` first, in full: the build's hash and size, the test counts, and the ordered
   path, with the phase marked **Start here**.
2. Then `CLAUDE_INSTRUCTIONS.md`: the build contract (ES5, one file, no dependencies, phase markers,
   failures warned and toasted), the patch protocol (anchored Python scripts asserting exact counts
   and the base hash), the test protocol and the standing laws. Its paths under `claude/` and on a
   Mac are from an older setup: the files are at the repository's root, `Phase/`, `tests/` and
   `reference/`.
3. The current work plan is `reference/plan-v167-v170.md`; each phase's research note is in
   `reference/`; the engineering log is `canvas_v10_STATUS.md` (search it, never read it whole).

## Research depth (the owner, 2026-10-17)

"The more careful research the better for our plan when execute." Every phase's research follows
`reference/research-protocol.md`:
- every fact the code uses is read in its primary source (P), or in a dependable secondary one with
  the gap said (S); search-engine summaries are pointers, not sources (U), and U facts never reach
  the code;
- practice, the standard and its edition, where it applies, the free data tested from here, open
  implementations read as text, the edges of the rules, and the app's own code, for each topic;
- the owner's decisions asked together at the end of research;
- the note records each source, what was read, the date and its level, and what is still open.

## Notion (the owner, 2026-10-19)

The owner follows the project in Notion, on **World BIM Platform** (a Project in their G/P/R DB): every phase is
a task in the Internal Task DB, every research note and document a page in the Documentation DB, each pull
request a line on its phase's task. Keep it current as the work goes, through the Notion connector, at each step
of a phase (research started, the owner's decisions, PR opened, PR merged): `reference/notion-sync.md` has the
ids, the relations, the fields and the steps. The repository stays the source of truth; Notion mirrors it,
summarised and linked, never the full text.

## Standing choices of the owner

- Free, keyless data only, credited; a server without CORS is named, not proxied.
- Industry standards kept as data with their editions, flexible when they change (V167's registry).
- Everything on phone, tablet and desktop. No emojis. No placeholders. Copyrighted text in our own
  words. Project photos and third-party screenshots never committed: the repository is public.
