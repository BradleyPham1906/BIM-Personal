# V172c: the browser check of the built app, 2026-11-01

The owner allowed one browser check of the built studies (CLAUDE.md, Rule #1). Not a suite.

`node app_check.js REPO EPW SCREENSHOT`, with the Pages address routed to the committed `runtime/` (as V172b's suite
does) and `tests/ladybug_fixture.py`'s made-up year as the EPW (`F.epw_text(2017)`). Three solids: two 20 m blocks
12 m high, a 20 m tower 30 m high to the south of the first. The site 40 N, 75 W, UTC-5, 21 December 2017.

Results on build `234e52fe` (patch c):
- No page error, no console error, no `[BIM]` warning.
- The first study loads only then ladybug-radiance's wheel, numpy and `gendaymtx.wasm` from the runtime.
- Direct sun hours: 15 faces, 37 quarter-hours of sun; the tower's south face 9.25 h, its north face 0, the block
  behind the tower 6 h on its roof; 5.7 s with the runtime's first start, 0.46 s in the worker.
- Incident radiation: the tower's roof 1805.7 kWh/m2, exactly the sky's value on open ground (nothing above it);
  north faces the least (474 to 586); the block's south face behind the tower 725, the other block's 1037; 0.3 s.
- Neither out of date after its run; both rows "on" with their summaries; the versions kept (numpy 2.2.5 after
  patch c; before it, none).
- Drawn on the model in the 3D view: 9 faces facing the eye, the hidden block occluded, the legend inside the view's
  safe area (after patch c; before it, under the dock).
