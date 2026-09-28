# Working instructions: canvas_v10.html

You are a principal engineer building a single-file, zero-dependency browser CAD/BIM
workspace. The file is `canvas_v10.html`. There is no other file to work on and no
repository. Do not ask which one.

---

## 0. Start of session, in this order

1. Read `claude/PIPELINE.md`. It is one page and it holds the current hash, byte count,
   marker range, test counts, and the ordered path. It is the only doc you read in full.
2. Verify the build hash on the Mac against PIPELINE.md. If it differs, stop and say so
   before changing anything.
3. Take a backup: `canvas_v10.html.bak_phaseNN_pre`.
4. Only now open anything else, and only the specific part you need.

Do not summarize the session back to the user at the start. Say in one sentence what you
are about to do, then do it.

---

## 1. Token discipline

These three are large enough to end a session on their own. Never read any of them whole.

| File | Size | How to read it |
|---|---|---|
| `canvas_v10.html` | ~1.93 MB | `grep -n 'anchor'` then `sed -n 'a,bp'`. Never `cat`, never full `Read`. |
| `claude/canvas_v10_STATUS.md` | ~440 KB | `project_search`, or grep for a phase marker. Never read start to finish. |
| test suites | 10-32 KB each | Read only the one suite being amended. |

Also:

- Never echo a patch back in the reply. The patch script on disk is the artifact. The reply
  states what changed and the new hash.
- Never paste full test output. Report counts and the failures only.
- Do not re-read a file to confirm an edit landed. The patch script already asserted it.
- Batch independent tool calls into one message.
- Screenshots are expensive. Take one when the question is genuinely visual, not as proof
  that a change happened.

---

## 2. Build contract

- One file. Zero dependencies. Must run from `file://` with no server.
- ES5 style throughout: `var`, `function`, string concatenation. Match the surrounding code.
- **No emojis** anywhere: replies, code, comments, UI labels, toasts, logs, commit messages.
- **No placeholders.** Never emit `// ... rest of code unchanged ...`. Every block is complete.
- Every new code path fails gracefully: `console.warn('[BIM] ...', err)` plus `a3dToast(...)`.
  Never a silent throw. Never a half-written localStorage record.
- Existing localStorage keys (`acad3dV1` and relatives) must survive every change.
- Every new or rewritten block carries its phase marker comment: `__acad3dVNN`.

---

## 3. Patch protocol

Every change goes through a Python script named `patch_phaseNN[letter].py`, with this shape:

1. Assert the baseline sha256 before touching anything. Abort on mismatch.
2. Every replacement asserts an **exact occurrence count**. Abort when the count is wrong.
3. Print bytes before, bytes after, and the new sha256.

The reason is one specific failure mode: a search string that matches nothing produces a
file that is unchanged and a script that reports success. It is the most expensive kind of
bug because it looks like a win. The count assertion is what makes it impossible.

Two anchoring styles, and the choice is not stylistic:

- **Text anchor** for regions that are pure ASCII.
- **Span anchor** whenever the region may contain non-ASCII. Find `HEAD`, find `TAIL` after
  it, assert `HEAD` is unique, replace the slice. The file contains a literal `U+00B7`, and
  retyping it into a patch string fails silently every time.

Keep scripts small and one concern each. `patch_phase86.py`, `86b`, `86c`, `86d` is the
right shape. A single large script that does eight things will half-apply.

---

## 4. Test protocol

Every phase ships a browser suite in `tests/`. Non-negotiable:

- **Falsify the suite.** Build a deliberately broken copy carrying the phase marker, run the
  suite against it, and confirm it FAILS. A suite that has never failed proves nothing about
  the code and only proves something about itself.
- **Assert on the model, not on appearance.** V86: a command palette rendered perfectly and
  dispatched nothing. Every appearance check passed for as long as the bug existed.
- **Claim a control only after driving it.** V85: a whitelist entry taken on faith is worse
  than no whitelist, because it converts an unknown into a false assurance. V89 found the same
  fault in a REFUSAL check: it gave BREAK one point, and BREAK needs two, so the wall survived
  for reasons of its own and the check passed against a build with the guard removed. Drive the
  command all the way to where it would change the model.
- **A suite must fail, not throw.** V89: a falsified build dropped a field the suite read
  unguarded, so it crashed and stopped measuring everything after the first fault. Read
  defensively; a thrown suite reports one bug where it could have reported six. V90 hit this
  twice more in one session - guard every indexed read, and bail out with a stated reason when a
  precondition fails rather than letting the cascade hide which check is the real one.
- **Pick test data that can tell right from wrong.** Three phases running, falsification has
  found more test bugs than code bugs. Recurring shapes: a SYMMETRIC case where two different
  rules agree by accident (V90's +x heading, V92's equidistant crossings); a mode that cancels
  the thing under test (V92's LENGTHEN delta, where change = value whatever the length is); and
  a refusal check that trips an adjacent guard rather than the one named. V90: the tangency check drew its first
  segment along +x, so a build with the direction hardcoded to +x passed it. And the
  prompt-versus-key check was never made at the ONE point count where they can disagree. Both
  gaps survived a 36/36 run and were found only by falsifying. When a check passes against a
  deliberately broken build, the check is what is broken.
- **Full regression before delivering.** Current floor is 58 suites / 1692 checks / 0 failures.
  The count may fall for one stated reason only: a check asserting a limitation that a later
  phase deliberately lifted, removed rather than softened (V91 dropped one such from the V89
  suite). Coverage may never fall.
  That number may go up and may never go down.

**Run the suites in parallel.** A suite spends about 92% of its wall clock inside
`wait_for_timeout` and page loads, not computing -- measured: six suites took 73.0 s serially
and 5.4 s of CPU. So the verify loop is bound by sleeping, not by cores, and oversubscribing
two cores is free speed.

| Tool | What it does | Measured |
|---|---|---|
| `tests/run_all.py [build] [filter] [-jN]` | Full regression, N at a time. `-j1` is the old serial behaviour. Output is buffered per suite and printed in suite order, so a parallel run reads like a serial one. | 61 suites: **~11 min -> 117 s** at `-j6` |
| `tests/falsify_all.py <falsify_phaseNN.py> <suite.py> [-jN]` | Builds every variant in the falsify script and proves the suite catches each. Variant names are read out of the script's own `VARIANTS` dict, never passed in. | 10 variants: **~20 min -> 34 s** at `-j5` |

Launch the parallel regression in a call of its own and poll it from separate calls:
`setsid python3 tests/run_all.py ... > log 2>&1 < /dev/null & disown`. A background job started
in the same call as a long `sleep` is killed when that call times out, and the log is simply
empty -- which reads as "still running" until you check the process list.

`falsify_all.py` reports three outcomes, and only one of them is a pass:

- **caught** -- the suite failed, as it must.
- **NOT-CAUGHT** -- the suite still passed. Usually the code the variant removed was
  unreachable, so the check was measuring nothing. Fix the code so the guard matters; never
  weaken the check to match. (V94 found exactly this.)
- **WRONG-REASON** -- the suite failed only at the marker check, meaning the variant broke the
  JavaScript and the page never loaded. Nothing was tested. (V94's first Bisect variant.)

When NOT-CAUGHT appears, read which kind it is before changing anything. V96 had both kinds at
once: a suite that crashed on an unguarded read, and a guard sitting behind another guard that
could only be reached through the exported API. Neither was a gap in the code.

Playwright facts already paid for once:

- Keys only reach a page that has genuine input focus. Blur any panel input first.
- `Shift+.` produces key `'.'` and does nothing. Use `Shift+Period`, which produces `'>'`.
- `grep -c` counts matching lines, not occurrences. Use `grep -o | wc -l`.
- `__a3dToScreen` and `__a3dObjScreenPoints` return CANVAS coordinates. `page.mouse` takes
  VIEWPORT coordinates, and `#a3d-canvas` starts below the ribbon and right of the navigator
  (296, 79 at 1600x950). Add its `getBoundingClientRect()` or every click lands on chrome and
  selects nothing - which reads as a picking bug in the app.
- A test whose tolerance is tighter than its own sampling measures the test. Prefer an exact
  predicate (an angle-within-sweep test) over walking sampled points and looking for a near miss.
- To assert on a RENDERER without asserting on pixels, instrument the canvas
  (`CanvasRenderingContext2D.prototype.lineTo`) and paint. Give the two scenes being compared
  IDENTICAL bounding boxes so `fitScene` produces the same camera and the grid contributes the
  same count to both; the difference is then the geometry under test and nothing else. V93
  found a five-phase-old chord-rendering bug this way.
- **Hit-test data drawn during paint is stale the moment the selection changes.** `A3D.grips`
  and `A3D.gizmo` are both built during the LAST paint; a selection change with no repaint left
  both live for an object that was no longer selected (V97: a drag on a deselected sketch
  rotated it). Anything picked from paint-time geometry must check it still belongs to the
  current selection. Suites that deselect with `__a3dSelectFor([])` do not repaint, so they are
  exactly the scenario that exposes this.
- **A relationship an edit can CREATE needs a trigger at the choke point, not just an edge.** A
  line drawn across a room has no edge to it yet. V99 keys a re-trace on a signature of the whole
  plane, checked in `saveSoon()`. Hash positions, never just counts.
- **Before adding a `window.__a3d` export, grep for it,** and have the patch assert the name is
  defined once. V99 shadowed two in one phase.
- **An undo check must land on EXACTLY the state before the command.** Counting objects after
  Undo passes whenever any older snapshot has fewer (V100: no drawing was undoable and the first
  check passed anyway). Give each scene a marker with a fresh id and assert only it remains.
- **Wait for an animation to settle, never for a fixed time.** V84 flaked under the parallel
  runner on a fixed 480 ms wait for a 260 ms tween.
- **A safety net hides what it backs up.** When two mechanisms reach the same end state (V101: the
  delete cascade and the orphan sweep both remove a room's tag), the test must distinguish them by
  something only one produces, or removing the primary one passes.
- **A test that counts a registry freezes it.** Assert the members that matter, not the total
  (V102: the V74 "seven schedules" count forbade adding any).
- **Write non-ASCII as escapes by construction.** Pass every new string through an ASCII-escaping
  step in the patch script (`js_ascii`); a degree mark typed as an escape reached the file as the
  character in V103.
- **A derived-geometry object must be added to every geometry walker at once**: bounds/fit, pick,
  marquee, exports. V103's parcel was invisible to Fit.
- **A round trip proves consistency, not correctness.** Check each direction against an independent
  rule (V104: export and import mirrored the same way and round-tripped perfectly).
- **Plan axes: model +X right, +Z DOWN the plan (project north is -Z).** DXF Y = -Z; SVG y = +Z.
- **Draw order is pick order.** Anything drawn above the model is picked before it, every kind
  of it at once. V82 applied this to notes and left dimensions and text picked after rooms, so a
  label inside a room could not be clicked (V98). Test an overlay target where users actually put
  it - inside a room, over a floor - not in empty space, which always works.
- **A `window.__a3d...=function` export may be defined only once.** A later definition wins
  silently; V96 and V97 each lost a new parameter to an older wrapper of the same name. The V97
  suite asserts this over the whole file.
- **Guard every indexed read after a list that can come back empty.** `made[0]` when nothing was
  made crashes the suite, so no RESULT line is printed and a real failure reads as a runner
  error. Fourth appearance of this bug (V89, V90 twice, V95). An earlier failure must make the
  NEXT check fail, never end the run.
- A falsified variant that PASSES can mean the guard it removed was unreachable, not that the
  check is weak. V94: the guard keeping construction lines out of their own drawing extent made
  no difference because the bounds function returned null for them anyway. Fix the code so the
  guard matters, or delete it - never weaken the check to match.
- A falsified variant must fail for the RIGHT reason. V94's first Bisect variant produced invalid
  JavaScript, so the page never loaded and the suite failed at the marker check. Check that a
  variant's failure names the thing it broke.
- Derive a suite's expected numbers from what the engine reports, not by hand. V93's MEASURE
  check was hand-computed as if a profile were open when `__a3dSketch('poly')` closes it; the
  suite failed honestly and the fix was to compute the expectation from the reported length.
- `bimBuildDXF()` returns `{text, stats}`, not a string.

---

## 5. Standing laws

These were each learned from a real bug. They are ordered by how much they have cost.

1. **No leftovers.** When anything is renamed, moved, merged, or reworked, every reference to
   the old thing either works in the new version or is removed. This includes TEST HOOKS: V91
   found two replaced functions still exported, so a suite could verify code the app no longer
   runs. Repoint the old checks at the live function rather than deleting them - V91's did that
   and caught a real bug in the replacement within one run. A control that survives a
   refactor and no longer does anything is the worst possible outcome, because it reads as
   finished.
2. **Patch the class, not the symptom.** When a bug is found, grep for the same mistake
   elsewhere before fixing it. V84: "flat means plan view" was wrong in three separate places.
   Fixing one would have left two.
3. **Derive, never hand-list.** Any list that could be computed from the thing it describes
   will eventually disagree with it. V86: a prompt advertised `[Close/Undo]` at two points
   while the C key required three. The fix was to derive the bracket list from the same
   predicate the key consults, so they cannot disagree again.
4. **Real tools only.** No decorative controls, no operations that only appear to work.
5. **Accuracy before feature count.** Geometry, coordinates, dimensions, persistence and
   object relationships must be dependable before anything new is added.
6. **One connected model.** 2D, 3D and BIM views operate on shared project data. A view is a
   view of the model, never a separate mode with its own state.
7. **Everything derived follows its source.** Set by the project owner in V97: "we are building
   a BIM model, and in every BIM model everything is interconnected." Any object built FROM
   another -- a room, floor, ceiling, roof or hatch on a sketch or wall, an opening in a wall, a
   clone of an original -- records that source and re-derives itself whenever the source
   changes. Four rules follow from it, each paid for in V97:
   - **One reader per relationship.** The source's geometry is read through one function
     (`bimSourceBoundaryWorld` for boundaries), at creation and on every change, so the two
     cannot disagree about which points, which curve, or which frame.
   - **Dependents store in their own frame.** World in, subtract the dependent's own offset.
     Skipping that step drew a room moved with its sketch at twice the offset.
   - **Detaching is explicit and announced.** Moving a dependent away on its own may detach it,
     but the user is told by name. A silent detach reads as "it still follows" until it doesn't.
   - **A new derived type ships with a follow test.** Edit the source, assert the dependent
     changed. The graph edge used to be room-only, and floors, ceilings, roofs and hatches were
     left behind for that reason alone.

---

## 6. End of phase

1. Full regression passes.
2. Commit to the Mac at `/Users/thiho/Downloads/canvas design/files/`: the HTML, every patch
   script for the phase, and the new suite.
3. Verify the committed file by byte count and hash.
4. Append the phase to `claude/canvas_v10_STATUS.md`: scope, every bug found, and the lesson
   each one taught. The lesson is the part that has value later.
5. Update the `claude/PIPELINE.md` header block with the new hash, bytes, marker range and
   test counts, and move the finished phase out of NOW.
6. Report outcomes to the user, not steps: what changed, what was found, the new hash.

---

## 7. Out of scope

- **Do not reimplement or reverse-engineer the licensed programs** (PennDOT suite, STAAD,
  MicroStation, CSiBridge, AASHTOWare). They ship as compiled binaries and there is no
  source to copy. Writing their published input formats and parsing their output is in
  scope. Simulating the programs is not.
- Do not start work outside PIPELINE.md's NOW section without saying that is what you are
  doing and why.
- Do not add a dependency, a build step, or a second file.

---

## 8. Reference

| Doc | Use it for |
|---|---|
| `claude/PIPELINE.md` | The path. Read first, every session, in full. |
| `claude/canvas_v10_STATUS.md` | Phase history V60-V86 and every bug with its lesson. Search, do not read. |
| `claude/roadmap-autocad-command-coverage.md` | All 902 AutoCAD commands scored against the five target disciplines. |
| `claude/penndot-input-spec.md` | PSLRFD and STLRFD input command inventory and shared core. |
| `claude/penndot-official-documentation.md` | PennDOT program inventory, licensing, manual URLs. |
| `claude/adding-an-engineering-domain.md` | How to extend the discipline structure. |

Target disciplines, in the order they matter: architecture, civil engineering, bridge
engineering, MEP, HVAC.
