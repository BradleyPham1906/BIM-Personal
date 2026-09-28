"""patch_phase104c.py -- __acad3dV104: marker."""
import hashlib, pathlib
SRC = pathlib.Path('canvas_v10.html')
BASE = 'a989f88b523a0186cd281e0b59e2b2879a3531095d45b04750b8c992569390fb'
txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'
OLD = "  window.__a3dNorthArrow=function(){"
assert txt.count(OLD) == 1 and txt.count('window.__acad3dV104=') == 0
txt = txt.replace(OLD, "  window.__acad3dV104='exportoffset,dxfnorthup,dxfbulgeflip,dxfimportinverse,svgnorthup,viewportframing';\n" + OLD, 1)
SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
