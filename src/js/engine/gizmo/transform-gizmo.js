  /* ================= __acad3dV76: the translate gizmo =================
     Attached to the selection, recomputed from live geometry every frame. */
  /* edgeOn: an axis projecting to less than this FRACTION of the best-projecting axis's
   pixels-per-world-unit is too foreshortened to drag, and is hidden rather than drawn. */
  /* ring: the rotate handle's screen radius, a little outside the arrow tips so the two
     handles never overlap in the pick radius. ringSeg is how many segments the circle is
     projected as -- the ring is an ELLIPSE in any 3D view, so it cannot be drawn with
     ctx.arc and has to be projected point by point like any other world geometry. */
  /* ================= __acad3dV110: the transform gizmo, reworked =================

     V76 gave the selection three move arrows and V78 a ring that turns it about the vertical.
     This phase completes the handle set the reference tools share (Revit's move gizmo, Unity's
     transform handles, the Vertex Tools gizmo):

       - an arrow moves along one axis (V76, unchanged in behaviour);
       - a square between two arrows moves in that plane;
       - the square on the origin moves freely: in the plan plane in a 2D view, in the screen
         plane in 3D;
       - the blue ring turns about the vertical (V78);
       - the red and green arcs tilt about X and Y, and the boxes at the far ends of the axes
         scale along them (Shift for an even scale). These are drawn only when EVERY selected
         object can follow them: generic solids tilt and scale in 3D, a sketch scales in plan,
         and a building element does neither -- a wall that leans is no longer a wall;
       - a right-click on any handle opens the gizmo's menu: align to World, Local or View, or
         hide it (the GIZMO command brings it back).

     Colours are Revit's: X red (east), Y green (north), Z blue (up). The internal KEYS stay the
     model's own axis names so every earlier suite keeps its meaning: 'y' is the model's
     vertical, which Revit calls Z, and 'z' is the model's north-south axis, which Revit calls Y.
     Project north is -z, so the Y arrow points along -z. */
  var A3D_GIZ={arm:74,head:13,pick:10,minArm:26,edgeOn:0.16,ring:96,ringSeg:72,ringPick:9,
               centre:7,plane0:0.30,plane1:0.54,planeFlat:0.25,planeClear:14,box:5.5,arcSeg:24,arcFlat:0.22,
               viewRing:1.18,uniform:0.55,farFade:0.26,     /* __acad3dV111 */
               snapSrc:24,snapTgt:400,fine:0.25,            /* __acad3dV112 */
               click:3,                                     /* __acad3dV123: a press that travels no further is a click, */
               clickWait:280};                              /* and its value box waits out a double-click */
  var A3D_GIZ_AXES=[
    {k:'x',col:'#ff5f56',lab:'X'},
    {k:'z',col:'#5ec98a',lab:'Y'},
    {k:'y',col:'#4ea1ff',lab:'Z'}
  ];
  /* The planes a square moves in, named by the two axes that span them, each drawn in the colour
     of the axis it leaves out -- the plan square is blue because it moves everything except Z. */
  var A3D_GIZ_PLANES=[
    {k:'xz',a:'x',b:'z',n:'y'},
    {k:'xy',a:'x',b:'y',n:'z'},
    {k:'zy',a:'z',b:'y',n:'x'}
  ];
  var A3D_ORIGIN_AXES=[
    {k:'X',to:[13,0,0],col:'#8a4a4a'},
    {k:'Y',to:[0,0,-13],col:'#4f8a5f'},
    {k:'Z',to:[0,13,0],col:'#3f5b82'}
  ];
  function bimGizAxis(k){
    var i;
    for(i=0;i<A3D_GIZ_AXES.length;i++)if(A3D_GIZ_AXES[i].k===k)return A3D_GIZ_AXES[i];
    return null;
  }
  /* The ids the gizmo acts on: the multi-selection if there is one, otherwise the single
     selection. Locked objects are dropped here rather than at drag time so that a selection of
     only locked objects shows no gizmo at all -- a handle that refuses every drag is worse than
     no handle. */
  function bimGizmoIds(){
    var ids=(A3D.selSet&&A3D.selSet.length)?A3D.selSet.slice():(A3D.sel?[A3D.sel]:[]);
    return ids.filter(function(id){
      var o=objById(id);
      if(!o||bimIsLocked(o))return false;
      if(!bimLayerSelectable(o))return false;   /* __acad3dV121: what the selection may hold */
      return true;
    });
  }
  /* World centre of everything the gizmo will move. Read from the objects THEMSELVES on every
     call -- never cached at selection time, which is the mistake Phase 75 had to undo for grips. */
  function bimGizmoCenter(o){
    var q=bimObjOffset(o),i;
    var m=meshOf(o);
    if(m&&m.v&&m.v.length){
      var a=[Infinity,Infinity,Infinity],b=[-Infinity,-Infinity,-Infinity],k;
      for(i=0;i<m.v.length;i++)for(k=0;k<3;k++){
        var v=m.v[i][k];
        if(v<a[k])a[k]=v;
        if(v>b[k])b[k]=v;
      }
      return [(a[0]+b[0])/2+q[0],(a[1]+b[1])/2+q[1],(a[2]+b[2])/2+q[2]];
    }
    /* Plan-point objects (sketches, rooms) have no mesh. Their centre is the centroid of their
       own points at their own elevation -- the same world transform every other consumer uses
       since Phase 75, not a second interpretation of it. */
    var pts=o.pts;
    if(!pts||!pts.length)return null;
    var mnx=Infinity,mxx=-Infinity,mnz=Infinity,mxz=-Infinity;
    for(i=0;i<pts.length;i++){
      if(pts[i][0]<mnx)mnx=pts[i][0];
      if(pts[i][0]>mxx)mxx=pts[i][0];
      if(pts[i][1]<mnz)mnz=pts[i][1];
      if(pts[i][1]>mxz)mxz=pts[i][1];
    }
    return [(mnx+mxx)/2+q[0],(o.y||0)+q[1],(mnz+mxz)/2+q[2]];
  }
  function bimGizmoOrigin(ids){
    /* __acad3dV112: a pivot the user has placed wins over the selection's middle. Every handle
       reads the origin from here, so a rotation, a scale and the arrows all move to it together. */
    if(A3D.gizPivot&&ids&&ids.length)return A3D.gizPivot.slice();
    var i,n=0,sx=0,sy=0,sz=0;
    for(i=0;i<ids.length;i++){
      var o=objById(ids[i]);
      if(!o)continue;
      var c=bimGizmoCenter(o);
      if(!c||!isFinite(c[0])||!isFinite(c[1])||!isFinite(c[2]))continue;
      sx+=c[0];sy+=c[1];sz+=c[2];n++;
    }
    return n?[sx/n,sy/n,sz/n]:null;
  }
  /* The gizmo as SCREEN geometry. Each arm is scaled so that all three are the same pixel length,
     measured through the app's own projection rather than assumed: a perspective view foreshortens
     the three axes by different amounts, so a single world length cannot give three equal arms.
     An arm whose projection is shorter than minArm is dropped -- in a plan view that is the
     vertical axis, which points at the camera and cannot be dragged, and a 4px stub on the origin
     would be a control that looks live and does nothing. */
  function bimGizmoGeom(V,W,H){
    var ids=bimGizmoIds();
    if(!ids.length)return null;
    var o=bimGizmoOrigin(ids);
    if(!o)return null;
    var so=toScreen(o,V,W,H);
    if(!isFinite(so[0])||!isFinite(so[1]))return null;
    /* Measure how many screen pixels ONE world unit along each axis is worth, BEFORE any
       scaling. This is the only honest place to decide whether an axis is edge-on: the scaling
       step below stretches every axis to the same pixel length by construction, so a length test
       applied after it can never fail -- which is exactly the mistake the first version of this
       function made. In a plan view the vertical axis points straight at the camera, its true
       pxPerUnit is ~0, and scaling it to 74px produced a full-size arm that looked draggable and
       moved the object by kilometres per pixel. __acad3dV110: measured along the FRAME's axes --
       World, Local or View -- rather than fixed world ones. */
    var fr=bimGizmoFrame(ids);
    var raw=[],i,maxPx=0;
    for(i=0;i<A3D_GIZ_AXES.length;i++){
      var ax=A3D_GIZ_AXES[i],d=fr[ax.k];
      var probe=toScreen([o[0]+d[0],o[1]+d[1],o[2]+d[2]],V,W,H);
      if(!isFinite(probe[0])||!isFinite(probe[1])){raw.push(null);continue;}
      var vx=probe[0]-so[0],vy=probe[1]-so[1];
      var pxPerUnit=Math.sqrt(vx*vx+vy*vy);
      if(!isFinite(pxPerUnit))pxPerUnit=0;
      raw.push({ax:ax,d:d,px:pxPerUnit});
      if(pxPerUnit>maxPx)maxPx=pxPerUnit;
    }
    if(maxPx<=1e-9)return null;
    var arms=[];
    for(i=0;i<raw.length;i++){
      if(!raw[i])continue;
      /* Compared against the BEST-projecting axis rather than against an absolute pixel figure,
         so the same rule holds at any zoom: what matters is that this axis is foreshortened
         relative to the others, not how far away the camera happens to be. */
      if(raw[i].px<A3D_GIZ.edgeOn*maxPx)continue;
      var a2=raw[i].ax,dd=raw[i].d;
      var world=A3D_GIZ.arm/raw[i].px;
      var tip=toScreen([o[0]+dd[0]*world,o[1]+dd[1]*world,o[2]+dd[2]*world],V,W,H);
      var tx=tip[0]-so[0],ty=tip[1]-so[1];
      if(Math.sqrt(tx*tx+ty*ty)<A3D_GIZ.minArm)continue;
      arms.push({axis:a2.k,col:a2.col,lab:a2.lab,dir:dd.slice(),world:world,px:raw[i].px,
                 x0:so[0],y0:so[1],x1:tip[0],y1:tip[1],
                 sx:tx/world,sy:ty/world});             // screen px per 1 world unit along the axis
    }
    if(!arms.length)return null;
    var geom={ids:ids,origin:o,ox:so[0],oy:so[1],arms:arms,frame:fr};
    geom.caps=bimGizmoCaps(ids,fr);
    geom.ring=bimGizmoRingGeom(geom,V,W,H);   // __acad3dV78: null when the plan plane is edge-on
    geom.centre={x:so[0],y:so[1],h:A3D_GIZ.centre};
    geom.planes=bimGizmoPlaneGeom(geom,V,W,H);
    /* The scale boxes and the tilt arcs sit at the ring's radius, so the far side of the gizmo
       reads as one cage; with no ring (an elevation) the radius comes from the arms instead. */
    var pxSum=0;
    for(i=0;i<arms.length;i++)pxSum+=arms[i].px;
    geom.cageR=geom.ring?geom.ring.R:A3D_GIZ.ring/(pxSum/arms.length);
    geom.scales=bimGizmoScaleGeom(geom,V,W,H);
    geom.uniform=bimGizmoUniformGeom(geom,V,W,H);   /* __acad3dV111 */
    geom.rings=bimGizmoRingsGeom(geom,V,W,H);       /* __acad3dV111: every axis, full circles */
    /* kept under its V110 name: the rings that TILT, which is what the caps rule and the suites
       that drive a tilt ask for. Derived from the ring list rather than built again, so the two
       cannot disagree about which tilts exist. */
    geom.tilts=geom.rings.filter(function(r){return r.kind==='tilt';});
    return geom;
  }
  /* The rotate ring, as projected screen geometry, about the WORLD vertical whatever the frame
     (__acad3dV110): building elements turn about the vertical and nothing else, so the ring means
     the same thing in World, Local and View. The world radius is derived from the two HORIZONTAL
     directions' measured pixels-per-world-unit -- the ring lies in the plan plane, so the vertical
     says nothing about how big it should be drawn. When the plan plane is close to edge-on the
     ring collapses to a line; it is dropped in that case for the same reason an edge-on arm is,
     and for the extra reason that a rotation drag there would have no stable angle to read. */
  function bimGizmoRingGeom(g,V,W,H){
    var o=g.origin,probes=[[1,0,0],[0,0,-1],[0,1,0]],px=[],i,maxPx=0;
    for(i=0;i<3;i++){
      var pp=toScreen([o[0]+probes[i][0],o[1]+probes[i][1],o[2]+probes[i][2]],V,W,H);
      var vx=pp[0]-g.ox,vy=pp[1]-g.oy,l=Math.sqrt(vx*vx+vy*vy);
      if(!isFinite(l))l=0;
      px.push(l);
      if(l>maxPx)maxPx=l;
    }
    if(maxPx<=1e-9||px[0]<A3D_GIZ.edgeOn*maxPx||px[1]<A3D_GIZ.edgeOn*maxPx)return null;
    var pxPerUnit=(px[0]+px[1])/2;
    if(!isFinite(pxPerUnit)||pxPerUnit<1e-6)return null;
    var R=A3D_GIZ.ring/pxPerUnit;
    var pts=[],n=A3D_GIZ.ringSeg,t;
    for(i=0;i<=n;i++){
      t=i/n*Math.PI*2;
      var s=toScreen([o[0]+Math.cos(t)*R,o[1],o[2]+Math.sin(t)*R],V,W,H);
      if(!isFinite(s[0])||!isFinite(s[1]))return null;
      pts.push([s[0],s[1]]);
    }
    /* A ring whose minor screen extent has collapsed is a line the user cannot aim at, and the
       angle read off it would be unstable. Measured rather than inferred from the camera. */
    var minX=Infinity,maxX=-Infinity,minY=Infinity,maxY=-Infinity;
    for(i=0;i<pts.length;i++){
      if(pts[i][0]<minX)minX=pts[i][0];
      if(pts[i][0]>maxX)maxX=pts[i][0];
      if(pts[i][1]<minY)minY=pts[i][1];
      if(pts[i][1]>maxY)maxY=pts[i][1];
    }
    var minor=Math.min(maxX-minX,maxY-minY);
    if(minor<A3D_GIZ.minArm)return null;
    return {pts:pts,R:R,minor:minor};
  }
  /* The cursor's angle about the gizmo origin, measured in the MODEL. groundPoint un-projects the
     cursor onto the plan plane at the origin's elevation -- the same function the sketch tools and
     the grip drag already use -- so the angle is a world angle, not a screen angle. A screen angle
     would drift: the ring projects to an ellipse, and equal screen angles around an ellipse are
     not equal world angles, so the object would lag the cursor near the ends of the minor axis.
     bimRotatePoint's positive direction is atan2(z, x) increasing, so this matches it exactly. */
  function bimGizmoAngleAt(xy,origin){
    var p=groundPoint(xy[0],xy[1],origin[1]);
    if(!p)return null;
    var dx=p[0]-origin[0],dz=p[2]-origin[2];
    if(Math.sqrt(dx*dx+dz*dz)<1e-6)return null;     // exactly on the centre: no direction to read
    return Math.atan2(dz,dx);
  }
  /* __acad3dV110: the frame the gizmo is drawn in -- three world unit vectors under the model's
     keys. World is fixed. View is the camera's own right, up and toward-the-viewer, so an arrow
     drags along the screen. Local is the one orientation an object actually stores: a column's
     rotation, or the direction of a wall's first segment. Anything else has no stored
     orientation, and the frame says so (fallback) rather than pretending to align to one. All
     three are right-handed in Revit's order: X cross Y is Z. */
  function bimGizmoFrame(ids){
    var asked=A3D.gizAlign||'world';
    if(asked==='view'){
      var V=camVecs(A3D.cam);
      return {x:V.r.slice(),z:V.u.slice(),y:V.d.slice(),mode:'view',asked:asked,fallback:false};
    }
    if(asked==='local'){
      var dir=(ids&&ids.length===1)?bimGizmoLocalDir(objById(ids[0])):null;
      if(dir)return {x:[dir[0],0,dir[1]],z:[dir[1],0,-dir[0]],y:[0,1,0],mode:'local',asked:asked,fallback:false};
      return {x:[1,0,0],z:[0,0,-1],y:[0,1,0],mode:'world',asked:asked,fallback:true};
    }
    return {x:[1,0,0],z:[0,0,-1],y:[0,1,0],mode:'world',asked:asked,fallback:false};
  }
  function bimGizmoLocalDir(o){
    if(!o||!o.bim)return null;
    if(o.bim.type==='column'){
      var r=o.bim.rotation||0;
      return [Math.cos(r),Math.sin(r)];
    }
    if(o.bim.type==='wall'&&o.bim.centerline&&o.bim.centerline.length>=2){
      var a=o.bim.centerline[0],b=o.bim.centerline[1];
      var dx=b[0]-a[0],dz=b[1]-a[1],L=Math.sqrt(dx*dx+dz*dz);
      return L>1e-9?[dx/L,dz/L]:null;
    }
    return null;
  }
  /* __acad3dV110: what the WHOLE selection can do beyond moving. A tilt or scale handle is drawn
     only when every selected object would follow it -- a wall left standing while the box beside
     it tilted is a broken arrangement, not a partial success. Generic solids (primitives, pads,
     meshes) tilt and scale in 3D. A sketch is plan geometry at one elevation, so it scales along
     horizontal directions only and never tilts. Building elements neither tilt nor scale. */
  function bimGizmoKind(o){
    if(!o)return 'none';
    if(o.t==='sketch')return (o.pts&&o.pts.length)?'sketch':'other';
    if(o.bim||o.t==='opening')return 'bim';
    if(o.t==='solid'&&o.mesh&&o.mesh.v&&o.mesh.v.length)return 'solid';
    if(TYPES[o.t]&&(o.mesh||o.prm))return 'solid';
    return 'other';
  }
  function bimGizmoCaps(ids,fr){
    var i,solids=0,sketches=0,arcs=0,n=ids.length;
    for(i=0;i<n;i++){
      var o=objById(ids[i]),k=bimGizmoKind(o);
      if(k==='solid')solids++;
      else if(k==='sketch'){sketches++;if(o.bulges&&bimHasBulge(o.bulges))arcs++;}
    }
    var allScal=n>0&&solids+sketches===n,keys=['x','y','z'],sc={x:false,y:false,z:false};
    for(i=0;i<3;i++)
      sc[keys[i]]=allScal&&(sketches===0||Math.abs(fr[keys[i]][1])<1e-6);
    return {tilt:n>0&&solids===n,scale:sc,arcs:arcs,sketches:sketches,solids:solids};
  }
  /* __acad3dV110: the cursor as a world ray, in the same two projections groundPoint() inverts --
     generalised because the new handles need planes that are not horizontal. */
  function bimScreenRay(sx,sy){
    var V=camVecs(A3D.cam),W=cvW(),H=cvH(),f=H*1.2;
    if(A3D.flat){
      var k=f/Math.max(A3D.cam.dist,0.5);
      var xc=(sx-W/2)/k,yc=(H/2-sy)/k;
      return {o:[V.eye[0]+V.r[0]*xc+V.u[0]*yc,V.eye[1]+V.r[1]*xc+V.u[1]*yc,V.eye[2]+V.r[2]*xc+V.u[2]*yc],
              d:[-V.d[0],-V.d[1],-V.d[2]]};
    }
    var a=(sx-W/2)/f,b=(H/2-sy)/f;
    var d=[V.r[0]*a+V.u[0]*b-V.d[0],V.r[1]*a+V.u[1]*b-V.d[1],V.r[2]*a+V.u[2]*b-V.d[2]];
    var L=Math.sqrt(d[0]*d[0]+d[1]*d[1]+d[2]*d[2])||1;
    return {o:V.eye.slice(),d:[d[0]/L,d[1]/L,d[2]/L]};
  }
  /* Where the cursor ray meets the plane through P0 with unit normal N -- or null when the ray
     runs within minCos of parallel to it, because a grazing plane turns a pixel of cursor into
     metres, or when the plane is behind the camera. */
  function bimRayPlane(sx,sy,P0,N,minCos){
    var r=bimScreenRay(sx,sy);
    var dn=r.d[0]*N[0]+r.d[1]*N[1]+r.d[2]*N[2];
    if(!isFinite(dn)||Math.abs(dn)<minCos)return null;
    var t=((P0[0]-r.o[0])*N[0]+(P0[1]-r.o[1])*N[1]+(P0[2]-r.o[2])*N[2])/dn;
    if(!isFinite(t)||(!A3D.flat&&t<=0))return null;
    return [r.o[0]+r.d[0]*t,r.o[1]+r.d[1]*t,r.o[2]+r.d[2]*t];
  }
  /* __acad3dV123: WHERE THE CURSOR MEETS AN OBJECT -- the point, the face (its index in the object's
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
  /* A plane square: a parallelogram part-way along two axes. Dropped when either arrow is missing
     (its axis is edge-on) or the two arrows project close to parallel -- measured on screen, so
     the rule is the same for every frame and camera.
     Which QUADRANT of its plane a square sits in is measured too. The first choice is the one
     facing the camera, as the reference tools place it. But an arrow that points away from the
     viewer still projects across the near side at some angles -- in the default view the Y arrow
     ran straight through the XZ square, and the arrow won every click there -- so a square that
     does not clear every arrow and every square already placed by A3D_GIZ.planeClear pixels moves
     to whichever quadrant clears them most. */
  function bimGizPlaneQuad(o,A,B,sa,sb,V,W,H){
    var f0=A3D_GIZ.plane0,f1=A3D_GIZ.plane1,cs=[[f0,f0],[f1,f0],[f1,f1],[f0,f1]],q=[],c;
    for(c=0;c<4;c++){
      var ua=sa*A.world*cs[c][0],ub=sb*B.world*cs[c][1];
      var s=toScreen([o[0]+A.dir[0]*ua+B.dir[0]*ub,o[1]+A.dir[1]*ua+B.dir[1]*ub,o[2]+A.dir[2]*ua+B.dir[2]*ub],V,W,H);
      if(!isFinite(s[0])||!isFinite(s[1]))return null;
      q.push([s[0],s[1]]);
    }
    return q;
  }
  function bimGizQuadCentre(q){
    var x=0,y=0,i;
    for(i=0;i<q.length;i++){x+=q[i][0];y+=q[i][1];}
    return [x/q.length,y/q.length];
  }
  function bimGizQuadClearance(q,arms,placed){
    var pts=q.concat([bimGizQuadCentre(q)]),best=1e9,i,j;
    for(i=0;i<pts.length;i++)for(j=0;j<arms.length;j++){
      var a=arms[j],d=bimPointSegDist(pts[i][0],pts[i][1],a.x0,a.y0,a.x1,a.y1);
      if(d<best)best=d;
    }
    var c=bimGizQuadCentre(q);
    for(j=0;j<placed.length;j++){
      var pc=bimGizQuadCentre(placed[j].quad);
      var dd=Math.sqrt((c[0]-pc[0])*(c[0]-pc[0])+(c[1]-pc[1])*(c[1]-pc[1]))-2*A3D_GIZ.planeClear;
      if(dd<best)best=dd;
    }
    return best;
  }
  function bimGizmoPlaneGeom(g,V,W,H){
    var out=[],i,j,k,by={},o=g.origin;
    var tc=[V.eye[0]-o[0],V.eye[1]-o[1],V.eye[2]-o[2]];
    for(j=0;j<g.arms.length;j++)by[g.arms[j].axis]=g.arms[j];
    for(i=0;i<A3D_GIZ_PLANES.length;i++){
      var P=A3D_GIZ_PLANES[i],A=by[P.a],B=by[P.b];
      if(!A||!B)continue;
      var ax=A.x1-A.x0,ay=A.y1-A.y0,bx=B.x1-B.x0,bY=B.y1-B.y0;
      var la=Math.sqrt(ax*ax+ay*ay),lb=Math.sqrt(bx*bx+bY*bY);
      if(Math.abs(ax*bY-ay*bx)/Math.max(la*lb,1e-9)<A3D_GIZ.planeFlat)continue;
      var fa=(!A3D.flat&&vdot(A.dir,tc)<0)?-1:1,fb=(!A3D.flat&&vdot(B.dir,tc)<0)?-1:1;
      var cands=[[fa,fb],[fa,-fb],[-fa,fb],[-fa,-fb]],best=null;
      for(k=0;k<cands.length;k++){
        var q=bimGizPlaneQuad(o,A,B,cands[k][0],cands[k][1],V,W,H);
        if(!q)continue;
        var cl=bimGizQuadClearance(q,g.arms,out);
        if(k===0&&cl>=A3D_GIZ.planeClear){best={q:q,cl:cl};break;}
        if(!best||cl>best.cl)best={q:q,cl:cl};
      }
      if(!best)continue;
      out.push({k:P.k,a:P.a,b:P.b,col:bimGizAxis(P.n).col,lab:A.lab+B.lab,quad:best.q,
                da:A.dir.slice(),db:B.dir.slice()});
    }
    return out;
  }
  /* The scale boxes, on the far side of the origin at the cage radius, one per axis the whole
     selection can scale along and that is not edge-on. */
  function bimGizmoScaleGeom(g,V,W,H){
    var out=[],i,o=g.origin,R=g.cageR;
    if(!isFinite(R)||R<=0)return out;
    for(i=0;i<g.arms.length;i++){
      var a=g.arms[i];
      if(!g.caps.scale[a.axis])continue;
      var s=toScreen([o[0]-a.dir[0]*R,o[1]-a.dir[1]*R,o[2]-a.dir[2]*R],V,W,H);
      var dx=s[0]-g.ox,dy=s[1]-g.oy,L=Math.sqrt(dx*dx+dy*dy);
      if(!isFinite(L)||L<A3D_GIZ.minArm)continue;
      out.push({axis:a.axis,col:a.col,lab:a.lab,dir:a.dir.slice(),x:s[0],y:s[1],L:L,ux:dx/L,uy:dy/L});
    }
    return out;
  }
  /* __acad3dV111: every rotation the gizmo offers, as a FULL ring -- the way the reference tools
     draw them (3ds Max's trackball rings, Unity's rotate gizmo, Blender's dials) rather than V110's
     quarter arcs. One ring about each frame axis, plus the screen ring about the camera's own
     direction, at a slightly larger radius so it reads as the outermost circle.

     Each sample carries whether it is on the near side of the sphere, measured against the
     direction to the camera. The near half is drawn solid and picked first; the far half is drawn
     faded and picked only when the near half misses. Without that a ring is a flat ellipse, and a
     click on the part of it that is behind the object grabs the same handle as the part in front.

     The VERTICAL ring is the one every selection has (V78): a building element turns about the
     vertical and nothing else. It keeps the model's own parameterisation -- angle measured as
     atan2(z, x), the same as bimGizmoAngleAt and bimRotatePoint -- so the drawn sweep and the
     rotation it performs cannot disagree. The rest are drawn only for a selection that can tilt. */
  function bimGizmoRingsGeom(g,V,W,H){
    var out=[],fr=g.frame,o=g.origin,R=g.cageR,defs=[],i,j;
    if(!isFinite(R)||R<=0)return out;
    var toCam=A3D.flat?V.d.slice():[V.eye[0]-o[0],V.eye[1]-o[1],V.eye[2]-o[2]];
    var tcL=Math.sqrt(toCam[0]*toCam[0]+toCam[1]*toCam[1]+toCam[2]*toCam[2])||1;
    var vd=[toCam[0]/tcL,toCam[1]/tcL,toCam[2]/tcL];
    var upright=Math.abs(fr.y[1])>0.999;
    if(g.caps.tilt){
      defs.push({axis:'x',kind:'tilt',A:fr.x,B:fr.z,C:fr.y});
      defs.push({axis:'z',kind:'tilt',A:fr.z,B:fr.y,C:fr.x});
      if(upright)defs.push({axis:'y',kind:'vertical',A:[0,1,0],B:[1,0,0],C:[0,0,1]});
      else{
        defs.push({axis:'y',kind:'tilt',A:fr.y,B:fr.x,C:fr.z});
        defs.push({axis:'vert',kind:'vertical',A:[0,1,0],B:[1,0,0],C:[0,0,1]});
      }
      /* the screen ring, unless the frame's own third axis already points at the camera */
      if(1-Math.abs(vdot(fr.y,vd))>0.03)
        defs.push({axis:'view',kind:'view',A:vd.slice(),B:V.r.slice(),C:V.u.slice()});
    }else{
      defs.push({axis:'y',kind:'vertical',A:[0,1,0],B:[1,0,0],C:[0,0,1]});
    }
    for(i=0;i<defs.length;i++){
      var D=defs[i];
      /* a vertical ring exists exactly when V78's own ring does -- same rule, same radius, so the
         ring a suite reads through __a3dGizmoRing is the ring that is drawn */
      if(D.kind==='vertical'&&!g.ring)continue;
      var RR=(D.kind==='view')?R*A3D_GIZ.viewRing:(D.kind==='vertical'?g.ring.R:R);
      var pts=[],n=A3D_GIZ.ringSeg,ok=true,rmax=0,area=0,t,s,wp,near;
      var so=toScreen(o,V,W,H);
      for(j=0;j<=n;j++){
        t=j/n*Math.PI*2;
        wp=bimGizArcPt(o,D.B,D.C,RR,t);
        s=toScreen(wp,V,W,H);
        if(!isFinite(s[0])||!isFinite(s[1])){ok=false;break;}
        /* near is measured as DEPTH against the gizmo's own centre -- the same number the
           projection reports and the renderer sorts by. Measuring it as a hemisphere about the
           direction to the eye instead put a handful of samples either side of the boundary in
           the wrong half, because that direction is not the view axis unless the gizmo happens to
           sit at the middle of the screen. */
        near=(D.kind==='view')||(s[2]<=so[2]);
        pts.push([s[0],s[1],near?1:0]);
        var rr=Math.sqrt((s[0]-g.ox)*(s[0]-g.ox)+(s[1]-g.oy)*(s[1]-g.oy));
        if(rr>rmax)rmax=rr;
      }
      if(!ok||rmax<A3D_GIZ.minArm)continue;
      for(j=0;j<pts.length-1;j++)area+=pts[j][0]*pts[j+1][1]-pts[j+1][0]*pts[j][1];
      area=Math.abs(area)/2;
      /* measured flatness: the projected circle's area against the circle it would be face-on.
         A ring seen edge-on is a line, which cannot be aimed at and has no stable angle to read.
         The vertical ring has already passed V78's own edge-on rule, so it is kept. */
      if(D.kind!=='vertical'&&area/(Math.PI*rmax*rmax)<A3D_GIZ.arcFlat)continue;
      var inf=(D.axis==='view')?{col:'#c8d2dd',lab:'VIEW'}:(D.axis==='vert'?bimGizAxis('y'):bimGizAxis(D.axis));
      out.push({axis:D.axis,kind:D.kind,col:inf.col,lab:inf.lab,
                A:D.A.slice(),B:D.B.slice(),C:D.C.slice(),R:RR,pts:pts,rmax:rmax});
    }
    return out;
  }
  /* __acad3dV111: 3ds Max's uniform-scale region, as a triangle between the three scale boxes but
     drawn inside them, where nothing else can be aimed at. Only offered when all three axes can
     scale -- a two-axis triangle would be a line. Shift on any single box does the same thing, and
     both go through one drag. */
  function bimGizmoUniformGeom(g,V,W,H){
    var o=g.origin,R=g.cageR*A3D_GIZ.uniform,tri=[],i;
    if(!g.scales||g.scales.length<3||!isFinite(R)||R<=0)return null;
    for(i=0;i<3;i++){
      var d=g.scales[i].dir;
      var s=toScreen([o[0]-d[0]*R,o[1]-d[1]*R,o[2]-d[2]*R],V,W,H);
      if(!isFinite(s[0])||!isFinite(s[1]))return null;
      tri.push([s[0],s[1]]);
    }
    var a2=Math.abs((tri[1][0]-tri[0][0])*(tri[2][1]-tri[0][1])-(tri[2][0]-tri[0][0])*(tri[1][1]-tri[0][1]))/2;
    if(a2<200)return null;              // collapsed to a sliver in this view: nothing to aim at
    return {tri:tri,c:[(tri[0][0]+tri[1][0]+tri[2][0])/3,(tri[0][1]+tri[1][1]+tri[2][1])/3]};
  }
  function bimGizArcPt(o,B,C,R,t){
    var c=Math.cos(t)*R,s=Math.sin(t)*R;
    return [o[0]+B[0]*c+C[0]*s,o[1]+B[1]*c+C[1]*s,o[2]+B[2]*c+C[2]*s];
  }
  function bimGizInQuad(q,x,y){
    var i,sg=0;
    for(i=0;i<q.length;i++){
      var a=q[i],b=q[(i+1)%q.length];
      var c=(b[0]-a[0])*(y-a[1])-(b[1]-a[1])*(x-a[0]);
      if(Math.abs(c)<1e-12)continue;
      if(!sg)sg=c>0?1:-1;
      else if((c>0?1:-1)!==sg)return false;
    }
    return true;
  }
