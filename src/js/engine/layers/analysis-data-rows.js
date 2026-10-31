  /* ================= __acad3dV148: Analysis and Data, in Layers =================
     A row's key is its section and its id: res:<id> a result layer, data:<id> a data layer. */
  var BIM_LY_IC_UPD='<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M19.5 12a7.5 7.5 0 1 1-2.2-5.3M19.5 4.5v4.2h-4.2"/></svg>';
  function bimLyKey(k){k=String(k||'');var i=k.indexOf(':');return {t:i>0?k.slice(0,i):'',id:i>0?k.slice(i+1):''};}
  function bimLyTarget(k){var s=bimLyKey(k);return s.t==='res'?bimResById(s.id):s.t==='data'?bimDataById(s.id):null;}
  function bimResSwatch(R){
    if(R.kind==='tool'){var K=(R.data&&R.data.keys)||[];return K.length>1?'linear-gradient(90deg,'+K.map(function(k){return k.col;}).join(',')+')':(K.length?K[0].col:'#888');}   /* __acad3dV172 */
    if(R.kind==='walk')return 'linear-gradient(90deg,#cde2fb,#5598e7,#1c5cab)';   /* __acad3dV161 */
    var c=R.kind==='sunhours'?BIM_SIM_RAMP:R.kind==='rain'?['#7fb6f0','#2f7fe0','#1565c0']:R.mode==='slope'?BIM_SLOPE_COLS:R.mode==='elevation'?BIM_ELEV_COLS:
      R.mode==='cutfill'?BIM_CUTFILL_COLS:BIM_ASPECT.map(function(a){return a.c;});
    return 'linear-gradient(90deg,'+c.join(',')+')';
  }
  function bimResLegendHtml(R){
    var o,b=null,d=R.data;
    if(R.kind==='sunhours'&&d)return '<div class="a3d-anzleg"><span>0 h</span><span class="a3d-anzramp">'+BIM_SIM_RAMP.map(function(c){return '<i style="background:'+c+'"></i>';}).join('')+'</span><span>'+bimDispNum(d.day,1)+' h</span></div>';
    if(R.kind==='rain')return '<div class="a3d-lyleg"><span><i style="background:#2f7fe0"></i>Ponds</span><span><i class="ln" style="background:#1565c0"></i>Flow lines</span></div>';
    if(R.kind==='walk')return bimResGone(R)?'':'<div class="a3d-lyleg">'+['5 min or less','5 to 10 min','10 to 15 min'].map(function(n,j){return '<span><i class="ln" style="background:'+['#cde2fb','#5598e7','#1c5cab'][j]+'"></i>'+n+'</span>';}).join('')+
      '<span><i style="background:#fff;border:1.5px solid #111;border-radius:1px"></i>Bus or tram stop</span><span><i style="background:#fff;border:1.5px solid #111;border-radius:50%"></i>Rail or metro</span></div>';   /* __acad3dV161 */
    if(R.kind==='tool')return d&&d.keys&&d.keys.length?'<div class="a3d-lyleg">'+d.keys.map(function(k){return '<span><i style="background:'+bimEsc(k.col)+'"></i>'+bimEsc(k.name)+'</span>';}).join('')+'</div>':'';   /* __acad3dV172 */
    if(R.kind!=='terrain'||bimResGone(R))return '';
    o=objById(R.src);
    try{b=bimBandsOf(o,R.mode);}catch(eB){b=null;}
    return b?'<div class="a3d-lyleg">'+b.bands.filter(function(x){return x.area>0;}).map(function(x){return '<span><i style="background:'+x.col+'"></i>'+bimEsc(x.label)+'</span>';}).join('')+'</div>':'';
  }
  function bimResMetaText(R){
    var d=R.data,o=objById(R.src),s='';
    if(R.kind==='sunhours'&&d)s='Direct sun on the ground on '+d.date+': '+bimDispNum(d.min,1)+' to '+bimDispNum(d.max,1)+' h of '+bimDispNum(d.day,1)+' h; '+Math.round((d.sixPlus||0)*100)+'% has 6 h or more.';
    else if(R.kind==='rain'&&d)s=d.ponds+' pond'+(d.ponds===1?'':'s')+(d.ponds?', '+bimDispNum(d.pondVolume,1)+' m\u00b3 held, the deepest '+bimDispNum(d.deepest||0,2)+' m':'')+
      '; flow lines where '+bimDispNum(d.threshold*d.cell*d.cell,0)+' m\u00b2 or more drains.';
    else if(R.kind==='walk'){var S=A3D.site&&A3D.site.access;s=bimResGone(R)?'The access data it showed is gone: Get access and people in Site analysis brings it back.':
      'Walk times from the '+(S.lot&&S.lot.ring?'lot':'site point')+' along the streets at '+S.speed+' m a minute, from OpenStreetMap data of '+S.fetched+': 5, 10 and 15 minutes. It follows the access data, so a refresh in Site analysis updates it.';}   /* __acad3dV161 */
    else if(R.kind==='terrain')s=bimResGone(R)?'The surface it showed is gone, or is no longer a proposed one.':BIM_TVIEW_LABEL[R.mode]+' of '+o.name+'. It follows the surface, so it is never out of date.';
    else if(R.kind==='tool'){var th=bimTlRunById(R.run),tt=bimTlTool(R.tool);s=(tt?tt.name:'A tool')+'\'s output'+(th?', from the run of '+th.at+(th.sum?': '+th.sum:''):'')+'. Update runs it again with the same parameters.';   /* __acad3dV172 */
      if(bimTlStale(R))s+=' The lot has changed since: Update runs it on the lot as it is now.';}
    if(R.kind!=='terrain'&&R.kind!=='walk'&&R.kind!=='tool'&&bimResStale(R))s+=' The model has changed since: Update runs it again'+(R.kind==='sunhours'?' for '+(d&&d.date):'')+'.';
    return s+(R.created?' Added '+R.created+(R.updated?', updated '+R.updated:'')+'.':'');
  }
  function bimLyNameHtml(key,name){
    return A3D_LY.redit===key?'<input type="text" class="a3d-lyren" data-lyresren="'+bimEsc(key)+'" value="'+bimEsc(name)+'" aria-label="Name of the layer">':
      '<span class="a3d-lynm" data-lyresname="'+bimEsc(key)+'" title="'+bimEsc(name)+' -- double-click to rename">'+bimEsc(name)+'</span>';
  }
  function bimLyOpacityHtml(key,name,op){
    op=Math.round(op*100);
    return '<label class="a3d-lyopl">Opacity<input type="range" min="10" max="100" step="5" value="'+op+'" data-lyresop="'+bimEsc(key)+'" aria-label="Opacity of '+bimEsc(name)+'"><span class="a3d-lyopv">'+op+'%</span></label>';
  }
  function bimLyResRowHtml(R){
    var key='res:'+R.id,sel=A3D_LY.rsel===key,hid=R.visible===false,gone=bimResGone(R),st=!gone&&bimResStale(R),h;
    h='<div class="a3d-lyres'+(sel?' sel':'')+(hid?' dim':'')+'" data-lyres="'+bimEsc(key)+'" draggable="true" aria-expanded="'+sel+'">'+
      '<span class="a3d-lyramp" style="background:'+bimResSwatch(R)+'"></span>'+bimLyNameHtml(key,R.name)+
      (gone?'<span class="a3d-lybadge gone" title="'+(R.kind==='walk'?'The access data it showed is gone':'The surface it showed is gone')+'">Gone</span>':st?'<span class="a3d-lybadge" title="The model has changed since it was run">Out of date</span>':'')+
      bimLyTgl('lyreson',key,hid,hid?'Show '+R.name:'Hide '+R.name,BIM_LY_IC.off,BIM_LY_IC.on)+'<span class="a3d-lyi a3d-lyspc" aria-hidden="true"></span><span class="a3d-lyi a3d-lyspc" aria-hidden="true"></span>'+'</div>';   /* __acad3dV158: in the eye column */
    if(sel)h+='<div class="a3d-lyresd" data-lyresd="'+bimEsc(key)+'">'+bimLyOpacityHtml(key,R.name,bimResOpacity(R))+bimResLegendHtml(R)+
      '<div class="a3d-lyresmeta">'+bimEsc(bimResMetaText(R))+'</div><div class="a3d-lyresacts">'+
      (R.kind!=='terrain'&&R.kind!=='walk'?'<button type="button" data-lyresupd="'+bimEsc(key)+'"'+(st?' class="pri"':'')+'>Update</button>':'')+
      '<button type="button" data-lyresrn="'+bimEsc(key)+'">Rename</button><button type="button" class="danger" data-lyresdel="'+bimEsc(key)+'">Remove</button></div></div>';
    return h;
  }
  function bimLyDataRowHtml(L){
    var key='data:'+L.id,sel=A3D_LY.rsel===key,hid=!L.visible,n=bimDataFeats(L.id).length,h,col=/^#[0-9a-fA-F]{6}$/.test(L.color||'')?L.color:'#7f9db8';
    h='<div class="a3d-lyres'+(sel?' sel':'')+(hid?' dim':'')+'" data-lyres="'+bimEsc(key)+'" aria-expanded="'+sel+'">'+
      '<span class="a3d-lyramp" style="background:'+col+'"></span>'+bimLyNameHtml(key,L.name)+
      (L.status&&L.status.error?'<span class="a3d-lybadge gone" title="'+bimEsc(bimDataStatusText(L))+'">Failed</span>':'')+
      bimLyTgl('lyreson',key,hid,hid?'Show '+L.name:'Hide '+L.name,BIM_LY_IC.off,BIM_LY_IC.on)+'<span class="a3d-lyi a3d-lyspc" aria-hidden="true"></span><span class="a3d-lyi a3d-lyspc" aria-hidden="true"></span>'+'</div>';
    if(sel)h+='<div class="a3d-lyresd" data-lyresd="'+bimEsc(key)+'">'+bimLyOpacityHtml(key,L.name,bimDataOpacity(L))+
      '<div class="a3d-lyresmeta">'+bimEsc(bimDataStatusText(L)+(n?'; '+n+' feature'+(n===1?'':'s'):'')+(L.credit?'. Source: '+L.credit:''))+'</div><div class="a3d-lyresacts">'+
      '<button type="button" data-lyresset="'+bimEsc(key)+'">Settings</button><button type="button" data-lyresrn="'+bimEsc(key)+'">Rename</button>'+
      '<button type="button" class="danger" data-lyresdel="'+bimEsc(key)+'">Remove</button></div></div>';
    return h;
  }
  function bimLySectionsHtml(f){
    var shut=A3D_LY.secShut||{},rb='',db='';
    function hit(s){return !f||String(s).toLowerCase().indexOf(f)>=0;}
    bimResLayers().forEach(function(R){if(hit(R.name))rb+=bimLyResRowHtml(R);});
    bimDataList().forEach(function(L){if(hit(L.name))db+=bimLyDataRowHtml(L);});
    /* __acad3dV158: the group's row, a layer row's columns: caret, status, swatch, name, count, eye */
    function sec(key,label,n,body,empty){
      if(f&&!body)return '';
      var open=!!f||!shut[key],off=bimLySecHidden(key),sw=key==='analysis'?'linear-gradient(135deg,#f6c445,#e0603b 55%,#2f7fe0)':'#7f9db8';
      return '<div class="a3d-lysec'+(off?' dim':'')+'" data-lysec="'+key+'"><div class="a3d-lysechd"><button type="button" class="a3d-lycar" data-lysectog="'+key+'" aria-expanded="'+open+'" title="'+
        (open?'Close ':'Open ')+label+'" aria-label="'+(open?'Close ':'Open ')+label+'">'+(open?BIM_LY_IC.open:BIM_LY_IC.closed)+'</button>'+
        '<span class="a3d-lystat" aria-hidden="true"></span><span class="a3d-lygsw" style="background:'+sw+'"></span>'+
        '<span class="a3d-lynm a3d-lysecttl">'+label+'</span><span class="a3d-lycnt">'+(n||'')+'</span>'+
        bimLyTgl('lysecon',key,off,(off?'Show ':'Hide ')+'everything in '+label,BIM_LY_IC.off,BIM_LY_IC.on)+'<span class="a3d-lyi a3d-lyspc" aria-hidden="true"></span><span class="a3d-lyi a3d-lyspc" aria-hidden="true"></span>'+'</div>'+
        (open?(body||'<div class="a3d-lyempty a3d-lyhint">'+empty+'</div>'):'')+'</div>';
    }
    return sec('analysis','Analysis',bimResLayers().length,rb,'Results you keep from Analyze, with Add as layer, are listed here')+
      sec('data','Data',bimDataList().length,db,'Data layers added in Properties, Site, Data Layers, are listed here');
  }
  /* __acad3dV158: a group is hidden when it holds layers and none of them shows */
  function bimLySecItems(key){return key==='analysis'?bimResLayers():key==='data'?bimDataList():null;}
  function bimLySecHidden(key){
    var L=bimLySecItems(key)||[],i;
    if(!L.length)return false;
    for(i=0;i<L.length;i++)if(key==='analysis'?L[i].visible!==false:!!L[i].visible)return false;
    return true;
  }
  /* the group's eye: everything in it shown, or hidden, in one undo step */
  function bimLySecVisible(key,v){
    var L=bimLySecItems(key),i;
    if(!L)return null;
    if(!L.length){a3dToast('Nothing in '+(key==='analysis'?'Analysis':'Data')+' yet');return null;}
    if(v===undefined)v=bimLySecHidden(key);
    v=!!v;
    pushUndo();
    for(i=0;i<L.length;i++){
      L[i].visible=v;
      if(key==='data'&&!v&&A3D_DATA.sel&&A3D_DATA.sel.layer===L[i].id)A3D_DATA.sel=null;
    }
    refreshLayers();refreshProps();paint();saveSoon();
    return v;
  }
  /* ---- a row's actions, either section ---- */
  function bimLyResVisible(k){
    var s=bimLyKey(k),T=bimLyTarget(k);
    if(!T)return false;
    if(s.t==='res')return bimResultLayerSet(s.id,'visible',T.visible===false);
    var ok=bimDataSet(s.id,'visible',!T.visible);
    refreshLayers();
    return ok;
  }
  function bimLyResSetOpacity(k,v){
    var s=bimLyKey(k),ok;
    if(s.t==='res')return bimResultLayerSet(s.id,'opacity',v);
    if(s.t!=='data')return false;
    ok=bimDataSet(s.id,'opacity',v);
    refreshLayers();
    return ok;
  }
  function bimLyResRename(k,name){
    var s=bimLyKey(k),ok;
    if(s.t==='res')return bimResultLayerSet(s.id,'name',name);
    if(s.t!=='data')return false;
    ok=bimDataSet(s.id,'name',name);
    refreshLayers();
    return ok;
  }
  function bimLyResRemove(k){
    var s=bimLyKey(k),ok;
    if(s.t==='res')return bimResultLayerRemove(s.id);
    if(s.t!=='data')return false;
    ok=bimDataRemove(s.id);
    if(A3D_LY.rsel===k)A3D_LY.rsel=null;
    refreshLayers();
    return ok;
  }
  /* the opacity while it is dragged: shown, not yet an edit; let go, it is one undo step */
  function bimLyResOpPreview(inp){
    var k=inp.getAttribute('data-lyresop'),T=bimLyTarget(k),v=Math.max(10,Math.min(100,+inp.value||0))/100,lab;
    if(!T)return;
    if(!A3D_LY.opWas||A3D_LY.opWas.k!==k)A3D_LY.opWas={k:k,had:T.hasOwnProperty('opacity'),v:T.opacity};
    T.opacity=v;
    lab=inp.parentNode?inp.parentNode.querySelector('.a3d-lyopv'):null;
    if(lab)lab.textContent=Math.round(v*100)+'%';
    paint();
  }
  function bimLyResOpCommit(inp){
    var k=inp.getAttribute('data-lyresop'),T=bimLyTarget(k),w=A3D_LY.opWas;
    if(!T)return;
    if(w&&w.k===k){if(w.had)T.opacity=w.v;else delete T.opacity;}
    A3D_LY.opWas=null;
    bimLyResSetOpacity(k,+inp.value);
  }
  function bimLyResFocusEdit(){
    var inp=document.querySelector('#a3d-leftpanel [data-lyresren]');
    if(inp){try{inp.focus();inp.select();}catch(eF){}}
  }
  function bimLyResEndEdit(inp,cancel){
    var k=inp.getAttribute('data-lyresren');
    if(A3D_LY.redit!==k)return;
    A3D_LY.redit=null;
    if(!cancel)bimLyResRename(k,inp.value);
    refreshLayers();
  }
  function bimLyResClick(t){
    var b,k;
    if((b=t.closest('[data-lysectog]'))){k=b.getAttribute('data-lysectog');A3D_LY.secShut=A3D_LY.secShut||{};A3D_LY.secShut[k]=!A3D_LY.secShut[k];refreshLayers();return true;}
    if((b=t.closest('[data-lysecon]'))){bimLySecVisible(b.getAttribute('data-lysecon'));return true;}   /* __acad3dV158 */
    if((b=t.closest('[data-lyreson]'))){bimLyResVisible(b.getAttribute('data-lyreson'));return true;}
    if((b=t.closest('[data-lyresupd]'))){bimResultLayerUpdate(bimLyKey(b.getAttribute('data-lyresupd')).id);return true;}
    if((b=t.closest('[data-lyresdel]'))){bimLyResRemove(b.getAttribute('data-lyresdel'));return true;}
    if((b=t.closest('[data-lyresrn]'))){A3D_LY.redit=b.getAttribute('data-lyresrn');refreshLayers();bimLyResFocusEdit();return true;}
    if((b=t.closest('[data-lyresset]'))){bimAnzAct('open:Data Layers');return true;}
    if(t.closest('input')||t.closest('[data-lyresd]'))return !!t.closest('[data-lyresd],[data-lyres]');
    if((b=t.closest('[data-lyres]'))){k=b.getAttribute('data-lyres');A3D_LY.rsel=A3D_LY.rsel===k?null:k;refreshLayers();return true;}
    return false;
  }
  function bimLayersPanelRefresh(){
    var host=document.querySelector('#a3d-leftpanel .a3d-layers-wrap');
    if(host)bimRenderInto(host,bimLayersPanelHtml());
  }
  /* every view of the layers, redrawn from them */
  function refreshLayers(){
    bimLayersPanelRefresh();
    bimLayerManagerRefresh();   /* __acad3dV121 */
  }
  function bimLyFocusEdit(){
    var inp=document.querySelector('#a3d-leftpanel [data-lyren]');
    if(inp){try{inp.focus();inp.select();}catch(eF){console.warn('[BIM] The layer name field could not take the focus',eF);}}
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
    var why=bimLayerPickRefusal(o);   /* the one refusal */
    if(why){a3dToast(why);return;}
    A3D.sel=o.id;A3D.sel2=null;A3D.selSet=[o.id];
    refreshTree();refreshProps();paint();
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
    }else if(a==='lpm'){
      bimLayerManagerOpen();
    }
  }
  /* one set of delegated listeners on the left panel, which outlives the Layers tab's markup */
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
        if(t.closest('.a3d-lysec')){bimLyResClick(t);return;}   /* __acad3dV148: Analysis and Data */
        if(t.closest('input'))return;
        if((b=t.closest('[data-lyobj]'))){bimLySelectObj(b.getAttribute('data-lyobj'));return;}
        if((b=t.closest('[data-lyid]'))){A3D_LY.sel=b.getAttribute('data-lyid');refreshLayers();return;}
      }catch(eL){
        console.warn('[BIM] A Layers panel action failed',eL);
        a3dToast('That layer action could not be completed');
      }
    });
    panel.addEventListener('dblclick',function(ev){
      var rn=inLyp(ev.target)?ev.target.closest('[data-lyresname]'):null;   /* __acad3dV148 */
      if(rn){A3D_LY.redit=rn.getAttribute('data-lyresname');refreshLayers();bimLyResFocusEdit();return;}
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
      var o=t.closest('[data-lyobj]'),l=t.closest('[data-lyid]'),rr=t.closest('[data-lyres]'),rk=rr?bimLyKey(rr.getAttribute('data-lyres')):null;   /* __acad3dV148: a result layer, in its stack */
      A3D_LY.drag=o?'obj:'+o.getAttribute('data-lyobj'):(l?'layer:'+l.getAttribute('data-lyid'):(rk&&rk.t==='res'?'rl:'+rk.id:null));
      if(A3D_LY.drag){
        try{ev.dataTransfer.setData('text/plain',A3D_LY.drag);ev.dataTransfer.effectAllowed='move';}
        catch(eD){console.warn('[BIM] The drag could not carry its data',eD);}
      }
    });
    panel.addEventListener('dragover',function(ev){
      var t=ev.target;
      if(A3D_LY.drag&&inLyp(t)&&(t.closest('[data-lyid]')||t.closest('[data-lylist]')))ev.preventDefault();
      else if(A3D_LY.drag&&A3D_LY.drag.indexOf('rl:')===0&&inLyp(t)&&t.closest('[data-lyres^="res:"]'))ev.preventDefault();
    });
    panel.addEventListener('drop',function(ev){
      var t=ev.target,v=A3D_LY.drag;
      A3D_LY.drag=null;
      if(!v||!inLyp(t))return;
      ev.preventDefault();
      var row=t.closest('[data-lyid]'),tgt=row?row.getAttribute('data-lyid'):null;
      try{
        var rt=t.closest('[data-lyres]'),rtk=rt?bimLyKey(rt.getAttribute('data-lyres')):null;
        if(v.indexOf('rl:')===0){if(rtk&&rtk.t==='res')bimResultLayerMove(v.slice(3),rtk.id);}   /* __acad3dV148: onto a row, to its place */
        else if(v.indexOf('obj:')===0){if(tgt)bimObjSetLayer(v.slice(4),tgt);}
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
    /* __acad3dV148: the Analysis and Data rows -- a name typed, the opacity dragged */
    panel.addEventListener('keydown',function(ev){
      var t=ev.target;
      if(!inLyp(t)||!t.hasAttribute('data-lyresren'))return;
      if(ev.key==='Enter'){ev.preventDefault();bimLyResEndEdit(t,false);}
      else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();bimLyResEndEdit(t,true);}
    });
    panel.addEventListener('focusout',function(ev){
      var t=ev.target;
      if(t&&t.hasAttribute&&t.hasAttribute('data-lyresren'))bimLyResEndEdit(t,false);
    });
    panel.addEventListener('input',function(ev){
      var t=ev.target;
      if(inLyp(t)&&t.hasAttribute('data-lyresop'))bimLyResOpPreview(t);
    });
    panel.addEventListener('change',function(ev){
      var t=ev.target;
      if(inLyp(t)&&t.hasAttribute('data-lyresop'))bimLyResOpCommit(t);
    });
  }
