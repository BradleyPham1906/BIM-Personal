#!/usr/bin/env python3
"""V171d, patch k: the sun's angles are lines like any other, and take any motion lines take (V170's suite sets every
multi-line element marching); only the sun now, the clock's own, is Default or Still.

Run from the repository root: python3 Phase/patch_v171d_k.py
"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from p171 import begin, rep, done   # noqa: E402

begin('ff07bd02a1e8c9f2bbd4dac9558456585b91ae3949ddd198242a0c538346b9e2')   # after patch j

rep('js/engine/site-analysis/motion.js',
    "    if(o.dg.a==='sun'&&(o.dg.k==='now'||o.dg.k==='angles'))return L;   /* __acad3dV171d: the sun now moves with the clock, or is still */",
    "    if(o.dg.a==='sun'&&o.dg.k==='now')return L;   /* __acad3dV171d: the sun now moves with the clock, or is still */")
done()
