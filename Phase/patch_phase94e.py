"""patch_phase94e.py -- __acad3dV94: snapping to, and picking, a construction line.

A construction line that cannot be snapped to is a decoration. The whole reason to draw one is
to catch the place it crosses something, so the snap gather now offers:

  - the ROOT of every construction line on the plane (the only point on an xline that means
    anything),
  - every crossing between a construction line and a sketch or wall on the plane,
  - every crossing between two construction lines.

Also collected here: a V93 gap. bimPickSketch walks segments, and a POINT has one vertex and
therefore no segments, so a point could be selected from the tree or a marquee but never by
clicking on it. That is exactly the "control that reads as finished" law 1 names, and it was
shipped one phase ago.
"""
import hashlib, pathlib

SRC = pathlib.Path('canvas_v10.html')
BASE = 'db155adf4654903f0585cc6a971211ed8a328ef31948547bf0adc44ae973ad5d'

txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'

EDITS = [
    # ---- snap candidates
    ("""      }else if(o.t==='solid'&&o.bim&&o.bim.centerline&&Math.abs((o.bim.baseY||0)+q[1]-y0)<0.05){
        for(j=0;j<o.bim.centerline.length;j++)
          pts.push([o.bim.centerline[j][0]+q[0],o.bim.centerline[j][1]+q[2]]);
      }
    }
    return pts;
  }""",
     """      }else if(o.t==='solid'&&o.bim&&o.bim.centerline&&Math.abs((o.bim.baseY||0)+q[1]-y0)<0.05){
        for(j=0;j<o.bim.centerline.length;j++)
          pts.push([o.bim.centerline[j][0]+q[0],o.bim.centerline[j][1]+q[2]]);
      }else if(bimIsCline(o)&&Math.abs((o.y||0)+q[1]-y0)<0.05){
        /* __acad3dV94: the root. It is the one point on an infinite line that means anything,
           and it is the one a drafter comes back to. */
        pts.push([o.p[0]+q[0],o.p[1]+q[2]]);
      }
    }
    /* __acad3dV94: and where the construction lines CROSS things, which is the whole reason to
       draw one. Gathered after the vertices so a crossing never displaces a real corner that
       sits at the same distance. */
    try{
      var cl=bimClinesOnPlane(y0),ci,cj,hits,hk;
      for(ci=0;ci<cl.length;ci++){
        var C=cl[ci];
        for(j=0;j<A3D.objs.length;j++){
          var t=A3D.objs[j];
          if(bimIsCline(t))continue;
          var tq=bimObjOffset(t),src=null;
          if(t.t==='sketch'&&t.pts&&t.pts.length>=2&&Math.abs((t.y||0)+tq[1]-y0)<0.05)
            src={pts:t.pts,bulges:t.bulges||null,closed:t.closed!==false};
          else if(t.t==='solid'&&t.bim&&t.bim.centerline&&t.bim.centerline.length>=2&&
                  Math.abs((t.bim.baseY||0)+tq[1]-y0)<0.05)
            src={pts:t.bim.centerline,bulges:t.bim.bulges||null,closed:!!t.bim.closed};
          if(!src)continue;
          var moved=src.pts.map(function(p){return [p[0]+tq[0],p[1]+tq[2]];});
          hits=bimClineCrossings(C.p,C.dir,C.ray,moved,src.bulges,src.closed);
          for(hk=0;hk<hits.length;hk++)pts.push(hits[hk]);
        }
        /* Two construction lines crossing is the classic setup-out point. */
        for(cj=ci+1;cj<cl.length;cj++){
          var D=cl[cj];
          var seg=bimClipInfinite(D.p,D.dir,false,bimDrawingExtent2D());
          if(!seg)continue;
          var x2=bimClineSegIntersect(C.p,C.dir,C.ray,seg[0],seg[1]);
          if(x2&&(!D.ray||bimClinePointAhead(D,x2)))pts.push(x2);
        }
      }
    }catch(eX){console.warn('[BIM] Construction-line snap candidates unavailable',eX);}
    return pts;
  }
  /* __acad3dV94: the construction lines sitting on one plan elevation, already offset into
     world coordinates so every caller works in the same space. */
  function bimClinesOnPlane(y0){
    var out=[],i,o,q;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(!bimIsCline(o))continue;
      var lyr=bimLayerOf(o);
      if(lyr&&lyr.visible===false)continue;
      q=bimObjOffset(o);
      if(Math.abs((o.y||0)+q[1]-y0)>0.05)continue;
      out.push({id:o.id,p:[o.p[0]+q[0],o.p[1]+q[2]],dir:[o.dir[0],o.dir[1]],ray:!!o.ray});
    }
    return out;
  }
  function bimClinePointAhead(C,pt){
    if(!C.ray)return true;
    return (pt[0]-C.p[0])*C.dir[0]+(pt[1]-C.p[1])*C.dir[1]>=-1e-9;
  }"""),

    # ---- picking: clines, and the V93 point gap
    ("""      var pts=bimFlattenSketch(o),n=pts.length,segCount=(o.closed!==false)?n:n-1,k;
      for(k=0;k<segCount;k++){""",
     """      /* __acad3dV94, collecting a V93 gap: a POINT has one vertex and therefore no
         segments, so the segment walk below could never reach it and a point was selectable
         from the tree and by marquee but not by clicking the thing itself. */
      if(bimIsPoint(o)){
        var pp=toScreen(bimWorldPt(o,o.pts[0],o.y),V,W,H);
        var dP=Math.sqrt((x-pp[0])*(x-pp[0])+(y-pp[1])*(y-pp[1]));
        if(dP<bestD){bestD=dP;best=o;}
        continue;
      }
      var pts=bimFlattenSketch(o),n=pts.length,segCount=(o.closed!==false)?n:n-1,k;
      for(k=0;k<segCount;k++){"""),

    ("""    return best||bimPickRoom(x,y)||bimPickDim(x,y)||bimPickText(x,y);
  }""",
     """    return best||bimPickCline(x,y)||bimPickRoom(x,y)||bimPickDim(x,y)||bimPickText(x,y);
  }
  /* __acad3dV94: picked on the piece that is DRAWN, which is the clipped segment -- the same
     one bimClineVisibleSeg hands the renderer, so a construction line is selectable exactly
     where it appears and nowhere else. */
  function bimPickCline(x,y){
    var V=camVecs(A3D.cam),W=cvW(),H=cvH();
    var best=null,bestD=8,i,o,box=null;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(!bimIsCline(o))continue;
      var lyr=bimLayerOf(o);
      if(lyr&&(lyr.visible===false||lyr.locked))continue;
      if(!box)box=bimDrawingExtent2D();
      var seg=bimClineVisibleSeg(o,box);
      if(!seg)continue;
      var pa=toScreen(bimWorldPt(o,seg[0],o.y),V,W,H);
      var pb=toScreen(bimWorldPt(o,seg[1],o.y),V,W,H);
      var d=bimPointSegDist(x,y,pa[0],pa[1],pb[0],pb[1]);
      if(d<bestD){bestD=d;best=o;}
    }
    return best;
  }"""),

    # ---- Copy translates the root and leaves the direction alone
    ("""  function bimDuplicateObject(o,dx,dz){
    var copy;
    if(o.t==='opening')return null;""",
     """  function bimDuplicateObject(o,dx,dz){
    var copy;
    if(o.t==='opening')return null;
    if(bimIsCline(o)){          /* __acad3dV94: a translation moves the root, never the angle */
      copy=JSON.parse(JSON.stringify(o));
      copy.id='a3d-'+Date.now().toString(36)+'-'+(A3D.seq++);
      copy.p=[o.p[0]+dx,o.p[1]+dz];
      copy.name=o.name+' copy';
      return copy;
    }"""),

    # ---- properties
    ("""    }else if(bimIsPoint(o)){                    /* __acad3dV93 */""",
     """    }else if(bimIsCline(o)){                    /* __acad3dV94 */
      dims+=bimPropText('Through',o.p[0].toFixed(3)+', '+o.p[1].toFixed(3));
      dims+=bimPropText('Angle',(Math.atan2(o.dir[1],o.dir[0])*180/Math.PI).toFixed(3)+' deg');
      dims+=bimPropText('Extent',o.ray?'One direction (ray)':'Both directions (xline)');
    }else if(bimIsPoint(o)){                    /* __acad3dV93 */"""),

    ("""    if(bimIsPoint(o))return 'Points : Nodes';   /* __acad3dV93 */""",
     """    if(bimIsCline(o))return 'Lines : Construction Lines';   /* __acad3dV94 */
    if(bimIsPoint(o))return 'Points : Nodes';   /* __acad3dV93 */"""),
]

for old, new in EDITS:
    assert txt.count(old) == 1, 'anchor count %d for %r' % (txt.count(old), old[:64])
    txt = txt.replace(old, new, 1)

SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
