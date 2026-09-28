"""patch_phase121c.py -- V121: what is on a layer looks like its layer.

The owner asked for color, linetype and transparency in the layer table. They are real only if they
change the drawing, so the rule is set here, from AutoCAD's By Layer and Revit's materials:

  - the linework drawn with LINE, PLINE, ARC, CIRCLE, RECTANG, POLYGON and POINT takes its layer's
    color, linetype and lineweight;
  - everything on a layer takes its transparency: linework, annotation, hatches, rooms, construction
    lines, property lines, terrain, notes and solids, in the GL renderer and the CPU one;
  - building elements keep their materials, and annotation and construction lines their own styles.

Found on the way: drawSketches never asked about layers at all. Turning a layer off hid its walls,
rooms, dimensions and notes, and left every line, polyline, arc and circle on it drawn -- on screen
and on every sheet, since sheets are painted by the same function.

The linetype patterns are derived from the acad.lin definitions V121b keeps (24 px to the unit on
screen: Dashed is 12 on, 6 off). A lineweight is drawn at 6.4 px to the millimetre, so AutoCAD's
0.25 mm is the 1.6 px every line was drawn at before, and Default stays exactly that. Transparent
solids are drawn after the opaque ones, blended, without writing depth, so what is behind shows."""
NAME = 'patch_phase121c.py'
BASE = 'CHAIN'
import re
