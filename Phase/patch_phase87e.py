"""patch_phase87e.py -- Phase 87 part 5: a two-object selection hook for the suite.

Chamfer and Fillet are the only modify commands that take a PAIR (sel + sel2, the Join Walls
convention). __a3dSelectFor clears sel2, so without this the suite could only reach them through
their apply functions -- and a command claimed without being driven is the V85 fault.
"""
import hashlib, pathlib, sys

BASE = 'aac36c628e759c0c7759045235ea1e4e813a83be646b39c79f5d6e0fdf1ab0c9'
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')

src = P.read_text(encoding='utf-8')
h0 = hashlib.sha256(src.encode('utf-8')).hexdigest()
assert h0 == BASE, 'baseline hash mismatch: %s' % h0
b0 = len(src.encode('utf-8'))

OLD = """  window.__a3dSelectFor=function(ids){A3D.sel=(ids&&ids[0])||null;A3D.selSet=(ids||[]).slice();A3D.sel2=null;};"""
NEW = """  window.__a3dSelectFor=function(ids){A3D.sel=(ids&&ids[0])||null;A3D.selSet=(ids||[]).slice();A3D.sel2=null;};
  /* __acad3dV87: the pair selection Chamfer, Fillet, Join and Merge all take. */
  window.__a3dSelectPair=function(a,b){A3D.sel=a||null;A3D.sel2=b||null;A3D.selSet=[a,b].filter(Boolean);};"""
assert src.count(OLD) == 1, 'anchor count %d' % src.count(OLD)
out = src.replace(OLD, NEW, 1)
b1 = len(out.encode('utf-8'))
P.write_text(out, encoding='utf-8')
print('bytes before %d  after %d  (+%d)' % (b0, b1, b1 - b0))
print('sha256 %s' % hashlib.sha256(out.encode('utf-8')).hexdigest())
