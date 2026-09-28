# Direct manipulation: research and the V123 design

Written for V123. The owner's words: "geometry manipulation for objects, shapes and assets ... quite
limited for my push, pull, rotate when I click on these kinds of objects, even though we have the
gizmo ... look into Autodesk but also Rhinoceros by McNeel on how they do it ... this would help set
the base" -- the base the Assets library (V124) is placed and edited on.

## 1. What the reference tools do

### Rhino (McNeel) -- the Gumball
- Arrows move along an axis, arcs rotate, small boxes scale, and a square between two arrows moves
  in that plane.
- **Click a handle without dragging and type a value**: an arrow asks for a distance, an arc for an
  angle, a scale handle for a factor. This is the single most-used precision feature.
- Ctrl while dragging extrudes; Alt toggles copy; Shift scales in more than one direction.
- An extrude handle (the dot on the Z arrow) pulls a closed curve or surface into a solid.
- Align to CPlane, Object, World or View; GumballRelocate moves its origin.
- Snappy dragging uses object snaps while dragging; smooth dragging ignores them.
- Sub-object selection (Ctrl+Shift+click) picks a single face, edge or point of a solid; the gumball
  then works on that face, and moving it stretches the faces around it.

### AutoCAD -- PRESSPULL, gizmos, grips
- PRESSPULL: click inside a bounded area or on a face of a solid, then move the cursor or type a
  distance. A closed area becomes a solid; a solid's face is offset and the solid follows.
- Ctrl+click on a face changes how the adjacent faces follow it; Shift+click picks several; the
  Multiple option repeats.
- The 3D move, rotate and scale gizmos highlight the axis under the cursor; Ctrl+click picks
  sub-objects (faces, edges, vertices).
- Grips: a click on a grip starts Stretch, and Space cycles Move, Rotate, Scale, Mirror. Dynamic
  input takes a typed distance at the cursor.

### Revit -- drag controls and temporary dimensions
- Dots at wall ends lengthen, shorten or rotate in plan; single arrows (shape handles) in elevation
  and 3D move a face along one line; double arrows drive instance parameters of families.
- Tab over a control cycles what the click will take.
- Temporary dimensions appear on selection; click the number to type a new one.
- A wall's thickness belongs to its type and is never dragged; its height (top) and its ends are.

### SketchUp -- Push/Pull (the benchmark for directness)
- Hover a face, click, move, click. Type a number and Enter for an exact distance.
- Hover another piece of geometry while pulling and the face stops at its height (inference).
- Double-click another face to repeat the last distance; with Ctrl (Option on a Mac) the pull
  starts a new face and leaves the old one.
- Pushing a face through the far side cuts a hole.

### Fusion 360 -- Press Pull
- One command by context: a face offsets, a sketch profile extrudes, an edge fillets. A manipulator
  arrow on the selection and a value box on screen.

## 2. What this app did before V123 (audited on the V122 build)

The gizmo (V110 to V112) was already a full manipulator: arrows, plane squares, a free-move square,
rotation rings, scale boxes, typed values during a drag, snapping to points and the grid, Escape to
cancel, Ctrl-drag copies, Shift precision, Alt to move the pivot. What was missing was everything
below the level of the whole object, and several paths were not dependable.

Missing:
- **No face could be pushed or pulled.** A box's height, a wall's top, a column's top, a pad's side:
  none could be dragged. A box's size was not even shown in Properties (a handler for it existed
  with nothing left to call it).
- **A closed sketch could not be pulled into a solid**; Pad needed a command and a typed height.
- **Clicking a handle did nothing** (Rhino's click-to-type was missing).

Faults found and confirmed with real pointer events:
1. **Dragging a selected object by its body was not an undo step.** Ctrl+Z afterwards undid the step
   before it -- after placing a box and dragging it, Ctrl+Z deleted the box.
2. The body drag snapped to nothing (no grid, no points), unlike every gizmo drag.
3. Ctrl+click on a gizmo arrow without dragging left an invisible copy on top of the original.
4. A plain click on a gizmo handle added an undo step that changed nothing.
5. The gizmo read-out and typed values were metres whatever the project's units: in a millimetre
   project, typing 500 moved an object 500 m. Coordinates typed while drawing had the same fault.
6. Editing a wall's Height in Properties removed its type; so did a grip drag of its end, Join,
   Trim, and copying it (Ctrl+D, Ctrl-drag, arrays, mirror). Copies of floors and columns fell back
   to the default type.
7. Rotating or scaling a floor turned its solid but not its outline; the next rebuild (a thickness
   edit) put it back where it was. Mirroring a floor threw an error.
8. Pad and Pocket of a moved sketch were made where the sketch had been before the move.
9. A primitive's Base Offset in Properties read its middle, not its base: a 3.5 m box standing on the
   ground read 1750 mm, and a Base Offset of 0 sank it half into the ground.

## 3. The V123 design

One principle from all five tools: **say how far with the hand, say exactly with a number, and let
the model decide what "pull this face" means for the thing being pulled.**

### Faces (push and pull)
- **Enter a face:** double-click a face, or Ctrl+Shift+click it (Rhino's sub-object gesture), or
  run PRESSPULL (PP) and click one. In a plan view, a click on an object's outline takes the side
  face seen edge-on there. Tab and Shift+Tab step through the object's faces; Esc goes back to the
  whole object.
- **The face shows** highlighted, with one arrow along its outward normal and a read-out naming it
  and its size ("TOP  HEIGHT 3 m"). The gizmo steps aside while a face is being worked.
- **Drag** the arrow or the face itself: the face follows the cursor along its normal. It stops on a
  point of other geometry the cursor passes over (SketchUp's inference), on a level's elevation for
  a horizontal face, and on grid steps with grid snap on. Shift is precision. Typing during the drag
  replaces the distance, keeping the direction the drag shows. Esc puts it back.
- **Click** the arrow or the face without dragging (or just start typing): a value box, which for a
  named size takes the size itself (Revit's temporary dimension) and otherwise a distance (Rhino).
- **What a face means depends on the object** -- the model decides, never the mesh:
  - Box: each face moves on its own; the opposite face stays; the box stays a parametric box.
  - Cylinder, cone, tube, prism, wedge: top and bottom set the height; a cylinder's or tube's curved
    side sets its radius; a sphere's surface its radius.
  - A solid made of faces (pads, cut solids, imported meshes, primitives turned into solids): any
    flat face bounded by edges of 25 degrees or more; it moves along its normal and its neighbours
    stretch. A facet of a curved surface says so instead. A push that would turn the solid inside out
    stops where it still holds.
  - Wall: its top is its height; the ends of an open wall lengthen or shorten it along its line; its
    sides do not move, because thickness belongs to its type (the face says so, and where to change
    it). Openings, rooms and clones follow as the wall changes.
  - Column: its top is its height; its sides are its type's width and depth.
  - Closed sketch: pulled up it becomes a solid (Pad) as it moves; pushed down it becomes a solid
    below. A sketch drawn on a solid is not pushed into it -- that is Pocket.
  - Anything else (floors, roofs, stairs, assets, openings): the face says what it is and where its
    sizes are set.
- One drag or one typed value is one undo step.

### The gizmo
- **Click a handle to type** (Rhino): an arrow asks for a distance, a square for two, the free-move
  square for two in plan or three in 3D, a ring for an angle, a scale box or the triangle for a
  factor. What each handle asks for, its hover name and its status-bar hint come from one table.
- A click adds no undo step; Ctrl+click makes no copy (the copy is made when the drag starts).
- Lengths read and type in the project's units.

### Moving by the body
- Dragging a selected object by its body is the gizmo's plan move: one undo step, snapping to
  points and the grid, typed "x,y" distances, Esc to cancel. Alt+drag lifts it straight up in 3D.

### Fixed with it (the class of each fault, not just the instance)
- One function carries every field of an element's record that a rebuild does not own, used by
  every rebuild, copy and transform of walls, floors and columns.
- A floor's transform returns its new outline.
- Pad and Pocket use the sketch where it is.
- Typed lengths, in the gizmo and in drawing coordinates, are in the project's units.
- A primitive's Base Offset is its base.

## 4. Not in V123
- Pushing a face into the solid it was drawn on (cut through, SketchUp's hole) -- Pocket does it.
- Edges and vertices of solids (Rhino's other sub-objects); fillets from edges (Fusion).
- Ctrl-to-copy a face before pulling it (SketchUp's new starting face).
- Scaling assets (families) -- V124 decides it with import units.

## Sources
- [Rhino 8 Help: Gumball](https://docs.mcneel.com/rhino/8/help/en-us/commands/gumball.htm)
- [Rhino Gumball guide](https://www.rhino3d.com/docs/guides/user-guide/gumball-basics/)
- [AutoCAD Help: PRESSPULL](https://help.autodesk.com/cloudhelp/2023/ENU/AutoCAD-Core/files/GUID-9D072BB2-D97F-41DB-8414-41BC83A16EFA.htm)
- [Revit Help: About Drag Controls](https://help.autodesk.com/cloudhelp/2025/ENU/Revit-GetStarted/files/GUID-A9AABE14-D963-46A4-AB74-CDDD336575DA.htm)
- [Revit Help: Controls and Shape Handles](https://knowledge.autodesk.com/guidref/RVT/2020/getting-started/GUID-EECE4EA1-DDBB-49A4-88DA-733DE0DE0B9E)
- [SketchUp Help: Pushing and Pulling Shapes into 3D](https://help.sketchup.com/en/sketchup/pushing-and-pulling-shapes-3d)
