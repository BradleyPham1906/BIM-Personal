---
title: User Guide
order: 0
---
# User guide

A BIM and CAD app that runs in a browser, in one file, with no account and no install. It draws
like AutoCAD, models buildings like Revit, and brings the site in from free public data:
- the map and the terrain;
- the buildings around the site, at LOD1 and LOD2;
- parcels, zoning and flood zones;
- your own survey, checked every time you load it.

Open it at **https://bradleypham1906.github.io/BIM-Personal/**, or open `canvas_v10.html` from
the repository on your own computer. It works offline: it only goes to the network when you ask it
to (a map, an address, the site's context, a data layer).

## Where to start

| If you want to | Read |
|---|---|
| find your way around the window | [Getting started](getting-started.html) |
| draw lines, shapes, dimensions and text | [Drawing](drawing.html) |
| model walls, floors, roofs, rooms and structure | [Building model](bim.html) |
| put the project on the map, with what is around it | [Site and context](site.html) |
| bring in a survey, and trust it | [Survey and terrain](survey-terrain.html) |
| model neighbouring buildings from LOD1 to LOD2, and exchange CityJSON | [Buildings and LOD](buildings-lod.html) |
| run the analyses | [Analysis](analysis.html) |
| make sheets, and import and export files | [Sheets and files](sheets-files.html) |
| look up one command | [Command reference](commands.html) |
| see what changed | [Release notes](changelog.html), [Versions](versions.html) |

## Help inside the app

- **Ctrl K**, or start typing on the drawing, opens the command search. **F1** on a highlighted
  command opens its page in the [command reference](commands.html).
- `DOCS` opens this guide; `RELEASENOTES` opens the notes for the version you are running.
- **?** opens the keyboard shortcuts.
- With nothing selected, **Properties > Project > Statistics** says which version you have.
