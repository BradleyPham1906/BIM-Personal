"""patch_phase97d.py -- __acad3dV97: ADD VERTEX, the operation the user was reaching for.

The user described adding vertices to a rectangle or polygon and watching the room follow. No
such operation existed: a sketch's vertices could be moved and nothing more. So the report
could not have been reproduced exactly as described -- the thing being done was not possible.

AutoCAD's answer is the midpoint grip on a polyline segment: drag it and a new vertex is
inserted there. That is what this adds, for sketches:

  - a midpoint grip on every segment, drawn smaller and hollow so it cannot be mistaken for a
    vertex grip, and placed at the SWEEP midpoint on an arc, where the curve actually is;
  - pressing it inserts the vertex and hands the drag straight to the ordinary vertex drag, so
    everything a vertex drag already does -- snapping, constraints, live propagation to rooms
    and slabs -- applies to the new vertex with no second copy of that logic;
  - an arc segment is split into two arcs on the SAME circle, through V95's bimArcBulgeBetween,
    so inserting a vertex on a curve does not straighten it.

Two things that would otherwise be quietly wrong afterwards are handled at the insert:
constraint references are INDICES into o.pts, so every index after the insert point shifts by
one -- or a 'horizontal' constraint would start holding two different points together -- and
the insert propagates immediately, so a room re-derives its vertex count without waiting for
the drag to move.

Walls are deliberately excluded. A wall vertex hosts openings along the segments either side,
and re-hosting them on an insert is its own piece of work.
"""
import hashlib, pathlib

SRC = pathlib.Path('canvas_v10.html')
BASE = 'e42f452da202c1bb7be0a8a504852b936a9f0da49d05d49a8ddeefb7f6422439'

txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'

EDITS = [
    ("""  function bimDragSketchPoint(o,idx,newXZ){""",
     """  /* ================= __acad3dV97: add a vertex to a sketch ================= */
  function bimSketchSegCount(o){
    if(!o||!o.pts||o.pts.length<2)return 0;
    return (o.closed!==false)?o.pts.length:o.pts.length-1;
  }
  /* The midpoint of one segment, measured along the CURVE -- on an arc that is the sweep
     midpoint, which is where the segment actually is. */
  function bimSketchSegMid(o,seg){
    var n=o.pts.length,A=o.pts[seg],B=o.pts[(seg+1)%n];
    var arc=bimBulgeArc(A,B,bimBulgeAt(o.bulges,seg));
    if(arc)return bimArcPointAt(arc,0.5);
    return [(A[0]+B[0])/2,(A[1]+B[1])/2];
  }
  function bimInsertSketchVertex(o,seg,pt){
    if(!o||o.t!=='sketch'||bimIsPoint(o)||!o.pts)return {error:'Only a sketch takes an added vertex'};
    var segs=bimSketchSegCount(o);
    if(!(seg>=0&&seg<segs)||Math.floor(seg)!==seg)return {error:'There is no such segment'};
    var n=o.pts.length,A=o.pts[seg],B=o.pts[(seg+1)%n];
    var b=bimBulgeAt(o.bulges,seg),b1=0,b2=0;
    if(Math.abs(b)>BIM_BULGE_EPS){
      /* Both halves on the SAME circle, so a curve stays a curve. */
      var arc=bimBulgeArc(A,B,b);
      if(arc){
        var sg=arc.sweep>=0?1:-1;
        b1=bimArcBulgeBetween(arc.center,A,pt,sg);
        b2=bimArcBulgeBetween(arc.center,pt,B,sg);
      }
    }
    o.pts.splice(seg+1,0,[pt[0],pt[1]]);
    if(bimHasBulge(o.bulges)||Math.abs(b1)>BIM_BULGE_EPS||Math.abs(b2)>BIM_BULGE_EPS){
      var nb=[],i;
      for(i=0;i<n;i++){
        if(i===seg){nb.push(b1,b2);}
        else nb.push(bimBulgeAt(o.bulges,i));
      }
      o.bulges=nb;
    }
    /* Constraint references are indices into o.pts. Every index past the insert moves up by
       one, or the constraint would silently start holding two different points together. */
    if(o.constraints&&o.constraints.length){
      var c,k;
      for(c=0;c<o.constraints.length;c++){
        var refs=o.constraints[c].refs||[];
        for(k=0;k<refs.length;k++)if(refs[k]>seg)refs[k]++;
      }
    }
    return {idx:seg+1};
  }
  function bimDragSketchPoint(o,idx,newXZ){"""),

    # --- midpoint grips, sketches only, drawn so they cannot be mistaken for vertex grips
    ("""      ctx.strokeRect(sp[0]-4,sp[1]-4,8,8);
      ctx.restore();
    }
  }
  // ---- __acad3dV45: Sketch geometric constraints""",
     """      ctx.strokeRect(sp[0]-4,sp[1]-4,8,8);
      ctx.restore();
    }
    /* __acad3dV97: a midpoint grip on every segment of a sketch -- drag it to add a vertex.
       Smaller and hollow, so it reads as "insert here" and never as a vertex. Pushed AFTER the
       vertex grips, and bimPickGrip prefers the nearest, so on a very short segment a vertex
       still wins a tie. */
    if(ep.kind==='sketch'&&!bimIsPoint(o)&&!(A3D.conPick&&o.id===A3D.sel)){
      var segs=bimSketchSegCount(o),s,mp,msp;
      for(s=0;s<segs;s++){
        mp=bimSketchSegMid(o,s);
        msp=toScreen(bimWorldPt(o,mp,ep.y),V,W,H);
        A3D.grips.push({x:msp[0],y:msp[1],seg:s,mid:true,objId:o.id,kind:'sketch',elev:wElev});
        ctx.save();
        ctx.strokeStyle='#4ea1ff';ctx.lineWidth=1.2;
        ctx.fillStyle='rgba(13,17,23,0.85)';
        ctx.fillRect(msp[0]-3,msp[1]-3,6,6);
        ctx.strokeRect(msp[0]-3,msp[1]-3,6,6);
        ctx.restore();
      }
    }
  }
  // ---- __acad3dV45: Sketch geometric constraints"""),

    # --- pressing a midpoint grip inserts, then hands over to the ordinary vertex drag
    ("""      var grip=bimPickGrip(xy[0],xy[1]);
      if(grip){
        pushUndo();
        drag={grip:true,objId:grip.objId,idx:grip.idx,kind:grip.kind,elev:grip.elev,moved:false};""",
     """      var grip=bimPickGrip(xy[0],xy[1]);
      if(grip&&grip.mid){
        /* __acad3dV97: insert, then become an ordinary vertex drag on the new point, so the new
           vertex snaps, obeys constraints and propagates exactly as any other vertex does. */
        pushUndo();
        var mo=objById(grip.objId);
        var ins=mo?bimInsertSketchVertex(mo,grip.seg,bimSketchSegMid(mo,grip.seg)):{error:'That sketch no longer exists'};
        if(ins.error){a3dToast('Add vertex: '+ins.error);ev.preventDefault();return;}
        bimPropagateFrom([mo.id],'rebuild');
        drag={grip:true,objId:grip.objId,idx:ins.idx,kind:'sketch',elev:grip.elev,moved:false};
        refreshProps();paint();saveSoon();
        ev.preventDefault();
        return;
      }
      if(grip){
        pushUndo();
        drag={grip:true,objId:grip.objId,idx:grip.idx,kind:grip.kind,elev:grip.elev,moved:false};"""),

    # --- test surface
    ("""  /* __acad3dV96 */
  window.__a3dPatternRotation=bimPatternRotation;""",
     """  /* __acad3dV97 */
  window.__a3dSourceBoundaryWorld=function(id){var b=bimSourceBoundaryWorld(objById(id));return b;};
  window.__a3dFollowSource=function(id){var ctx={};var ok=bimFollowSource(objById(id),ctx);return {ok:ok,ctx:ctx};};
  window.__a3dSourceOf=function(id){var o=objById(id);return o?{id:bimGraphRoomSourceId(o),type:bimSourceTypeOf(o)}:null;};
  window.__a3dInsertSketchVertex=function(id,seg,pt){
    var o=objById(id);
    var r=bimInsertSketchVertex(o,seg,pt||(o?bimSketchSegMid(o,seg):null));
    if(!r.error)bimPropagateFrom([id],'rebuild');
    return r;
  };
  window.__a3dSketchSegMid=function(id,seg){var o=objById(id);return o?bimSketchSegMid(o,seg):null;};
  window.__a3dGrips=function(){return (A3D.grips||[]).map(function(g){return {x:g.x,y:g.y,idx:g.idx,seg:g.seg,mid:!!g.mid,objId:g.objId};});};
  window.__acad3dV97='sourcecontract,everydependentfollows,dependentframe,cutsaysso,addvertex,constraintindexshift,chainedsources';
  /* __acad3dV96 */
  window.__a3dPatternRotation=bimPatternRotation;"""),
]

for old, new in EDITS:
    assert txt.count(old) == 1, 'anchor count %d for %r' % (txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)

SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
