#!/usr/bin/env python3
"""V172, patch e: found by the full regression. V120's derivation of dead code found one function the tools declare and
never call: a count of a mask's cells within another (the tools count with bimTlCount and bimTlMaskStats). It goes.

Run from the repository root: python3 Phase/patch_v172_e.py
"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from p171 import begin, rep, done   # noqa: E402

begin('ea2d5113d65d6aa1da2824efe1e987b84a6fe41717578a199ea314f7ef4eab17')   # patch d, the build the falsification and the regression ran on

rep('js/engine/site-tools/tools.js', "  function bimTlCountIn(G,m,w){var n=0,k;for(k=0;k<G.n;k++)if(m[k]&&(!w||w[k]))n++;return n;}\n", "")
done()
