"""patch_phase91b.py -- Phase 91 part 2: Trim and Break run on the curve.

ONE PATH, not two. Trim and Break now always go through the bulged geometry; there is no
"straight version" kept alongside for walls without arcs, because two implementations of the same
operation are two things that can disagree, and the bulged code reduces to the straight answer
exactly when there are no bulges. The full regression is the evidence for that claim - the V35,
V86 and V87 suites all exercise straight Trim and Break.

The V89 refusals for Trim and Break are REMOVED, and this script asserts they are gone.
"""
import hashlib, pathlib, sys

BASE = '7b9eeb6546dfcb2c0f5e046b6075db9e3789fad60e22789fcfb41fd09914b6c0'
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')

src = P.read_text(encoding='utf-8')
h0 = hashlib.sha256(src.encode('utf-8')).hexdigest()
assert h0 == BASE, 'baseline hash mismatch: %s' % h0
b0 = len(src.encode('utf-8'))

reps = []

# ---- 1. Trim ---------------------------------------------------------------------------------
reps.append(("""      var cl=o.bim.centerline,n=cl.length,segs=o.bim.closed?n:n-1,k;
      for(k=0;k<segs;k++){
        var d=bimPtSegDist2D(clickPt,cl[k],cl[(k+1)%n]);
        if(d<bestD){bestD=d;target=o;}
      }
    }
    if(!target||bestD>3){a3dToast('Click closer to the wall you want to trim');return;}
    if(bimRefuseIfCurved(target,'Trim')||bimRefuseIfCurved(cutter,'Trim'))return;   /* __acad3dV89 */
    var r=bimTrimPolyline(target.bim.centerline,target.bim.closed,cutter.bim.centerline,cutter.bim.closed,clickPt);
    if(r.error){a3dToast('Trim: '+r.error);return;}
    var res=bimBuildWallGeometry(r.pts,target.bim.baseY,target.bim.height,target.bim.thickness,target.bim.align,false,null);""",
"""      /* __acad3dV91: measure to the CURVE. Picking a curved wall by its chords finds it in the
         wrong place, and on a tight arc can fail to find it at all. */
      var cl=o.bim.centerline,n=cl.length,segs=o.bim.closed?n:n-1,k;
      for(k=0;k<segs;k++){
        var d=bimPtDistToBulgedSeg(clickPt,cl[k],cl[(k+1)%n],bimBulgeAt(o.bim.bulges,k)).dist;
        if(d<bestD){bestD=d;target=o;}
      }
    }
    if(!target||bestD>3){a3dToast('Click closer to the wall you want to trim');return;}
    var r=bimTrimBulged(target.bim.centerline,target.bim.bulges,target.bim.closed,
                        cutter.bim.centerline,cutter.bim.bulges,cutter.bim.closed,clickPt);
    if(r.error){a3dToast('Trim: '+r.error);return;}
    var res=bimBuildWallGeometry(r.pts,target.bim.baseY,target.bim.height,target.bim.thickness,target.bim.align,false,r.bulges);""", 1))

# ---- 2. Break --------------------------------------------------------------------------------
reps.append(("""      if(bimRefuseIfCurved(w,'Break'))return false;   /* __acad3dV89 */
      var r=bimBreakPolyline(w.bim.centerline,w.bim.closed,p1,p2);
      if(r.error){a3dToast('Break: '+r.error);return false;}
      var made=bimNewWallFromSource(w,r.b,false,'Wall');
      if(made.error){a3dToast('Break: '+made.error);return false;}
      pushUndo();
      var rb=bimRebuildWallFrom(w,r.a,false);""",
"""      /* __acad3dV91: both pieces keep whatever curve they had, with the split arc's two halves
         recomputed rather than inherited. */
      var r=bimBreakBulged(w.bim.centerline,w.bim.bulges,w.bim.closed,p1,p2);
      if(r.error){a3dToast('Break: '+r.error);return false;}
      var made=bimNewWallFromSource(w,r.b.pts,false,'Wall',r.b.bulges);
      if(made.error){a3dToast('Break: '+made.error);return false;}
      pushUndo();
      var rb=bimRebuildWallFrom(w,r.a.pts,false,r.a.bulges);""", 1))

# The Break toast quoted r.removed, which the bulged result does not carry; it now measures the
# two pieces against the original, which is the number the user actually cares about.
reps.append(("""      a3dToast(p2?('Broken into 2 walls, '+bimFmtLen(Math.abs(r.removed))+' removed')
                 :'Split into 2 walls');""",
"""      var gone=bimBulgedLength(w.bim.centerline,w.bim.bulges,false);
      a3dToast(p2?('Broken into 2 walls, '+bimFmtLen(Math.max(0,before-gone-bimBulgedLength(made.obj.bim.centerline,made.obj.bim.bulges,false)))+' removed')
                 :'Split into 2 walls');""", 1))

# ...which needs the original length measured before anything is rebuilt.
reps.append(("""      var r=bimBreakBulged(w.bim.centerline,w.bim.bulges,w.bim.closed,p1,p2);""",
"""      var before=bimBulgedLength(w.bim.centerline,w.bim.bulges,w.bim.closed);
      var r=bimBreakBulged(w.bim.centerline,w.bim.bulges,w.bim.closed,p1,p2);""", 1))

# ---- 3. picking a wall near a point measures the curve too ------------------------------------
reps.append(("""      var cl=o.bim.centerline,n=cl.length,segs=o.bim.closed?n:n-1,k;
      for(k=0;k<segs;k++){
        var d=bimPtSegDist2D(clickPt,cl[k],cl[(k+1)%n]);
        if(d<bestD){bestD=d;best=o;}
      }""",
"""      var cl=o.bim.centerline,n=cl.length,segs=o.bim.closed?n:n-1,k;
      for(k=0;k<segs;k++){
        /* __acad3dV91: to the curve, not the chord. */
        var d=bimPtDistToBulgedSeg(clickPt,cl[k],cl[(k+1)%n],bimBulgeAt(o.bim.bulges,k)).dist;
        if(d<bestD){bestD=d;best=o;}
      }""", 1))

# ---- 4. hooks and marker ----------------------------------------------------------------------
reps.append(("""  /* __acad3dV90 */
  window.__a3dTangentBulge=bimTangentBulge;""",
"""  /* __acad3dV91 */
  window.__a3dProjectOntoBulged=bimProjectOntoBulged;
  window.__a3dPtDistToBulgedSeg=bimPtDistToBulgedSeg;
  window.__a3dIntersectBulgedSegs=bimIntersectBulgedSegs;
  window.__a3dSplitBulgedAt=bimSplitBulgedAt;
  window.__a3dTrimBulged=bimTrimBulged;
  window.__a3dBreakBulged=bimBreakBulged;
  window.__a3dArcPointAt=bimArcPointAt;
  window.__acad3dV91='arcawaretrim,arcawarebreak,sweepparameter,arcarcintersection,curvepicking';
  /* __acad3dV90 */
  window.__a3dTangentBulge=bimTangentBulge;""", 1))

out = src
for old, new, want in reps:
    got = out.count(old)
    assert got == want, 'occurrence count %d (wanted %d) for: %s' % (got, want, old[:70])
    out = out.replace(old, new, want)

for gone in ("bimRefuseIfCurved(target,'Trim')", "bimRefuseIfCurved(w,'Break')"):
    assert gone not in out, 'a V89 refusal survived the work it was waiting for: %s' % gone

b1 = len(out.encode('utf-8'))
P.write_text(out, encoding='utf-8')
print('%d replacements' % len(reps))
print('bytes before %d  after %d  (+%d)' % (b0, b1, b1 - b0))
print('sha256 %s' % hashlib.sha256(out.encode('utf-8')).hexdigest())
