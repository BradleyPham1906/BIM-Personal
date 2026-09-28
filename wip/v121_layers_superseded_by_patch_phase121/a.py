"""patch_phase121a.py -- V121: one test per question, asked of a layer and everything above it.

The owner's first panel is Layers: "i should be able to manipulate a table like how autocad do like
linetype, color, hide/show, layer, sub layer, transparency". Before a table can switch anything, the
drawing has to agree on what a switched layer means. It did not. 28 places read a layer's `visible`
and `locked` flags for themselves, and three of them got it wrong:

  - bimAnnotDrawable treated a LOCKED layer as a hidden one. It decides whether a room tag is drawn,
    exported and counted, so locking a layer made its room tags disappear from the canvas, the SVG,
    the DXF and every sheet -- and the room's own label came back, since its room no longer counted
    as tagged. Locked means displayed and not modified; it is the picking that stops.
  - bimSnapCandidates asked nothing: a line or wall on a hidden layer went on offering its corners
    as snap points, so new geometry pulled to things that were not on screen. The construction
    lines beside it did ask.
  - no sub-layer could exist, because nothing looked above a layer.

AutoCAD's definitions (Layer Properties Manager, AutoCAD 2024 help) are the ones used:
  On      off: not displayed, not plotted, still in the drawing's extents.
  Freeze  frozen: not displayed, not plotted, not regenerated -- and not in the extents.
  Lock    locked: displayed, snapped to, plotted; not selected or modified.
A sub-layer is off, frozen or locked when any layer above it is (Rayon nests layers; AutoCAD
groups them).

Two questions, each asked in one place: bimLayerShown(o) -- is it drawn, snapped to, traced and
measured -- and bimLayerPickable(o) -- can the user select it. All 28 sites ask one of them. Layers
are read tolerantly (a layer without `frozen` is thawed), so an older acad3dV1 loads unchanged."""
NAME = 'patch_phase121a.py'
BASE = 'CHAIN'
import re
