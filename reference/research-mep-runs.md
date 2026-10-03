# Research: duct and pipe runs that connect, with a size and a flow (V137)

This is Track B item 4, the last of the object model. The owner asked "are these mep features
being group under MEP?" and chose **one MEP discipline** in the dock's picker, as Revit gathers
them under its Systems tab.

The points below come from search summaries of the pages under Sources. The equations are standard
and are checked in the suite against their closed forms.

## How Revit does it

- **Connectors carry the system.** Every MEP element has connectors. Each connector carries:
  - a domain (HVAC or piping);
  - a system classification (Supply Air, Domestic Cold Water, …);
  - a flow direction;
  - a shape and size.

  An element without connectors cannot take part in a system.
- **Physical connections pass size and flow.** A connection in the mechanical and plumbing domains
  is physical: its connectors pass sizing and flow from one part to the next.
- **Fittings are made, not drawn.** Where runs meet, the routing preferences insert an elbow, a
  tee, a cross, a transition (reducer) or a union. A person draws runs, and the fittings follow.
- **Systems gather the connected parts.** A system is the set of connected parts of one
  classification. Flow is summed from the terminals (air terminals, fixtures) back to the
  equipment.

## The friction equations

- **Darcy-Weisbach**, ASHRAE Fundamentals' method for ducts:

      Δp = f · (L / Dh) · ρV²/2

  - For a round section, Dh is the diameter.
  - For a rectangular section a × b, Dh = 2ab / (a + b).
- **The friction factor f:**
  - **Turbulent (Re ≥ 2300):** Colebrook, solved by iteration:

        1/√f = −2 log₁₀( ε/(3.7 Dh) + 2.51/(Re √f) )

  - **Laminar (Re < 2300):** f = 64/Re.
- **Roughness ε:**
  - galvanised steel: 0.09 mm (the basis of ASHRAE's duct friction chart);
  - copper: 0.0015 mm.
- **Fluid properties:**
  - **Air:** standard air at 20 °C, ρ = 1.204 kg/m³ and μ = 1.8185 × 10⁻⁵ Pa·s.
  - **Water at 20 °C:** ρ = 998.2 kg/m³ and μ = 1.002 × 10⁻³ Pa·s.
  - **Domestic hot water at 60 °C:** ρ = 983.2 kg/m³ and μ = 0.467 × 10⁻³ Pa·s.
- **Hazen-Williams**, for water pipes, is shown beside Darcy as the check plumbers use:

      h = 10.67 · L · Q^1.852 / (C^1.852 · d^4.87)

  - Units: h and L in metres, Q in m³/s, d in metres.
  - C = 140 for copper (its design value).

## What V137 takes

- **The MEP discipline** in the dock's picker, with three groups:
  - **HVAC:** Duct and Air Terminal.
  - **Plumbing:** Pipe and Fixture.
  - **Systems:** Flow, which turns the flow and loss display on and off, as ANALYZE does.
  - There are no fitting tools, because the fittings are made where runs meet (Revit's routing
    preferences). Electrical waits until it has a tool.
- **A run** is drawn like a polyline, on the active level at an offset above it: 2.7 m for a duct
  and 2.4 m for a pipe. Enter ends it, and it becomes one object.
  - **Its size:**
    - a duct is rectangular (width × height) or round (diameter);
    - a pipe is round, and its size is the inside diameter.
  - **Its system:**
    - ducts: Supply, Return or Exhaust Air;
    - pipes: Domestic Cold Water, Domestic Hot Water, Hydronic Supply or Hydronic Return.
  - **Its direction:** it is drawn from the equipment outward, its start upstream.
  - **Its geometry is derived** from the stored centreline, with mitred elbows at the bends.
- **Connections are found, never stored**, the way V125 finds a frame's joints. A run's end is
  connected when it lies on another run of the same system at the same elevation:
  - on that run's end, it makes an elbow, a union or a transition;
  - part way along that run, it makes a tee.

  A run started on another run is snapped onto its centreline, so it connects.
- **Flow.**
  - Each open end at the downstream side is a terminal, carrying the flow set on the run.
  - Flow sums from the terminals back to the source, the run whose start meets nothing.
  - Each section between a bend or a tee gets its flow Q, velocity V = Q/A, Reynolds number,
    friction factor, loss per metre and loss.
  - The index path is the terminal with the greatest total loss from the source.
- **Refusals, each with its reason:** a loop, two sources in one system, a terminal with no flow,
  and a run touching one of another system.

## Not taken, yet

- **Fitting losses.** These are local loss coefficients from ASHRAE's fitting database. They need
  that table to be defensible, so the display says that fittings are not counted.
- **Risers:** runs that change elevation.
- **Sizing:** equal friction and velocity methods.
- **Gravity drainage:** sanitary runs, which are sized by slope, not pressure.
- **Electrical** circuits.
- **Equipment families** with their own connectors.
- **IfcDuctSegment and IfcPipeSegment export:** runs export as generic solids.

## Sources

- [Autodesk: Connectors (Revit)](https://help.autodesk.com/view/RVT/2024/ENU/?guid=GUID-92B74F31-03EB-4D14-93A1-BD4E4294A629)
- [The Revit MEP API](https://jeremytammik.github.io/tbc/a/0219_mep_api.htm)
- [Revit MEP connectors: pipe, duct, electrical](https://pipingcontent.com/blog/revit-mep-connectors-pipe-duct-electrical-cable-tray-conduit)
- [Straight duct airflow calculations (ASHRAE duct design)](https://studylib.net/doc/25535778/ashrae-duct-design)
- [Duct pressure loss calculation](https://www.cky.com.tw/en/insights/duct-pressure-loss-calculation)
- [Hazen-Williams equation](https://en.wikipedia.org/wiki/Hazen%E2%80%93Williams_equation)
- [Engineering ToolBox: Hazen-Williams](https://www.engineeringtoolbox.com/hazen-williams-water-d_797.html)
- [Hazen-Williams C coefficients](https://hydraulic-calculator.com/guides/hazen-williams-coefficients-table)
