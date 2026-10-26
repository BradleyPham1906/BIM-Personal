#!/usr/bin/env python3
"""V171d, patch h: a run, or Reset, draws an element again from the inputs of that moment: the inputs it was last
synced from (dg.sk) go with its old shape, so the sun's sync looks at it again (the suite: an offset typed, Analyze
site again, the offset set back -- the paths kept the typed one, their key still the earlier one's).

Run from the repository root: python3 Phase/patch_v171d_h.py
"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from p171 import begin, rep, done   # noqa: E402

begin('5d79e3b3bc53f4f73497fa94dbdde1c189eaab9faba667a23ddcb4e77b468679')   # after patch g

ML = 'js/engine/site-analysis/model-layers.js'
rep(ML, "          x.dg.g=core.g;x.dg.s=core.s;x.dg.lb=core.lb;x.dg.sym=core.sym;x.dg.gen=gen;x.dg.info=e.info||{};",
    "          x.dg.g=core.g;x.dg.s=core.s;x.dg.lb=core.lb;x.dg.sym=core.sym;x.dg.gen=gen;x.dg.info=e.info||{};delete x.dg.sk;   /* __acad3dV171d: drawn again, its sync's inputs gone */")
rep(ML, "    o.dg.g=c.g;o.dg.s=c.s;o.dg.lb=c.lb;o.dg.sym=c.sym;o.pos=[0,0,0];delete o.dg.newer;",
    "    o.dg.g=c.g;o.dg.s=c.s;o.dg.lb=c.lb;o.dg.sym=c.sym;o.pos=[0,0,0];delete o.dg.newer;delete o.dg.sk;   /* __acad3dV171d */")
done()
