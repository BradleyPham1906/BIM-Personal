---
title: Drawing
order: 2
---
# Drawing

The drafting tools work in plan, on the active level.

## Draw

| To draw | Command |
|---|---|
| a line | `LINE` |
| a polyline (with arcs) | `PLINE` |
| a rectangle | `RECTANG` |
| an arc | `ARC` |
| a circle | `CIRCLE` |
| a regular polygon | `POLYGON` |
| a point | `POINT` |
| construction lines and rays | `XLINE`, `RAY` |
| points along a curve | `DIVIDE`, `MEASURE` |
| a closed boundary from what surrounds a point | `BOUNDARY` |
| a hatch | `HATCH` (edit with `HATCHEDIT`) |

**Exact input.** While a tool is running, you can type:
- a length or an angle;
- a coordinate;
- **C** to close.

`OSNAP` turns object snaps on and off, `ORTHO` locks to right angles, and `GRID` shows the grid.

## Constraints

Geometric constraints keep relations as you edit:
- `GCHORIZONTAL`, `GCVERTICAL`, `GCPARALLEL`, `GCPERPENDICULAR`;
- `GCCOINCIDENT`, `GCEQUAL`, `GCMIDPOINT`;
- `GCSYMMETRICLINE`, `GCSYMMETRICPOINT`, `GCPOINTONLINE`.

Dimensional constraints fix a size: `DCDISTANCE`, `DCANGLE`.

## Modify

- **Moving and copying:** drag a selection, or use the gizmo, to move it; `COPY`, `ROTATE`, `SCALE`,
  `MIRROR`, `ALIGN`.
- **Arrays:** `ARRAYRECT`, `ARRAYPOLAR`.
- **Editing lines:** `OFFSET`, `TRIM`, `EXTEND`, `BREAK`. For walls, `LENGTHEN` changes a length at one end and `BREAKATPOINT` splits a wall at a point.
- **Corners:** `FILLET`, `CHAMFER`.
- **Deleting:** `ERASE`.
- **The gizmo** (`GIZMO`): moves, rotates and scales a selection in place.
- **Faces:** `PRESSPULL`, or drag a face, to push or pull it.

`SELECTALL` selects everything. A window drag selects what is inside it, and a crossing drag (right
to left) what it touches.

## Dimensions and text

- **Dimensions:** `DIMLINEAR`, `DIMANGULAR`, `DIMRADIUS`, `DIMDIAMETER`.
- **Text and leaders:** `TEXT`, `MTEXT`, `LEADER`.

Dimensions and hatches follow what they are attached to.

## Layers

`LAYER` opens the Layers panel. There you can:
- make sub-layers;
- turn layers off;
- freeze or lock them;
- set colour, linetype and lineweight.

The layer tree is also the Layers tab on the left rail.
