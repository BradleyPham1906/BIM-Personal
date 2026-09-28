"""patch_phase93d.py -- __acad3dV93: CIRCLE draws a circle.

finishCircle predated arc storage and tessellated into a 24-sided polygon: 24 grips, a
circumference 0.5% short and an area out by 0.14 m2 on a 2 m circle. Two vertices with bulge 1
each is exact, is what DXF stores, and is what every other consumer in this build has been able
to read since V88.
"""
import hashlib, pathlib

SRC = pathlib.Path('canvas_v10.html')
BASE = 'ef920a376dba0422b3e8c896c0800053b944bd895c5fb592a81c08f126e1440d'

txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'

OLD = """  function finishCircle(){
    var sk=A3D.sk;if(!sk||sk.pts.length<2)return null;
    var c=sk.pts[0],e=sk.pts[1];
    var r=Math.sqrt((e[0]-c[0])*(e[0]-c[0])+(e[1]-c[1])*(e[1]-c[1]));
    if(r<0.05){a3dToast('Circle is too small');sk.pts=[];paint();return null;}
    var pts=[],i,n=24;
    for(i=0;i<n;i++){
      var an=i/n*Math.PI*2;
      pts.push([c[0]+Math.cos(an)*r,c[1]+Math.sin(an)*r]);
    }
    return addSketchObj(pts);
  }"""

NEW = """  /* __acad3dV93: two vertices, both bulge 1. The 24-gon this replaces was the last piece of
     geometry in the build that approximated a shape the storage can hold exactly. */
  function finishCircle(){
    var sk=A3D.sk;if(!sk||sk.pts.length<2)return null;
    var c=sk.pts[0],e=sk.pts[1];
    var r=Math.sqrt((e[0]-c[0])*(e[0]-c[0])+(e[1]-c[1])*(e[1]-c[1]));
    if(r<0.05){a3dToast('Circle is too small');sk.pts=[];paint();return null;}
    var cir=bimCircleSketch(c,r);
    if(!cir||cir.error){
      console.warn('[BIM] Circle could not be built',c,r,cir&&cir.error);
      sk.pts=[];paint();
      a3dToast(cir&&cir.error?cir.error:'That circle could not be built');
      return null;
    }
    return addSketchObj(cir.pts,{bulges:cir.bulges,
      toast:'Circle created, radius '+bimFmtLen(r)});
  }"""

assert txt.count(OLD) == 1, 'anchor count %d' % txt.count(OLD)
txt = txt.replace(OLD, NEW, 1)

SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
