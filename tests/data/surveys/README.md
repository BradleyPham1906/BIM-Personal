# Survey datasets: checked on every build

Every survey here is read by the app and checked by its Survey Check (V138) each time the suites
run (`tests/bim_phase138_survey_check_browser_tests.py`). Each one must come out the way its
sidecar says, so a change that alters how a survey is read, triangulated or measured fails before
it ships.

## Adding your own survey

1. Put the file here as it came from the field: `mysite_2026-10.txt`.
2. Code your check shots with a description starting `CHK`. These are shots taken to measure the
   surface, not to build it.
3. Run it once and read the report:

       python3 tools/verify_survey.py tests/data/surveys/mysite_2026-10.txt --format PNEZD --units usft --base 5000,2000,100 --control "BM1=102.345"

4. When the report is what you expect, write a sidecar `mysite_2026-10.json` beside it:

       {
         "file": "mysite_2026-10.txt",
         "format": "PNEZD",            "units": "usft",
         "base": {"n": 5000, "e": 2000, "z": 100},
         "checkCode": "CHK",
         "control": "BM1=102.345",
         "note": "Crew A, total station, 3 October 2026",
         "expect": {"verdict": "pass", "points": 812, "checks": 12, "skippedLines": [1],
                    "duplicates": [], "busts": [], "fidelity": "pass", "control": "pass",
                    "checkStatus": "pass", "checkRmseMax": 0.03}
       }

   Every key under `expect` is optional; the ones given are held.

## The checks

| Check | Passes when |
|---|---|
| Read | every line was read (a skipped line is a warning, with its line number) |
| Duplicates | no point repeats a place already surveyed (a warning, by point name) |
| Through every point | the surface passes through every survey point, to 1 mm |
| Triangles | no triangle has zero area |
| Bust shots | no point is more than 0.5 m (and six times the survey's typical scatter) from a plane through its neighbours |
| Check shots | their RMSE against the surface is 0.05 m or less (0.15 m warns) |
| Control points | each known elevation is matched to 2 cm |
| Public terrain | with the site context's terrain: no offset over 1 m, and no relief ratio of 3.28 (feet read as metres) or 0.30 |

## The seeds

`tools/make_seed_survey.py` writes them from a known ground, so every elevation is known exactly.
- `seed_site_m`: metres, PNEZD. It has a header line, a mistyped easting, a duplicate, a 3 m bust
  shot, six check shots and two control points. Its verdict must be **fail**.
- `seed_site_usft`: US survey feet, PENZD, with a manhole lid 0.2 m proud. Its verdict must be
  **pass**.
