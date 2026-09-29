# Research: finding a command, and learning its keys (V128)

The owner: "lets make command UI easy to use. shortcuts searchable and stuff. i know we can do ctrl
+ k and it have a drop down for quick search. but as this app become more sophisticate, it is hard.
pls research on how and execute."

Autodesk, McNeel, Figma, Linear and blender.org could not be reached from the build environment,
so those points come from search summaries. The VS Code, Blender, MDN and W3C points were checked
against their source on GitHub and are marked [src].

## What the app had

Two searches, and each missed what the other had:
- **Ctrl+K** listed the ~90 typed commands (LINE, WALL, TRIM) but none of the ribbon's tools: Box,
  Union, Pad, the sketch constraints, the exports.
- **The dock's magnifier** listed the ribbon's tools but none of the typed commands.

There were other gaps:
- Neither search showed a keyboard shortcut, and neither forgave a typo.
- A command could only be typed after Ctrl+K. AutoCAD and Rhino take it straight from the
  drawing.
- The shortcut sheet (SHORTCUTS) could not be searched.

## What the mature tools do

1. **AutoCAD** (Input Search Options):
   - AutoComplete, and mid-string search.
   - AutoCorrect, which learns misspellings.
   - Synonyms: ROUND offers FILLET.
   - Sorting by how often each command is used, and a search of content (hatch patterns, blocks).
   - Tab cycles through the matches, and Enter or Space repeats the last command.
   - Keystrokes on the canvas go to the command line.
   - Aliases live in acad.pgp and appear in the suggestion list.
2. **Rhino**: autocomplete matches prefixes first, then fuzzy "did you mean" matches ranked by
   closeness. Enter repeats. There is a command history, aliases, and prompt options you can click.
3. **Revit**:
   - Keyboard Shortcuts dialog: search matching any part of a word, a filter by UI area, a column
     for where each command lives, and several keys per command.
   - Two-letter shortcuts with no modifier (WA).
   - Keytips on Alt.
4. **VS Code** [src]:
   - Contiguous or word-start matches first, and "similar commands" only when nothing matched.
   - A "recently used" group at the top, then the rest.
   - The keybinding on every row, and in the row's accessible name.
   - `?` lists the palette's prefixes.
   - The Keyboard Shortcuts editor can be searched by the key itself.
5. **Blender F3** [src]:
   - Every item shows its menu path (Mesh ▸ Delete ▸ Vertices) and its shortcut.
   - Matching by word prefixes, by initials, and with typos allowed.
   - Recent items boosted only when the query is empty or one character.
   - Disabled items shown greyed.
6. **Figma, Linear:**
   - Figma's Ctrl+K shows each action's shortcut, and typing a shortcut finds its action.
   - Linear's `?` opens a searchable help sheet of its shortcuts.
7. **Accessibility** [src: MDN, W3C combobox pattern]:
   - The input is a `role=combobox` with `aria-controls` pointing at a `role=listbox`, and the
     focus stays in the input.
   - `aria-activedescendant` names the active `role=option`, which is `aria-selected`.

## What V128 takes

- **One catalogue.** It holds every typed command that runs and every implemented ribbon tool.
  - A ribbon button that is a typed command becomes that command's row, with its ribbon place
    added (VS Code, Blender).
  - Each row's keys come from the shortcut sheet's own table, so the two cannot disagree.
  - Ribbon-only tools get names to type: the booleans are UNION, SUBTRACT and INTERSECT; the
    sketch constraints use AutoCAD's GC/DC names; the exports are EXPORTPDF and the like.
- **Layered matching** (AutoCAD, Rhino, VS Code, Blender), in this order:
  1. an exact name or alias;
  2. a keyboard chord;
  3. a name or alias prefix;
  4. letters anywhere in the name;
  5. a word of the description or of the command's synonyms (AutoCAD's ROUND → FILLET);
  6. the letters in order from the first (PLNE → PLINE);
  7. the ribbon place;
  8. a one-letter typo, only when nothing matched as typed, under "Did you mean" (VS Code).

  Every word typed must match. The letters that matched are marked.
- **Ordering.** Match quality comes first, then how often the command is used (AutoCAD), then
  catalogue order. The empty list starts with the recently used (Blender, VS Code).
- **Rows.** Each row shows the name, what it does, its ribbon place, its alias and its keys. It
  teaches the shortcut (VS Code, Linear) and where the button is (Blender). A command that cannot
  run where you are says why.
- **Shortcuts in the search.** `?` searches the keyboard shortcuts by what they do or by the key,
  and Ctrl or Cmd count as the same key (Linear, Figma, VS Code). A shortcut that runs a command
  runs it on Enter.
- **Type-anywhere** (AutoCAD, Rhino). A letter typed on the drawing opens the search with that
  letter in it, but only when nothing else is listening: not a tool taking points, a field, a
  dialog, a held face, a sheet, a slideshow or the Start page. Tab cycles, and Enter repeats a
  ribbon tool run from the search, as it repeats a typed command.
- **One search.** The dock's magnifier opens it, and every ribbon tooltip names the command to
  type (Revit, AutoCAD).
- **The shortcut sheet can be searched** (Revit, VS Code). Escape clears the search, then closes
  the sheet.
- **The ARIA combobox pattern.**

## Not taken, yet

- Rebinding keys, and user aliases (Revit KS, acad.pgp, VS Code).
- Revit's two-letter shortcuts without Enter.
- AutoCAD's Find, which shows a command's place on the ribbon.
- Pinned favourites.
- Command history on Up and Down.
- Clickable prompt options.
- Searching project content (levels, views, families) with an `@` prefix.

## Sources

- [AutoCAD: Input Search Options](https://help.autodesk.com/cloudhelp/2019/ENU/AutoCAD-Core/files/GUID-3179393F-958F-42EA-8A92-E9975A1D160B.htm)
- [AutoCAD: the command window](https://www.autodesk.com/blogs/autocad/autocad-command-window-exploring-features-benefits-autocad/)
- [AutoCAD synonym list](https://ukcommunity.arkance.world/hc/en-us/articles/21550864332690-AutoCAD-Command-Line-8-Synonym-List)
- [AutoCAD: acad.pgp aliases](https://cadpedia.ca/acad-pgp-autocad/)
- [Rhino 8: the Rhino window](https://docs.mcneel.com/rhino/8/help/en-us/user_interface/rhino_window.htm)
- [Rhino: command-line autocomplete](https://discourse.mcneel.com/t/command-line-autocomplete-command-list/123573)
- [Revit 2025: Keyboard Shortcuts](https://help.autodesk.com/view/RVT/2025/ENU/?guid=GUID-81EF5A21-F562-43A2-A816-109915C82B01)
- [VS Code: commandsQuickAccess.ts](https://github.com/microsoft/vscode/blob/main/src/vs/platform/quickinput/browser/commandsQuickAccess.ts)
- [VS Code: fuzzyScorer.ts](https://github.com/microsoft/vscode/blob/main/src/vs/base/common/fuzzyScorer.ts)
- [VS Code: keybindingsEditor.ts](https://github.com/microsoft/vscode/blob/main/src/vs/workbench/contrib/preferences/browser/keybindingsEditor.ts)
- [Blender: operator search menu](https://github.com/blender/blender/blob/main/source/blender/editors/interface/templates/interface_template_search_menu.cc)
- [Blender: string search](https://github.com/blender/blender/blob/main/source/blender/blenlib/intern/string_search.cc)
- [Fusion 360: the S key](https://www.autodesk.com/products/fusion-360/blog/quick-tip-the-s-key/)
- [Figma: the actions menu](https://help.figma.com/hc/en-us/articles/23570416033943-Use-the-actions-menu-in-Figma-Design)
- [Linear: keyboard shortcuts help](https://linear.app/changelog/2021-03-25-keyboard-shortcuts-help)
- [MDN: combobox role](https://github.com/mdn/content/blob/main/files/en-us/web/accessibility/aria/reference/roles/combobox_role/index.md)
- [W3C: combobox pattern](https://github.com/w3c/aria-practices/blob/main/content/patterns/combobox/combobox-pattern.html)
