# ---- 1. the panel: the layer tree, and the objects on each layer
span("  function refreshLayers(){\n", "  function bimEsc(s){\n", r"""  /* ================= __acad3dV121: the Layers panel =================
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
    var s=bimLayerEff(l),nm=bimEsc(l.name),id=bimEsc(l.id);
    var col=/^#[0-9a-fA-F]{6}$/.test(l.color||'')?l.color:'#7f9db8';
    var h='<div class="a3d-lyrow'+(l.id===sel?' sel':'')+(l.id===cur?' cur':'')+((!s.on||s.frozen)?' dim':'')+
      '" data-lyid="'+id+'" draggable="true" style="padding-left:'+(4+depth*14)+'px">';
    h+=(nObj||nKids)?'<button type="button" class="a3d-lycar" data-lytog="'+id+'" title="'+(open?'Close ':'Open ')+nm+'" aria-label="'+
        (open?'Close ':'Open ')+nm+'">'+(open?BIM_LY_IC.open:BIM_LY_IC.closed)+'</button>':'<span class="a3d-lycar"></span>';
    /* the status column, AutoCAD's first: the current layer's mark, and the way to make one current */
    h+='<button type="button" class="a3d-lystat'+(l.id===cur?' on':'')+'" data-lycur="'+id+'" title="'+
      (l.id===cur?nm+' is the current layer':'Make '+nm+' current')+'" aria-label="'+(l.id===cur?nm+' is the current layer':'Make '+nm+' current')+
      '" aria-pressed="'+(l.id===cur?'true':'false')+'">'+(l.id===cur?BIM_LY_IC.cur:BIM_LY_IC.notcur)+'</button>';
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
    return h+'</div></div>';
  }
  function bimLayersPanelRefresh(){
    var host=document.querySelector('#figma-layers-panel .a3d-layers-wrap');
    if(host)bimRenderInto(host,bimLayersPanelHtml());
  }
  /* every view of the layers, redrawn from them */
  function refreshLayers(){
    bimLayersPanelRefresh();
  }
  function bimLyFocusEdit(){
    var inp=document.querySelector('#figma-layers-panel [data-lyren]');
    if(inp){try{inp.focus();inp.select();}catch(eF){}}
  }
  function bimLyEndEdit(inp,cancel){
    var id=inp.getAttribute('data-lyren');
    if(A3D_LY.edit!==id)return;
    A3D_LY.edit=null;
    if(!cancel)bimLayerSet(id,'name',inp.value);
    refreshLayers();
  }
  function bimLySelectObj(id){
    var o=objById(id);
    if(!o)return;
    var s=bimObjLayerState(o);
    if(!s.on||s.frozen||s.locked){
      a3dToast(o.name+' is on a layer that is '+(!s.on?'off':(s.frozen?'frozen':'locked'))+': it cannot be selected');
      return;
    }
    A3D.sel=o.id;A3D.sel2=null;A3D.selSet=[o.id];
    refreshTree();paint();
  }
  function bimLyAct(a){
    var sel=bimLayerById(A3D_LY.sel)||bimLayerById(A3D.activeLayer),n;
    if(a==='new'){
      n=bimLayerNew({from:sel?sel.id:null});
      if(n){A3D_LY.sel=n.id;A3D_LY.edit=n.id;refreshLayers();bimLyFocusEdit();}
    }else if(a==='sub'){
      if(!sel)return;
      n=bimLayerNew({parent:sel.id});
      if(n){A3D_LY.open[sel.id]=true;A3D_LY.sel=n.id;A3D_LY.edit=n.id;refreshLayers();bimLyFocusEdit();}
    }else if(a==='std'){
      openAddLayerDlg();
    }else if(a==='cur'){
      if(sel)bimLayerMakeCurrent(sel.id);
    }else if(a==='del'){
      if(sel&&bimLayerDelete(sel.id)){A3D_LY.sel=A3D.activeLayer;refreshLayers();}
    }
  }
  /* one set of delegated listeners on the dock panel, which outlives the Layers tab's markup */
  function bimWireLayersPanel(panel){
    if(!panel||panel.getAttribute('data-lywired'))return;
    panel.setAttribute('data-lywired','1');
    function inLyp(t){return !!(t&&t.closest&&t.closest('.a3d-lyp'));}
    panel.addEventListener('click',function(ev){
      var t=ev.target,b,l;
      if(!inLyp(t))return;
      try{
        if((b=t.closest('[data-lyact]'))){bimLyAct(b.getAttribute('data-lyact'));return;}
        if((b=t.closest('[data-lytog]'))){l=b.getAttribute('data-lytog');A3D_LY.open[l]=!A3D_LY.open[l];refreshLayers();return;}
        if((b=t.closest('[data-lycur]'))){if(bimLayerMakeCurrent(b.getAttribute('data-lycur')))A3D_LY.sel=A3D.activeLayer;refreshLayers();return;}
        if((b=t.closest('[data-lyon]'))){l=bimLayerById(b.getAttribute('data-lyon'));if(l)bimLayerSet(l.id,'visible',l.visible===false);return;}
        if((b=t.closest('[data-lyfrz]'))){l=bimLayerById(b.getAttribute('data-lyfrz'));if(l)bimLayerSet(l.id,'frozen',!l.frozen);return;}
        if((b=t.closest('[data-lylock]'))){l=bimLayerById(b.getAttribute('data-lylock'));if(l)bimLayerSet(l.id,'locked',!l.locked);return;}
        if((b=t.closest('[data-lypin]'))){var po=objById(b.getAttribute('data-lypin'));if(po)bimSetLocked(po,!bimIsLocked(po));return;}
        if(t.closest('input'))return;
        if((b=t.closest('[data-lyobj]'))){bimLySelectObj(b.getAttribute('data-lyobj'));return;}
        if((b=t.closest('[data-lyid]'))){A3D_LY.sel=b.getAttribute('data-lyid');refreshLayers();return;}
      }catch(eL){
        console.warn('[BIM] A Layers panel action failed',eL);
        a3dToast('That layer action could not be completed');
      }
    });
    panel.addEventListener('dblclick',function(ev){
      var n=inLyp(ev.target)?ev.target.closest('[data-lyname]'):null;
      if(!n)return;
      A3D_LY.edit=n.getAttribute('data-lyname');A3D_LY.sel=A3D_LY.edit;
      refreshLayers();bimLyFocusEdit();
    });
    panel.addEventListener('change',function(ev){
      var t=ev.target;
      if(inLyp(t)&&t.hasAttribute('data-lycol'))bimLayerSet(t.getAttribute('data-lycol'),'color',t.value);
    });
    panel.addEventListener('input',function(ev){
      var t=ev.target;
      if(inLyp(t)&&t.hasAttribute('data-lysearch')){A3D_LY.filter=t.value;refreshLayers();}
    });
    panel.addEventListener('keydown',function(ev){
      var t=ev.target;
      if(!inLyp(t)||!t.hasAttribute('data-lyren'))return;
      if(ev.key==='Enter'){ev.preventDefault();bimLyEndEdit(t,false);}
      else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();bimLyEndEdit(t,true);}
    });
    panel.addEventListener('focusout',function(ev){
      var t=ev.target;
      if(t&&t.hasAttribute&&t.hasAttribute('data-lyren'))bimLyEndEdit(t,false);
    });
    /* drag an object onto a layer to move it there; a layer onto a layer to put it under it, or onto
       the list below the rows to bring it back to the top */
    panel.addEventListener('dragstart',function(ev){
      var t=ev.target;
      if(!inLyp(t))return;
      var o=t.closest('[data-lyobj]'),l=t.closest('[data-lyid]');
      A3D_LY.drag=o?'obj:'+o.getAttribute('data-lyobj'):(l?'layer:'+l.getAttribute('data-lyid'):null);
      if(A3D_LY.drag){try{ev.dataTransfer.setData('text/plain',A3D_LY.drag);ev.dataTransfer.effectAllowed='move';}catch(eD){}}
    });
    panel.addEventListener('dragover',function(ev){
      var t=ev.target;
      if(A3D_LY.drag&&inLyp(t)&&(t.closest('[data-lyid]')||t.closest('[data-lylist]')))ev.preventDefault();
    });
    panel.addEventListener('drop',function(ev){
      var t=ev.target,v=A3D_LY.drag;
      A3D_LY.drag=null;
      if(!v||!inLyp(t))return;
      ev.preventDefault();
      var row=t.closest('[data-lyid]'),tgt=row?row.getAttribute('data-lyid'):null;
      try{
        if(v.indexOf('obj:')===0){if(tgt)bimObjSetLayer(v.slice(4),tgt);}
        else if(v.indexOf('layer:')===0&&v.slice(6)!==tgt){
          if(tgt)A3D_LY.open[tgt]=true;
          bimLayerSet(v.slice(6),'parent',tgt);
        }
      }catch(eX){
        console.warn('[BIM] A layer drop failed',eX);
        a3dToast('That could not be moved');
      }
    });
    panel.addEventListener('dragend',function(){A3D_LY.drag=null;});
  }
""", 14)

# ---- 2. the Layer fields in Properties list the tree
rep("""  function bimLayerOptionsHtml(curId){
    var i,h='';
    for(i=0;i<A3D.layers.length;i++){
      h+='<option value="'+A3D.layers[i].id+'"'+(A3D.layers[i].id===curId?' selected':'')+'>'+bimEsc(A3D.layers[i].name)+'</option>';
    }
    return h;
  }
""", r"""  function bimLayerOptionsHtml(curId){
    var h='';
    bimLayerTree().forEach(function(t){   /* __acad3dV121: the tree, sub-layers indented */
      var pad='',k;
      for(k=0;k<t.depth;k++)pad+='   ';
      h+='<option value="'+bimEsc(t.ly.id)+'"'+(t.ly.id===curId?' selected':'')+'>'+pad+bimEsc(t.ly.name)+'</option>';
    });
    return h;
  }
""")

# ---- 3. the rail: a Layers tab, first, as Rayon's rail has it
rep("    panel:'<rect x=\"2.5\" y=\"3\" width=\"13\" height=\"12\" rx=\"2\"/><path d=\"M7 3v12\"/>',\n",
    "    panel:'<rect x=\"2.5\" y=\"3\" width=\"13\" height=\"12\" rx=\"2\"/><path d=\"M7 3v12\"/>',\n"
    "    layers:'<path d=\"M9 2.5 16 6 9 9.5 2 6z\"/><path d=\"M2 9l7 3.5L16 9\"/><path d=\"M2 12l7 3.5 7-3.5\"/>',   /* __acad3dV121 */\n")
rep("      '<button type=\"button\" class=\"fl-rail-btn active\" data-tab=\"file\" data-fl-tab=\"file\" title=\"Project Browser\" aria-label=\"Project Browser\">'+\n",
    "      '<button type=\"button\" class=\"fl-rail-btn\" data-tab=\"layers\" data-fl-tab=\"layers\" title=\"Layers\" aria-label=\"Layers\">'+\n"
    "      bimRailIcon('layers')+'</button>'+   /* __acad3dV121 */\n"
    "      '<button type=\"button\" class=\"fl-rail-btn active\" data-tab=\"file\" data-fl-tab=\"file\" title=\"Project Browser\" aria-label=\"Project Browser\">'+\n")
rep("      if(tb)bimShellSetTab(tb.getAttribute('data-tab'));\n    });\n",
    "      if(tb)bimShellSetTab(tb.getAttribute('data-tab'));\n    });\n"
    "    bimWireLayersPanel(sh.querySelector('#figma-layers-panel'));   /* __acad3dV121 */\n")
rep("    if(shell.dataset.tab==='assets'&&!panel.querySelector('.a3d-assets')){\n",
    r"""    if(shell.dataset.tab==='layers'&&!panel.querySelector('.a3d-layers-wrap')){   /* __acad3dV121 */
      var lbox=document.createElement('div');
      lbox.className='fl-tab-content a3d-layers-wrap';
      lbox.innerHTML=bimLayersPanelHtml();
      panel.appendChild(lbox);
      did=true;
    }
    if(shell.dataset.tab!=='layers'){
      var lstale=panel.querySelector('.a3d-layers-wrap');
      if(lstale){lstale.parentNode.removeChild(lstale);did=true;}
    }
    if(shell.dataset.tab==='assets'&&!panel.querySelector('.a3d-assets')){
""")
rep("    try{bimCleanShell();}catch(eS){}\n",
    "    try{bimCleanShell();}catch(eS){}\n    bimLayersPanelRefresh();   /* __acad3dV121: the objects on each layer, and which are selected */\n")
rep('body.a3d-tree-docked #figma-layers-shell[data-tab="assets"] #figma-layers-panel > .a3d-tree{display:none}',
    '/* __acad3dV121: the tree is the Project Browser tab\'s alone */body.a3d-tree-docked #figma-layers-shell:not([data-tab="file"]) #figma-layers-panel > .a3d-tree{display:none}')
after_line("body.light-theme #figma-layers-rail{background:#f6f6f4;border-color:rgba(0,0,0,.1)}", r"""/* __acad3dV121: the Layers panel */
.a3d-lyp{display:flex;flex-direction:column;min-height:0;padding:6px 6px 14px;font:12px/1.3 Inter,system-ui,sans-serif;color:#c9d1d9}
.a3d-lyhd{display:flex;align-items:center;justify-content:space-between;padding:4px 4px 6px}
.a3d-lyttl{font-size:11px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;color:#aeb8c2}
.a3d-lybtns{display:flex;gap:2px}
.a3d-lyb{width:24px;height:24px;border:0;border-radius:6px;background:transparent;color:#9aa3ad;display:grid;place-items:center;cursor:pointer;padding:0}
.a3d-lyb:hover{background:rgba(255,255,255,.1);color:#fff}
.a3d-lyb svg,.a3d-lyi svg,.a3d-lycar svg{width:15px;height:15px}
.a3d-lysearch{margin:0 4px 6px;background:#1f2327;border:1px solid #3a4048;border-radius:6px;color:#e6eaef;padding:5px 8px;font:inherit;min-width:0}
.a3d-lylist{display:flex;flex-direction:column;min-height:48px;padding-bottom:24px}
.a3d-lyrow,.a3d-lyobj{display:flex;align-items:center;gap:3px;height:26px;padding-right:2px;border-radius:6px;cursor:grab;user-select:none}
.a3d-lyrow:hover,.a3d-lyobj:hover{background:rgba(255,255,255,.06)}
.a3d-lyrow.sel,.a3d-lyobj.sel{background:rgba(78,161,255,.18)}
.a3d-lyrow.dim .a3d-lynm{color:#6e7781}
.a3d-lyrow.cur .a3d-lynm{font-weight:600;color:#fff}
.a3d-lycar{width:16px;height:16px;flex:0 0 16px;border:0;background:transparent;color:#8b949e;display:grid;place-items:center;padding:0;cursor:pointer}
.a3d-lysw{width:14px;height:14px;flex:0 0 14px;padding:0;border:1px solid rgba(255,255,255,.25);border-radius:3px;background:none;cursor:pointer}
.a3d-lysw::-webkit-color-swatch-wrapper{padding:0}.a3d-lysw::-webkit-color-swatch{border:0;border-radius:2px}
.a3d-lynm{flex:1 1 auto;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.a3d-lyren{flex:1 1 auto;min-width:0;background:#1f2327;border:1px solid #4ea1ff;border-radius:4px;color:#fff;padding:2px 5px;font:inherit}
.a3d-lycnt{flex:0 0 auto;color:#6e7781;font-size:10.5px;min-width:12px;text-align:right}
.a3d-lyi{width:20px;height:22px;flex:0 0 20px;border:0;border-radius:5px;background:transparent;color:#5d6570;display:grid;place-items:center;cursor:pointer;padding:0}
.a3d-lyi:hover{background:rgba(255,255,255,.1);color:#dfe4ea}
.a3d-lyi.on{color:#e0b85e}
.a3d-lystat{width:14px;height:14px;flex:0 0 14px;border:0;background:transparent;color:#5d6570;display:grid;place-items:center;cursor:pointer;padding:0}
.a3d-lystat svg{width:12px;height:12px}.a3d-lystat:hover{color:#dfe4ea}.a3d-lystat.on{color:#4ea1ff}
.a3d-lydot{width:8px;height:8px;flex:0 0 8px;border-radius:2px}
.a3d-lyty{flex:0 0 auto;color:#6e7781;font-size:10px}
.a3d-lyobj .a3d-lynm{color:#aeb6bf}
.a3d-lyempty{padding:8px;color:#6e7781}
body.light-theme .a3d-lyp{color:#2b2f33}body.light-theme .a3d-lyttl{color:#555}
body.light-theme .a3d-lyrow:hover,body.light-theme .a3d-lyobj:hover{background:rgba(0,0,0,.05)}
body.light-theme .a3d-lyrow.cur .a3d-lynm{color:#000}body.light-theme .a3d-lyobj .a3d-lynm{color:#444}
body.light-theme .a3d-lysearch,body.light-theme .a3d-lyren{background:#fff;border-color:#c9ced4;color:#222}
body.light-theme .a3d-lyb,body.light-theme .a3d-lyi{color:#7a828c}body.light-theme .a3d-lyb:hover,body.light-theme .a3d-lyi:hover{background:rgba(0,0,0,.07);color:#111}
""")

# ---- 4. the shell audit claims the panel's controls, and lets go of the ones that went
rep("    {sel:'.fl-rail-btn[data-tab=\"file\"]',why:'Project Browser tab'},\n",
    "    {sel:'.fl-rail-btn[data-tab=\"layers\"]',why:'Layers tab: the layer tree and the objects on each layer'},   /* __acad3dV121 */\n"
    "    {sel:'[data-lyact]',why:'Layers panel action: new layer, sub-layer, standard layer, make current, delete'},\n"
    "    {sel:'[data-lytog]',why:'opens or closes a layer in the Layers panel'},\n"
    "    {sel:'[data-lycur]',why:'makes a layer current'},\n"
    "    {sel:'[data-lyon]',why:'turns a layer on or off'},\n"
    "    {sel:'[data-lyfrz]',why:'freezes or thaws a layer'},\n"
    "    {sel:'[data-lylock]',why:'locks or unlocks a layer'},\n"
    "    {sel:'[data-lypin]',why:'pins or unpins an object in the Layers panel'},\n"
    "    {sel:'.fl-rail-btn[data-tab=\"file\"]',why:'Project Browser tab'},\n")
rep("    {sel:'.a3d-lyrvis',why:'toggles layer visibility'},\n    {sel:'.a3d-lyrlock',why:'toggles layer lock'},\n"
    "    {sel:'.a3d-btgl',why:'toggles object lock in the browser'},\n", "")

# ---- 5. what the panel replaces: the browser's Layers and Model groups, +Lyr, the hidden rows
span("    // ---- Layers (with visibility + lock, which is what was missing) ----\n", "    el.browser.innerHTML=h;\n",
     "    /* __acad3dV121: the Layers and Model groups moved to the Layers panel, where the model is the\n"
     "       layers' contents */\n", 29)
rep("    schedules:false,families:false,layers:false,model:true,sheets:false,classifications:false};\n",
    "    schedules:false,families:false,sheets:false,classifications:false};\n")
rep("  function bimBrowserLeaf(label,attrs,depth,extra){\n",
    "  function bimBrowserLeaf(label,attrs,depth,extra){\n"
    "    /* __acad3dV121: the browser's search filters every leaf; it filtered only the Model group, which\n"
    "       moved to the Layers panel */\n"
    "    if(A3D.browserFilter&&String(label).toLowerCase().indexOf(A3D.browserFilter)<0)return '';\n")
rep("      if((b=cl('[data-a3dblock]'))){ev.stopPropagation();var o=objById(b.getAttribute('data-a3dblock'));if(o){bimSetLocked(o,!bimIsLocked(o));}return;}\n"
    "      if((b=cl('[data-a3dblayerlock]'))){ev.stopPropagation();var bl=bimLayerById(b.getAttribute('data-a3dblayerlock'));if(bl)bimLayerSet(bl.id,'locked',!bl.locked);return;}\n"
    "      if((b=cl('[data-a3dblayervis]'))){ev.stopPropagation();var bv=bimLayerById(b.getAttribute('data-a3dblayervis'));if(bv)bimLayerSet(bv.id,'visible',bv.visible===false);return;}\n",
    "")
rep("      if((b=cl('[data-a3dblayer]'))){setActiveLayer(b.getAttribute('data-a3dblayer'));refreshBrowser();return;}\n", "")
rep("""      if((b=cl('[data-a3did]'))){
        A3D.sel=b.getAttribute('data-a3did');
        A3D.selSet=A3D.sel?[A3D.sel]:[];
        var trOpen=root.querySelector('.a3d-tree.open');
        if(trOpen)trOpen.classList.remove('open');
        refreshTree();paint();
        return;
      }
""", "")
rep("            '<button class=\"a3d-palbtn\" id=\"a3d-layeradd\" title=\"Add Layer\">+Lyr</button>'+\n", "")
rep("        '<div id=\"a3d-layerrows\" style=\"display:none\"></div>'+\n", "")
span("    el.layerrows=root.querySelector('#a3d-layerrows');\n", "    el.schedbody=root.querySelector('#a3d-schedbody');\n", "", 23)

# ---- the hidden object rows' pin mark was an emoji too
rep("(bimIsLocked(o)?'<span class=\"a3d-lockicon\" title=\"Locked (Pin)\">\\ud83d\\udd12</span>':'')",
    "(bimIsLocked(o)?'<span class=\"a3d-lockicon\" title=\"Locked (Pin)\">'+BIM_LOCK_ON+'</span>':'')   /* __acad3dV121: not an emoji */")

# ---- the injected stylesheet's rules for what went: the hidden rows, and the browser's swatch, type and toggle
rep("""    '#a3d-layerrows{overflow:auto;flex:1 1 auto}'+
    '.a3d-layerrow{display:flex;align-items:center;gap:5px;padding:5px 8px;border-bottom:1px solid #24282d;cursor:pointer}'+
    '.a3d-layerrow:hover{background:#262b31}'+
    '.a3d-layerrow.active{background:#2b3d52}'+
    '.a3d-lyrdot{width:9px;height:9px;border-radius:2px;flex:0 0 auto}'+
    '.a3d-lyrnm{flex:1 1 auto;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-size:11px;color:#dfe4ea}'+
    '.a3d-lyrvis,.a3d-lyrlock{background:transparent;border:none;color:#aeb6bf;cursor:pointer;padding:0;width:16px;height:16px;flex:0 0 auto}'+
    '.a3d-lyrvis svg,.a3d-lyrlock svg{width:14px;height:14px}'+
    '.a3d-lyrvis.off{color:#565c64}'+
    '.a3d-lyrlock.on{color:#e0b85e}'+
""", "")
rep("""    '.a3d-bty{color:#6e7781;font-size:9px;flex:0 0 auto}'+
    '.a3d-bswatch{width:8px;height:8px;border-radius:2px;display:inline-block}'+
    '.a3d-btgl{background:transparent;border:0;color:#6e7781;cursor:pointer;font-size:10px;padding:0 2px;flex:0 0 auto;line-height:1}'+
    '.a3d-btgl:hover{color:#dfe4ea}'+
    '.a3d-btgl.on{color:#e0b060}'+
""", "")
rep("    '.a3d-lockicon{font-size:10px;opacity:0.8;margin-right:2px}'+\n",
    "    '.a3d-lockicon{display:inline-flex;opacity:0.8;margin-right:2px}.a3d-lockicon svg{width:10px;height:10px}'+   /* __acad3dV121 */\n")

# ---- 6. hooks for a suite's setup; the claims are driven through the panel itself
rep("  window.__a3dSetLayer=setActiveLayer;\n", r"""  window.__a3dSetLayer=setActiveLayer;
  /* __acad3dV121: the layer rules, for a suite to set a scene up with */
  window.__a3dLayerSet=function(id,f,v){return bimLayerSet(id,f,v);};
  window.__a3dLayerNew=function(o){var l=bimLayerNew(o||{});return l?l.id:null;};
  window.__a3dLayerDelete=function(id){return bimLayerDelete(id);};
  window.__a3dLayerCurrent=function(id){return bimLayerMakeCurrent(id);};
  window.__a3dObjLayer=function(oid,lid){return bimObjSetLayer(oid,lid);};
  window.__a3dLayerState=function(oid){
    var o=objById(oid);
    return o?{shown:bimLayerShown(o),pickable:bimLayerPickable(o),alpha:bimLayerAlpha(o),look:bimLayerLook(o)}:null;
  };
""")

# ---- nothing is left of what the panel replaced
code = re.sub(r'/\*.*?\*/', '', t, flags=re.S)
for dead in ('a3dblayer', 'a3dblock', 'a3dblayervis', 'a3dblayerlock', 'a3d-layeradd', 'a3d-layerrows', 'layerrows',
             'data-lyrvis', 'data-lyrlock', 'data-lyrdel', 'data-a3dlyr', 'a3d-lyrvis', 'a3d-lyrlock', 'a3d-btgl',
             'a3d-bswatch', 'a3d-bty', '\\ud83d'):
    if dead in code:
        sys.exit('ABORT: still referenced: ' + dead)
