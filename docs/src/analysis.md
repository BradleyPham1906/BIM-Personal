---
title: Analysis
order: 7
---
# Analysis

The **Analyze** tab on the left rail lists every analysis. Each card says what it shows now, with
buttons to run it or to open its settings in Properties. `ANALYSES` opens the tab.

| Analysis | Run it | Settings |
|---|---|---|
| Structure: the frame's forces and deflection | `ANALYZE` | Properties > Analysis |
| Sun and shadows | `SUNSTUDY` | Properties > Site > Location |
| Colour by usage, level, type, layer or any property | `COLOURBY` | Properties > View |
| Areas by usage | live | Properties > Analysis |
| Survey check | `SURVEYCHECK` | the surface's Survey Check group |
| Buildings: LOD and solids | `LODCHECK` | each building's LOD group |
| Statistics | live | Properties > Project |

A button with nothing to act on yet (no frame, no survey) is disabled and says why.

## Simulation

Under the analyses, the Analyze tab has three simulations. Each runs when you ask, draws its
result over the plan, and says when the model has changed since it ran.

| Simulation | Command | What it gives |
|---|---|---|
| Sun hours | `SUNHOURS` | hours of direct sun on the ground through the site's date, every 15 minutes, with a legend |
| Solar on roofs and facades | `SOLAR` | a clear-sky year of sun on every face: kWh/m2 a year on each building's roof and facades |
| Rain on terrain | `RAINFLOW` | where rain runs and where it ponds on a terrain surface: flow lines, ponds, their depth and volume |

`SIMCLEAR` clears all three.

### Sun hours

- **How it works:** for each 15-minute step of daylight on the site's date, every solid's shadow
  is cast onto the ground, and each cell of a grid counts the steps it is lit.
- **Cells under a building** are its roof, not ground, and are left out.
- **The date:** set it in **Properties > Site > Location**.

### Solar

- **The year:** the sun on the 21st of each month, every half hour.
- **Direct sun:** Meinel's clear-sky model, 1361 x 0.7^(AM^0.678) W/m2, with Kasten and Young's
  air mass.
- **Sky light:** a tenth of that on a horizontal face, less on a tilted face by how much sky it
  sees.
- **Shading:** a face only gets direct sun when a ray from its centre to the sun meets no solid,
  including the building itself.
- **What it leaves out:** clouds. This is the clear-sky potential: real weather gives less.

**Where the results go:**
- each building's LOD group shows them;
- **Colour By** can colour the buildings by their roofs' or facades' solar (the card's Colour By
  button sets it);
- they are saved with the project until cleared.

With buildings selected, only those are simulated. Everything still shades them.

### Rain on terrain

1. The surface (selected, or the first) is sampled on a grid.
2. Its dips are filled from the edges inward (Priority-Flood). The depth of each fill is where
   water ponds.
3. Each cell drains to its steepest lower neighbour.
4. Cells that collect enough rain become the flow lines, drawn thicker as they gather more.

The card gives each pond's volume and the deepest one.
