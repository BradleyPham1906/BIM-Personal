---
title: Getting started
order: 1
---
# Getting started

## The window

- **Tabs along the top.** Start, then one tab per open project. **+** starts a new project, and
  each project keeps its own undo history.
- **The ribbon.** Tools grouped by discipline:
  - Architecture, Structure, Massing & Site, Drafting;
  - Modify, View, Insert, Manage.
- **The dock,** at the bottom of the drawing. The tools pinned for the current discipline, with
  **All tools** and the search beside them.
- **The left rail,** a column of panels:
  - **Layers:** the layer tree, with the objects on each layer.
  - **Presentation:** the pages of the set, to present and print.
  - **Project Browser:** views, sheets, schedules, families.
  - **Assets:** a library of models, blocks and templates. Drag one onto the drawing.
  - **Analyze:** every analysis, what it shows now, and its settings. See [Analysis](analysis.html).
- **Properties,** on the right. With an object selected, its properties. With nothing selected,
  four tabs:
  - **Project:** project, client and site name, and the statistics, including the app's version.
  - **Site:** Location (latitude, longitude, true north, the sun's date and time), Map, Site
    Context, Data Layers.
  - **View:** active level and layer, colour by, appearance.
  - **Analysis:** floor loads, the frame's analysis, areas by usage, the usages.
  - **Project** also holds the **History**: see [Sheets and files](sheets-files.html).
- **Sizing Properties.** Drag the panel's left edge to widen it (240 to 560 px); double-click the
  edge to put it back. The arrow beside the word Properties minimises the panel to a strip. Both
  are remembered.
- **On a phone or a tablet.** **Props** opens Properties. On a phone it is a sheet from the bottom:
  tap its grab bar to raise it and lower it. On a tablet it is a drawer from the right. On either,
  the arrow beside the word Properties closes it, and on a touch screen every field and button is
  sized for a finger.
- **The status bar.** Level, snaps, ortho, grid; pan, orbit, 2D and 3D.

## Finding a command

Every command and every ribbon tool is in one search:
- Press **Ctrl K**, or just start typing on the drawing, as on AutoCAD's command line.
- Type a name (`WALL`), an alias (`WA`), or what you want ("door", "flood zone").
- **Enter** runs the highlighted command. **F1** opens its help page.
- Type **?** to search the keyboard shortcuts instead.

`SHORTCUTS` opens the tools and shortcuts panel: every tool by group, every key, and a pin on each
tool to put it on the dock.

## Saving

- Projects are saved in the browser as you work.
- `SAVE` writes a project file (`.json`) to keep, send or put under version control; `OPEN`
  reads one back.
- `NEW` starts an empty project.

## Undo

**Ctrl Z** and **Ctrl Y** (`UNDO`, `REDO`). Each action is one step, including fetches from
the network: getting the site context is one step, and undoing it removes everything it
brought.
