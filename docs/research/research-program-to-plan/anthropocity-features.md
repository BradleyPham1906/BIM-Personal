# Anthropocity's features, and where each goes in this app

Read 2026-11-16 by Claude: all 13 pages of anthropocity.com/docs (index, getting-started, ui-overview,
ui-main-toolbar, ui-map-graph-preview, ui-map-graph-editing, ui-nodes-map, ui-parameters-table,
ui-adjacency-chart, layout-view, graph-lab-paths, graph-lab-clusters, export-formats) and its home page. Level S:
a vendor describing its own product. Anthropocity is a proprietary web application; no code is available and
none is taken. What the app takes is the feature set, described here in our own words; every algorithm behind
it is the app's own, from published methods (`algorithms.md`).

The owner, 2026-11-16: "for the diagram and bubble diagram and adjacency matrix, those should be like an engine
like how anthropocity.com has (like i want everthing that anthropocity has and bring it into our system)".

## 1. The inventory

| # | Feature, as the documents describe it | The app today | Where it goes |
|---|---|---|---|
| 1 | Projects with a name, location (address or coordinates), units; canvas mode without a location | Projects, map, units | Exists |
| 2 | Program entry: buildings, rooms, size, floor, copies; landscape elements; first element always a building; switch row type room/building | V179 programme items (queued) | V179 amended |
| 3 | Import a programming sheet from CSV, Excel or PDF, parsed into buildings and rooms | CSV import elsewhere in the app | V179 amended (CSV, JSON); Excel and PDF need a library decision |
| 4 | "Generate Draft": rooms from a building description (AI, online) | No model inside the app | Paste-in text (decision 9 of program-to-plan); a pattern library offline |
| 5 | Pattern library: predefined building graphs (homes, libraries, shops) | Templates (assets/) | V234: programme templates as data |
| 6 | Manage Elements: one list of everything; double-click to edit; edited rows highlighted and zoomed to; duplicate, delete; offsets between buildings | Properties, the contents pane | V234 |
| 7 | Room groups with colours; assign by selecting rows; nodes take the group colour; sort by group then name | Usages colour rooms | V179 amended (group on an item) and V234 (colour) |
| 8 | Merge copies: identical rooms (differing only by an index) shown as one row for bulk adjacency editing, reversible | None | V179 amended (count already does this) and V234 (the matrix row) |
| 9 | Levels: a room's floor value creates the level; level 0 is ground; switch levels | Levels | V179 amended (level preference) |
| 10 | Graph view: bubbles arranged by their adjacencies (a force solver), rooms inside building nodes, on a map or blank canvas | V179's bubble diagram as a board figure (static) | V234: the graph engine |
| 11 | Link thickness by strength; view links to contextual elements | None | V234 |
| 12 | Pin a node by moving it; double-click to unpin; freeze or unfreeze all; solver status shown | None | V234 |
| 13 | Building outline as a bubble cluster or an editable polygon: corner and edge handles, add corners, rotate, lock; grid, snap, rotation increments, spacing | Drawing tools, grids | V234 |
| 14 | Target area, current area and delta for a building outline | Usages' live areas | V234 |
| 15 | Display modes: architecture (rooms and links), hybrid (outlines, names, rooms), planning (buildings and building links only) | None | V234 |
| 16 | Room names abbreviated under a size, full on hover or always | None | V234 |
| 17 | Underlays: site images and drawings, moved, scaled, rotated, reordered, locked | Map, image import | V234 (reuse) |
| 18 | Map backgrounds: grey, aerial, blank | Map tiles | Exists |
| 19 | Program Map: rooms as scaled circles, squares or rectangles grouped by building, with a scale; fold and unfold | V178 report figures | V234 |
| 20 | Program Table: named qualitative parameters (privacy, daylight...) with a description, a value per room (blanks allowed), a weight per parameter | None | V179 amended (the data), V234 (the table) |
| 21 | Radar charts of each building's rooms by parameter; label modes | Charts on boards | V234 |
| 22 | Generate links from parameters: adjacencies from weighted parameter similarity; regenerating overwrites | None | V234 (method in `algorithms.md`) |
| 23 | Adjacency matrix: double-click a cell for strength 1 (primary), 2, 3; source and target; open all or close all (building level); cleanup of visible links; hide a group | V179 relations (three kinds) | V179 amended (strength beside kind), V234 (the matrix) |
| 24 | Split screen: matrix or table beside the graph, live | Docked panels | V234 |
| 25 | Functional spaces mode: zone diagrams from the graph | None | V235 |
| 26 | Graph Lab clusters: community detection with a resolution; bridges (a link whose removal separates at least N rooms); ignore bridges while clustering; communication path between cluster anchors; circulation anchors | None | V235 |
| 27 | Articulation points; top hub (sum of link strengths); max and average hub score; average and max depth from the network's centre; building aspect, major and minor axes | None | V235 |
| 28 | User paths: named, ordered rooms one kind of user visits, a frequency (primary, secondary, occasional), a colour; add, edit, delete, undo; show on the graph | V181 routes (queued) | V235 |
| 29 | Path coverage: rooms on at least one path, groups and main rooms covered, the rooms left out | None | V235 |
| 30 | Walk-through rooms: open, closed or guessed from the name | None | V235 (data), V236 (used) |
| 31 | Suggest paths and suggest an entrance (AI, online) | No model inside | Paste-in text; an offline heuristic for the entrance |
| 32 | Layout view: rooms as scaled shapes inside each building on a bay grid, per level; rooms rectangles except round a corridor elbow or the stair | None | V236 |
| 33 | Layout settings: minimum bay width, bay width per building, fit or auto-optimise bay widths; small-room threshold and max rooms per cluster; keep the outline; spare floor as exterior space or rooms grow; follow the bubble diagram | None | V236 |
| 34 | Corridors routed from user paths along walls, never through rooms unless allowed; loops round blocks with short stubs to the facade; main width where a wall is walked by at least the spine threshold of paths; spine and access spurs, or all legs | None | V236 |
| 35 | Stair core in a corridor corner, the same place on every level, sized by the programme; placed by path priority or to balance the worst leg; how far it may move | None | V236 |
| 36 | Entrances on the exterior wall, snapped where a room meets it; the corridor network routed to arrive there | None | V236 |
| 37 | Doors on each wall a room shares with a corridor, generated; open spaces without a wall line to the corridor | Door openings (bim/) | V236, V237 |
| 38 | Walls drawn with exterior and interior thicknesses | Walls | V236 (drawn), V237 (real walls) |
| 39 | Problems reported in plain words: no wall route, unjoined pieces, legs between levels, access spurs and their length, rooms with no access and why, corridor area and share | None | V236 |
| 40 | A one-line summary per layout: programme fill, corridor share, area deviation | None | V236 (the scorecard) |
| 41 | The layout follows edits; once settled it does not reshuffle; dragging a room moves its node | None | V236 |
| 42 | Export the current view to PDF and SVG; the Program Map to a scaled PDF; radar charts to PDF; DXF with chosen levels, one file or one per level, levels stacked by floor height | Print, DXF export | V234 to V236 (each view) |
| 43 | Undo and redo; save and load a local file (no autosave) | Undo, autosave, history | Exists, and better |
| 44 | Hints the first time an action is used; a short tutorial; template projects | The guide | V234 |
| 45 | "Evaluate: analyse arrangements, compare alternatives" (planned, not built) | V231 queued | V231 with V238's records |

## 2. What the documents do not say

The force solver, the community detection method, how parameter similarity becomes a link, how rooms are cut on
the bay grid, how corridors are routed from paths, and how the stair is placed are all undocumented. These are
the algorithms the app must choose from published methods (`algorithms.md`).

## 3. What the app already does better

Autosave and versioned history; real BIM elements and IFC export downstream; standards with editions; the
site-analysis findings with sources and confidence (V158, V172); offline from one file.
