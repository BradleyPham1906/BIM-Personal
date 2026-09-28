"""patch_phase100b.py -- __acad3dV100: marker."""
import hashlib, pathlib
SRC = pathlib.Path('canvas_v10.html')
BASE = '8e2940c78a6e41856748859bd81a6e54e876259b2f963d0f217a9baca8c2b293'
txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'
OLD = "  window.__acad3dV99='regiondependent,regiontrace,regiongraph,regionregen,regionopen,legacywallgroup,deletedsource,followstext';"
assert txt.count(OLD) == 1 and txt.count('window.__acad3dV100=') == 0
txt = txt.replace(OLD, OLD + "\n  window.__acad3dV100='escapekeeps,viewchangekeeps,newcommandkeeps,plineenteropen,plinetwopoints';", 1)
SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
