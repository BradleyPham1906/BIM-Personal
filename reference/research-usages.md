# Research: usages and live areas (V131)

The first of Giraffe's ideas the owner chose (`research-giraffe.md`). In Giraffe, a **usage**
(Residential, Commercial...) assigned to a shape brings a whole set of assumptions: its colour,
its area efficiencies (GBA→GFA, GBA→NSA), and its rates. The numbers update as the shape is drawn.

## The areas, as the industry names them

- **GBA, gross building area.** Every floor, measured to the outside face of the external walls,
  including the walls, stairs and shafts. IPMS calls it IPMS 1 (external), and BOMA's Gross Area is
  close to it.
- **GFA, gross floor area.** The planning measure. It is close to GBA, but each jurisdiction
  excludes its own list: often car parking, plant, voids, sometimes the external walls. Giraffe
  takes it as a percentage of GBA, set per usage.
- **NSA, net saleable (or NLA, net lettable) area.** What a buyer or tenant gets: no common
  circulation, cores, services or walls. IPMS 3 (exclusive occupation) and BOMA's Usable Area are
  its relatives. Giraffe takes it as a percentage, per usage.
- **The ratios are assumptions, not measurements,** at the stage Giraffe works in. They come from
  the use. An apartment building is commonly about 80% efficient (NSA/GFA); an office floor plate
  about 85% net lettable; retail higher; a car park sells nothing.

## What this app already has

- **Rooms** carry a department and an occupancy. They are measured net, at their own area. Rooms can
  be filled by colour (ROOMCOLOR, V105).
- **Areas by Level** (V105b) traces the gross area inside the external walls of each level and sets
  the rooms' net area against it (efficiency %).
- **Floors** (slabs) are outlines on a level. **Masses** (box, cylinder, prism... and pads) are
  solids with a height.

## What V131 takes

- **A usage library,** saved with the project's types (`A3D.types.usage`).
  - Each usage has a name, a colour, a GBA→GFA ratio, a GFA→NSA ratio and a floor-to-floor height.
  - It also holds its own **parameters** (`unitSize = 75`) and **formulas** (`units = floor(NSA /
    unitSize)`).
  - It starts with Residential, Office, Retail, Hotel and Parking. Each can be changed, removed or
    added to.
- **A usage on a room, a floor or a mass,** chosen in Properties.
  - **Mass:** stacked into floors by its usage's floor-to-floor height. Each floor is measured by
    slicing the solid at the floor's mid-height, so a tapered or stepped mass is measured as it is.
    GBA is the sum, GFA = GBA × ratio, and NSA = GFA × ratio.
  - **Floor slab:** one floor of GBA, its outline's area.
  - **Room:** already a net area, so it counts as **NSA, measured**. It adds no GBA or GFA, which
    would invent a gross the drawing does not have.
- **Formulas,** in our own small evaluator. Never `eval`, and not HyperFormula, which is GPLv3.
  - Supported: numbers, + − × ÷ ^, brackets, `min max round floor ceil abs sqrt`.
  - Names: GBA, GFA, NSA, levels, height, footprint, the usage's parameters and its earlier
    formulas.
  - An error is said in words where it is written ("unknown name unitsize").
- **Live areas,** in Properties:
  - with nothing selected, the whole project by usage;
  - with a selection, the selection by usage.

  Also a schedule, **Areas by Usage**: per usage and level, with GBA, GFA, NSA and the formulas'
  totals.

## Not taken, yet

- **Colour by usage on the model.** That is the lens, V136.
- **Jurisdiction-specific GFA exclusion lists.**
- **Costs and a pro forma.** Formulas can already carry rates; a feasibility summary is later.

## Sources

- [Gross Building Area (RoomSketcher)](https://www.roomsketcher.com/blog/gross-building-area-gba/)
- [BOMA standards explained](https://creop.com/measure-an-owner-user-building-using-boma-standards/)
- [REBNY method of measurement](https://www.buildingengines.com/blog/rebny-method-of-commercial-building-measurement/)
- [Giraffe help: calculations overview](https://help.giraffe.build/en/articles/12334672-calculations-overview), [built-in properties](https://help.giraffe.build/en/articles/11818694-built-in-properties)
