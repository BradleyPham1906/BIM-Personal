import { A3D } from '../core/state.js';
import { bimObjOffset } from '../drawing/plan-mode-sketch.js';
import { bimEnsureBuildings } from './building-site-hierarchy.js';
import {
  bimIntCheck, bimIntDistances, bimIntDoorLinks, bimIntMatch, bimIntProgramItem, bimIntRelation,
  bimIntSharedLength
} from './interiors.js';
import { bimFindWallSegmentAt } from './columns-openings.js';
import { A3D_CLB, bimClbE } from '../site-analysis/climate-board.js';
import { BIM_OPENING_REPLACE_TOL } from './dependency-graph.js';
import { bimUsageById } from './usages-live-areas.js';
import { objById } from './csg-booleans.js';


  /* ================= __acad3dV179: Interiors I1 on the live model =================
     docs/work-orders/v179/SPEC.md part 5, WO-10 and WO-11. The programme is the building's own (b.programme, saved
     and undone with the buildings): items by use, relations between uses. A room's use is its usage's name, else its
     own name, so a room named Kitchen or given the Kitchen usage is matched to the Kitchen item. Relations name uses,
     not room ids (WO-10's choice): a programme is written before its rooms are drawn, and a use with two rooms is
     next to another when either room is. Facts are measured per level: a shared wall within BIM_INT_SHARED_TOL of
     the other room's edge (rooms are measured to their faces, so a wall's thickness lies between them); a door joins
     the rooms either side of it on its wall's level; a route goes by the doors and costs, for each door, room centre to
     the door to room centre (an estimate: true walking distances are I3's). A room on an open region is left out as
     missing, never measured; a door off its wall (its cut failed) is left out with a warning. */
  var BIM_INT_SHARED_TOL=0.5;
  /* the building the programme belongs to: the given one, else the active one */
  function bimIntBuilding(id){
    var L=bimEnsureBuildings(),i,want=id||A3D.activeBuilding;
    for(i=0;i<L.length;i++)if(L[i].id===want)return L[i];
    return L[0]||null;
  }
  /* the building's programme, read as the pure part reads it; nothing is written unless asked */
  function bimIntProgOf(b){
    var p=b&&b.programme&&typeof b.programme==='object'?b.programme:{},items=[],rels=[],i,it,r;
    for(i=0;i<(Array.isArray(p.items)?p.items.length:0);i++){it=bimIntProgramItem(p.items[i]);if(it.id)items.push(it);}
    for(i=0;i<(Array.isArray(p.relations)?p.relations.length:0);i++){r=bimIntRelation(p.relations[i]);if(r)rels.push(r);}
    return {items:items,relations:rels};
  }
  function bimIntRoomUse(o){
    var u=o&&o.usage?bimUsageById(o.usage):null,s=u&&u.name?u.name:(o&&typeof o.name==='string'?o.name:'');
    return String(s).replace(/^\s+|\s+$/g,'');
  }
  function bimIntLevelsOf(bid){
    var out={},i;
    for(i=0;i<A3D.levels.length;i++)if(A3D.levels[i].buildingId===bid)out[A3D.levels[i].id]=1;
    return out;
  }
  /* the building's rooms as facts, and the rooms left out with why */
  function bimIntLiveRooms(bid){
    var lv=bimIntLevelsOf(bid),rooms=[],missing=[],i,o,q,pts,j;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(!o||o.t!=='room'||!lv[o.levelId])continue;
      if(o.region&&o.region.open){missing.push({id:o.id,name:o.name,why:'its outline is not enclosed'});continue;}
      if(!Array.isArray(o.pts)||o.pts.length<3){missing.push({id:o.id,name:o.name,why:'it has no outline'});continue;}
      q=bimObjOffset(o);pts=[];
      for(j=0;j<o.pts.length;j++)pts.push([o.pts[j][0]+q[0],o.pts[j][1]+q[2]]);
      rooms.push({id:o.id,name:o.name,use:bimIntRoomUse(o),area:(typeof o.area==='number'&&isFinite(o.area))?o.area:null,pts:pts,levelId:o.levelId});
    }
    return {rooms:rooms,missing:missing};
  }
  /* the building's doors, in world plan points, and those left out with why */
  function bimIntLiveDoors(bid){
    var lv=bimIntLevelsOf(bid),doors=[],left=[],i,o,w,q,seg;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(!o||o.t!=='opening'||!o.bim||o.bim.type!=='door')continue;
      w=objById(o.bim.hostWallId);
      if(!w||!w.bim||!lv[w.bim.levelId])continue;
      if(!Array.isArray(o.bim.center)||!Array.isArray(o.bim.dir)){left.push({id:o.id,name:o.name,why:'it has no recorded position'});continue;}
      seg=bimFindWallSegmentAt(w,o.bim.center);
      if(!seg||seg.d>BIM_OPENING_REPLACE_TOL*10){left.push({id:o.id,name:o.name,why:'it is no longer cut into '+(w.name||'its wall')});continue;}
      q=bimObjOffset(w);
      doors.push({id:o.id,center:[o.bim.center[0]+q[0],o.bim.center[1]+q[2]],dir:o.bim.dir.slice(),width:o.bim.width,levelId:w.bim.levelId});
    }
    return {doors:doors,left:left};
  }
  function bimIntCentroid(pts){
    var x=0,z=0,i,n=pts?pts.length:0;
    if(!n)return null;
    for(i=0;i<n;i++){x+=pts[i][0];z+=pts[i][1];}
    return [x/n,z/n];
  }
  /* the facts for bimIntCheck, by use, from rooms {id, use, pts, levelId} and doors {id, center, dir, width,
     levelId}. Pure. Answers {facts, links, cost}: facts.rooms the uses with a room; facts.shared and facts.doors
     under 'useA|useB' (each pair of different uses on one level, summed); facts.dist[useA][useB] the shortest
     route from any room of one to any room of the other. The outside of each level is its own place. */
  function bimIntFactsFrom(rooms,doors,tol){
    var facts={rooms:{},shared:{},doors:{},dist:{}},links=[],cost={},byLv={},useOf={},cen={},i,j,k,a,b,key,L,lv,ra,rb,d,c,lk,u;
    tol=(typeof tol==='number'&&tol>=0)?tol:BIM_INT_SHARED_TOL;
    rooms=rooms||[];doors=doors||[];
    for(i=0;i<rooms.length;i++){
      a=rooms[i];
      if(!a||!a.id||!a.use)continue;
      facts.rooms[a.use]=1;useOf[a.id]=a.use;cen[a.id]=bimIntCentroid(a.pts);
      lv=String(a.levelId||'');
      if(!byLv[lv])byLv[lv]={rooms:[],doors:[]};
      byLv[lv].rooms.push(a);
    }
    for(i=0;i<doors.length;i++){
      lv=String(doors[i].levelId||'');
      if(byLv[lv])byLv[lv].doors.push(doors[i]);
    }
    function dd(p,q){return (p&&q)?Math.sqrt((p[0]-q[0])*(p[0]-q[0])+(p[1]-q[1])*(p[1]-q[1])):0;}
    for(lv in byLv){
      if(!byLv.hasOwnProperty(lv))continue;
      L=byLv[lv];
      for(i=0;i<L.rooms.length;i++)for(j=i+1;j<L.rooms.length;j++){
        ra=L.rooms[i];rb=L.rooms[j];
        if(ra.use===rb.use)continue;
        d=bimIntSharedLength(ra.pts,rb.pts,tol);
        if(!(d>1e-9))continue;
        key=ra.use<rb.use?ra.use+'|'+rb.use:rb.use+'|'+ra.use;
        facts.shared[key]=(facts.shared[key]||0)+d;
      }
      lk=bimIntDoorLinks(L.rooms,L.doors);
      for(k=0;k<lk.length;k++){
        if(lk[k].a==='outside')lk[k].a='outside@'+lv;
        if(lk[k].b==='outside')lk[k].b='outside@'+lv;
        for(j=0;j<L.doors.length;j++)if(L.doors[j].id===lk[k].door){
          c=L.doors[j].center;
          cost[lk[k].door]=dd(cen[lk[k].a],c)+dd(c,cen[lk[k].b]);
        }
        links.push(lk[k]);
        if(useOf[lk[k].a]&&useOf[lk[k].b]&&useOf[lk[k].a]!==useOf[lk[k].b]){
          key=useOf[lk[k].a]<useOf[lk[k].b]?useOf[lk[k].a]+'|'+useOf[lk[k].b]:useOf[lk[k].b]+'|'+useOf[lk[k].a];
          facts.doors[key]=(facts.doors[key]||0)+1;
        }
      }
    }
    for(i=0;i<rooms.length;i++){
      a=rooms[i];
      if(!a||!a.id||!a.use)continue;
      d=bimIntDistances(links,a.id,cost);
      for(k in d){
        if(!d.hasOwnProperty(k)||!useOf[k]||useOf[k]===a.use)continue;
        u=useOf[k];
        if(!facts.dist[a.use])facts.dist[a.use]={};
        if(facts.dist[a.use][u]===undefined||d[k]<facts.dist[a.use][u])facts.dist[a.use][u]=d[k];
      }
    }
    return {facts:facts,links:links,cost:cost};
  }
  /* the programme against the model: each item matched, each relation checked, and what was left out */
  function bimIntReport(bid){
    var b=bimIntBuilding(bid),P=bimIntProgOf(b),R,D,F,warn=[],i;
    if(!b)return {building:null,items:[],relations:[],matches:[],checks:[],rooms:[],warnings:[]};
    R=bimIntLiveRooms(b.id);D=bimIntLiveDoors(b.id);
    F=bimIntFactsFrom(R.rooms,D.doors,BIM_INT_SHARED_TOL);
    for(i=0;i<R.missing.length;i++)warn.push((R.missing[i].name||'A room')+' is left out: '+R.missing[i].why);
    for(i=0;i<D.left.length;i++)warn.push((D.left[i].name||'A door')+' is left out: '+D.left[i].why);
    return {building:b,items:P.items,relations:P.relations,rooms:R.rooms,facts:F.facts,warnings:warn,
      matches:bimIntMatch(P.items,R.rooms),
      checks:P.relations.map(function(r){return bimIntCheck(r,F.facts);})};
  }
  /* a door left out is said once per change of the model, not on every render */
  var A3D_INT_WARNED={};
  function bimIntWarnOnce(list){
    var i;
    for(i=0;i<list.length;i++)if(!A3D_INT_WARNED[list[i]]){A3D_INT_WARNED[list[i]]=1;console.warn('[BIM] Programme: '+list[i]);}
  }
  /* ---- WO-11: the bubble diagram, laid out. Pure: circles {use, r} by area, relations as springs, a fixed number
     of steps from a fixed start, so the same programme draws the same diagram. Answers [{x, y, r}] in item order. */
  function bimIntBubbleLayout(items,relations){
    var n=items?items.length:0,P=[],i,j,k,a,b,dx,dy,d,want,f,ix={},R0=0,step;
    for(i=0;i<n;i++){ix[items[i].use]=i;R0+=items[i].r;}
    R0=Math.max(R0/Math.max(1,Math.PI),1);
    for(i=0;i<n;i++)P.push({x:R0*Math.cos(2*Math.PI*i/Math.max(1,n)),y:R0*Math.sin(2*Math.PI*i/Math.max(1,n)),r:items[i].r});
    for(k=0;k<300;k++){
      step=0.1*(1-k/300);
      for(j=0;j<(relations?relations.length:0);j++){
        a=ix[relations[j].a];b=ix[relations[j].b];
        if(a===undefined||b===undefined||a===b)continue;
        dx=P[b].x-P[a].x;dy=P[b].y-P[a].y;d=Math.sqrt(dx*dx+dy*dy)||1e-6;
        want=P[a].r+P[b].r+(relations[j].rel==='apart'?R0:(relations[j].rel==='near'?0.25*R0:0.05*R0));
        if(relations[j].rel==='apart'&&d>=want)continue;
        f=step*(d-want)/d*0.5;
        P[a].x+=dx*f;P[a].y+=dy*f;P[b].x-=dx*f;P[b].y-=dy*f;
      }
      for(i=0;i<n;i++)for(j=i+1;j<n;j++){
        dx=P[j].x-P[i].x;dy=P[j].y-P[i].y;d=Math.sqrt(dx*dx+dy*dy);
        want=P[i].r+P[j].r+0.04*R0;
        if(d>=want)continue;
        if(d<1e-9){dx=1;dy=0;d=1;}
        f=(want-d)/d*0.5;
        P[i].x-=dx*f;P[i].y-=dy*f;P[j].x+=dx*f;P[j].y+=dy*f;
      }
    }
    return P;
  }
  /* the circle's area: the count by the middle of the range (or the end that is set), else the rooms measured */
  function bimIntBubbleArea(it,m,rooms){
    var per=(it.areaMin!==null&&it.areaMax!==null)?(it.areaMin+it.areaMax)/2:(it.areaMin!==null?it.areaMin:it.areaMax),s=0,i,j;
    if(per!==null&&per>0)return {area:per*it.count,set:true};
    for(i=0;m&&i<m.rooms.length;i++)for(j=0;j<rooms.length;j++)if(rooms[j].id===m.rooms[i]&&rooms[j].area>0)s+=rooms[j].area;
    return {area:s>0?s:10*it.count,set:false};
  }
  var BIM_INT_COLS={'met':'#2f7d3a','not met':'#c0392b','not evaluated':'#8a8f98'};
  function bimIntBubbleSvg(rep,narrow){
    var W=narrow?360:640,H=narrow?300:380,pad=18,items=[],i,P,minX=1e9,maxX=-1e9,minY=1e9,maxY=-1e9,s,ox,oy,h='',r,c,a,b,ia,ib,ix={},ar,st;
    for(i=0;i<rep.items.length;i++){
      ar=bimIntBubbleArea(rep.items[i],rep.matches[i],rep.rooms);
      items.push({use:rep.items[i].use,r:Math.sqrt(ar.area/Math.PI),set:ar.set,st:rep.matches[i]?rep.matches[i].status:'ok'});
      ix[rep.items[i].use]=i;
    }
    var rels=rep.relations.filter(function(x){return x.status!=='rejected';});
    P=bimIntBubbleLayout(items,rels);
    for(i=0;i<P.length;i++){minX=Math.min(minX,P[i].x-P[i].r);maxX=Math.max(maxX,P[i].x+P[i].r);minY=Math.min(minY,P[i].y-P[i].r);maxY=Math.max(maxY,P[i].y+P[i].r);}
    s=Math.min((W-2*pad)/Math.max(maxX-minX,1e-6),(H-2*pad)/Math.max(maxY-minY,1e-6));
    ox=pad+((W-2*pad)-(maxX-minX)*s)/2-minX*s;oy=pad+((H-2*pad)-(maxY-minY)*s)/2-minY*s;
    for(i=0;i<rep.relations.length;i++){
      r=rep.relations[i];
      if(r.status==='rejected')continue;
      ia=ix[r.a];ib=ix[r.b];
      if(ia===undefined||ib===undefined)continue;
      st=rep.checks[i].status;c=BIM_INT_COLS[st]||BIM_INT_COLS['not evaluated'];
      a=P[ia];b=P[ib];
      h+='<line x1="'+(a.x*s+ox).toFixed(1)+'" y1="'+(a.y*s+oy).toFixed(1)+'" x2="'+(b.x*s+ox).toFixed(1)+'" y2="'+(b.y*s+oy).toFixed(1)+'" stroke="'+c+'" stroke-width="'+(4-r.strength)+'"'+
        (st==='not evaluated'||r.status==='suggested'?' stroke-dasharray="5 4"':'')+'><title>'+bimClbE(r.a+' '+r.rel+' '+r.b+': '+st+', '+rep.checks[i].why)+'</title></line>';
    }
    for(i=0;i<P.length;i++){
      c=items[i].st==='ok'?'#3b6ea5':'#c98a1b';
      h+='<g><circle cx="'+(P[i].x*s+ox).toFixed(1)+'" cy="'+(P[i].y*s+oy).toFixed(1)+'" r="'+Math.max(3,P[i].r*s).toFixed(1)+'" fill="'+c+'" fill-opacity="0.18" stroke="'+c+'" stroke-width="1.5"'+
        (items[i].set?'':' stroke-dasharray="4 3"')+'><title>'+bimClbE(items[i].use+': '+items[i].st)+'</title></circle>'+
        '<text x="'+(P[i].x*s+ox).toFixed(1)+'" y="'+(P[i].y*s+oy+4).toFixed(1)+'" text-anchor="middle" font-size="'+(narrow?11:12)+'" fill="#1f2328">'+bimClbE(items[i].use)+'</text></g>';
    }
    return '<svg class="a3d-int-bub" viewBox="0 0 '+W+' '+H+'" width="100%" role="img" aria-label="Programme bubble diagram">'+h+'</svg>';
  }
  /* the board figure 'int.bubble': null without a programme */
  function bimIntBubbleFig(){
    var rep=bimIntReport(),n={met:0,'not met':0,'not evaluated':0},i,leg='';
    if(!rep.building||!rep.items.length)return null;
    for(i=0;i<rep.checks.length;i++)if(rep.relations[i].status!=='rejected')n[rep.checks[i].status]=(n[rep.checks[i].status]||0)+1;
    leg='<p class="a3d-clb-dek">'+['met','not met','not evaluated'].map(function(k){
      return '<span style="display:inline-block;width:18px;height:3px;vertical-align:middle;margin:0 4px 0 10px;background:'+BIM_INT_COLS[k]+'"></span>'+bimClbE(k+' '+n[k]);
    }).join('')+'. Circles by area; dashed where no area is set. Amber: count or area not as programmed.</p>';
    return {cls:['a3d-int-fig'],title:'Programme and adjacency',
      dek:(rep.building.name||'The building')+': '+rep.items.length+' use'+(rep.items.length===1?'':'s')+', '+rep.relations.length+' relation'+(rep.relations.length===1?'':'s')+', '+rep.rooms.length+' room'+(rep.rooms.length===1?'':'s')+' drawn',
      body:bimIntBubbleSvg(rep,!!A3D_CLB.narrow)+leg,
      src:'the project\'s programme and the rooms drawn; routes by the doors, room centre to centre, an estimate'};
  }
export { bimIntBubbleFig, bimIntBuilding, bimIntProgOf, bimIntReport, bimIntWarnOnce };
