#!/usr/bin/env python3
"""V171d, patch i: the places along a path for its name were worked out by a function named as one V164's noise
analysis already has (bimDgAlong, a line's points every step): the later in the closure won, the names had no place.
Mine is bimDgAlongPath; no other name is declared twice (a scan of every file's top-level functions).

Run from the repository root: python3 Phase/patch_v171d_i.py
"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from p171 import begin, rep, done   # noqa: E402

begin('669632d9689e752159dde6c3077f32ad631e99fadfcf127277af0347ccb73834')   # after patch h

ML = 'js/engine/site-analysis/model-layers.js'
rep(ML, "        cands:L.near?bimDgBeside(sp):(L.alt?bimDgAlong(o,L,sp,V,W,H):null)});", "        cands:L.near?bimDgBeside(sp):(L.alt?bimDgAlongPath(o,L,sp,V,W,H):null)});")
rep(ML, "  function bimDgAlong(o,L,sp,V,W,H){", "  function bimDgAlongPath(o,L,sp,V,W,H){")
done()
