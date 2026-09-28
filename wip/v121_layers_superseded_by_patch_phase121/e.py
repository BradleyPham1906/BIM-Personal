"""patch_phase121e.py -- V121: every object is on a layer.

Building the Layers panel showed a wall listed under the Model layer that had been made on A-WALL.
Nine of the ways an object is made never gave it a layer -- walls, columns, floors, pads, pockets,
property lines, imported sketches and faces, copied rooms -- and bimLayerOf reads a missing layer as
the CURRENT one. So each of those objects was on whichever layer happened to be current: make another
layer current and every wall went with it; make an off layer current and every wall disappeared;
lock the current layer and none of them could be picked. The same held for every object in a project
saved before this phase.

Rather than a tenth fix at each of nine places (and the next place someone writes), the layer is
given where every change already passes: saveSoon adopts, onto the current layer, any object without
one -- the layer it was made on, since every maker calls saveSoon at once -- and an object whose layer
no longer exists onto the first layer, which is what bimLayerOf already read it as. A stored project
is adopted as it loads, onto the layer that was current when it was saved: the one its layerless
objects were being drawn as, so nothing changes on screen."""
NAME = 'patch_phase121e.py'
BASE = 'CHAIN'
import re
