"""patch_phase121b.py -- V121: changing a layer, by AutoCAD's rules, through one set of functions.

A layer was changed by six small functions, each doing its part and none of them checking anything:
two layers could share a name, the current layer could be deleted (its objects moved to whichever
layer happened to be first), and turning a layer off left its objects selected -- so a Delete or a
nudge acted on objects nobody could see. The Properties panel's Layer field wrote the object's
layer directly.

Now every change goes through bimLayerSet, bimLayerNew, bimLayerDelete, bimLayerMakeCurrent or
bimObjSetLayer. Each is one undo step, and each refuses what AutoCAD refuses and says why:

  - a name must be new (AutoCAD's names are not case-sensitive) and free of < > / \\ " : ; ? * | , = `;
  - the current layer cannot be frozen, deleted, or moved under a frozen layer, and a frozen layer
    cannot be made current;
  - the last layer cannot be deleted; a deleted layer's objects go to the layer above it (or the
    current layer), and its sub-layers move up;
  - a layer cannot be put under itself or under one of its own sub-layers.

A new layer takes its appearance -- color, linetype, lineweight, transparency, plot -- from the
layer it is made from, as AutoCAD's New Layer takes the selected layer's. Whatever a change makes
unpickable (off, frozen, locked) leaves the selection.

The linetypes are AutoCAD's acad.lin set, kept as their definitions so the drawing, the plots and
the DXF derive their patterns from one table; the lineweights are AutoCAD's list, in millimetres."""
NAME = 'patch_phase121b.py'
BASE = 'CHAIN'
import re
