# V305 spec: OB1, IFC identity: GlobalIds that last

Research: `docs/research/research-thatopen-gap.md` part 11 (the owner's answers, 2026-11-28: "Do what's standard and as
recommended") and `docs/research/research-thatopen-gap/authoring-openbim.md` parts 5.4 and 9. Implementation target:
local `main`. Written by Claude, 2026-11-28. Cline reads this with TASKS.md.

## 1. What it does for the user

Save as IFC writes the same GlobalId for the same element every time: walls (each straight segment), floors, columns,
beams, roofs, stairs, footings, doors and windows (and the opening each cuts), every storey and building, the site and
the project. A BCF issue, a model comparison or a federated coordination model can then follow an element from one
save to the next, as they can with Revit's exports. A copy, an array or a mirror copy is a new element and gets new
GlobalIds. Elements on hidden layers are now saved too (the owner, 2026-11-28), and the file says which layers were
hidden. Nothing changes on screen; Properties shows the element's GlobalId.

## 2. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/bim/ifc-identity.js` | new (header done) | the six pure functions of part 4 | Cline, WO-01 to WO-06 |
| `docs/work-orders/v305/v305.test.mjs` | new | their tests | Claude (done) |
| `io/ifc-save.js`, `src/py/bim_ifcos.py`, `io/ifcos-worker.js`, the copy paths, `properties/palette.js` | changed | the wiring, hidden layers | Claude, WO-07, WO-08 |
| `io/thatopen-runtime.js`, `io/ifc-full.js` | changed | the faster import route, then cc-ifc retired | Claude, WO-09 |

## 3. Data

- `bim.ifc` on an element's `bim` record: `{guid: string22, segGuids: [string22] (walls), openingGuid: string22
  (doors and windows), cls, predefined (V306)}`. `bimCarryBim` already keeps every `bim` field through rebuilds.
- `A3D.ifcIds`: `{project, site, buildings: {buildingId: string22}, levels: {levelId: string22}}`, saved with the project.
- A GlobalId is IFC's 22-character form (alphabet `0-9A-Za-z_$`, the first character 0 to 3): 128 bits, here a random
  RFC 4122 version 4 UUID, compressed. The codec is `bimTorGuidFromHex`, `bimTorGuidToHex`, `bimTorGuidValid`
  (`io/ifc-review.js`), checked against IfcOpenShell's `guid.py` on 207 vectors (second-reader.md, F8).
- `rand`: a function returning a number in [0, 1); tests pass a seeded one, the app passes nothing (Math.random).

## 4. Functions, `src/js/engine/bim/ifc-identity.js`

ES5. Each may use only the names its task lists.

- **WO-01 `bimIfcGuidNew(rand)`**: rand is used when it is a function, else Math.random. 16 bytes, byte i =
  Math.floor(v * 256) where v = +rand(), with v = 0 when it is not a number at or above 0, and v = 0.999999 when it is 1
  or more. Then byte 6 = (byte 6 AND 0x0f) OR 0x40 and byte 8 = (byte 8 AND 0x3f) OR 0x80 (RFC 4122 version 4). The 16
  bytes as 32 lower-case hex digits, two per byte, through `bimTorGuidFromHex`. Example: rand giving 0, 1/256, 2/256 ...
  makes hex `000102030405460788090a0b0c0d0e0f`.
- **WO-02 `bimIfcEnsureIdentity(bim, rand)`**: null when bim is null or undefined. Stamps and returns the same bim:
  when `bim.ifc.guid` is valid, nothing changes; else `bim.ifc` (made `{}` when missing or not an object; its other
  fields kept) gets `guid` = `bim.guid` when that is valid (an imported element), else `bimIfcGuidNew(rand)`.
- **WO-03 `bimIfcSegmentGuids(bim, n, rand)`**: [] when bim is null. Calls `bimIfcEnsureIdentity(bim, rand)`, then makes
  a list of length n (n below 1 or not a number: 0): entry 0 is `bim.ifc.guid`; entry i > 0 is `bim.ifc.segGuids[i]`
  when that is valid and not already in the list, else `bimIfcGuidNew(rand)`. Stores it as `bim.ifc.segGuids` and
  returns a copy.
- **WO-04 `bimIfcForgetIdentity(bim)`**: null when bim is null. Deletes `bim.guid`, `bim.ifc.guid`, `bim.ifc.segGuids`,
  `bim.ifc.openingGuid`; deletes `bim.ifc` when nothing is left in it; returns bim. Every other field stays.
- **WO-05 `bimIfcSpatialIds(prev, levelIds, buildingIds, rand)`**: a new object `{project, site, buildings, levels}`;
  prev (may be null) is not changed. Each value is prev's when valid, else `bimIfcGuidNew(rand)`, made in this order:
  project, site, each building id in buildingIds' order, each level id in levelIds' order. Only the ids given appear.
- **WO-06 `bimIfcDedupe(items, rand)`**: items `[{id, guid}]` (not changed); returns `{guids: {id: string22}, made,
  repeated}`. In order: an item without an id (null, undefined or '') is left out; a valid guid not seen before is
  kept; otherwise a new one from `bimIfcGuidNew(rand)`, made again while it equals one already given. `made` counts the
  new ones; `repeated` counts the valid guids seen before (a copy that kept its GlobalId).

## 5. Order of the work

WO-01 to WO-06 in order (each may use the earlier ones). Then Claude:

- **WO-07 the wiring.** `bimIfcSaveBase` (io/ifc-save.js) stamps each exported element with `bimIfcEnsureIdentity` and
  writes `bim.ifc.guid`; straight walls take `bimIfcSegmentGuids` (replacing the `<id>#i` segments' dropped GlobalIds,
  line 80); doors and windows send `ifc.openingGuid` (made with `bimIfcGuidNew` once) for their IfcOpeningElement;
  `A3D.ifcIds = bimIfcSpatialIds(A3D.ifcIds, levels, buildings)` before each save, saved with the project; the export
  runs `bimIfcDedupe` over everything it sends and writes the result back. `bim_ifcos.py`: the project, site, each
  building and each storey take their GlobalIds (`bim_ifcos_keep_guid`); `bim_ifcos_put_opening` keeps the opening's.
  The copy paths (`bimCopySelection` editing/drafting-modify.js, `duplicateSelection` editing/selection-tools.js,
  `bimMirrorSelection` with copy editing/precision-editing.js, the array tools, paste) call `bimIfcForgetIdentity` on
  each new element's `bim`; the list is made by grep at the time, not assumed. Properties shows the GlobalId.
- **WO-08 hidden layers exported** (the owner, 2026-11-28): `io/ifcos-worker.js:142` stops leaving them out; the file's
  header description lists the hidden layers' names.
- **WO-09 the faster import, then cc-ifc retired** (the owner's decision 1): measure IfcImporter then
  `SingleThreadedFragmentsModel` (no worker round trips; research-thatopen-gap/fragments-webifc.md part 5) against the
  present route on V196's 13 files (e03). Keep whichever is faster when e03 still agrees. Then remove cc-ifc
  (`runtime/cc-ifc/`, `tools/ifc/`, its branch in `io/ifc-full.js`), keeping the walls-and-slabs fallback.
- **WO-10 the browser check** (Rule #1, once): a small model saved as IFC twice without edits gives two files with the
  same GlobalId set; a copied wall's GlobalId differs from its source's; a hidden layer's wall is in the file.
- Records: PIPELINE row 305, QUEUE, the STATUS log, Notion.

## 6. Not in this phase

IFC classes and predefined types (V306), type objects (V307), material layers (OB4), standard property sets (OB5),
spaces (OB6), joins (OB7), classification and georeferencing (OB8).
