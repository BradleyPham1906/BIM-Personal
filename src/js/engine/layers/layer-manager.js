  /* ================= __acad3dV121: the Layer Properties Manager (LAYER, LA) =================
     AutoCAD's table: Status, Name, On, Freeze, Lock, Plot, Color, Linetype, Lineweight,
     Transparency -- with the object count and Description -- in tree order, sub-layers indented.
     Every cell goes through V121b's rules, and after every edit the table is drawn again from the
     layers, so a refused change cannot go on showing what was refused. The picked row (A3D_LPM.sel)
     is what New sub-layer, Delete and Set current act on; neither it nor the search is saved. */
  var A3D_LPM={sel:null,filter:''};
  var BIM_LPM_IC={
    plot:ric('<path d="M7 9V4h10v5"/><rect x="4" y="9" width="16" height="7" rx="1.5"/><path d="M7 14h10v6H7z"/>'),
    noplot:ric('<path d="M7 9V4h10v5"/><rect x="4" y="9" width="16" height="7" rx="1.5"/><path d="M7 14h10v6H7z"/><path d="M3 3l18 18"/>'),
    close:ric('<path d="M6 6l12 12M18 6 6 18"/>')
  };
  function bimLpmOpen(){return !!(el.dlg&&el.dlg.parentNode&&el.dlg.classList.contains('a3d-lpm'));}
  function bimLpmLwText(v){return (v===null||v===undefined||!isFinite(v))?'Default':(+v).toFixed(2)+' mm';}
  /* a switch shows the state that is not the default -- off, frozen, locked, not plotted -- lit */
  function bimLpmTgl(field,lit,titleLit,titleNot,icLit,icNot){
    var tt=bimEsc(lit?titleLit:titleNot);
    return '<button type="button" class="a3d-lyi'+(lit?' on':'')+'" data-lpmtgl="'+field+'" title="'+tt+'" aria-label="'+tt+
      '" aria-pressed="'+(lit?'true':'false')+'">'+(lit?icLit:icNot)+'</button>';
  }
  function bimLpmBtn(a,label,ic){
    return '<button type="button" class="a3d-lpmbtn" data-lpmact="'+a+'" title="'+bimEsc(label)+'">'+ic+'<span>'+bimEsc(label)+'</span></button>';
  }
  function bimLpmTableHtml(){
    var con=bimLayerContents(),f=String(A3D_LPM.filter||'').toLowerCase(),cur=A3D.activeLayer,tree=bimLayerTree();
    var sel=bimLayerById(A3D_LPM.sel)?A3D_LPM.sel:cur,keep={},rows='',shown=0;
    /* a match brings its parents with it, so a sub-layer is never listed without its place */
    if(f)tree.forEach(function(t){
      if(String(t.ly.name).toLowerCase().indexOf(f)>=0)bimLayerChain(t.ly).forEach(function(a){keep[a.id]=1;});
    });
    tree.forEach(function(t){
      var l=t.ly;
      if(f&&!keep[l.id])return;
      shown++;
      var id=bimEsc(l.id),nm=bimEsc(l.name),isCur=(l.id===cur),s=bimLayerEff(l),k;
      var lt=(bimLinetypeDef(l.linetype)||BIM_LINETYPES[0]).name;
      var lw=(l.lineweight===undefined||l.lineweight===null||!isFinite(l.lineweight))?null:+l.lineweight;
      var tr=isFinite(l.transparency)?+l.transparency:0;
      var col=/^#[0-9a-fA-F]{6}$/.test(l.color||'')?l.color.toLowerCase():'#7f9db8';
      var lto='',lwo='<option value=""'+(lw===null?' selected':'')+'>Default</option>';
      for(k=0;k<BIM_LINETYPES.length;k++)
        lto+='<option value="'+BIM_LINETYPES[k].name+'" title="'+bimEsc(BIM_LINETYPES[k].desc)+'"'+(BIM_LINETYPES[k].name===lt?' selected':'')+'>'+BIM_LINETYPES[k].name+'</option>';
      for(k=0;k<BIM_LINEWEIGHTS.length;k++)
        lwo+='<option value="'+BIM_LINEWEIGHTS[k]+'"'+(BIM_LINEWEIGHTS[k]===lw?' selected':'')+'>'+bimLpmLwText(BIM_LINEWEIGHTS[k])+'</option>';
      rows+='<tr class="a3d-lpmrow'+(l.id===sel?' sel':'')+(isCur?' cur':'')+((!s.on||s.frozen)?' dim':'')+'" data-lpmid="'+id+'">'+
        '<td><button type="button" class="a3d-lystat'+(isCur?' on':'')+'" data-lpmcur="'+id+'" title="'+(isCur?nm+' is the current layer':'Make '+nm+' current')+
          '" aria-label="'+(isCur?nm+' is the current layer':'Make '+nm+' current')+'" aria-pressed="'+(isCur?'true':'false')+'">'+(isCur?BIM_LY_IC.cur:BIM_LY_IC.notcur)+'</button></td>'+
        '<td class="a3d-lpmname"><input type="text" data-lpmf="name" value="'+nm+'" style="margin-left:'+(t.depth*16)+'px" aria-label="Name of '+nm+'"></td>'+
        '<td>'+bimLpmTgl('visible',l.visible===false,'Turn '+nm+' on','Turn '+nm+' off',BIM_LY_IC.off,BIM_LY_IC.on)+'</td>'+
        '<td>'+bimLpmTgl('frozen',!!l.frozen,'Thaw '+nm,'Freeze '+nm,BIM_LY_IC.frozen,BIM_LY_IC.thawed)+'</td>'+
        '<td>'+bimLpmTgl('locked',!!l.locked,'Unlock '+nm,'Lock '+nm,BIM_LY_IC.locked,BIM_LY_IC.unlocked)+'</td>'+
        '<td>'+bimLpmTgl('plot',l.plot===false,'Plot '+nm,'Do not plot '+nm,BIM_LPM_IC.noplot,BIM_LPM_IC.plot)+'</td>'+
        '<td><input type="color" class="a3d-lysw" data-lpmf="color" value="'+col+'" aria-label="Color of '+nm+'"><span class="a3d-lpmhex">'+col+'</span></td>'+
        '<td><select data-lpmf="linetype" aria-label="Linetype of '+nm+'">'+lto+'</select></td>'+
        '<td><select data-lpmf="lineweight" aria-label="Lineweight of '+nm+'">'+lwo+'</select></td>'+
        '<td><input type="number" min="0" max="90" step="1" data-lpmf="transparency" value="'+tr+'" aria-label="Transparency of '+nm+'"></td>'+
        '<td class="a3d-lpmcnt">'+(con[l.id]||[]).length+'</td>'+
        '<td class="a3d-lpmdesc"><input type="text" data-lpmf="description" value="'+bimEsc(typeof l.description==='string'?l.description:'')+'" aria-label="Description of '+nm+'"></td>'+
        '</tr>';
    });
    return '<table class="a3d-lpmt"><thead><tr><th title="The current layer">Status</th><th>Name</th><th>On</th><th>Freeze</th><th>Lock</th><th>Plot</th>'+
      '<th>Color</th><th>Linetype</th><th>Lineweight</th><th>Transparency</th><th>Objects</th><th>Description</th></tr></thead><tbody>'+rows+
      '</tbody></table>'+(shown?'':'<div class="a3d-lyempty">No layer matches</div>');
  }
  function bimLayerManagerRefresh(){
    if(!bimLpmOpen())return;
    var body=el.dlg.querySelector('.a3d-lpmbody'),ft=el.dlg.querySelector('.a3d-lpmft'),cur=bimLayerById(A3D.activeLayer);
    bimRenderInto(body,bimLpmTableHtml());
    if(ft)ft.textContent=A3D.layers.length+' layer'+(A3D.layers.length===1?'':'s')+'. Current layer: '+(cur?cur.name:'none')+'.';
  }
  function bimLpmFocusName(id){
    var r=el.dlg?el.dlg.querySelector('[data-lpmid="'+String(id).replace(/"/g,'')+'"] [data-lpmf="name"]'):null;
    if(r){try{r.focus();r.select();}catch(eF){console.warn('[BIM] The layer name field could not take the focus',eF);}}
  }
  function bimLpmAct(a){
    var sel=bimLayerById(A3D_LPM.sel)||bimLayerById(A3D.activeLayer),n;
    if(a==='close'){closeDlg();return;}
    if(a==='new'){
      n=bimLayerNew({from:sel?sel.id:null});
      if(n){A3D_LPM.sel=n.id;bimLayerManagerRefresh();bimLpmFocusName(n.id);}
    }else if(a==='sub'){
      if(!sel)return;
      n=bimLayerNew({parent:sel.id});
      if(n){A3D_LY.open[sel.id]=true;A3D_LPM.sel=n.id;bimLayerManagerRefresh();bimLpmFocusName(n.id);}
    }else if(a==='del'){
      if(sel&&bimLayerDelete(sel.id))A3D_LPM.sel=A3D.activeLayer;
      bimLayerManagerRefresh();
    }else if(a==='cur'){
      if(sel)bimLayerMakeCurrent(sel.id);
      bimLayerManagerRefresh();
    }
  }
  function bimWireLayerManager(d){
    function rowOf(t){var r=(t&&t.closest)?t.closest('[data-lpmid]'):null;return r?bimLayerById(r.getAttribute('data-lpmid')):null;}
    d.addEventListener('click',function(ev){
      var t=ev.target,b,l,f;
      try{
        if((b=t.closest('[data-lpmact]'))){bimLpmAct(b.getAttribute('data-lpmact'));return;}
        if((b=t.closest('[data-lpmcur]'))){if(bimLayerMakeCurrent(b.getAttribute('data-lpmcur')))A3D_LPM.sel=A3D.activeLayer;bimLayerManagerRefresh();return;}
        if((b=t.closest('[data-lpmtgl]'))){
          l=rowOf(b);
          if(!l)return;
          f=b.getAttribute('data-lpmtgl');
          bimLayerSet(l.id,f,(f==='visible'||f==='plot')?(l[f]===false):!l[f]);
          bimLayerManagerRefresh();
          return;
        }
        if(t.closest('input,select'))return;
        l=rowOf(t);
        if(l){A3D_LPM.sel=l.id;bimLayerManagerRefresh();}
      }catch(eC){
        console.warn('[BIM] A Layer Properties Manager action failed',eC);
        a3dToast('That layer change could not be made');
      }
    });
    d.addEventListener('change',function(ev){
      var t=ev.target,f=(t&&t.getAttribute)?t.getAttribute('data-lpmf'):null,l=rowOf(t);
      if(!f||!l)return;
      try{bimLayerSet(l.id,f,t.value);}
      catch(eF){console.warn('[BIM] A layer field could not be set',eF);a3dToast('That layer change could not be made');}
      bimLayerManagerRefresh();
    });
    d.addEventListener('input',function(ev){
      var t=ev.target;
      if(t&&t.hasAttribute&&t.hasAttribute('data-lpmsearch')){A3D_LPM.filter=t.value;bimLayerManagerRefresh();}
    });
    d.addEventListener('keydown',function(ev){
      if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();}
    });
  }
  function bimLayerManagerOpen(){
    try{
      closeDlg();
      var d=document.createElement('div');
      d.className='a3d-dlg a3d-lpm';
      d.setAttribute('role','dialog');
      d.setAttribute('aria-label','Layer Properties Manager');
      d.innerHTML='<div class="a3d-dlghd a3d-lpmhd"><span>Layer Properties Manager</span>'+
        '<button type="button" class="a3d-lpmx" data-lpmact="close" title="Close" aria-label="Close">'+BIM_LPM_IC.close+'</button></div>'+
        '<div class="a3d-lpmtb">'+
          bimLpmBtn('new','New layer',BIM_LY_IC.add)+
          bimLpmBtn('sub','New sub-layer',BIM_LY_IC.sub)+
          bimLpmBtn('del','Delete',BIM_LY_IC.del)+
          bimLpmBtn('cur','Set current',BIM_LY_IC.make)+
          '<input type="text" class="a3d-lysearch" data-lpmsearch="1" placeholder="Search for layer" aria-label="Search for layer" value="'+bimEsc(A3D_LPM.filter||'')+'">'+
        '</div><div class="a3d-lpmbody"></div><div class="a3d-lpmft"></div>';
      el.root.appendChild(d);
      el.dlg=d;
      bimWireLayerManager(d);
      bimLayerManagerRefresh();
      return true;
    }catch(eM){
      console.warn('[BIM] The Layer Properties Manager could not open',eM);
      a3dToast('The Layer Properties Manager could not open');
      return false;
    }
  }
  function bimEsc(s){
    return String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }
  function bimLayerOptionsHtml(curId){
    var h='';
    bimLayerTree().forEach(function(t){   /* __acad3dV121: the tree, sub-layers indented */
      var pad='',k;
      for(k=0;k<t.depth;k++)pad+='\u00a0\u00a0\u00a0';
      h+='<option value="'+bimEsc(t.ly.id)+'"'+(t.ly.id===curId?' selected':'')+'>'+pad+bimEsc(t.ly.name)+'</option>';
    });
    return h;
  }
