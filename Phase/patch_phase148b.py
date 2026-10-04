"""patch_phase148b.py -- V148: Layers holds the results and the data too.

- Below the layer tree, two sections: Analysis (the results added from Analyze) and Data (the
  site's data layers, V134). A row is a swatch, the name, a badge when a result is out of date or
  its surface is gone, and an eye. A click opens the row: its opacity, its legend, what it is, and
  Update, Rename and Remove (Data: Settings, which opens its group in Properties).
- A result layer is dragged to its place in the stack; the top of the list is drawn on top.
- Double-click a name to rename it, as a layer's.
- The opacity is shown live while it is dragged and is one undo step when let go.
- Analyze's search matches the starts of words, and an analysis that is off says so to a screen
  reader only: a column of the word Off was noise.
- On a touch screen the rows and the buttons are sized for a finger.
- On a phone the Project Browser's tree no longer lies over the other tabs of the left panel."""
NAME = 'patch_phase148b.py'
BASE = '982ff529da1d6fdf98dbe6ca3aa71fd1a3f323a493c72200b52483ea1ffa0c58'
import hashlib, pathlib, sys
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')
raw = P.read_bytes()
h0 = hashlib.sha256(raw).hexdigest()
if h0 != BASE:
    sys.exit('ABORT: baseline %s, expected %s' % (h0, BASE))
t = raw.decode('utf-8')


def esc(s):
    return ''.join(ch if ord(ch) < 128 else '\\u%04x' % ord(ch) for ch in s)


def rep(old, new, n=1):
    global t
    new = esc(new)
    c = t.count(old)
    if c != n:
        sys.exit('ABORT: %d occurrences, expected %d: %r' % (c, n, old[:90]))
    t = t.replace(old, new)


# ---------------------------------------------------------------- the look
rep(""".a3d-anzstate-off{background:transparent;color:#6e7781;padding:1px 2px}""",
    """.a3d-anzstate-off{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap;border:0}   /* said, not shown */""")
rep("""/* __acad3dV121: the Layer Properties Manager */""", r"""/* __acad3dV148: Layers' Analysis and Data sections */
.a3d-lysec{margin:2px 0 0;border-top:1px solid rgba(255,255,255,.07);padding-top:4px}
.a3d-lysechd{display:flex;align-items:center;gap:3px;height:28px;padding:0 4px 0 4px}
.a3d-lysecttl{flex:1 1 auto;font-size:11px;font-weight:600;color:#aeb8c2}
.a3d-lyres{display:flex;align-items:center;gap:6px;height:28px;padding:0 2px 0 22px;border-radius:6px;cursor:pointer;user-select:none;min-width:0}
.a3d-lyres:hover{background:rgba(255,255,255,.06)}
.a3d-lyres.sel{background:rgba(78,161,255,.18)}
.a3d-lyres.dim .a3d-lynm{color:#6e7781}
.a3d-lyres.a3d-dropbefore{box-shadow:0 -2px 0 #4ea1ff}
.a3d-lyramp{flex:0 0 18px;width:18px;height:12px;border-radius:3px;box-shadow:inset 0 0 0 1px rgba(255,255,255,.18)}
.a3d-lybadge{flex:0 0 auto;font-size:10px;padding:1px 6px;border-radius:8px;background:rgba(255,183,77,.18);color:#ffb74d;white-space:nowrap}
.a3d-lybadge.gone{background:rgba(239,83,80,.18);color:#ef9a9a}
.a3d-lyresd{margin:2px 2px 6px 22px;padding:8px 9px;border-radius:7px;background:rgba(255,255,255,.04);display:flex;flex-direction:column;gap:8px;font-size:11.5px;min-width:0}
.a3d-lyopl{display:flex;align-items:center;gap:8px;color:#aeb6bf}
.a3d-lyopl input[type=range]{flex:1 1 auto;min-width:0;margin:0;accent-color:#4ea1ff}
.a3d-lyopv{flex:0 0 36px;text-align:right;color:#dfe4ea;font-variant-numeric:tabular-nums}
.a3d-lyresmeta{color:#8b949e;line-height:1.4;overflow-wrap:anywhere}
.a3d-lyleg{display:flex;flex-wrap:wrap;gap:3px 10px}
.a3d-lyleg span{display:inline-flex;align-items:center;gap:4px;color:#aeb6bf}
.a3d-lyleg i{width:10px;height:10px;border-radius:2px;flex:0 0 10px}
.a3d-lyleg i.ln{height:3px;border-radius:2px}
.a3d-lyresacts{display:flex;gap:5px;flex-wrap:wrap}
.a3d-lyresacts button{border:1px solid #3a4048;border-radius:6px;background:#2a2f35;color:#dfe4ea;font:inherit;padding:0 10px;min-height:24px;cursor:pointer}
.a3d-lyresacts button:hover{background:#343a41}
.a3d-lyresacts button.danger:hover{border-color:#e06c6c;color:#ffb4b4}
.a3d-lyresacts button.pri{background:#2f6fd6;border-color:#2f6fd6;color:#fff}
.a3d-lyhint{padding:4px 8px 8px 26px;line-height:1.4}
@media(pointer:coarse){
.a3d-lysechd{height:40px}
.a3d-lyres{height:44px}
.a3d-lyres .a3d-lyi{width:36px;height:36px;flex-basis:36px}
.a3d-lyresacts button{min-height:36px;padding:0 14px}
.a3d-lyopl input[type=range]{height:32px}
.a3d-lysec .a3d-lycar{width:32px;height:32px;flex-basis:32px}
}
/* on a phone the docked tree is forced on (V67); it is still the Project Browser tab's alone, or it
   lies over Analyze and Layers */
body.a3d-tree-docked #a3d-shell:not([data-tab="browser"]) #a3d-leftpanel > .a3d-tree{display:none!important}
body.light-theme .a3d-lysec{border-color:rgba(0,0,0,.08)}
body.light-theme .a3d-lysecttl{color:#555}
body.light-theme .a3d-lyres:hover{background:rgba(0,0,0,.05)}
body.light-theme .a3d-lyresd{background:rgba(0,0,0,.035)}
body.light-theme .a3d-lyopv{color:#222}
body.light-theme .a3d-lyresacts button{background:#fff;border-color:#c9ced4;color:#222}
body.light-theme .a3d-lyleg span,body.light-theme .a3d-lyopl{color:#444}
/* __acad3dV121: the Layer Properties Manager */""")

# ---------------------------------------------------------------- Analyze's search: the starts of words
rep("""      for(j=0;j<R.length;j++){
        hit=!q||(R[j].getAttribute('data-anzcard')+' '+R[j].textContent+' '+(hd?hd.textContent:'')).toLowerCase().indexOf(q)>=0;""",
    """      for(j=0;j<R.length;j++){
        hit=!q||bimAnzWordsHit(q,R[j].getAttribute('data-anzcard')+' '+[].map.call(R[j].querySelectorAll('.a3d-anzttl,.a3d-anzst,.a3d-anzbtn'),function(e){return e.textContent;}).join(' ')+' '+(hd?hd.textContent:''));""")
rep("""  /* the search: rows by their name, what they say, their buttons and their group; in place */""",
    """  /* every word asked for starts a word of the text: rain is not in terrain */
  function bimAnzWordsHit(q,text){
    var s=' '+String(text).toLowerCase().replace(/[^a-z0-9\\u00c0-\\u024f]+/g,' ')+' ',W=String(q).toLowerCase().split(/[^a-z0-9\\u00c0-\\u024f]+/),i;
    for(i=0;i<W.length;i++)if(W[i]&&s.indexOf(' '+W[i])<0)return false;
    return true;
  }
  /* the search: rows by their name, what they say, their buttons and their group; in place */""")

# ---------------------------------------------------------------- the sections
rep("""    if(f&&!Object.keys(seen).length)h+='<div class="a3d-lyempty">Nothing matches</div>';
    return h+'</div></div>';
  }""", """    if(f&&!Object.keys(seen).length)h+='<div class="a3d-lyempty">Nothing matches</div>';
    return h+'</div>'+bimLySectionsHtml(f)+'</div>';   /* __acad3dV148: the results and the data, below the layers */
  }
  /* ================= __acad3dV148: Analysis and Data, in Layers =================
     A row's key is its section and its id: res:<id> a result layer, data:<id> a data layer. */
  var BIM_LY_IC_UPD='<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M19.5 12a7.5 7.5 0 1 1-2.2-5.3M19.5 4.5v4.2h-4.2"/></svg>';
  function bimLyKey(k){k=String(k||'');var i=k.indexOf(':');return {t:i>0?k.slice(0,i):'',id:i>0?k.slice(i+1):''};}
  function bimLyTarget(k){var s=bimLyKey(k);return s.t==='res'?bimResById(s.id):s.t==='data'?bimDataById(s.id):null;}
  function bimResSwatch(R){
    var c=R.kind==='sunhours'?BIM_SIM_RAMP:R.kind==='rain'?['#7fb6f0','#2f7fe0','#1565c0']:R.mode==='slope'?BIM_SLOPE_COLS:R.mode==='elevation'?BIM_ELEV_COLS:
      R.mode==='cutfill'?BIM_CUTFILL_COLS:BIM_ASPECT.map(function(a){return a.c;});
    return 'linear-gradient(90deg,'+c.join(',')+')';
  }
  function bimResLegendHtml(R){
    var o,b=null,d=R.data;
    if(R.kind==='sunhours'&&d)return '<div class="a3d-anzleg"><span>0 h</span><span class="a3d-anzramp">'+BIM_SIM_RAMP.map(function(c){return '<i style="background:'+c+'"></i>';}).join('')+'</span><span>'+bimDispNum(d.day,1)+' h</span></div>';
    if(R.kind==='rain')return '<div class="a3d-lyleg"><span><i style="background:#2f7fe0"></i>Ponds</span><span><i class="ln" style="background:#1565c0"></i>Flow lines</span></div>';
    if(R.kind!=='terrain'||bimResGone(R))return '';
    o=objById(R.src);
    try{b=bimBandsOf(o,R.mode);}catch(eB){b=null;}
    return b?'<div class="a3d-lyleg">'+b.bands.filter(function(x){return x.area>0;}).map(function(x){return '<span><i style="background:'+x.col+'"></i>'+bimEsc(x.label)+'</span>';}).join('')+'</div>':'';
  }
  function bimResMetaText(R){
    var d=R.data,o=objById(R.src),s='';
    if(R.kind==='sunhours'&&d)s='Direct sun on the ground on '+d.date+': '+bimDispNum(d.min,1)+' to '+bimDispNum(d.max,1)+' h of '+bimDispNum(d.day,1)+' h; '+Math.round((d.sixPlus||0)*100)+'% has 6 h or more.';
    else if(R.kind==='rain'&&d)s=d.ponds+' pond'+(d.ponds===1?'':'s')+(d.ponds?', '+bimDispNum(d.pondVolume,1)+' m\\u00b3 held, the deepest '+bimDispNum(d.deepest||0,2)+' m':'')+
      '; flow lines where '+bimDispNum(d.threshold*d.cell*d.cell,0)+' m\\u00b2 or more drains.';
    else if(R.kind==='terrain')s=bimResGone(R)?'The surface it showed is gone, or is no longer a proposed one.':BIM_TVIEW_LABEL[R.mode]+' of '+o.name+'. It follows the surface, so it is never out of date.';
    if(R.kind!=='terrain'&&bimResStale(R))s+=' The model has changed since: Update runs it again'+(R.kind==='sunhours'?' for '+(d&&d.date):'')+'.';
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
      (gone?'<span class="a3d-lybadge gone" title="The surface it showed is gone">Gone</span>':st?'<span class="a3d-lybadge" title="The model has changed since it was run">Out of date</span>':'')+
      bimLyTgl('lyreson',key,hid,hid?'Show '+R.name:'Hide '+R.name,BIM_LY_IC.off,BIM_LY_IC.on)+'</div>';
    if(sel)h+='<div class="a3d-lyresd" data-lyresd="'+bimEsc(key)+'">'+bimLyOpacityHtml(key,R.name,bimResOpacity(R))+bimResLegendHtml(R)+
      '<div class="a3d-lyresmeta">'+bimEsc(bimResMetaText(R))+'</div><div class="a3d-lyresacts">'+
      (R.kind!=='terrain'?'<button type="button" data-lyresupd="'+bimEsc(key)+'"'+(st?' class="pri"':'')+'>Update</button>':'')+
      '<button type="button" data-lyresrn="'+bimEsc(key)+'">Rename</button><button type="button" class="danger" data-lyresdel="'+bimEsc(key)+'">Remove</button></div></div>';
    return h;
  }
  function bimLyDataRowHtml(L){
    var key='data:'+L.id,sel=A3D_LY.rsel===key,hid=!L.visible,n=bimDataFeats(L.id).length,h,col=/^#[0-9a-fA-F]{6}$/.test(L.color||'')?L.color:'#7f9db8';
    h='<div class="a3d-lyres'+(sel?' sel':'')+(hid?' dim':'')+'" data-lyres="'+bimEsc(key)+'" aria-expanded="'+sel+'">'+
      '<span class="a3d-lyramp" style="background:'+col+'"></span>'+bimLyNameHtml(key,L.name)+
      (L.status&&L.status.error?'<span class="a3d-lybadge gone" title="'+bimEsc(bimDataStatusText(L))+'">Failed</span>':'')+
      bimLyTgl('lyreson',key,hid,hid?'Show '+L.name:'Hide '+L.name,BIM_LY_IC.off,BIM_LY_IC.on)+'</div>';
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
    function sec(key,label,n,body,empty){
      if(f&&!body)return '';
      var open=!!f||!shut[key];
      return '<div class="a3d-lysec" data-lysec="'+key+'"><div class="a3d-lysechd"><button type="button" class="a3d-lycar" data-lysectog="'+key+'" aria-expanded="'+open+'" title="'+
        (open?'Close ':'Open ')+label+'" aria-label="'+(open?'Close ':'Open ')+label+'">'+(open?BIM_LY_IC.open:BIM_LY_IC.closed)+'</button>'+
        '<span class="a3d-lysecttl">'+label+'</span><span class="a3d-lycnt">'+(n||'')+'</span></div>'+
        (open?(body||'<div class="a3d-lyempty a3d-lyhint">'+empty+'</div>'):'')+'</div>';
    }
    return sec('analysis','Analysis',bimResLayers().length,rb,'Results you keep from Analyze, with Add as layer, are listed here')+
      sec('data','Data',bimDataList().length,db,'Data layers added in Properties, Site, Data Layers, are listed here');
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
    if((b=t.closest('[data-lyreson]'))){bimLyResVisible(b.getAttribute('data-lyreson'));return true;}
    if((b=t.closest('[data-lyresupd]'))){bimResultLayerUpdate(bimLyKey(b.getAttribute('data-lyresupd')).id);return true;}
    if((b=t.closest('[data-lyresdel]'))){bimLyResRemove(b.getAttribute('data-lyresdel'));return true;}
    if((b=t.closest('[data-lyresrn]'))){A3D_LY.redit=b.getAttribute('data-lyresrn');refreshLayers();bimLyResFocusEdit();return true;}
    if((b=t.closest('[data-lyresset]'))){bimAnzAct('open:Data Layers');return true;}
    if(t.closest('input')||t.closest('[data-lyresd]'))return !!t.closest('[data-lyresd],[data-lyres]');
    if((b=t.closest('[data-lyres]'))){k=b.getAttribute('data-lyres');A3D_LY.rsel=A3D_LY.rsel===k?null:k;refreshLayers();return true;}
    return false;
  }""")

# wiring: clicks, renaming, the opacity, the stack
rep("""        if((b=t.closest('[data-lypin]'))){var po=objById(b.getAttribute('data-lypin'));if(po)bimSetLocked(po,!bimIsLocked(po));return;}
        if(t.closest('input'))return;""", """        if((b=t.closest('[data-lypin]'))){var po=objById(b.getAttribute('data-lypin'));if(po)bimSetLocked(po,!bimIsLocked(po));return;}
        if(t.closest('.a3d-lysec')){bimLyResClick(t);return;}   /* __acad3dV148: Analysis and Data */
        if(t.closest('input'))return;""")
rep("""    panel.addEventListener('dblclick',function(ev){
      var n=inLyp(ev.target)?ev.target.closest('[data-lyname]'):null;
      if(!n)return;""", """    panel.addEventListener('dblclick',function(ev){
      var rn=inLyp(ev.target)?ev.target.closest('[data-lyresname]'):null;   /* __acad3dV148 */
      if(rn){A3D_LY.redit=rn.getAttribute('data-lyresname');refreshLayers();bimLyResFocusEdit();return;}
      var n=inLyp(ev.target)?ev.target.closest('[data-lyname]'):null;
      if(!n)return;""")
rep("""      var o=t.closest('[data-lyobj]'),l=t.closest('[data-lyid]');
      A3D_LY.drag=o?'obj:'+o.getAttribute('data-lyobj'):(l?'layer:'+l.getAttribute('data-lyid'):null);""",
    """      var o=t.closest('[data-lyobj]'),l=t.closest('[data-lyid]'),rr=t.closest('[data-lyres]'),rk=rr?bimLyKey(rr.getAttribute('data-lyres')):null;   /* __acad3dV148: a result layer, in its stack */
      A3D_LY.drag=o?'obj:'+o.getAttribute('data-lyobj'):(l?'layer:'+l.getAttribute('data-lyid'):(rk&&rk.t==='res'?'rl:'+rk.id:null));""")
rep("""      if(A3D_LY.drag&&inLyp(t)&&(t.closest('[data-lyid]')||t.closest('[data-lylist]')))ev.preventDefault();""",
    """      if(A3D_LY.drag&&inLyp(t)&&(t.closest('[data-lyid]')||t.closest('[data-lylist]')))ev.preventDefault();
      else if(A3D_LY.drag&&A3D_LY.drag.indexOf('rl:')===0&&inLyp(t)&&t.closest('[data-lyres^="res:"]'))ev.preventDefault();""")
rep("""        if(v.indexOf('obj:')===0){if(tgt)bimObjSetLayer(v.slice(4),tgt);}""",
    """        var rt=t.closest('[data-lyres]'),rtk=rt?bimLyKey(rt.getAttribute('data-lyres')):null;
        if(v.indexOf('rl:')===0){if(rtk&&rtk.t==='res')bimResultLayerMove(v.slice(3),rtk.id);}   /* __acad3dV148: onto a row, to its place */
        else if(v.indexOf('obj:')===0){if(tgt)bimObjSetLayer(v.slice(4),tgt);}""")
rep("""    panel.addEventListener('dragend',function(){A3D_LY.drag=null;});""",
    """    panel.addEventListener('dragend',function(){A3D_LY.drag=null;});
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
    });""")

# the data layers' own edits reach Layers too
rep("""    if(field==='visible'&&!v&&A3D_DATA.sel&&A3D_DATA.sel.layer===id)A3D_DATA.sel=null;
    refreshProps();paint();saveSoon();
    return true;""", """    if(field==='visible'&&!v&&A3D_DATA.sel&&A3D_DATA.sel.layer===id)A3D_DATA.sel=null;
    refreshProps();paint();saveSoon();bimLayersPanelRefresh();   /* __acad3dV148 */
    return true;""")
rep("""    if(A3D_DATA.sel&&A3D_DATA.sel.layer===id)A3D_DATA.sel=null;
    refreshProps();paint();saveSoon();
    a3dToast(nm+' removed');""", """    if(A3D_DATA.sel&&A3D_DATA.sel.layer===id)A3D_DATA.sel=null;
    refreshProps();paint();saveSoon();bimLayersPanelRefresh();   /* __acad3dV148 */
    a3dToast(nm+' removed');""")
rep("""    A3D.site.dataLayers.push(lyr);
    refreshProps();saveSoon();""", """    A3D.site.dataLayers.push(lyr);
    refreshProps();saveSoon();bimLayersPanelRefresh();   /* __acad3dV148 */""")

rep("""    {sel:'[data-anzact]',why:'an analysis: run it, show or hide it, or open its settings in Properties'},""",
    """    {sel:'[data-anzact]',why:'an analysis: run it, show or hide it, or open its settings in Properties'},
    {sel:'[data-anztog]',why:'an analysis row: opens and closes it, to its whole status, legend and other actions'},   /* __acad3dV148 */
    {sel:'[data-lysectog]',why:'opens or closes the Analysis or Data section of the Layers panel'},
    {sel:'[data-lyreson]',why:'shows or hides a result layer or a data layer'},
    {sel:'[data-lyresupd]',why:'runs a result layer again, on its own date and surface'},
    {sel:'[data-lyresrn]',why:'renames a result layer or a data layer'},
    {sel:'[data-lyresdel]',why:'removes a result layer or a data layer'},
    {sel:'[data-lyresset]',why:'opens a data layer\\'s settings in Properties'},""")

# ---------------------------------------------------------------- version, hooks, marker
rep("""  var BIM_APP_VERSION={v:'V147',date:'2026-10-04'};   /* __acad3dV147 */""",
    """  var BIM_APP_VERSION={v:'V148',date:'2026-10-04'};   /* __acad3dV148 */""")
rep("""  window.__acad3dV147='phonesheet,""", """  /* __acad3dV148: Analyze as a list; results as layers */
  window.__a3dAnzToggle=function(id,on){return bimAnzToggle(id,on);};
  window.__a3dAnzOpenAll=function(on){bimAnzCards().forEach(function(c){bimAnzToggle(c.id,on!==false);});return Object.keys(A3D_ANZ.open).sort();};
  window.__a3dAnzSearch=function(q){
    A3D_ANZ.q=String(q==null?'':q);
    var w=document.querySelector('.a3d-analyze-wrap'),s=w?w.querySelector('[data-anzsearch]'):null;
    if(s)s.value=A3D_ANZ.q;
    if(w)bimAnzFilter(w);
    return w?[].filter.call(w.querySelectorAll('[data-anzcard]'),function(e){return !e.hasAttribute('hidden');}).map(function(e){return e.getAttribute('data-anzcard');}):null;
  };
  window.__a3dAnzWordsHit=function(q,s){return bimAnzWordsHit(q,s);};
  window.__a3dResultLayers=function(){return bimResLayers().map(function(R){
    return {id:R.id,name:R.name,kind:R.kind,mode:R.mode||null,src:R.src||null,visible:R.visible!==false,opacity:bimResOpacity(R),stale:bimResStale(R),gone:bimResGone(R),
      created:R.created||null,run:R.run||null,cells:R.data?R.data.cells.length:0,date:R.data&&R.data.date||null,segs:R.data&&R.data.segs?R.data.segs.length:0};});};
  window.__a3dResultLayerData=function(id){var R=bimResById(id);return R&&R.data?JSON.parse(JSON.stringify(R.data)):null;};
  window.__a3dResultLayerAdd=function(k,o){var R=bimResultLayerAdd(k,o||{});return R?R.id:null;};
  window.__a3dResultLayerSet=function(id,f,v){return bimResultLayerSet(id,f,v);};
  window.__a3dResultLayerRemove=function(id){return bimResultLayerRemove(id);};
  window.__a3dResultLayerUpdate=function(id){return bimResultLayerUpdate(id);};
  window.__a3dResultLayerMove=function(id,to){return bimResultLayerMove(id,to);};
  window.__a3dResultDrawn=function(){return (A3D.lastResultDrawn||[]).slice();};
  window.__a3dResultLayersValid=function(a){return bimResValid(a).map(function(R){return R.id;});};
  window.__a3dSimHolds=function(){return {sun:bimResHolds(A3D_SIM.sun),rain:bimResHolds(A3D_SIM.rain)};};
  window.__acad3dV148='anzlist,anzgroups,anzsearch,anzwords,anzexpand,anzremember,addaslayer,reslayers,ressnapshot,reslive,resstale,resupdate,resorder,resopacity,ressaved,resundo,layersanalysis,layersdata,touchrows';
  window.__acad3dV147='phonesheet,""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
