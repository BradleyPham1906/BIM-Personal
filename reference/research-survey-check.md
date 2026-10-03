# Research: verifying a survey (V138)

The owner: "if I go out on a survey and I have the survey data ... build the genesis of a good
foundation so data can be verified every time."

## What a surveyor checks, and what V138 does

- **Every line accounted for.** A file is read line by line. A line that is not numbers where
  numbers belong (a header, a typo such as `2110.00O`) is skipped and reported by its line number,
  never dropped silently.
- **Duplicates.** Two shots at one place cannot both be on a surface. The second is left out and
  named, because it is often a re-shot or a mis-keyed point number.
- **The surface honours the data.** A TIN must pass through every point it was built from. This
  is checked to 1 mm. It guards against a stale or wrong triangulation, the kind of bug that would
  otherwise show only as a slightly wrong volume.
- **Blunders (bust shots).**
  - A wrong rod height or a mis-coded shot sits away from its neighbours.
  - Each point is compared with a plane through its neighbours, weighted by inverse squared
    distance.
    - A plane predicts a tilted ground exactly, even at the survey's edge.
    - An inverse-distance mean does not, and flagged every edge point in testing.
    - A corner has two neighbours, too few for a plane, so it uses theirs too.
  - A point is a suspect when it is more than six times the survey's typical scatter (1.4826
    times the median absolute deviation) and more than 0.5 m away.
  - The worst suspect is set aside and the rest looked at again, so one bust does not make its
    neighbours suspects.
  - The 0.5 m floor keeps real features, such as a manhole lid on a flat car park, from being
    called busts.
- **Check shots** are the standard proof of a surface's accuracy.
  - Shots coded `CHK` are kept out of the surface and measured against it.
  - The report gives their RMSE (the root of the mean square difference, as ASPRS accuracy
    standards use) and the worst.
  - It passes at 0.05 m or less, and warns up to 0.15 m.
- **Control points.** Known elevations, such as benchmarks or control monuments, are typed in as
  `name=elevation` in the survey's units and checked to 2 cm. A name that is not in the survey
  fails.
- **Against the public terrain** (V133's AWS Terrain Tiles), when the site context has it:
  - The median offset says whether the base elevation or datum is off. More than 1 m is a warning,
    because public terrain is good only to a few metres.
  - The relief ratio (the slope of survey heights against public heights) says whether feet were
    read as metres (3.28) or metres as feet (0.30).
- **The verdict:** fail if any check fails, warn if any warns, else pass.

## How it is kept true every time

- **The datasets in `tests/data/surveys/`**, each with a sidecar of what its check must find, are
  run by the V138 suite on every build. A real survey dropped there is held to its sidecar from
  then on.
- **`tools/verify_survey.py`** runs the app's own check headless on any file and writes the
  report page, so the command line and the app cannot disagree.
- **The seeds** are made by `tools/make_seed_survey.py` from a ground known exactly. Each has one
  planted fault of each kind, and a clean one must pass.

## Not in V138

- Breaklines and boundaries, so a surface can hold an edge of pavement or a wall: next for the
  survey.
- Horizontal checks of control (only elevations are checked).
- Reading LandXML or a total station's raw file, rather than a coordinate file.
