# Research: the panels (V166b)

The owner, 2026-10-17: "make sure to fix the right panel also since i still see the analysis tab on
it (looks like form the old design). left panel needs to be dragable like the right panel also."

Researched to `reference/research-protocol.md`, the app's own code first.

## What was read

| Source | What was read | Date | Level |
|---|---|---|---|
| The app: V141's tabs (`BIM_PTABS`, `bimPropTabOf`, `bimSetPropTab`) | The Analysis tab held four groups: the active level's Floor Loads (V106), the frame's Analysis page (V125), the project's Areas by Usage and the Usages library (V131). Analyze's Frame analysis and Areas by usage rows had Settings and Open buttons that opened them there. | 2026-10-17 | P |
| The app: V147's right panel (`bimRightWire`) | Its edge: dragged with a mouse, 240 to 560 px, a double click resets it, kept in this browser, a computer's only; minimised to a strip. No keyboard and no one-press alternative. | 2026-10-17 | P |
| The app: V149's layouts (`bimShellTier`, `bimShellDockW`) | Desktop (a tablet on its side counts), overlay (an upright tablet, a phone on its side) and phone. The drawing's left edge is `--a3d-left-w`: 54 + 242 on a computer, measured as the panel's right edge in the browser. | 2026-10-17 | P |
| The app: V162's Analyze (`bimAnalyzeRefresh`) | Analyze is not redrawn under one of its own fields that has the focus, so words being typed survive; the redraw waits for the field to be left. | 2026-10-17 | P |
| The app: the key chain (`onKey`, `bimKeyForControl`, `__a3dTypeAnywhere`) | The model's keys run first, in the window's capture phase; a focused field or dropdown keeps its keys. Arrow keys nudge the selection. | 2026-10-17 | P |
| W3C, WAI-ARIA Authoring Practices, Window Splitter Pattern | Read as text from its source, `raw.githubusercontent.com/w3c/aria-practices/main/content/patterns/windowsplitter/windowsplitter-pattern.html`: role `separator`, `aria-valuenow`, `aria-valuemin`, `aria-valuemax`, a label, `aria-controls` naming the primary pane; Left and Right move a vertical splitter, Enter collapses the pane and restores it, Home and End (optional) to the smallest and largest. The page says the task force's review waits on a complete example. | 2026-10-17 | P |
| W3C, Understanding WCAG 2.2, 2.5.7 Dragging Movements | Read as text from `raw.githubusercontent.com/w3c/wcag/main/understanding/22/dragging-movements.html`: what a drag does needs a single-pointer way without dragging; keyboard access is a separate requirement, since a touch user may have no keyboard. | 2026-10-17 | P |
| W3C, Understanding WCAG 2.2, 2.5.8 Target Size (Minimum) | Read as text from `raw.githubusercontent.com/w3c/wcag/main/understanding/22/target-size-minimum.html`: 24 by 24 CSS px, with exceptions; one is an equivalent control that meets the size. | 2026-10-17 | P |

Refused here on 2026-10-17: `www.w3.org` (the same pages, published) and `code.visualstudio.com`.
Nothing at level U reached the code.

## What was decided, and why

- **The Analysis tab goes.** Properties keeps Project, Site and View with nothing selected. A tab
  remembered as Analysis opens on Project.
  - Frame analysis's settings (combination, self-weight, display, deflected shape), its results and
    the active level's floor loads are in its row in Analyze: the settings sit beside the analysis
    they set, which is what V162's one Analyze is for. The floor loads feed the Column Loads schedule
    and TRIBAREA, not the frame solve, and the row says so.
  - The project's areas by usage are in Areas by usage's row.
  - The usages library is the project's own (rooms, floors and masses take a usage; Colour by and the
    schedules read them), so it is on Project.
  - A change in a row is the model's at once, so the row is redrawn under the field, which keeps the
    focus (`bimRenderInto`). V162's wait still covers words being typed.
- **The left panel's edge**, as Properties' is: a mouse, a pen or a finger (pointer events), 242 px
  (what the panel's contents are built for) to 560 px, the drawing keeping 320 px beside Properties,
  a double click to put it back, kept in this browser. A computer's layout only, a tablet on its side
  included: a drawer keeps its own width, as Properties' sheet and drawer do.
- **The keyboard**, by the window splitter pattern: the edge is a focusable separator with its width
  as its value; Left and Right move it 16 px (64 with Shift), Home and End, Enter shuts the panel.
  The edge goes with the panel, so the focus moves to the panel button, whose Enter opens it again:
  that is how "Enter restores" is met here. The model's key chain treats a focused separator as a
  control, so the arrows do not nudge the selection.
- **One press.** For 2.5.7, a button beside the panel's collapse widens the panel a step at a time
  (242, 320, 400, 480, 560, within what the screen allows) and from the widest back to 242, saying
  where the next press goes. It is 30 px (36 on a touch screen), and it is the equivalent control
  that excepts the 6 px edge (12 px for a finger) under 2.5.8.

## Still open

- Properties' own edge (V147) has the same 2.5.7 gap: its only one-press control is minimise. The
  same button beside its minimise would close it.
- V162's wait covers a focused dropdown in Analyze too: Ctrl+Z pressed with one focused undoes the
  model, and the row shows it when the dropdown is left.
