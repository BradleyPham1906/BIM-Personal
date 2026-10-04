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
  - **Layers:** the layer tree, with the objects on each layer; below it, **Analysis** (the
    results you keep as layers) and **Data** (the site's data layers). See
    [Analysis](analysis.html).
  - **Presentation:** the pages of the set, to present and print.
  - **Project Browser:** views, sheets, schedules, families.
  - **Assets:** a library of models, blocks and templates. Drag one onto the drawing.
  - **Analyze:** every analysis, in four groups, with a search. See [Analysis](analysis.html).
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
- **On a phone or a tablet.** The drawing gets the screen:
  - **A phone held upright:** the rail is a bar of tabs along the bottom (Layers, Present,
    Browser, Assets, Analyze). A tab opens its panel as a drawer over the drawing; tap the same
    tab, tap beside the drawer or press **Esc** to close it. **More** holds the rail's tools: zoom,
    appearance, snaps, units, save image, shortcuts.
  - **A tablet held upright, or a phone on its side:** the rail stays down the left, and the panel
    opens as the same drawer, from a rail tab or the panel button.
  - **A tablet on its side, or a computer:** the panel sits beside the drawing, as before.
  - The panel starts closed on a phone or an upright tablet, and the layout follows the screen as
    it turns.
  - **The tool palette** takes the dock's place: Select, Pan, Line, Rectangle, Circle, Wall,
    Door, Window, Dimension, Delete, and **More** for every other tool and the search. The tool in
    use is filled in blue; Select puts it away. Drag the palette by its grip: let go near the left
    or right edge and it stands upright there, anywhere else it lies flat. The chevron folds it to
    one round button showing the tool in use; tap the button to open it again, or drag it. The
    palette stays where you leave it.
  - **Props** opens Properties. On a phone it is a sheet from the bottom: tap its grab bar to raise
    it and lower it. On a tablet it is a drawer from the right. On either, the arrow beside the
    word Properties closes it.
  - On a touch screen every field and button is sized for a finger, and every field's text is
    16 px, so a phone does not zoom in when you tap one. When the keyboard comes up, Properties and
    the drawer sit on top of it, with the field you tapped in view. Two fingers pinch to zoom and
    drag to pan.
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

## Large models

The 3D view draws the model in a few large batches instead of one element at a time. Each
element's position, colour, selection and transparency is kept in one table on the graphics card.
Turning or zooming the view sends nothing new to the card, and moving or selecting an element
updates only that element's entry. A model of 5,000 elements is drawn in one or two calls rather
than thousands, so large imports and city context stay smooth to orbit.

A device whose graphics cannot read that table (some very old phones) draws element by element as
before. The picture is the same either way.
