"""patch_phase101f.py -- __acad3dV101: test surface for the label point."""
import hashlib, pathlib, re
SRC = pathlib.Path('canvas_v10.html')
BASE = '829efd987ddf940c1da57aa825bfdb9e51496be002db9fadc1ed39bd313bda14'
txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'
OLD = "  window.__a3dRoomTagged=bimRoomTagged;"
assert txt.count(OLD) == 1 and txt.count('window.__a3dRoomLabelPoint') == 0
txt = txt.replace(OLD, OLD + "\n  window.__a3dRoomLabelPoint=function(id){var o=objById(id);return o?bimRoomLabelPoint(o):null;};", 1)
SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
