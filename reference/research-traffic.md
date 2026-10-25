# Research: traffic and pedestrians around the site (V171)

The plan's V171 (`plan-v167-v170.md`): cars on V166's street graph by IDM car following, signals where
OpenStreetMap maps them, pedestrians on the sidewalks crossing on green, drawn with V170's clock. Researched
to `research-protocol.md` from 2026-10-24, while V169's and V170's checks ran (the owner: never idle on long
checks). Every source was read as text in a folder of its own in the session's scratch; nothing downloaded
was run. Research done 2026-10-24; the owner's decisions are in section 6.

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
| Unsignalled junctions in SUMO: a junction's type says who yields (priority: the minor road waits for the major; priority_stop: the minor road always stops first; allway_stop; right_before_left). Right of way by default goes to the two incoming edges ranked highest by priority, then speed, then lanes; every other approach is minor. A car without right of way slows until a visibility distance, then looks for higher-priority traffic and brakes or goes; it keeps a time gap of at least 1 s to a priority car not yet in the junction (`jmTimegapMinor`); it waits 1 m before a signal's stop line, at the line on a minor road; a stop sign is at least one step's stop (`jmStopSignWait`); it keeps 10 m from a pedestrian walking toward its path (`jmCrossingGap`) | SUMO's documentation, `Simulation/Intersections.md`, `Networks/PlainXML.md` (node types, Right-of-way) and the junction model parameters' table in `Definition_of_Vehicles, Vehicle Types, and Routes.md` | the sections and the table, as text | S (an implementation's rules and defaults); EPL-2.0, the rules only |

| City traffic: three drivers' radar trajectories in Stuttgart (1995, an afternoon peak hour, a fairly straight one-lane road, standstills at traffic lights; 250, 400 and 300 s), the IDM fitted to each by a genetic algorithm. With the mixed error measure: T 1.12, 1.43 and 1.30 s; s0 2.33, 2.82 and 1.52 m; a 1.23, 0.977 and 1.56 m/s^2; b 3.20, 0.994 and 0.633 m/s^2; v0 only bounded from below (58 km/h for the third, the most it reached; the others never drove free); errors 11 to 29%. Intra-driver variability accounts for much of the error | Kesting and Treiber, "Calibrating car-following models using trajectory data: methodological study", Transportation Research Record 2088 (2008); arXiv 0803.4063 v1, https://arxiv.org/abs/0803.4063 | the data's description (page 2), Table 1 and its discussion (page 7) | P (the authors' version) |
| The authors' own guidance: for city traffic adapt the desired speed and leave the others essentially unchanged; realistic T from 0.8 to 2 s (German driving schools teach 1.8 s), a 0.8 to 2.5 m/s^2, b around 2 m/s^2; s0 kept at standstill, in queues at red lights too. A red light or a stop sign is a standing virtual vehicle of length zero at the stop line, removed on green; a free road is a gap of 1000 m. The ballistic update (speed by a dt, position by v dt + a dt^2 / 2); any step below 0.5 s gives essentially the same result; a car that would go below zero speed within a step stops where it would and stays, and a gap a little under s0 is kept, not driven backwards from | Treiber, "The Intelligent-Driver Model and its Variants", https://traffic-simulation.de/info/info_IDM.html | the page, as text (2026-10-24) | P (the model's author on his model) |

| Lane changes, MOBIL: a change is safe if the new follower's acceleration after it stays above -b_safe, and worth it if the driver's own gain plus p times the gains (or losses) of the new and old followers exceeds a threshold; p the politeness (0 to 1). With the IDM: threshold 0.1 m/s^2, b_safe 4 m/s^2 (well below the about 9 m/s^2 a car can brake on a dry road), a keep-right bias 0.3 m/s^2 for European rules; the values depend on the car-following model | Kesting, Treiber and Helbing, "MOBIL: General Lane-Changing Model for Car-Following Models", the authors' manuscript for the Transportation Research Board, https://mtreiber.de/publications/MOBIL_TRB.pdf | sections 2.1, 2.2, Table 1 | P (the authors' manuscript) |

My memory of a "city" parameter set in the 2010 paper was wrong: it has none. Nothing remembered goes in
without its source.

Searched for a city calibration (2026-10-24): the 2025 review of the IDM (Zhou, Zheng, Tian, Jiang and Zhang,
"Twenty-Five Years of the Intelligent Driver Model", arXiv 2506.05909, read as text) surveys calibration methods
but gives no table of city values; the freeway calibrations it cites (Kurtc and Treiber, NGSIM I-80) are a freeway's.
A Shanghai study of naturalistic driving reports urban drivers keeping slightly longer time gaps than on freeways;
only its summary page was seen (U, not used).

City values, then: the calibration's ranges agree with the author's advice (T about 1.1 to 1.4 s, s0 1.5 to 3 m, a
about 1 to 1.6 m/s^2, b spread widely by driver), and v0 is the street's speed. A red light and a stop line are a
standing car at the line, by the model's author. **Closed** (2026-10-24).

## 2. Signals

| Fact | Source | Read | Level |
|---|---|---|---|
| The yellow change interval's and the red clearance interval's durations are set by engineering practice; a yellow should last 3 to 6 s, the longer at higher speeds; a red clearance should not exceed 6 s (but at a one-lane two-way facility or an exceptionally wide intersection); neither varies cycle by cycle within a timing plan | FHWA, Manual on Uniform Traffic Control Devices, 11th Edition (December 2023), Section 4F.17, https://mutcd.fhwa.dot.gov/ | Part 4's PDF, the section's text (page 708), kept from V169's reading | P |
| The change period (yellow plus red clearance) by Kell and Fullerton: CP = [t + 1.47 v / (2 (a + 32.2 g))] + [(W + Lv) / (1.47 v)], v in mph, W the intersection's width and Lv a vehicle's length in feet; t 1.0 s, a 10 ft/s^2 and Lv 20 ft "often cited"; under the restrictive yellow rule the yellow may be the whole of it, under the permissive rule the first term, at least 3.0 s, with any red clearance from the second | FHWA, Traffic Signal Timing Manual (FHWA-HOP-08-024, 2008), chapter 5, https://ops.fhwa.dot.gov/publications/fhwahop08024/chapter5.htm | section 5.3, Equation 5-2 and its text | P, in the 2008 edition |
| Typical minimum greens for driver expectancy (Table 5-3): a major arterial through phase 10 to 15 s (over 40 mph) or 7 to 15 s; a minor arterial 4 to 10 s; collector, local or driveway 2 to 10 s; a left turn 2 to 5 s. Pedestrian clearance time = crossing distance / walking speed | the same | Tables 5-3 and 5-9 | P, in the 2008 edition |
| SUMO's generated signal programs: a fixed cycle of 90 s, the green split equally between the main phases (31 s each at a plain four-arm junction), every green followed by a yellow computed from the approaches' top speed, no all-red unless asked; below 70 km/h a left turn runs with the oncoming through traffic and yields; actuated programs vary each green from 5 to 50 s | Eclipse SUMO's documentation, `docs/web/docs/Simulation/Traffic_Lights.md`, "Automatically Generated TLS-Programs" | the section, as text | S (an implementation's defaults); EPL-2.0 |
| The WALK interval by setting (Table 5-8): 10 to 15 s where pedestrians are many (a school, a central business district, a stadium); 7 to 10 s with typical volumes and a longer cycle; 7 s with a shorter cycle; 4 s where there are almost none; where older pedestrians are present, the distance to the road's centre at 3.0 ft/s | the same | Table 5-8 | P, in the 2008 edition |
| Cycle length: Webster's optimum for an isolated junction, C = (1.5 L + 5) / (1.0 - Y), C in seconds, L the time lost per cycle, Y the critical lane volumes over the saturation flow summed over the phases (Equation 6-1, read as its image); the HCM's estimate C = L / (1 - min(CS, RS) / RS) (Equation 6-2), CS the critical sum, RS the reference sum; the cycle grows toward a maximum the jurisdiction sets ("such as 150 seconds"), the least suggested 60 s; the plotted ranges run from 30 s at light demand to 180 s near capacity. An agency's harmonic cycles by street (Table 6-1, Harris County, Texas): a minor arterial 60, 70, 80 or 90 s with a major arterial at 90, 105, 120 or 135 s | FHWA, Traffic Signal Timing Manual (2008), chapter 6, https://ops.fhwa.dot.gov/publications/fhwahop08024/chapter6.htm | section 6.4's cycle length methods, Equations 6-1 and 6-2 (images), Figures 6-19 and 6-20's descriptions, Table 6-1 | P, in the 2008 edition |
| The manual's second edition (NCHRP Report 812, 2015) | The National Academies Press, https://nap.nationalacademies.org/catalog/22097 | its page answered; the PDF behind its download page did not come through | not read: the 2008 edition's values are used and its edition said |

A fixed-time plan, then: a cycle of at least 60 s, its greens split to the approaches' volumes by Webster's
logic or set evenly as SUMO does, each green at least the manual's minimum and long enough for WALK plus the
pedestrian clearance at 3.5 ft/s, each change interval by Kell and Fullerton's period. **Open:** the second
edition's changes to these (not read).

## 3. Pedestrians

| Fact | Source | Read | Level |
|---|---|---|---|
| The social force model: a pedestrian accelerates toward a desired velocity within a relaxation time and is pushed by exponential repulsions from others and from walls. Its simulations take the desired speeds as Gaussian, mean 1.34 m/s, standard deviation 0.26 m/s (citing Henderson's measurements), capped at 1.3 times each one's own; relaxation time 0.5 s; V0 2.1 m^2/s^2, sigma 0.3 m; walls U0 10 m^2/s^2, R 0.2 m; a 200 degree field of view | Helbing and Molnar, "Social force model for pedestrian dynamics", Phys. Rev. E 51, 4282 (1995); arXiv cond-mat/9805244 v1, https://arxiv.org/abs/cond-mat/9805244 | section III, the simulations' values (pages 7 and 8) | P (the authors' version); the 1.34 m/s mean is S, cited to Henderson, not read |
| The MUTCD's walking speeds for the pedestrian clearance time (4I.06) | V169's registry record `mutcd.walk`, read at the MUTCD 11th Edition with Revision 1 | (V169) | P |
| The pedestrian intervals: WALK while pedestrians may leave the curb, at least 7 s (as short as 4 s where volumes allow); then the flashing DON'T WALK change interval, then a steady DON'T WALK buffer of at least 2 s before any conflicting vehicles go; change plus buffer at least the clearance time, the crossing at 3.5 ft/s to the far side (up to 4 ft/s with an extended push button; slower where slower walkers routinely cross); WALK plus clearance enough to cross from 6 ft behind the curb at 3 ft/s; conflicting vehicles held on red throughout | FHWA, MUTCD 11th Edition (December 2023), Section 4I.06, paragraphs 1 to 14 | Part 4's text, pages 722 to 724 | P |

| SUMO's default pedestrian model ("striping"): each sidewalk, crossing and walking area divided across its width into stripes of 0.65 m; a walker advances as fast as it can without coming too close to the one ahead in its stripe, moving sideways to another stripe when it must (oncoming walkers evade to the right), its speed cut by a random fraction up to 0.2 of its maximum (dawdling); walkers wait at a crossing in a wide queue; on crossings and walking areas a third of the width is kept for those coming the other way; a walker stuck 300 s (10 s on a crossing) moves on through the others at a quarter speed | SUMO's documentation, `Simulation/Pedestrians.md`, "Model striping" and "Jamming" | the sections, as text | S (an implementation's model); EPL-2.0, the method only |

So a pedestrian at the site's scale need not feel forces: a desired speed, a lateral stripe on the sidewalk, a gap
to the one ahead and a wait at the crossing is the established simple model, with the social force model kept for
crowds. Which to build is the owner's (below). **Open:** Henderson's measurements themselves.

## 4. Demand

| Fact | Source | Read | Level |
|---|---|---|---|
| K is the share of the AADT in the design hour, the year's 30th-highest hour (DHV = K x AADT); D the share of that hour in the heavier direction (D > 0.5; DDHV = D x DHV). Delaware's values by traffic pattern group (K and D in percent, for 2023): group 1, 9.3 and 55.4; 2, 11.1 and 56.9; 4, 14.3 and 60.7; 5, 11.8 and 57.2; 7, 13.5 and 59.1; 8, 11.7 and 55.9. Single-unit and combination trucks: 7.9% and 4.8% (group 1), 4.2% and 2.3% (2), 4.4% and 0.8% (8) | Delaware Department of Transportation, Growth and K&D Factors (2024 traffic counts), https://deldot.gov/Publications/manuals/traffic_counts/pdfs/2024/ | the two pages | P, for Delaware |
| Florida's Standard K factors (Figure 2.4), replacing K30 because urbanized roads cannot be designed cost-effectively for the 30th-highest hour: arterials and highways 9.0% of AADT in urbanized areas (large, other, transitioning) and urban areas (typical weekday peak hour), 9.5% rural (the 100th-highest hour); freeways 8.0 to 9.0% in the large urbanized areas, 9.0 in other urbanized areas, 10.5 urban and rural; 7.5% in approved multimodal transportation districts | Florida Department of Transportation, Project Traffic Forecasting Handbook (January 2014), section 2.6.2.1, https://www.fdot.gov/docs/default-source/statistics/trafficdata/PTF.pdf | page 2-33, the figure read as an image; the proxy cut the file at 4,884,126 bytes and a range request fetched the rest | P, for Florida (2014) |
| The typical AADT of each functional class, rural and urban | FHWA, Highway Functional Classification (2023), Tables 3-5 and 3-6: V167's registry record `fhwa.fc` | (V164, V167) | P |

Two states read: Delaware's design hour (the 30th-highest) runs from 9.3 to 14.3%; Florida's standard peak hour is
9.0% on urban arterials. A weekday peak hour near a site is the one the simulation wants, so Florida's 9% is the
closer reading for a city street; the choice is the owner's (below).

| Turns at a junction from link volumes: an initial estimate of the turning shares, then the turning matrix balanced alternately by rows (inflows) and columns (outflows) to the links' volumes, six to ten iterations (Furness's method, modified for intersections by Mekky). The shares to start from come from counts, similar junctions or the land use around; none are given. A sketch method for two-way volumes takes each approach's volume as the stand-in for what lies beyond it, the turns following the approaches' weights; its example assumes at most 20% of the inflow turns, "on the basis of conditions at similar intersections" | Pedersen and Samdahl (JHK and Associates), NCHRP Report 255, Highway Traffic Data for Urbanized Area Project Planning and Design (TRB, December 1982), Chapter 8, https://onlinepubs.trb.org/Onlinepubs/nchrp/nchrp_rpt_255.pdf | Chapter 8, pages 110 to 118, as text | P (1982; its successor, NCHRP Report 765 of 2014, is behind a download form, not read) |

So no free table of turning shares exists for a junction without counts; the method is a matrix balanced to the
streets' volumes from a first guess. The streets' volumes here are the registry's typical AADT by class (`fhwa.fc`).

| A site's own vehicle trips, from counts at every driveway of four to seven sites of a use, up to seven days (Table 1, driveway rates, with the AM and PM peak hours' shares of the day and their in:out splits): apartments 8 trips a dwelling a day under 20 dwellings an acre, 6 over it, AM 8% (2:8), PM 10% or 9% (7:3); single family, urbanized, 9 a dwelling, 8% (2:8) and 10% (7:3); a commercial office Ln(T) = 0.756 Ln(x) + 3.95 (T trips a day, x thousand sq ft), AM 13% (9:1), PM 14% (2:8); a single-tenant office 10 a thousand sq ft, 15% (9:1) and 15% (1:9); a neighbourhood shopping centre 120 a thousand sq ft, 4% (6:4) and 11% (5:5); strip retail 40, 3% (6:4) and 9% (5:5); a supermarket 150, 4% (7:3) and 10% (5:5). Downtown (Centre City, Table 5) the rates are lower, for transit, density, walking and parking's cost: apartments 5 (under 20 an acre) and 4 a dwelling, a commercial office 0.85 (under 100,000 sq ft) or 0.81 times the formula's trips, strip retail 18, a supermarket 60. The rates come from the city's, SANDAG's and ITE's studies, local data where possible | City of San Diego, Trip Generation Manual (revised May 2003), https://www.sandiego.gov/sites/default/files/legacy/planning/documents/pdf/trans/tripmanual.pdf | the introduction, Table 1 (residential, office, retail rows and notes) and Table 5, as text | P, for San Diego (2003), its sources cited (SANDAG's Traffic Generators, ITE's 5th and 6th editions) |

A free table of a site's trips exists, then, in a city's own manual: San Diego's, of 2003, with peak shares and
directions. It is one region's and old; the owner chooses whether the lot's trips come from it (by V131's usages and
their areas), from a number they give, or not at all (below).

## 5. What the app has (read 2026-10-24)

- **The crossings' controls (V166, `bimMvCross`):** each node OpenStreetMap tags `highway=traffic_signals`,
  `highway=stop` or `highway=crossing`, or any `crossing`, within the movement window, read into flags: signals
  (`traffic_signals` on the node or its crossing, or `crossing:signals=yes`), an all-way stop (`stop=all`) or a stop
  on one approach, a marked crossing, an island. The request is part of V166's one Overpass query (`bimMvQuery`).
- **The streets (V166, `bimMvOf`):** kept with the site as arrays: the nodes' plan coordinates (`x`, `z`), each way
  as its tag set's index then its node indices (`w`), the tag sets (`t`); each way's speed and lanes read by
  `bimMvSpeed` and `bimMvLanes` (OpenStreetMap's maxspeed and lanes, else the registry's class defaults,
  `app.roads`), one-way and parking by side; the walk network (V161).
- **Data test (2026-10-24):** overpass-api.de refused again at 23:13 UTC (the tunnel to the egress proxy closed
  mid-exchange), private.coffee timed out, mail.ru's mirror answered 504; overpass.osm.ch (Switzerland only) answered.
  Within 400 m of Paradeplatz, Zurich: 27 `highway=traffic_signals` nodes and 37 crossings tagged
  `crossing=traffic_signals`, 19 signals with `traffic_signals:direction` (forward or backward, the approach they
  control), 4 `highway=stop` and 6 `highway=give_way`; 135 crossings, 56 of them zebras; 244 sidewalks drawn as their
  own ways (`footway=sidewalk`, 46 streets `sidewalk=separate`); lanes on 89 ways, `turn:lanes` on 26; maxspeed 30 on
  67 ways and 50 on 54. No timing anywhere: OpenStreetMap maps where a signal is and which way it faces, never its
  plan, so every cycle the simulation runs is assumed and said.
- **What V166 keeps of these:** the crossings' flags (signals, stop, all-way stop, marked, island), the streets' lanes,
  one-way, speeds and sidewalks (`BIM_MV_KEYS`); the walk network walks the sidewalks without drawing them. Not kept:
  `highway=give_way`, a signal's direction, `turn:lanes`.
- **The clock (V170):** one animation clock, Play, Pause and Stop, still on paper; a fixed simulation step
  (the plan's 0.2 s) runs inside it.
- **Drawing many moving things (V152, V153, read 2026-10-24):** the scene is chunks of merged triangles, each vertex
  tagged with its object's slot, and a table of eight floats a slot (`bimGbPut`): the object's position, its
  transparency (or hidden), its colour and its selection; only the rows that change are sent to the GPU, in both
  WebGL and WebGPU. A car can therefore move by its row alone, with no chunk rebuilt; it cannot turn, the table
  having no heading, so a car that turns needs a heading added to the table and both engines' shaders, or is drawn
  on the overlay as V170's motions are. V169's vehicles (P, SU-30, CITY-BUS) are meshes built from their
  parameters.

## 6. What the research supports, and what is the owner's

Already the owner's (`research-valdrada.md`, 2026-10-19): valdrada's methods rewritten inside the app (MIT,
credited), only the site's streets, agents as typed arrays, light by design. With what is read above:

- **Cars** by the IDM on V166's street graph, its values a standards record with its source and edition, the
  desired speed the street's own (`bimMvSpeed`); a fixed step under 0.5 s inside V170's clock, by the ballistic
  update and the author's rule for stopping; a red light or a stop line a standing car at the line; a minor road
  yields to a major by SUMO's ranking (priority, then speed, then lanes), keeping a gap of 1 s.
- **Lane changes** by MOBIL where a direction has two lanes or more (its values from its paper), none on one lane.
- **Pedestrians** by a desired speed on the sidewalks, a stripe across their width, a gap to the one ahead and a
  wait at the crossing (SUMO's striping model), not by social forces: the owner's light-by-design choice.
- **Signals** only where OpenStreetMap maps them, on the side `traffic_signals:direction` gives where it is
  mapped; every timing assumed and said, OpenStreetMap having none.
- **Drawing**: the table of V152 gains a heading, so a car turns in 3D on both engines; in plan, rectangles and
  dots on the overlay.

**The owner's decisions** (asked together, 2026-10-24):
1. The signal plan: valdrada's one 40 s cycle everywhere (15 s green, 3 s amber, 2 s all red), or the timing
   manual's practice, each junction's own: a cycle of at least 60 s split by Webster's logic to the approaches'
   volumes, amber by Kell and Fullerton, and each green long enough for WALK (7 s) and the crossing at 3.5 ft/s
   (MUTCD 4I.06). WALK and the crossing of a 15 m street take 21 s (7 + 14), more than valdrada's 20 s of
   green, amber and all red together.
2. The cars' values: the city calibration's middle values (Stuttgart, 2008: T 1.30 s, s0 2.33 m, a 1.23 m/s^2,
   b 0.994 m/s^2), valdrada's (T 1.15 s, s0 2.2 m, a 1.9, b 2.6), or the authors' standard car with the street's
   speed (T 1.5 s, s0 2 m, a 1.4, b 2.0, Kesting 2010).
3. The streets' traffic: each street's typical AADT by class (`fhwa.fc`) at Florida's standard K (9%, the weekday
   peak hour in urban areas), or at Delaware's design hour (9.3 to 14.3%); turns at each junction by NCHRP 255's
   balancing, from the exits' volumes, or split evenly.
4. The lot's own trips: San Diego's rates by V131's usages and areas (free, read; one region's, 2003), from the
   parking spaces at an assumed rate (the earlier plan, when no free table was known), a number the owner gives,
   or none.

**The owner's answers** (2026-10-25, the start of V171's session), each as the research proposed:
1. **Each junction's own signal plan:** a cycle of at least 60 s split by Webster's logic to the approaches'
   volumes, amber by Kell and Fullerton, each green long enough for WALK (7 s) and the crossing at 3.5 ft/s
   (MUTCD 4I.06); not valdrada's one 40 s cycle.
2. **The authors' standard car** (Kesting, Treiber and Helbing 2010: T 1.5 s, s0 2 m, a 1.4 m/s^2, b 2.0 m/s^2,
   delta 4) with the street's own speed, as the model's author advises for city traffic.
3. **The streets' traffic** at each street's typical AADT by class (`fhwa.fc`) times Florida's standard K, 9%
   (the weekday peak hour in urban areas); turns at each junction by NCHRP 255's balancing to the exits'
   volumes.
4. **The lot's own trips** by San Diego's Trip Generation Manual (2003), from V131's usages and their areas,
   with the table's peak shares and in:out splits; said on the layer as one region's rates of 2003.
