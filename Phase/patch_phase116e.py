"""patch_phase116e.py -- V116 Model and layout tabs, part 5: a viewport given a fixed scale looks at the
model. A new 1:100 viewport, or a fitted one switched to 1:100, was centred on the model origin and
showed the building off in a corner or not at all; AutoCAD's MVIEW opens on the drawing's extents.
It now opens centred where the fit would centre it -- the same projection the first pan uses."""
NAME = 'patch_phase116e.py'
BASE = '76064cd76863a9b5158de62a69b91f51c0f3e5ca87e025593b7f5b2dc8e0271a'
import hashlib, pathlib, sys
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')
raw = P.read_bytes()
h0 = hashlib.sha256(raw).hexdigest()
if h0 != BASE:
    sys.exit('ABORT: baseline %s, expected %s' % (h0, BASE))
t = raw.decode('utf-8')


def esc(s):
    """Non-ASCII in inserted text becomes a \\uXXXX escape, by code rather than by care (V103)."""
    return ''.join(ch if ord(ch) < 128 else '\\u%04x' % ord(ch) for ch in s)


def rep(old, new, n=1):
    global t
    new = esc(new)
    c = t.count(old)
    if c != n:
        sys.exit('ABORT: %d occurrences, expected %d: %r' % (c, n, old[:90]))
    t = t.replace(old, new)


def after_line(head, new):
    """Insert new text after the whole line that starts with head (head must be unique)."""
    global t
    c = t.count(head)
    if c != 1:
        sys.exit('ABORT: %d occurrences, expected 1: %r' % (c, head[:90]))
    e = t.index('\n', t.index(head)) + 1
    t = t[:e] + esc(new) + t[e:]


def span(head, tail, new, lines):
    """Replace from the start of head up to (not including) the first tail after it. The span may
    hold non-ASCII that cannot be retyped, so it is found by its ends; head must be unique, and the
    number of lines removed must be exactly what was measured, so a tail that matched somewhere
    unexpected cannot quietly take the wrong amount."""
    global t
    c = t.count(head)
    if c != 1:
        sys.exit('ABORT: span head %d occurrences, expected 1: %r' % (c, head[:90]))
    s = t.index(head)
    e = t.find(tail, s + len(head))
    if e < 0:
        sys.exit('ABORT: span tail not found after head: %r' % tail[:90])
    got = t[s:e].count('\n')
    if got != lines:
        sys.exit('ABORT: span covers %d lines, expected %d: %r' % (got, lines, head[:60]))
    t = t[:s] + esc(new) + t[e:]
rep("    var cam=bimSheetSolveCamera(src,vp.w,vp.h,1,'fit',vp.scaleDenom);\n    var mmPerM=1.2*vp.h/Math.max(cam.dist,1e-9),want=1000/Math.max(mmPerM,1e-9),d=SHEET_SCALES[SHEET_SCALES.length-1].denom,i;\n    for(i=0;i<SHEET_SCALES.length;i++)if(SHEET_SCALES[i].denom>=want-1e-6){d=SHEET_SCALES[i].denom;break;}\n    var V=camVecs({yaw:src.cam.yaw,pitch:src.cam.pitch,dist:1,tx:src.cam.tx,ty:src.cam.ty,tz:src.cam.tz});\n    var dx=cam.tx-src.cam.tx,dy=cam.ty-src.cam.ty,dz=cam.tz-src.cam.tz;\n    vp.pan=[dx*V.r[0]+dy*V.r[1]+dz*V.r[2],dx*V.u[0]+dy*V.u[1]+dz*V.u[2]];\n    vp.scaleMode='ratio';vp.scaleDenom=d;\n",
    "    var cam=bimSheetSolveCamera(src,vp.w,vp.h,1,'fit',vp.scaleDenom);\n    var mmPerM=1.2*vp.h/Math.max(cam.dist,1e-9),want=1000/Math.max(mmPerM,1e-9),d=SHEET_SCALES[SHEET_SCALES.length-1].denom,i;\n    for(i=0;i<SHEET_SCALES.length;i++)if(SHEET_SCALES[i].denom>=want-1e-6){d=SHEET_SCALES[i].denom;break;}\n    vp.pan=bimSheetVpFitPan(vp)||[0,0];\n    vp.scaleMode='ratio';vp.scaleDenom=d;\n")
rep("  function bimSheetVpToRatio(vp){\n",
    r'''  /* __acad3dV116: where a fit would centre this viewport, as a pan -- read back from the fit's own
     camera, so a fixed scale opens on the model the same way the first pan or zoom keeps it. */
  function bimSheetVpFitPan(vp){
    var src=bimResolveViewportSource(vp);
    if(src.error||!src.cam)return null;
    var cam=bimSheetSolveCamera(src,vp.w,vp.h,1,'fit',vp.scaleDenom);
    var V=camVecs({yaw:src.cam.yaw,pitch:src.cam.pitch,dist:1,tx:src.cam.tx,ty:src.cam.ty,tz:src.cam.tz});
    var dx=cam.tx-src.cam.tx,dy=cam.ty-src.cam.ty,dz=cam.tz-src.cam.tz;
    return [dx*V.r[0]+dy*V.r[1]+dz*V.r[2],dx*V.u[0]+dy*V.u[1]+dz*V.u[2]];
  }
  function bimSheetVpToRatio(vp){
''')
rep("      if(scaleI.value==='fit'){vp.scaleMode='fit';}\n      else{vp.scaleMode='ratio';vp.scaleDenom=parseInt(scaleI.value,10)||100;}\n",
    "      if(scaleI.value==='fit'){vp.scaleMode='fit';}\n      else{vp.scaleMode='ratio';vp.scaleDenom=parseInt(scaleI.value,10)||100;vp.pan=bimSheetVpFitPan(vp)||[0,0];}   /* __acad3dV116: opens on the model */\n")
rep("      if(scaleI.value==='fit')vp.scaleMode='fit';\n      else{vp.scaleMode='ratio';vp.scaleDenom=parseInt(scaleI.value,10)||100;}\n",
    "      var wasFit=(vp.scaleMode!=='ratio');\n"
    "      if(scaleI.value==='fit')vp.scaleMode='fit';\n"
    "      else{vp.scaleMode='ratio';vp.scaleDenom=parseInt(scaleI.value,10)||100;if(wasFit)vp.pan=bimSheetVpFitPan(vp)||[0,0];}   /* __acad3dV116: keeps where the fit looked */\n")
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
