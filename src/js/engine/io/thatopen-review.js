import { bimEsc } from '../layers/layer-manager.js';
import { bimIfcImportBuffer } from './ifc-full.js';
import {
  bimToeClassName, bimToePotreeMissing, bimToeRange, bimToeRaw, bimToeSets, bimToeStoreyClasses, bimToeVal,
  bimTorArea, bimTorClip
} from './ifc-review.js';
import {
  BIM_TOE, bimToeClassLists, bimToeImporterSetup, bimToeLoad, bimToePotreeLoad
} from './thatopen-runtime.js';
import { a3dToast } from '../bim/csg-booleans.js';

/* ================= __acad3dV206 WO-08: the Review view =================
   docs/research/research-thatopen.md (the owner's choice B, 2026-11-13) and research-thatopen-gap/. One or more IFC
   models looked at as they are, without importing them, in That Open's own world on the app's three.js: fast display
   of large and federated models, picking with their IFC data, section planes, length and area measuring, hiding and
   isolating, and a tree of storeys and classes. Import brings the model under review into the editable model through
   the same reader as File, Import (io/ifc-full.js). It opens over the app, on every screen size, and gives everything
   back when closed. Loaded on demand (io/thatopen-runtime.js): nothing of That Open is fetched until REVIEW. */
var A3D_RVW={open:false,busy:false,el:null,L:null,c:null,world:null,fm:null,hl:null,clip:null,len:null,area:null,hider:null,
  mode:'select',models:[],seq:0,keys:null};
var BIM_RVW_MODES={select:'Select',clip:'Section',length:'Length',area:'Area'};
function bimRvwStatus(t){var R=A3D_RVW,s=R.el&&R.el.querySelector('.a3d-rvw-status');if(s)s.textContent=String(t||'');}
function bimRvwHtml(){
  var m,b='';
  for(m in BIM_RVW_MODES)if(BIM_RVW_MODES.hasOwnProperty(m))b+='<button type="button" data-rvwmode="'+m+'">'+BIM_RVW_MODES[m]+'</button>';
  return '<div class="a3d-rvw-bar" role="toolbar" aria-label="Review">'+
    '<button type="button" data-rvw="open" title="Open one or more IFC files to review">Open IFC</button>'+
    '<button type="button" data-rvw="cloud" title="Open a Potree 2.0 point cloud: choose its metadata.json, hierarchy.bin and octree.bin">Point cloud</button>'+
    '<button type="button" data-rvw="splat" title="Open a Gaussian splat (.ply or .compressed.ply)">Splat</button>'+
    '<button type="button" data-rvw="fit" title="Frame every model">Fit</button>'+b+
    '<button type="button" data-rvw="clear" title="Remove the section planes and measurements">Clear</button>'+
    '<button type="button" data-rvw="hide" title="Hide the selection">Hide</button>'+
    '<button type="button" data-rvw="isolate" title="Show only the selection">Isolate</button>'+
    '<button type="button" data-rvw="show" title="Show everything">Show all</button>'+
    '<button type="button" data-rvw="import" title="Bring the model under review into the editable model">Import</button>'+
    '<button type="button" data-rvw="close" class="a3d-rvw-close" title="Close the Review view">Close</button>'+
    '<input type="file" accept=".ifc" multiple hidden data-rvwfile>'+
    '<input type="file" multiple hidden data-rvwcloud>'+
    '<input type="file" accept=".ply" hidden data-rvwsplat></div>'+
    '<div class="a3d-rvw-main"><div class="a3d-rvw-view" tabindex="0"></div>'+
    '<div class="a3d-rvw-side"><div class="a3d-rvw-tree"><p class="a3d-rvw-hint">Open an IFC file to review it.</p></div>'+
    '<div class="a3d-rvw-props"></div></div></div>'+
    '<div class="a3d-rvw-status" aria-live="polite">Review: That Open Engine (MIT) on web-ifc (MPL-2.0)</div>';
}
/* the world, once per opening: scene, renderer and camera in the view's box; fragments on the classic worker; the tools */
function bimRvwWorld(L){
  var R=A3D_RVW,T=L.T,OBC=L.OBC,OBF=L.OBF,c=new OBC.Components(),view=R.el.querySelector('.a3d-rvw-view');
  var w=c.get(OBC.Worlds).create();
  w.scene=new OBC.SimpleScene(c);w.scene.setup();w.scene.three.background=null;
  /* That Open's PostproductionRenderer (a SimpleRenderer with its passes): point clouds are drawn only in its deferred
     occlusion pass (components-front PointCloudLoader 323-324, 592-598) */
  w.renderer=new OBF.PostproductionRenderer(c,view);
  w.camera=new OBC.OrthoPerspectiveCamera(c);
  c.init();
  var grid=c.get(OBC.Grids).create(w);
  var fm=c.get(OBC.FragmentsManager);
  fm.init(L.worker,{classicWorker:true});
  w.camera.controls.addEventListener('update',function(){fm.core.update();});
  fm.list.onItemSet.add(function(e){e.value.useCamera(w.camera.three);w.scene.three.add(e.value.object);fm.core.update(true);});
  c.get(OBC.Raycasters).get(w);
  var hl=c.get(OBF.Highlighter);
  hl.setup({world:w,selectMaterialDefinition:{color:new T.Color('#3a8fd8'),opacity:1,transparent:false,renderedFaces:0}});
  hl.events.select.onHighlight.add(function(map){bimRvwProps(map);});
  hl.events.select.onClear.add(function(){var p=R.el&&R.el.querySelector('.a3d-rvw-props');if(p)p.innerHTML='';});
  var clip=c.get(OBC.Clipper);clip.enabled=false;
  var len=c.get(OBF.LengthMeasurement);len.world=w;len.enabled=false;len.color=new T.Color('#e8a33a');
  var area=c.get(OBF.AreaMeasurement);area.world=w;area.enabled=false;area.color=new T.Color('#e8a33a');
  area.list.onItemAdded.add(function(a){bimRvwStatus(bimRvwAreaText(a));});
  R.grid=grid;R.deferred=false;
  R.c=c;R.world=w;R.fm=fm;R.hl=hl;R.clip=clip;R.len=len;R.area=area;R.hider=c.get(OBC.Hider);
}
/* an area's readout: That Open's value, checked against the app's own Newell area of the same points (bimTorArea) */
function bimRvwAreaText(a){
  var pts=[];
  try{a.points.forEach(function(p){pts.push([p.x,p.y,p.z]);});}catch(eP){pts=[];}
  var ours=bimTorArea(pts),theirs=+a.value;
  return 'Area: '+(isFinite(theirs)?theirs:ours).toFixed(3)+' m2 ('+pts.length+' points'+
    (isFinite(theirs)&&Math.abs(theirs-ours)>1e-3*Math.max(1,ours)?'; out of plane, the app measures '+ours.toFixed(3):'')+')';
}
/* the picked element's IFC data in the side panel: class, GlobalId, name, storey, then its property and quantity sets */
function bimRvwProps(map){
  var R=A3D_RVW,p=R.el&&R.el.querySelector('.a3d-rvw-props'),mid,id,n=0,k;
  if(!p)return;
  for(k in map)if(map.hasOwnProperty(k)){map[k].forEach(function(x){if(id==null){id=x;mid=k;}n++;});}
  if(id==null){p.innerHTML='';return;}
  var M=R.fm.list.get(mid);
  if(!M)return;
  M.getItemsData([id],{attributesDefault:true,relations:{IsDefinedBy:{attributes:true,relations:true},ContainedInStructure:{attributes:true,relations:false}}})
  .then(function(d){
    var it=d&&d[0]||{},sets=bimToeSets(it),st=(it.ContainedInStructure||[])[0],h='';
    function row(a,b){return '<tr><th>'+bimEsc(a)+'</th><td>'+bimEsc(b)+'</td></tr>';}
    h+='<h4>'+bimEsc(bimToeVal(it.Name)||bimToeClassName(bimToeVal(it._category),bimToeClassLists()))+(n>1?' <small>and '+(n-1)+' more</small>':'')+'</h4>';
    h+='<table>'+row('IFC Class',bimToeClassName(bimToeVal(it._category),bimToeClassLists()))+row('GlobalId',bimToeVal(it._guid))+
      (st?row('Contained in',bimToeVal(st.Name)+' ('+bimToeClassName(bimToeVal(st._category),bimToeClassLists())+')'):'')+row('Model',(bimRvwModel(mid)||{}).name||'')+'</table>';
    sets.forEach(function(s){h+='<details><summary>'+bimEsc(s.name)+'</summary><table>'+s.rows.map(function(r){return row(r[0],r[1]);}).join('')+'</table></details>';});
    p.innerHTML=h;
  },function(e){p.textContent='The element\'s data could not be read: '+String(e&&e.message||e);});
}
function bimRvwModel(mid){var R=A3D_RVW,i;for(i=0;i<R.models.length;i++)if(R.models[i].id===mid)return R.models[i];return null;}
/* the tree of each model: storeys, then classes with their counts; a box shows or hides, a name selects */
function bimRvwTree(){
  var R=A3D_RVW,t=R.el&&R.el.querySelector('.a3d-rvw-tree');
  if(!t)return Promise.resolve();
  if(!R.models.length){t.innerHTML='<p class="a3d-rvw-hint">Open an IFC file to review it.</p>';return Promise.resolve();}
  return Promise.all(R.models.map(function(m){
    return m.model.getSpatialStructure().then(function(root){
      var rows=bimToeStoreyClasses(root),ids=rows.filter(function(r){return r.storey!=null;}).map(function(r){return r.storey;});
      return (ids.length?m.model.getItemsData(ids,{attributesDefault:true}):Promise.resolve([])).then(function(sd){
        var names={};
        (sd||[]).forEach(function(x){names[bimToeRaw(x._localId)]=bimToeVal(x.Name);});
        m.rows=rows;m.names=names;
      });
    });
  })).then(function(){
    var h='',mi,ri,c;
    for(mi=0;mi<R.models.length;mi++){
      var m=R.models[mi];
      h+='<details open><summary><label><input type="checkbox" checked data-rvwvis="'+mi+'"> '+bimEsc(m.name)+'</label></summary>';
      for(ri=0;ri<(m.rows||[]).length;ri++){
        var r=m.rows[ri],nm=r.storey!=null?(m.names[r.storey]||('Storey '+(ri+1))):'Not in a storey';
        h+='<details open><summary><label><input type="checkbox" checked data-rvwvis="'+mi+','+ri+'"> '+bimEsc(nm)+'</label></summary><ul>';
        for(c in r.classes)if(r.classes.hasOwnProperty(c))
          h+='<li><label><input type="checkbox" checked data-rvwvis="'+mi+','+ri+','+bimEsc(c)+'"></label> <button type="button" data-rvwsel="'+mi+','+ri+','+bimEsc(c)+'">'+
            bimEsc(bimToeClassName(c,bimToeClassLists()))+' <span>'+r.classes[c].length+'</span></button></li>';
        h+='</ul></details>';
      }
      h+='</details>';
    }
    t.innerHTML=h;
  });
}
/* a tree key ("model", "model,row" or "model,row,CLASS") as That Open's {modelId: Set of ids} */
function bimRvwMap(key){
  var R=A3D_RVW,k=String(key).split(','),m=R.models[+k[0]],out={},ids=[],ri,c;
  if(!m)return out;
  var rows=k.length>1?[m.rows[+k[1]]]:(m.rows||[]);
  for(ri=0;ri<rows.length;ri++){
    if(!rows[ri])continue;
    for(c in rows[ri].classes)if(rows[ri].classes.hasOwnProperty(c)&&(k.length<3||c===k[2]))ids=ids.concat(rows[ri].classes[c]);
  }
  out[m.id]=new Set(ids);
  return out;
}
function bimRvwMode(mode){
  var R=A3D_RVW,b,i;
  if(!R.c)return;
  if(R.area&&R.area.enabled)try{R.area.cancelCreation();}catch(eA){}
  if(R.len&&R.len.enabled)try{R.len.cancelCreation();}catch(eL){}
  R.mode=BIM_RVW_MODES.hasOwnProperty(mode)?mode:'select';R.lenPts=0;
  R.hl.config.selectEnabled=R.mode==='select';
  R.clip.enabled=R.mode==='clip';
  R.len.enabled=R.mode==='length';
  R.area.enabled=R.mode==='area';
  b=R.el.querySelectorAll('[data-rvwmode]');
  for(i=0;i<b.length;i++)b[i].classList.toggle('on',b[i].getAttribute('data-rvwmode')===R.mode);
  bimRvwStatus({select:'Select: tap an element for its IFC data',clip:'Section: double-click a face to cut there; Delete removes the plane under the pointer',
    length:'Length: double-click two points',area:'Area: double-click the corners, Enter to finish'}[R.mode]);
}
function bimRvwFit(){
  var R=A3D_RVW;
  if(!R.world||!R.models.length)return Promise.resolve();
  return Promise.resolve(R.world.camera.fitToItems()).then(function(){return R.fm.core.update(true);});
}
/* files opened into the review: each read by That Open into a fragments model of its own (nothing enters the project) */
function bimRvwAdd(bytes,name){
  var R=A3D_RVW,L=R.L,ld=R.c.get(L.OBC.IfcLoader),id='review-'+(++R.seq);
  return ld.setup({autoSetWasm:false,wasm:{path:BIM_TOE.wasmUrl.replace(/[^\/]*$/,''),absolute:true}}).then(function(){
    return ld.load(bytes,true,id,{instanceCallback:function(imp){bimToeImporterSetup(imp,false);}});
  }).then(function(model){
    R.models.push({id:id,name:String(name||'model.ifc'),bytes:bytes,model:model});
    return bimRvwTree().then(bimRvwFit);
  });
}
function bimRvwFiles(list){
  var R=A3D_RVW,files=[],i,k=0;
  for(i=0;i<(list||[]).length;i++)files.push(list[i]);
  if(!files.length)return Promise.resolve();
  R.busy=true;
  function next(){
    if(k>=files.length)return Promise.resolve();
    var f=files[k++];
    bimRvwStatus('Reading '+f.name+'...');
    return f.arrayBuffer().then(function(b){return bimRvwAdd(new Uint8Array(b),f.name);}).then(function(){
      bimRvwStatus(f.name+': ready. '+R.models.length+' model'+(R.models.length===1?'':'s')+' under review');
      return next();
    });
  }
  return next().then(function(){R.busy=false;},function(e){
    R.busy=false;
    var s=String(e&&e.message||e);
    bimRvwStatus('The file could not be read: '+s);a3dToast('Review: the file could not be read: '+s);
  });
}
/* the section planes' report: how many of each model's elements have their placement point on the cut-away side
   (bimTorClip). The plane is read from what is drawn (its three.js plane, current after a drag); three.js cuts away
   the side where the signed distance is negative, so bimTorClip is given the opposite normal */
function bimRvwSectionText(){
  var R=A3D_RVW,T=R.L.T,planes=[];
  R.clip.list.forEach(function(pl){
    var P=pl&&pl.three;if(!P||!P.normal)return;
    var c=P.coplanarPoint(new T.Vector3());
    planes.push({n:[-P.normal.x,-P.normal.y,-P.normal.z],p:[c.x,c.y,c.z]});
  });
  if(!planes.length||!R.models.length)return Promise.resolve('');
  return Promise.all(R.models.map(function(m){return m.model.getPositions();})).then(function(all){
    var cut=0,n=0,i,j,k,p;
    for(i=0;i<all.length;i++)for(j=0;j<(all[i]||[]).length;j++){
      p=all[i][j];n++;
      for(k=0;k<planes.length;k++)if(bimTorClip([p.x,p.y,p.z],planes[k])){cut++;break;}
    }
    return 'Section: '+planes.length+' plane'+(planes.length===1?'':'s')+'; '+cut+' of '+n+' elements have their placement point cut away';
  },function(){return '';});
}
/* point clouds (and splats) are drawn only in the deferred occlusion pass of That Open's PostproductionRenderer: turned on
   at the first one, as That Open's own example sets it (components-front PointCloudLoader/example.ts 64-68: enabled,
   DEFERRED, pen and shadows, the grid kept out of the passes); off until then, as it costs frame time */
function bimRvwDeferred(){
  var R=A3D_RVW,pp=R.world.renderer.postproduction,OBF=R.L.OBF;
  if(R.deferred)return;
  pp.enabled=true;
  pp.mode=OBF.PostproductionMode.DEFERRED;
  pp.style=OBF.PostproductionAspect.COLOR_PEN_SHADOWS;
  if(R.grid&&R.grid.material&&pp.basePass&&pp.basePass.isolatedMaterials)pp.basePass.isolatedMaterials.push(R.grid.material);
  R.deferred=true;
}
/* the camera on a box, as That Open's examples frame a cloud or a splat: from a radius out, a little above */
function bimRvwFrame(box){
  var R=A3D_RVW,T=R.L.T;
  if(!box||box.isEmpty())return;
  var c=box.getCenter(new T.Vector3()),r=box.getSize(new T.Vector3()).length()/2||8;
  R.world.camera.controls.setLookAt(c.x+r,c.y+r*0.7,c.z+r,c.x,c.y,c.z,true);
}
/* __acad3dV206, the owner's decision 11 (2026-11-28): point clouds and splats beside the models, through That Open. A Potree 2.0
   cloud is read from the three files chosen on this device: potree-core (bim-potree.min.js, fetched now, once) asks for
   byte ranges, which are cut from the files here (bimToeRange), so nothing goes over the network */
function bimRvwCloud(list){
  var R=A3D_RVW,files={},names=[],i;
  for(i=0;i<(list||[]).length;i++){files[list[i].name]=list[i];names.push(list[i].name);}
  var miss=bimToePotreeMissing(names);
  if(miss.length){bimRvwStatus('A Potree 2.0 point cloud needs '+miss.join(', ')+' too: choose its three files together');return Promise.resolve(false);}
  var rm={
    getUrl:function(u){return 'local/'+u;},
    fetch:function(input,init){
      var u=String(input&&input.url||input),name=u.split(/[\\\/]/).pop().split('?')[0],f=files[name],h=null;
      if(!f)return Promise.resolve(new Response(null,{status:404}));
      try{h=new Headers(init&&init.headers).get('Range');}catch(eH){h=null;}
      var r=bimToeRange(h,f.size);
      return Promise.resolve(r?new Response(f.slice(r.start,r.end),{status:206}):new Response(f));
    }
  };
  bimRvwStatus('Reading the point cloud (the first time loads its reader, about 100 KB)...');
  return bimToePotreeLoad().then(function(){
    var pcl=R.c.get(R.L.OBF.PointCloudLoader);
    pcl.world=R.world;
    bimRvwDeferred();
    return pcl.load({url:'local',requestManager:rm},{id:'cloud-'+(++R.seq)});
  }).then(function(cloud){
    bimRvwFrame(cloud&&cloud.box);
    var z=cloud&&cloud.box&&!cloud.box.isEmpty()?cloud.box.getSize(new R.L.T.Vector3()):null;
    bimRvwStatus('Point cloud'+(z?' of '+z.x.toFixed(2)+' x '+z.z.toFixed(2)+' m, '+z.y.toFixed(2)+' m high':'')+
      '. A section plane cuts it as it cuts the models');
    return true;
  },function(e){
    var s=String(e&&e.message||e);
    bimRvwStatus('The point cloud could not be read: '+s);a3dToast('Review: the point cloud could not be read: '+s);
    return false;
  });
}
/* a Gaussian splat (.ply, .compressed.ply: INRIA 3DGS) from this device, drawn among the models by That Open's own
   WebGL2 splat renderer, in the same deferred pass as the clouds */
function bimRvwSplat(file){
  var R=A3D_RVW;
  bimRvwStatus('Reading '+file.name+'...');
  return file.arrayBuffer().then(function(b){
    var sl=R.c.get(R.L.OBF.SplatLoader);
    sl.world=R.world;
    bimRvwDeferred();
    return Promise.resolve(sl.load({fileBytes:new Uint8Array(b)},{id:file.name+'-'+(++R.seq)})).then(function(h){
      var box=h&&h.box&&!h.box.isEmpty()?h.box:null,z=box?box.getSize(new R.L.T.Vector3()):null;
      bimRvwFrame(box);
      bimRvwStatus('Splat '+file.name+(z?': '+z.x.toFixed(2)+' x '+z.z.toFixed(2)+' m, '+z.y.toFixed(2)+' m high':''));
      return true;
    });
  }).then(null,function(e){
    var s=String(e&&e.message||e);
    bimRvwStatus('The splat could not be read: '+s);a3dToast('Review: the splat could not be read: '+s);
    return false;
  });
}
function bimRvwAct(a){
  var R=A3D_RVW,sel=R.hl?R.hl.selection.select:null,has=false,k;
  for(k in sel||{})if(sel.hasOwnProperty(k)&&sel[k]&&sel[k].size)has=true;
  if(a==='open'||a==='cloud'||a==='splat'){
    var f=R.el.querySelector(a==='open'?'[data-rvwfile]':a==='cloud'?'[data-rvwcloud]':'[data-rvwsplat]');
    f.value='';f.click();return;
  }
  if(a==='close'){bimReviewClose();return;}
  if(!R.c)return;
  if(a==='fit')bimRvwFit();
  else if(a==='clear'){R.clip.deleteAll();R.len.list.clear();R.area.list.clear();bimRvwStatus('Section planes and measurements removed');}
  else if(a==='hide'){if(has)R.hider.set(false,sel).then(function(){return R.hl.clear('select');});else bimRvwStatus('Select an element to hide first');}
  else if(a==='isolate'){if(has)R.hider.isolate(sel);else bimRvwStatus('Select an element to isolate first');}
  else if(a==='show')R.hider.set(true);
  else if(a==='import'){
    var m=null;
    for(k in sel||{})if(sel.hasOwnProperty(k)&&sel[k]&&sel[k].size)m=bimRvwModel(k);
    if(!m&&R.models.length===1)m=R.models[0];
    if(!m){bimRvwStatus(R.models.length?'Select an element of the model to import':'Open an IFC file first');return;}
    bimRvwStatus('Importing '+m.name+'...');
    var bytes=m.bytes,name=m.name;
    bimReviewClose();
    bimIfcImportBuffer(bytes,name).then(function(r){a3dToast(r.text);},function(e){a3dToast('IFC import failed: '+String(e&&e.message||e));});
  }
}
function bimRvwWire(){
  var R=A3D_RVW,el=R.el,view=el.querySelector('.a3d-rvw-view');
  el.addEventListener('click',function(ev){
    var t=ev.target,b=t.closest&&t.closest('[data-rvw],[data-rvwmode],[data-rvwsel]');
    if(!b)return;
    if(b.hasAttribute('data-rvwmode'))bimRvwMode(b.getAttribute('data-rvwmode'));
    else if(b.hasAttribute('data-rvwsel')){if(R.hl)R.hl.highlightByID('select',bimRvwMap(b.getAttribute('data-rvwsel')),true,true);}
    else bimRvwAct(b.getAttribute('data-rvw'));
  });
  el.addEventListener('change',function(ev){
    var t=ev.target;
    if(t.hasAttribute('data-rvwfile'))bimRvwFiles(t.files);
    else if(t.hasAttribute('data-rvwcloud'))bimRvwCloud(t.files);
    else if(t.hasAttribute('data-rvwsplat')&&t.files&&t.files[0])bimRvwSplat(t.files[0]);
    else if(t.hasAttribute('data-rvwvis')&&R.hider){
      R.hider.set(!!t.checked,bimRvwMap(t.getAttribute('data-rvwvis')));
      var box=t.closest('details'),sub=box?box.querySelectorAll('[data-rvwvis]'):[],i;
      for(i=0;i<sub.length;i++)if(sub[i]!==t&&sub[i].getAttribute('data-rvwvis').indexOf(t.getAttribute('data-rvwvis')+',')===0)sub[i].checked=t.checked;
    }
  });
  /* That Open's measuring tools take their point from the last pointer move over the canvas; a tap on a touch screen
     makes none, so the view sends one where the double-click is and waits (at most 800 ms) for the pick to settle */
  function pointAt(ev,tool){
    var cv=R.world.renderer.three.domElement,was=tool.lastPick&&tool.lastPick.point?tool.lastPick.point.clone():null,t0=Date.now();
    try{cv.dispatchEvent(new PointerEvent('pointermove',{clientX:ev.clientX,clientY:ev.clientY,bubbles:true,pointerType:'mouse'}));}catch(eP){}
    return new Promise(function(res){
      (function wait(){
        var p=tool.lastPick&&tool.lastPick.point;
        if((p&&(!was||!p.equals(was)))||Date.now()-t0>800){res();return;}
        setTimeout(wait,30);
      })();
    });
  }
  view.addEventListener('dblclick',function(ev){
    if(!R.c)return;
    if(R.mode==='clip')Promise.resolve(R.clip.create(R.world)).then(bimRvwSectionText).then(function(s){if(s)bimRvwStatus(s);});
    else if(R.mode==='length'){
      /* a length is two points: its readout once the second is placed, from the finished measurement */
      R.lenPts=(R.lenPts||0)+1;
      pointAt(ev,R.len).then(function(){return R.len.create();}).then(function(){
        if(R.lenPts<2){bimRvwStatus('Length: double-click the second point');return;}
        R.lenPts=0;
        var last=null;R.len.list.forEach(function(l){last=l;});
        if(last)bimRvwStatus('Length: '+(+last.value).toFixed(3)+' m');
      });
    }
    else if(R.mode==='area')pointAt(ev,R.area).then(function(){return R.area.create();});
  });
  R.keys=function(ev){
    if(!R.open)return;
    if(ev.key==='Escape'){if(R.mode!=='select')bimRvwMode('select');else bimReviewClose();ev.preventDefault();}
    else if(ev.key==='Enter'&&R.mode==='area'){try{R.area.endCreation();}catch(eE){}ev.preventDefault();}
    else if((ev.key==='Delete'||ev.key==='Backspace')&&R.mode==='clip'){R.clip.delete(R.world);ev.preventDefault();}
  };
  document.addEventListener('keydown',R.keys,true);
  ['dragover','drop'].forEach(function(n){el.addEventListener(n,function(ev){
    ev.preventDefault();
    if(n==='drop'&&ev.dataTransfer)bimRvwFiles([].filter.call(ev.dataTransfer.files||[],function(f){return /\.ifc$/i.test(f.name);}));
  });});
}
/* REVIEW: the view opened (That Open loaded the first time), optionally with files */
function bimReviewOpen(files){
  var R=A3D_RVW;
  if(R.open){if(files)bimRvwFiles(files);return Promise.resolve(true);}
  var el=document.createElement('div');
  el.className='a3d-review';el.setAttribute('role','dialog');el.setAttribute('aria-label','Review IFC models');
  el.innerHTML=bimRvwHtml();
  document.body.appendChild(el);
  R.el=el;R.open=true;R.models=[];
  bimRvwWire();
  bimRvwStatus('Loading That Open (about 2 MB, once)...');
  return bimToeLoad().then(function(L){
    if(!R.open)return false;
    R.L=L;bimRvwWorld(L);bimRvwMode('select');
    if(files)return bimRvwFiles(files).then(function(){return true;});
    return true;
  },function(e){
    var s=String(e&&e.message||e);
    console.warn('[BIM] Review: That Open could not be loaded',e);
    bimRvwStatus('That Open could not be loaded: '+s);a3dToast('Review: That Open could not be loaded: '+s);
    return false;
  });
}
function bimReviewClose(){
  var R=A3D_RVW;
  if(!R.open)return;
  R.open=false;
  if(R.keys)document.removeEventListener('keydown',R.keys,true);
  try{if(R.c)R.c.dispose();}catch(eD){console.warn('[BIM] Review: That Open could not be closed cleanly',eD);}
  if(R.el&&R.el.parentNode)R.el.parentNode.removeChild(R.el);
  R.el=null;R.c=null;R.world=null;R.grid=null;R.deferred=false;R.fm=null;R.hl=null;R.clip=null;R.len=null;R.area=null;R.hider=null;R.models=[];R.keys=null;
}
function bimReviewCommand(){if(A3D_RVW.open)bimReviewClose();else bimReviewOpen();}
export { A3D_RVW, bimReviewCommand };
