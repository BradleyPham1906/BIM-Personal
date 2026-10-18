"""patch_phase166g.py -- V166c: the analytical member keeps only what is read.

  bimAnalyticalModel (V125) gives each member it derives from a column or a beam seventeen fields.
  Four are read nowhere, and have not been since V125: hy and hz (the section's sizes along the
  member's local y and z), p2 (its far end) and material (its material's name). In V125 the locals
  hy and hz fed bimRectSection; since V126 the section is its profile's (bimMemberSection), which
  maps a column's width and a beam's depth to the section's own d, so the locals are dead too.
  V166b found this when falsify_phase125.py's column_axes_swapped (which swapped them) was not
  caught; that variant is retired there.

  The member is derived on every solve and never stored: not on the element, so not in bimCarryBim,
  the project's JSON, the history, IFC or Properties. A project saved by any build opens unchanged.
  BIM_APP_VERSION stays V166, as V166b's did.
"""
import hashlib, pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
BASE = 'b7ee1405e5248fbb833127618991763e1d0d997790b7230525e00d3d75032b7e'   # V166b, after patch_phase166f.py

raw = SRC.read_bytes()
sha = hashlib.sha256(raw).hexdigest()
if sha != BASE:
    sys.exit('baseline sha mismatch: %s' % sha)
txt = raw.decode('utf-8')
assert 'function bimLeftStep(){' in txt, 'run patch_phase166f.py first'


def rep(old, new, count=1):
    global txt
    n = txt.count(old)
    assert n == count, 'anchor count %d (wanted %d): %r' % (n, count, old[:80])
    txt = txt.replace(old, new)


# ---- the two locals that only filled the record ----
rep("""      var q=bimObjOffset(o),b=o.bim,p1,p2,yRef,hy,hz;
""", """      var q=bimObjOffset(o),b=o.bim,p1,p2,yRef;
""")
rep("""        yRef=[Math.cos(r),0,Math.sin(r)];hy=b.width;hz=b.depth;
""", """        yRef=[Math.cos(r),0,Math.sin(r)];
""")
rep("""        yRef=[0,1,0];hy=b.depth;hz=b.width;
""", """        yRef=[0,1,0];
""")
# ---- the record: the fields the solve, the signature and the display read ----
rep("""      members.push({id:o.id,name:o.name,kind:b.type,p1:p1,p2:p2,L:bimVLen(bimVSub(p2,p1)),ax:ax,
        n1:nodeAt(p1),n2:nodeAt(p2),sec:sec,E:E,G:E/(2*(1+nu)),rho:mat&&mat.density||0,material:mat?mat.name:'',
        hy:hy,hz:hz,els:[]});
""", """      /* __acad3dV166c: only what the solve, its signature and the display read. The section's sizes
         are its profile's (bimMemberSection); the far end, p2, is read through L and ax. */
      members.push({id:o.id,name:o.name,kind:b.type,p1:p1,L:bimVLen(bimVSub(p2,p1)),ax:ax,
        n1:nodeAt(p1),n2:nodeAt(p2),sec:sec,E:E,G:E/(2*(1+nu)),rho:mat&&mat.density||0,els:[]});
""")

out = txt.encode('utf-8')
SRC.write_bytes(out)
print('patch_phase166g applied:', hashlib.sha256(raw).hexdigest(), len(raw), '->', hashlib.sha256(out).hexdigest(), len(out))
