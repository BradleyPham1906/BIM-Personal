# V199: the interface pass

Review and build, 2026-11-13. The owner's fifth of five after V194: make the interface professional. Levels as in
`research-protocol.md`: P primary (seen here), U a pointer only.

## 1. Method

`tests/e2e/bim_ui_walkthrough.mjs` opens the app in Edge 157 (headless) at three sizes, desktop 1500 x 950, tablet
1024 x 768 (touch) and phone 390 x 844 (touch), and screenshots eleven states each: start, empty, a small model, a
selection, the command palette, Layers, Project properties, plan, the Analyze workspace, a sheet, the rendered view.
33 screenshots, no console errors. Each finding below is seen in those pictures (P); where a size was measured in
the page, the number is given. The screenshots are not committed (the repository is public).

## 2. Findings

| # | Finding | Where | Owner's choice |
|---|---|---|---|
| F1 | The status bar squeezed its own parts: the Model tab read "M...", "Not saved to a file" was cut; on the tablet its right end ("Technical style") was cut off | all sizes | fix |
| F2 | The tool bar at the bottom was cut at both ends on the tablet (Wall's label, All tools, Search) | tablet | fix |
| F3 | The Analyze side panel was cut by 16 px on its right ("0 finding", "Not run"): when the panel scrolls, its scroll bar takes 16 px while its content and header were held at the panel's full 242 px; the scroll bar was the browser's white one | desktop, tablet | fix |
| F4 | Every notice appeared at the bottom, over the tool bar and the status bar; on the phone it hid SNAP | all sizes | fix |
| F5 | Project Browser buttons were abbreviations: +Sht, +Lvl, +Bldg, +Fam, Imp | all sizes | fix |
| F6 | The Layers panel's "List by" was the browser's white drop-down in the dark theme | all sizes | fix |
| F7 | Usages: each line's figures wrapped beside its Edit button ("3.1" / "m") | desktop | fix |
| F8 | Properties shows the version as "V172, 2026-11-01" (the app is at V198); the same string goes into saved files | all sizes | not now (the owner) |

## 3. As built (V199)

- F1: the hint gives way first; the layout tabs, the file state and the controls keep their size; a bar still too
  narrow scrolls sideways instead of cutting. At 1280 px and under, the cursor coordinates, the words PAN and ORBIT
  and the word "Level" go (their icons, the level box and their titles stay). Tablet: 728 of 728 px used, nothing cut.
- F2: the tool bar's row scrolls sideways when narrower than its tools; nothing shrinks or is cut.
- F3: a docked left panel that scrolls keeps its content and header inside the scroll bar
  (`min-width: panel width - 16px`), with a thin dark scroll bar (light in the light theme). Measured: content width
  231 of 231 px.
- F4: notices appear at the top of the drawing area, under its header and below the "open in another tab" banner
  (108 px from the top; 112 px on a phone), no wider than 560 px.
- F5: + View, + Sheet, + Level, + Building, + Family, Import.
- F6: the drop-down takes the panel fields' dark style.
- F7: a usage's figures sit under its name, its Edit button alone on the right.

## 4. Checks

`npm run check`, `npm test` 250 of 250; the walkthrough re-run after the fixes, and the tablet and desktop pictures
re-taken (no console errors).

## 5. Open

- F8, the version string.
- A selected object's gizmo in plan is large for a small object (a 0.4 m column).
- The empty "2D Views" and "Sections" groups show "none yet" in the Project Browser.
- The tool bar and status bar scroll without a visible cue on a tablet.
