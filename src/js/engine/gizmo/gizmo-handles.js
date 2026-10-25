  function bimGizmoVisible(){
    /* __acad3dV110: and not while the user has hidden it from the gizmo menu */
    return !!(A3D.on!==false)&&!A3D.sk&&!A3D.conPick&&!A3D.sheetCapture&&!A3D.gizHidden&&
      !A3D.face;   /* __acad3dV123: a held face has its own arrow */
  }
  function bimPickGizmo(x,y){
    if(!bimGizmoVisible())return null;
    var g=A3D.gizmo;
    if(!g)return null;
    /* __acad3dV97: A3D.gizmo is what the LAST paint drew, for the selection of that moment. If
       the selection has changed since with no repaint, this gizmo belongs to objects that are
       no longer selected, and a drag on it moved or rotated them. Compared through the same
       function that built it, so "the selection" means one thing in both places. */
    var now=bimGizmoIds(),was=g.ids||[];
    if(now.length!==was.length)return null;
    var gi;
    for(gi=0;gi<now.length;gi++)if(was.indexOf(now[gi])<0)return null;
    /* __acad3dV110/V111: the order of precedence where handles meet. The centre square sits on the
       origin every arrow starts from; the arrows are what the user reaches for most; the plane
       squares sit between them and the scale boxes sit on the rings. Then the NEAR half of every
       ring, then the uniform triangle those rings enclose, and only then the far halves: a click
       on the front of a ring must never be taken by the part of it that is behind the object. */
    var c=g.centre,i;
    if(c&&Math.abs(x-c.x)<=c.h+1&&Math.abs(y-c.y)<=c.h+1)return {kind:'centre',giz:g};
    var best=null,bestD=A3D_GIZ.pick;
    for(i=0;i<g.arms.length;i++){
      var a=g.arms[i];
      var d=bimPointSegDist(x,y,a.x0,a.y0,a.x1,a.y1);
      if(d<bestD){bestD=d;best=a;}
    }
    if(best)return {kind:'axis',axis:best.axis,arm:best,giz:g};
    for(i=0;i<g.planes.length;i++)
      if(bimGizInQuad(g.planes[i].quad,x,y))return {kind:'plane',plane:g.planes[i],giz:g};
    var bx=A3D_GIZ.box+3;
    for(i=0;i<g.scales.length;i++)
      if(Math.abs(x-g.scales[i].x)<=bx&&Math.abs(y-g.scales[i].y)<=bx)
        return {kind:'scale',axis:g.scales[i].axis,sq:g.scales[i],giz:g};
    var hr=bimPickGizmoRing(g,x,y,true);
    if(hr)return hr;
    if(g.uniform&&bimGizInTri(g.uniform.tri,x,y))return {kind:'uniform',giz:g};
    hr=bimPickGizmoRing(g,x,y,false);
    if(hr)return hr;
    return null;
  }
  /* A vertical ring answers as V78's rotate hit, so the path that turns a wall about the vertical
     is the one it always was; every other ring answers as a tilt about its own axis. */
  function bimPickGizmoRing(g,x,y,nearHalf){
    var i,best=null,bestD=A3D_GIZ.ringPick;
    for(i=0;i<(g.rings||[]).length;i++){
      var d=bimGizRingDist(g.rings[i],x,y,nearHalf);
      if(d<bestD){bestD=d;best=g.rings[i];}
    }
    if(!best)return null;
    if(best.kind==='vertical')return {kind:'ring',rot:true,ring:best,giz:g};
    return {kind:'tilt',axis:best.axis,arc:best,ring:best,giz:g};
  }
  function bimGizRingDist(r,x,y,nearHalf){
    var best=1e9,i;
    for(i=0;i<r.pts.length-1;i++){
      var isNear=!!(r.pts[i][2]&&r.pts[i+1][2]);
      if(isNear!==nearHalf)continue;
      var d=bimPointSegDist(x,y,r.pts[i][0],r.pts[i][1],r.pts[i+1][0],r.pts[i+1][1]);
      if(d<best)best=d;
    }
    return best;
  }
  function bimGizInTri(t,x,y){
    function sg(a,b){return (b[0]-a[0])*(y-a[1])-(b[1]-a[1])*(x-a[0]);}
    var s1=sg(t[0],t[1]),s2=sg(t[1],t[2]),s3=sg(t[2],t[0]);
    return !(((s1<0)||(s2<0)||(s3<0))&&((s1>0)||(s2>0)||(s3>0)));
  }
  /* __acad3dV111: the key of the handle under the cursor. The hover highlight compares keys rather
     than objects, because the geometry is rebuilt on every paint and no two objects survive it. */
  function bimGizmoHoverKey(h){
    if(!h)return null;
    if(h.rot)return 'rotate';
    if(h.kind==='axis'||h.kind==='scale'||h.kind==='tilt')return h.kind+':'+h.axis;
    if(h.kind==='plane')return 'plane:'+h.plane.k;
    return h.kind;
  }
  /* A handle's name as the user reads it -- Revit's axis letters, never the model's keys. */
  function bimGizmoHandleName(h){
    if(!h)return '';
    if(h.rot)return 'the rotate ring';
    if(h.kind==='centre')return 'the free-move square';
    if(h.kind==='plane')return 'the '+h.plane.lab+' move square';
    if(h.kind==='scale')return 'the '+bimGizAxis(h.axis).lab+' scale box';
    if(h.kind==='uniform')return 'the even scale triangle';          /* __acad3dV111 */
    if(h.kind==='tilt')return 'the '+bimGizRingLab(h.arc)+' rotate ring';
    return 'the '+bimGizAxis(h.axis).lab+' move handle';
  }
  function bimGizRingLab(r){
    return r?(r.axis==='view'?'screen':r.lab):'';
  }
  /* The live read-out. Angles are Revit's: positive is counter-clockwise looking down the axis
     from its positive end (right-handed), so a turn to the left in plan reads positive. The
     ring's own drag angle is kept in the model's sense (toward +z), hence the sign. */
  function bimGizmoReadout(dr){
    function deg(r){return (Math.round(r*180/Math.PI*10)/10)+'\u00b0';}
    if(dr.rot)return 'ROTATE Z  '+deg(-dr.rotAngle);
    var typed=bimGizmoTyping();                                  /* __acad3dV112 */
    if(typed!==null)return bimGizmoTypeLabel(dr)+'  '+typed+'_'+bimGizmoUnitSuffix(bimGizmoValueKind(dr));   /* __acad3dV123 */
    if(dr.snapAt)return bimGizmoPlainReadout(dr)+'   SNAP';      /* __acad3dV112 */
    return bimGizmoPlainReadout(dr);
  }
  /* __acad3dV123: the words of the value being typed, from the one function that names what a handle
     takes -- the value box a click opens says the same thing */
  function bimGizmoTypeLabel(dr){
    return bimGizmoValueLabel(dr).toUpperCase();
  }
  function bimGizmoPlainReadout(dr){
    function deg(r){return (Math.round(r*180/Math.PI*10)/10)+'\u00b0';}
    if(dr.rot)return 'ROTATE Z  '+deg(-dr.rotAngle);
    if(dr.gk==='axis')return bimGizAxis(dr.axis).lab+'  '+bimFmtLen(dr.gizDist);
    if(dr.gk==='plane'||(dr.gk==='centre'&&!dr.snapWorld))
      return dr.labA+' '+bimFmtLen(dr.da)+'   '+dr.labB+' '+bimFmtLen(dr.db);
    if(dr.gk==='centre'){
      var v=dr.gizVec||[0,0,0];
      return 'MOVE  '+bimFmtLen(Math.sqrt(v[0]*v[0]+v[1]*v[1]+v[2]*v[2]));
    }
    if(dr.gk==='scale')return 'SCALE '+(dr.uniform?'':bimGizAxis(dr.axis).lab+' ')+' '+(Math.round(dr.factor*1000)/1000);
    if(dr.gk==='tilt')return 'ROTATE '+(dr.lab||'')+'  '+deg(dr.tiltAngle);   /* __acad3dV111 */
    return '';
  }
  function bimDrawGizmo(ctx,V,W,H){
    A3D.gizmo=null;
    if(!bimGizmoVisible())return;
    var g=bimGizmoGeom(V,W,H);
    if(!g)return;
    A3D.gizmo=g;
    var dk=(drag&&drag.giz)?drag.gk:null;
    var rotting=!!(drag&&drag.rot);
    var hov=(!drag)?A3D.gizHover:null;      /* __acad3dV111: highlight what the cursor is over */
    var gold='#ffd479',warm='#ffe9a8',i,j;
    ctx.save();
    ctx.lineCap='round';ctx.lineJoin='round';
    /* __acad3dV111: the far half of every ring first and faded, so the rings read as circles in
       space; the near halves go on last, over the handles they pass behind. */
    for(i=0;i<g.rings.length;i++)bimGizDrawRing(ctx,g.rings[i],false,hov,dk,rotting,gold,warm);
    /* the swept angle, as the reference tools show it: a filled sector from where the drag started
       to where it is now, in the ring's own plane, with a witness line at each end */
    if(drag&&(drag.rot||dk==='tilt'))bimGizDrawSweep(ctx,g,V,W,H,gold);
    ctx.setLineDash([3,3]);
    ctx.lineWidth=1.2;
    for(i=0;i<g.scales.length;i++){
      ctx.strokeStyle=g.scales[i].col;
      ctx.beginPath();ctx.moveTo(g.ox,g.oy);ctx.lineTo(g.scales[i].x,g.scales[i].y);ctx.stroke();
    }
    ctx.setLineDash([]);
    if(g.uniform){
      var onu=(dk==='scale'&&drag.uniform)||hov==='uniform';
      ctx.beginPath();
      ctx.moveTo(g.uniform.tri[0][0],g.uniform.tri[0][1]);
      ctx.lineTo(g.uniform.tri[1][0],g.uniform.tri[1][1]);
      ctx.lineTo(g.uniform.tri[2][0],g.uniform.tri[2][1]);
      ctx.closePath();
      ctx.globalAlpha=onu?0.5:0.22;
      ctx.fillStyle=onu?gold:'#c8d2dd';
      ctx.fill();
      ctx.globalAlpha=1;
      ctx.strokeStyle=onu?gold:'rgba(200,210,221,0.75)';
      ctx.lineWidth=1.2;
      ctx.stroke();
    }
    for(i=0;i<g.planes.length;i++){
      var pl=g.planes[i],onp=(dk==='plane'&&drag.plane===pl.k)||hov==='plane:'+pl.k;
      ctx.beginPath();
      ctx.moveTo(pl.quad[0][0],pl.quad[0][1]);
      for(j=1;j<pl.quad.length;j++)ctx.lineTo(pl.quad[j][0],pl.quad[j][1]);
      ctx.closePath();
      ctx.globalAlpha=onp?0.65:0.45;
      ctx.fillStyle=onp?gold:pl.col;
      ctx.fill();
      ctx.globalAlpha=1;
      /* a dark rim under the coloured one, so a square reads over a light, selected face as
         well as over the dark background -- the blue plan square vanished on a selected box */
      ctx.strokeStyle='rgba(13,17,23,0.85)';
      ctx.lineWidth=3;
      ctx.stroke();
      ctx.strokeStyle=onp?gold:pl.col;
      ctx.lineWidth=1.4;
      ctx.stroke();
    }
    for(i=0;i<g.arms.length;i++){
      var a=g.arms[i],on=(dk==='axis'&&drag.axis===a.axis),onh=on||hov==='axis:'+a.axis;
      var ux=a.x1-a.x0,uy=a.y1-a.y0,L=Math.sqrt(ux*ux+uy*uy)||1;
      ux/=L;uy/=L;
      ctx.strokeStyle=on?gold:(onh?warm:a.col);
      ctx.lineWidth=onh?3.4:2.4;
      ctx.beginPath();
      ctx.moveTo(a.x0,a.y0);
      ctx.lineTo(a.x1-ux*A3D_GIZ.head,a.y1-uy*A3D_GIZ.head);
      ctx.stroke();
      // arrow head, built from the arm's own screen direction so it points correctly under any
      // camera without a separate 2D/3D case
      var hx=a.x1,hy=a.y1,bx=a.x1-ux*A3D_GIZ.head,by=a.y1-uy*A3D_GIZ.head,w=5.2;
      ctx.fillStyle=on?gold:(onh?warm:a.col);
      ctx.beginPath();
      ctx.moveTo(hx,hy);
      ctx.lineTo(bx-uy*w,by+ux*w);
      ctx.lineTo(bx+uy*w,by-ux*w);
      ctx.closePath();
      ctx.fill();
      ctx.font='bold 10px "Segoe UI",Inter,system-ui,sans-serif';
      ctx.fillStyle=on?gold:(onh?warm:a.col);
      ctx.textAlign='center';ctx.textBaseline='middle';
      ctx.fillText(a.lab,a.x1+ux*9,a.y1+uy*9);
    }
    for(i=0;i<g.rings.length;i++)bimGizDrawRing(ctx,g.rings[i],true,hov,dk,rotting,gold,warm);
    for(i=0;i<g.scales.length;i++){
      var sq=g.scales[i];
      var ons=(dk==='scale'&&(drag.uniform||drag.axis===sq.axis))||hov==='scale:'+sq.axis;
      var bs=A3D_GIZ.box;
      ctx.fillStyle=ons?gold:sq.col;
      ctx.fillRect(sq.x-bs,sq.y-bs,bs*2,bs*2);
      ctx.strokeStyle='#0d1117';ctx.lineWidth=1;
      ctx.strokeRect(sq.x-bs,sq.y-bs,bs*2,bs*2);
    }
    /* __acad3dV112: where a snap has caught, marked on the point it caught */
    if(drag&&drag.snapAt){
      var sm=toScreen(drag.snapAt,V,W,H);
      if(isFinite(sm[0])&&isFinite(sm[1])){
        ctx.strokeStyle='#ffd479';ctx.lineWidth=1.6;
        ctx.strokeRect(sm[0]-6,sm[1]-6,12,12);
        ctx.beginPath();
        ctx.moveTo(sm[0]-9,sm[1]);ctx.lineTo(sm[0]+9,sm[1]);
        ctx.moveTo(sm[0],sm[1]-9);ctx.lineTo(sm[0],sm[1]+9);
        ctx.stroke();
      }
    }
    var ch=g.centre.h,onc=(dk==='centre')||dk==='pivot'||hov==='centre';
    ctx.fillStyle=onc?gold:'rgba(230,237,243,0.92)';
    ctx.fillRect(g.ox-ch,g.oy-ch,ch*2,ch*2);
    ctx.strokeStyle='#0d1117';ctx.lineWidth=1.3;
    ctx.strokeRect(g.ox-ch,g.oy-ch,ch*2,ch*2);
    /* __acad3dV112: a pivot the user placed is not the selection's middle, and the gizmo says so */
    if(A3D.gizPivot){
      ctx.strokeStyle=onc?gold:'#ffd479';
      ctx.lineWidth=1.4;
      ctx.beginPath();ctx.arc(g.ox,g.oy,ch+5,0,Math.PI*2);ctx.stroke();
    }
    /* Live read-out while dragging. Revit shows the distance as you move; without it a
       constrained drag is still drag-by-eye, which is most of what the constraint was for.
       __acad3dV111: with nothing being dragged the same box names the handle under the cursor,
       which is how a handle nobody has met before gets introduced. */
    var txt=(drag&&(drag.giz||drag.rot))?bimGizmoReadout(drag):(hov?A3D.gizHoverName:null);
    if(txt)bimGizDrawHud(ctx,g,txt,!drag);
    ctx.restore();
  }
  /* One ring, one half. The far half is faded and thinner: it is behind the object, and drawing it
     at full strength is what made a ring read as a flat ellipse. */
  function bimGizDrawRing(ctx,r,nearHalf,hov,dk,rotting,gold,warm){
    var on=(rotting&&r.kind==='vertical')||(dk==='tilt'&&drag&&drag.axis===r.axis);
    var onh=on||hov===(r.kind==='vertical'?'rotate':('tilt:'+r.axis));
    var i,started=false;
    ctx.save();
    ctx.globalAlpha=nearHalf?1:A3D_GIZ.farFade;
    ctx.strokeStyle=on?gold:(onh?warm:r.col);
    ctx.lineWidth=(onh?3.4:2)*(nearHalf?1:0.85);
    ctx.beginPath();
    for(i=0;i<r.pts.length-1;i++){
      var a=r.pts[i],b=r.pts[i+1];
      if(!!(a[2]&&b[2])!==nearHalf){started=false;continue;}
      if(!started){ctx.moveTo(a[0],a[1]);started=true;}
      ctx.lineTo(b[0],b[1]);
    }
    ctx.stroke();
    ctx.restore();
  }
  /* The swept sector, in the plane of whichever ring is being dragged. The vertical ring keeps the
     model's own angle sense (atan2(z, x)); a tilt carries its own basis. One function for both, so
     the picture and the rotation are read from the same numbers. */
  function bimGizDrawSweep(ctx,g,V,W,H,gold){
    var B,C,R,a0,ang,i,n=36,s;
    if(drag.rot){
      if(!g.ring)return;
      B=[1,0,0];C=[0,0,1];R=g.ring.R;a0=drag.a0;ang=drag.rotAngle||0;
    }else{
      B=drag.B;C=drag.C;R=drag.R;a0=drag.a0;ang=drag.tiltAngle||0;
    }
    if(!B||!C||!isFinite(R)||!ang)return;
    var o=drag.origin||drag.O||g.origin;
    ctx.save();
    ctx.beginPath();
    var so=toScreen(o,V,W,H);
    ctx.moveTo(so[0],so[1]);
    for(i=0;i<=n;i++){
      s=toScreen(bimGizArcPt(o,B,C,R,a0+ang*i/n),V,W,H);
      ctx.lineTo(s[0],s[1]);
    }
    ctx.closePath();
    ctx.globalAlpha=0.18;
    ctx.fillStyle=gold;
    ctx.fill();
    ctx.globalAlpha=1;
    var pa=toScreen(bimGizArcPt(o,B,C,R,a0),V,W,H);
    var pb=toScreen(bimGizArcPt(o,B,C,R,a0+ang),V,W,H);
    ctx.setLineDash([5,4]);
    ctx.strokeStyle='rgba(255,212,121,0.75)';
    ctx.lineWidth=1.3;
    ctx.beginPath();ctx.moveTo(so[0],so[1]);ctx.lineTo(pa[0],pa[1]);ctx.stroke();
    ctx.setLineDash([]);
    ctx.strokeStyle=gold;
    ctx.lineWidth=1.8;
    ctx.beginPath();ctx.moveTo(so[0],so[1]);ctx.lineTo(pb[0],pb[1]);ctx.stroke();
    ctx.restore();
  }
  /* The read-out box, placed clear of the rings rather than beside the origin: at the origin it
     sat squarely on the witness lines during a rotation, covering the reading it accompanies. */
  function bimGizDrawHud(ctx,g,txt,quiet){
    ctx.save();
    ctx.font='600 12px "Segoe UI",Inter,system-ui,sans-serif';
    var tw=ctx.measureText(txt).width;
    ctx.textAlign='left';ctx.textBaseline='middle';
    ctx.fillStyle=quiet?'rgba(13,17,23,0.78)':'rgba(13,17,23,0.88)';
    ctx.strokeStyle=quiet?'rgba(120,132,148,0.9)':'#4ea1ff';
    ctx.lineWidth=1;
    var minY=Infinity,maxX=-Infinity,i,j;
    for(i=0;i<g.rings.length;i++)for(j=0;j<g.rings[i].pts.length;j++){
      if(g.rings[i].pts[j][1]<minY)minY=g.rings[i].pts[j][1];
      if(g.rings[i].pts[j][0]>maxX)maxX=g.rings[i].pts[j][0];
    }
    var bx=isFinite(maxX)?(maxX-tw-16):(g.ox+14),by=isFinite(minY)?(minY-28):(g.oy-30);
    ctx.beginPath();
    if(ctx.roundRect)ctx.roundRect(bx,by,tw+16,20,4);
    else ctx.rect(bx,by,tw+16,20);
    ctx.fill();ctx.stroke();
    ctx.fillStyle=quiet?'#c8d2dd':'#e6edf3';
    ctx.fillText(txt,bx+8,by+10);
    ctx.restore();
  }
  /* Distance in the project's own unit, at a precision that is readable rather than exact --
     the read-out is a guide during the gesture; Properties carries the authoritative number.
     __acad3dV123: it said so and wrote metres and millimetres whatever the project was set to. It
     is the project's unit and precision now, through the function Properties shows a length with,
     so a read-out, every message that states a length and Properties give the same figure. */
  function bimFmtLen(d){
    var s=bimDispLen(d);
    if(s==='-0')s='0';
    return s+' '+bimUnitLabel();
  }
  /* __acad3dV110: one entry point for every handle; each kind builds its own drag record. */
  function bimGizmoBegin(hit,xy,ev){
    if(ev&&ev.shiftKey)hit.shift=true;                 /* __acad3dV112: Shift is precision */
    if(hit.rot)return bimGizmoBeginRotate(hit,xy);
    if(hit.kind==='axis')return bimGizmoBeginAxis(hit,xy,ev);
    if(hit.kind==='centre'&&ev&&ev.altKey)return bimGizmoBeginPivot(hit,xy);   /* __acad3dV112 */
    if(hit.kind==='plane'||hit.kind==='centre')return bimGizmoBeginPlane(hit,xy,ev);
    if(hit.kind==='scale')return bimGizmoBeginScale(hit,xy,!!(ev&&ev.shiftKey));
    if(hit.kind==='uniform')return bimGizmoBeginUniform(hit,xy);   /* __acad3dV111 */
    if(hit.kind==='tilt')return bimGizmoBeginTilt(hit,xy);
    return null;
  }
  /* __acad3dV112: OBJECT SNAPPING FOR THE GIZMO.

     Until now a gizmo drag could land on the grid and on nothing else, while every drawing tool in
     the app snapped to real geometry. A drafting program's move lands one point of what is moving
     onto one point of what is not: a wall end onto another wall's end, a column centre onto a grid
     node. That is what this does, and it does it through the freedom the handle allows -- along
     the axis for an arrow, within the plane for a square -- so a constrained drag stays
     constrained.

     Sources are the selection's own plan points; targets are everything else's, at the same
     elevation, from the same function the sketch tools use. Both are gathered once, at the start
     of the drag: they cannot change while it runs, and gathering them per frame was the only way
     this could be slow. */
  function bimGizmoOwnPoints(ids){
    var out=[],i,j;
    for(i=0;i<ids.length;i++){
      var o=objById(ids[i]);
      if(!o)continue;
      var q=bimObjOffset(o),y=null,pts=null;
      if(o.t==='sketch'&&o.pts){y=(o.y||0)+q[1];pts=o.pts;}
      else if(o.bim&&o.bim.centerline){y=(o.bim.baseY||0)+q[1];pts=o.bim.centerline;}
      else if(o.bim&&o.bim.profile){y=(o.bim.baseY||0)+q[1];pts=o.bim.profile;}
      else if(o.bim&&o.bim.center){y=(o.bim.baseY||0)+q[1];pts=[o.bim.center];}
      else if(o.t==='room'&&o.pts){y=(o.y||0)+q[1];pts=o.pts;}
      if(!pts)continue;
      for(j=0;j<pts.length&&out.length<A3D_GIZ.snapSrc;j++)
        out.push([pts[j][0]+q[0],y,pts[j][1]+q[2]]);
    }
    return out;
  }
  function bimGizmoSnapSetup(ids){
    var src=bimGizmoOwnPoints(ids);
    if(!src.length)return null;
    var elevs=[],i,j,tg=[];
    for(i=0;i<src.length;i++){
      for(j=0;j<elevs.length;j++)if(Math.abs(elevs[j]-src[i][1])<0.05)break;
      if(j===elevs.length)elevs.push(src[i][1]);
    }
    for(i=0;i<elevs.length;i++){
      var c=bimSnapCandidates(elevs[i],ids);
      for(j=0;j<c.length&&tg.length<A3D_GIZ.snapTgt;j++)tg.push([c[j][0],elevs[i],c[j][1]]);
    }
    return tg.length?{src:src,tgt:tg}:null;
  }
  /* The offset the handle would take if it landed a source point on a target point, tested against
     the offset the cursor is asking for. An arrow may only move along its axis, so the candidate
     offset is the component of (target - source) along it and the rest is residual; a square may
     move anywhere in its plane, so the residual is only what leaves the plane. A candidate counts
     when the point it lands on is within the snap threshold of the target ON SCREEN -- pixels,
     because that is what the user is aiming with -- and when the landing is near where the cursor
     already is, so a snap pulls rather than teleports. */
  function bimGizmoSnapVec(v,dirs){
    var sn=drag.snaps;
    if(!A3D_SNAP.point||!sn)return null;
    var V=camVecs(A3D.cam),W=cvW(),H=cvH(),i,j,k;
    var best=null,bestD=1e9,px=A3D_SNAP.pxThreshold;
    for(i=0;i<sn.src.length;i++)for(j=0;j<sn.tgt.length;j++){
      var s=sn.src[i],t=sn.tgt[j];
      var want=[t[0]-s[0],t[1]-s[1],t[2]-s[2]],cand=[0,0,0];
      for(k=0;k<dirs.length;k++){
        var d=dirs[k],a=want[0]*d[0]+want[1]*d[1]+want[2]*d[2];
        cand[0]+=d[0]*a;cand[1]+=d[1]*a;cand[2]+=d[2]*a;
      }
      var land=[s[0]+cand[0],s[1]+cand[1],s[2]+cand[2]];
      var sl=toScreen(land,V,W,H),st=toScreen(t,V,W,H);
      var res=Math.sqrt((sl[0]-st[0])*(sl[0]-st[0])+(sl[1]-st[1])*(sl[1]-st[1]));
      if(!isFinite(res)||res>px)continue;                 // the handle cannot reach this target
      var now=[s[0]+v[0],s[1]+v[1],s[2]+v[2]];
      var sn2=toScreen(now,V,W,H);
      var pull=Math.sqrt((sl[0]-sn2[0])*(sl[0]-sn2[0])+(sl[1]-sn2[1])*(sl[1]-sn2[1]));
      if(pull>px)continue;                                // the cursor is not near it yet
      if(pull+res<bestD){bestD=pull+res;best={v:cand,at:land,tgt:t};}
    }
    return best;
  }
  /* __acad3dV112: Ctrl on a move handle copies. The copies are made where the originals are and
     the drag takes the COPIES, so the originals stay exactly where they were -- which is what
     makes this a copy rather than a move that leaves something behind. */
  function bimGizmoCopySelection(ids){
    var made=[],pairs=[],i,prevSel=A3D.sel,prevSet=(A3D.selSet||[]).slice();
    for(i=0;i<ids.length;i++){
      var o=objById(ids[i]);
      if(!o)continue;
      var c=bimDuplicateObject(o,0,0);
      if(c){A3D.objs.push(c);made.push(c.id);pairs.push([o,c]);}
    }
    var cut=pairs.length?bimRelinkCopies(pairs,0,0,0):0;   /* __acad3dV124 */
    if(!made.length){
      console.warn('[BIM] Ctrl-drag: nothing in the selection could be copied.');
      a3dToast('These object(s) cannot be copied - dragging the originals instead');
      return null;
    }
    A3D.selSet=made;A3D.sel=made[0];A3D.sel2=null;
    a3dToast('Copying '+made.length+' object(s) - the originals stay where they are'+bimRelinkNote(cut));
    refreshTree();
    return {ids:made,sel:prevSel,set:prevSet};
  }
  function bimGizmoDropCopies(c){
    if(!c||!c.ids)return;
    A3D.objs=A3D.objs.filter(function(o){return c.ids.indexOf(o.id)<0;});
    A3D.selSet=c.set||[];A3D.sel=c.sel||null;A3D.sel2=null;
    refreshTree();
  }
  function bimGizmoStarts(ids){
    var out=[],i;
    for(i=0;i<ids.length;i++){
      var o=objById(ids[i]);
      out.push(o&&o.pos?[o.pos[0],o.pos[1],o.pos[2]]:[0,0,0]);
    }
    return out;
  }
  function bimGizmoBeginAxis(hit,xy,ev){
    var a=hit.arm;
    var len2=a.sx*a.sx+a.sy*a.sy;
    /* An axis almost parallel to the view direction projects to almost nothing, and the division
       in the drag would turn a few pixels of cursor movement into an enormous world distance.
       Refuse rather than fling the object out of the model. */
    if(!isFinite(len2)||len2<1e-4){
      console.warn('[BIM] Gizmo axis '+a.lab+' is edge-on to the camera; drag refused.');
      a3dToast('Rotate the view to drag along '+a.lab+' - that axis is edge-on');
      return null;
    }
    return {giz:true,gk:'axis',axis:a.axis,dir:a.dir,sx:a.sx,sy:a.sy,len2:len2,
            ids:hit.giz.ids,start:bimGizmoStarts(hit.giz.ids),x0:xy[0],y0:xy[1],
            snaps:bimGizmoSnapSetup(hit.giz.ids),          /* __acad3dV112 */
            fine:!!(ev&&ev.shiftKey),                      /* __acad3dV112: Shift is precision */
            gizDist:0,gizVec:[0,0,0],moved:false};
  }
  /* A plane square moves in the plane of its two axes. The centre square moves in the plan
     plane in a 2D view -- the frame's two horizontal axes -- and in the screen plane in 3D, where
     no single pair of model axes is what the user sees. Both read the cursor as the point where
     its ray meets that plane, so the object stays under the cursor at any camera. */
  function bimGizmoBeginPlane(hit,xy,ev){
    var g=hit.giz,a,b,la,lb,snapWorld=false;
    if(hit.kind==='plane'){
      a=hit.plane.da;b=hit.plane.db;
      la=bimGizAxis(hit.plane.a).lab;lb=bimGizAxis(hit.plane.b).lab;
    }else if(A3D.flat){
      a=g.frame.x;b=g.frame.z;la=bimGizAxis('x').lab;lb=bimGizAxis('z').lab;
      if(Math.abs(a[1])>1e-6||Math.abs(b[1])>1e-6){a=[1,0,0];b=[0,0,-1];la='X';lb='Y';}
    }else{
      var V=camVecs(A3D.cam);
      a=V.r.slice();b=V.u.slice();la='';lb='';snapWorld=true;
    }
    var N=vnorm(vcross(a,b));
    var P0=bimRayPlane(xy[0],xy[1],g.origin,N,0.12);
    if(!P0){
      console.warn('[BIM] Gizmo plane is edge-on to the camera; drag refused.');
      a3dToast('Rotate the view to drag in that plane - it is edge-on');
      return null;
    }
    return {giz:true,gk:hit.kind,plane:hit.kind==='plane'?hit.plane.k:null,a:a.slice(),b:b.slice(),n:N,
            fr:g.frame,                                    /* __acad3dV123: what a typed X, Y, Z is along */
            labA:la,labB:lb,snapWorld:snapWorld,O:g.origin.slice(),P0:P0,
            snaps:bimGizmoSnapSetup(g.ids),                /* __acad3dV112 */
            fine:!!(ev&&ev.shiftKey),                      /* __acad3dV112 */
            ids:g.ids,start:bimGizmoStarts(g.ids),x0:xy[0],y0:xy[1],da:0,db:0,gizVec:[0,0,0],moved:false};
  }
  /* A scale box scales along its own axis about the gizmo origin, by the ratio of the box's new
     distance from the origin to its old one; Shift scales evenly. A sketch with arcs refuses a
     one-way scale, because an arc stretched one way is an ellipse, which a sketch cannot hold. */
  function bimGizmoBeginScale(hit,xy,uniform){
    var g=hit.giz,sq=hit.sq;
    if(!uniform&&g.caps.arcs){
      console.warn('[BIM] One-way scale refused: a sketch in the selection has arcs.');
      a3dToast('A sketch with arcs only scales evenly - hold Shift while you drag (an arc stretched one way is no longer an arc)');
      return null;
    }
    return {giz:true,gk:'scale',axis:sq.axis,uniform:uniform,dir:sq.dir.slice(),O:g.origin.slice(),
            L:sq.L,ux:sq.ux,uy:sq.uy,ids:g.ids,snap:bimGizmoSnapObjs(g.ids),
            x0:xy[0],y0:xy[1],factor:1,moved:false};
  }
  /* __acad3dV112: moving the GIZMO rather than the model. Alt on the centre square drags the
     pivot every other handle turns and scales about -- 3ds Max's Affect Pivot Only, Blender's 3D
     cursor, the reposition every reference tool has. It lands on real points like any other drag,
     and the gizmo menu puts it back at the selection's middle. */
  function bimGizmoBeginPivot(hit,xy){
    var g=hit.giz,N,a,b;
    if(A3D.flat){a=[1,0,0];b=[0,0,-1];}
    else{var V=camVecs(A3D.cam);a=V.r.slice();b=V.u.slice();}
    N=vnorm(vcross(a,b));
    var P0=bimRayPlane(xy[0],xy[1],g.origin,N,0.12);
    if(!P0){
      console.warn('[BIM] The pivot drag plane is edge-on; drag refused.');
      a3dToast('Rotate the view a little to move the pivot');
      return null;
    }
    return {giz:true,gk:'pivot',a:a,b:b,n:N,O:g.origin.slice(),P0:P0,pivot0:A3D.gizPivot?A3D.gizPivot.slice():null,
            snaps:{src:[g.origin.slice()],tgt:(bimGizmoSnapSetup(g.ids)||{tgt:[]}).tgt},
            ids:g.ids,x0:xy[0],y0:xy[1],moved:false};
  }
  function bimGizmoApplyPivot(xy){
    var P=bimRayPlane(xy[0],xy[1],drag.O,drag.n,0.05);
    if(!P)return;
    var v=[P[0]-drag.P0[0],P[1]-drag.P0[1],P[2]-drag.P0[2]];
    var gs=(A3D_SNAP.grid&&A3D_SNAP.gridSize>0)?A3D_SNAP.gridSize:0;
    if(gs)v=[Math.round(v[0]/gs)*gs,Math.round(v[1]/gs)*gs,Math.round(v[2]/gs)*gs];
    var sn=bimGizmoSnapVec(v,[drag.a,drag.b]);
    drag.snapAt=sn?sn.at:null;
    if(sn)v=sn.v;
    A3D.gizPivot=[drag.O[0]+v[0],drag.O[1]+v[1],drag.O[2]+v[2]];
  }
  /* __acad3dV111: the even-scale triangle. It and Shift on a box are the same drag with the same
     read-out; the difference is only how the factor is read -- here it is how much further from
     the gizmo's centre the cursor is than where it was pressed, which is the gesture 3ds Max's
     uniform region uses and the only one that makes sense for a handle with no axis of its own. */
  function bimGizmoBeginUniform(hit,xy){
    var g=hit.giz;
    var dx=xy[0]-g.ox,dy=xy[1]-g.oy,L=Math.sqrt(dx*dx+dy*dy);
    if(!isFinite(L)||L<A3D_GIZ.centre+6){
      console.warn('[BIM] Even scale: the press was on the gizmo centre, which has no radius to scale by.');
      a3dToast('Grab the triangle away from the centre to scale evenly');
      return null;
    }
    return {giz:true,gk:'scale',axis:null,uniform:true,radial:true,L0:L,sox:g.ox,soy:g.oy,
            O:g.origin.slice(),ids:g.ids,snap:bimGizmoSnapObjs(g.ids),
            x0:xy[0],y0:xy[1],factor:1,moved:false};
  }
  /* A rotate ring turns about its axis through the gizmo origin. The angle is read in the MODEL, as
     the ring's is: the cursor ray meets the arc's own plane, and the angle is measured there, so
     an arc seen at a slant does not make the object lag the cursor. */
  function bimGizmoBeginTilt(hit,xy){
    var g=hit.giz,arc=hit.arc;
    var P=bimRayPlane(xy[0],xy[1],g.origin,arc.A,0.12);
    var a0=P?bimGizArcAngle(P,g.origin,arc.B,arc.C):null;
    if(a0===null){
      console.warn('[BIM] Rotate ring '+bimGizRingLab(arc)+': its plane is edge-on, or the cursor is on the centre.');
      a3dToast('Rotate the view a little to turn about '+bimGizRingLab(arc)+' - that ring is edge-on');
      return null;
    }
    return {giz:true,gk:'tilt',axis:arc.axis,A:arc.A.slice(),B:arc.B.slice(),C:arc.C.slice(),
            R:arc.R,lab:bimGizRingLab(arc),                      /* __acad3dV111: for the sweep */
            O:g.origin.slice(),a0:a0,tiltAngle:0,ids:g.ids,snap:bimGizmoSnapObjs(g.ids),
            fine:!!(hit.shift),                            /* __acad3dV112 */
            x0:xy[0],y0:xy[1],moved:false};
  }
  function bimGizArcAngle(P,O,B,C){
    var d=[P[0]-O[0],P[1]-O[1],P[2]-O[2]];
    var x=vdot(d,B),y=vdot(d,C);
    if(Math.sqrt(x*x+y*y)<1e-9)return null;
    return Math.atan2(y,x);
  }
  /* A deep copy of every object the rotation will touch, taken once at drag start. Each frame
     restores from this and applies the TOTAL angle, rather than nudging the previous frame's
     result: incremental rotation accumulates floating-point drift over hundreds of mousemoves,
     and re-runs bimBuildWallGeometry on already-rebuilt geometry, so a wall's mitred joints would
     degrade a little on every frame of a slow drag. */
  function bimGizmoSnapObjs(ids){
    var out=[],i;
    for(i=0;i<ids.length;i++){
      var o=objById(ids[i]);
      out.push(o?JSON.parse(JSON.stringify(o)):null);
    }
    return out;
  }
  function bimGizmoRestoreObjs(ids,snap){
    var i,j;
    for(i=0;i<ids.length;i++){
      if(!snap[i])continue;
      for(j=0;j<A3D.objs.length;j++){
        if(A3D.objs[j].id===ids[i]){
          A3D.objs[j]=JSON.parse(JSON.stringify(snap[i]));
          break;
        }
      }
    }
  }
  /* __acad3dV81: which of the selected objects can actually turn, asked BEFORE the gesture.
     Roofs, stairs and openings genuinely cannot be transformed -- that limitation is unchanged --
     but the ring used to read 'ANGLE 45' over an object sitting perfectly still and only mention
     it on release. A probe is cheap: run the transform against a zero-angle rotation and see
     whether it reports an error, which asks the real dispatcher rather than a second list of
     types that would drift away from it. */
  function bimRotatableSplit(ids){
    var ok=[],no=[],i;
    for(i=0;i<ids.length;i++){
      var o=objById(ids[i]);
      if(!o)continue;
      var probe=bimComputeTransformedGeometry(o,function(p){return [p[0],p[1]];},
        {kind:'rotate',angle:0});
      if(probe&&probe.error)no.push(o.name);else ok.push(ids[i]);
    }
    return {ok:ok,no:no};
  }
  function bimGizmoBeginRotate(hit,xy){
    var g=hit.giz;
    var split=bimRotatableSplit(g.ids);
    if(!split.ok.length){
      console.warn('[BIM] Nothing in the selection can be rotated: '+split.no.join(', '));
      a3dToast('Nothing selected can be rotated \u2014 '+split.no.slice(0,3).join(', ')+
        (split.no.length>3?' and others':''));
      return null;
    }
    if(split.no.length)
      a3dToast(split.no.length+' object(s) will not rotate: '+split.no.slice(0,2).join(', ')+
        (split.no.length>2?' and others':''));
    var a0=bimGizmoAngleAt(xy,g.origin);
    if(a0===null){
      console.warn('[BIM] Rotate ring: the plan plane is edge-on, or the cursor is on the centre.');
      a3dToast('Tilt the view a little to rotate \u2014 the rotation plane is edge-on');
      return null;
    }
    return {rot:true,ids:split.ok.slice(),origin:g.origin.slice(),
            center:[g.origin[0],g.origin[2]],
            snap:bimGizmoSnapObjs(split.ok),
            fine:!!(hit.shift),                            /* __acad3dV112 */
            a0:a0,rotAngle:0,x0:xy[0],y0:xy[1],moved:false};
  }
  function bimGizmoApplyRotate(xy){
    if(!drag||!drag.rot)return;
    var a=bimGizmoAngleAt(xy,drag.origin);
    if(a===null)return;
    var d=a-drag.a0;
    // keep the reported angle in (-180, 180] so a drag past the far side reads as -170, not +190
    while(d>Math.PI)d-=Math.PI*2;
    while(d<-Math.PI)d+=Math.PI*2;
    /* ORTHO is the toggle already in the status bar, and already means "constrain to clean
       directions" for the sketch tools -- so it means 15-degree increments here rather than
       introducing a second modifier the user has to discover. */
    if(drag.fine)d*=A3D_GIZ.fine;                      /* __acad3dV112 */
    if(A3D_SNAP.ortho){
      var step=Math.PI/12;
      d=Math.round(d/step)*step;
    }
    bimGizmoRotateTo(d);
  }
  /* __acad3dV112: the rotation itself, by a TOTAL angle, whether that angle came from the cursor
     or was typed. Every frame restores the snapshot and applies the total, so nothing drifts. */
  function bimGizmoRotateTo(d){
    if(!drag||!drag.rot)return;
    drag.rotAngle=d;
    bimGizmoRestoreObjs(drag.ids,drag.snap);
    var i,failed=0;
    for(i=0;i<drag.ids.length;i++){
      var o=objById(drag.ids[i]);
      if(!o)continue;
      if(!bimRotateObjectInPlace(o,drag.center,d))failed++;
    }
    drag.rotFailed=failed;
    paint();saveSoon();
  }
  /* __acad3dV112: everything that has to happen once a gizmo gesture is over. The objects' own
     geometry is already correct -- the drag did that live -- so what settles here is everything
     DEPENDENT on them, walked once with the gesture's total: 'transform' with the vector for a
     move, 'rebuild' for a rotation or a scale, because a dependent room is re-measured from the
     turned walls rather than shifted by them. */
  function bimGizmoEndDrag(d){
    if(d.pp){bimPushEnd(d.rec);return;}   /* __acad3dV123 */
    if(d.rot){
      if(d.angle)bimPropagateFrom(d.ids,'rebuild');
      if(d.rotFailed)a3dToast(d.rotFailed+' object(s) could not be rotated \u2014 see the console');
    }else if(d.gk==='scale'||d.gk==='tilt'){
      if(d.gk==='scale'?(d.factor!==1):!!d.tilt)bimPropagateFrom(d.ids,'rebuild');
      if(d.failed)a3dToast(d.failed+' object(s) could not be '+(d.gk==='scale'?'scaled':'tilted')+' - see the console');
    }else if(d.vec&&(d.vec[0]||d.vec[1]||d.vec[2])){
      bimPropagateFrom(d.ids,'transform',d.vec);
    }
    bimFlushMaterialized();
    refreshTree();refreshProps();paint();saveSoon();
  }
  /* __acad3dV112: TYPING AN EXACT VALUE DURING A DRAG.

     Every drafting program lets a gesture be finished with a number: AutoCAD's direct distance
     entry, Revit's listening dimension. The gesture says WHICH WAY and the number says HOW FAR, so
     a typed distance keeps the direction the cursor is already showing and only replaces its
     size. An angle is typed the way the read-out shows it (counter-clockwise positive, seen from
     the axis's own end) and a scale is typed as a factor.

     Enter applies it and ends the drag through the same path the mouse uses. Escape puts
     everything back where it was. */
  var A3D_GIZ_TYPE={active:false,buf:''};
  function bimGizmoTyping(){return A3D_GIZ_TYPE.active?A3D_GIZ_TYPE.buf:null;}
  function bimGizmoTypeClear(){A3D_GIZ_TYPE.active=false;A3D_GIZ_TYPE.buf='';}
  /* __acad3dV123: the drag that is listening for a typed value, if any -- one test, read by the key
     handler, the key claim and the read-out. */
  function bimTypingDrag(){
    return (drag&&(drag.giz||drag.rot||(drag.pp&&drag.moved&&drag.f)))?drag:null;   /* a push listens too */
  }
  /* __acad3dV123: WHAT A HANDLE TAKES. A length along an arrow; two along a plane square, or along
     the free-move square in a plan; three along the gizmo's X, Y and Z for the free-move square in
     3D; an angle on a ring; a factor on a scale handle. The characters accepted while typing, the
     parser, the unit in the read-out and the commit all read this -- before V123 a free move could
     not be typed at all, because the commit had no case for it. */
  function bimGizmoValueKind(r){
    if(!r)return null;
    if(r.pp)return 'len';   /* a push: how far */
    /* a drag record carries gk and snapWorld; a picked handle carries kind -- one rule for both, so
       what the hover hint promises is what the drag and the value box take */
    var k=r.gk||r.kind;
    if(r.rot||k==='tilt')return 'deg';
    if(k==='scale'||k==='uniform')return 'factor';
    if(k==='axis')return 'len';
    if(k==='plane')return 'len2';
    if(k==='centre')return (r.gk?r.snapWorld:!A3D.flat)?'len3':'len2';
    return null;
  }
  function bimGizmoValueCount(kind){return kind==='len2'?2:(kind==='len3'?3:1);}
  function bimGizmoUnitSuffix(kind){
    if(kind==='deg')return '\u00b0';
    if(kind==='factor'||!kind)return '';
    return ' '+bimUnitLabel();
  }
  /* A typed value as numbers, lengths in metres. A length is typed in the project's unit: in a
     millimetre project 500 is half a metre. Before V123 it was taken as metres whatever the project
     showed, so 500 typed there moved the selection half a kilometre. X,Y on the free-move square in
     3D leaves Z at nought. */
  function bimGizmoParseValue(kind,text){
    if(!kind)return {error:'This handle is placed by dragging it'};
    var parts=String(text===undefined||text===null?'':text).split(','),nums=[],i,n=bimGizmoValueCount(kind);
    for(i=0;i<parts.length;i++){
      var p=parts[i].replace(/^\s+|\s+$/g,'');
      if(!/^[-+]?(\d+\.?\d*|\.\d+)$/.test(p))return {error:'Not a number: '+(p||'(nothing)')};
      nums.push(parseFloat(p));
    }
    if(kind==='len3'&&nums.length===2)nums.push(0);
    if(nums.length!==n)
      return {error:kind==='len2'?'Type two numbers: X,Y':(kind==='len3'?'Type X,Y or X,Y,Z':'Type one number')};
    if(kind==='factor'&&!(nums[0]>0))return {error:'A scale factor has to be greater than zero'};
    if(kind==='len'||kind==='len2'||kind==='len3'){
      var sc=bimUnitDef().scale;
      for(i=0;i<nums.length;i++)nums[i]=nums[i]/sc;
    }
    return {v:nums};
  }
  /* One value, applied to the running drag rec (the global drag), however it was typed. keepSign is
     typing during a drag along an arrow: the gesture chose the direction and the number only
     replaces the distance, as V112 had it. A value with no gesture behind it keeps its own sign. */
  function bimGizmoApplyValue(rec,nums,keepSign){
    var kind=bimGizmoValueKind(rec);
    if(rec.pp){
      /* a typed push keeps the direction the drag shows; a distance it will not take leaves the drag
         running where it was, and says why */
      if(!bimPushTo(keepSign?((rec.dist<0)?-1:1)*Math.abs(nums[0]):nums[0],true)){a3dToast(rec.limit||'That is further than this face can go');return null;}
      return {pp:true,rec:rec};
    }
    if(kind==='deg'){
      if(rec.rot){
        /* the read-out is Revit's sense; the model's own angle runs the other way about the vertical */
        bimGizmoRotateTo(-nums[0]*Math.PI/180);
        return {rot:true,ids:rec.ids,angle:rec.rotAngle,rotFailed:rec.rotFailed};
      }
      bimGizmoTiltTo(nums[0]*Math.PI/180);
      return {gk:'tilt',ids:rec.ids,tilt:rec.tiltAngle,failed:rec.gizFailed};
    }
    if(kind==='factor'){
      bimGizmoScaleTo(nums[0]);
      return {gk:'scale',ids:rec.ids,factor:rec.factor,failed:rec.gizFailed};
    }
    if(kind==='len'){
      bimGizmoAxisTo(keepSign?((rec.gizDist<0)?-1:1)*Math.abs(nums[0]):nums[0]);
      return {gk:'axis',ids:rec.ids,vec:rec.gizVec};
    }
    /* two or three lengths: along the square's own two axes, or the gizmo's X, Y and Z */
    var dirs=(kind==='len3'&&rec.fr)?[rec.fr.x,rec.fr.z,rec.fr.y]:[rec.a,rec.b],v=[0,0,0],i,k;
    for(i=0;i<dirs.length&&i<nums.length;i++)for(k=0;k<3;k++)v[k]+=dirs[i][k]*nums[i];
    rec.da=nums[0];rec.db=nums[1];rec.snapAt=null;rec.gizVec=v;
    bimGizmoSetPos(v);
    paint();saveSoon();
    return {gk:rec.gk,ids:rec.ids,vec:v};
  }
  /* __acad3dV123: whether a character goes into the value being typed -- digits and a point always,
     a minus at the start of a number, a comma between numbers only where the handle takes more than
     one. Every one of these characters is consumed while a drag listens, typed or not, so a stray
     minus cannot reach a shortcut; the claim below says the same. */
  function bimGizmoTypeChar(rec,k,buf){
    if(/^[0-9]$/.test(k)||k==='.')return true;
    if(k==='-')return !buf||buf.charAt(buf.length-1)===',';
    if(k!==',')return false;
    var n=bimGizmoValueCount(bimGizmoValueKind(rec));
    return n>1&&!!buf&&buf.charAt(buf.length-1)!==','&&buf.split(',').length<n;
  }
  function bimGizmoTypeKey(ev){
    var d=bimTypingDrag();
    if(!d)return false;
    var k=ev.key;
    /* __acad3dV112: Escape ends the gesture whatever is held down -- a Ctrl-drag copy and an
       Alt-drag of the pivot are exactly the drags most worth being able to call off, and testing
       the modifiers first meant neither of them could be. */
    if(k==='Escape'){bimGizmoCancelDrag();return true;}
    if(ev.ctrlKey||ev.metaKey||ev.altKey)return false;
    if(/^[0-9.,-]$/.test(k)){
      if(bimGizmoTypeChar(d,k,A3D_GIZ_TYPE.buf)){A3D_GIZ_TYPE.active=true;A3D_GIZ_TYPE.buf+=k;}
      paint();return true;
    }
    if(k==='Backspace'&&A3D_GIZ_TYPE.active){
      A3D_GIZ_TYPE.buf=A3D_GIZ_TYPE.buf.slice(0,-1);
      if(!A3D_GIZ_TYPE.buf)A3D_GIZ_TYPE.active=false;
      paint();return true;
    }
    if(k==='Enter'&&A3D_GIZ_TYPE.active)return bimGizmoTypedCommit();
    return false;
  }
  /* __acad3dV112: which keys a running gizmo drag is entitled to, asked by the workspace-era
     gates through __a3dWantsKey before they swallow one. Same predicate the handler above reads,
     so what is claimed and what is acted on cannot drift apart. */
  function bimGizmoWantsKey(ev){
    if(!bimTypingDrag())return false;
    var k=ev.key;
    if(k==='Escape')return true;
    if(ev.ctrlKey||ev.metaKey||ev.altKey)return false;
    return /^[0-9.,-]$/.test(k)||k==='Backspace'||k==='Enter';
  }
  function bimGizmoTypedCommit(){
    var d=bimTypingDrag(),text=A3D_GIZ_TYPE.buf;
    bimGizmoTypeClear();
    if(!d){paint();return true;}
    var p=bimGizmoParseValue(bimGizmoValueKind(d),text);
    if(p.error){a3dToast(p.error);paint();return true;}
    var summary=bimGizmoApplyValue(d,p.v,true);
    if(!summary){paint();return true;}
    drag=null;
    bimGizmoEndDrag(summary);
    return true;
  }
  /* __acad3dV123: what a handle takes, in words: the value box's label, and in capitals the read-out
     of a value typed during a drag. From a picked handle or from a drag record. */
  function bimGizmoValueLabel(r){
    var k=r.gk||r.kind,kind=bimGizmoValueKind(r);
    if(r.pp)return 'Distance';
    if(r.rot)return 'Rotate Z';
    if(k==='tilt')return 'Rotate '+(r.lab||bimGizRingLab(r.arc||r.ring));
    if(k==='scale')return r.uniform?'Scale evenly':('Scale '+bimGizAxis(r.axis).lab);
    if(k==='uniform')return 'Scale evenly';
    if(k==='axis')return 'Move '+bimGizAxis(r.axis).lab;
    if(k==='plane'&&r.labA)return 'Move '+r.labA+', '+r.labB;
    if(k==='plane'&&r.plane&&r.plane.a)return 'Move '+bimGizAxis(r.plane.a).lab+', '+bimGizAxis(r.plane.b).lab;
    if(kind==='len3')return 'Move X, Y, Z';
    if(kind==='len2')return 'Move X, Y';
    return 'Move';
  }
  /* __acad3dV123: WHAT A HANDLE DOES, as the status bar says it while the cursor is on it: the drag,
     the click, and the modifiers its press reads -- the copy rule in onDown (Ctrl on a move handle),
     Shift and Alt in bimGizmoBegin, ORTHO's steps on a ring. The V123 suite drives each claim. */
  function bimGizmoHandleHint(h){
    if(!h)return '';
    var k=h.kind,kind=bimGizmoValueKind(h),what,mods;
    var ask=kind==='deg'?'an angle':(kind==='factor'?'a factor':(bimGizmoValueCount(kind)>1?'the distances':'a distance'));
    if(h.rot||k==='tilt'){what='drag to turn';mods='F8 turns in 15-degree steps, Shift is fine';}
    else if(k==='scale'){what='drag to stretch';mods='Shift scales evenly';}
    else if(k==='uniform'){what='drag to scale evenly';mods='';}
    else if(k==='centre'){what=A3D.flat?'drag to move in the plan':'drag to move across the screen';
      mods='Ctrl+drag copies, Alt+drag moves the pivot, Shift is fine';}
    else{what='drag to move';mods='Ctrl+drag copies, Shift is fine';}
    var nm=bimGizmoHandleName(h);
    return nm.charAt(0).toUpperCase()+nm.slice(1)+': '+what+', click to type '+ask+(mods?'; '+mods:'');
  }
  /* __acad3dV123: the first movement of a gizmo drag -- the moment it stops being a click. The undo
     step is taken here, and a Ctrl drag makes its copies here and carries on with them, exactly as
     V112's did from the press. */
  function bimGizmoStartMoving(d){
    if(d.undoPending){pushUndo();d.undoPending=false;}
    if(d.copyPending){
      d.copyPending=false;
      var made=bimGizmoCopySelection(d.ids);
      if(made){
        d.copies=made;
        d.ids=made.ids.slice();
        d.start=bimGizmoStarts(d.ids);
        d.snaps=bimGizmoSnapSetup(d.ids);
      }
    }
  }
  /* __acad3dV123: A CLICK ON A HANDLE -- Rhino's gumball. The box asks for what the handle takes; Enter
     applies it through a drag begun then, so its snapshots are of the model as it is, and ends it on
     the path every drag ends by, as one undo step. A Ctrl+click does nothing, as in Revit, and the
     pivot is only ever dragged. */
  var A3D_CLICKBOX_T=null;
  function bimGizmoClickValue(rec,ev){
    paint();
    if(!rec||rec.copyPending||!rec.hit)return false;
    var kind=bimGizmoValueKind(rec);
    if(!kind)return false;
    var hit=rec.hit,xy=rec.xy0.slice(),mods=rec.mods||{},cx=ev.clientX,cy=ev.clientY;
    /* opened once a double-click can no longer be under way: the second click of one takes a face
       (V123) and must not find a box in its way. Nothing opens over a drag begun meanwhile. */
    if(A3D_CLICKBOX_T)clearTimeout(A3D_CLICKBOX_T);
    A3D_CLICKBOX_T=setTimeout(function(){
      A3D_CLICKBOX_T=null;
      if(drag)return;
      bimValueBox({x:cx,y:cy,label:bimGizmoValueLabel(rec),
        unit:bimGizmoUnitSuffix(kind).replace(/^ /,''),value:'',
        hint:bimGizmoValueCount(kind)>1?'Numbers separated by commas; Enter to apply, Esc to cancel':'Enter to apply, Esc to cancel',
        submit:function(text){
          var now=bimGizmoIds(),was=(hit.giz&&hit.giz.ids)||[],i;
          if(now.length!==was.length)return 'The selection has changed - click the handle again';
          for(i=0;i<now.length;i++)if(was.indexOf(now[i])<0)return 'The selection has changed - click the handle again';
          var p=bimGizmoParseValue(kind,text);
          if(p.error)return p.error;
          A3D_MATERIALIZED=[];
          var fresh=bimGizmoBegin(hit,xy,mods);
          if(!fresh)return 'That handle cannot take a value now - see the message';
          drag=fresh;
          pushUndo();
          var summary=bimGizmoApplyValue(fresh,p.v,false);
          drag=null;
          bimGizmoEndDrag(summary);
          return null;
        }});
    },A3D_GIZ.clickWait);
    return true;
  }
  /* __acad3dV123: THE VALUE BOX -- Rhino's "click the handle and type", Revit's temporary dimension. One
     field beside the cursor, named for what it takes, in the project's unit. submit returns a message
     to show, or null when the value was applied; Escape, a click elsewhere or anything that takes
     the focus closes it with nothing changed. Keys typed in it are the value's: the app's shortcuts
     leave a focused field alone (bimKeyForControl). */
  var A3D_VALBOX=null;
  function bimValueBox(o){
    bimCloseValueBox();
    var host=el.root||document.body;
    var d=document.createElement('div');
    d.id='a3d-valbox';
    d.innerHTML='<label>'+bimEsc(o.label)+'</label><input type="text" spellcheck="false" autocomplete="off" aria-label="'+bimEsc(o.label)+'">'+
      (o.unit?'<span class="u">'+bimEsc(o.unit)+'</span>':'')+
      (o.hint?'<div class="h">'+bimEsc(o.hint)+'</div>':'')+'<div class="e"></div>';
    host.appendChild(d);
    var inp=d.querySelector('input'),er=d.querySelector('.e'),done=false;
    inp.value=(o.value===undefined||o.value===null)?'':String(o.value);
    var vw=window.innerWidth||1200,vh=window.innerHeight||800,w=d.offsetWidth||240,hh=d.offsetHeight||44;
    d.style.left=Math.max(4,Math.min((o.x||0)+14,vw-w-4))+'px';
    d.style.top=Math.max(4,Math.min((o.y||0)+14,vh-hh-4))+'px';
    function close(){
      if(done)return;
      done=true;
      if(d.parentNode)d.parentNode.removeChild(d);
      if(A3D_VALBOX&&A3D_VALBOX.el===d)A3D_VALBOX=null;
      if(o.onClose){try{o.onClose();}catch(eC){console.warn('[BIM] Value box close',eC);}}
      paint();bimSyncStatusHint();
    }
    inp.addEventListener('keydown',function(ev){
      if(ev.key==='Enter'){
        ev.preventDefault();ev.stopPropagation();
        var r;
        try{r=o.submit(inp.value);}
        catch(eV){console.warn('[BIM] The typed value could not be applied',eV);r='That value could not be applied - see the console';}
        if(r){er.textContent=r;inp.select();return;}
        close();
      }else if(ev.key==='Escape'){
        ev.preventDefault();ev.stopPropagation();close();
      }
    });
    inp.addEventListener('blur',function(){setTimeout(close,0);});
    A3D_VALBOX={el:d,close:close,label:o.label,input:inp,err:er};
    inp.focus();
    if(inp.value)inp.setSelectionRange(inp.value.length,inp.value.length);
    return d;
  }
  function bimCloseValueBox(){if(A3D_VALBOX)A3D_VALBOX.close();}
  /* Escape: the objects go back exactly where the press found them, and the gesture is over. */
  function bimGizmoCancelDrag(){
    var d=drag;
    if(!d)return false;
    drag=null;
    bimGizmoTypeClear();
    if(d.pp)return bimPushCancel(d);   /* __acad3dV123 */
    if(d.snap)bimGizmoRestoreObjs(d.ids,d.snap);
    else if(d.start){
      var i;
      for(i=0;i<d.ids.length;i++){
        var o=objById(d.ids[i]);
        if(!o||!d.start[i])continue;
        o.pos=[d.start[i][0],d.start[i][1],d.start[i][2]];
      }
    }
    if(d.gk==='pivot')A3D.gizPivot=d.pivot0;                     /* __acad3dV112 */
    if(d.copies)bimGizmoDropCopies(d.copies);                    /* __acad3dV112 */
    a3dToast('Cancelled');
    refreshTree();refreshProps();paint();saveSoon();
    return true;
  }
  function bimGizmoAxisTo(dist){
    if(!drag||drag.gk!=='axis')return;
    drag.gizDist=dist;
    drag.gizVec=[drag.dir[0]*dist,drag.dir[1]*dist,drag.dir[2]*dist];
    drag.snapAt=null;
    bimGizmoSetPos(drag.gizVec);
    paint();saveSoon();
  }
  function bimGizmoApply(xy){
    if(!drag||!drag.giz)return;
    if(drag.gk==='axis')bimGizmoApplyAxis(xy);
    else if(drag.gk==='plane'||drag.gk==='centre')bimGizmoApplyPlane(xy);
    else if(drag.gk==='pivot')bimGizmoApplyPivot(xy);   /* __acad3dV112 */
    else if(drag.gk==='scale')bimGizmoApplyScale(xy);
    else if(drag.gk==='tilt')bimGizmoApplyTilt(xy);
    paint();saveSoon();
  }
  /* Every move handle ends here: each object's position is its start plus the gesture's TOTAL
     vector, never the previous frame nudged, so a slow drag accumulates no drift. */
  function bimGizmoSetPos(v){
    var i;
    for(i=0;i<drag.ids.length;i++){
      var o=objById(drag.ids[i]);
      if(!o)continue;
      if(!o.pos)o.pos=[0,0,0];
      o.pos[0]=drag.start[i][0]+v[0];
      o.pos[1]=drag.start[i][1]+v[1];
      o.pos[2]=drag.start[i][2]+v[2];
    }
  }
  function bimGizmoApplyAxis(xy){
    var dx=xy[0]-drag.x0,dy=xy[1]-drag.y0;
    // least-squares projection of the cursor delta onto the axis's screen direction, divided by
    // the screen length of one world unit along it -- one formula for all three axes, both
    // projections and any camera
    if(drag.fine){dx*=A3D_GIZ.fine;dy*=A3D_GIZ.fine;}   /* __acad3dV112 */
    var dist=(dx*drag.sx+dy*drag.sy)/drag.len2;
    if(A3D_SNAP.grid&&A3D_SNAP.gridSize>0)
      dist=Math.round(dist/A3D_SNAP.gridSize)*A3D_SNAP.gridSize;
    var v=[drag.dir[0]*dist,drag.dir[1]*dist,drag.dir[2]*dist];
    /* __acad3dV112: a real point beats the grid -- the grid is where nothing else is */
    var sn=bimGizmoSnapVec(v,[drag.dir]);
    drag.snapAt=sn?sn.at:null;
    if(sn){
      v=sn.v;
      dist=v[0]*drag.dir[0]+v[1]*drag.dir[1]+v[2]*drag.dir[2];
    }
    drag.gizDist=dist;
    drag.gizVec=v;
    bimGizmoSetPos(v);
  }
  function bimGizmoApplyPlane(xy){
    var P=bimRayPlane(xy[0],xy[1],drag.O,drag.n,0.05);
    if(!P)return;                        // grazing for this frame: hold the last good position
    var dv=[P[0]-drag.P0[0],P[1]-drag.P0[1],P[2]-drag.P0[2]],v;
    if(drag.fine){dv=[dv[0]*A3D_GIZ.fine,dv[1]*A3D_GIZ.fine,dv[2]*A3D_GIZ.fine];}   /* __acad3dV112 */
    var gs=(A3D_SNAP.grid&&A3D_SNAP.gridSize>0)?A3D_SNAP.gridSize:0;
    if(drag.snapWorld){
      /* the screen plane has no model axes of its own, so the grid rounds the world components */
      if(gs)dv=[Math.round(dv[0]/gs)*gs,Math.round(dv[1]/gs)*gs,Math.round(dv[2]/gs)*gs];
      v=dv;
    }else{
      var da=vdot(dv,drag.a),db=vdot(dv,drag.b);
      if(gs){da=Math.round(da/gs)*gs;db=Math.round(db/gs)*gs;}
      drag.da=da;drag.db=db;
      v=[drag.a[0]*da+drag.b[0]*db,drag.a[1]*da+drag.b[1]*db,drag.a[2]*da+drag.b[2]*db];
    }
    /* __acad3dV112: within the plane, a source point may land on a target point */
    var sn=bimGizmoSnapVec(v,[drag.a,drag.b]);
    drag.snapAt=sn?sn.at:null;
    if(sn){
      v=sn.v;
      drag.da=vdot(v,drag.a);drag.db=vdot(v,drag.b);
    }
    drag.gizVec=v;
    bimGizmoSetPos(v);
  }
  function bimGizmoApplyScale(xy){
    var s;
    if(drag.radial){
      /* __acad3dV111: the triangle has no axis, so the factor is radial: how far the cursor is
         from the gizmo's centre against how far it was when it was pressed. */
      var rx=xy[0]-drag.sox,ry=xy[1]-drag.soy;
      s=Math.sqrt(rx*rx+ry*ry)/drag.L0;
    }else{
      var t=(xy[0]-drag.x0)*drag.ux+(xy[1]-drag.y0)*drag.uy;
      s=(drag.L+t)/drag.L;
    }
    /* ORTHO means clean increments for every gizmo handle -- 15 degrees on the ring and arcs,
       tenths here. A factor never reaches zero or below: that would flatten or mirror. */
    if(A3D_SNAP.ortho)s=Math.round(s*10)/10;
    if(!isFinite(s)||s<0.01)s=A3D_SNAP.ortho?0.1:0.01;
    bimGizmoScaleTo(s);
  }
  function bimGizmoScaleTo(s){
    if(!drag||drag.gk!=='scale')return;
    drag.factor=s;
    bimGizmoRestoreObjs(drag.ids,drag.snap);
    var M=drag.uniform?[s,0,0,0,s,0,0,0,s]:bimGizScaleMat(drag.dir,s);
    var Mplan=[s,0,0,0,1,0,0,0,s],i,failed=0;
    for(i=0;i<drag.ids.length;i++){
      var o=objById(drag.ids[i]);
      if(!o)continue;
      /* an even scale of a sketch is an even scale of its PLAN: it has no height to scale */
      var Mo=(drag.uniform&&bimGizmoKind(o)==='sketch')?Mplan:M;
      if(!bimGizmoXformObj(o,Mo,drag.O))failed++;
    }
    drag.gizFailed=failed;
  }
  function bimGizScaleMat(a,s){
    var k=s-1;
    return [1+k*a[0]*a[0],k*a[0]*a[1],k*a[0]*a[2],
            k*a[1]*a[0],1+k*a[1]*a[1],k*a[1]*a[2],
            k*a[2]*a[0],k*a[2]*a[1],1+k*a[2]*a[2]];
  }
  function bimGizmoApplyTilt(xy){
    var P=bimRayPlane(xy[0],xy[1],drag.O,drag.A,0.05);
    if(!P)return;
    var a=bimGizArcAngle(P,drag.O,drag.B,drag.C);
    if(a===null)return;
    var d=a-drag.a0;
    while(d>Math.PI)d-=Math.PI*2;
    while(d<-Math.PI)d+=Math.PI*2;
    if(drag.fine)d*=A3D_GIZ.fine;                      /* __acad3dV112 */
    if(A3D_SNAP.ortho){
      var step=Math.PI/12;
      d=Math.round(d/step)*step;
    }
    bimGizmoTiltTo(d);
  }
  function bimGizmoTiltTo(d){
    if(!drag||drag.gk!=='tilt')return;
    drag.tiltAngle=d;
    bimGizmoRestoreObjs(drag.ids,drag.snap);
    var M=bimGizRotMat(drag.A,d),i,failed=0;
    for(i=0;i<drag.ids.length;i++){
      var o=objById(drag.ids[i]);
      if(!o)continue;
      if(!bimGizmoXformObj(o,M,drag.O))failed++;
    }
    drag.gizFailed=failed;
  }
  /* Rodrigues: a right-handed turn of t radians about the unit axis A, as a row-major 3x3. */
  function bimGizRotMat(A,t){
    var c=Math.cos(t),s=Math.sin(t),k=1-c,x=A[0],y=A[1],z=A[2];
    return [c+x*x*k,   x*y*k-z*s, x*z*k+y*s,
            y*x*k+z*s, c+y*y*k,   y*z*k-x*s,
            z*x*k-y*s, z*y*k+x*s, c+z*z*k];
  }
  /* __acad3dV110: a 3D linear map M (row-major 3x3) about the world point O. A generic solid's
     mesh is transformed in WORLD space and stored back in its own frame: it sits at o.pos, and
     transforming local vertices about a world point is the mistake the plan dispatcher made. A
     primitive has no mesh of its own to transform, so it becomes a plain solid first. A sketch is
     plan geometry, so only a map that keeps it in its plane is accepted -- the handles offer a
     sketch nothing else, and anything else is refused rather than half-applied. */
  function bimGizmoXformObj(o,M,O){
    var k=bimGizmoKind(o),q=bimObjOffset(o),i;
    if(k==='solid'){
      var base=o.mesh||bimPrimitiveMesh(o),prim=!o.mesh;
      if(!base||!base.v)return false;
      var nv=[];
      for(i=0;i<base.v.length;i++){
        var v=base.v[i],wx=v[0]+q[0]-O[0],wy=v[1]+q[1]-O[1],wz=v[2]+q[2]-O[2];
        nv.push([O[0]+M[0]*wx+M[1]*wy+M[2]*wz-q[0],
                 O[1]+M[3]*wx+M[4]*wy+M[5]*wz-q[1],
                 O[2]+M[6]*wx+M[7]*wy+M[8]*wz-q[2]]);
      }
      var nm={v:nv,f:base.f.map(function(fc){return fc.slice();})};
      if(prim)bimMaterializeInto(o,nm);else o.mesh=nm;
      return true;
    }
    if(k==='sketch'){
      if(Math.abs(M[1])>1e-9||Math.abs(M[3])>1e-9||Math.abs(M[4]-1)>1e-9||
         Math.abs(M[5])>1e-9||Math.abs(M[7])>1e-9){
        console.warn('[BIM] '+o.name+': a sketch can only be transformed within its own plane.');
        return false;
      }
      o.pts=o.pts.map(function(p){
        var wx=p[0]+q[0]-O[0],wz=p[1]+q[2]-O[2];
        return [O[0]+M[0]*wx+M[2]*wz-q[0],O[2]+M[6]*wx+M[8]*wz-q[2]];
      });
      return true;
    }
    console.warn('[BIM] '+o.name+' cannot be scaled or tilted by the gizmo.');
    return false;
  }
  /* __acad3dV110: the gizmo's menu -- a right-click on any of its handles, or the GIZMO command.
     Align to World, Local or View, and Hide: the reference tools' set. Session state only: an
     alignment is a way of looking at the selection, not part of the model. */
  var A3D_GIZ_ALIGN=[['world','Align to World'],['local','Align to Local'],['view','Align to View']];
  function bimOpenGizmoMenu(cx,cy){
    bimCloseGizmoMenu();
    var host=el.root||document.body;
    var asked=A3D.gizAlign||'world',i,h='<div class="a3d-gizmenu-hd">Gizmo</div>';
    for(i=0;i<A3D_GIZ_ALIGN.length;i++)
      h+='<button type="button" data-a3dgiz="'+A3D_GIZ_ALIGN[i][0]+'"'+
         (A3D_GIZ_ALIGN[i][0]===asked?' class="on"':'')+'>'+A3D_GIZ_ALIGN[i][1]+'</button>';
    if(A3D.gizPivot)h+='<button type="button" data-a3dgiz="pivot">Reset Pivot</button>';   /* __acad3dV112 */
    h+='<div class="a3d-gizmenu-sep"></div>'+(A3D.gizHidden?
      '<button type="button" data-a3dgiz="show">Show Gizmo</button>':
      '<button type="button" data-a3dgiz="hide">Hide Gizmo</button>');
    var m=document.createElement('div');
    m.id='a3d-gizmenu';
    m.innerHTML=h;
    host.appendChild(m);
    var mw=m.offsetWidth||180,mh=m.offsetHeight||150;
    var vw=window.innerWidth||1200,vh=window.innerHeight||800;
    m.style.left=Math.max(4,Math.min(cx,vw-mw-4))+'px';
    m.style.top=Math.max(4,Math.min(cy,vh-mh-4))+'px';
    m.addEventListener('click',function(ev){
      var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dgiz]'):null;
      if(!b)return;
      ev.stopPropagation();
      bimGizmoMenuAct(b.getAttribute('data-a3dgiz'));
    });
    return m;
  }
  function bimCloseGizmoMenu(){
    var m=document.getElementById('a3d-gizmenu');
    if(m&&m.parentNode)m.parentNode.removeChild(m);
  }
  function bimGizmoMenuAct(act){
    bimCloseGizmoMenu();
    if(act==='world'||act==='local'||act==='view'){
      A3D.gizAlign=act;
      A3D.gizHidden=false;
      var ids=bimGizmoIds(),fr=bimGizmoFrame(ids);
      if(act==='local'&&fr.fallback)
        a3dToast('Align to Local: '+(ids.length===1?(objById(ids[0]).name+' stores no orientation of its own'):
          'Local needs one wall or one column selected')+' - the gizmo stays aligned to World until it does');
      else a3dToast('Gizmo aligned to '+act.charAt(0).toUpperCase()+act.slice(1));
    }else if(act==='pivot'){                                     /* __acad3dV112 */
      A3D.gizPivot=null;
      a3dToast('Pivot back at the middle of the selection');
    }else if(act==='hide'){
      A3D.gizHidden=true;
      a3dToast('Gizmo hidden - type GIZMO to show it again');
    }else if(act==='show'){
      A3D.gizHidden=false;
      a3dToast('Gizmo shown');
    }else return;
    paint();
  }
  /* GIZMO: shows a hidden gizmo; otherwise opens the menu beside it (or mid-canvas with nothing
     selected, so the alignment can be chosen before the selection). */
  function bimGizmoCommand(){
    if(A3D.gizHidden){
      A3D.gizHidden=false;
      paint();
      a3dToast('Gizmo shown - right-click any of its handles for the gizmo menu');
      return;
    }
    paint();
    var g=A3D.gizmo,r=el.cv?el.cv.getBoundingClientRect():null;
    var cx=r?(g?r.left+g.ox+12:r.left+r.width/2):200,cy=r?(g?r.top+g.oy+12:r.top+r.height/2):200;
    bimOpenGizmoMenu(cx,cy);
  }
