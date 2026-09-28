"""patch_phase99f.py -- __acad3dV99: drop a duplicate test export added in 99e.

__a3dApplyHatchAt already exists (V96). A second definition would shadow it -- the exact
mistake the V97 suite guards against, made a third time. Removed.
"""
import hashlib, pathlib
SRC = pathlib.Path('canvas_v10.html')
BASE = '23682fe5a12c1b8ca6d3009a8abf73023f42aa72b4862795fc195843ee00972d'
txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'
OLD = "  window.__a3dApplyHatchAt=function(pt,y,opts){var o=bimApplyHatchAt(pt,y||0,opts||bimHatchDefaults());return o?o.id:null;};\n"
assert txt.count(OLD) == 1
txt = txt.replace(OLD, '', 1)
SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
