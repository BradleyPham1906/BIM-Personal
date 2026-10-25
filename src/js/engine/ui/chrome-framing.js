  /* ================= __acad3dV79: framing that respects the floating chrome =================

     Selectors for every overlay that floats OVER the drawing area. Measured live: an element that
     is absent, hidden or collapsed contributes nothing, so one list is correct in every workspace
     and at every window size without a per-layout branch. The left navigator and the right
     inspector are NOT here -- they are laid out beside the canvas, not over it, so the canvas
     rectangle already excludes them. */
  var A3D_CHROME_SEL=['#a3d-dock .a3d-dockbody','#a3d-navgrp','#a3d-snapgrp','.a3d-touchlen'];   /* __acad3dV109 */
  function bimChromeRects(){
    var out=[],i,e,r;
    for(i=0;i<A3D_CHROME_SEL.length;i++){
      e=document.querySelector(A3D_CHROME_SEL[i]);
      if(!e)continue;
      var st=window.getComputedStyle(e);
      if(st.display==='none'||st.visibility==='hidden'||parseFloat(st.opacity||'1')<0.05)continue;
      r=e.getBoundingClientRect();
      if(r.width<1||r.height<1)continue;
      out.push({sel:A3D_CHROME_SEL[i],left:r.left,top:r.top,right:r.right,bottom:r.bottom});
    }
    return out;
  }
  /* The part of the canvas a handle can actually be clicked in, in CANVAS coordinates.

     Each overlapping overlay is turned into an inset on the SIDE it hugs -- the side whose edge it
     is nearest. That is deliberate rather than clever: an overlay floating in the middle of the
     drawing would otherwise eat the whole viewport, and none of this app's chrome does that. The
     list holds only overlays that MEASURABLY sit over the canvas AND accept pointer events: the
     status bar is below the canvas, not over it, and the dock's own container is already
     pointer-events:none -- it is the rounded body inside it that blocks. An
     overlay that would consume more than 40% of a dimension is ignored, so a mis-measured or
     mis-placed panel degrades to "frame as before" rather than to an unusable sliver. */
  function bimSafeViewRect(){
    var W=cvW(),H=cvH();
    var full={x:0,y:0,w:W,h:H,insets:{top:0,right:0,bottom:0,left:0}};
    if(!el.cv||W<1||H<1)return full;
    var cr=el.cv.getBoundingClientRect();
    var rects=bimChromeRects(),i;
    var ins={top:0,right:0,bottom:0,left:0};
    for(i=0;i<rects.length;i++){
      var r=rects[i];
      var l=r.left-cr.left,t=r.top-cr.top,rt=r.right-cr.left,b=r.bottom-cr.top;
      if(rt<=0||l>=W||b<=0||t>=H)continue;                  // does not overlap the canvas at all
      var dTop=t,dBottom=H-b,dLeft=l,dRight=W-rt;
      var m=Math.min(dTop,dBottom,dLeft,dRight);
      if(m===dBottom)      ins.bottom=Math.max(ins.bottom,H-t);
      else if(m===dTop)    ins.top=Math.max(ins.top,b);
      else if(m===dLeft)   ins.left=Math.max(ins.left,rt);
      else                 ins.right=Math.max(ins.right,W-l);
    }
    if(ins.top+ins.bottom>H*0.4||ins.left+ins.right>W*0.4){
      console.warn('[BIM] Floating chrome would cover more than 40% of the viewport; framing '+
                   'against the full canvas instead.');
      return full;
    }
    return {x:ins.left,y:ins.top,w:W-ins.left-ins.right,h:H-ins.top-ins.bottom,insets:ins};
  }
  /* Point the camera so that world point P projects to the CENTRE OF THE SAFE RECT rather than the
     centre of the canvas, and pull back enough that a model sized for the canvas still fits the
     safe rectangle.

     The offset is the inverse of toScreen at the target's own depth, with toScreen's flat-mode
     branch mirrored -- not the pan handler's empirical 0.0018 factor, which is tuned for feel and
     would only be approximately right here. A point at the camera target projects to the canvas
     centre; a point at target + (r*a + u*b) projects a*f and b*f pixels away from it. Solving that
     for the offset we want is the whole of this function. */
  function bimAimAtSafeCentre(c,P){
    var W=cvW(),H=cvH();
    if(W<1||H<1){c.tx=P[0];c.ty=P[1];c.tz=P[2];return {w:1,h:1};}
    var s=bimSafeViewRect();
    if(s.w<40||s.h<40){c.tx=P[0];c.ty=P[1];c.tz=P[2];return s;}
    c.dist*=Math.max(1,Math.max(W/s.w,H/s.h));
    var V=camVecs(c);
    var sx=s.x+s.w/2,sy=s.y+s.h/2;
    var a,b;
    if(A3D.flat){
      var k=H*1.2/Math.max(c.dist,0.5);
      a=(sx-W/2)/k;b=(H/2-sy)/k;
    }else{
      var f=H*1.2;
      a=(sx-W/2)/f*c.dist;b=(H/2-sy)/f*c.dist;
    }
    c.tx=P[0]-(V.r[0]*a+V.u[0]*b);
    c.ty=P[1]-(V.r[1]*a+V.u[1]*b);
    c.tz=P[2]-(V.r[2]*a+V.u[2]*b);
    return s;
  }
  /* The world bounding box of a set of objects, or of everything. One place, so fitScene and
     Zoom to Selection cannot disagree about what a bounding box is. */
  function bimWorldBounds(ids){
    var mn=[1e9,1e9,1e9],mx=[-1e9,-1e9,-1e9],any=false,i,j,k;
    var list=ids?ids.map(objById).filter(Boolean):A3D.objs;
    for(i=0;i<list.length;i++){
      var o=list[i],m=meshOf(o),q=bimObjOffset(o);
      if(!ids&&bimObjLayerState(o).frozen)continue;   /* __acad3dV121 */
      if(m&&m.v&&m.v.length){
        for(j=0;j<m.v.length;j++)for(k=0;k<3;k++){
          var vv=m.v[j][k]+q[k];
          if(vv<mn[k])mn[k]=vv;
          if(vv>mx[k])mx[k]=vv;
          any=true;
        }
      }else if(o.t==='terrain'&&o.survey&&o.survey.length){   /* __acad3dV108: survey points are [x, z, y] */
        for(j=0;j<o.survey.length;j++){
          var tv=[o.survey[j][0]+q[0],o.survey[j][2]+q[1],o.survey[j][1]+q[2]];
          for(k=0;k<3;k++){if(tv[k]<mn[k])mn[k]=tv[k];if(tv[k]>mx[k])mx[k]=tv[k];}
        }
        any=true;
      }else if(bimIsDiag(o)){   /* __acad3dV164: a diagram's points, labels and symbols */
        var dgb=bimDgBounds(o);
        for(j=0;j<dgb.length;j++)for(k=0;k<3;k++){if(dgb[j][k]<mn[k])mn[k]=dgb[j][k];if(dgb[j][k]>mx[k])mx[k]=dgb[j][k];any=true;}
      }else if(o.pts&&o.pts.length){
        /* Sketches and rooms have no mesh. Before V79 fitScene skipped them outright, so a
           drawing made only of sketches fit to nothing at all. */
        for(j=0;j<o.pts.length;j++){
          var wp=bimWorldPt(o,o.pts[j],o.y);
          for(k=0;k<3;k++){
            if(wp[k]<mn[k])mn[k]=wp[k];
            if(wp[k]>mx[k])mx[k]=wp[k];
          }
          any=true;
        }
      }else if(bimIsAlignment(o)){   /* __acad3dV127 */
        var aep=bimAlignExtentPts(o);
        for(j=0;j<aep.length;j++){
          var awp=bimWorldPt(o,aep[j],o.y||0);
          for(k=0;k<3;k++){if(awp[k]<mn[k])mn[k]=awp[k];if(awp[k]>mx[k])mx[k]=awp[k];}
          any=true;
        }
      }else if(bimIsProperty(o)||((o.t==='text'||o.t==='roomtag')&&o.pt)){
        /* __acad3dV103: derived corners (property) or one insertion point (text, tag) */
        var extra=bimIsProperty(o)?bimPropertyGeometry(o).ring.map(function(p){return [p[0],(o.y||0)+q[1],p[1]];})
                                  :[bimWorldPt(o,o.pt,o.y||0)];
        for(j=0;j<extra.length;j++){
          for(k=0;k<3;k++){
            if(extra[j][k]<mn[k])mn[k]=extra[j][k];
            if(extra[j][k]>mx[k])mx[k]=extra[j][k];
          }
          any=true;
        }
      }
    }
    return any?{mn:mn,mx:mx}:null;
  }
  function bimFrameBounds(bb){
    var c=A3D.cam;
    var P=[(bb.mn[0]+bb.mx[0])/2,(bb.mn[1]+bb.mx[1])/2,(bb.mn[2]+bb.mx[2])/2];
    var sz=Math.max(bb.mx[0]-bb.mn[0],bb.mx[1]-bb.mn[1],bb.mx[2]-bb.mn[2])+3.2;
    c.dist=Math.max(14,sz*1.6);
    bimAimAtSafeCentre(c,P);
    A3D.view='Custom';
    refreshHud();paint();saveSoon();
  }
  /* Revit's ZS. The direct answer to "the handles I need are behind the tool dock": it frames the
     selection into the rectangle those handles can be clicked in. */
  function bimZoomToSelection(){
    var ids=(A3D.selSet&&A3D.selSet.length)?A3D.selSet.slice():(A3D.sel?[A3D.sel]:[]);
    if(!ids.length){a3dToast('Select something first, then Zoom to Selection');return false;}
    var bb=bimWorldBounds(ids);
    if(!bb){a3dToast('That selection has no geometry to zoom to');return false;}
    bimFrameBounds(bb);
    return true;
  }
