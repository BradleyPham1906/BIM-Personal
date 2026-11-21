import { A3D } from '../core/state.js';
import { bimObjOffset, pushUndo } from '../drawing/plan-mode-sketch.js';
import { bimSegNormal } from './section-profiles.js';
import { bimAlignOffsets } from './footings.js';
import { bimIntInside } from './interiors.js';
import {
  bimClrCircleFits, bimClrConflicts, bimClrRect, bimClrRule, bimClrZone
} from './interiors-clearance.js';
import { bimLayerShown } from '../layers/layer-rules.js';
import { bimEsc } from '../layers/layer-manager.js';
import { bimDispLen, bimLenLabel, bimPropGroup, bimPropRow, bimPropText } from '../properties/palette.js';
import { bimStd, bimStdEdition, bimStdUsedText } from '../standards/registry.js';
import { refreshProps } from '../site-analysis/panel.js';
import { toScreen } from '../io/import-entry.js';
import { paint } from '../map/terrain-3d.js';
import { saveSoon } from './region-regenerate.js';
import { a3dToast, objById } from './csg-booleans.js';


  /* ================= __acad3dV180: Interiors I2 on the live model =================
     docs/work-orders/v180/SPEC.md, WO-07. A furniture or fixture model (an asset of the library, category Furniture or
     Fixtures) has a body: its footprint, the box of its own vertices in the frame it faces. It has a clearance zone when
     the designer gives it a kind (o.bim.clr.kind): a fixture's zone is ADA 305.3's clear floor space (ada.space), the
     others the registry's int.zone depths, all with their edition and the owner's overrides. Which way an item faces is
     the designer's statement (o.bim.clr.face, radians, front along (-sin, cos)), never guessed from the mesh; it follows
     the item's later turns through two of its own vertices (ref), whose bearing is kept from when it was set. A zone is
     blocked by another item's body or by a wall (each straight piece of its centreline, as thick as the wall; a curved
     wall is taken by its chords); zones may overlap each other. A door's opening width and a room's turning space are
     measured against the registry's rules (404.2.3, 304.3.1) and named with their clause and edition: a measurement,
     never a compliance finding. Everything on one level: bases within BIM_CLR_LEVEL_TOL. */
  var BIM_CLR_LEVEL_TOL=0.5;
  var BIM_CLR_KINDS=[['','None: no zone'],['fixture','Fixture: a clear floor space (ADA 305.3)'],['seat','Seat'],['storage','Storage'],['work','Work surface'],['bed','Bed, at its side']];
  function bimClrIsItem(o){
    return !!(o&&o.t==='solid'&&o.mesh&&o.mesh.v&&o.mesh.v.length&&o.bim&&o.bim.type==='familyInstance'&&
      (o.bim.category==='Furniture'||o.bim.category==='Fixtures'||(o.bim.clr&&o.bim.clr.kind)));
  }
  /* the item's vertices in world plan points, and its base */
  function bimClrPlanPts(o){
    var q=bimObjOffset(o),v=o.mesh.v,pts=[],i,y=Infinity;
    for(i=0;i<v.length;i++){pts.push([v[i][0]+q[0],v[i][2]+q[2]]);if(v[i][1]<y)y=v[i][1];}
    return {pts:pts,y:(y===Infinity?0:y)+q[1]};
  }
  /* the box of points in the frame turned by rot: {center, w, d, rot}. Pure. */
  function bimClrBodyOf(pts,rot){
    var cs=Math.cos(rot||0),sn=Math.sin(rot||0),a0=Infinity,a1=-Infinity,b0=Infinity,b1=-Infinity,i,a,b,am,bm;
    if(!pts||!pts.length)return null;
    for(i=0;i<pts.length;i++){
      a=pts[i][0]*cs+pts[i][1]*sn;b=-pts[i][0]*sn+pts[i][1]*cs;
      if(a<a0)a0=a;if(a>a1)a1=a;if(b<b0)b0=b;if(b>b1)b1=b;
    }
    am=(a0+a1)/2;bm=(b0+b1)/2;
    return {center:[am*cs-bm*sn,am*sn+bm*cs],w:a1-a0,d:b1-b0,rot:rot||0};
  }
  function bimClrBearing(v,i,j){return Math.atan2(v[j][2]-v[i][2],v[j][0]-v[i][0]);}
  /* the way the item faces now, radians; 0 when not set */
  function bimClrFace(o){
    var c=o&&o.bim&&o.bim.clr,v=o&&o.mesh&&o.mesh.v;
    if(!c||typeof c.face!=='number')return 0;
    if(c.ref&&v&&v[c.ref[0]]&&v[c.ref[1]]&&typeof c.b0==='number')return c.face+(bimClrBearing(v,c.ref[0],c.ref[1])-c.b0);
    return c.face;
  }
  /* two of the item's vertices far apart in plan, to follow its turns */
  function bimClrRef(o){
    var v=o.mesh.v,j,best=-1,bd=0,d;
    for(j=1;j<v.length;j++){d=(v[j][0]-v[0][0])*(v[j][0]-v[0][0])+(v[j][2]-v[0][2])*(v[j][2]-v[0][2]);if(d>bd){bd=d;best=j;}}
    return bd>1e-8?[0,best]:null;
  }
  /* the zone's depth and side reach for a kind, from the registry; null for none */
  function bimClrZoneSize(kind,w){
    if(kind==='fixture'){
      var L=bimStd('ada.space','clear_l'),W=bimStd('ada.space','clear_w');
      if(!(L>0))return null;
      return {front:L,side:(W>w)?(W-w)/2:0,topic:'ada.space'};
    }
    if(!kind)return null;
    var f=bimStd('int.zone',kind),s=bimStd('int.zone','side');
    return f>0?{front:f,side:s>0?s:0,topic:'int.zone'}:null;
  }
  /* each straight piece of each wall, as a polygon, with its base */
  function bimClrWalls(){
    var out=[],i,j,o,cl,n,segs,a,b,nr,off,q,t;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(!o||o.t!=='solid'||!o.bim||o.bim.type!=='wall'||!o.bim.centerline||o.bim.centerline.length<2||!bimLayerShown(o))continue;
      cl=o.bim.centerline;n=cl.length;segs=o.bim.closed?n:n-1;t=o.bim.thickness||0.2;
      off=bimAlignOffsets(t,o.bim.align);q=bimObjOffset(o);
      for(j=0;j<segs;j++){
        a=cl[j];b=cl[(j+1)%n];nr=bimSegNormal(a,b);
        out.push({id:o.id,name:o.name,y:(o.bim.baseY||0)+q[1],poly:[
          [a[0]+q[0]+nr[0]*off.dLeft,a[1]+q[2]+nr[1]*off.dLeft],[b[0]+q[0]+nr[0]*off.dLeft,b[1]+q[2]+nr[1]*off.dLeft],
          [b[0]+q[0]-nr[0]*off.dRight,b[1]+q[2]-nr[1]*off.dRight],[a[0]+q[0]-nr[0]*off.dRight,a[1]+q[2]-nr[1]*off.dRight]]});
      }
    }
    return out;
  }
  /* every item's body and zone, and what blocks each zone */
  function bimClrScene(){
    var items=[],walls=bimClrWalls(),i,o,P,rot,B,kind,Z,it,sub,obs,cf,j,names={};
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(!bimClrIsItem(o)||!bimLayerShown(o))continue;
      P=bimClrPlanPts(o);kind=o.bim.clr&&o.bim.clr.kind||'';rot=bimClrFace(o);
      B=bimClrBodyOf(P.pts,rot);
      if(!B)continue;
      Z=bimClrZoneSize(kind,B.w);
      it={id:o.id,name:o.name,kind:kind,y:P.y,box:B,body:bimClrRect(B.center,B.w,B.d,B.rot),zone:Z?bimClrZone(B,Z.front,Z.side):null,size:Z,blocked:[]};
      items.push(it);names[o.id]=o.name;
    }
    for(i=0;i<walls.length;i++)names[walls[i].id]=walls[i].name;
    for(i=0;i<items.length;i++){
      it=items[i];
      if(!it.zone)continue;
      sub=[it];obs=[];
      for(j=0;j<items.length;j++)if(j!==i&&Math.abs(items[j].y-it.y)<BIM_CLR_LEVEL_TOL)sub.push({id:items[j].id,body:items[j].body});
      for(j=0;j<walls.length;j++)if(Math.abs(walls[j].y-it.y)<BIM_CLR_LEVEL_TOL)obs.push({id:walls[j].id,poly:walls[j].poly});
      cf=bimClrConflicts(sub,obs);
      for(j=0;j<cf.length;j++)if(cf[j].item===it.id&&it.blocked.indexOf(names[cf[j].with]||cf[j].with)<0)it.blocked.push(names[cf[j].with]||cf[j].with);
    }
    return {items:items,walls:walls};
  }
  /* the widest turning circle that fits in a room around the bodies in it: its diameter and a centre. Pure: poly the
     room, bodies convex polygons, step the grid of centres tried; answers {d, at} (d 0 when none fits). */
  function bimClrTurnFit(poly,bodies,step,maxD){
    var x0=Infinity,x1=-Infinity,z0=Infinity,z1=-Infinity,i,lo=0,hi,mid,k,best=null;
    if(!poly||poly.length<3)return {d:0,at:null};
    step=step>0?step:0.05;
    for(i=0;i<poly.length;i++){x0=Math.min(x0,poly[i][0]);x1=Math.max(x1,poly[i][0]);z0=Math.min(z0,poly[i][1]);z1=Math.max(z1,poly[i][1]);}
    hi=Math.min(maxD>0?maxD:Infinity,Math.min(x1-x0,z1-z0));
    function clearOf(c,r){
      var b,j,n,dx,dz,L2,t,px,pz;
      for(b=0;b<(bodies?bodies.length:0);b++){
        n=bodies[b].length;
        if(bimIntInside(c,bodies[b]))return false;
        for(j=0;j<n;j++){
          var p=bodies[b][j],q=bodies[b][(j+1)%n];
          dx=q[0]-p[0];dz=q[1]-p[1];L2=dx*dx+dz*dz;t=L2>0?Math.max(0,Math.min(1,((c[0]-p[0])*dx+(c[1]-p[1])*dz)/L2)):0;
          px=p[0]+t*dx-c[0];pz=p[1]+t*dz-c[1];
          if(Math.sqrt(px*px+pz*pz)<r-1e-9)return false;
        }
      }
      return true;
    }
    function fits(d){
      var x,z,c;
      for(x=x0+d/2;x<=x1-d/2+1e-9;x+=step)for(z=z0+d/2;z<=z1-d/2+1e-9;z+=step){
        c=[x,z];
        if(bimClrCircleFits(poly,c,d/2)&&clearOf(c,d/2))return c;
      }
      return null;
    }
    if(!(hi>0))return {d:0,at:null};
    for(k=0;k<14;k++){
      mid=(lo+hi)/2;
      var c=fits(mid);
      if(c){lo=mid;best=c;}else hi=mid;
    }
    return {d:best?lo:0,at:best};
  }
  /* the registry's rule for a check: its clause, its edition's name, its least value in inches */
  function bimClrRuleOf(which){
    var t=which==='door'?'ada.door':'ada.space',n=which==='door'?'clear':'turn',v=bimStd(t,n),E=bimStdEdition(t);
    return {clause:which==='door'?'404.2.3':'304.3.1',edition:E&&E.name?E.name:'',minIn:(typeof v==='number'&&isFinite(v))?v/0.0254:undefined,topic:t};
  }
  function bimClrSay(R){
    var s=R.status==='not evaluated'?'not evaluated':(R.status==='meets'?'meets':'below');
    return s+(R.measuredIn!==undefined?', '+R.measuredIn+' in measured':'')+' ('+(R.clause?R.clause+', ':'')+(R.edition||'no edition in force')+')';
  }
  /* a door: its opening width against 404.2.3. The opening is what the model holds; the leaf and the stops are not taken off. */
  function bimClrDoorCheck(o){
    var w=o&&o.bim&&typeof o.bim.width==='number'&&isFinite(o.bim.width)&&o.bim.width>0?o.bim.width:null;
    return bimClrRule(bimClrRuleOf('door'),w===null?undefined:w);
  }
  /* a room: the widest turning circle around the items in it, against 304.3.1 */
  function bimClrRoomCheck(o){
    if(!o||!Array.isArray(o.pts)||o.pts.length<3||(o.region&&o.region.open))return {rule:bimClrRule(bimClrRuleOf('turn'),undefined),fit:{d:0,at:null}};
    var q=bimObjOffset(o),poly=o.pts.map(function(p){return [p[0]+q[0],p[1]+q[2]];}),S=bimClrScene(),bodies=[],i,rule=bimClrRuleOf('turn');
    for(i=0;i<S.items.length;i++)if(Math.abs(S.items[i].y-((o.y||0)+q[1]))<BIM_CLR_LEVEL_TOL)bodies.push(S.items[i].body);
    var fit=bimClrTurnFit(poly,bodies,0.05,(rule.minIn>0?rule.minIn*0.0254*1.5:3));
    return {rule:bimClrRule(rule,fit.d),fit:fit};
  }
  /* ---- on the plan: the zones of the items selected, red when blocked ---- */
  function bimClrDrawZones(ctx,V,W,H){
    var ids=(A3D.selSet&&A3D.selSet.length)?A3D.selSet:(A3D.sel?[A3D.sel]:[]),S,i,j,it,s2,on,pts;
    A3D.lastZones=0;
    if(!ids.length)return;
    var any=false;
    for(i=0;i<ids.length;i++)if(bimClrIsItem(objById(ids[i])))any=true;
    if(!any)return;
    S=bimClrScene();
    ctx.save();ctx.lineWidth=1.5;
    for(i=0;i<S.items.length;i++){
      it=S.items[i];
      if(ids.indexOf(it.id)<0||!it.zone)continue;
      A3D.lastZones++;
      var bad=it.blocked.length>0;
      ctx.strokeStyle=bad?'rgba(220,53,69,0.95)':'rgba(46,160,67,0.95)';ctx.fillStyle=bad?'rgba(220,53,69,0.16)':'rgba(46,160,67,0.14)';
      if(ctx.setLineDash)ctx.setLineDash([6,4]);
      ctx.beginPath();on=false;pts=it.zone;
      for(j=0;j<pts.length;j++){
        s2=toScreen([pts[j][0],it.y+0.02,pts[j][1]],V,W,H);
        if(!s2)continue;
        if(on)ctx.lineTo(s2[0],s2[1]);else{ctx.moveTo(s2[0],s2[1]);on=true;}
      }
      ctx.closePath();ctx.fill();ctx.stroke();
    }
    ctx.restore();
  }
  /* ---- Properties ---- */
  function bimClrPropsHtml(o){
    var S=bimClrScene(),it=null,i,r='',c=o.bim.clr||{},Z;
    for(i=0;i<S.items.length;i++)if(S.items[i].id===o.id)it=S.items[i];
    r+=bimPropRow('Kind','<select data-clr="kind">'+BIM_CLR_KINDS.map(function(k){return '<option value="'+k[0]+'"'+((c.kind||'')===k[0]?' selected':'')+'>'+bimEsc(k[1])+'</option>';}).join('')+'</select>');
    if(!it)return bimPropGroup('Clearance',r+bimPropText('Zone','not evaluated: the item is hidden or has no shape'));
    r+=bimPropText(bimLenLabel('Body'),bimDispLen(it.box.w)+' by '+bimDispLen(it.box.d));
    if(c.kind){
      var deg=Math.round(((bimClrFace(o)*180/Math.PI)%360+360)%360);
      r+=bimPropRow('Faces (deg)','<input type="number" step="any" data-clr="face" value="'+deg+'"> <button type="button" class="a3d-pedit" data-clract="turn">Turn 90</button>');
      Z=it.size;
      if(Z){
        r+=bimPropText(bimLenLabel('Zone'),bimDispLen(it.box.w+2*Z.side)+' wide, '+bimDispLen(Z.front)+' deep, in front');
        r+=bimPropText('Zone is',it.blocked.length?'blocked by '+it.blocked.join(', '):'clear of walls and other items');
        r+='<div class="a3d-stdsrc">Standards: '+bimEsc(bimStdUsedText(Z.topic))+'</div>';
      }else r+=bimPropText('Zone','not evaluated: the registry has no depth for this kind');
    }else r+=bimPropText('Zone','none: give the item a kind');
    return bimPropGroup('Clearance',r);
  }
  function bimClrDoorHtml(o){
    var R=bimClrDoorCheck(o);
    return bimPropGroup('Clearance',bimPropText('Clear width',bimClrSay(R))+
      bimPropText('Measured','the opening\'s width; the leaf and the stops are not taken off, and no exception is applied')+
      '<div class="a3d-stdsrc">Standards: '+bimEsc(bimStdUsedText('ada.door'))+'</div>');
  }
  function bimClrRoomHtml(o){
    var C=bimClrRoomCheck(o);
    return bimPropGroup('Clearance',bimPropText('Turning space',bimClrSay(C.rule))+
      bimPropText(bimLenLabel('Widest circle'),C.fit.d>0?bimDispLen(C.fit.d)+' across, around the furniture and fixtures in it':'none fits')+
      '<div class="a3d-stdsrc">Standards: '+bimEsc(bimStdUsedText('ada.space'))+'</div>');
  }
  function bimClrSet(o,fn){
    var c=JSON.parse(JSON.stringify(o.bim.clr||{}));
    fn(c);
    pushUndo();
    if(!c.kind){delete o.bim.clr;}
    else{
      if(typeof c.face!=='number')c.face=0;
      c.ref=bimClrRef(o);c.b0=c.ref?bimClrBearing(o.mesh.v,c.ref[0],c.ref[1]):undefined;
      o.bim.clr=c;
    }
    refreshProps();paint();saveSoon();
    return true;
  }
  function bimClrPropChange(ev){
    var f=ev.target&&ev.target.closest?ev.target.closest('[data-clr]'):null;
    if(!f)return false;
    var o=objById(A3D.sel);
    if(!bimClrIsItem(o)){a3dToast('Select a furniture or fixture model');return false;}
    var k=f.getAttribute('data-clr'),v=f.value,face=bimClrFace(o);
    if(k==='kind')return bimClrSet(o,function(c){c.kind=v;c.face=face;});
    if(k==='face'){
      var x=parseFloat(v);
      if(!isFinite(x)){a3dToast('Faces is an angle in degrees');refreshProps();return false;}
      return bimClrSet(o,function(c){c.face=x*Math.PI/180;});
    }
    return false;
  }
  function bimClrPropClick(ev){
    var b=ev.target&&ev.target.closest?ev.target.closest('[data-clract]'):null;
    if(!b)return false;
    var o=objById(A3D.sel);
    if(!bimClrIsItem(o))return false;
    var face=bimClrFace(o);
    return bimClrSet(o,function(c){c.face=face+Math.PI/2;});
  }
export {
  bimClrDoorCheck, bimClrDoorHtml, bimClrDrawZones, bimClrIsItem, bimClrPropChange, bimClrPropClick,
  bimClrPropsHtml, bimClrRoomCheck, bimClrRoomHtml, bimClrScene
};
