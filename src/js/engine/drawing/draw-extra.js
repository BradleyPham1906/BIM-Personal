import { addSketchObj } from './command-ending.js';
import { bimPolySignedArea } from '../bim/rooms.js';
import { bimCircleFrom3Points } from '../annotation/dimensions.js';
import { paint } from '../map/terrain-3d.js';
import { bimFmtLen } from '../gizmo/gizmo-handles.js';
import { bimCircleSketch } from './curve-walking.js';
import { a3dToast } from '../bim/csg-booleans.js';

  /* ================= __acad3dV253: AutoCAD's other draw commands (D3) =================
     CIRCLE's 2P and 3P forms, ELLIPSE (EL) by its axis endpoints and the other half-axis, and REVCLOUD's rectangular
     form. A circle is two half-circle arcs as CIRCLE makes it; a revision cloud is arcs along its outline, bulging
     outward; an ellipse has no arc form in a polyline, so it is stored as 72 points on it, as an imported ELLIPSE is.
     The geometry is pure (bimCircle2P, bimEllipseFromAxis, bimRevcloudRect), tested without a canvas. */
  var BIM_REVCLOUD={arc:0.5};   /* the arc length as a fraction of a metre: AutoCAD's default arc length is in drawing units */
  function bimCircle2P(a,b){
    var c=[(a[0]+b[0])/2,(a[1]+b[1])/2],r=Math.sqrt(Math.pow(b[0]-a[0],2)+Math.pow(b[1]-a[1],2))/2;
    return r>1e-9?{center:c,radius:r}:null;
  }
  /* The ellipse whose major axis runs from a to b, with the other half-axis d long. */
  function bimEllipseFromAxis(a,b,d,n){
    var c=[(a[0]+b[0])/2,(a[1]+b[1])/2],ax=(b[0]-a[0])/2,az=(b[1]-a[1])/2,A=Math.sqrt(ax*ax+az*az),k,out=[];
    if(!(A>1e-9)||!(d>1e-9))return null;
    var ux=ax/A,uz=az/A;
    n=n||72;
    for(k=0;k<n;k++){
      var t=k/n*Math.PI*2,x=Math.cos(t)*A,y=Math.sin(t)*d;
      out.push([c[0]+x*ux-y*uz,c[1]+x*uz+y*ux]);
    }
    return {pts:out,center:c,a:A,b:d};
  }
  /* The distance of p from the line through a and b: the other half-axis the third click gives. */
  function bimDistToLine(p,a,b){
    var dx=b[0]-a[0],dz=b[1]-a[1],L=Math.sqrt(dx*dx+dz*dz);
    return L>0?Math.abs((p[0]-a[0])*dz-(p[1]-a[1])*dx)/L:0;
  }
  /* A rectangle's outline split into arcs about len long, each bulging outward. */
  function bimRevcloudRect(a,b,len){
    var x0=Math.min(a[0],b[0]),x1=Math.max(a[0],b[0]),z0=Math.min(a[1],b[1]),z1=Math.max(a[1],b[1]);
    if(x1-x0<1e-9||z1-z0<1e-9)return null;
    len=len>0?len:BIM_REVCLOUD.arc;
    var corners=[[x0,z0],[x1,z0],[x1,z1],[x0,z1]],pts=[],i,k;
    for(i=0;i<4;i++){
      var p=corners[i],q=corners[(i+1)%4],L=Math.sqrt(Math.pow(q[0]-p[0],2)+Math.pow(q[1]-p[1],2)),n=Math.max(1,Math.round(L/len));
      for(k=0;k<n;k++)pts.push([p[0]+(q[0]-p[0])*k/n,p[1]+(q[1]-p[1])*k/n]);
    }
    /* a positive bulge bows to the right of the direction of travel (arc-storage.js); round a polygon of positive
       signed area the outside is on the right */
    var s=bimPolySignedArea(pts)>0?0.5:-0.5;
    return {pts:pts,bulges:pts.map(function(){return s;})};
  }
  /* The clicks of the four tools, from skPlacePoint. */
  function bimDrawExtraPoint(sk,p){
    sk.pts.push([p[0],p[1]]);
    var n=sk.pts.length,r,c;
    if(sk.tool==='circle2p'){
      if(n<2){a3dToast('Circle 2P: specify the second end of the diameter');paint();return;}
      r=bimCircle2P(sk.pts[0],sk.pts[1]);
      if(!r){sk.pts=[];a3dToast('Circle 2P: the two points are the same');paint();return;}
      c=bimCircleSketch(r.center,r.radius);
      addSketchObj(c.pts,{bulges:c.bulges,toast:'Circle created, radius '+bimFmtLen(r.radius)});
    }else if(sk.tool==='circle3p'){
      if(n<3){a3dToast('Circle 3P: specify the '+(n===1?'second':'third')+' point on the circle');paint();return;}
      r=bimCircleFrom3Points(sk.pts[0],sk.pts[1],sk.pts[2]);
      if(!r||!(r.radius>1e-9)||!isFinite(r.radius)){sk.pts=[];a3dToast('Circle 3P: three points in a line make no circle');paint();return;}
      c=bimCircleSketch(r.center,r.radius);
      addSketchObj(c.pts,{bulges:c.bulges,toast:'Circle created, radius '+bimFmtLen(r.radius)});
    }else if(sk.tool==='ellipse'){
      if(n<2){a3dToast('Ellipse: specify the other endpoint of the axis');paint();return;}
      if(n<3){a3dToast('Ellipse: specify the distance to the other axis');paint();return;}
      r=bimEllipseFromAxis(sk.pts[0],sk.pts[1],bimDistToLine(sk.pts[2],sk.pts[0],sk.pts[1]));
      if(!r){sk.pts=[];a3dToast('Ellipse: the axes must have length');paint();return;}
      addSketchObj(r.pts,{toast:'Ellipse created, axes '+bimFmtLen(2*r.a)+' by '+bimFmtLen(2*r.b)});
    }else if(sk.tool==='revcloud'){
      if(n<2){a3dToast('Revision cloud: specify the opposite corner');paint();return;}
      r=bimRevcloudRect(sk.pts[0],sk.pts[1],BIM_REVCLOUD.arc);
      if(!r){sk.pts=[];a3dToast('Revision cloud: drag out a rectangle');paint();return;}
      addSketchObj(r.pts,{bulges:r.bulges,toast:'Revision cloud created'});
    }
  }
  function bimIsDrawExtra(sk){return !!sk&&(sk.tool==='circle2p'||sk.tool==='circle3p'||sk.tool==='ellipse'||sk.tool==='revcloud');}
export { bimDrawExtraPoint, bimIsDrawExtra };
