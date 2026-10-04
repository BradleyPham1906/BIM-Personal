---
title: Building model
order: 3
---
# Building model

## Levels and grids

- `LEVEL` adds a level.
- `GRIDLINE` draws a grid line, with its bubble.

The active level is in the status bar and in **Properties > View**.

## Walls, openings, floors and roofs

| To place | Command |
|---|---|
| walls (A for arc segments) | `WALL` (`JOINWALLS` joins two at a corner, `JOIN` two in line) |
| doors and windows, in a wall | `DOOR`, `WINDOW` |
| a floor or a ceiling | `FLOOR`, `CEILING` |
| a roof: shed, hipped or gabled, over any footprint | `ROOF` |
| a stair | `STAIR` |
| a column | `COLUMN` |
| a model from the library | `COMPONENT` (or drag it from Assets) |

**Types.** Walls, floors and roofs carry a type with its layers and thickness. **Edit Type** in
Properties changes the type, and with it every instance.

## Rooms and areas

- **Rooms:**
  - `ROOM` places a room in the space you click.
  - `ROOMTAG` and `TAGALLROOMS` tag them.
  - `ROOMCOLOR` fills rooms by department or occupancy.
- **Area plans:** `AREAPLAN` shows or hides the gross area inside the exterior walls on a level.
- **Usages:** `USAGE` gives rooms, floors or masses a use (residential, office...). `USAGES`
  edits the library of uses, each with its colour, area ratios and formulas. **Analysis > Areas
  by Usage** totals them live.

## Structure

- **Members:** `COLUMN` and `BEAM`, with sections from the steel and concrete section library.
- **Foundations:** `FOOTING`, `WALLFOUNDATION`, `FOUNDATIONSLAB`. `FOOTINGSALL` puts a footing
  under every column.
- **Loads:**
  - Floor loads are set per level (**Properties > Analysis**).
  - `TRIBAREA` shows the tributary areas.
  - `LOAD` adds a load to a member.
  - `SUPPORT` sets a column's support.
- **The frame:** `ANALYZE` solves it and shows forces and deflection over the model.
  `ANALYZEOFF` hides them.

## Massing

- **Conceptual solids:** `BOX`, `CYLINDER`, `CONE`, `SPHERE`, `TORUS`, `WEDGE`, `PRISM`, `TUBE`,
  `ELLIPSOID`.
- **From a sketch:** `PAD` and `POCKET` extrude and cut.
- **Combining:** `UNION`, `SUBTRACT`, `INTERSECT`.
- Masses take usages, so the massing gives its areas as you shape it.

## Checking the model

- `CHECKMODEL` lists problems.
- `CLASSIFY` manages the classification systems objects are classified by.
