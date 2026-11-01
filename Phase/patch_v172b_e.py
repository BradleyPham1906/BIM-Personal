#!/usr/bin/env python3
"""V172b, patch e: what the suite asked of the build. reference/research-ladybug-weather-comfort.md.

- Open-Meteo out of reach is said in the app's words (the browser's own is "Failed to fetch"): the hours need the
  network, and the weather the project names stays.
- An Open-Meteo year as Ladybug holds an EPW's: Ladybug moves a file's last row to the front for the fields at an instant
  (temperature, dew point, humidity, wind, sky cover; ladybug/epw.py), so those take Open-Meteo's own hour, and pressure
  and the radiations the hour after. They all took the hour after: the instants were an hour late. Found by the suite's
  hour-by-hour check against the official UTCI polynomial.
- The version: V172 still (a sub-phase keeps its number, as V171b to V171d did), of 2026-11-01, its marker noted.

Run from the repository root: python3 Phase/patch_v172b_e.py
"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from p171 import begin, rep, done, ROOT   # noqa: E402

begin('37a4a7ea22e341ab1ccf01e14ef6a52f635807eae088c5ceed8b665720cd2cce')   # patch d

# the adapter (src/py/bim_ladybug.py, edited: an Open-Meteo year as Ladybug holds an EPW's -- the variables at an instant
# at their own hour, pressure and radiation the hour after) written again into js/engine/ladybug/adapter-py.js
import subprocess   # noqa: E402
subprocess.check_call([sys.executable, str(ROOT / 'tools' / 'embed_py.py')])

rep('js/engine/ladybug/sources.js',
    "    return fetch(url).then(function(r){if(!r.ok)throw new Error('archive-api.open-meteo.com answered '+r.status);return r.json();}).then(function(js){",
    "    return fetch(url).then(function(r){if(!r.ok)throw new Error('archive-api.open-meteo.com answered '+r.status);return r.json();},\n"
    "      function(e){throw new Error('archive-api.open-meteo.com could not be reached ('+(e&&e.message||e)+'): the hours need the network');}).then(function(js){")
rep('js/engine/ui/guide-versions.js', "  var BIM_APP_VERSION={v:'V172',date:'2026-10-31'};   /* __acad3dV162; __acad3dV163; __acad3dV164; __acad3dV165; __acad3dV166; __acad3dV167; __acad3dV168; __acad3dV170; __acad3dV171; __acad3dV172 */",
    "  var BIM_APP_VERSION={v:'V172',date:'2026-11-01'};   /* __acad3dV162; __acad3dV163; __acad3dV164; __acad3dV165; __acad3dV166; __acad3dV167; __acad3dV168; __acad3dV170; __acad3dV171; __acad3dV172; __acad3dV172b */")
done()
