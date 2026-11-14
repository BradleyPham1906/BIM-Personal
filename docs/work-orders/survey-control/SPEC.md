# Survey control: horizontal control and raw total-station files (outline)

Notion: Later: Survey control. PIPELINE: later. Research: `docs/research/research-later-survey-control.md`, `docs/research/research-survey-check.md`. Written by Claude, 2026-11-14, as an outline: not yet Cline-ready; the next spec sprint turns its first slice into work orders with tests.

## 0. Status

Next spec sprint: the traverse arithmetic is pure and testable now; raw formats need real files from the owner.

## 1. The owner's decisions, 2026-11-14, as recommended

- closed traverses adjusted by the compass (Bowditch) rule first, least squares later;
- angles in degrees-minutes-seconds and decimal degrees, distances in metres or US survey feet, the unit kept on every value;
- raw files: the owner provides one real file per format before its parser is ordered; nothing parsed from guesswork.

## 2. What it does for the user

Enter a closed traverse: the app gives its angular and linear misclosure, its precision ratio and the adjusted coordinates, into V138's checks.

## 3. The first slice (pure functions in `src/js/engine/survey/traverse.js`, ES5, no other file's names)

- `bimSvDms(s)`: a DMS string ("123-45-30" or 123.4530) as decimal degrees.
- `bimSvAzimuths(start, angles)`: azimuths from a starting azimuth and interior angles.
- `bimSvLatDep(az, dist)`: latitudes and departures.
- `bimSvMisclosure(lat, dep, angles)`: angular misclosure, linear misclosure and the precision ratio.
- `bimSvCompass(lat, dep, dist)`: the compass-rule corrections and adjusted coordinates.

Tests: A textbook closed traverse worked by hand in the test (its misclosure and adjusted coordinates).

## 4. Not in this phase

Least-squares networks; levelling; gnss.
