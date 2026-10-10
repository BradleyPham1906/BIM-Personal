---
title: Analysis
order: 7
---
# Analysis

The **Analyze** tab on the left rail is one list: every analysis and the site analysis together.
`ANALYSES` and `SITEANALYSIS` both open it. It runs in the order the work goes:
1. **The stages** of the site analysis, and red flags first when there are any.
2. **Define:** the boundary, the project type, and the questions the analysis must answer.
3. **The ten categories.** Each holds its data, its analyses, its findings, and what to check at
   the desk and on site (see [Site](site.html)).
4. **Model:** what reads the model itself, with no site data needed.

- **One line each.** A row has the analysis's name, what it shows now, its state (On, Out of
  date, Problems), and its main button (Run, Check, Show, Open). A category's line says how many
  findings it has, how much of its checklist is ticked, and which of its analyses are on.
- **Click a row to open it.** It opens to the whole status, the legend and the other buttons:
  Clear, Settings, Export, **Add as layer**. A row you open stays open the next time. A row inside a
  category opens on its own; opening the category does not open its rows.
- **Search.** The field at the top searches all of it:
  - analyses, by their name, what they say or their buttons;
  - categories, by their question, their data, their findings and their checklists.

  A category your words name shows whole, opened. Otherwise only the analyses in it that match are
  shown: "cut fill" shows Grading, inside Landform. It matches the start of words, so "rain" finds
  Rain on terrain and not every row that mentions terrain. **Esc** empties it.
- A button with nothing to act on yet (no frame, no survey) is disabled and says why.

| Where | Analysis | Run it | Settings |
|---|---|---|---|
| 3. Landform | Survey check | `SURVEYCHECK` | the surface's Survey Check group |
| 3. Landform | Slope, elevation, aspect | `SLOPEMAP`, `ELEVATIONMAP`, `ASPECTMAP` | the surface's Analysis group |
| 3. Landform | Grading, cut and fill | `GRADE`, `CUTFILLMAP` | the pad's Pad Elevation |
| 4. Water | Rain on terrain | `RAINFLOW` | |
| 5. Climate | Sun and shadows | `SUNSTUDY` | Properties > Site > Location |
| 5. Climate | Sun hours | `SUNHOURS` | Properties > Site > Location |
| 5. Climate | Solar on roofs and facades | `SOLAR` | |
| Model | Colour by usage, level, type, layer or any property | `COLOURBY` | Properties > View |
| Model | Areas by usage | live | Properties > Analysis |
| Model | Buildings, LOD and solids | `LODCHECK` | each building's LOD group |
| Model | Statistics | live | Properties > Project |
| Model | Frame analysis: the frame's forces and deflection | `ANALYZE` | Properties > Analysis |

The site's data sits in its category too:
- **1. Location** has the site context, `CONTEXT`;
- **2. Legal** has zoning and yield, `ZONING`;
- **5. Climate** has the climate and risk data, `CLIMATEGET`;
- **8. Access** has the access and people data, `ACCESSGET`.

Environmental risk and People and place share the Climate and Access data, and link to it.

On a phone or a tablet, the rows and buttons are sized for a finger.

## Results as layers

**Add as layer** keeps a result as a layer, in the **Layers** tab under **Analysis**. It is there
for the results drawn on the plan: sun hours, rain on terrain, a surface's slope, elevation or
aspect, and a proposed surface's cut and fill.

- **Sun hours and rain are kept as they were when run.** The picture is saved with the project, so
  it opens offline, and two runs can be compared: add December's sun hours, change the date, run
  again, add June's, and switch between them or lay one over the other.
- **Out of date.** When the model changes after a run, the layer says **Out of date**. **Update**
  runs it again on the layer's own date and surface, whatever the site's date is now.
- **Slope, elevation, aspect, cut and fill follow their surface.** They are never out of date. If
  the surface is deleted, the layer says **Gone** and draws nothing until an undo brings the
  surface back. When one becomes a layer, the surface's own colours are turned off, so it is not
  coloured twice.
- **One layer per run.** Once a run is a layer, the live picture gives way to the layer, so it is
  not drawn twice. Run it again to add another.

In **Layers**, a result layer's row has its colours, its name and an eye to show or hide it. Click
the row for:

- **Opacity:** shown on the plan while you drag; one undo step when you let go;
- its **legend**, and what it is: the date, the hours, the ponds, when it was added;
- **Update**, **Rename** (or double-click the name) and **Remove**.

Drag a row onto another to move it there. The top of the list is drawn on top.

The site's **data layers** (Properties > Site > Data Layers) are listed below, under **Data**:
the same eye, opacity, name and Remove as in Properties, and **Settings** to open their group.

Result layers are saved with the project and in a project file, and **Undo** takes back any change
to them. They are not part of the model's **History**: restoring a version leaves them as they are.

## Simulation

Three of the analyses are simulations. Each runs when you ask, draws its result over the plan,
and says when the model has changed since it ran.

| Simulation | Command | What it gives |
|---|---|---|
| Sun hours | `SUNHOURS` | hours of direct sun on the ground through the site's date, every 15 minutes, with a legend |
| Solar on roofs and facades | `SOLAR` | a clear-sky year of sun on every face: kWh/m2 a year on each building's roof and facades |
| Rain on terrain | `RAINFLOW` | where rain runs and where it ponds on a terrain surface: flow lines, ponds, their depth and volume |

`SIMCLEAR` clears all three. It does not remove their layers.

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
- **Colour By** can colour the buildings by their roofs' or facades' solar (the row's Colour by
  button sets it);
- they are saved with the project until cleared.

With buildings selected, only those are simulated. Everything still shades them.

### Rain on terrain

1. The surface (selected, or the first) is sampled on a grid.
2. Its dips are filled from the edges inward (Priority-Flood). The depth of each fill is where
   water ponds.
3. Each cell drains to its steepest lower neighbour.
4. Cells that collect enough rain become the flow lines, drawn thicker as they gather more.

The row gives each pond's volume and the deepest one.
