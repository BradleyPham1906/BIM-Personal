# Research: every tool in one panel, and a dock of the few used most (V130)

The owner, on the V129 dock: "this tool bar is very crowded. I say we combine it in the shortcut
table and use search, filter sorting. group the features and stuff here. and in the main screen
only show the keys one (those that most likely use the most)".

This builds on the V128 and V129 research (`research-command-ui.md`, `research-shortcuts-ui.md`).
The points come from those sources and from general HCI knowledge; no new page was fetched for this
phase.

## What the mature tools do

- **Fusion** keeps a short toolbar of the commonest tools. Every other tool is in its menus and the
  S-key toolbox, and any tool can be pinned to the toolbar.
- **Figma's Actions** (Ctrl+K) is the place for every action. Its toolbar holds only the few drawing
  tools.
- **VS Code's** activity bar and command palette work the same way: the full list is searchable,
  and the visible surface is small and set by the user.
- **Revit's** Quick Access Toolbar is a strip the user adds commands to, beside a full ribbon.
- **Giraffe** keeps few drawing tools and does the rest in Properties (`research-giraffe.md`).

## Why the pins are fixed, not automatic

The owner asked for the tools "most likely use the most". The dock could re-order itself by use,
but adaptive menus that move items have long been found to slow people down. A tool that is not
where it was yesterday is a tool to hunt for (Sears and Shneiderman's split menus; Findlater and
McGrenere's comparison of adaptive and adaptable menus). So V130 makes the dock *adaptable*, not
*adaptive*:

- It starts with the tools each discipline uses most.
- The user changes it with a pin.
- Use is counted, so **Most used** in the panel shows the user what they actually reach for, ready
  to pin. Nothing moves on its own.

## What V130 takes

- **The panel is Tools and shortcuts.**
  - It lists every ribbon tool, grouped by its tab, then every key, grouped as before.
  - **Search** covers names, what a tool does, the command, its aliases and its keys.
  - **Filters:** All, Tools and Keys.
  - **Sort:** by group, by name, or by most used.
  - **On the dock** lists the pinned tools.
  - A row runs its tool and puts the panel away.
  - A tool not built yet is greyed and cannot be run or pinned.
- **The dock is one row:** the discipline, the pinned tools (twelve at most, kept per discipline
  and per browser), All tools (`?`), and the search (Ctrl K).

## Not taken, yet

- Dragging to reorder the pins.
- Sharing a pin set between people, or across devices.
- A second-stage, illustrated tooltip.
