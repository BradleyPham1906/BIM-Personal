"""patch_phase90b.py -- Phase 90 part 2: arc mode on the wall and polyline tools.

AutoCAD's PLINE switches to arc segments with A and back with L. Same here, for WALL and PLINE.
LINE is deliberately excluded, as it is in AutoCAD: LINE has no arc option.

The Arc/Line option in the prompt is DERIVED from the same predicate the key consults, so the
prompt cannot advertise a mode the key would refuse - the V86 lesson, applied where the next
option was being added rather than after it drifted.
"""
import hashlib, pathlib, sys

BASE = '3575216e6091185cbb83d738bd95704dffa936aa551c373135b462e188cf88f3'
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')

src = P.read_text(encoding='utf-8')
h0 = hashlib.sha256(src.encode('utf-8')).hexdigest()
assert h0 == BASE, 'baseline hash mismatch: %s' % h0
b0 = len(src.encode('utf-8'))

reps = []

# ---- 1. the predicate, and the prompt derived from it ----------------------------------------
reps.append(("""  function bimPromptOpts(sk){
    var n=sk.pts?sk.pts.length:0,o=[];
    if(bimCanClose(sk))o.push('Close');
    if(n)o.push('Undo');
    return o.length?(' or ['+o.join('/')+']'):'';
  }""",
"""  /* __acad3dV90: which tools take arc segments, and when.

     WALL and PLINE do; LINE does not, exactly as in AutoCAD. An arc needs a direction to leave
     along, so it needs a finished segment to continue from: arc mode is offered only once two
     points are down. That is a real precondition, and it is the same predicate the A key
     consults, so the prompt can never offer a mode the key refuses. */
  function bimCanArc(sk){
    if(!sk||!sk.pts)return false;
    if(sk.tool!=='wall'&&sk.tool!=='poly')return false;
    return sk.pts.length>=2;
  }
  function bimSetArcMode(sk,on){
    if(!sk)return false;
    if(on&&!bimCanArc(sk))return false;
    sk.arcMode=!!on;
    bimSyncStatusHint();paint();
    return true;
  }
  /* The direction the run is travelling at its last point, which is what a tangent arc
     continues. Derived from the segment that is actually there, arc or straight. */
  function bimSkHeading(sk){
    if(!sk||!sk.pts||sk.pts.length<2)return null;
    var i=sk.pts.length-1;
    return bimSegEndDir(sk.pts[i-1],sk.pts[i],bimBulgeAt(sk.bulges,i-1));
  }
  function bimPromptOpts(sk){
    var n=sk.pts?sk.pts.length:0,o=[];
    if(bimCanClose(sk))o.push('Close');
    if(sk&&sk.arcMode)o.push('Line');
    else if(bimCanArc(sk))o.push('Arc');
    if(n)o.push('Undo');
    return o.length?(' or ['+o.join('/')+']'):'';
  }""", 1))

# ---- 2. placing a point while in arc mode ----------------------------------------------------
reps.append(("""    }else if(sk.tool==='arc'){
      sk.pts.push([gx,gz]);
      if(sk.pts.length>=3)finishArc();""",
"""    }else if((sk.tool==='wall'||sk.tool==='poly')&&sk.arcMode&&sk.pts.length>=1){
      /* __acad3dV90: an arc segment, tangent to the run so far. The bulge belongs to the
         segment being closed - index pts.length-1 - so it is written BEFORE the point is
         pushed, which keeps bulges[i] describing the segment from pts[i] to pts[i+1] exactly
         as it does everywhere else. */
      var segIdx=sk.pts.length-1;
      var heading=bimSkHeading(sk);
      var tb=heading?bimTangentBulge(heading,sk.pts[segIdx],[gx,gz]):null;
      if(tb===null){
        a3dToast('No arc continues from here to that point - pick a point off the current direction');
        paint();return;
      }
      if(!sk.bulges)sk.bulges=[];
      while(sk.bulges.length<segIdx)sk.bulges.push(0);
      sk.bulges[segIdx]=tb;
      sk.pts.push([gx,gz]);
    }else if(sk.tool==='arc'){
      sk.pts.push([gx,gz]);
      if(sk.pts.length>=3)finishArc();""", 1))

# ---- 3. the keys ------------------------------------------------------------------------------
reps.append(("""        if((ev.key==='c'||ev.key==='C')&&!ev.ctrlKey&&!ev.metaKey&&bimCanClose(A3D.sk)){""",
"""        /* __acad3dV90: A switches to arc segments, L back to straight - PLINE's own keys. */
        if((ev.key==='a'||ev.key==='A')&&!ev.ctrlKey&&!ev.metaKey&&bimCanArc(A3D.sk)&&!A3D.sk.arcMode){
          bimSetArcMode(A3D.sk,true);ev.preventDefault();ev.stopImmediatePropagation();return;
        }
        if((ev.key==='l'||ev.key==='L')&&!ev.ctrlKey&&!ev.metaKey&&A3D.sk.arcMode){
          bimSetArcMode(A3D.sk,false);ev.preventDefault();ev.stopImmediatePropagation();return;
        }
        if((ev.key==='c'||ev.key==='C')&&!ev.ctrlKey&&!ev.metaKey&&bimCanClose(A3D.sk)){""", 1))

# ---- 4. Undo drops the bulge with the point --------------------------------------------------
reps.append(("""  function bimUndoLastPoint(){
    var sk=A3D.sk;
    if(!sk||!sk.pts||!sk.pts.length)return false;
    sk.pts.pop();""",
"""  function bimUndoLastPoint(){
    var sk=A3D.sk;
    if(!sk||!sk.pts||!sk.pts.length)return false;
    sk.pts.pop();
    /* __acad3dV90: the segment that point closed goes with it, or the arrays drift apart. */
    if(sk.bulges&&sk.bulges.length>Math.max(0,sk.pts.length-1))sk.bulges.length=Math.max(0,sk.pts.length-1);""", 1))

# ---- 5. the preview draws the curve ----------------------------------------------------------
reps.append(("""    if(A3D.sk&&A3D.sk.pts.length)drawSketchPath(ctx,V,W,H,A3D.sk.pts,A3D.sk.y,'#ffd479',false,true);""",
"""    /* __acad3dV90: preview the CURVE, not the chords. A rubber band that draws straight and
       commits curved is the interface disagreeing with the model. */
    if(A3D.sk&&A3D.sk.pts.length)drawSketchPath(ctx,V,W,H,
      bimFlattenPoly(A3D.sk.pts,A3D.sk.bulges,false),A3D.sk.y,'#ffd479',false,true);""", 1))

# ---- 6. the finishers carry the bulges through ------------------------------------------------
reps.append(("""  function finishWall(closed){
    var sk=A3D.sk;
    if(!sk||sk.pts.length<2){a3dToast('Wall needs at least 2 points');A3D.sk=null;paint();return;}
    openWallDlg(sk.pts.slice(),sk.y,!!closed);
  }
  function openWallDlg(pts,y0,closed){""",
"""  function finishWall(closed){
    var sk=A3D.sk;
    if(!sk||sk.pts.length<2){a3dToast('Wall needs at least 2 points');A3D.sk=null;paint();return;}
    openWallDlg(sk.pts.slice(),sk.y,!!closed,sk.bulges?sk.bulges.slice():null);   /* __acad3dV90 */
  }
  function openWallDlg(pts,y0,closed,bulges){""", 1))

reps.append(("""      buildWallSolid(pts,y0,hgt,thk,align,closed);""",
"""      buildWallSolid(pts,y0,hgt,thk,align,closed,bulges);   /* __acad3dV90 */""", 1))

reps.append(("""  function finishPoly(){
    var sk=A3D.sk;if(!sk||sk.pts.length<3)return null;
    return addSketchObj(sk.pts.slice());
  }""",
"""  function finishPoly(){
    var sk=A3D.sk;if(!sk||sk.pts.length<3)return null;
    return addSketchObj(sk.pts.slice(),{bulges:sk.bulges});   /* __acad3dV90 */
  }""", 1))

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
