#!/usr/bin/env python3
"""V172, patch b: found while building. The suite's view of the result layers read every layer's cells as a string,
as sun hours and rain keep them; a tool's output keeps runs, so it threw for one. It counts a tool layer's cells by its
grid now.

Run from the repository root: python3 Phase/patch_v172_b.py
"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from p171 import begin, rep, done   # noqa: E402

begin('9483c90134bedca082f31ccb5e5d792f380373a98adaf91f721d530896bab0d0')   # patch a, with the tools' files as they stood after the first run (the level alphabet widened)

rep('js/engine/testing/hooks-commands-site.js', "created:R.created||null,run:R.run||null,cells:R.data?R.data.cells.length:0,",
    "created:R.created||null,run:R.run||null,cells:R.data&&typeof R.data.cells==='string'?R.data.cells.length:(R.kind==='tool'&&R.data?R.data.nx*R.data.nz:0),   /* __acad3dV172: a tool's output keeps runs */\n      ")
done()
