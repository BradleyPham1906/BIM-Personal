"""patch_phase121d.py -- V121: the Layers panel, with the model inside it.

The owner: "layers (this should combine with model)". The rail gets a Layers tab, first, as Rayon's
rail has it. The panel is the layer tree -- sub-layers under their parents -- and each layer opens to
the objects on it, so the model tree is what the layers contain rather than a list of its own:

  - per layer: open or closed, its color (a real color field), its name (double-click to rename in
    place; Enter keeps it, Escape does not), how many objects are on it, and four switches: current,
    On, Freeze, Lock -- each through V121b's rules, so the panel refuses what AutoCAD refuses;
  - per object: its name and type, a click that selects it (and says why not when its layer is off,
    frozen or locked), and its Pin;
  - drag an object onto a layer to move it there; drag a layer onto another to make it a sub-layer,
    or onto the empty list to bring it back to the top;
  - New layer (named Layer 1, 2 ... and taking the selected layer's appearance, as AutoCAD's does),
    New sub-layer, Standard (the AIA / NCS dialog that was the Project Browser's +Lyr), Make current,
    Delete; and a search over layers and objects.

What it replaces goes with it, so nothing is left that reads as a control and does less:
  - the Project Browser's Layers group and its Model group. Both drew their lock toggles as emoji
    (the build contract forbids them), the Model group's click selected objects on locked layers,
    and the browser's search box filtered nothing else -- it now filters every leaf of the browser;
  - the browser's +Lyr button, which the panel's Standard button is;
  - the hidden #a3d-layerrows list with its handlers: never shown, and only V82's suite clicked it.

The Properties panel's Layer fields list the layers as the tree, sub-layers indented."""
NAME = 'patch_phase121d.py'
BASE = 'CHAIN'
import re
