import { A3D, el } from '../core/state.js';
import { bimObjOffset } from './plan-mode-sketch.js';
import { bimLayerShown } from '../layers/layer-rules.js';
import { paint } from '../map/terrain-3d.js';
import { bimBulgeArc, bimBulgeAt } from './arc-storage.js';
import { closeDlg } from '../ui/touch-input.js';
import { a3dToast } from '../bim/csg-booleans.js';

  /* ================= __acad3dV249: object snaps and polar tracking (D1) =================
     AutoCAD's running object snaps, by its names: ENDpoint, MIDpoint, CENter, QUAdrant,
     INTersection, PERpendicular, TANgent, NEArest, NODe. Before this only vertices, grid nodes
     and construction-line crossings snapped (bimSnapCandidates), which is ENDpoint alone.

     Everything is worked out on PRIMITIVES in world plan coordinates [x,z]: a line {k:'L',a,b}
     or an arc {k:'A',c,r,a1,sw} (a1 the start angle, sw the signed sweep), which is exactly what
     a sketch's pts and bulges describe (a circle is two bulge-1 arcs). The pure functions below
     take primitives and a cursor, so they are tested without a canvas; bimOsnapModelPrims()
     reads the model the same way bimSnapCandidates() does.

     Choosing: every candidate within the pick tolerance of the cursor competes on distance;
     NEArest only wins when nothing else is in range, as in AutoCAD, or it would hide every
     other snap on the line under the cursor. */
  var A3D_OSNAP={end:true,mid:true,cen:true,qua:true,int:true,per:true,tan:false,nea:false,node:true,
    polar:false,polarInc:45,polarTolDeg:3,lastKind:'',polarAngle:null};
  var BIM_OSNAP_KINDS=['end','mid','cen','node','qua','int','per','tan','nea'];
  var BIM_OSNAP_NAMES={end:'Endpoint',mid:'Midpoint',cen:'Center',node:'Node',qua:'Quadrant',
    int:'Intersection',per:'Perpendicular',tan:'Tangent',nea:'Nearest'};
  function bimOsnapAngIn(a,a1,sw){
    /* is angle a on the arc that starts at a1 and sweeps sw (either sign)? */
    var t=sw>=0?a-a1:a1-a,TWO=Math.PI*2;
    t=((t%TWO)+TWO)%TWO;
    return t<=Math.abs(sw)+1e-9;
  }
  function bimOsnapArcPt(A,ang){return [A.c[0]+Math.cos(ang)*A.r,A.c[1]+Math.sin(ang)*A.r];}
  /* A polyline (pts, bulges, closed) as primitives, offset by off=[dx,dz]. */
  function bimOsnapPolyPrims(pts,bulges,closed,off){
    var out=[],n=pts?pts.length:0,i,ox=off?off[0]:0,oz=off?off[1]:0;
    if(n<2)return out;
    var segs=closed?n:n-1;
    for(i=0;i<segs;i++){
      var p=[pts[i][0]+ox,pts[i][1]+oz],q=[pts[(i+1)%n][0]+ox,pts[(i+1)%n][1]+oz];
      var arc=bimBulgeArc(p,q,bimBulgeAt(bulges,i));
      if(arc)out.push({k:'A',c:arc.center,r:arc.radius,a1:arc.a1,sw:arc.sweep,p:p,q:q});
      else if(Math.abs(p[0]-q[0])+Math.abs(p[1]-q[1])>1e-12)out.push({k:'L',a:p,b:q});
    }
    /* A closed run of arcs on one centre is a CIRCLE: AutoCAD gives a circle no endpoints and no
       midpoint, only its centre and quadrants, and the joins of its two halves sit on quadrants. */
    if(closed&&out.length&&out.every(function(P){return P.k==='A'&&Math.abs(P.r-out[0].r)<1e-9&&
       Math.abs(P.c[0]-out[0].c[0])<1e-9&&Math.abs(P.c[1]-out[0].c[1])<1e-9;}))
      for(i=0;i<out.length;i++)out[i].circle=true;
    return out;
  }
  /* Distance from point c to a primitive, and the nearest point on it. */
  function bimOsnapNearest(P,c){
    if(P.k==='L'){
      var dx=P.b[0]-P.a[0],dz=P.b[1]-P.a[1],L2=dx*dx+dz*dz;
      var t=L2>0?((c[0]-P.a[0])*dx+(c[1]-P.a[1])*dz)/L2:0;
      t=Math.max(0,Math.min(1,t));
      var q=[P.a[0]+dx*t,P.a[1]+dz*t];
      return {p:q,d:Math.sqrt((c[0]-q[0])*(c[0]-q[0])+(c[1]-q[1])*(c[1]-q[1]))};
    }
    var ang=Math.atan2(c[1]-P.c[1],c[0]-P.c[0]),best;
    if(bimOsnapAngIn(ang,P.a1,P.sw))best=bimOsnapArcPt(P,ang);
    else{
      var e1=bimOsnapArcPt(P,P.a1),e2=bimOsnapArcPt(P,P.a1+P.sw);
      best=(Math.pow(c[0]-e1[0],2)+Math.pow(c[1]-e1[1],2)<=Math.pow(c[0]-e2[0],2)+Math.pow(c[1]-e2[1],2))?e1:e2;
    }
    return {p:best,d:Math.sqrt(Math.pow(c[0]-best[0],2)+Math.pow(c[1]-best[1],2))};
  }
  /* Where two primitives cross (0, 1 or 2 points), each kept only if it lies on both. */
  function bimOsnapIntersect(P,Q){
    if(P.k==='A'&&Q.k==='L')return bimOsnapIntersect(Q,P);
    var out=[],i;
    if(P.k==='L'&&Q.k==='L'){
      var r=[P.b[0]-P.a[0],P.b[1]-P.a[1]],s=[Q.b[0]-Q.a[0],Q.b[1]-Q.a[1]];
      var den=r[0]*s[1]-r[1]*s[0];
      if(Math.abs(den)<1e-12)return out;
      var w=[Q.a[0]-P.a[0],Q.a[1]-P.a[1]];
      var t=(w[0]*s[1]-w[1]*s[0])/den,u=(w[0]*r[1]-w[1]*r[0])/den;
      if(t>=-1e-9&&t<=1+1e-9&&u>=-1e-9&&u<=1+1e-9)out.push([P.a[0]+r[0]*t,P.a[1]+r[1]*t]);
      return out;
    }
    var hits=[];
    if(P.k==='L'){   /* line against the arc's circle */
      var d=[P.b[0]-P.a[0],P.b[1]-P.a[1]],f=[P.a[0]-Q.c[0],P.a[1]-Q.c[1]];
      var A=d[0]*d[0]+d[1]*d[1],B=2*(f[0]*d[0]+f[1]*d[1]),C=f[0]*f[0]+f[1]*f[1]-Q.r*Q.r;
      var disc=B*B-4*A*C;
      if(A<1e-18||disc<-1e-12)return out;
      disc=Math.sqrt(Math.max(0,disc));
      var ts=disc<1e-12?[-B/(2*A)]:[(-B-disc)/(2*A),(-B+disc)/(2*A)];
      for(i=0;i<ts.length;i++)if(ts[i]>=-1e-9&&ts[i]<=1+1e-9)hits.push([P.a[0]+d[0]*ts[i],P.a[1]+d[1]*ts[i]]);
    }else{           /* circle against circle */
      var dx=Q.c[0]-P.c[0],dz=Q.c[1]-P.c[1],D=Math.sqrt(dx*dx+dz*dz);
      if(D<1e-12||D>P.r+Q.r+1e-9||D<Math.abs(P.r-Q.r)-1e-9)return out;
      var a=(P.r*P.r-Q.r*Q.r+D*D)/(2*D),h=Math.sqrt(Math.max(0,P.r*P.r-a*a));
      var mx=P.c[0]+dx*a/D,mz=P.c[1]+dz*a/D;
      hits.push([mx+h*dz/D,mz-h*dx/D]);
      if(h>1e-12)hits.push([mx-h*dz/D,mz+h*dx/D]);
    }
    for(i=0;i<hits.length;i++){
      var ok=true,arcs=[P,Q],j;
      for(j=0;j<2;j++){
        var R=arcs[j];
        if(R.k==='A'&&!bimOsnapAngIn(Math.atan2(hits[i][1]-R.c[1],hits[i][0]-R.c[0]),R.a1,R.sw))ok=false;
      }
      if(ok)out.push(hits[i]);
    }
    return out;
  }
  /* The candidates near the cursor c, within tol (world units). last is the previous point of
     the command (or null), which PERpendicular and TANgent are measured from. nodes are point
     objects ([x,z]); modes defaults to A3D_OSNAP. */
  function bimOsnapCandidates(prims,c,tol,last,modes,nodes){
    var m=modes||A3D_OSNAP,out=[],near=[],i,j,k;
    function add(p,kind){
      var d=Math.sqrt(Math.pow(p[0]-c[0],2)+Math.pow(p[1]-c[1],2));
      if(d<=tol)out.push({p:[p[0],p[1]],kind:kind,d:d});
    }
    if(m.node&&nodes)for(i=0;i<nodes.length;i++)add(nodes[i],'node');
    for(i=0;i<prims.length;i++){
      var P=prims[i],nr=bimOsnapNearest(P,c);
      if(P.k==='L'){
        if(m.end){add(P.a,'end');add(P.b,'end');}
        if(m.mid)add([(P.a[0]+P.b[0])/2,(P.a[1]+P.b[1])/2],'mid');
      }else{
        if(m.end&&!P.circle){add(bimOsnapArcPt(P,P.a1),'end');add(bimOsnapArcPt(P,P.a1+P.sw),'end');}
        if(m.mid&&!P.circle)add(bimOsnapArcPt(P,P.a1+P.sw/2),'mid');
        if(m.cen)add(P.c,'cen');
        if(m.qua)for(k=0;k<4;k++)if(bimOsnapAngIn(k*Math.PI/2,P.a1,P.sw))add(bimOsnapArcPt(P,k*Math.PI/2),'qua');
      }
      if(nr.d>tol)continue;
      near.push(P);
      if(m.nea)add(nr.p,'nea');
      if(last&&m.per){
        if(P.k==='L'){
          var dx=P.b[0]-P.a[0],dz=P.b[1]-P.a[1],L2=dx*dx+dz*dz;
          if(L2>0){
            var t=((last[0]-P.a[0])*dx+(last[1]-P.a[1])*dz)/L2;
            if(t>=0&&t<=1)add([P.a[0]+dx*t,P.a[1]+dz*t],'per');
          }
        }else{
          var la=Math.atan2(last[1]-P.c[1],last[0]-P.c[0]);
          if(bimOsnapAngIn(la,P.a1,P.sw))add(bimOsnapArcPt(P,la),'per');
          if(bimOsnapAngIn(la+Math.PI,P.a1,P.sw))add(bimOsnapArcPt(P,la+Math.PI),'per');
        }
      }
      if(last&&m.tan&&P.k==='A'){
        var ex=last[0]-P.c[0],ez=last[1]-P.c[1],dd=Math.sqrt(ex*ex+ez*ez);
        if(dd>P.r+1e-9){
          var base=Math.atan2(ez,ex),off=Math.acos(P.r/dd);
          if(bimOsnapAngIn(base+off,P.a1,P.sw))add(bimOsnapArcPt(P,base+off),'tan');
          if(bimOsnapAngIn(base-off,P.a1,P.sw))add(bimOsnapArcPt(P,base-off),'tan');
        }
      }
    }
    if(m.int)for(i=0;i<near.length;i++)for(j=i+1;j<near.length;j++){
      var xs=bimOsnapIntersect(near[i],near[j]);
      for(k=0;k<xs.length;k++)add(xs[k],'int');
    }
    return out;
  }
  /* The winner: the closest candidate, NEArest only when nothing else is in range; at equal
     distance the earlier kind in BIM_OSNAP_KINDS wins (a corner is reported as Endpoint, not
     as Intersection). */
  function bimOsnapPick(cands){
    var best=null,i,c;
    for(i=0;i<cands.length;i++){
      c=cands[i];
      if(!best){best=c;continue;}
      var cn=c.kind==='nea',bn=best.kind==='nea';
      if(cn!==bn){if(bn)best=c;continue;}
      if(c.d<best.d-1e-9||(Math.abs(c.d-best.d)<=1e-9&&
         BIM_OSNAP_KINDS.indexOf(c.kind)<BIM_OSNAP_KINDS.indexOf(best.kind)))best=c;
    }
    return best;
  }
  /* Polar tracking: when the direction from last to c is within tolDeg of a multiple of incDeg,
     the point is moved onto that direction at the same distance along it. Null when it is not. */
  function bimPolarTrack(last,c,incDeg,tolDeg){
    var dx=c[0]-last[0],dz=c[1]-last[1],L=Math.sqrt(dx*dx+dz*dz);
    if(!(incDeg>0)||L<1e-9)return null;
    var deg=Math.atan2(dz,dx)*180/Math.PI;
    var snap=Math.round(deg/incDeg)*incDeg;
    if(Math.abs(deg-snap)>(tolDeg>0?tolDeg:3))return null;
    var r=snap*Math.PI/180,ux=Math.cos(r),uz=Math.sin(r);
    var t=dx*ux+dz*uz;
    var ang=((snap%360)+360)%360;
    return {p:[last[0]+ux*t,last[1]+uz*t],angle:ang,dist:t};
  }
  /* The model's primitives on one plan elevation, read as bimSnapCandidates() reads it. */
  function bimOsnapModelPrims(y0,skip,sk){
    var prims=[],nodes=[],i,o,q;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(skip&&skip.indexOf(o.id)>=0)continue;
      if(!bimLayerShown(o))continue;
      q=bimObjOffset(o);
      if(o.t==='sketch'&&o.pts&&Math.abs((o.y||0)+q[1]-y0)<0.05){
        if(o.pts.length===1)nodes.push([o.pts[0][0]+q[0],o.pts[0][1]+q[2]]);
        else prims=prims.concat(bimOsnapPolyPrims(o.pts,o.bulges||null,o.closed!==false,[q[0],q[2]]));
      }else if(o.t==='solid'&&o.bim&&o.bim.centerline&&Math.abs((o.bim.baseY||0)+q[1]-y0)<0.05){
        prims=prims.concat(bimOsnapPolyPrims(o.bim.centerline,o.bim.bulges||null,!!o.bim.closed,[q[0],q[2]]));
      }
    }
    if(sk&&sk.pts&&sk.pts.length>=2)prims=prims.concat(bimOsnapPolyPrims(sk.pts,sk.bulges||null,false,[0,0]));
    return {prims:prims,nodes:nodes};
  }
  /* The marker AutoCAD draws for each kind, centred on (x,y) in screen pixels. */
  function bimOsnapDrawMarker(ctx,x,y,kind){
    var s=6;
    ctx.save();
    ctx.strokeStyle='#4ea1ff';ctx.lineWidth=1.8;ctx.beginPath();
    if(kind==='end'){ctx.rect(x-s,y-s,2*s,2*s);}
    else if(kind==='mid'){ctx.moveTo(x,y-s);ctx.lineTo(x+s,y+s);ctx.lineTo(x-s,y+s);ctx.closePath();}
    else if(kind==='cen'){ctx.arc(x,y,s,0,Math.PI*2);}
    else if(kind==='node'){ctx.arc(x,y,s,0,Math.PI*2);ctx.moveTo(x-s,y-s);ctx.lineTo(x+s,y+s);ctx.moveTo(x+s,y-s);ctx.lineTo(x-s,y+s);}
    else if(kind==='qua'){ctx.moveTo(x,y-s);ctx.lineTo(x+s,y);ctx.lineTo(x,y+s);ctx.lineTo(x-s,y);ctx.closePath();}
    else if(kind==='int'){ctx.moveTo(x-s,y-s);ctx.lineTo(x+s,y+s);ctx.moveTo(x+s,y-s);ctx.lineTo(x-s,y+s);}
    else if(kind==='per'){ctx.moveTo(x-s,y-s);ctx.lineTo(x-s,y+s);ctx.lineTo(x+s,y+s);ctx.moveTo(x-s,y);ctx.lineTo(x,y);ctx.lineTo(x,y+s);}
    else if(kind==='tan'){ctx.arc(x,y,s*0.8,0,Math.PI*2);ctx.moveTo(x-s,y-s);ctx.lineTo(x+s,y-s);}
    else if(kind==='nea'){ctx.moveTo(x-s,y-s);ctx.lineTo(x+s,y-s);ctx.lineTo(x-s,y+s);ctx.lineTo(x+s,y+s);ctx.closePath();}
    else{ctx.arc(x,y,5,0,Math.PI*2);}
    ctx.stroke();
    ctx.restore();
  }
  /* OSNAP (AutoCAD's name; DSETTINGS and OS open it too): which running snaps are on, and the
     polar tracking increment. */
  function openOsnapDlg(){
    closeDlg();
    var d=document.createElement('div'),h='',i,k;
    d.className='a3d-dlg';
    for(i=0;i<BIM_OSNAP_KINDS.length;i++){
      k=BIM_OSNAP_KINDS[i];
      h+='<div class="a3d-dlgrow"><label><input type="checkbox" data-a3dos="'+k+'"'+(A3D_OSNAP[k]?' checked':'')+'> '+
        BIM_OSNAP_NAMES[k]+'</label></div>';
    }
    d.innerHTML='<div class="a3d-dlghd">Object snap and polar tracking</div><div class="a3d-dlgbody">'+h+
      '<div class="a3d-dlgrow"><label><input type="checkbox" data-a3dos="polar"'+(A3D_OSNAP.polar?' checked':'')+'> Polar tracking (F10)</label></div>'+
      '<div class="a3d-dlgrow"><label>Increment angle</label><select data-a3dos="inc">'+
      [90,45,30,22.5,18,15,10,5].map(function(a){return '<option value="'+a+'"'+(a===A3D_OSNAP.polarInc?' selected':'')+'>'+a+'</option>';}).join('')+
      '</select></div>'+
      '<div class="a3d-propnote">Object snap itself is switched with F3 or the status bar; these are the snaps it looks for.</div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="ok">OK</button></div>';
    el.root.appendChild(d);el.dlg=d;
    function submit(){
      var boxes=d.querySelectorAll('input[data-a3dos]'),j;
      for(j=0;j<boxes.length;j++)A3D_OSNAP[boxes[j].getAttribute('data-a3dos')]=!!boxes[j].checked;
      A3D_OSNAP.polarInc=parseFloat(d.querySelector('select[data-a3dos="inc"]').value)||45;
      closeDlg();
      a3dToast('Object snaps: '+bimOsnapSummary());
      paint();
    }
    d.addEventListener('click',function(ev){var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;if(!b)return;if(b.getAttribute('data-a3dlg')==='ok')submit();else closeDlg();});
    d.addEventListener('keydown',function(ev){if(ev.key==='Enter'){ev.preventDefault();ev.stopPropagation();submit();}else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();}});
  }
  function bimOsnapSummary(){
    var on=[],i;
    for(i=0;i<BIM_OSNAP_KINDS.length;i++)if(A3D_OSNAP[BIM_OSNAP_KINDS[i]])on.push(BIM_OSNAP_NAMES[BIM_OSNAP_KINDS[i]]);
    return (on.length?on.join(', '):'none')+(A3D_OSNAP.polar?'; polar every '+A3D_OSNAP.polarInc+'°':'');
  }
  function bimTogglePolar(){
    A3D_OSNAP.polar=!A3D_OSNAP.polar;
    a3dToast('Polar tracking '+(A3D_OSNAP.polar?'on, every '+A3D_OSNAP.polarInc+'°':'off')+' (F10)');
    paint();
  }
  function setOsnapModes(o){
    var k;
    for(k in o)if(o.hasOwnProperty(k)&&A3D_OSNAP.hasOwnProperty(k))A3D_OSNAP[k]=o[k];
    return A3D_OSNAP;
  }
export {
  A3D_OSNAP, BIM_OSNAP_NAMES, bimOsnapCandidates, bimOsnapDrawMarker, bimOsnapModelPrims, bimOsnapPick,
  bimPolarTrack, bimTogglePolar, openOsnapDlg, setOsnapModes
};
