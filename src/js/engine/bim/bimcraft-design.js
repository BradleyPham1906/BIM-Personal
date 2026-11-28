import { A3D } from '../core/state.js';
import { pushUndo } from '../drawing/plan-mode-sketch.js';
import { bimEsc } from '../layers/layer-manager.js';
import { bimLbBase } from '../ladybug/runtime.js';
import { bimIfcImportBuffer, bimIfcLoad } from '../io/ifc-full.js';
import { a3dToast } from './csg-booleans.js';

/* ================= __acad3dV308: DESIGN, building design on BimCraft's authoring core =================
   The owner, 2026-11-28: "we need to update to bridge the gap for BIM design features like revit ... copy their code,
   reuse the codes, dont write new stuff". docs/research/research-bimcraft-gap/ (walls, views, families, architecture).
   BimCraft's core (vendor/bimcraft, Apache-2.0, unchanged; runtime/bimcraft/<rev>/bim-craft.min.js, global BIMCRAFT,
   loaded on demand) does the work: compound walls by type that join, doors and windows by type cut into them, floors,
   ceilings and roofs by room, rooms with numbers and areas, section lines, its live plan view (PlanView: cut walls in
   their layers, door swings, window symbols), and the drawing set (plan, elevations, sections and schedules on sheets with
   title blocks, PDF), on an IFC model with undo. This file is only the panel around it and the meeting with the app: the
   building starts from the app's levels, and Send to model brings it in through the app's IFC import (io/ifc-full.js), so
   it lands as the app's elements with their GlobalIds, storeys and property sets. Lengths here are BimCraft's: millimetres,
   plan x right and y up. */
var BIM_CRAFT={rev:'79b603f6',dir:'bimcraft/79b603f6/',file:'bim-craft.min.js',global:'BIMCRAFT',
  sri:'sha256-z/vpKH8dV+8ooAEnzdTu/aVpcy2o1eQ8xqTsOjZ+wTc=',snapMm:600};
var A3D_DSN={open:false,el:null,C:null,M:null,ed:null,pv:null,level:null,tool:'select',pts:[],load:null,st:'',fitted:false,
  wallType:'ext-300',doorType:'door-single',winType:'win-double-hung',keys:null,name:'Building'};
var BIM_DSN_TOOLS={select:'Select',wall:'Wall',door:'Door',window:'Window',floor:'Floor',ceiling:'Ceiling',roof:'Roof',section:'Section'};

/* ---- pure helpers (tests/unit/bimcraft-design.test.mjs) ---- */
/* BimCraft's levels from the app's: count, the floor-to-floor height in mm (the first level's height, 3000 when it has
   none) and each name; at least one */
function bimDsnLevelsSpec(levels){
  var L=(levels||[]).slice().sort(function(a,b){return (+a.elev||0)-(+b.elev||0);}),h=3000,names=[],i;
  if(L.length&&isFinite(+L[0].height)&&+L[0].height>0)h=Math.round(+L[0].height*1000);
  for(i=0;i<L.length;i++)names.push(String(L[i].name||('Level '+i)));
  if(!names.length)names.push('Ground floor');
  return {count:names.length,height:h,names:names};
}
/* the clicks of the wall tool as BimCraft's segments [{a, b}]: repeated points (a double-click) dropped, closed into a
   ring when the last point is within tol mm of the first */
function bimDsnWallSegs(pts,tol){
  var P=[],i,a,b,out=[];
  tol=tol>0?tol:1;
  for(i=0;i<(pts||[]).length;i++){
    a=pts[i];if(!a||a.length<2||!isFinite(a[0])||!isFinite(a[1]))continue;
    b=P[P.length-1];
    if(!b||Math.abs(a[0]-b[0])>tol||Math.abs(a[1]-b[1])>tol)P.push([+a[0],+a[1]]);
  }
  var ring=P.length>3&&Math.abs(P[0][0]-P[P.length-1][0])<=tol*100&&Math.abs(P[0][1]-P[P.length-1][1])<=tol*100;
  if(ring)P[P.length-1]=P[0].slice();
  for(i=1;i<P.length;i++)out.push({a:P[i-1],b:P[i]});
  return out;
}
/* the wall a click on the plan means: the nearest wall of the level within maxD mm of p, and where along it; null for
   none. walls [{guid, a, b}] in plan mm */
function bimDsnWallAt(walls,p,maxD){
  var best=null,i,w,dx,dy,L2,t,qx,qy,d;
  for(i=0;i<(walls||[]).length;i++){
    w=walls[i];dx=w.b[0]-w.a[0];dy=w.b[1]-w.a[1];L2=dx*dx+dy*dy;if(!(L2>0))continue;
    t=((p[0]-w.a[0])*dx+(p[1]-w.a[1])*dy)/L2;t=Math.max(0,Math.min(1,t));
    qx=w.a[0]+dx*t;qy=w.a[1]+dy*t;d=Math.sqrt((p[0]-qx)*(p[0]-qx)+(p[1]-qy)*(p[1]-qy));
    if(d<=maxD&&(!best||d<best.d))best={guid:w.guid,offset:t*Math.sqrt(L2),d:d,t:t};
  }
  return best;
}
/* the next section line's name: A, B, ... Z, then AA, AB ... after the names in use */
function bimDsnNextSection(names){
  var used={},i,n,s;
  for(i=0;i<(names||[]).length;i++)used[String(names[i])]=true;
  for(n=0;n<702;n++){
    s=n<26?String.fromCharCode(65+n):String.fromCharCode(64+Math.floor(n/26))+String.fromCharCode(65+n%26);
    if(!used[s])return s;
  }
  return 'S'+(names||[]).length;
}

/* ---- the runtime ---- */
function bimDsnSources(protocol,base){
  var p=String(protocol||''),out=[];
  if(p!=='http:'&&p!=='https:')out.push({u:'runtime/'+BIM_CRAFT.dir+BIM_CRAFT.file,sri:false});
  out.push({u:String(base)+BIM_CRAFT.dir+BIM_CRAFT.file,sri:true});
  return out;
}
/* BimCraft's core, and Manifold from the app's IFC runtime (the same 3.5.4 BimCraft pins): a promise of {C, M} */
function bimDsnLoad(){
  var D=A3D_DSN;
  if(D.load)return D.load;
  D.st='loading';
  /* Manifold (openings cut in the 3D meshes) from the app's IFC runtime over http; from a file:// page the browser refuses
     its WebAssembly, and nothing Design draws needs it (the plan, the drawing set and Send to model: e05, file://) */
  var web=/^https?:$/.test(String(window.location&&window.location.protocol||''));
  D.load=(web?bimIfcLoad().then(null,function(e){console.warn('[BIM] Design: Manifold could not be had; openings are not cut in 3D',e);return {M:null};}):Promise.resolve({M:null})).then(function(R){
    D.M=R&&R.M||null;
    if(window[BIM_CRAFT.global])return window[BIM_CRAFT.global];
    var src=bimDsnSources(window.location&&window.location.protocol,bimLbBase()),i=0;
    return new Promise(function(res,rej){
      function next(){
        if(i>=src.length){rej(new Error('the design engine could not be loaded from '+src.map(function(s){return s.u;}).join(' or ')));return;}
        var s=src[i++],tag=document.createElement('script');
        tag.src=s.u;
        if(s.sri){tag.integrity=BIM_CRAFT.sri;tag.crossOrigin='anonymous';}
        tag.onload=function(){if(window[BIM_CRAFT.global])res(window[BIM_CRAFT.global]);else next();};
        tag.onerror=function(){if(tag.parentNode)tag.parentNode.removeChild(tag);next();};
        document.head.appendChild(tag);
      }
      next();
    });
  }).then(function(C){D.C=C;D.st='ready';return D;},function(e){D.st='failed';D.load=null;throw e;});
  return D.load;
}
/* a BimCraft IFC model and editor on the given bytes (their engine meshes on the page, as their tests run it) */
function bimDsnEditor(bytes){
  var D=A3D_DSN,C=D.C;
  window.ccIfcGeoWorker=false;
  return C.ifcModel.IfcModel.create(C.ifc,null,D.M?{manifold:D.M}:undefined).then(function(eng){
    return Promise.resolve(eng.load(bytes,function(){},{worker:false})).then(function(model){
      return {eng:eng,model:model,ed:new C.ifcEdit.IfcEditor(C.ifc,eng)};
    });
  });
}
/* a new building on the app's levels */
function bimDsnNew(){
  var D=A3D_DSN,C=D.C,spec=bimDsnLevelsSpec(A3D.levels);
  var text=C.newModel.newBuilding({name:D.name,siteName:'Site',levels:C.newModel.stackLevels(spec.count,spec.height,function(i){return spec.names[i]||('Level '+i);}),
    fileName:D.name+'.ifc',now:new Date()});
  return bimDsnEditor(new TextEncoder().encode(text)).then(function(S){D.ed=S.ed;D.level=null;D.fitted=false;bimDsnRefresh();return S;});
}
function bimDsnSnap(){return A3D_DSN.C.modelOps.snapshotModel(A3D_DSN.ed);}
function bimDsnLevel(snap){
  var D=A3D_DSN,L=snap.levels,i;
  for(i=0;i<L.length;i++)if(L[i].guid===D.level)return L[i];
  D.level=L.length?L[0].guid:null;
  return L[0]||null;
}
/* the plan of the level: BimCraft's own scene (plan-export.js planSceneOf), with its rooms labelled */
function bimDsnScene(snap,lv){
  var C=A3D_DSN.C,scene=C.planExport.planSceneOf(snap,lv.id),loops={},i,r,sp;
  try{loops=C.modelOps.loopsOf(A3D_DSN.ed,lv.id)||{};}catch(eL){loops={};}
  var rooms=loops.rooms||[],spaces=(snap.derived&&snap.derived.spaces||[]).filter(function(s){return s.storey===lv.id;});
  scene.rooms=[];
  for(i=0;i<rooms.length;i++){
    r=rooms[i];var poly=r.poly||r.ring||r.loop||null;if(!poly)continue;
    sp=null;
    for(var k=0;k<spaces.length;k++)if(spaces[k].seed&&C.planExport&&bimDsnInside(poly,spaces[k].seed))sp=spaces[k];
    var at=sp?sp.seed:bimDsnCentre(poly);
    scene.rooms.push({key:'room-'+i,poly:poly,at:at,label:[(sp?(sp.number+' '+sp.name).trim():'Room'),(Math.round(r.area/1e4)/100)+' m2']});
  }
  return scene;
}
function bimDsnInside(poly,p){
  var c=false,i,j,n=poly.length,xi,yi,xj,yj;
  for(i=0,j=n-1;i<n;j=i++){
    xi=poly[i][0];yi=poly[i][1];xj=poly[j][0];yj=poly[j][1];
    if(((yi>p[1])!==(yj>p[1]))&&(p[0]<(xj-xi)*(p[1]-yi)/((yj-yi)||1e-12)+xi))c=!c;
  }
  return c;
}
function bimDsnCentre(poly){var x=0,y=0,i;for(i=0;i<poly.length;i++){x+=poly[i][0];y+=poly[i][1];}return poly.length?[x/poly.length,y/poly.length]:[0,0];}
/* the plan view shown again after a change, and the panel's list */
function bimDsnRefresh(){
  var D=A3D_DSN;
  if(!D.ed||!D.pv)return;
  var snap=bimDsnSnap(),lv=bimDsnLevel(snap);
  if(!lv)return;
  D.pv.setScene(bimDsnScene(snap,lv));
  if(!D.fitted&&snap.walls.length){D.pv.fit();D.fitted=true;}
  D.pv.render();
  bimDsnSide(snap,lv);
}
function bimDsnSide(snap,lv){
  var D=A3D_DSN,s=D.el&&D.el.querySelector('.a3d-dsn-side');
  if(!s)return;
  var sel=D.el.querySelector('[data-dsnlevel]');
  if(sel){sel.innerHTML=snap.levels.map(function(l){return '<option value="'+bimEsc(l.guid)+'"'+(l.guid===lv.guid?' selected':'')+'>'+bimEsc(l.name)+'</option>';}).join('');}
  var ops=snap.openings||[],sp=(snap.derived&&snap.derived.spaces)||[];
  function table(title,head,rows){
    return '<details open><summary>'+bimEsc(title)+' <span>'+rows.length+'</span></summary><table><tr>'+head.map(function(h){return '<th>'+bimEsc(h)+'</th>';}).join('')+'</tr>'+
      rows.map(function(r){return '<tr>'+r.map(function(c){return '<td>'+bimEsc(c)+'</td>';}).join('')+'</tr>';}).join('')+'</table></details>';
  }
  s.innerHTML=table('Walls',['Type','Length m'],snap.walls.filter(function(w){return w.storey===lv.id;}).map(function(w){return [w.typeKey||'',(w.len/1000).toFixed(2)];}))+
    table('Doors',['Mark','Type','Size'],ops.filter(function(o){return o.kind==='door';}).map(function(o){return [o.mark||'',o.typeName||'',o.sizeName||''];}))+
    table('Windows',['Mark','Type','Size'],ops.filter(function(o){return o.kind==='window';}).map(function(o){return [o.mark||'',o.typeName||'',o.sizeName||''];}))+
    table('Rooms',['Number','Name'],sp.map(function(r){return [r.number||'',r.name||''];}));
}
function bimDsnStatus(t){var s=A3D_DSN.el&&A3D_DSN.el.querySelector('.a3d-rvw-status');if(s)s.textContent=String(t||'');}
/* one change through BimCraft's editor (one undo step); a refusal said, not thrown */
function bimDsnChange(op,what){
  var D=A3D_DSN;
  try{D.ed.modelChange(op);}catch(e){
    var s=String(e&&(e.key||e.message)||e);
    bimDsnStatus(what+' could not be made: '+s);console.warn('[BIM] Design: '+what,e);return false;
  }
  bimDsnRefresh();
  return true;
}

/* ---- the tools ---- */
function bimDsnClick(pt){
  var D=A3D_DSN,C=D.C,OPS=C.modelOps,snap,lv,w;
  if(!D.ed)return;
  snap=bimDsnSnap();lv=bimDsnLevel(snap);if(!lv)return;
  var walls=snap.walls.filter(function(x){return x.storey===lv.id;});
  if(D.tool==='wall'){D.pts.push([pt[0],pt[1]]);bimDsnOverlay();bimDsnStatus('Wall: click the next corner; double-click or Enter ends it; Escape drops it');return;}
  if(D.tool==='section'){
    D.pts.push([pt[0],pt[1]]);
    if(D.pts.length<2){bimDsnStatus('Section: click where the line ends');bimDsnOverlay();return;}
    var name=bimDsnNextSection(C.resSheets.readSectionLines(new C.modelWrite.ModelWriter(C.ifc,D.ed.api,D.ed.mid)).map(function(x){return x.name;}));
    if(bimDsnChange(C.resSheets.placeSectionLine({level:lv.guid,a:D.pts[0],b:D.pts[1],name:name}),'The section line'))bimDsnStatus('Section '+name+' placed');
    D.pts=[];bimDsnOverlay();return;
  }
  if(D.tool==='door'||D.tool==='window'){
    w=bimDsnWallAt(walls,pt,BIM_CRAFT.snapMm);
    if(!w){bimDsnStatus('Click on a wall to place a '+D.tool);return;}
    if(bimDsnChange(OPS.placeOpening({wall:w.guid,typeKey:D.tool==='door'?D.doorType:D.winType,offset:w.offset,face:'right'}),'The '+D.tool))
      bimDsnStatus((D.tool==='door'?'Door ':'Window ')+'placed; its mark and size are in the list');
    return;
  }
  if(D.tool==='floor'||D.tool==='ceiling'){
    var f=D.tool==='floor'?OPS.placeFloor:OPS.placeCeiling;
    if(bimDsnChange(f({storey:lv.guid,seed:pt,mode:'room'}),'The '+D.tool))bimDsnStatus((D.tool==='floor'?'Floor':'Ceiling')+' placed in the room clicked; the room is listed');
    return;
  }
  if(D.tool==='roof'){
    if(bimDsnChange(OPS.placeRoof({storey:lv.guid,seed:pt,pitch:30,overhang:300,edges:''}),'The roof'))bimDsnStatus('Roof placed over the walls round the point clicked (30 degrees, 300 mm overhang)');
  }
}
function bimDsnFinishWall(){
  var D=A3D_DSN,C=D.C,segs=bimDsnWallSegs(D.pts,1),snap,lv;
  D.pts=[];bimDsnOverlay();
  if(!segs.length){bimDsnStatus('A wall needs two corners');return;}
  snap=bimDsnSnap();lv=bimDsnLevel(snap);
  if(bimDsnChange(C.modelOps.drawWalls({storey:lv.guid,segs:segs,typeKey:D.wallType,extSide:'right'}),'The wall'))
    bimDsnStatus(segs.length+' wall'+(segs.length===1?'':'s')+' of type '+D.wallType+', joined at their corners');
}
function bimDsnOverlay(pt){
  var D=A3D_DSN,P=D.pts.slice(),lines=[],i;
  if(!D.pv)return;
  if(pt&&P.length)P.push(pt);
  for(i=1;i<P.length;i++)lines.push([P[i-1][0],P[i-1][1],P[i][0],P[i][1]]);
  D.pv.setOverlay(lines.length||P.length?{lines:lines,points:D.pts.slice(),dashed:D.tool==='section'}:null);
  D.pv.render();
}
function bimDsnTool(t){
  var D=A3D_DSN,b,i;
  D.tool=BIM_DSN_TOOLS.hasOwnProperty(t)?t:'select';D.pts=[];bimDsnOverlay();
  b=D.el.querySelectorAll('[data-dsntool]');
  for(i=0;i<b.length;i++)b[i].classList.toggle('on',b[i].getAttribute('data-dsntool')===D.tool);
  bimDsnStatus({select:'Select: pan by dragging, zoom with the wheel or two fingers',wall:'Wall ('+D.wallType+'): click its corners',
    door:'Door ('+D.doorType+'): click on a wall',window:'Window ('+D.winType+'): click on a wall',floor:'Floor: click inside a room',
    ceiling:'Ceiling: click inside a room',roof:'Roof: click inside the walls it covers',section:'Section: click where the line starts'}[D.tool]);
}

/* ---- the drawing set, the files, and sending the building to the model ---- */
function bimDsnSave(bytes,name,type){
  var a=document.createElement('a'),u=URL.createObjectURL(new Blob([bytes],{type:type}));
  a.href=u;a.download=name;document.body.appendChild(a);a.click();
  setTimeout(function(){URL.revokeObjectURL(u);if(a.parentNode)a.parentNode.removeChild(a);},1000);
}
/* the drawing set as BimCraft's test house makes it: each level's plan, the four elevations, a section per section line,
   the door and window schedules, on A1 sheets with title blocks, as one PDF */
function bimDsnDrawingSet(){
  var D=A3D_DSN,C=D.C,bytes=D.ed.save();
  bimDsnStatus('Making the drawing set...');
  return bimDsnEditor(bytes).then(function(S){
    var snap=C.modelOps.snapshotModel(S.ed),w=new C.modelWrite.ModelWriter(C.ifc,S.ed.api,S.ed.mid),V=C.resViews,SH=C.resSheets,MG=C.modelGrids;
    var g=snap.levels[0],M=C.modelPlan.viewerToPlan(S.eng.api.GetCoordinationMatrix(S.model.modelID),w.storeyWorld(g.id));
    var els=V.modelTriangles(S.model,M),axes=MG.toPlan(w,g.id,MG.readGrids(w)).flatMap(function(x){return x.axes;}),elev=[],k;
    for(k in V.elevationDirs)if(V.elevationDirs.hasOwnProperty(k)){
      var v=V.projectView(els,{dir:V.elevationDirs[k]});v.grids=MG.gridsInView(axes,V.elevationDirs[k]);
      elev.push({ref:k,title:k.charAt(0).toUpperCase()+k.slice(1)+' elevation',view:v});
    }
    var secs=SH.readSectionLines(w).map(function(sl){var sd=SH.sectionDir(sl);return {ref:sl.name,title:'Section '+sl.name,view:V.projectView(els,{dir:sd.dir,cut:{o:sd.o},far:sl.depth})};});
    var ops=snap.openings||[],kind=function(k2){return ops.filter(function(o){return o.kind===k2;});};
    var input={plans:snap.levels.map(function(l,i){return {ref:'p'+i,title:l.name+' plan',scene:C.planExport.planSceneOf(snap,l.id)};}),elevations:elev,sections:secs,
      schedules:[{ref:'doors',title:'Doors',head:['Mark','Type','Size'],rows:kind('door').map(function(o){return [o.mark,o.typeName,o.sizeName];}),total:null},
        {ref:'windows',title:'Windows',head:['Mark','Type','Size'],rows:kind('window').map(function(o){return [o.mark,o.typeName,o.sizeName];}),total:null}]};
    var opts={paper:'a1',units:'mm',project:D.name,date:new Date().toISOString().slice(0,10)};
    var set=SH.buildSet(input,opts),pdf=SH.setPdf(set,{paper:'a1',title:D.name});
    bimDsnSave(pdf,D.name+' drawings.pdf','application/pdf');
    bimDsnStatus('Drawing set: '+set.length+' sheets ('+set.map(function(s){return s.number;}).join(', ')+'), saved as a PDF');
    return {sheets:set.map(function(s){return s.number;}),bytes:pdf.length};
  }).then(null,function(e){bimDsnStatus('The drawing set could not be made: '+String(e&&e.message||e));console.warn('[BIM] Design: drawing set',e);return null;});
}
/* a second Send replaces the first: the elements an earlier send of this building brought in (an imported element
   keeps its file's name, bim.file) go first, as one undo step (research-bimcraft-gap/architecture.md, the plan) */
function bimDsnDropSent(name){
  var keep=[],gone=0,i,o;
  for(i=0;i<A3D.objs.length;i++){o=A3D.objs[i];if(o&&o.bim&&o.bim.imported&&o.bim.file===name)gone++;else keep.push(o);}
  if(!gone)return 0;
  pushUndo();
  A3D.objs=keep;
  return gone;
}
function bimDsnAct(a){
  var D=A3D_DSN;
  if(a==='close'){bimDesignClose();return;}
  if(!D.ed)return;
  if(a==='undo'){try{D.ed.undo();}catch(eU){}bimDsnRefresh();}
  else if(a==='redo'){try{D.ed.redo();}catch(eR){}bimDsnRefresh();}
  else if(a==='fit'&&D.pv){D.pv.fit();D.pv.render();}
  else if(a==='set')bimDsnDrawingSet();
  else if(a==='plan'){
    try{var snap=bimDsnSnap(),lv=bimDsnLevel(snap),r=D.C.planExport.planFile(D.ed,{level:lv.guid,format:'pdf',paper:'a3',name:D.name});
      bimDsnSave(r.bytes,D.name+' '+lv.name+' plan.pdf','application/pdf');bimDsnStatus('Plan of '+lv.name+' saved as a PDF at 1:'+r.scale);}
    catch(eP){bimDsnStatus('The plan could not be saved: '+String(eP&&eP.message||eP));}
  }
  else if(a==='ifc'){bimDsnSave(D.ed.save(),D.name+'.ifc','application/x-step');bimDsnStatus('Saved as IFC');}
  else if(a==='send'){
    var bytes=D.ed.save(),name=D.name+'.ifc',gone=bimDsnDropSent(name);
    bimDsnStatus('Bringing the building into the model'+(gone?' (replacing the '+gone+' elements sent before)':'')+'...');
    bimIfcImportBuffer(bytes,name).then(function(r){a3dToast(r.text);bimDsnStatus('In the model: '+r.ids.length+' elements');},function(e){bimDsnStatus('It could not be brought in: '+String(e&&e.message||e));});
  }
}

/* ---- the panel ---- */
function bimDsnHtml(){
  var t,b='',opt=function(list,sel){return list.map(function(x){return '<option'+(x.key===sel?' selected':'')+'>'+x.key+'</option>';}).join('');},C=A3D_DSN.C;
  for(t in BIM_DSN_TOOLS)if(BIM_DSN_TOOLS.hasOwnProperty(t))b+='<button type="button" data-dsntool="'+t+'">'+BIM_DSN_TOOLS[t]+'</button>';
  return '<div class="a3d-rvw-bar" role="toolbar" aria-label="Design">'+
    '<select data-dsnlevel title="Level"></select>'+b+
    '<select data-dsntype="wall" title="Wall type">'+opt(C.modelWalls.WALL_TYPES,A3D_DSN.wallType)+'</select>'+
    '<select data-dsntype="door" title="Door type">'+opt(C.openingTypes.DOOR_TYPES,A3D_DSN.doorType)+'</select>'+
    '<select data-dsntype="window" title="Window type">'+opt(C.openingTypes.WINDOW_TYPES,A3D_DSN.winType)+'</select>'+
    '<button type="button" data-dsn="undo">Undo</button><button type="button" data-dsn="redo">Redo</button><button type="button" data-dsn="fit">Fit</button>'+
    '<button type="button" data-dsn="plan" title="This level\'s plan as a PDF">Plan PDF</button>'+
    '<button type="button" data-dsn="set" title="Plans, elevations, sections and schedules on sheets, as one PDF">Drawing set</button>'+
    '<button type="button" data-dsn="ifc">Save IFC</button>'+
    '<button type="button" data-dsn="send" title="Bring the building into the app\'s model">Send to model</button>'+
    '<button type="button" data-dsn="close" class="a3d-rvw-close">Close</button></div>'+
    '<div class="a3d-rvw-main"><div class="a3d-rvw-view a3d-dsn-plan"><canvas></canvas></div><div class="a3d-rvw-side a3d-dsn-side"></div></div>'+
    '<div class="a3d-rvw-status" aria-live="polite">Design: BimCraft\'s building tools (Apache-2.0)</div>';
}
function bimDsnWire(){
  var D=A3D_DSN,el=D.el;
  el.addEventListener('click',function(ev){
    var b=ev.target.closest&&ev.target.closest('[data-dsn],[data-dsntool]');
    if(!b)return;
    if(b.hasAttribute('data-dsntool'))bimDsnTool(b.getAttribute('data-dsntool'));else bimDsnAct(b.getAttribute('data-dsn'));
  });
  el.addEventListener('change',function(ev){
    var t=ev.target;
    if(t.hasAttribute('data-dsnlevel')){D.level=t.value;D.pts=[];bimDsnRefresh();}
    else if(t.hasAttribute('data-dsntype')){var k=t.getAttribute('data-dsntype');if(k==='wall')D.wallType=t.value;else if(k==='door')D.doorType=t.value;else D.winType=t.value;bimDsnTool(D.tool);}
  });
  D.keys=function(ev){
    if(!D.open)return;
    if(ev.target&&/^(INPUT|SELECT|TEXTAREA)$/.test(ev.target.tagName))return;
    if(ev.key==='Escape'){if(D.pts.length){D.pts=[];bimDsnOverlay();}else if(D.tool!=='select')bimDsnTool('select');else bimDesignClose();ev.preventDefault();}
    else if(ev.key==='Enter'&&D.tool==='wall'){bimDsnFinishWall();ev.preventDefault();}
    else if((ev.ctrlKey||ev.metaKey)&&ev.key.toLowerCase()==='z'){bimDsnAct(ev.shiftKey?'redo':'undo');ev.preventDefault();}
  };
  document.addEventListener('keydown',D.keys,true);
}
/* DESIGN: the panel over the app, the engine loaded the first time, a new building on the app's levels */
function bimDesignOpen(){
  var D=A3D_DSN;
  if(D.open)return Promise.resolve(true);
  var el=document.createElement('div');
  el.className='a3d-review a3d-design';el.setAttribute('role','dialog');el.setAttribute('aria-label','Design');
  el.innerHTML='<div class="a3d-rvw-status" aria-live="polite">Loading the design engine (about 0.5 MB, once)...</div>';
  document.body.appendChild(el);
  D.el=el;D.open=true;
  return bimDsnLoad().then(function(){
    if(!D.open)return false;
    el.innerHTML=bimDsnHtml();
    bimDsnWire();
    var cv=el.querySelector('.a3d-dsn-plan canvas');
    D.pv=new D.C.modelPlanview.PlanView(cv,{
      click:function(pt){bimDsnClick(pt);},
      dblclick:function(){if(D.tool==='wall')bimDsnFinishWall();},
      move:function(pt){if(D.pts.length)bimDsnOverlay(pt);},
      leave:function(){},contextmenu:function(){}
    });
    D.pv.dragPan=true;
    return bimDsnNew().then(function(){bimDsnTool('wall');return true;});
  }).then(null,function(e){
    var s=String(e&&e.message||e);
    console.warn('[BIM] Design: the engine could not be loaded',e);
    bimDsnStatus('The design engine could not be loaded: '+s);a3dToast('Design: the engine could not be loaded: '+s);
    return false;
  });
}
function bimDesignClose(){
  var D=A3D_DSN;
  if(!D.open)return;
  D.open=false;
  if(D.keys)document.removeEventListener('keydown',D.keys,true);
  try{if(D.pv&&D.pv.ro)D.pv.ro.disconnect();}catch(eR){}
  if(D.el&&D.el.parentNode)D.el.parentNode.removeChild(D.el);
  D.el=null;D.pv=null;D.ed=null;D.pts=[];D.keys=null;D.tool='select';
}
function bimDesignCommand(){if(A3D_DSN.open)bimDesignClose();else bimDesignOpen();}
export { A3D_DSN, bimDesignCommand };
