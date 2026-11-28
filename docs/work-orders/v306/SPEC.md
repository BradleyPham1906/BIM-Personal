# V306 spec: OB2, IFC class and predefined type

Research: `docs/research/research-thatopen-gap.md` part 11 (the owner's answers, 2026-11-28) and
`docs/research/research-thatopen-gap/authoring-openbim.md` parts 5.1 and 9. Implementation target: local `main`.
Written by Claude, 2026-11-28. After V305 (it writes into the same `bim.ifc` record).

## 1. What it does for the user

Every element is saved as the IFC4 class an openBIM tool expects, with its predefined type: a wall an IfcWall STANDARD,
a floor an IfcSlab FLOOR, a ceiling an IfcCovering CEILING, a pad footing an IfcFooting PAD_FOOTING, a gable roof an
IfcRoof GABLE_ROOF, a door an IfcDoor DOOR, a room an IfcSpace SPACE. In Properties, an element shows its class and
predefined type, and the predefined type can be chosen from the IFC4 list for its class (a shear wall, a parapet, a
lintel, a skylight); the choice is the element's own and overrides its type's (the owner, 2026-11-28).

## 2. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/bim/ifc-class.js` | new (header done) | the four functions and two tables of part 4 | Cline, WO-01 to WO-04 |
| `docs/work-orders/v306/v306.test.mjs` | new | their tests | Claude (done) |
| `io/ifc-save.js`, `src/py/bim_ifcos.py`, `properties/palette.js` | changed | the class and predefined type written and chosen | Claude, WO-05 |

## 3. Data

- `bim.ifc.cls` (optional): the element's own IFC class, chosen in Properties; `bim.ifc.predefined` (optional): its own
  predefined type. Both kept by `bimCarryBim`. Rooms (`t: 'room'`) have no `bim`: their class comes from `t`.
- Roofs: `bim.style` is 'shed', 'gable' or 'hip', `bim.pitch` in degrees (`bim/roofs.js` 382, 392).
- The IFC4 predefined type lists: `docs/research/experiments/thatopen-gap/ifc4-predefined.json`, made by
  `ifc4-predefined.cjs` from web-ifc's IFC4 schema. The table `BIM_IFC_PREDEFINED` holds exactly those 12 lists.

## 4. Functions, `src/js/engine/bim/ifc-class.js`

- **WO-01 `bimIfcRoofPredefined(style, pitch)`**: 'FLAT_ROOF' when pitch is a finite number with |pitch| < 0.5;
  else 'SHED_ROOF' for 'shed', 'GABLE_ROOF' for 'gable', 'HIP_ROOF' for 'hip', 'NOTDEFINED' for anything else.
- **WO-02 `BIM_IFC_PREDEFINED`** (a table just above the function: the 12 lists of the JSON, same order) and
  **`bimIfcPredefinedOptions(cls)`**: a copy of cls's list; [] for a class not in the table (or not a string).
- **WO-03 `bimIfcPredefinedValid(cls, value)`**: true when value is a non-empty string in `bimIfcPredefinedOptions(cls)`.
- **WO-04 `BIM_IFC_CLASS`** (a table just above the function) and **`bimIfcClassOf(rec)`**: null for no rec. b =
  rec.bim or {}, own = b.ifc when an object, else {}. Kind: 'room' when rec.t is 'room', else b.type.
  1. own.cls a non-empty string: {cls: own.cls, predefined: own.predefined when valid for own.cls, else 'NOTDEFINED'}.
  2. kind 'roof': cls 'IfcRoof', predefined `bimIfcRoofPredefined(b.style, b.pitch)`.
  3. kind in the table: wall IfcWall STANDARD; floor IfcSlab FLOOR; ceiling IfcCovering CEILING; column IfcColumn
     COLUMN; beam IfcBeam BEAM; footing IfcFooting PAD_FOOTING; stripfooting IfcFooting STRIP_FOOTING; stair IfcStair
     NOTDEFINED; door IfcDoor DOOR; window IfcWindow WINDOW; room IfcSpace SPACE.
  4. Otherwise b.ifcType a non-empty string (an imported element): {cls: b.ifcType, predefined: 'NOTDEFINED'}.
  5. Otherwise {cls: 'IfcBuildingElementProxy', predefined: 'NOTDEFINED'}.
  In 2 and 3, own.predefined replaces the default when it is valid for the class.

## 5. Order of the work

WO-01 to WO-04 in order. Then Claude, **WO-05**: `io/ifc-save.js` sends `bimIfcClassOf(o)` for every element (its
present `BIM_IFC_SAVE_CLASS` table and the IfcBuildingElementProxy fallback retired); `bim_ifcos.py` passes
`predefined_type` to `create_entity` (and sets `ObjectType` when it is USERDEFINED); Properties shows the class and a
choice of predefined type from `bimIfcPredefinedOptions`, writing `bim.ifc.predefined` with undo; rooms are written as
IfcSpace only from OB6 (V-number then), here their class is only shown. The tests to tests/unit/; one browser check:
a model with each kind saved, the file's classes and predefined types read back by the import.

## 6. Not in this phase

Type objects (V307), rooms as IfcSpace in the file (OB6), choosing another class than the kind's in Properties (the
data allows it; the interface waits for a request).
