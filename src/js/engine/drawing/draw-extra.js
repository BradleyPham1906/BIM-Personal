import { A3D, el } from '../core/state.js';
import { bimObjOffset } from './plan-mode-sketch.js';
import { addSketchObj } from './command-ending.js';
import { bimPolySignedArea } from '../bim/rooms.js';
import { bimCircleFrom3Points } from '../annotation/dimensions.js';
import { bimLayerShown } from '../layers/layer-rules.js';
import { paint } from '../map/terrain-3d.js';
import { bimFmtLen } from '../gizmo/gizmo-handles.js';
import { BIM_BULGE_EPS, bimBulgeAt } from './arc-storage.js';
import { bimCircleSketch } from './curve-walking.js';
import { closeDlg } from '../ui/touch-input.js';
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
    if(sk.tool==='circlettr'){bimTTRPoint(sk,p);return;}   /* __acad3dV265 */
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
  function bimIsDrawExtra(sk){return !!sk&&(sk.tool==='circle2p'||sk.tool==='circle3p'||sk.tool==='ellipse'||sk.tool==='revcloud'||sk.tool==='circlettr');}
  /* ================= __acad3dV265: CIRCLE TTR (tangent, tangent, radius) =================
     Two lines picked, then a radius: the circle tangent to both, on the sides the picks were made on, as AutoCAD
     chooses it (the pick points say which of the four corners the lines make). Each line is moved by the radius
     toward its pick's side of the other line's crossing, and the two moved lines meet at the centre. */
  function bimLineSide(a,b,p){return ((b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0]))>=0?1:-1;}
  function bimCircleTTR(l1,l2,p1,p2,r){
    if(!(r>0))return null;
    function off(l,s){var dx=l[1][0]-l[0][0],dz=l[1][1]-l[0][1],L=Math.sqrt(dx*dx+dz*dz);if(L<1e-12)return null;
      var nx=-dz/L*s*r,nz=dx/L*s*r;return [[l[0][0]+nx,l[0][1]+nz],[l[1][0]+nx,l[1][1]+nz]];}
    /* each circle centre lies on the side of line 1 where pick 2 is, and on the side of line 2 where pick 1 is */
    var a=off(l1,bimLineSide(l1[0],l1[1],p2)),b=off(l2,bimLineSide(l2[0],l2[1],p1));
    if(!a||!b)return null;
    var r1=[a[1][0]-a[0][0],a[1][1]-a[0][1]],r2=[b[1][0]-b[0][0],b[1][1]-b[0][1]],den=r1[0]*r2[1]-r1[1]*r2[0];
    if(Math.abs(den)<1e-12)return null;   /* parallel lines: no single circle */
    var t=((b[0][0]-a[0][0])*r2[1]-(b[0][1]-a[0][1])*r2[0])/den;
    return {center:[a[0][0]+r1[0]*t,a[0][1]+r1[1]*t],radius:r};
  }
  /* The straight segment of a sketch nearest a plan point, in world coordinates. */
  function bimNearestSegment(p,y){
    var best=null,bd=Infinity,i,j,o,q;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(o.t!=='sketch'||!o.pts||o.pts.length<2||!bimLayerShown(o))continue;
      q=bimObjOffset(o);
      if(Math.abs((o.y||0)+q[1]-y)>0.05)continue;
      var n=o.pts.length,segs=o.closed!==false&&n>2?n:n-1;
      for(j=0;j<segs;j++){
        if(Math.abs(bimBulgeAt(o.bulges,j))>BIM_BULGE_EPS)continue;
        var a=[o.pts[j][0]+q[0],o.pts[j][1]+q[2]],b=[o.pts[(j+1)%n][0]+q[0],o.pts[(j+1)%n][1]+q[2]];
        var dx=b[0]-a[0],dz=b[1]-a[1],L2=dx*dx+dz*dz,t=L2?Math.max(0,Math.min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dz)/L2)):0;
        var d=Math.sqrt(Math.pow(a[0]+dx*t-p[0],2)+Math.pow(a[1]+dz*t-p[1],2));
        if(d<bd){bd=d;best=[a,b];}
      }
    }
    return best;
  }
  function bimTTRPoint(sk,p){
    var seg=bimNearestSegment(p,sk.y);
    if(!seg){a3dToast('CIRCLE TTR: pick a straight line');return;}
    sk.ttr=(sk.ttr||[]).concat([{seg:seg,p:[p[0],p[1]]}]);
    if(sk.ttr.length<2){a3dToast('CIRCLE TTR: pick the second line');paint();return;}
    var A=sk.ttr[0],B=sk.ttr[1];
    A3D.sk=null;paint();
    bimTTRDlg(A,B,sk.y);
  }
  function bimTTRDlg(A,B,y){
    closeDlg();
    var d=document.createElement('div');
    d.className='a3d-dlg';
    d.innerHTML='<div class="a3d-dlghd">Circle: tangent, tangent, radius</div><div class="a3d-dlgbody">'+
      '<div class="a3d-dlgrow"><label>Radius, m</label><input type="number" min="0" step="any" data-a3dttr="r" value="1"></div>'+
      '<div id="a3d-dlgerr" class="a3d-dlgerr"></div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="ok">OK</button></div>';
    el.root.appendChild(d);el.dlg=d;
    function submit(){
      var r=parseFloat(d.querySelector('[data-a3dttr="r"]').value),c=bimCircleTTR(A.seg,B.seg,A.p,B.p,r);
      if(!c){d.querySelector('#a3d-dlgerr').textContent=r>0?'Those lines are parallel: no circle touches both there':'The radius must be more than zero';return;}
      closeDlg();
      var cs=bimCircleSketch(c.center,c.radius);
      A3D.sk={tool:'circle',pts:[],y:y,on:null};
      addSketchObj(cs.pts,{bulges:cs.bulges,toast:'Circle tangent to both lines, radius '+bimFmtLen(r)});
    }
    d.addEventListener('click',function(ev){var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;if(!b)return;if(b.getAttribute('data-a3dlg')==='ok')submit();else closeDlg();});
    d.addEventListener('keydown',function(ev){if(ev.key==='Enter'){ev.preventDefault();ev.stopPropagation();submit();}else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();}ev.stopPropagation();});
  }
export { bimDrawExtraPoint, bimIsDrawExtra };
