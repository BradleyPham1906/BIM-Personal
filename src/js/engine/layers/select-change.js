  /* ================= __acad3dV121: selecting, by the layers =================
     A click, a window and a list row pick what is shown and unlocked (bimLayerPickable); a list row
     that names one object refuses the rest through bimLayerPickRefusal. SELECT ALL and every
     select-by-criteria take AutoCAD's ALL through bimSelectByRule, and say how many of the
     selection cannot be seen and how many were left out. The selection never holds an object on a
     frozen or locked layer: saveSoon drops one (bimLayerDropUnselectable). */
  function bimLayerPickRefusal(o){
    var s=bimObjLayerState(o);
    if(s.on&&!s.frozen&&!s.locked)return '';
    return o.name+' is on a layer that is '+(!s.on?'off':(s.frozen?'frozen':'locked'))+': it cannot be selected';
  }
  function bimSelectByRule(cands){
    var ids=[],hidden=0,out=0,i,o;
    for(i=0;i<cands.length;i++){
      o=cands[i];
      if(!bimLayerSelectable(o)){out++;continue;}
      ids.push(o.id);
      if(!bimLayerShown(o))hidden++;
    }
    A3D.selSet=ids;A3D.sel=ids.length?ids[0]:null;A3D.sel2=null;
    refreshTree();refreshProps();paint();
    a3dToast('Selected '+ids.length+' object(s)'+(hidden?', '+hidden+' of them on layers that are off':'')+
      (out?'; '+out+' on frozen or locked layers left out':''));
    return ids;
  }
  function bimLayerDropUnselectable(){
    var o,n=0,k;
    if(A3D.sel&&(o=objById(A3D.sel))&&!bimLayerSelectable(o)){A3D.sel=null;n++;}
    if(A3D.sel2&&(o=objById(A3D.sel2))&&!bimLayerSelectable(o)){A3D.sel2=null;n++;}
    if(A3D.selSet&&A3D.selSet.length){
      k=A3D.selSet.length;
      A3D.selSet=A3D.selSet.filter(function(id){var q=objById(id);return !q||bimLayerSelectable(q);});
      n+=k-A3D.selSet.length;
    }
    return n;
  }
  var BIM_LAYER_PALETTE=['#7f9db8','#c0a377','#84b98c','#bd8a9b','#9b8abd','#8f9db0','#b8a47f','#7fb8b0','#c9c2b3','#9aa79a'];
  function bimNextLayerColor(){return BIM_LAYER_PALETTE[A3D.layers.length%BIM_LAYER_PALETTE.length];}
  var AIA_LAYER_PRESETS=[
    ['A-WALL','Walls'],['A-WALL-FULL','Full-height walls'],['A-DOOR','Doors'],['A-GLAZ','Windows / glazing'],
    ['A-FLOR','Floor'],['A-CLNG','Ceiling'],['A-ROOF','Roof'],['A-STRS','Stairs'],['A-FURN','Furniture'],
    ['A-ANNO-DIMS','Dimensions'],['A-ANNO-TEXT','Text / notes'],
    ['S-BEAM','Structural beams'],['S-COLS','Structural columns'],['S-SLAB','Structural slab'],
    ['M-HVAC','Mechanical HVAC'],['E-LITE','Electrical lighting'],['E-POWR','Electrical power'],['P-PIPE','Plumbing pipe'],
    ['C-ROAD','Civil roads'],['L-PLNT','Landscape planting']
  ];
  function openAddLayerDlg(){
    closeDlg();
    var d=document.createElement('div');
    d.className='a3d-dlg';
    var opts='<option value="__custom__">Custom name\u2026</option>'+AIA_LAYER_PRESETS.map(function(p){return '<option value="'+p[0]+'">'+p[0]+' \u2014 '+p[1]+'</option>';}).join('');
    d.innerHTML='<div class="a3d-dlghd">New Layer (AIA/NCS presets)</div>'+
      '<div class="a3d-dlgbody">'+
      '<div class="a3d-dlgrow"><label>Preset</label><select data-a3dp="preset">'+opts+'</select></div>'+
      '<div class="a3d-dlgrow" id="a3d-lyrcustomrow" style="display:none"><label>Name</label><input type="text" data-a3dp="custom" maxlength="40" placeholder="Layer name"></div>'+
      '<div id="a3d-dlgerr" class="a3d-dlgerr"></div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="ok">Add</button></div>';
    el.root.appendChild(d);
    el.dlg=d;
    var sel=d.querySelector('[data-a3dp="preset"]'),customRow=d.querySelector('#a3d-lyrcustomrow'),customInp=d.querySelector('[data-a3dp="custom"]');
    sel.addEventListener('change',function(){customRow.style.display=sel.value==='__custom__'?'':'none';if(sel.value==='__custom__')customInp.focus();});
    function submit(){
      var name;
      if(sel.value==='__custom__'){
        name=(customInp.value||'').trim();
        if(!name){document.getElementById('a3d-dlgerr').textContent='Enter a layer name';return;}
      }else{
        name=sel.value;
      }
      closeDlg();
      addLayer(name);
    }
    d.addEventListener('click',function(ev){
      var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;
      if(!b)return;
      if(b.getAttribute('data-a3dlg')==='ok')submit();else closeDlg();
    });
    d.addEventListener('keydown',function(ev){
      if(ev.key==='Enter'){ev.preventDefault();ev.stopPropagation();submit();}
      else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();}
    });
  }
  /* ================= __acad3dV121: changing a layer, by AutoCAD's rules =================

     Every change to a layer goes through bimLayerSet, bimLayerNew, bimLayerDelete,
     bimLayerMakeCurrent or bimObjSetLayer -- the Layers panel, the Layer Properties Manager, the
     Properties panel and the commands alike. Each is one undo step; each refuses what AutoCAD
     refuses, and says why. */

  /* AutoCAD's acadiso.lin set, as its definitions, in millimetres on paper: a positive number is a
     dash, a negative one a gap, 0 a dot. The canvas, the plots and the DXF each derive their
     pattern from this one table. */
  var BIM_LINETYPES=[
    {name:'Continuous',desc:'Solid line',pat:[]},
    {name:'DASHED',desc:'Dashed __ __ __ __ __',pat:[12.7,-6.35]},
    {name:'HIDDEN',desc:'Hidden _ _ _ _ _ _ _',pat:[6.35,-3.175]},
    {name:'CENTER',desc:'Center ____ _ ____ _ ____',pat:[31.75,-6.35,6.35,-6.35]},
    {name:'PHANTOM',desc:'Phantom _____ _ _ _____ _ _',pat:[31.75,-6.35,6.35,-6.35,6.35,-6.35]},
    {name:'DOT',desc:'Dot . . . . . . . .',pat:[0,-6.35]},
    {name:'DASHDOT',desc:'Dash dot __ . __ . __ .',pat:[12.7,-6.35,0,-6.35]},
    {name:'BORDER',desc:'Border __ __ . __ __ .',pat:[12.7,-6.35,12.7,-6.35,0,-6.35]},
    {name:'DIVIDE',desc:'Divide __ . . __ . .',pat:[12.7,-6.35,0,-6.35,0,-6.35]}
  ];
  /* AutoCAD's lineweights, in millimetres. A layer's lineweight is one of these, or null: Default. */
  var BIM_LINEWEIGHTS=[0,0.05,0.09,0.13,0.15,0.18,0.2,0.25,0.3,0.35,0.4,0.5,0.53,0.6,0.7,0.8,0.9,1,1.06,1.2,1.4,1.58,2,2.11];
  var BIM_LAYER_BADCHARS=/[<>\/\\":;?*|,=`]/;
  function bimLinetypeDef(name){
    var i,n=String(name==null?'':name).toLowerCase();
    for(i=0;i<BIM_LINETYPES.length;i++)if(BIM_LINETYPES[i].name.toLowerCase()===n)return BIM_LINETYPES[i];
    return null;
  }
  function bimLayerByName(name,exceptId){
    var i,n=String(name==null?'':name).replace(/^\s+|\s+$/g,'').toLowerCase();
    for(i=0;i<A3D.layers.length;i++)
      if(A3D.layers[i].id!==exceptId&&String(A3D.layers[i].name).toLowerCase()===n)return A3D.layers[i];
    return null;
  }
  /* true when layer `ancestorId` is `ly` itself or any layer above it */
  function bimLayerUnder(ly,ancestorId){
    var ch=bimLayerChain(ly),i;
    for(i=0;i<ch.length;i++)if(ch[i].id===ancestorId)return true;
    return false;
  }
  function bimLayerNameCheck(name,exceptId){
    var n=String(name==null?'':name).replace(/^\s+|\s+$/g,'');
    if(!n)return 'A layer needs a name';
    if(n.length>64)return 'A layer name is 64 characters at most';
    if(BIM_LAYER_BADCHARS.test(n))return 'A layer name cannot contain < > / \\ " : ; ? * | , = or `';
    if(bimLayerByName(n,exceptId))return 'There is already a layer called '+n;
    return '';
  }
  function bimLayerUniqueName(base){
    var n=1;
    while(bimLayerByName(base+' '+n))n++;
    return base+' '+n;
  }
  /* what can no longer be picked leaves the selection -- a Delete or a nudge must not act on objects
     nobody can see or is allowed to touch */
  function bimLayerDropUnpickable(){
    var o;
    if(A3D.sel&&(o=objById(A3D.sel))&&!bimLayerPickable(o))A3D.sel=null;
    if(A3D.sel2&&(o=objById(A3D.sel2))&&!bimLayerPickable(o))A3D.sel2=null;
    if(A3D.selSet&&A3D.selSet.length)A3D.selSet=A3D.selSet.filter(function(id){var q=objById(id);return !q||bimLayerPickable(q);});
  }
  function bimLayerChanged(){
    bimLayerDropUnpickable();
    refreshLayers();refreshTree();paint();saveSoon();
  }
  function bimLayerRefuse(msg){
    a3dToast(msg);
    return false;
  }
  function bimLayerSet(id,field,val){
    var ly=bimLayerById(id),err,v;
    if(!ly){console.warn('[BIM] No layer '+id);return bimLayerRefuse('That layer no longer exists');}
    var cur=bimLayerById(A3D.activeLayer);
    if(field==='name'){
      v=String(val==null?'':val).replace(/^\s+|\s+$/g,'');
      if(v===ly.name)return true;
      err=bimLayerNameCheck(v,ly.id);
      if(err)return bimLayerRefuse(err);
    }else if(field==='color'){
      v=String(val||'').toLowerCase();
      if(!/^#[0-9a-f]{6}$/.test(v))return bimLayerRefuse('A layer color is a colour such as #7f9db8');
    }else if(field==='visible'||field==='frozen'||field==='locked'||field==='plot'){
      v=!!val;
      if(field==='frozen'&&v&&cur&&bimLayerUnder(cur,ly.id))
        return bimLayerRefuse(cur.id===ly.id?'The current layer cannot be frozen: make another layer current first'
                                            :'This layer holds the current layer, which cannot be frozen');
    }else if(field==='linetype'){
      var lt=bimLinetypeDef(val);
      if(!lt)return bimLayerRefuse('Unknown linetype: '+val);
      v=lt.name;
    }else if(field==='lineweight'){
      if(val===null||val===''||val==='default'||val===undefined)v=null;
      else{
        v=+val;
        if(BIM_LINEWEIGHTS.indexOf(v)<0)return bimLayerRefuse('Not one of AutoCAD\'s lineweights: '+val);
      }
    }else if(field==='transparency'){
      v=Math.round(+val);
      if(!isFinite(v)||v<0||v>90)return bimLayerRefuse('Transparency is 0 to 90');
    }else if(field==='description'){
      v=String(val==null?'':val).slice(0,200);
    }else if(field==='parent'){
      v=(val===null||val===''||val===undefined)?null:String(val);
      if(v!==null){
        var P=bimLayerById(v);
        if(!P)return bimLayerRefuse('That layer no longer exists');
        if(bimLayerUnder(P,ly.id))return bimLayerRefuse('A layer cannot go under itself or one of its own sub-layers');
        if(cur&&bimLayerUnder(cur,ly.id)&&bimLayerEff(P).frozen)
          return bimLayerRefuse('The current layer cannot go under a frozen layer');
      }
    }else{
      console.warn('[BIM] Unknown layer field '+field);
      return bimLayerRefuse('That is not a layer property');
    }
    var was;   /* what the layer reads as now, by the same tolerant rules its flags are read by */
    if(field==='visible')was=(ly.visible!==false);
    else if(field==='plot')was=(ly.plot!==false);
    else if(field==='frozen'||field==='locked')was=!!ly[field];
    else if(field==='lineweight'||field==='parent')was=(ly[field]===undefined)?null:ly[field];
    else if(field==='linetype')was=(bimLinetypeDef(ly.linetype)||BIM_LINETYPES[0]).name;
    else if(field==='transparency')was=isFinite(ly.transparency)?+ly.transparency:0;
    else if(field==='description')was=(typeof ly.description==='string')?ly.description:'';
    else was=ly[field];
    if(was===v)return true;
    pushUndo();
    ly[field]=v;
    if(field==='visible'&&!v&&cur&&bimLayerUnder(cur,ly.id))a3dToast('The current layer is off: what you draw on it will not show until it is on');
    bimLayerChanged();
    return true;
  }
  /* opts: {name, parent, from (a layer to take the appearance of), color, current} */
  function bimLayerNew(opts){
    opts=opts||{};
    var name=(opts.name==null||opts.name==='')?bimLayerUniqueName('Layer'):String(opts.name).replace(/^\s+|\s+$/g,'');
    var err=bimLayerNameCheck(name,null);
    if(err){bimLayerRefuse(err);return null;}
    var par=opts.parent?bimLayerById(opts.parent):null;
    if(opts.parent&&!par){bimLayerRefuse('That layer no longer exists');return null;}
    var src=opts.from?bimLayerById(opts.from):par;
    pushUndo();
    var lyr={id:'layer-'+Date.now().toString(36)+'-'+(A3D.seq++),name:name,
      color:(opts.color&&/^#[0-9a-fA-F]{6}$/.test(opts.color))?opts.color.toLowerCase():(src?src.color:bimNextLayerColor()),
      visible:true,locked:false,frozen:false,
      linetype:(src&&bimLinetypeDef(src.linetype))?bimLinetypeDef(src.linetype).name:'Continuous',
      lineweight:(src&&src.lineweight!==undefined)?src.lineweight:null,
      transparency:(src&&isFinite(src.transparency))?src.transparency:0,
      plot:!(src&&src.plot===false),
      description:'',parent:par?par.id:null};
    A3D.layers.push(lyr);
    if(opts.current)A3D.activeLayer=lyr.id;
    bimLayerChanged();
    return lyr;
  }
  /* AutoCAD's Delete Layer refuses layer 0, the current layer and a layer that holds objects. The
     first layer here is layer 0's counterpart: it is where an object whose layer is gone is read to
     be, so it always exists. A deleted layer's sub-layers move up to its own parent. */
  function bimLayerDelete(id){
    var ly=bimLayerById(id),i,n=0;
    if(!ly)return bimLayerRefuse('That layer no longer exists');
    if(ly===A3D.layers[0])return bimLayerRefuse(ly.name+' is the first layer, which (as AutoCAD\'s layer 0) cannot be deleted');
    if(id===A3D.activeLayer)return bimLayerRefuse('The current layer cannot be deleted: make another layer current first');
    for(i=0;i<A3D.objs.length;i++)if(bimLayerOf(A3D.objs[i])===ly)n++;
    if(n)return bimLayerRefuse(ly.name+' holds '+n+' object'+(n===1?'':'s')+': move '+(n===1?'it':'them')+' to another layer first');
    pushUndo();
    var kids=0;
    for(i=0;i<A3D.layers.length;i++)if(A3D.layers[i].parent===id){A3D.layers[i].parent=ly.parent||null;kids++;}
    A3D.layers.splice(A3D.layers.indexOf(ly),1);
    bimLayerChanged();
    a3dToast('Layer '+ly.name+' deleted'+(kids?'; '+kids+' sub-layer'+(kids===1?'':'s')+' moved up':''));
    return true;
  }
  function bimLayerMakeCurrent(id){
    var ly=bimLayerById(id);
    if(!ly)return bimLayerRefuse('That layer no longer exists');
    if(bimLayerEff(ly).frozen)return bimLayerRefuse('A frozen layer cannot be current: thaw it first');
    if(A3D.activeLayer===id)return true;
    A3D.activeLayer=id;
    refreshLayers();refreshProps();saveSoon();
    return true;
  }
  function bimObjSetLayer(objId,layerId){
    var o=objById(objId),ly=bimLayerById(layerId);
    if(!o)return false;
    if(!ly)return bimLayerRefuse('That layer no longer exists');
    if(bimLayerOf(o)===ly&&o.layer===ly.id)return true;
    pushUndo();
    o.layer=ly.id;
    bimLayerChanged();
    return true;
  }
  /* The names the rest of the file has always called. A layer made by an import or a standard name
     that already exists is that layer -- the import's objects join it -- as AutoCAD merges them. */
  function addLayer(name,color){
    var ex=name?bimLayerByName(name):null;
    if(ex){bimLayerMakeCurrent(ex.id);return ex;}
    return bimLayerNew({name:name||null,color:color,current:true});
  }
  function setActiveLayer(id){return bimLayerMakeCurrent(id);}
  var BIM_EYE_ON=ric('<path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7-10-7-10-7z"/><circle cx="12" cy="12" r="3"/>');
  var BIM_EYE_OFF=ric('<path d="M3 3l18 18"/><path d="M10.6 5.2A10.6 10.6 0 0 1 12 5c6 0 10 7 10 7a17.7 17.7 0 0 1-3.2 4M6.5 6.5C3.8 8.3 2 12 2 12s4 7 10 7c1.4 0 2.7-.3 3.9-.8"/>');
  var BIM_LOCK_ON=ric('<rect x="5" y="11" width="14" height="9" rx="1.5"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>');
  var BIM_LOCK_OFF=ric('<rect x="5" y="11" width="14" height="9" rx="1.5"/><path d="M8 11V7a4 4 0 0 1 7.4-2"/>');
