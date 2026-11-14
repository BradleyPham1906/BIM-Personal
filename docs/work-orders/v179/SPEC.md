# V179 spec: Interiors I1, programme and adjacency (and I2's first measurement)

Research: `docs/research/research-notion-v177-v180-interiors.md` and its fixture
`docs/research/fixtures/interiors/`. PIPELINE numbers Interiors 179 to 182 (I1 to I4); Notion's task says
V177-V180, renamed with WO-12. The owner's decisions, 2026-11-14, all as recommended: the programme is kept apart from
the measured rooms and linked by stable ids, unmatched items and rooms kept; "next to" means a shared wall or a door,
"near" a route by the doors within a distance the owner sets (15 m when not set), "apart" neither; a missing or open
(stale) room makes a check "not evaluated", never a pass; a clearance or width is a measurement against a value from
V167's standards registry with its edition, never a compliance finding; routes in I1 cost one per door unless a
length is known (true walking distances are I3's). Implementation target: local `main`. Written by Claude,
2026-11-14.

## 1. What it does for the user

In Properties for the building, a Programme table: each use (Bedroom, Kitchen, ...), how many, the area range, why.
Under it the relations: Kitchen next to Dining (required), Bedroom apart from Garage, Office near Entry within 10 m.
The app reads the rooms already drawn, matches them by their use, and marks each line ok, short, over, area out of
range, met, not met or not evaluated, with the reason. The bubble diagram draws the programme as circles sized by
area and lines by relation, coloured by status. Phone, tablet and desktop: the table scrolls, the diagram fits.

## 2. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/bim/interiors.js` | new, after `rooms.js` (header done) | nine pure functions (part 4) | Cline, WO-01 to WO-09 |
| `docs/work-orders/v179/v179.test.mjs` | new | their tests | Claude (done) |
| `properties/`, `ui/`, `sheets/board-figures.js` | changed | the table, the checks on the live model, the bubble diagram | Claude, WO-10 to WO-12 |

## 3. Data

- **A programme item** `{id, use, count, areaMin, areaMax, rationale}`: `count` an integer 1 or more; areas in m2 or
  `null`, `areaMin <= areaMax`.
- **A relation** `{a, b, kind: 'required'|'desired'|'forbidden', rel: 'next'|'near'|'apart', nearM}`, `a` and `b`
  room ids or uses as WO-10 decides.
- **A room fact** `{id, use, area, pts: [[x, z], ...]}`, made by WO-10 from the model's rooms.
- **A door** `{id, center: [x, z], dir: [dx, dz], width}`, as the app's door markers hold them (`dir` along the wall).
- **A link** `{a, b, door, width}`: the room on the door's left (`center + (-dir.z, dir.x) * reach`) and on its right.
- **Facts for the checks** `{rooms: {id: 1}, shared: {'a|b': metres}, doors: {'a|b': count}, dist: {from: {to: cost}}}`.

## 4. Functions, `src/js/engine/bim/interiors.js`

- **WO-01 `bimIntProgramItem(raw)`**: `id` and `rationale` strings else `''`; `use` trimmed string else `''`;
  `count` floored when a finite number 1 or more, else 1; `areaMin`, `areaMax` finite numbers 0 or more, else `null`,
  swapped when both are set and out of order.
- **WO-02 `bimIntRelation(raw)`**: `null` unless `a` and `b` are non-empty, different strings. `kind` one of the
  three else `'desired'`; `rel` one of the three else `'next'`; `nearM` a finite number above 0 else 15.
- **WO-03 `bimIntInside(p, poly)`**: even-odd crossing test on `[x, z]` points; `false` without a polygon.
- **WO-04 `bimIntSharedLength(pa, pb, tol)`**: for each edge of `pa` (skipping one shorter than 1e-9) and each edge
  of `pb` whose both ends lie within `tol` (default 0.5 m when not a number 0 or more) of the edge's line, the length
  of the overlap of their projections onto the edge, clipped to the edge; the sum. 0 when either has fewer than 3
  points.
- **WO-05 `bimIntDoorLinks(rooms, doors, reach)`**: `reach` 0.4 m unless a positive number. For each door with a
  centre and a non-zero `dir`: the points `center ± (-dz, dx) / |dir| * reach`; the first room containing each (by
  `bimIntInside`), else `'outside'`; a link `{a: <left>, b: <right>, door: id, width: width or null}` unless both
  sides are the same. `[]` without rooms or doors.
- **WO-06 `bimIntDistances(links, from, cost)`**: Dijkstra over the links as undirected edges, each costing
  `cost[door]` when that is a number 0 or more, else 1; answers `{room: cost}` for every room reached, `from` at 0.
  Rooms not reached are absent. `{}` without links or a string `from`.
- **WO-07 `bimIntCheck(rel, facts)`**: no relation: `not evaluated`, `'not a relation'`; either room missing from
  `facts.rooms`: `not evaluated`, `'a room is not in the model'`. Shared length and door count read under `'a|b'` or
  `'b|a'`. `next`: met when either is above 0 (`'a door between them'` when a door, else `'a shared wall'`), else not
  met `'no shared wall or door'`. `apart`: the reverse with the same reasons. `near`: `facts.dist[a][b]`; absent:
  `not evaluated`, `'no route between them'`; else met `'route 9.0 m'` when within `nearM`, else not met
  `'route 9.0 m, over 5 m'` (one decimal, `nearM` as it is).
- **WO-08 `bimIntMatch(items, rooms)`**: for each item, the rooms of the same `use` in order (`rooms`), how many
  (`have`), those whose `area` is not a number or out of the item's range (`offArea`); `status` `'short'` when fewer
  than `count`, `'over'` when more, else `'area'` when any is out of range, else `'ok'`.
- **WO-09 `bimIntMinWidth(widthM, minIn)`**: `'not evaluated'` unless both are finite numbers; `'meets'` when
  `widthM / 0.0254 >= minIn - 1e-9`, else `'below'`.

## 5. Order of the work

WO-01 to WO-09 in order (WO-05 uses WO-03). Then Claude: **WO-10** the facts from the live model (rooms with their
use, area and outline from `rooms.js`; open regions as missing; door markers whose cut failed left out with a
warning), the Programme table in Properties, saved with the project, undo; **WO-11** the bubble diagram as a board
figure and the one browser check of the new interface; **WO-12** I2 to I4's next work orders (clearance zones on
assets from the standards registry, routes on walkable geometry, isovists), the records and Notion's renaming.

## 6. Not in this phase

Egress and fire compliance; daylight; clearance zones (I2, after WO-12); scans and RoomPlan import; walking
distances through rooms (I3).
