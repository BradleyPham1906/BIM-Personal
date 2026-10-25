  /* ================= __acad3dV121: the Layers panel =================
     The owner: "layers (this should combine with model)". The rail's Layers tab is the layer tree --
     sub-layers under their parents -- and each layer opens to the objects on it, so the model tree
     is what the layers contain. Every switch goes through V121b's rules; the panel's own state (what
     is open, which layer its buttons act on, the search) is neither saved nor undone. */
  var A3D_LY={open:{},sel:null,edit:null,filter:'',drag:null};
  var BIM_LY_IC={
    on:BIM_EYE_ON,off:BIM_EYE_OFF,locked:BIM_LOCK_ON,unlocked:BIM_LOCK_OFF,
    frozen:ric('<path d="M12 3v18M4.2 7.5l15.6 9M4.2 16.5l15.6-9"/><path d="M9.6 4.8 12 7l2.4-2.2M9.6 19.2 12 17l2.4 2.2"/>'),
    thawed:ric('<circle cx="12" cy="12" r="3.6"/><path d="M12 3v2.4M12 18.6V21M3 12h2.4M18.6 12H21M5.6 5.6l1.7 1.7M16.7 16.7l1.7 1.7M5.6 18.4l1.7-1.7M16.7 7.3l1.7-1.7"/>'),
    cur:ric('<circle cx="12" cy="12" r="5.5" fill="currentColor" stroke="none"/>'),
    notcur:ric('<circle cx="12" cy="12" r="5.5"/>'),
    add:ric('<path d="M12 5v14M5 12h14"/>'),
    sub:ric('<path d="M6.5 4.5v8.5a3 3 0 0 0 3 3h9"/><path d="M15.5 12.5 19 16l-3.5 3.5"/>'),
    std:ric('<path d="M5 6.5h14M5 12h14M5 17.5h9"/>'),
    make:ric('<path d="M5 12.5 9.8 17.3 19 7.5"/>'),
    del:ric('<path d="M4.5 7h15M9.5 7V4.5h5V7M6.5 7l1 13h9l1-13"/>'),
    lpm:ric('<rect x="3.5" y="5" width="17" height="14" rx="1.5"/><path d="M3.5 9.5h17M9 9.5V19M14.5 9.5V19"/>'),   /* __acad3dV121 */
    open:ric('<path d="M6.5 9.5 12 15l5.5-5.5"/>'),
    closed:ric('<path d="M9.5 6.5 15 12l-5.5 5.5"/>')
  };
  /* A layer's parent, when it has a real one. A parent that is missing, or that would put a layer
     inside its own branch, counts as none: the layer is listed at the top rather than lost. */
  function bimLayerParentOk(l){
    if(typeof l.parent!=='string'||!l.parent)return null;
    var p=bimLayerById(l.parent);
    if(!p||bimLayerUnder(p,l.id))return null;
    return p;
  }
  function bimLayerKids(l){
    return A3D.layers.filter(function(c){return c!==l&&bimLayerParentOk(c)===l;});
  }
  /* the layers in tree order, each with its depth: the panel, the manager and the Layer fields all
     list them this way */
  function bimLayerTree(){
    var out=[],seen={};
    function walk(l,d){
      if(seen[l.id])return;
      seen[l.id]=1;out.push({ly:l,depth:d});
      bimLayerKids(l).forEach(function(c){walk(c,d+1);});
    }
    A3D.layers.forEach(function(l){if(!bimLayerParentOk(l))walk(l,0);});
    return out;
  }
  function bimLayerContents(){
    var m={},i,o,ly;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];ly=bimLayerOf(o);
      if(ly)(m[ly.id]||(m[ly.id]=[])).push(o);
    }
    return m;
  }
  function bimLyBtn(a,title,ic){
    return '<button type="button" class="a3d-lyb" data-lyact="'+a+'" title="'+bimEsc(title)+'" aria-label="'+bimEsc(title)+'">'+ic+'</button>';
  }
  function bimLyTgl(k,id,on,title,icOn,icOff){
    return '<button type="button" class="a3d-lyi'+(on?' on':'')+'" data-'+k+'="'+bimEsc(id)+'" title="'+bimEsc(title)+'" aria-label="'+
      bimEsc(title)+'" aria-pressed="'+(on?'true':'false')+'">'+(on?icOn:icOff)+'</button>';
  }
  function bimLyRowHtml(l,depth,nObj,nKids,open,sel,cur){
    var s=bimLayerEff(l),nm=bimEsc(l.name),id=bimEsc(l.id),isCur=(l.id===cur);
    var col=/^#[0-9a-fA-F]{6}$/.test(l.color||'')?l.color:'#7f9db8';
    var h='<div class="a3d-lyrow'+(l.id===sel?' sel':'')+(isCur?' cur':'')+((!s.on||s.frozen)?' dim':'')+
      '" data-lyid="'+id+'" draggable="true" style="padding-left:'+(4+depth*14)+'px">';
    h+=(nObj||nKids)?'<button type="button" class="a3d-lycar" data-lytog="'+id+'" title="'+(open?'Close ':'Open ')+nm+'" aria-label="'+
        (open?'Close ':'Open ')+nm+'">'+(open?BIM_LY_IC.open:BIM_LY_IC.closed)+'</button>':'<span class="a3d-lycar"></span>';
    /* the status column, AutoCAD's first: the current layer's mark, and the way to make one current */
    h+='<button type="button" class="a3d-lystat'+(isCur?' on':'')+'" data-lycur="'+id+'" title="'+
      (isCur?nm+' is the current layer':'Make '+nm+' current')+'" aria-label="'+(isCur?nm+' is the current layer':'Make '+nm+' current')+
      '" aria-pressed="'+(isCur?'true':'false')+'">'+(isCur?BIM_LY_IC.cur:BIM_LY_IC.notcur)+'</button>';
    h+='<input type="color" class="a3d-lysw" data-lycol="'+id+'" value="'+col.toLowerCase()+'" title="Color of '+nm+'" aria-label="Color of '+nm+'">';
    h+=(A3D_LY.edit===l.id)
      ?'<input type="text" class="a3d-lyren" data-lyren="'+id+'" value="'+nm+'" aria-label="Name of the layer">'
      :'<span class="a3d-lynm" data-lyname="'+id+'" title="'+nm+' -- double-click to rename">'+nm+'</span>';
    h+='<span class="a3d-lycnt">'+(nObj||'')+'</span>';
    h+=bimLyTgl('lyon',l.id,l.visible===false,l.visible===false?'Turn '+nm+' on':'Turn '+nm+' off',BIM_LY_IC.off,BIM_LY_IC.on);
    h+=bimLyTgl('lyfrz',l.id,!!l.frozen,l.frozen?'Thaw '+nm:'Freeze '+nm,BIM_LY_IC.frozen,BIM_LY_IC.thawed);
    h+=bimLyTgl('lylock',l.id,!!l.locked,l.locked?'Unlock '+nm:'Lock '+nm,BIM_LY_IC.locked,BIM_LY_IC.unlocked);
    return h+'</div>';
  }
  function bimLyObjHtml(o,depth){
    var sel=(A3D.sel===o.id||(A3D.selSet&&A3D.selSet.indexOf(o.id)>=0)),pin=bimIsLocked(o);
    var ty=(o.bim&&o.bim.type)||o.t,dot=(o.t==='sketch')?bimLayerLook(o).color:(o.col||(TYPES[o.t]||{}).c||'#7f9db8');
    return '<div class="a3d-lyobj'+(sel?' sel':'')+'" data-lyobj="'+bimEsc(o.id)+'" draggable="true" style="padding-left:'+(22+depth*14)+
      'px" title="'+bimEsc(o.name)+' -- drag onto a layer to move it there">'+
      '<span class="a3d-lydot" style="background:'+bimEsc(dot)+'"></span>'+
      '<span class="a3d-lynm">'+bimEsc(o.name)+'</span><span class="a3d-lyty">'+bimEsc(ty)+'</span>'+
      bimLyTgl('lypin',o.id,pin,pin?'Unpin '+o.name:'Pin '+o.name,BIM_LY_IC.locked,BIM_LY_IC.unlocked)+'</div>';
  }
  function bimLayersPanelHtml(){
    var con=bimLayerContents(),f=String(A3D_LY.filter||'').toLowerCase(),cur=A3D.activeLayer;
    var sel=bimLayerById(A3D_LY.sel)?A3D_LY.sel:cur,memo={},seen={};
    function hit(s){return String(s).toLowerCase().indexOf(f)>=0;}
    function match(l){
      if(memo.hasOwnProperty(l.id))return memo[l.id];
      memo[l.id]=false;
      var r=hit(l.name)||(con[l.id]||[]).some(function(o){return hit(o.name);})||bimLayerKids(l).some(match);
      memo[l.id]=r;
      return r;
    }
    var h='<div class="a3d-lyp"><div class="a3d-lyhd"><span class="a3d-lyttl">Layers</span><span class="a3d-lybtns">'+
      bimLyBtn('new','New layer',BIM_LY_IC.add)+
      bimLyBtn('sub','New sub-layer under the selected layer',BIM_LY_IC.sub)+
      bimLyBtn('std','New layer with an AIA / NCS standard name',BIM_LY_IC.std)+
      bimLyBtn('cur','Make the selected layer current',BIM_LY_IC.make)+
      bimLyBtn('del','Delete the selected layer',BIM_LY_IC.del)+
      bimLyBtn('lpm','Layer Properties Manager (LAYER)',BIM_LY_IC.lpm)+
      '</span></div><input type="text" class="a3d-lysearch" data-lysearch="1" placeholder="Search layers and objects" value="'+
      bimEsc(A3D_LY.filter||'')+'" aria-label="Search layers and objects"><div class="a3d-lylist" data-lylist="1">';
    function render(l,depth){
      if(seen[l.id]||(f&&!match(l)))return;
      seen[l.id]=1;
      var kids=bimLayerKids(l),objs=con[l.id]||[],open=f?true:!!A3D_LY.open[l.id];
      h+=bimLyRowHtml(l,depth,objs.length,kids.length,open,sel,cur);
      if(!open)return;
      kids.forEach(function(c){render(c,depth+1);});
      objs.forEach(function(o){if(!f||hit(o.name)||hit(l.name))h+=bimLyObjHtml(o,depth+1);});
    }
    A3D.layers.forEach(function(l){if(!bimLayerParentOk(l))render(l,0);});
    if(f&&!Object.keys(seen).length)h+='<div class="a3d-lyempty">Nothing matches</div>';
    return h+'</div>'+bimLySectionsHtml(f)+'</div>';   /* __acad3dV148: the results and the data, below the layers */
  }
