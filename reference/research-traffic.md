# Research: traffic and pedestrians around the site (V171)

The plan's V171 (`plan-v167-v170.md`): cars on V166's street graph by IDM car following, signals where
OpenStreetMap maps them, pedestrians on the sidewalks crossing on green, drawn with V170's clock. Researched
to `research-protocol.md` from 2026-10-24, while V169's and V170's checks ran (the owner: never idle on long
checks). Every source was read as text in a folder of its own in the session's scratch; nothing downloaded
was run. **In progress:** the sections below say what is read so far and what is still open.

## 1. Car following: the Intelligent Driver Model

| Fact | Source | Read | Level |
|---|---|---|---|
| The IDM's acceleration: a free-road term a(1 - (v/v0)^delta) less a braking term a(s*/s)^2, where the desired gap s* = s0 + s1 sqrt(v/v0) + T v + v dv / (2 sqrt(a b)), dv the approach rate to the car ahead | Treiber, Hennecke and Helbing, "Congested traffic states in empirical observations and microscopic simulations", Phys. Rev. E 62, 1805 (2000); the authors' version, arXiv cond-mat/0002177 v2, https://arxiv.org/abs/cond-mat/0002177 | section II, equations (6) and (7) | P (the authors' own version of the published paper) |
| Its parameters on a German freeway (Table I): v0 120 km/h, T 1.6 s, a 0.73 m/s^2, b 1.67 m/s^2, delta 4, s0 2 m, s1 0, length 5 m; b "consistent with empirical investigations"; delta 4 used throughout | the same | Table I (page 29), section III | P, for a freeway |
| The authors' own browser simulator (traffic-simulation.de) sets other starting values for its demonstrations (v0 30 m/s, T 1.4 s, a 0.3 m/s^2, b 3 m/s^2, s0 2 m), each on a slider; its IDM adds a little random acceleration and caps braking at 18 m/s^2 | movsim/traffic-simulation-de, `js/models.js` and `js/control_gui.js`, https://github.com/movsim/traffic-simulation-de | the files, as text | S (an implementation's demonstration settings, not a calibration); GPL-3.0, so ideas only, nothing taken |

| The enhanced IDM's paper repeats the model (equations 2.1, 2.2) with its own Table 1: a car at 120 km/h, delta 4, T 1.5 s, s0 2.0 m, a 1.4 m/s^2, b 2.0 m/s^2; a truck at 85 km/h, T 2.0 s, s0 4.0 m, a 0.7 m/s^2, b 2.0 m/s^2 (freeway simulations); it calls the IDM fit "for all velocities in freeway traffic as well as city traffic" | Kesting, Treiber and Helbing, "Enhanced intelligent driver model to access the impact of driving strategies on traffic capacity", Phil. Trans. R. Soc. A 368 (2010); arXiv 0912.3613 v1, https://arxiv.org/abs/0912.3613 | section 2(a), Table 1 | P (the authors' version) |
| SUMO's vehicle classes' defaults: a passenger car 5 m by 1.8 m, minimum gap 2.5 m, accel 2.6 m/s^2, decel 4.5 m/s^2; a delivery van 6.5 m; a truck 7.1 m, accel 1.3, decel 4; a city bus 12 m, accel 1.2, decel 4; a pedestrian 5 km/h desired, 0.215 by 0.478 m; a cycle 20 km/h desired. SUMO says these accel and decel are "convenient" values for its default (Krauss) model and should be revisited for another; its IDM takes delta 4 and a 0.25 s internal step | Eclipse SUMO's documentation, `docs/web/docs/Vehicle_Type_Parameter_Defaults.md` and `Definition_of_Vehicles, Vehicle Types, and Routes.md`, https://github.com/eclipse-sumo/sumo | the tables, as text | S (an implementation's documented defaults, each footnoted to its own source, not read); EPL-2.0 |

| A red light, in the IDM's authors' simulator, is a standing "vehicle" placed across every lane at the light's position, so the car-following model alone brings the cars to a stop behind it; green removes it | movsim/traffic-simulation-de, `js/road.js`, `road.prototype.changeTrafficLight` | the function, as text | S (an implementation's method); GPL-3.0, the method only |
| On amber, SUMO's cars "start to decelerate if far away from the junction, otherwise they pass" | SUMO's `Traffic_Lights.md`, the signal states' table | the row for y | S (an implementation's behaviour) |

| Lane changes, MOBIL: a change is safe if the new follower's acceleration after it stays above -b_safe, and worth it if the driver's own gain plus p times the gains (or losses) of the new and old followers exceeds a threshold; p the politeness (0 to 1). With the IDM: threshold 0.1 m/s^2, b_safe 4 m/s^2 (well below the about 9 m/s^2 a car can brake on a dry road), a keep-right bias 0.3 m/s^2 for European rules; the values depend on the car-following model | Kesting, Treiber and Helbing, "MOBIL: General Lane-Changing Model for Car-Following Models", the authors' manuscript for the Transportation Research Board, https://mtreiber.de/publications/MOBIL_TRB.pdf | sections 2.1, 2.2, Table 1 | P (the authors' manuscript) |

My memory of a "city" parameter set in the 2010 paper was wrong: it has none. Nothing remembered goes in
without its source.

Searched for a city calibration (2026-10-24): the 2025 review of the IDM (Zhou, Zheng, Tian, Jiang and Zhang,
"Twenty-Five Years of the Intelligent Driver Model", arXiv 2506.05909, read as text) surveys calibration methods
but gives no table of city values; the freeway calibrations it cites (Kurtc and Treiber, NGSIM I-80) are a freeway's.
A Shanghai study of naturalistic driving reports urban drivers keeping slightly longer time gaps than on freeways;
only its summary page was seen (U, not used).

**Open:** values for city streets (the papers' are a freeway's), from a calibration read at its source; and how
the IDM approaches a red signal or a stop line (a standing "vehicle" at the line is the usual way; to read in a
documented implementation).

## 2. Signals

| Fact | Source | Read | Level |
|---|---|---|---|
| The yellow change interval's and the red clearance interval's durations are set by engineering practice; a yellow should last 3 to 6 s, the longer at higher speeds; a red clearance should not exceed 6 s (but at a one-lane two-way facility or an exceptionally wide intersection); neither varies cycle by cycle within a timing plan | FHWA, Manual on Uniform Traffic Control Devices, 11th Edition (December 2023), Section 4F.17, https://mutcd.fhwa.dot.gov/ | Part 4's PDF, the section's text (page 708), kept from V169's reading | P |
| The change period (yellow plus red clearance) by Kell and Fullerton: CP = [t + 1.47 v / (2 (a + 32.2 g))] + [(W + Lv) / (1.47 v)], v in mph, W the intersection's width and Lv a vehicle's length in feet; t 1.0 s, a 10 ft/s^2 and Lv 20 ft "often cited"; under the restrictive yellow rule the yellow may be the whole of it, under the permissive rule the first term, at least 3.0 s, with any red clearance from the second | FHWA, Traffic Signal Timing Manual (FHWA-HOP-08-024, 2008), chapter 5, https://ops.fhwa.dot.gov/publications/fhwahop08024/chapter5.htm | section 5.3, Equation 5-2 and its text | P, in the 2008 edition |
| Typical minimum greens for driver expectancy (Table 5-3): a major arterial through phase 10 to 15 s (over 40 mph) or 7 to 15 s; a minor arterial 4 to 10 s; collector, local or driveway 2 to 10 s; a left turn 2 to 5 s. Pedestrian clearance time = crossing distance / walking speed | the same | Tables 5-3 and 5-9 | P, in the 2008 edition |
| SUMO's generated signal programs: a fixed cycle of 90 s, the green split equally between the main phases (31 s each at a plain four-arm junction), every green followed by a yellow computed from the approaches' top speed, no all-red unless asked; below 70 km/h a left turn runs with the oncoming through traffic and yields; actuated programs vary each green from 5 to 50 s | Eclipse SUMO's documentation, `docs/web/docs/Simulation/Traffic_Lights.md`, "Automatically Generated TLS-Programs" | the section, as text | S (an implementation's defaults); EPL-2.0 |
| The manual's second edition (NCHRP Report 812, 2015) | The National Academies Press, https://nap.nationalacademies.org/catalog/22097 | its page answered; the PDF behind its download page did not come through | not read: the 2008 edition's values are used and its edition said |

**Open:** the second edition's changes to these; cycle length's range for a fixed-time plan; the walk interval
and pedestrian clearance from the 11th Edition's Chapter 4I (V169 read 4I.06's walking speeds).

## 3. Pedestrians

| Fact | Source | Read | Level |
|---|---|---|---|
| The social force model: a pedestrian accelerates toward a desired velocity within a relaxation time and is pushed by exponential repulsions from others and from walls. Its simulations take the desired speeds as Gaussian, mean 1.34 m/s, standard deviation 0.26 m/s (citing Henderson's measurements), capped at 1.3 times each one's own; relaxation time 0.5 s; V0 2.1 m^2/s^2, sigma 0.3 m; walls U0 10 m^2/s^2, R 0.2 m; a 200 degree field of view | Helbing and Molnar, "Social force model for pedestrian dynamics", Phys. Rev. E 51, 4282 (1995); arXiv cond-mat/9805244 v1, https://arxiv.org/abs/cond-mat/9805244 | section III, the simulations' values (pages 7 and 8) | P (the authors' version); the 1.34 m/s mean is S, cited to Henderson, not read |
| The MUTCD's walking speeds for the pedestrian clearance time (4I.06) | V169's registry record `mutcd.walk`, read at the MUTCD 11th Edition with Revision 1 | (V169) | P |

**Open:** whether sidewalk pedestrians need forces at all at the site's scale (they mostly walk single file along
V166's sidewalks) or only a desired speed, a gap and a wait at the crossing; Henderson's measurements themselves.

## 4. Demand

| Fact | Source | Read | Level |
|---|---|---|---|
| K is the share of the AADT in the design hour, the year's 30th-highest hour (DHV = K x AADT); D the share of that hour in the heavier direction (D > 0.5; DDHV = D x DHV). Delaware's values by traffic pattern group (K and D in percent, for 2023): group 1, 9.3 and 55.4; 2, 11.1 and 56.9; 4, 14.3 and 60.7; 5, 11.8 and 57.2; 7, 13.5 and 59.1; 8, 11.7 and 55.9. Single-unit and combination trucks: 7.9% and 4.8% (group 1), 4.2% and 2.3% (2), 4.4% and 0.8% (8) | Delaware Department of Transportation, Growth and K&D Factors (2024 traffic counts), https://deldot.gov/Publications/manuals/traffic_counts/pdfs/2024/ | the two pages | P, for Delaware |
| Florida's Standard K factors (Figure 2.4), replacing K30 because urbanized roads cannot be designed cost-effectively for the 30th-highest hour: arterials and highways 9.0% of AADT in urbanized areas (large, other, transitioning) and urban areas (typical weekday peak hour), 9.5% rural (the 100th-highest hour); freeways 8.0 to 9.0% in the large urbanized areas, 9.0 in other urbanized areas, 10.5 urban and rural; 7.5% in approved multimodal transportation districts | Florida Department of Transportation, Project Traffic Forecasting Handbook (January 2014), section 2.6.2.1, https://www.fdot.gov/docs/default-source/statistics/trafficdata/PTF.pdf | page 2-33, the figure read as an image; the proxy cut the file at 4,884,126 bytes and a range request fetched the rest | P, for Florida (2014) |
| The typical AADT of each functional class, rural and urban | FHWA, Highway Functional Classification (2023), Tables 3-5 and 3-6: V167's registry record `fhwa.fc` | (V164, V167) | P |

Two states read: Delaware's design hour (the 30th-highest) runs from 9.3 to 14.3%; Florida's standard peak hour is
9.0% on urban arterials. A weekday peak hour near a site is the one the simulation wants, so Florida's 9% is the
closer reading for a city street; the choice is the owner's (below).

**Open:** the share
of turns at a junction (no free source yet); the lot's own trips (no free trip-generation table: ITE's is sold).

## 5. What the app has (read 2026-10-24)

- **The crossings' controls (V166, `bimMvCross`):** each node OpenStreetMap tags `highway=traffic_signals`,
  `highway=stop` or `highway=crossing`, or any `crossing`, within the movement window, read into flags: signals
  (`traffic_signals` on the node or its crossing, or `crossing:signals=yes`), an all-way stop (`stop=all`) or a stop
  on one approach, a marked crossing, an island. The request is part of V166's one Overpass query (`bimMvQuery`).
- **The streets (V166, `bimMvOf`):** kept with the site as arrays: the nodes' plan coordinates (`x`, `z`), each way
  as its tag set's index then its node indices (`w`), the tag sets (`t`); each way's speed and lanes read by
  `bimMvSpeed` and `bimMvLanes` (OpenStreetMap's maxspeed and lanes, else the registry's class defaults,
  `app.roads`), one-way and parking by side; the walk network (V161).
- **Data test (2026-10-24):** Overpass refused twice at 20:46 UTC (the tunnel closed mid-exchange, a transient
  network failure, and the mirror timed out); to retry, for the signals mapped near a test site and their tags.
- **The clock (V170):** one animation clock, Play, Pause and Stop, still on paper; a fixed simulation step
  (the plan's 0.2 s) runs inside it.

## 6. Still to research

- City IDM values; the stop line and the signal in the car-following model; lane changes (MOBIL, the same
  authors) or none.
- Turning at junctions; the demand (the plan's K factor on FHWA's AADT ranges, V164's registry); the lot's own
  trips (no free trip-generation table).
- Pedestrians: walking speeds (V169's MUTCD 4I.06 record), crossing on WALK, the sidewalks from V166.
- OpenStreetMap's signal tags as V166 keeps them, and what is mapped near a test site.
- Open implementations read as text: SUMO's car-following and junction documentation (EPL-2.0).
- The app: V166's street graph, V152's instanced drawing, V170's clock.
- The owner's decisions, asked together at the end.
