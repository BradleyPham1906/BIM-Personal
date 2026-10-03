"""patch_phase133e.py -- V133e: zoom like AutoCAD and Revit (the owner: "zoom out further ... i feel
a bit limited here").

- The wheel and the pinch held the view between 6 m and 150 m from its target: a block, never a
  street, never the town. Now 0.5 m to 200 km.
- The wheel zooms about the cursor, as AutoCAD's and Revit's do: the point under it stays under it.
- The far clipping plane was a fixed 4 km, so a view zoomed past it would have shown nothing. It
  now reaches eight camera distances, and the near plane follows a very far view out, keeping the
  depth buffer's precision."""
NAME = 'patch_phase133e.py'
BASE = 'f4e62c84c139cee21689ffea43071d6d6091948e807d553f53db2da03008281f'
import hashlib, pathlib, sys
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')
raw = P.read_bytes()
h0 = hashlib.sha256(raw).hexdigest()
if h0 != BASE:
    sys.exit('ABORT: baseline %s, expected %s' % (h0, BASE))
t = raw.decode('utf-8')


def rep(old, new, n=1):
    global t
    c = t.count(old)
    if c != n:
        sys.exit('ABORT: %d occurrences, expected %d: %r' % (c, n, old[:90]))
    t = t.replace(old, new)


rep("""  function onWheel(ev){
    var c=A3D.cam;
    c.dist*=Math.pow(1.0015,ev.deltaY);
    if(c.dist<6)c.dist=6;
    if(c.dist>150)c.dist=150;
    ev.preventDefault();paint();saveSoon();
  }""", """  /* __acad3dV133e: how near and how far the view may go -- a door handle to the whole town */
  var BIM_ZOOM_MIN=0.5,BIM_ZOOM_MAX=200000;
  function bimZoomClamp(d){return d<BIM_ZOOM_MIN?BIM_ZOOM_MIN:(d>BIM_ZOOM_MAX?BIM_ZOOM_MAX:d);}
  /* zoom by a factor about a screen point: the ground under it stays under it, as in AutoCAD and Revit */
  function bimZoomAbout(f,sx,sy){
    var c=A3D.cam,y0=c.ty,p0=(sx==null)?null:groundPoint(sx,sy,y0),p1;
    c.dist=bimZoomClamp(c.dist*f);
    if(p0){
      p1=groundPoint(sx,sy,y0);
      if(p1){c.tx+=p0[0]-p1[0];c.tz+=p0[2]-p1[2];}
    }
    return c.dist;
  }
  function onWheel(ev){
    var xy=cvXY(ev);
    bimZoomAbout(Math.pow(1.0015,ev.deltaY),xy[0],xy[1]);
    ev.preventDefault();paint();saveSoon();
  }""")
rep("""      if(c2.dist<6)c2.dist=6;
      if(c2.dist>150)c2.dist=150;""", """      c2.dist=bimZoomClamp(c2.dist);   /* __acad3dV133e */""")
rep("""    var near=0.5,far=4000;""", """    var near=camDist>1000?camDist/2000:0.5,far=Math.max(4000,camDist*8);   /* __acad3dV133e: the view's own depth */""")
rep("""  window.__acad3dV133d=""", """  window.__acad3dV133e='zoomrange,zoomaboutcursor,farplanefollows';
  window.__a3dZoomAbout=function(f,sx,sy){var d=bimZoomAbout(f,sx,sy);paint();return d;};
  window.__a3dZoomLimits=function(){return [BIM_ZOOM_MIN,BIM_ZOOM_MAX];};
  window.__acad3dV133d=""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
