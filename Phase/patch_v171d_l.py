#!/usr/bin/env python3
"""V171d, patch l: what the falsification showed. A slider let go was put back in the hand by a timer; the panel's
redraw (bimRenderInto, V162) already keeps the field that has the focus, so the timer did nothing (the variant that
removed it was not caught): it goes.

Run from the repository root: python3 Phase/patch_v171d_l.py
"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from p171 import begin, rep, done   # noqa: E402

begin('e16592e40bd36fd155b91f9e827c4d6e827c9f4dc8d5a3a1d1c93b1815e0348f')   # V171d as first checked

rep('js/engine/site-analysis/analysis-workspace.js', """        else if((k=e.getAttribute('data-sunsl'))){   /* __acad3dV171d: a slider let go; the same slider in the hand again */
          bimSunSlide(k,e.value,true);
          setTimeout(function(){var s=el.propsbody.querySelector('[data-sunsl="'+k+'"]');if(s&&document.activeElement!==s)s.focus();},0);
        }""", """        else if((k=e.getAttribute('data-sunsl')))bimSunSlide(k,e.value,true);   /* __acad3dV171d: a slider let go; the redraw keeps it in the hand */""")
done()
