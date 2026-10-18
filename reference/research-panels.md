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

# Research: Properties' width by one press (V166d)

The owner, 2026-10-18: a button in Properties' header that steps its width through fixed widths
within what the screen allows (the drawing keeps 320 px, as V166b's left panel does), labelled with
the next width, 30 px (36 on coarse pointers), hidden where Properties is a drawer or a sheet, claimed
in the shell's audit; the edge given the window splitter's keys. V166b's "Still open", above.

Researched to `reference/research-protocol.md`, the app's own code first, then tested in the browser.

## What was read

| Source | What was read | Date | Level |
|---|---|---|---|
| The app: V147's right panel (`bimRightWire`, `bimRightApply`, `bimRightDesktop`, its stylesheet) | The edge: `aria-hidden`, not focusable, `mousedown` only; clamped to 240-560 px whatever the screen. Docked, in the code, where the window is wider than 900 px; in the stylesheet, over 1024 px wide and over 500 high. Tested on V166b's build: a 120 px finger drag on a tablet on its side (1180 x 820) left Properties at 280 px; the arrow on a drawer (1000 x 800) and on sheets (932 x 430, a large phone on its side; 1280 x 480) shrank them to a 42 px strip with the body hidden. | 2026-10-18 | P |
| The app: V166b's left edge and button (patches 166e, 166f) | The rule followed here: the next step up within `bimLeftMax`, the widest when no step fits, from the widest back to the narrowest, said in the label; pointer events; the key chain treating a focused separator as a control. The left panel gives way to Properties (`bimLeftMax` reads Properties' width). | 2026-10-18 | P |
| The app: the shell's audit (`bimShellAudit`, `A3D_SHELL_CLAIMS`, V80) | It walks `#a3d-shell` only. Properties (`#a3d-right`) is outside it, so V147's minimise was never audited and a claim for the new button would have been decorative. Its selector did not count a focusable separator. | 2026-10-18 | P |
| W3C, WAI-ARIA Authoring Practices, Window Splitter Pattern | Re-read as text from `raw.githubusercontent.com/w3c/aria-practices/main/content/patterns/windowsplitter/windowsplitter-pattern.html` for the case V166b did not meet, a pane to the splitter's right. "Left Arrow: Moves a vertical splitter to the left": the arrows are spatial, so Left widens a pane on the right. The value is the primary pane's size. "If the primary pane has a visible label, it is referenced by aria-labelledby." `aria-controls` names the primary pane; Enter collapses and restores it; Home and End give it its smallest and largest size. | 2026-10-18 | P |
| W3C, WAI-ARIA editor's draft, the `separator` role | Read as text from `raw.githubusercontent.com/w3c/aria/main/index.html`. A focusable separator MUST have `aria-valuenow`, SHOULD give `aria-valuemin` and `aria-valuemax` when they are not 0 and 100, and supports `aria-valuetext`. Its orientation is horizontal unless said, so a vertical edge says so. "In applications where there is more than one focusable separator, authors SHOULD provide an accessible name for each one." | 2026-10-18 | P |
| W3C, WCAG 2.2, 2.5.7 Dragging Movements | The normative text (`raw.githubusercontent.com/w3c/wcag/main/guidelines/sc/22/dragging-movements.html`) and Understanding (`.../understanding/22/dragging-movements.html`). The alternative "does not have to be the same component, so long as the functionality is equivalent". The examples include a map moved by up, down, left and right buttons: a stepped alternative. Keyboard access is evaluated separately. | 2026-10-18 | P |
| W3C, WCAG 2.2, 2.5.8 Target Size (Minimum) | The normative text (`.../guidelines/sc/22/target-size-minimum.html`): 24 by 24 CSS px, except where "the function can be achieved through a different control on the same page that meets this criterion". | 2026-10-18 | P |
| VS Code (MIT), `src/vs/workbench/browser/actions/layoutActions.ts` and `src/vs/base/browser/ui/sash/sash.ts`, main branch | Practice. The focused part's size is stepped 60 CSS px per command (`workbench.action.increaseViewSize` and its kin), with no control on screen. The sash takes the mouse and its own touch gestures; it has no role, no focus and no keys. | 2026-10-18 | P (code read as text) |
| react-resizable-panels 4.14.5 (MIT, Brian Vaughn), its package from `registry.npmjs.org`, read as text from its source map, never run | Practice. The separator has role `separator`, `tabIndex` 0, `aria-controls`, `aria-valuenow`, `-valuemin`, `-valuemax`, `aria-orientation`, and `touch-action: none`. The arrows move it spatially (ArrowLeft always moves it left); Home and End give the primary pane its smallest and largest size; Enter collapses and restores; F6 moves between separators. Its `aria-valuemax` is the primary pane's largest size given its neighbours' limits, as "within what the screen allows" is here. Pointer events for every pointer. | 2026-10-18 | P (code read as text) |

GitHub's API is not open to this session beyond the owner's repository (the library's file tree was
refused); `raw.githubusercontent.com` and `registry.npmjs.org` answered. Nothing at level U reached
the code.

## What was decided, and why

- **The steps** are 240, 320, 400, 480 and 560: the panel's narrowest and widest, with V166b's grid
  between. A press goes to the next step up within what the screen allows, to the screen's widest
  when no step fits, and from the widest back to 240: V166b's rule. Properties' default, 280, is not
  a step; the edge's double click gives it back. Steps starting at 280 were set aside, since no
  press would then reach the narrowest the panel is built for.
- **Within what the screen allows:** Properties' widest leaves the drawing 320 px beside the left
  panel at its narrowest (the window less 54, 242 and 320). V166b made the left panel give way to
  Properties, never below 242, so this one bound keeps the drawing's 320 px however the left panel
  is set, open or shut, and the two panels' limits do not depend on each other in a circle. The
  drag, End, the button and a width applied on a narrower screen all read it; a width kept on a
  wider screen stays kept.
- **The edge, by the pattern:** named by the header's own "Properties" (`aria-labelledby`, the
  pattern's choice where the pane has a visible label; the left edge's "Panel width" is a different
  name, as the spec asks of two separators). Left widens, since the arrows are spatial in the pattern
  and in the library; 16 px, 64 with Shift, as V166b's. Enter minimises Properties, its collapse,
  and the focus goes to the minimise button, whose Enter restores it, as V166b did for the left panel.
- **Any pointer:** pointer events with `touch-action: none`, as the left edge and the library have
  them; a 12 px edge inside the panel for a finger, with a line it can see without a hover. The left
  panel gives way during the drag, its easing turned off as V166b's own drag turns it off.
- **Docked by the stylesheet's own query:** the code tests `(max-width:1024px),(max-height:500px)`,
  the query of the one rule that hides the edge and the button. That ends V147's disagreement.
- **The audit** reaches Properties' chrome (its header, edge and grab bar), not its body, and counts
  a focusable separator as a control. It claims both edges, the button, and V147's minimise and grab
  bar (both driven by V147's suite).

## Still open

- The left edge's name, "Panel width", is not the name of its pane, as the pattern asks: the pane's
  visible label changes with the rail's tab.
- `aria-valuetext` ("280 pixels") on both edges: allowed by the spec, not added, since no screen
  reader was tested here.
- V166b's: a dropdown focused in Analyze waits for its row's redraw.
