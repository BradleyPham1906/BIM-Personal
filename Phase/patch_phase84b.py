"""patch_phase84b.py -- expose whether a section cut is active.

The V84 suite asserts that opening a floor plan FROM a section leaves the cut plane behind. There
was no hook that could answer that, so the check would have read null and passed vacuously -- a
check that cannot fail is worse than no check, because it looks like coverage.
"""

import hashlib
import pathlib
import sys

SRC = pathlib.Path(__file__).resolve().parent / 'canvas_v10.html'
BASE = 'f282e8e8d13b2a6f09b5c3fe4ef45dcb5d34df4726d71e2b1751464a39f44015'

src = SRC.read_bytes()
have = hashlib.sha256(src).hexdigest()
if have != BASE:
    print('ABORT: baseline mismatch\n  expected %s\n  found    %s' % (BASE, have))
    sys.exit(1)
print('baseline ok: %s (%d bytes)' % (have[:16], len(src)))

text = src.decode('utf-8')

OLD = "sheets:A3D.sheets,activeLevel:A3D.activeLevel,activeViewId:A3D.activeViewId,"
NEW = ("sheets:A3D.sheets,activeLevel:A3D.activeLevel,activeViewId:A3D.activeViewId,"
       "section:!!A3D.section,")

n = text.count(OLD)
if n != 1:
    print('ABORT: expected 1 occurrence of the state anchor, found %d' % n)
    sys.exit(1)
text = text.replace(OLD, NEW, 1)
print('  edit 1 ok: __a3dState reports whether a section cut is active')

out = text.encode('utf-8')
SRC.write_bytes(out)
print('\nbytes : %d -> %d (%+d)' % (len(src), len(out), len(out) - len(src)))
print('sha256: %s' % hashlib.sha256(out).hexdigest())
