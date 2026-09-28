"""patch_phase94i.py -- __acad3dV94: a construction line has a bounds, and it is its root.

Found by falsification, not by reading. One of the ten broken builds removed the guard in
bimDrawingExtent2D that excludes construction lines from the extent they are drawn across --
and the suite still passed. The guard was unreachable: bimObjBounds2D had no branch for a
cline, so it returned null and the object was skipped anyway.

Unreachable code that reads as load-bearing is the thing law 1 is about, and there are two ways
out. Deleting the guard would leave Align quietly doing nothing to a construction line, because
that is what a null bounds means there. So the bounds becomes honest instead: a construction
line's 2D bounds is its ROOT, which is the one definite point on it.

That makes the guard necessary rather than decorative -- without it a construction line rooted
9 km away sets the extent every construction line is then drawn across -- and it makes the
falsified build fail, which is the point.

AutoCAD's ZOOM EXTENTS ignores construction lines entirely; this build's zoom works from mesh
bounds and a cline has no mesh, so that behaviour is unchanged by this.
"""
import hashlib, pathlib

SRC = pathlib.Path('canvas_v10.html')
BASE = '170b8ca1689e9fef3298b31997829b54810a3a2631603dbd0d4fcdc148e1de20'

txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'

OLD = """    else if(o.t==='sketch')pts=bimSketchOutline(o);   /* __acad3dV93 */
    else if(o.t==='room')pts=o.pts;"""
NEW = """    else if(bimIsCline(o))pts=[o.p];                 /* __acad3dV94: the root, the one
       definite point on a line that has no ends. Without it Align silently did nothing to a
       construction line, and the extent guard that keeps one out of its own drawing extent was
       unreachable. */
    else if(o.t==='sketch')pts=bimSketchOutline(o);   /* __acad3dV93 */
    else if(o.t==='room')pts=o.pts;"""

assert txt.count(OLD) == 1, 'anchor count %d' % txt.count(OLD)
txt = txt.replace(OLD, NEW, 1)

SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
