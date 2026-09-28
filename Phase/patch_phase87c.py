"""patch_phase87c.py -- Phase 87 part 3: point placement, and the class bug behind it.

Extracts the per-tool point handler out of skClick as skPlacePoint(gx,gz,xy) and routes typed
coordinates through it, then adds the Phase 87 branches. Before this, a typed coordinate was
pushed onto sk.pts and nothing else: MIRROR, ROTATE, TRIM, POLAR ARRAY and DIM all advertised
coordinate entry and none of them acted on it.
"""
import hashlib, pathlib, sys

BASE = '9deb3e78febf3283f7a9b7929c4889b4459e22313b58d07ea5cc7362eba877df'
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')

src = P.read_text(encoding='utf-8')
h0 = hashlib.sha256(src.encode('utf-8')).hexdigest()
assert h0 == BASE, 'baseline hash mismatch: %s' % h0
b0 = len(src.encode('utf-8'))

reps = []

# ---- 1. split skClick into the screen part and the point part -------------------------------
OLD_HEAD = """  function skClick(xy){
    var sk=A3D.sk;if(!sk)return;
    var g=groundPoint(xy[0],xy[1],sk.y);if(!g)return;
    var snapped=bimSnapPoint(xy,g,sk);
    var gx=snapped[0],gz=snapped[1];
    if(sk.tool==='rect'||sk.tool==='circle'){"""
NEW_HEAD = """  function skClick(xy){
    var sk=A3D.sk;if(!sk)return;
    var g=groundPoint(xy[0],xy[1],sk.y);if(!g)return;
    var snapped=bimSnapPoint(xy,g,sk);
    skPlacePoint(snapped[0],snapped[1],xy);
  }
  /* __acad3dV87: ONE point handler, reached by a click and by a typed coordinate alike.

     It used to be reachable only by a click. bimCommitTypedPoint pushed the parsed point onto
     sk.pts and stopped there, with two special cases bolted on for RECTANG and CIRCLE, so every
     tool that ACTS on its points rather than collecting them -- MIRROR, ROTATE, POLAR ARRAY,
     TRIM, DIM -- accepted a typed coordinate, showed it landing, and did nothing. The command
     line said the coordinate was taken and the model disagreed: the V86 fault in a second
     place, which is why this is fixed as a class rather than per tool.

     xy is the SCREEN point and is optional. It exists for one thing: the click-near-the-start
     close test at the bottom, which has no meaning for a typed coordinate. Absent, that test is
     skipped and everything else behaves identically. */
  function skPlacePoint(gx,gz,xy){
    var sk=A3D.sk;if(!sk)return;
    if(sk.tool==='rect'||sk.tool==='circle'){"""
reps.append((OLD_HEAD, NEW_HEAD, 1))

# ---- 2. the close-to-start test only applies to a real click --------------------------------
OLD_CLOSE = """      if(sk.pts.length>=3){
        var V=camVecs(A3D.cam),p0=toScreen([sk.pts[0][0],sk.y,sk.pts[0][1]],V,cvW(),cvH());
        if(Math.abs(p0[0]-xy[0])<9&&Math.abs(p0[1]-xy[1])<9){"""
NEW_CLOSE = """      if(xy&&sk.pts.length>=3){
        var V=camVecs(A3D.cam),p0=toScreen([sk.pts[0][0],sk.y,sk.pts[0][1]],V,cvW(),cvH());
        if(Math.abs(p0[0]-xy[0])<9&&Math.abs(p0[1]-xy[1])<9){"""
reps.append((OLD_CLOSE, NEW_CLOSE, 1))

# ---- 3. typed coordinates go through the same path ------------------------------------------
OLD_TYPED = """    sk.pts.push([p[0],p[1]]);
    if(sk.tool==='rect'&&sk.pts.length>=2)finishRect();
    else if(sk.tool==='circle'&&sk.pts.length>=2)finishCircle();
    bimSyncStatusHint();paint();saveSoon();
    return true;"""
NEW_TYPED = """    skPlacePoint(p[0],p[1],null);   /* __acad3dV87: the same handler a click reaches */
    bimSyncStatusHint();paint();saveSoon();
    return true;"""
reps.append((OLD_TYPED, NEW_TYPED, 1))

# ---- 4. the Phase 87 tools' point branches --------------------------------------------------
OLD_MIRROR = """    }else if(sk.tool==='mirror'){"""
NEW_MIRROR = """    }else if(sk.tool==='extend'){
      var extBoundId=sk.boundaryId;
      A3D.sk=null;
      bimApplyExtend(extBoundId,[gx,gz]);
    }else if(sk.tool==='break'){
      sk.pts.push([gx,gz]);
      if(sk.breakAtPoint){
        var brOneId=sk.breakId,brOnePt=sk.pts[0];
        A3D.sk=null;
        bimApplyBreak(brOneId,brOnePt,null);
      }else if(sk.pts.length>=2){
        var brTwoId=sk.breakId,brA=sk.pts[0],brB=sk.pts[1];
        A3D.sk=null;
        bimApplyBreak(brTwoId,brA,brB);
      }else{
        a3dToast('Break: click the second point');
      }
    }else if(sk.tool==='lengthen'){
      var lenWallId=sk.lenId;
      A3D.sk=null;
      openLengthenDlg(lenWallId,[gx,gz]);
    }else if(sk.tool==='scale'){
      var scBase=[gx,gz],scIds=sk.scaleIds;
      A3D.sk=null;
      openScaleDlg(scBase,scIds);
    }else if(sk.tool==='mirror'){"""
reps.append((OLD_MIRROR, NEW_MIRROR, 1))

# ---- 5. prompts for the new tools, derived from the point count -----------------------------
OLD_PROMPT = """    var msg=(SK_TOOLS[sk.tool]||sk.tool);
    return msg+(n?'  ·  click the next point, or type a length + Enter':'  ·  click to start');"""
NEW_PROMPT = """    /* __acad3dV87: the modify tools take a PICK, not a length, so they do not print the
       typed-length hint the drawing tools print. Each states what its next click does. */
    if(sk.tool==='extend')return 'Extend \\u00b7 select the wall end to extend:';
    if(sk.tool==='break')return sk.breakAtPoint?'Break at point \\u00b7 specify the split point:'
      :(n?'Break \\u00b7 specify second break point:':'Break \\u00b7 specify first break point:');
    if(sk.tool==='lengthen')return 'Lengthen \\u00b7 select the end to change:';
    if(sk.tool==='scale')return 'Scale \\u00b7 specify base point:';
    var msg=(SK_TOOLS[sk.tool]||sk.tool);
    return msg+(n?'  ·  click the next point, or type a length + Enter':'  ·  click to start');"""
reps.append((OLD_PROMPT, NEW_PROMPT, 1))

out = src
for old, new, want in reps:
    got = out.count(old)
    assert got == want, 'occurrence count %d (wanted %d) for: %s' % (got, want, old[:70])
    out = out.replace(old, new, want)

assert out != src
b1 = len(out.encode('utf-8'))
P.write_text(out, encoding='utf-8')
print('%d replacements' % len(reps))
print('bytes before %d  after %d  (+%d)' % (b0, b1, b1 - b0))
print('sha256 %s' % hashlib.sha256(out.encode('utf-8')).hexdigest())
