# Program to plan: the question and the hypotheses

Written 2026-11-15, before any search (research-protocol.md, "The question first"). The main note is
`docs/research/research-program-to-plan.md`.

## Where this comes from

The owner wrote six brief research pages in Notion with Notion AI (2026-11-15), proposing phases V233 to V238:
the architectural brief and program; spatial relationships and the adjacency matrix; bubble, flow and site
diagrams; schematic space planning; program-to-BIM generation; design evaluation and comparison. Claude read
them against the repository and found the direction sound and three things unsettled: an overlap with phases
already queued (V179 programme and adjacency, V181 routes, V231 exploration), one phase underspecified where it
is hardest (V236, the plan generator), and one stale fact (IFC export is being built in V176 and V177). The
owner's pages are level U or S under the protocol until their sources are read here.

## The question

**How does the app get from a brief to a schematic plan to BIM spaces, on one data model that the queued
phases (V179 to V182, V228 to V232, V176 and V177) already begin, and with which layout method?**

## What a good answer must decide

1. One data model: how the brief, the programme, the relations, the schematic spaces and the BIM rooms relate,
   and whether V233 and V234 extend V179's records or replace them.
2. The identity chain: which ids exist, which is derived from which, and what survives a re-run or a re-import.
3. The layout method for V236: what can place 10 to 20 spaces with their areas, adjacencies and a corridor,
   deterministically, in plain ES5, and how often it meets the constraints.
4. What V237 adds to V177's IFC export (spaces, their properties, the GlobalId) and whether IDS checks can run in
   the app's Python worker.
5. Whether V238 is a phase of its own or the criteria and decision log of V231.
6. Where an approved revision lives: the app's history, or a record of its own.
7. What "suggested by AI" means in an offline app.
8. The order of the phases against V228 to V232.

## Hypotheses (each can be proved wrong)

- **H1, one model.** V179's programme item and relation records can be extended (more fields, more relation
  kinds) to carry everything V233 and V234 ask for, without a second model. (The app's code and V179's spec.)
- **H2, layout by slicing.** A slicing layout (a treemap ordered by adjacency, then local swaps scored by
  adjacency) places a 12-space, one-level programme in a rectangle with every area within 10% and at least 80%
  of the required adjacencies met, in under a second, in plain ES5. (Measured here.)
- **H3, the corridor is the hard part.** With a corridor that must reach every space, the same method meets
  fewer adjacencies or wastes more area, and a method built around the corridor first (a spine, rooms on both
  sides) does better for programmes of this size. (Measured here.)
- **H4, published methods.** Published deterministic methods for this size exist beyond treemaps (rectangular
  dualisation, spine and double-loaded layouts, mixed-integer formulations), and their own papers state the
  limits: rectangles only, or no corridor, or a solver library. (Papers and code read as text.)
- **H5, spaces in IFC.** IfcOpenShell's API in the app's worker can write IfcSpace with its storey, names,
  quantities and property sets, and its IDS checker (ifctester) is pure Python that the worker could carry.
  (IfcOpenShell's documentation and package metadata; nothing is run without the owner's approval.)
- **H6, evaluation is exploration.** Everything V238 asks for beyond V231 is data (criteria, gates, a decision
  record), not a new search engine. (V231's row and the research behind it; practice documents.)
- **H7, approvals.** An approved programme revision can be a named commit in the app's existing history, with no
  new mechanism. (The app's history code.)
