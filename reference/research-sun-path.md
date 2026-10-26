# The sun path, one clock (V171d research, 2026-10-26)

Research for V171d, after `reference/research-protocol.md`. Levels: **P** read in the primary source, **S** a
dependable secondary source (the gap said), **U** a pointer only, never in the code.

## The owner's request

The owner, 2026-10-25, with a screenshot of the app's sun paths in 3D and one of archiMap's sun diagram:

> sun path analysis is not coordinate the animation and the Sunpath diagram should coordinate with the shadow as it
> goes along ... throughout the dates. Visualization of the solar angle as moved in altitude, change over specific
> location; the correct calculation of the sun trajectory needs to follow this mathematically using the standard
> coordinate of the public NOAA solar algorithm. You need to check if our math is correct: the core mathematics formula
> is spherical to Cartesian coordinates, so you convert the calculated solar altitude alpha and the azimuth into the 3-D
> Cartesian coordinates X = R cos(alpha) sin(A), Y = R sin(alpha), Z = R cos(alpha) cos(A). ... I want to be able to
> have a drag board to change the latitude, longitude as well as the date and the time; update these numbers: solar
> altitude, solar azimuth. Also in our current model there isn't any mesh that's being generated according to the
> coordinates. The mesh can demonstrate the different temperature throughout the time ... different dates when the
> coordinates go throughout the sphere. ... on the right side when we access the site analysis I think we should break
> down the sun path analysis to show the winter solstice, summer [solstice] ... so that it becomes more professional.
> There should be a diagram too.

(Lightly cut; the spoken words' transcription mistakes mended: "Cortis" is Cartesian, "Asmer" azimuth.)

## 1. Is the math right?

**NOAA's Solar Calculator spreadsheet** (P; NOAA_Solar_Calculations_day, from gml.noaa.gov/grad/solcalc's
calculation details, read 2026-10-26, every column's formula). `bimSunCalc` (V107) is that spreadsheet formula for formula: the Julian day
and century (F, G), the Sun's geometric mean longitude and anomaly (I, J), the Earth's orbit eccentricity (K), the
equation of centre (L), the true and apparent longitude (M, P), the obliquity and its correction (Q, R), the
declination (T), the equation of time (V), the sunrise hour angle at 90.833 deg (W), the true solar time (AB), the hour
angle (AC), the zenith (AD), the elevation (AE), the refraction approximation (AF) and the azimuth (AH). The
spreadsheet's method is Meeus's (Astronomical Algorithms), as its own notes say.

NOAA's **General Solar Position Calculations** (P; `solareqns.pdf`, read 2026-10-26) is a shorter method from the
fractional year; it is less accurate and is not used.

**NREL's Solar Position Algorithm** (Reda and Andreas, NREL/TP-560-34302, 2008) is the reference a sun position is
held to. The report could not be fetched from here (nrel.gov answers the proxy 502, 2026-10-26); its worked example is
taken as pvlib's `tests/test_spa.py` transcribes it (S, an open implementation's test data, read 2026-10-26):
17 October 2003, 12:30:30 at UTC-7, 39.742476 N, 105.1786 W, 1830.14 m, 820 mbar, 11 deg C, delta T 67 s.

| | NREL SPA | the app (NOAA) | difference |
|---|---|---|---|
| topocentric elevation, no refraction | 39.872046 | 39.872074 | 0.00003 deg |
| elevation with refraction | 39.888378 | 39.891362 | 0.003 deg |
| azimuth from north | 194.340241 | 194.342583 | 0.0023 deg |

The refraction differs most: SPA's is Bennett's at the site's 820 mbar and 11 deg C, NOAA's an approximation for a
standard atmosphere. At a 30 m dome 0.003 deg is under 2 mm. V107's suite already holds the app to SPA at six places and
dates through pvlib 0.15.2 (elevation within 0.02 deg). **The math is right.**

## 2. From altitude and azimuth to the dome

The owner's formula, with alpha the altitude and A the azimuth from north: X = R cos(alpha) sin(A), Y = R sin(alpha),
Z = R cos(alpha) cos(A), Y up and Z north.

The app's axes are Y up and north on -Z, its plan turned by the site's true-north angle theta. `bimDgDome` (V164) is
the same formula in them, about the site's centre (cx, gy, cz):

    X = cx + R cos(alpha) sin(A + theta)
    Y = gy + R sin(alpha)
    Z = cz - R cos(alpha) cos(A + theta)

**Ladybug** (open implementation, read as text, `ladybug/sunpath.py`, `Sun._calculate_sun_vector`, AGPL, nothing
copied): the north vector (0, 1, 0) turned about X by the altitude and about Z by minus the azimuth, Z up, gives
(cos(alpha) sin(A), cos(alpha) cos(A), sin(alpha)) -- the same again. Every point is R from the centre.

## 3. What the owner saw: hours without their dots

In the owner's 3D screenshot "13h", "14h" and "15h" float between the paths. Two causes, both V164's:
- **A path's name sits on its highest point**, raised R x 0.05: on top of the hour dot nearest noon (13h, the site on
  daylight time), hiding it; in plan, raising a point does not move it on the screen at all.
- **The label placer moves a word a whole line up or down** (tries 0, -h, +h, -2h, +2h) when it meets another: an
  hour's label met the path's name and was put a line away from its dot.

The fix: the dots of labelled marks are places no word may cover; an hour's label tries beside its own dot only
(right, left, above, below) and is left out when none is free (the dot stays); a path's name goes along the path
between two hour dots, nearest noon first, shortened ("20 Mar, 22 Sep").

## 4. One clock for the sun, its paths and its shadows

V170 moves the time through the study's day only, and the dome's paths are the solstices' and the equinox's drawn when
the analysis ran. A study date that is none of them gave a sun moving along a path not drawn; a changed date, latitude
or time zone left the paths and "the sun now" as they were until Run again.

The design: the sun's elements follow what they are drawn from -- the place, the zone, the year, the moment -- as a run
would draw them, with no undo step (derived, like a cache); the clock's own day drawn as a path of its own with its
hours; the sun now with its angles drawn (the ray from the centre, the drop to the ground, the bearing on the ground,
the azimuth arc from true north, the altitude arc in the sun's vertical plane, labelled); the analemma, the sun at the
study's time through the year. Play goes **through the day** (V170's) or **through the year**: the date a day a step at
the study's time, the sun tracing the analemma, the day's path and the shadows following.

## 5. Time zones and daylight saving

**Open-Meteo** (P, its Historical Weather API page read 2026-10-26, and tested): "The requested timezone's UTC offset
at request time is returned as utc_offset_seconds and used for ISO 8601 timestamps and daily boundaries throughout the
response. Daylight saving time (DST) changes within the requested range are ignored." Tested from here on 2026-10-26
(New York still on daylight time): 8 to 10 March 2025 with `timezone=auto` came back at -14400 s for all 72 hours,
matching the GMT series shifted four hours on both sides of the 9 March change. So V164's "the time zone comes with the
climate" stored the offset of the day it was fetched: a New York site analysed in summer was UTC-4 all year, its winter
clock an hour off, and one analysed in winter UTC-5.

**ECMA-402** `Intl.DateTimeFormat` with an IANA `timeZone` (tested here in the bundled Chromium, 2026-10-26): ten zones,
New York's change at 02:00 on 8 March 2026 (01:30 at UTC-5, 03:30 at UTC-4), Kolkata's half hour, St John's and
Chatham's half and three-quarter hours, Phoenix without daylight saving, Casablanca's Ramadan hour (UTC+0 on 8 March
2026, UTC+1 either side), Dublin's winter hour, and an unknown zone's RangeError. The offset at a local time is found
by formatting the instant in the zone and comparing, three rounds (no `longOffset` needed, which older browsers lack).
A zone's **standard time** is the lower of its mid-January and mid-July offsets (Dublin's and Casablanca's daylight
saving, which the time zone database writes as negative, still give their standard time).

**Practice:** Ladybug's sun path takes a daylight saving period, none by default (standard time), and draws its
analemmas without it (P, `LB SunPath.py` and `sunpath.py`, read as text 2026-10-26). archiMap's card shows the UTC offset
"(Auto)" and "DST: Off (Auto)" (the owner's screenshot, not committed).

The design: the zone kept with the site (from the climate, `timezone=auto`); the UTC offset set from the zone's
standard time, not the fetch day's; **Daylight saving: Off** (standard time all year, Ladybug's default) or **Auto**
(each date's offset from the zone). The climate's hours stay in the offset they came in, which the temperature mesh
reads them by.

## 6. Temperature on the sun's dome

The owner asks for a mesh following the sun's coordinates, coloured by the temperature through the hours and dates.

**Practice:** Ladybug's sun path colours the hourly sun positions by any hourly data (temperature first), for an
analysis period (P, `LB SunPath.py`, its `data_` input, read as text). archiMap writes the average temperature in its
notes.

**Data:** the climate's year of hours (V159: ERA5 temperature at 2 m for the last full year, via Open-Meteo, CC BY
4.0), kept with the project (`A3D.site.climate.hourly.heat`), its hours local at the fetch day's offset.

**The design:** the band of the sky the sun crosses, between the winter and summer paths, divided by the hour and by
month (the 21st). Every place in that band is passed twice a year, once with the days lengthening and once shortening,
in different weather, so the mesh shows the half-year holding the clock's date (21 December to 21 June, or 21 June to
21 December), and Play through the year turns it at each solstice. A cell is the mean temperature at its hour over its
days; its colour is the climate board's eleven bands (V159), so the dome and the board read alike. Every corner is the
sun's place at that instant, the hours' instants from the climate's own offset, so the colours sit where the sun was.
Below the horizon nothing is drawn; the band's edge is cut every 20 minutes.

## 7. The panel

archiMap's card: location, day, time with its offset "(Auto)", "DST: Off (Auto)", a notes key with the sun hours, the
sun, the path, the compass, the winds, the average temperature and the humidity. The owner asks for the solstices and
the equinoxes broken down, with a diagram.

The sun's panel: **the sun now** (the place, the day, the time with its offset and zone, daylight saving, altitude,
azimuth, its point on the dome X, Y, Z with the formula, sunrise, sunset, the day's length); **sliders** for latitude
and longitude (a place tried, never saved, the site's own a press away), the date and the time (the study's own, one
undo step when let go); **Play** through the day or the year; **the turning points** -- the summer solstice, the
equinoxes, the winter solstice, by hemisphere -- each with sunrise and sunset (time and bearing), the noon altitude,
the day's length and a 10 m building's noon shadow; **two diagrams** (looking up at the sky; the sun's height through
the day); the temperature's key and the reading where the sun is. A range input is operable by keys and a click as
well as by dragging (WCAG 2.2, 2.5.7) and has its label and value (4.1.2).

## 8. Decisions taken

The owner's standing choice is to go on without stopping for questions; these are taken, and can be changed:
1. **Daylight saving Off by default** (standard time all year, Ladybug's default), Auto by choice.
2. **A tried place is never saved**; the date and time sliders set the study's own.
3. **The mesh shows the half-year holding the clock's date.**
4. **Play through the year**: a day a step, 36 seconds for the year, at the study's time.

## 9. Still open

- The report of NREL's SPA read in the original when nrel.gov answers.
- Sun hours on the dome (how long each part of the sky is lit), and radiation on the dome: V172's tools.
- A typed zone for a site without the climate; the zone of a place tried.

## 10. As built (2026-10-26)

As designed, with these found while building (the log, V171d, has them in full):
- **The sync's memory** was one record for the session: a run made with other inputs, or a project opened, left the
  elements as they came while the sync took them for current. Each element keeps the inputs it was drawn from, and a
  run or Reset clears them.
- **A name declared twice:** the places along a path for its name were first worked out by a function named as V164's
  noise analysis already has; the later in the closure won. Renamed, and a scan of every file's top-level functions
  finds no other.
- **The words' places:** a path's name 12 px off its line still met the hours' dots; 15 px.
- **Motion:** the sun now, now a dot and its ray, was offered a line's motions in Properties; it is Default (with the
  clock) or Still, as V170 designed.

## Sources

| Source | What was read | Date | Level |
|---|---|---|---|
| NOAA Solar Calculator spreadsheet (gml.noaa.gov/grad/solcalc) | every column's formula | 2026-10-26 | P |
| NOAA, General Solar Position Calculations (solareqns.pdf) | the fractional-year method | 2026-10-26 | P |
| Reda and Andreas, NREL SPA (NREL/TP-560-34302) | its worked example, through pvlib's tests | 2026-10-26 | S |
| pvlib-python, `tests/test_spa.py` | the SPA example's inputs and outputs | 2026-10-26 | S |
| Ladybug, `ladybug/sunpath.py`; `LB SunPath.py` (ladybug-grasshopper) | the sun vector, analemmas, daylight saving, hourly data | 2026-10-26 | P (as text) |
| Open-Meteo Historical Weather API page | `timezone`, `utc_offset_seconds` | 2026-10-26 | P |
| Open-Meteo archive, New York, 8-10 March 2025 | `timezone=auto` against GMT | 2026-10-26 | P (tested) |
| ECMA-402 `Intl.DateTimeFormat`, Chromium 1243 | ten zones' offsets | 2026-10-26 | P (tested) |
| archiMap's sun diagram (the owner's screenshot) | its card, key, labels | 2026-10-25 | S |
