"""patch_phase123d.py -- V123: dragging an object by its body is the gizmo's move.

Every reference tool moves a selected object when it is dragged, and moves it the way its move
tool does: Revit and SketchUp snap it to the points of other elements, Rhino's snappy dragging uses
object snaps, AutoCAD takes a typed distance. This app had two moves. The gizmo's (V76 to V112)
snaps to points and the grid, reads out, takes a typed distance, is cancelled by Escape, is one
undo step and settles what depends on the objects once at the end. The body drag -- the move most
used, because it needs no handle -- did none of it:

1. It was not an undo step. Measured on V122: place a box, drag it by its body, Ctrl+Z -- the box
   was deleted, because the undo went to the step before the drag.
2. It snapped to nothing: no grid, no point of another object.
3. A distance could not be typed and Escape did not call it off.

The press now arms it, and its first movement (past the same three pixels as before) builds the
gizmo's own plan-move record -- in the horizontal plane through the point where the cursor meets
the object, so the object stays under the cursor where it was taken, at any camera -- and from
there it IS the gizmo's move: the undo step, snapping, the read-out, typed X,Y, Escape, and the one
end path with its propagation. Alt+drag lifts it straight up, as it did, now as the vertical
arrow's drag, following the cursor instead of an arbitrary rate -- in a 3D view; a plan looks down
the vertical and says so. The old body-drag code in onMove and onUp is removed with it.

bimRayHitObject is where the cursor meets an object: each face met on its own plane and tested
inside its own outline, so a concave face is not taken for the hull of its corners."""
NAME = 'patch_phase123d.py'
BASE = '905c4c2875e98787d5f541c124a607196b9af9d72128ac1e789db2c4897df982'
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

# 1. where the cursor meets an object, and the body drag's start
rep("""  /* A plane square: a parallelogram part-way along two axes. Dropped when either arrow is missing""",
"""  /* __acad3dV123: WHERE THE CURSOR MEETS AN OBJECT -- the point, the face (its index in the object's
     mesh) and that face's normal as its corners run, or null. Each face is met on its own plane and
     tested inside its own outline, so a concave face (an L-shaped pad's top) is not taken for the
     hull of its corners, which a fan of triangles from its first corner would be. The pick's
     painter's order sorts whole faces by average depth: a picture of what is in front, not an
     intersection. */
  function bimFaceWorldPts(o,m,fi){
    var q=bimObjOffset(o),fc=m.f[fi],out=[],i;
    for(i=0;i<fc.length;i++){var v=m.v[fc[i]];out.push([v[0]+q[0],v[1]+q[1],v[2]+q[2]]);}
    return out;
  }
  function bimPointInFace(P,pts,N){
    /* in the two coordinates the face is widest in: drop the normal's largest component */
    var ax=Math.abs(N[0]),ay=Math.abs(N[1]),az=Math.abs(N[2]),u,v,i,j,inside=false;
    if(ax>=ay&&ax>=az){u=1;v=2;}else if(ay>=az){u=0;v=2;}else{u=0;v=1;}
    for(i=0,j=pts.length-1;i<pts.length;j=i++){
      var xi=pts[i][u],yi=pts[i][v],xj=pts[j][u],yj=pts[j][v];
      if(((yi>P[v])!==(yj>P[v]))&&(P[u]<(xj-xi)*(P[v]-yi)/(yj-yi)+xi))inside=!inside;
    }
    return inside;
  }
  function bimRayHitObject(o,sx,sy){
    var m=o?meshOf(o):null;
    if(!m||!m.v||!m.f||!m.f.length)return null;
    var r=bimScreenRay(sx,sy),best=null,i;
    for(i=0;i<m.f.length;i++){
      if(!m.f[i]||m.f[i].length<3)continue;
      var pts=bimFaceWorldPts(o,m,i),N=faceNormal(pts);
      if(!N||!isFinite(N[0])||!isFinite(N[1])||!isFinite(N[2]))continue;
      var dn=vdot(r.d,N);
      if(Math.abs(dn)<1e-9)continue;
      var t=(vdot(pts[0],N)-vdot(r.o,N))/dn;
      if(!isFinite(t)||t<=0||(best&&t>=best.t))continue;
      var P=[r.o[0]+r.d[0]*t,r.o[1]+r.d[1]*t,r.o[2]+r.d[2]*t];
      if(!bimPointInFace(P,pts,N))continue;
      best={fi:i,t:t,P:P,N:N};
    }
    return best;
  }
  /* The point an object was taken by: on its solid where it has one, otherwise on its own plan plane
     (a sketch, a room, a dimension) or at its height (a note). */
  function bimGrabPoint(o,x,y){
    var h=bimRayHitObject(o,x,y);
    if(h)return h.P;
    var planar=(o.t==='sketch'||o.t==='room'||o.t==='text'||o.t==='dim'||bimIsHatch(o));
    var elev=planar?bimWorldElev(o,o.y):((o.pos&&o.pos[1])||0);
    return groundPoint(x,y,elev);
  }
  /* __acad3dV123: DRAGGING AN OBJECT BY ITS BODY IS THE GIZMO'S MOVE. V122's body drag was a second,
     lesser move: no undo step (placing a box, dragging it and pressing Ctrl+Z deleted the box, the
     undo going to the step before the drag), no snapping, no typed distance, no Escape. Its first
     movement builds the gizmo's own record -- the plan move in the horizontal plane through the point
     grabbed, so the object stays under the cursor where it was taken, or with Alt the vertical
     arrow's drag -- and from there everything is the gizmo's. The objects are the gizmo's too: the
     selection when the pressed object is in it, the pressed object otherwise. */
  function bimBodyDragStart(bd){
    var o=objById(bd.id);
    if(!o)return null;
    var ids=bimGizmoIds();
    if(ids.indexOf(o.id)<0)ids=[o.id];
    var P=bimGrabPoint(o,bd.x,bd.y),rec;
    if(!P){
      console.warn('[BIM] Body drag: the press did not meet the object or its plane.');
      a3dToast('Tilt the view a little to drag '+o.name);
      return null;
    }
    if(bd.vert){
      var V=camVecs(A3D.cam),W=cvW(),H=cvH();
      var s0=toScreen(P,V,W,H),s1=toScreen([P[0],P[1]+1,P[2]],V,W,H);
      var sr=toScreen([P[0]+V.r[0],P[1]+V.r[1],P[2]+V.r[2]],V,W,H);
      var sx=s1[0]-s0[0],sy=s1[1]-s0[1],len2=sx*sx+sy*sy;
      var ref=(sr[0]-s0[0])*(sr[0]-s0[0])+(sr[1]-s0[1])*(sr[1]-s0[1]);
      /* the arrows' own rule for an axis seen end-on: shorter than edgeOn of a screen-parallel one */
      if(!isFinite(len2)||!(len2>=A3D_GIZ.edgeOn*A3D_GIZ.edgeOn*ref)||len2<1e-4){
        console.warn('[BIM] Alt-drag: the vertical points at the camera in this view.');
        a3dToast('Lifting needs a 3D view - here the vertical points straight at you');
        return null;
      }
      rec={giz:true,gk:'axis',axis:'y',dir:[0,1,0],sx:sx,sy:sy,len2:len2,
           ids:ids,start:bimGizmoStarts(ids),x0:bd.x,y0:bd.y,snaps:bimGizmoSnapSetup(ids),
           fine:false,gizDist:0,gizVec:[0,0,0],moved:true,body:true};
    }else{
      var N=[0,1,0];
      if(!bimRayPlane(bd.x,bd.y,P,N,0.05)){
        console.warn('[BIM] Body drag: the view looks along the ground plane.');
        a3dToast('Tilt the view to drag in the plan - you are looking along the ground; Alt+drag lifts');
        return null;
      }
      rec={giz:true,gk:'plane',plane:'body',a:[1,0,0],b:[0,0,-1],n:N,
           labA:bimGizAxis('x').lab,labB:bimGizAxis('z').lab,snapWorld:false,O:P.slice(),P0:P.slice(),
           snaps:bimGizmoSnapSetup(ids),fine:false,
           ids:ids,start:bimGizmoStarts(ids),x0:bd.x,y0:bd.y,da:0,db:0,gizVec:[0,0,0],moved:true,body:true};
    }
    A3D_MATERIALIZED=[];
    pushUndo();
    return rec;
  }
  /* A plane square: a parallelogram part-way along two axes. Dropped when either arrow is missing""")

# 2. the press arms it
rep("""        drag.mv=hit;drag.my=hit.pos[1];drag.vert=ev.altKey;
        drag.mvObjStart=[hit.pos[0],hit.pos[1],hit.pos[2]];
        /* __acad3dV99: where on the object it was grabbed, so it moves by the drag, not to it */
        var gGrab=groundPoint(xy[0],xy[1],drag.my);
        drag.mvGrab=gGrab?[gGrab[0]-hit.pos[0],gGrab[2]-hit.pos[2]]:[0,0];
        if(A3D.selSet&&A3D.selSet.length>1&&A3D.selSet.indexOf(hit.id)>=0){
          drag.mvGroup=A3D.selSet.filter(function(id){var oo=objById(id);return oo&&!bimIsLocked(oo);});
          drag.mvStart=drag.mvGroup.map(function(id){var oo=objById(id);return oo?[oo.pos[0],oo.pos[1],oo.pos[2]]:null;});
          var g0=groundPoint(xy[0],xy[1],drag.my);
          drag.mvOrigin=g0?[g0[0],g0[2]]:[0,0];
        }""", """        /* __acad3dV123: armed here; its first movement makes it the gizmo's move (bimBodyDragStart).
           It still moves by the drag and not to it (V99): the plane goes through the point grabbed. */
        drag.body={id:hit.id,x:xy[0],y:xy[1],vert:!!ev.altKey};""")

# 3. the first movement makes it the gizmo's; the old body-drag branch goes
rep("""    if(drag.mv){
      if(drag.vert){
        var vdy=-dy*Math.max(A3D.cam.dist,6)*0.003;
        if(drag.mvGroup){
          var gi;
          for(gi=0;gi<drag.mvGroup.length;gi++){
            var go=objById(drag.mvGroup[gi]);
            if(go)go.pos[1]+=vdy;
          }
        }else{
          drag.mv.pos[1]+=vdy;
        }
        paint();saveSoon();
        return;
      }
      if(drag.mvGroup){
        var gNow=groundPoint(xy[0],xy[1],drag.my);
        if(gNow){
          var totalDx=gNow[0]-drag.mvOrigin[0],totalDz=gNow[2]-drag.mvOrigin[1],gj;
          for(gj=0;gj<drag.mvGroup.length;gj++){
            var gobj=objById(drag.mvGroup[gj]);
            if(gobj&&drag.mvStart[gj]){gobj.pos[0]=drag.mvStart[gj][0]+totalDx;gobj.pos[2]=drag.mvStart[gj][2]+totalDz;}
          }
          paint();saveSoon();
        }
        return;
      }
      var g=groundPoint(xy[0],xy[1],drag.my);
      if(g){   /* __acad3dV99: by the grab offset -- it used to jump its origin under the cursor */
        var gb=drag.mvGrab||[0,0];
        drag.mv.pos[0]=g[0]-gb[0];drag.mv.pos[2]=g[2]-gb[1];paint();saveSoon();
      }
      return;
    }""", """    if(drag.body){   /* __acad3dV123: from here on the gizmo's move */
      var bodyRec=bimBodyDragStart(drag.body);
      if(!bodyRec){drag=null;paint();return;}
      drag=bodyRec;
      bimGizmoApply(xy);
      return;
    }""")

# 4. the release: the gizmo's end path settles it, so the body drag's own ending goes
rep("""    var mvObj=drag.mv,mvGroup=drag.mvGroup,mvObjStart=drag.mvObjStart,mvStart=drag.mvStart;
""", "")
span("""    /* __acad3dV55: the continuous drag-move handler (onMove's drag.mv/drag.mvGroup branches)""",
     """    if(gizMenu&&!moved){bimOpenGizmoMenu(gizMenu.x,gizMenu.y);return;}   /* __acad3dV110 */""",
"""    /* __acad3dV55 deferred a body drag's propagation to one walk with the gesture's total delta.
       __acad3dV123: a body drag is the gizmo's move, and the gizmo's end path (above) is that walk. */
""", 20)
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
