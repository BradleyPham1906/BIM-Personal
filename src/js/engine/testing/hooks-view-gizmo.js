  /* __acad3dV75: the world-offset invariant, exposed so a suite can assert it directly rather
     than inferring it from pixels. bimObjWorldPoints returns the SCREEN points an object's plan
     geometry actually occupies, which is the one thing every consumer in this phase had to
     agree on. */
  window.__a3dObjOffset=function(id){var o=objById(id);return o?bimObjOffset(o):null;};
  window.__a3dObjScreenPoints=function(id){
    var o=objById(id);if(!o)return null;
    var V=camVecs(A3D.cam);
    return bimObjScreenPoints(o,V,cvW(),cvH()).map(function(p){return [p[0],p[1]];});
  };
  window.__a3dSnapCandidates=function(y0){return bimSnapCandidates(y0||0);};
  /* __acad3dV76: test surface. The geometry is reported exactly as drawn and picked, so a suite
     asserts the handle the user sees rather than a parallel recomputation of it. */
  window.__a3dGizmo=function(){
    paint();
    if(!A3D.gizmo)return null;
    var g=A3D.gizmo;
    function cen(q){var x=0,y=0,i;for(i=0;i<q.length;i++){x+=q[i][0];y+=q[i][1];}return [x/q.length,y/q.length];}
    return {ox:g.ox,oy:g.oy,origin:g.origin.slice(),ids:g.ids.slice(),
      arms:g.arms.map(function(a){
        /* __acad3dV79: sx/sy -- screen pixels per ONE world unit along this axis, at the
           gizmo's own depth -- are published because they ARE the drag's contract: every
           axis move is the cursor delta projected onto them. Without them a suite can only
           check that a drag moved something, never that it moved the right amount, and
           cannot position anything deliberately on screen. */
        return {axis:a.axis,lab:a.lab,col:a.col,dir:a.dir.slice(),x0:a.x0,y0:a.y0,x1:a.x1,y1:a.y1,
                sx:a.sx,sy:a.sy,world:a.world,
                len:Math.sqrt((a.x1-a.x0)*(a.x1-a.x0)+(a.y1-a.y0)*(a.y1-a.y0))};
      }),
      /* __acad3dV110: the rest of the handle set, reported exactly as drawn and picked */
      frame:{mode:g.frame.mode,asked:g.frame.asked,fallback:g.frame.fallback,
             x:g.frame.x.slice(),y:g.frame.y.slice(),z:g.frame.z.slice()},
      caps:{tilt:g.caps.tilt,scale:{x:g.caps.scale.x,y:g.caps.scale.y,z:g.caps.scale.z},arcs:g.caps.arcs},
      centre:{x:g.centre.x,y:g.centre.y,h:g.centre.h},
      planes:g.planes.map(function(p){return {k:p.k,lab:p.lab,col:p.col,c:cen(p.quad),
                                             quad:p.quad.map(function(q){return q.slice();})};}),
      scales:g.scales.map(function(s){return {axis:s.axis,lab:s.lab,col:s.col,x:s.x,y:s.y,L:s.L};}),
      tilts:g.tilts.map(function(t){return {axis:t.axis,lab:t.lab,col:t.col,R:t.R,A:t.A.slice(),
                                           mid:t.pts[Math.floor(t.pts.length/2)].slice()};}),
      /* __acad3dV111: every rotation ring as drawn -- its axis, its kind, and how much of it is
         on the near side of the sphere, which is what the drawing and the picking both use. */
      rings:g.rings.map(function(r){
        var near=0,i;
        for(i=0;i<r.pts.length;i++)if(r.pts[i][2])near++;
        /* every third sample, with its near flag: the same points the ring is drawn from and
           picked against, so a suite aims at the half it means rather than at a guess */
        var pts=[];
        for(i=0;i<r.pts.length;i+=3)pts.push([r.pts[i][0],r.pts[i][1],r.pts[i][2]]);
        return {axis:r.axis,kind:r.kind,lab:r.lab,col:r.col,R:r.R,A:r.A.slice(),
                B:r.B.slice(),C:r.C.slice(),   /* the basis it is drawn from (__acad3dV111) */
                n:r.pts.length,near:near,rmax:r.rmax,pts:pts};
      }),
      uniform:g.uniform?{tri:g.uniform.tri.map(function(p){return p.slice();}),c:g.uniform.c.slice()}:null,
      ring:!!g.ring,cageR:g.cageR};
  };
  window.__a3dGizmoAt=function(x,y){
    var h=bimPickGizmo(x,y);
    if(!h)return null;
    /* __acad3dV111: derived from the one function that names a handle, rather than a second list
       of kinds beside it. The second list is exactly what went wrong: it had no case for the
       even-scale triangle, so a point squarely inside it answered 'nothing here' -- the handle
       worked and the surface that reports it did not. An arrow still answers by its bare axis,
       which is V76's contract. */
    var k=bimGizmoHoverKey(h);
    return (k&&k.indexOf('axis:')===0)?k.slice(5):k;
  };
  /* __acad3dV110: the screen point on a tilt arc's circle at an angle in its own (B, C)
     parameter -- 180 to 270 is the drawn quarter -- which is what a suite aims at to drive a tilt
     with real pointer events. */
  window.__a3dGizmoArcPoint=function(axis,deg){
    paint();
    var g=A3D.gizmo,i;
    if(!g)return null;
    /* __acad3dV111: over every ring, not only the tilts, so a suite can aim at the vertical ring
       and at the screen ring through the same call it uses for the others. */
    for(i=0;i<g.rings.length;i++)if(g.rings[i].axis===axis){
      var t=g.rings[i],p=window.__a3dProject(bimGizArcPt(g.origin,t.B,t.C,t.R,deg*Math.PI/180));
      return [p.x,p.y];
    }
    return null;
  };
  /* __acad3dV111: what the cursor is over, as the highlight sees it */
  window.__a3dGizmoHover=function(){
    return {key:A3D.gizHover||null,name:A3D.gizHoverName||null};
  };
  /* __acad3dV112: the live drag, as the read-out and the snap marker see it */
  window.__a3dGizmoDrag=function(){
    if(!drag||!(drag.giz||drag.rot))return null;
    return {kind:drag.rot?'rotate':drag.gk,axis:drag.axis||null,fine:!!drag.fine,
            typing:bimGizmoTyping(),snapAt:drag.snapAt?drag.snapAt.slice():null,
            dist:drag.gizDist,angle:drag.rot?drag.rotAngle:(drag.tiltAngle||0),
            factor:drag.factor||null,copies:drag.copies?drag.copies.ids.slice():null,
            readout:bimGizmoReadout(drag)};   /* __acad3dV123: what the read-out says, unit and all */
  };
  window.__a3dGizmoState=function(){
    var m=document.getElementById('a3d-gizmenu');
    return {align:A3D.gizAlign||'world',hidden:!!A3D.gizHidden,
            pivot:A3D.gizPivot?A3D.gizPivot.slice():null,   /* __acad3dV112 */
            menu:m?Array.prototype.map.call(m.querySelectorAll('[data-a3dgiz]'),function(b){
              return {act:b.getAttribute('data-a3dgiz'),label:b.textContent,on:b.classList.contains('on')};}):null};
  };
  window.__a3dOriginAxes=function(){
    return A3D_ORIGIN_AXES.map(function(a){return {k:a.k,to:a.to.slice(),col:a.col};});
  };
  /* where the cursor's ray meets a plane -- checked by a suite against __a3dProject, which is
     the independent direction, so an un-projection that disagreed with the drawing would show */
  window.__a3dRayPlane=function(sx,sy,P0,N){return bimRayPlane(sx,sy,P0,N,0.01);};
  /* __acad3dV79: the one occasion a handle is still unreachable -- the user aimed at a grip or a
     gizmo arm that lies under the dock's own solid panel. A click on a toolbar is a click on a
     toolbar, so this does not pass the event through; it explains, once per press, and names the
     way out. It hit-tests the REAL pickers at the REAL canvas coordinates, so it only ever fires
     when a handle is genuinely there -- a generic "something might be hidden" warning would be
     noise on every dock click. */
  function bimHandleUnderPoint(clientX,clientY){
    if(!el.cv||!A3D.on)return null;
    var r=el.cv.getBoundingClientRect();
    var x=clientX-r.left,y=clientY-r.top;
    if(x<0||y<0||x>r.width||y>r.height)return null;
    var gz=bimPickGizmo(x,y);
    if(gz)return bimGizmoHandleName(gz);   /* __acad3dV110: Revit's letters, every handle */
    var gp=bimPickGrip(x,y);
    if(gp)return 'a shape handle';
    return null;
  }
  function bimWireOcclusionNotice(){
    var body=document.querySelector('#a3d-dock .a3d-dockbody');
    if(!body||body.__a3dOccWired)return false;
    body.__a3dOccWired=true;
    body.addEventListener('pointerdown',function(ev){
      // A press on an actual control is the user using the dock; only an aim at its background
      // could have been meant for the drawing underneath.
      if(ev.target&&ev.target.closest&&ev.target.closest('button,input,select'))return;
      var what=bimHandleUnderPoint(ev.clientX,ev.clientY);
      if(!what)return;
      a3dToast(what+' is behind the tool dock — press Zoom to Selection to bring it clear');
    },true);
    return true;
  }
  /* __acad3dV80: the type the NEXT wall will be drawn with. Real state (it is in
     bimSnapshotState and persists), but nothing published it, so neither a user-facing
     read-out nor a suite could tell which type was active. */
  window.__a3dActiveWallType=function(){return A3D.activeWallType||null;};
  /* A colour input only accepts #rrggbb, and an overlay fill may be an rgba() string. Falling
     back to a neutral rather than emitting an invalid value keeps the swatch usable. */
  function bimNoteHex(c){
    return (typeof c==='string'&&/^#[0-9a-fA-F]{6}$/.test(c))?c:'#f6e7a8';
  }
  window.__a3dRailUtils=function(){
    var box=document.getElementById('a3d-railutil');
    if(!box)return null;
    var bs=box.querySelectorAll('button'),out=[],i;
    for(i=0;i<bs.length;i++){
      var r=bs[i].getBoundingClientRect();
      out.push({id:bs[i].getAttribute('data-a3drumenu')||bs[i].getAttribute('data-a3druact'),
        menu:!!bs[i].getAttribute('data-a3drumenu'),
        title:bs[i].getAttribute('title'),
        x:Math.round(r.left),y:Math.round(r.top),w:Math.round(r.width),h:Math.round(r.height)});
    }
    return out;
  };
  window.__a3dRailOpen=function(id){
    var b=document.querySelector('[data-a3drumenu="'+id+'"]');
    if(!b)return null;
    b.click();
    var p=document.getElementById('a3d-rupop');
    if(!p||!p.classList.contains('open'))return null;
    var r=p.getBoundingClientRect();
    var items=[],ns=p.querySelectorAll('[data-a3druitem]'),i;
    for(i=0;i<ns.length;i++)items.push({spec:ns[i].getAttribute('data-a3druitem'),
      label:ns[i].textContent.trim(),on:ns[i].classList.contains('on')});
    var fs=[],gs=p.querySelectorAll('[data-a3druset]');
    for(i=0;i<gs.length;i++)fs.push({spec:gs[i].getAttribute('data-a3druset'),
      type:gs[i].type,value:gs[i].value,checked:gs[i].checked});
    return {for:p.getAttribute('data-for'),items:items,fields:fs,
      left:Math.round(r.left),top:Math.round(r.top),
      right:Math.round(r.right),bottom:Math.round(r.bottom),
      onScreen:r.left>=0&&r.top>=0&&r.right<=window.innerWidth&&r.bottom<=window.innerHeight};
  };
  window.__a3dRailClick=function(spec){
    var p=document.getElementById('a3d-rupop');
    if(!p)return false;
    var b=p.querySelector('[data-a3druitem="'+spec+'"]');
    if(!b)return false;
    b.click();
    return true;
  };
  window.__a3dRailSet=function(spec,value){
    var p=document.getElementById('a3d-rupop');
    if(!p)return false;
    var f=p.querySelector('[data-a3druset="'+spec+'"]');
    if(!f)return false;
    if(f.type==='checkbox')f.checked=!!value;else f.value=String(value);
    f.dispatchEvent(new Event('change',{bubbles:true}));
    return true;
  };
  window.__a3dZoomWindowArmed=function(){return !!A3D.zoomWindow;};
  window.__a3dSnapState=function(){
    return {point:A3D_SNAP.point,grid:A3D_SNAP.grid,ortho:A3D_SNAP.ortho,
            gridSize:A3D_SNAP.gridSize};
  };
  window.__acad3dV83='railutilitystack,zoommenu,zoomwindow,appearancemenu,snapsmenu,unitsmenu,saveviewportpng,clampedpopover';
  window.__a3dNoteKinds=function(){
    return BIM_NOTE_KINDS.map(function(k){return {kind:k.k,label:k.label};});
  };
  window.__a3dPlaceNote=function(kind,opts){
    var o=bimPlaceNoteAtViewCentre(kind,opts||null);
    return o?o.id:null;
  };
  window.__a3dNoteAt=function(x,y){var o=bimPickNote(x,y);return o?o.id:null;};
  window.__a3dNoteRect=function(id){
    var o=objById(id);
    if(!o||o.t!=='note')return null;
    var r=bimNoteRect(o,camVecs(A3D.cam),cvW(),cvH());
    return r?{x:r.x,y:r.y,w:r.w,h:r.h,ax:r.ax,ay:r.ay}:null;
  };
  window.__acad3dV82='annotationoverlay,worldanchoredscreendrawn,notekinds,overlaypickedfirst,assetsannotationgroup';
  window.__a3dColumnRotation=function(id){
    var o=objById(id);
    return (o&&o.bim&&o.bim.type==='column')?(o.bim.rotation||0):null;
  };
  window.__a3dRotatableSplit=function(ids){return bimRotatableSplit(ids||[]);};
  window.__acad3dV81='columnorientation,transformkind,mirrorreflectsorientation,rotationproperty,ringrefusalsupfront';
  window.__a3dShellAudit=bimShellAudit;
  window.__a3dCleanShell=bimCleanShell;
  window.__a3dAssetRows=function(){
    var p=document.getElementById('a3d-leftpanel');
    if(!p)return null;
    var rows=p.querySelectorAll('[data-a3dassets]'),out=[],i;
    for(i=0;i<rows.length;i++)out.push({
      spec:rows[i].getAttribute('data-a3dassets'),
      label:rows[i].querySelector('.a3d-asnm').textContent.trim(),
      meta:rows[i].querySelector('.a3d-asmeta').textContent.trim(),
      live:!rows[i].disabled});
    return out;
  };
  window.__a3dAssetClick=function(spec){
    var p=document.getElementById('a3d-leftpanel');
    if(!p)return false;
    var b=p.querySelector('[data-a3dassets="'+spec+'"]');
    if(!b||b.disabled)return false;
    b.click();
    return true;
  };
  window.__acad3dV80='shellaudit,canvasleftoverspurged,bimassetlibrary,projectfilecard,deadrailbuttonsremoved';
  window.__a3dSafeViewRect=function(){
    var s=bimSafeViewRect();
    return {x:s.x,y:s.y,w:s.w,h:s.h,insets:s.insets,
            chrome:bimChromeRects().map(function(r){return r.sel;})};
  };
  window.__a3dZoomToSelection=bimZoomToSelection;
  window.__a3dWorldBounds=function(ids){return bimWorldBounds(ids||null);};
  window.__a3dHandleUnderPoint=function(cx,cy){return bimHandleUnderPoint(cx,cy);};
  window.__acad3dV79='safeviewrect,chromeawarefit,zoomtoselection,sketchesinfit,occludedhandlenotice';
  window.__a3dGizmoRing=function(){
    paint();
    var g=A3D.gizmo;
    if(!g||!g.ring)return null;
    var p=g.ring.pts,i,minX=Infinity,maxX=-Infinity,minY=Infinity,maxY=-Infinity;
    for(i=0;i<p.length;i++){
      if(p[i][0]<minX)minX=p[i][0];
      if(p[i][0]>maxX)maxX=p[i][0];
      if(p[i][1]<minY)minY=p[i][1];
      if(p[i][1]>maxY)maxY=p[i][1];
    }
    return {R:g.ring.R,segs:p.length,pts:p,
            w:maxX-minX,h:maxY-minY,minor:Math.min(maxX-minX,maxY-minY),
            ox:g.ox,oy:g.oy};
  };
  /* The screen point on the ring at a given world angle -- what a suite has to aim at to drive
     a rotation through real pointer events. */
  window.__a3dGizmoRingPoint=function(deg){
    paint();
    var g=A3D.gizmo;
    if(!g||!g.ring)return null;
    var t=deg*Math.PI/180,R=g.ring.R;
    var p=window.__a3dProject([g.origin[0]+Math.cos(t)*R,g.origin[1],
                               g.origin[2]+Math.sin(t)*R]);
    return [p.x,p.y];
  };
  window.__a3dGizmoConfig=function(){
    return {arm:A3D_GIZ.arm,pick:A3D_GIZ.pick,minArm:A3D_GIZ.minArm,edgeOn:A3D_GIZ.edgeOn,
            ring:A3D_GIZ.ring,ringSeg:A3D_GIZ.ringSeg,ringPick:A3D_GIZ.ringPick,
            centre:A3D_GIZ.centre,box:A3D_GIZ.box,plane0:A3D_GIZ.plane0,plane1:A3D_GIZ.plane1};   // __acad3dV110
  };
  window.__acad3dV78='rotatering,worldangleviagroundpoint,snapshotpreview,orthofifteendegree,witnesslines,edgeonplanerefused,deferredrebuildpropagation';
  window.__acad3dV76='translategizmo,axisconstraineddrag,liveorigin,equalscreenarms,edgeonaxisrefused,griddeltasnap,livedistancereadout';
  window.__acad3dV110='transformdispatcherownframe,primitivesbecomeplainsolids,mirroredfacesrewound,revitaxiscolours,worldlocalviewframe,planesquares,centrefreemove,scaleboxes,tiltarcs,wholeselectioncaps,gizmomenu,gizmocommand';
  window.__acad3dV111='hoverhighlight,fullrotationrings,screenring,nearfarhalves,sweptanglesector,uniformscaletriangle,handlenameonhover';
  window.__acad3dV112='objectsnapondrags,typedexactvalue,escapecancels,ctrldragcopies,shiftfine,movablepivot,oneenddragpath';
  /* __acad3dV123: the held face, as drawn and as the model sees it -- a suite aims at the arrow the
     user sees and checks the size the object reports */
  window.__a3dFace=function(){
    paint();
    var cur=bimFaceCurrent();
    if(!cur)return null;
    var f=cur.f,fd=A3D.faceDraw;
    return {id:cur.o.id,key:f.key,kind:f.kind||null,ok:f.ok,why:f.why,name:f.name,dimName:f.dimName,dim:f.dim,
            N:f.N.slice(),C:cur.region.C.slice(),polys:cur.region.polys.length,edges:cur.region.edges.length,
            arrow:fd&&fd.arrow?{x0:fd.arrow.x0,y0:fd.arrow.y0,x1:fd.arrow.x1,y1:fd.arrow.y1,sx:fd.arrow.sx,sy:fd.arrow.sy}:null,
            dot:fd?fd.c.slice():null,text:fd?fd.text:null,
            screen:fd?fd.scr.map(function(p){return p.map(function(q){return [q[0],q[1]];});}):null};
  };
  window.__a3dFaceList=function(id){
    var o=objById(id||A3D.sel);
    return o?bimFaceList(o).map(function(p){return p.key;}):[];
  };
  window.__a3dFacePickAt=function(x,y){var p=bimFacePickAt(x,y);return p?{id:p.o.id,key:p.key}:null;};
  window.__a3dFaceHitAt=function(x,y){paint();return bimFaceHitAt(x,y);};
  window.__a3dFaceKeys=function(){
    return A3D_FACE_KEYS.map(function(k){return {act:k.act,keys:k.keys.slice(),shift:k.shift,say:k.say.slice(),label:k.label};});
  };
  window.__a3dValueBox=function(){
    if(!A3D_VALBOX)return null;
    return {label:A3D_VALBOX.label,value:A3D_VALBOX.input.value,error:A3D_VALBOX.err.textContent,
            focused:document.activeElement===A3D_VALBOX.input};
  };
  window.__a3dStatusHint=function(){return bimStatusHintText();};
  window.__a3dFacePending=function(){return {facePick:!!A3D.facePick,clickWaiting:!!A3D_CLICKBOX_T};};
  window.__a3dPushDrag=function(){
    if(!drag||!drag.pp)return null;
    return {moved:!!drag.moved,dist:drag.dist===undefined?null:drag.dist,limit:drag.limit||null,
            snapAt:drag.snapAt?drag.snapAt.slice():null,snapLevel:drag.snapLevel||null,typing:bimGizmoTyping(),
            kind:drag.f?drag.f.kind:null,fine:!!drag.fine,readout:drag.f?bimPushReadout(drag):null};
  };
  window.__a3dPushValue=function(dist){return bimPushValue(dist);};
  /* a suite that counts undo steps starts each scene from an empty history: past UNDO_MAX a step
     pushes the oldest out and the depth stops moving */
  window.__a3dTestClearUndo=function(){UNDO_STACK.length=0;REDO_STACK.length=0;return true;};
