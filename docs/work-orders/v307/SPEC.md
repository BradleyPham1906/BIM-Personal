# V307 spec: OB3, types as IFC type objects

Research: `docs/research/research-thatopen-gap.md` part 11 (the owner's answers, 2026-11-28) and
`docs/research/research-thatopen-gap/authoring-openbim.md` parts 5.2 and 9. Implementation target: local `main`.
Written by Claude, 2026-11-28. After V305 (it uses `bimIfcGuidNew`) and V306.

## 1. What it does for the user

The app's types (Walls, Floors, Ceilings, Columns, Beams, Isolated Footings, Wall Foundations: `TYPE_CATS` in
`bim/type-instance-params.js` 115-124) are saved as IFC type objects (IfcWallType, IfcSlabType, IfcCoveringType,
IfcColumnType, IfcBeamType, IfcFootingType), each with a GlobalId that lasts, and every element of a type is tied to it
(IfcRelDefinesByType), as Revit's exports do. A schedule or a checking tool reading the file sees "Generic 200mm" once,
with its 40 walls, instead of 40 unrelated walls. A type's predefined type is written on the type; an element writes
its own only when it differs (the owner: the instance overrides).

## 2. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/io/ifc-save-types.js` | new (header done) | the five functions of part 4 | Cline, WO-01 to WO-05 |
| `docs/work-orders/v307/v307.test.mjs` | new | their tests | Claude (done) |
| `bim/type-instance-params.js`, `io/ifc-save.js`, `src/py/bim_ifcos.py` | changed | types stamped, sent, written and assigned | Claude, WO-06 |

## 3. Data

- A type record (`bim/type-instance-params.js`): `{id, name, params}` in its category's list; it gains `ifc: {guid,
  predefined}`. `bimIfcSaveTypes` takes them flattened as `{id, cat, name, ifc}`.
- An element names its type by `bim.typeId` (and `bim.typeCat` for footings).

## 4. Functions, `src/js/engine/io/ifc-save-types.js`

- **WO-01 `BIM_IFC_TYPE_CLASS`** (a table just above the function: wall IfcWallType STANDARD, floor IfcSlabType FLOOR,
  ceiling IfcCoveringType CEILING, column IfcColumnType COLUMN, beam IfcBeamType BEAM, footing IfcFootingType
  PAD_FOOTING, stripfooting IfcFootingType STRIP_FOOTING) and **`bimIfcTypeClassOf(cat)`**: the type class, '' for any
  other cat (only the table's own keys: use hasOwnProperty).
- **WO-02 `bimIfcTypePredefinedDefault(cat)`**: the table's predefined type, 'NOTDEFINED' for any other cat.
- **WO-03 `bimIfcEnsureTypeIdentity(t, cat, rand)`**: null for no t. Stamps and returns the same t: `t.ifc` made `{}`
  when missing or not an object (its other fields kept); `t.ifc.guid` kept when valid, else `bimIfcGuidNew(rand)`;
  `t.ifc.predefined` kept when a non-empty string, else `bimIfcTypePredefinedDefault(cat)`.
- **WO-04 `bimIfcPredefinedPair(typePre, instPre)`**: an empty or non-string value counts as none. No type predefined:
  {type: null, instance: instPre or 'NOTDEFINED'}. Else {type: typePre, instance: instPre when it is given and differs
  from typePre, else null} (null: the element writes none and inherits the type's).
- **WO-05 `bimIfcSaveTypes(types, used)`**: in the order of types (null: []), each t with `used[t.id]` true, a class
  (`bimIfcTypeClassOf(t.cat)` not '') and a valid `t.ifc.guid`, as `{id, guid, cls, name: t.name or t.id, predefined:
  t.ifc.predefined when a non-empty string, else the category's default}`; the rest left out.

## 5. Order of the work

WO-01 to WO-05 in order. Then Claude, **WO-06**: `bimEnsureTypes` (type-instance-params.js 546-572) stamps every type
with `bimIfcEnsureTypeIdentity`; `io/ifc-save.js` sends `bimIfcSaveTypes(...)` and each element's `typeGuid` and
`bimIfcPredefinedPair`'s instance value; `bim_ifcos.py` makes each type (`root.create_entity` with its GlobalId, name
and predefined type), then `type.assign_type(related_objects, relating_type)` per type, and only after it sets an
element's own predefined type where the pair gives one (assign_type clears it: IfcOpenShell `assign_type.py` 259-265,
authoring-openbim.md part 9). The tests to tests/unit/; one browser check: two walls of one type and one of another,
saved, the file holds two IfcWallType each with its walls, and the GlobalIds are the same on a second save. Records.

## 6. Not in this phase

Material layer sets on the types (OB4), property sets on the types (OB5), roofs and stairs as types (they have no type
category in the app).
