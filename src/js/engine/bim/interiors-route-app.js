import { A3D } from '../core/state.js';
import { bimObjOffset, pushUndo } from '../drawing/plan-mode-sketch.js';
import { bimEgGrid, bimEgNearest, bimEgPath, bimEgStatus } from './interiors-routes.js';
import { bimLayerShown } from '../layers/layer-rules.js';
import { bimEsc } from '../layers/layer-manager.js';
import { bimSimStamp } from '../analysis/simulation.js';
import { bimStd, bimStdClear, bimStdEdition, bimStdOvOf, bimStdOverride } from '../standards/registry.js';
import { toScreen } from '../io/import-entry.js';
import { bimFlattenPoly } from '../drawing/arc-storage.js';
import { saveSoon } from './region-regenerate.js';
import { bimCameraIsPlan } from '../views/saved-views.js';
import { a3dToast } from './csg-booleans.js';

  /* ================= __acad3dV181: Interiors I3, the app integration ================= */
  var A3D_EG_RUN={show:false,stamp:'',rooms:[],cell:0.25};
  var BIM_EG_STD='app.egress';

  function bimEgRouteCell(){
    var v=A3D.site&&A3D.site.egressCell;
    return typeof v==='number'&&isFinite(v)&&v>0?v:0.25;
  }
  function bimEgRouteLimit(){
    var v=bimStd(BIM_EG_STD,'limit');
    return typeof v==='number'&&isFinite(v)&&v>0?v:null;
  }
  function bimEgRouteStamp(){
    var parts=[bimSimStamp(),bimEgRouteCell(),bimEgRouteLimit(),bimStdEdition(BIM_EG_STD)];
    A3D.objs.forEach(function(o){
      var shown=bimLayerShown(o),q=bimObjOffset(o);
      if(o.t==='room')parts.push([o.id,shown,o.pts,o.y,o.levelId,q,o.region&&o.region.open,o.region&&o.region.islands]);
      else if(o.t==='opening'&&o.bim&&o.bim.type==='door')
        parts.push([o.id,shown,o.bim.exit,o.bim.center,o.bim.width,o.bim.hostWallId,q]);
      else if(o.t==='solid'&&o.bim&&o.bim.type==='wall')
        parts.push([o.id,shown,o.bim.centerline,o.bim.bulges,o.bim.closed,o.bim.thickness,o.bim.baseY,o.bim.height,q]);
    });
    return JSON.stringify(parts);
  }
  function bimEgWorldRing(o){
    var q=bimObjOffset(o);
    return (o.pts||[]).map(function(p){return [p[0]+q[0],p[1]+q[2]];});
  }
  function bimEgNearestFree(g,p,maxDistance){
    var best=-1,bestD=Infinity,i,j,cx,cz,dx,dz,d;
    for(j=0;j<g.nz;j++)for(i=0;i<g.nx;i++){
      var idx=j*g.nx+i;
      if(!g.free[idx])continue;
      cx=g.x0+(i+0.5)*g.cell;cz=g.z0+(j+0.5)*g.cell;
      dx=cx-p[0];dz=cz-p[1];d=dx*dx+dz*dz;
      if(d<bestD){bestD=d;best=idx;}
    }
    return best>=0&&(maxDistance===undefined||bestD<=maxDistance*maxDistance)?best:-1;
  }
  function bimEgCellPoint(g,idx){
    return [g.x0+((idx%g.nx)+0.5)*g.cell,g.z0+(Math.floor(idx/g.nx)+0.5)*g.cell];
  }
  function bimEgRoomCenter(poly){
    var a=0,cx=0,cz=0,i,j,p,q;
    for(i=0;i<poly.length;i++){
      p=poly[i];q=poly[(i+1)%poly.length];
      var cross=p[0]*q[1]-q[0]*p[1];
      a+=cross;cx+=(p[0]+q[0])*cross;cz+=(p[1]+q[1])*cross;
    }
    if(Math.abs(a)>1e-9)return [cx/(3*a),cz/(3*a)];
    cx=0;cz=0;
    for(i=0;i<poly.length;i++){cx+=poly[i][0];cz+=poly[i][1];}
    return [cx/poly.length,cz/poly.length];
  }
  function bimEgPointSegDist(p,a,b){
    var dx=b[0]-a[0],dz=b[1]-a[1],l=dx*dx+dz*dz;
    var t=l?((p[0]-a[0])*dx+(p[1]-a[1])*dz)/l:0;
    t=Math.max(0,Math.min(1,t));
    dx=p[0]-(a[0]+t*(b[0]-a[0]));dz=p[1]-(a[1]+t*(b[1]-a[1]));
    return Math.sqrt(dx*dx+dz*dz);
  }
  function bimEgNearBoundary(poly,p){
    var best=Infinity,i;
    for(i=0;i<poly.length;i++)best=Math.min(best,bimEgPointSegDist(p,poly[i],poly[(i+1)%poly.length]));
    return best;
  }
  function bimEgDoorWorld(door,host){
    var q=bimObjOffset(host||door),p=door&&door.bim&&door.bim.center;
    return p&&p.length>=2?[p[0]+q[0],p[1]+q[2]]:null;
  }
  function bimEgStrip(a,b,half){
    var dx=b[0]-a[0],dz=b[1]-a[1],len=Math.sqrt(dx*dx+dz*dz);
    if(len<1e-6||half<=0)return null;
    var nx=-dz/len*half,nz=dx/len*half;
    return [[a[0]+nx,a[1]+nz],[b[0]+nx,b[1]+nz],[b[0]-nx,b[1]-nz],[a[0]-nx,a[1]-nz]];
  }
  function bimEgWallObstacles(wall,doors){
    var b=wall.bim,q=bimObjOffset(wall),line=bimFlattenPoly(b.centerline,b.bulges||null,!!b.closed,0.12);
    var out=[],segCount=b.closed?line.length:line.length-1,th=(b.thickness||0.15)/2,i,d,a,cx,cz,dx,dz,len2,len,t,off,cuts,k,cursor,lo,hi,p1,p2,poly;
    for(i=0;i<segCount;i++){
      a=[line[i][0]+q[0],line[i][1]+q[2]];
      var z=[line[(i+1)%line.length][0]+q[0],line[(i+1)%line.length][1]+q[2]];
      dx=z[0]-a[0];dz=z[1]-a[1];len2=dx*dx+dz*dz;
      if(len2<1e-8)continue;
      len=Math.sqrt(len2);cuts=[];
      for(d=0;d<doors.length;d++){
        if(doors[d].bim.hostWallId!==wall.id||!(doors[d].bim.width>0))continue;
        c=bimEgDoorWorld(doors[d],wall);if(!c)continue;
        t=((c[0]-a[0])*dx+(c[1]-a[1])*dz)/len2;
        cx=a[0]+t*dx;cz=a[1]+t*dz;off=Math.sqrt((c[0]-cx)*(c[0]-cx)+(c[1]-cz)*(c[1]-cz));
        if(t<0||t>1||off>th+0.25)continue;
        var gap=(doors[d].bim.width/2+0.05)/len;
        cuts.push([Math.max(0,t-gap),Math.min(1,t+gap)]);
      }
      cuts.sort(function(x,y){return x[0]-y[0];});
      cursor=0;
      for(k=0;k<cuts.length;k++){
        lo=Math.max(cursor,cuts[k][0]);hi=Math.max(lo,cuts[k][1]);
        if(lo>cursor){
          p1=[a[0]+dx*cursor,a[1]+dz*cursor];p2=[a[0]+dx*lo,a[1]+dz*lo];
          poly=bimEgStrip(p1,p2,th);if(poly)out.push(poly);
        }
        cursor=Math.max(cursor,hi);
      }
      if(cursor<1){
        p1=[a[0]+dx*cursor,a[1]+dz*cursor];p2=z;
        poly=bimEgStrip(p1,p2,th);if(poly)out.push(poly);
      }
    }
    return out;
  }
  function bimEgHull(points){
    var p=points.slice().sort(function(a,b){return a[0]-b[0]||a[1]-b[1];}),lo=[],hi=[],i;
    function cross(o,a,b){return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0]);}
    for(i=0;i<p.length;i++){
      if(i&&p[i][0]===p[i-1][0]&&p[i][1]===p[i-1][1])continue;
      while(lo.length>1&&cross(lo[lo.length-2],lo[lo.length-1],p[i])<=0)lo.pop();
      lo.push(p[i]);
    }
    for(i=p.length-1;i>=0;i--){
      if(i<p.length-1&&p[i][0]===p[i+1][0]&&p[i][1]===p[i+1][1])continue;
      while(hi.length>1&&cross(hi[hi.length-2],hi[hi.length-1],p[i])<=0)hi.pop();
      hi.push(p[i]);
    }
    lo.pop();hi.pop();
    return lo.concat(hi);
  }
  function bimEgSolidObstacle(o,floorY){
    if(!o.mesh||!o.mesh.v)return null;
    var q=bimObjOffset(o),points=[],i,v,y;
    for(i=0;i<o.mesh.v.length;i++){
      v=o.mesh.v[i];y=v[1]+q[1];
      if(y>=floorY-0.1&&y<=floorY+2)points.push([v[0]+q[0],v[2]+q[2]]);
    }
    if(points.length<3)return null;
    var hull=bimEgHull(points);
    return hull.length>=3?hull:null;
  }
  function bimEgObstacles(room,doors){
    var out=[],roomY=(room.y||0)+bimObjOffset(room)[1],i,o,b,wallY;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];b=o.bim;
      if(!b||o.t!=='solid'||!bimLayerShown(o))continue;
      if(b.type==='wall'){
        wallY=(b.baseY||0)+bimObjOffset(o)[1];
        if(Math.abs(wallY-roomY)>0.5)continue;
        out=out.concat(bimEgWallObstacles(o,doors));
      }else if(b.type!=='floor'&&b.type!=='ceiling'&&b.type!=='roof'){
        var poly=bimEgSolidObstacle(o,roomY);
        if(poly)out.push(poly);
      }else if(!b.type){
        var poly2=bimEgSolidObstacle(o,roomY);
        if(poly2)out.push(poly2);
      }
    }
    return out;
  }
  function bimEgRouteOne(room,doors,cell,limit){
    var poly=bimEgWorldRing(room),roomY=(room.y||0)+bimObjOffset(room)[1],i,obstacles,g,startIdx,start,routes={},targets=[],door,host,p,name,path,nearest,best,points=[],status;
    if(room.region&&room.region.open)return {room:room, status:{status:'not evaluated',why:'room boundary is open'},points:[]};
    if(room.region&&room.region.islands)return {room:room, status:{status:'not evaluated',why:'room boundary contains islands'},points:[]};
    if(poly.length<3)return {room:room,status:{status:'not evaluated',why:'room outline is incomplete'},points:[]};
    obstacles=bimEgObstacles(room,doors);g=bimEgGrid(poly,obstacles,cell);
    if(!g)return {room:room,status:{status:'not evaluated',why:'room grid could not be built'},points:[]};
    startIdx=bimEgNearestFree(g,bimEgRoomCenter(poly));
    if(startIdx<0)return {room:room,status:bimEgStatus(null,limit),points:[]};
    start=bimEgCellPoint(g,startIdx);
    for(i=0;i<doors.length;i++){
      door=doors[i];if(!door.bim.exit)continue;
      host=null;
      for(var h=0;h<A3D.objs.length;h++)if(A3D.objs[h].id===door.bim.hostWallId){host=A3D.objs[h];break;}
      if(!host||!host.bim||host.bim.type!=='wall')continue;
      if(Math.abs((host.bim.baseY||0)+bimObjOffset(host)[1]-roomY)>0.5)continue;
      p=bimEgDoorWorld(door,host);if(!p)continue;
      if(bimEgNearBoundary(poly,p)>Math.max(0.75,(door.bim.width||0)/2+0.35))continue;
      var targetIdx=bimEgNearestFree(g,p,Math.max(0.75,(door.bim.width||0)/2+0.75));
      if(targetIdx<0)continue;
      name=String(door.name||'Exit')+' ['+door.id+']';
      path=bimEgPath(g,start,bimEgCellPoint(g,targetIdx));
      routes[name]=path;
      if(path)targets.push({name:name,path:path,point:p});
    }
    nearest=bimEgNearest(routes);
    if(nearest){
      for(i=0;i<targets.length;i++)if(targets[i].name===nearest.exit){best=targets[i];break;}
      status=bimEgStatus(nearest,limit);
      if(best)points=best.path.cells.map(function(idx){return bimEgCellPoint(g,idx);});
      return {room:room,status:status,exit:best?best.name:nearest.exit,len:nearest.len,points:points,y:roomY};
    }
    return {room:room,status:bimEgStatus(null,limit),points:[],y:roomY};
  }
  function bimEgRouteSummary(){
    var i,n={within:0,over:0,blocked:0,'not evaluated':0,unknown:0},stale=!!(A3D_EG_RUN.stamp&&A3D_EG_RUN.stamp!==bimEgRouteStamp());
    if(!A3D_EG_RUN.stamp)    return {state:'off',status:'Not run',stale:false,hideDisabled:true};
    for(i=0;i<A3D_EG_RUN.rooms.length;i++){
      var s=A3D_EG_RUN.rooms[i].status.status;
      if(n.hasOwnProperty(s))n[s]++;else n.unknown++;
    }
    if(stale)return {state:'stale',status:'The model changed; run routes again',stale:true,hideDisabled:!A3D_EG_RUN.show};
    return {state:A3D_EG_RUN.show?'on':'off',status:A3D_EG_RUN.rooms.length+' rooms: '+n.within+' within, '+n.over+' over, '+n.blocked+
      ' blocked, '+(n.unknown+n['not evaluated'])+' not evaluated',stale:false,counts:n,hideDisabled:!A3D_EG_RUN.show};
  }
  function bimEgRouteCard(){
    var cell=bimEgRouteCell(),limit=bimEgRouteLimit(),E=bimStdEdition(BIM_EG_STD),sum=bimEgRouteSummary(),rows='',i,r;
    for(i=0;i<A3D_EG_RUN.rooms.length;i++){
      r=A3D_EG_RUN.rooms[i];
      rows+='<div class="a3d-prow"><div class="a3d-plabel">'+bimEsc(r.room.name||'Room')+'</div><div class="a3d-pval">'+
        bimEsc(r.status.status+(r.exit?': '+r.exit:'')+'; '+r.status.why)+'</div></div>';
    }
    var extra='<div class="a3d-prow"><div class="a3d-plabel">Grid cell (m)</div><div class="a3d-pval"><input type="number" min="0.05" max="2" step="0.05" data-egress-param="cell" value="'+cell+'"></div></div>'+
      '<div class="a3d-prow"><div class="a3d-plabel">Travel limit (m)</div><div class="a3d-pval"><input type="number" min="0.01" step="any" data-egress-param="limit" value="'+(limit===null?'':limit)+'" placeholder="Not chosen"></div></div>'+
      '<div class="a3d-propnote">Basis: '+bimEsc(E&&E.name?E.name:'owner-selected project limit')+'. No legal limit is preselected. Marked doors are assumed passable; this plan estimate is not an egress-compliance finding.</div>'+rows;
    return {state:sum.state,status:sum.status,extra:extra,runDisabled:!A3D.objs.some(function(o){return o.t==='room'&&o.pts&&o.pts.length>=3;}),hideDisabled:sum.hideDisabled};
  }
  function bimEgRouteRun(){
    var rooms=A3D.objs.filter(function(o){return o.t==='room'&&o.pts&&o.pts.length>=3;});
    if(!rooms.length){a3dToast('Circulation routes need at least one room');return false;}
    var doors=A3D.objs.filter(function(o){return o.t==='opening'&&o.bim&&o.bim.type==='door';});
    var cell=bimEgRouteCell(),limit=bimEgRouteLimit();
    A3D_EG_RUN.rooms=rooms.map(function(room){return bimEgRouteOne(room,doors,cell,limit);});
    A3D_EG_RUN.cell=cell;A3D_EG_RUN.show=true;A3D_EG_RUN.stamp=bimEgRouteStamp();
    return bimEgRouteSummary();
  }
  function bimEgRouteHide(){
    A3D_EG_RUN.show=false;
    return true;
  }
  function bimEgRouteParam(field,value){
    if(field==='cell'){
      var cell=parseFloat(value);
      if(!isFinite(cell)||cell<0.05||cell>2){a3dToast('Grid cell must be between 0.05 and 2 m');return false;}
      if(cell===bimEgRouteCell())return true;
      pushUndo();
      if(!A3D.site)A3D.site={name:'Site'};
      A3D.site.egressCell=cell;saveSoon();
      return true;
    }
    if(field==='limit'){
      if(String(value||'').trim()===''){
        var old=bimStdOvOf(BIM_EG_STD,'limit');
        return old?bimStdClear(BIM_EG_STD,'limit'):true;
      }
      var limit=parseFloat(value);
      if(!isFinite(limit)||limit<=0){a3dToast('Travel limit must be a positive number of metres');return false;}
      return bimStdOverride(BIM_EG_STD,'limit',limit,'Owner-selected limit for this project');
    }
    return false;
  }
  function bimEgRouteDraw(ctx,V,W,H){
    if(!bimCameraIsPlan())return;
    var i,j,r,p,s,color,stale=bimEgRouteSummary().stale;
    ctx.save();ctx.lineCap='round';ctx.lineJoin='round';ctx.font='12px sans-serif';
    if(A3D_EG_RUN.show&&!stale)for(i=0;i<A3D_EG_RUN.rooms.length;i++){
      r=A3D_EG_RUN.rooms[i];
      if(!r.points||!r.points.length)continue;
      color=r.status.status==='within'?'#24b47e':(r.status.status==='over'?'#f08a32':'#d9534f');
      ctx.strokeStyle=color;ctx.fillStyle=color;ctx.lineWidth=3;ctx.beginPath();
      for(j=0;j<r.points.length;j++){
        p=toScreen([r.points[j][0],r.y+0.03,r.points[j][1]],V,W,H);
        if(j===0)ctx.moveTo(p[0],p[1]);else ctx.lineTo(p[0],p[1]);
      }
      ctx.stroke();
      if(r.exit)ctx.fillText(r.status.status+' '+r.len.toFixed(1)+' m',p[0]+5,p[1]-5);
    }
    A3D.objs.forEach(function(o){
      if(o.t!=='opening'||!o.bim||o.bim.type!=='door'||!o.bim.exit)return;
      var host=null;
      for(var k=0;k<A3D.objs.length;k++)if(A3D.objs[k].id===o.bim.hostWallId){host=A3D.objs[k];break;}
      var c=bimEgDoorWorld(o,host);
      if(!c)return;
      s=toScreen([c[0],host&&host.bim?(host.bim.baseY||0)+bimObjOffset(host)[1]+0.05:0.05,c[1]],V,W,H);
      ctx.fillStyle='#ffbf47';ctx.beginPath();ctx.arc(s[0],s[1],6,0,Math.PI*2);ctx.fill();
      ctx.fillStyle='#111';ctx.fillText('EXIT',s[0]+7,s[1]-6);
    });
    ctx.restore();
  }
export { bimEgRouteCard, bimEgRouteDraw, bimEgRouteHide, bimEgRouteParam, bimEgRouteRun };
