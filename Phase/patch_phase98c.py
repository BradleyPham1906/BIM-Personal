"""patch_phase98c.py -- __acad3dV98: annotations have grips.

Selecting a dimension or a text label gave it no handles, so the only edit available was to
move the whole thing; nothing about WHAT it measures could be changed on the canvas. Now each
kind shows grips at its defining points, and dragging one re-derives the annotation through
the SAME compute function its creation used (bimComputeDim / bimComputeAngularDim /
bimComputeRadialDim / bimComputeLeader), so an edited dimension cannot disagree with a freshly
drawn one. A drag that would make it degenerate is refused and the annotation stays as it was.

  linear    : [first point, second point, dimension line]   -- offset is kept on a point drag
  angular   : [vertex, first ray point, second ray point]
  radius/dia: [centre, text point]                          -- centre moves the circle
  leader    : [arrow point, elbow, landing side]
  text      : [insertion point]
"""
import hashlib, pathlib

SRC = pathlib.Path('canvas_v10.html')
BASE = '1f94ba565b959bba0908aba36bf942d735c652758fa462562afaa4e7b19cb184'

txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'

EDITS = [
    ("""  function bimGetEditablePoints(o){
    if(!o)return null;
    if(o.t==='sketch')return {pts:o.pts,y:o.y,kind:'sketch'};
    if(o.t==='solid'&&o.bim&&o.bim.type==='wall'&&o.bim.centerline)return {pts:o.bim.centerline,y:o.bim.baseY,kind:'wall'};
    return null;
  }""",
     """  function bimGetEditablePoints(o){
    if(!o)return null;
    if(o.t==='sketch')return {pts:o.pts,y:o.y,kind:'sketch'};
    if(o.t==='solid'&&o.bim&&o.bim.type==='wall'&&o.bim.centerline)return {pts:o.bim.centerline,y:o.bim.baseY,kind:'wall'};
    var ap=bimAnnotGripPoints(o);   /* __acad3dV98 */
    if(ap)return {pts:ap,y:o.y||0,kind:'annot'};
    return null;
  }
  /* ================= __acad3dV98: annotation grips =================
     The grip list and the drag below index the SAME points, in the same order, per kind. */
  function bimAnnotGripPoints(o){
    if(!o)return null;
    if(o.t==='text')return o.pt?[o.pt]:null;
    if(o.t!=='dim')return null;
    var k=bimDimKind(o);
    if(k==='linear'){
      if(!o.p1||!o.p2||!o.d1||!o.d2)return null;
      return [o.p1,o.p2,[(o.d1[0]+o.d2[0])/2,(o.d1[1]+o.d2[1])/2]];
    }
    if(k==='angular')return (o.vertex&&o.ap1&&o.ap2)?[o.vertex,o.ap1,o.ap2]:null;
    if(k==='radius'||k==='diameter')return (o.center&&o.dEdge)?[o.center,o.dEdge]:null;
    if(k==='leader')return (o.anchor&&o.elbow&&o.landing)?[o.anchor,o.elbow,o.landing]:null;
    return null;
  }
  /* Move grip idx of annotation o to p (LOCAL plan coordinates). Returns true when the
     annotation changed; false, with the annotation untouched, when the result would be
     degenerate. */
  function bimDragAnnotPoint(o,idx,p){
    if(!o||!p||!isFinite(p[0])||!isFinite(p[1]))return false;
    p=[p[0],p[1]];
    try{
      if(o.t==='text'){
        if(idx!==0)return false;
        o.pt=p;return true;
      }
      if(o.t!=='dim')return false;
      var k=bimDimKind(o),r;
      if(k==='linear'){
        var a=o.p1,b=o.p2,p3;
        if(idx===2){
          p3=p;
        }else if(idx===0||idx===1){
          /* keep the dimension line at the same signed offset from the measured points */
          var old=bimComputeDim(o.p1,o.p2,o.d1);
          var off=old?old.offset:0;
          if(idx===0)a=p;else b=p;
          var dx=b[0]-a[0],dz=b[1]-a[1],len=Math.sqrt(dx*dx+dz*dz);
          if(len<1e-9)return false;
          p3=[a[0]+(-dz/len)*off,a[1]+(dx/len)*off];
        }else return false;
        r=bimComputeDim(a,b,p3);
        if(!r)return false;
        o.p1=[a[0],a[1]];o.p2=[b[0],b[1]];o.d1=r.d1;o.d2=r.d2;o.length=r.length;
        return true;
      }
      if(k==='angular'){
        var v=o.vertex,q1=o.ap1,q2=o.ap2;
        if(idx===0)v=p;else if(idx===1)q1=p;else if(idx===2)q2=p;else return false;
        r=bimComputeAngularDim(v,q1,q2);
        if(!r)return false;
        o.vertex=[v[0],v[1]];o.ap1=[q1[0],q1[1]];o.ap2=[q2[0],q2[1]];
        o.a1=r.a1;o.sweep=r.sweep;o.arcRadius=r.radius;o.degrees=r.degrees;
        return true;
      }
      if(k==='radius'||k==='diameter'){
        var isD=(k==='diameter');
        if(idx===0){
          var tx=p[0]-o.center[0],tz=p[1]-o.center[1];
          r=bimComputeRadialDim(p,o.radius,[o.dEdge[0]+tx,o.dEdge[1]+tz],isD);
        }else if(idx===1){
          if(Math.abs(p[0]-o.center[0])<1e-9&&Math.abs(p[1]-o.center[1])<1e-9)return false;
          r=bimComputeRadialDim(o.center,o.radius,p,isD);
        }else return false;
        o.center=[r.center[0],r.center[1]];o.dStart=r.start;o.dEdge=r.edge;o.value=r.value;
        return true;
      }
      if(k==='leader'){
        var an=o.anchor,el=o.elbow,tp=[o.elbow[0]+(o.ldir<0?-1:1),o.elbow[1]];
        if(idx===0)an=p;
        else if(idx===1){el=p;tp=[p[0]+(o.ldir<0?-1:1),p[1]];}
        else if(idx===2)tp=p;
        else return false;
        r=bimComputeLeader([an[0],an[1]],[el[0],el[1]],tp);
        o.anchor=r.anchor;o.elbow=r.elbow;o.landing=r.landing;o.ldir=r.dir;
        return true;
      }
    }catch(eA){
      console.warn('[BIM] Annotation grip edit failed for '+(o&&o.name),eA);
      a3dToast('That annotation could not be edited - see the console');
    }
    return false;
  }"""),
    ("""        else if(drag.kind==='wall'){
          bimDragWallPoint(o,drag.idx,[snapped[0],snapped[1]]);
          bimPropagateFrom([o.id],'rebuild');   // __acad3dV52: live -- openings/rooms depending on this wall follow it
        }""",
     """        else if(drag.kind==='wall'){
          bimDragWallPoint(o,drag.idx,[snapped[0],snapped[1]]);
          bimPropagateFrom([o.id],'rebuild');   // __acad3dV52: live -- openings/rooms depending on this wall follow it
        }
        else if(drag.kind==='annot'){   /* __acad3dV98 */
          bimDragAnnotPoint(o,drag.idx,[snapped[0],snapped[1]]);
        }"""),
]

for old, new in EDITS:
    assert txt.count(old) == 1, 'anchor count %d for %r' % (txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)

SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
