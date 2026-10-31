#!/usr/bin/env python3
"""V172, patch f: found reading the new files against the build contract (ES5, match the surrounding code). The hook
that runs Locate's growth on a grid made by the suite built its typed arrays with Float64Array.from and Uint8Array.from,
the only TypedArray.from in the engine; everywhere else a typed array is made by its constructor, as here now. The same
arrays: a constructor given an array copies it.

Run from the repository root: python3 Phase/patch_v172_f.py
"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from p171 import begin, rep, done   # noqa: E402

begin('534795feea5a79799c744dd88a66c9bdd7fc65aeeedd61af90c96f85bc8036f0')   # patch e

rep('js/engine/testing/hooks-tools.js', "r=bimTlGrow(G,Float64Array.from(V),Uint8Array.from(ok),seed,need);", "r=bimTlGrow(G,new Float64Array(V),new Uint8Array(ok),seed,need);")
done()
