"""patch_phase148a.py -- V148: Analyze, as a list; results as layers.

- The Analyze tab is a list, not a stack of cards: grouped Model, Site and terrain, Structure,
  Environment, with a search. Each row is one line -- the name, what it shows, its state and its
  first action -- and opens to the whole status, the legend and the other actions.
- Add as layer: a result becomes a layer. Sun hours and rain are kept as they were when run (the
  picture saved with the project, so it opens offline and two runs can be compared); a terrain's
  slope, elevation, aspect or cut and fill follows its surface. Each layer has its visibility, its
  opacity and its place in the stack, and is drawn on the plan in that order.
- The layers are saved with the project and in a project file, and an undo takes one back.
  History (V146) does not keep them: a version restored leaves them as they are."""
NAME = 'patch_phase148a.py'
BASE = 'cff2ad402b13f8b5a3cabc2a076cc9deb3e511b8542deefdfc30105b59944d34'
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


# ---------------------------------------------------------------- the list's look
s0 = '.a3d-anz{display:flex;flex-direction:column;min-height:0;flex:1;overflow:auto;padding:10px 12px 16px}\n'
s1 = '.a3d-anzsimhd{margin-top:16px}\n'
i0 = t.index(s0)
i1 = t.index(s1) + len(s1)
assert t.count(s0) == 1 and t.count(s1) == 1 and i1 > i0
CSS = r"""/* __acad3dV148: Analyze, a list of rows in four groups */
.a3d-anz{display:flex;flex-direction:column;min-height:0;flex:1;overflow:auto;padding:8px 10px 18px}
.a3d-anz [hidden]{display:none!important}
.a3d-anzhead{display:flex;align-items:baseline;justify-content:space-between;gap:8px;margin:2px 2px 8px}
.a3d-anzttl0{font-weight:650;font-size:13px}
.a3d-anzcount{color:#8a96a3;font-size:11.5px;white-space:nowrap}
.a3d-anzsearch{display:block;width:100%;box-sizing:border-box;margin:0 0 4px;background:#1f2327;border:1px solid #3a4048;border-radius:6px;color:#e6eaef;padding:4px 8px;min-height:28px;font:inherit;font-size:12px}
.a3d-anzsearch:focus{border-color:#4ea1ff;outline:0}
.a3d-anzgrphd{font-size:11px;font-weight:600;color:#8a96a3;padding:12px 4px 4px}
.a3d-anzlist{display:flex;flex-direction:column;gap:1px}
.a3d-anzcard{border-radius:7px;min-width:0}
.a3d-anzcard.open{background:rgba(255,255,255,.035)}
.a3d-anzhd{display:flex;align-items:center;gap:6px;min-height:36px;padding:0 4px 0 0;border-radius:7px;min-width:0}
.a3d-anzhd:hover{background:rgba(255,255,255,.045)}
.a3d-anztog{flex:1 1 auto;min-width:0;display:flex;align-items:center;gap:4px;background:transparent;border:0;padding:4px 0 4px 2px;margin:0;color:inherit;font:inherit;text-align:left;cursor:pointer}
.a3d-anztog:focus-visible{outline:2px solid #4ea1ff;outline-offset:-2px;border-radius:6px}
.a3d-anzchev{flex:0 0 16px;width:16px;height:16px;display:grid;place-items:center;color:#8b949e;transition:transform .12s}
.a3d-anzcard.open .a3d-anzchev{transform:rotate(90deg)}
.a3d-anzname{display:flex;flex-direction:column;min-width:0;flex:1 1 auto}
.a3d-anzttl{font-weight:500;font-size:12.5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.a3d-anzsum{font-size:11px;color:#8a96a3;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-top:1px}
.a3d-anzcard.open .a3d-anzsum{display:none}
.a3d-anzstate{flex:0 0 auto;font-size:10.5px;padding:1px 6px;border-radius:9px;background:rgba(255,255,255,.08);color:#9aa3ad;white-space:nowrap}
.a3d-anzstate-off{background:transparent;color:#6e7781;padding:1px 2px}
.a3d-anzstate-on{background:rgba(76,175,80,.18);color:#81c784}
.a3d-anzstate-warn{background:rgba(255,183,77,.18);color:#ffb74d}
.a3d-anzstate-fail{background:rgba(239,83,80,.18);color:#ef9a9a}
.a3d-anzbody{display:none;padding:0 8px 10px 22px}
.a3d-anzcard.open .a3d-anzbody{display:block}
.a3d-anzst{color:#aab4bf;font-size:12px;margin:0 0 8px;line-height:1.4}
.a3d-anzacts{display:flex;flex-wrap:wrap;gap:5px}
.a3d-anzbtn{flex:0 0 auto;border:1px solid rgba(255,255,255,.14);border-radius:6px;padding:0 9px;min-height:24px;background:transparent;color:#dfe5ea;font:inherit;font-size:11.5px;cursor:pointer;white-space:nowrap}
.a3d-anzbtn:hover{background:rgba(255,255,255,.08)}
.a3d-anzbtn.pri{background:#2f6fd6;border-color:#2f6fd6;color:#fff}
.a3d-anzbtn.pri:hover{background:#3a7be0}
.a3d-anzbtn.lay{border-color:rgba(78,161,255,.55);color:#9cc9ff}
.a3d-anzbtn:disabled{opacity:.45;cursor:default}
.a3d-anzempty{padding:14px 6px;color:#8a96a3;font-size:12px}
@media(pointer:coarse){
.a3d-anzhd{min-height:46px}
.a3d-anztog{padding:6px 0 6px 2px}
.a3d-anzttl{font-size:13.5px}
.a3d-anzsum{font-size:12px}
.a3d-anzbtn{min-height:34px;padding:0 12px;font-size:12.5px}
.a3d-anzsearch{min-height:36px;font-size:13px}
.a3d-anzchev{flex-basis:22px;width:22px}
}
body.light-theme .a3d-anzcard.open{background:rgba(0,0,0,.035)}
body.light-theme .a3d-anzhd:hover{background:rgba(0,0,0,.04)}
body.light-theme .a3d-anzsearch{background:#fff;border-color:#c9ced4;color:#222}
body.light-theme .a3d-anzst{color:#555}
body.light-theme .a3d-anzsum,body.light-theme .a3d-anzgrphd,body.light-theme .a3d-anzcount{color:#6b737c}
body.light-theme .a3d-anzbtn{border-color:rgba(0,0,0,.15);color:#222}
body.light-theme .a3d-anzbtn.pri{color:#fff}
body.light-theme .a3d-anzbtn.lay{border-color:#4a8fe0;color:#1d63b8}
"""
t = t[:i0] + esc(CSS) + t[i1:]

# ---------------------------------------------------------------- the rows
rep("""  var A3D_ANZ={lod:null};""",
    """  var A3D_ANZ={lod:null,open:bimAnzOpenLoad(),q:''};   /* __acad3dV148: the rows open, and the search */""")

OLD_CARD = t[t.index("  function bimAnzCard(id,title,status,acts,state,extra){"):t.index("  /* each analysis: what it shows now, and its buttons */")]
rep(OLD_CARD, r"""  /* __acad3dV148: a row, not a card. Its name, what it shows, its state and its first action on one
     line; the whole status, the legend and every other action a click away. A row is opened by the
     viewer, and stays open, in this browser. */
  var BIM_ANZ_GROUPS=[['model','Model'],['site','Site and terrain'],['structure','Structure'],['env','Environment']];
  var BIM_ANZ_GROUP_OF={lens:'model',areas:'model',lod:'model',stats:'model',survey:'site',terrain:'site',grading:'site',rain:'site',structure:'structure',sun:'env',sunhours:'env',solar:'env'};
  var BIM_ANZ_KEY='acad3dAnzOpen';
  var BIM_ANZ_CHEV='<svg viewBox="0 0 16 16" width="12" height="12" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 3.5 10.5 8 6 12.5"/></svg>';
  /* the key written out: A3D_ANZ is made before BIM_ANZ_KEY is set */
  function bimAnzOpenLoad(){try{var v=JSON.parse(localStorage.getItem('acad3dAnzOpen')||'{}');return v&&typeof v==='object'&&!Array.isArray(v)?v:{};}catch(eO){return {};}}
  function bimAnzStateText(s){return s==='on'?'On':s==='warn'?'Check':s==='fail'?'Problems':s==='stale'?'Out of date':s==='busy'?'Running':'Off';}
  function bimAnzBtn(a){
    return '<button type="button" class="a3d-anzbtn'+(a.pri?' pri':'')+(a.lay?' lay':'')+'" data-anzact="'+a.act+'"'+(a.off?' disabled title="'+bimEsc(a.off)+'"':(a.tip?' title="'+bimEsc(a.tip)+'"':''))+'>'+bimEsc(a.label)+'</button>';
  }
  /* the surface shown by slope, elevation or aspect, if one is */
  function bimAnzTerrainShown(){return A3D.objs.filter(function(o){return o.t==='terrain'&&o.survey&&o.tview&&o.tview!=='cutfill';})[0]||null;}
  /* Add as layer, on the analyses whose result is a picture on the plan */
  function bimAnzLayerAct(id){
    var tip='Keep it as a layer, in Layers under Analysis',s,o;
    if(id==='sunhours'||id==='rain'){
      s=id==='sunhours'?A3D_SIM.sun:A3D_SIM.rain;
      return {act:'layer:'+id,label:'Add as layer',lay:true,tip:tip,off:!s?'Run it first':bimResHolds(s)?'This run is a layer already':''};
    }
    if(id==='terrain'){o=bimAnzTerrainShown();return {act:'layer:terrain',label:'Add as layer',lay:true,tip:tip,off:o?'':'Show slope, elevation or aspect first'};}
    if(id==='grading'){
      o=A3D.objs.filter(function(x){return x.t==='terrain'&&x.grading;})[0];
      return {act:'layer:cutfill',label:'Add as layer',lay:true,tip:tip,off:!o?'Grade first':bimResLayers().some(function(R){return R.kind==='terrain'&&R.mode==='cutfill'&&R.src===o.id;})?'Its cut and fill is a layer already':''};
    }
    return null;
  }
  function bimAnzCard(c){
    var open=!!A3D_ANZ.open[c.id],a0=c.acts[0],rest=c.acts.slice(1),ly=bimAnzLayerAct(c.id);
    if(ly)rest.push(ly);
    return '<div class="a3d-anzcard'+(open?' open':'')+'" data-anzcard="'+c.id+'">'+
      '<div class="a3d-anzhd"><button type="button" class="a3d-anztog" data-anztog="'+c.id+'" aria-expanded="'+open+'">'+
      '<span class="a3d-anzchev">'+BIM_ANZ_CHEV+'</span><span class="a3d-anzname"><span class="a3d-anzttl">'+bimEsc(c.title)+'</span>'+
      '<span class="a3d-anzsum">'+bimEsc(c.status)+'</span></span></button>'+
      (c.state?'<span class="a3d-anzstate a3d-anzstate-'+c.state+'">'+bimAnzStateText(c.state)+'</span>':'')+(a0?bimAnzBtn(a0):'')+'</div>'+
      '<div class="a3d-anzbody"><div class="a3d-anzst">'+bimEsc(c.status)+'</div>'+(c.extra||'')+
      (rest.length?'<div class="a3d-anzacts">'+rest.map(bimAnzBtn).join('')+'</div>':'')+'</div></div>';
  }
  /* a row opened or closed, in place */
  function bimAnzToggle(id,on){
    id=String(id||'');
    if(!/^[a-z]+$/.test(id))return false;
    var v=on===undefined?!A3D_ANZ.open[id]:!!on;
    if(v)A3D_ANZ.open[id]=true;else delete A3D_ANZ.open[id];
    try{localStorage.setItem(BIM_ANZ_KEY,JSON.stringify(A3D_ANZ.open));}catch(eS){}
    var w=document.querySelector('.a3d-analyze-wrap'),c=w?w.querySelector('[data-anzcard="'+id+'"]'):null,b;
    if(c){c.classList.toggle('open',v);b=c.querySelector('[data-anztog]');if(b)b.setAttribute('aria-expanded',String(v));}
    return v;
  }
""")

# sentence case, as the rest of the panels since V147
for old, new in (("C.push({id:'structure',title:'Structure',", "C.push({id:'structure',title:'Frame analysis',"),
                 ("{act:'structure:run',label:A3D_STRUCT.show?'Run Again':'Run'", "{act:'structure:run',label:A3D_STRUCT.show?'Run again':'Run'"),
                 ("C.push({id:'sun',title:'Sun and Shadows',", "C.push({id:'sun',title:'Sun and shadows',"),
                 ("C.push({id:'lens',title:'Colour By',", "C.push({id:'lens',title:'Colour by',"),
                 ("C.push({id:'areas',title:'Areas by Usage',", "C.push({id:'areas',title:'Areas by usage',"),
                 ("C.push({id:'survey',title:'Survey Check',", "C.push({id:'survey',title:'Survey check',"),
                 ("C.push({id:'terrain',title:'Terrain: Slope, Elevation, Aspect',", "C.push({id:'terrain',title:'Slope, elevation, aspect',"),
                 ("C.push({id:'grading',title:'Grading: Cut and Fill',", "C.push({id:'grading',title:'Grading, cut and fill',"),
                 ("label:gs0?'Grade Again':'Grade'", "label:gs0?'Grade again':'Grade'"),
                 ("label:'Cut and Fill Map'", "label:'Cut and fill map'"),
                 ("label:'Slope Arrows'", "label:'Slope arrows'"),
                 ("C.push({id:'lod',title:'Buildings: LOD and Solids',", "C.push({id:'lod',title:'Buildings, LOD and solids',"),
                 ("C.push({id:'sunhours',sim:true,title:'Sun Hours',", "C.push({id:'sunhours',sim:true,title:'Sun hours',"),
                 ("{act:'sunhours:run',label:sh?'Run Again':'Run'", "{act:'sunhours:run',label:sh?'Run again':'Run'"),
                 ("C.push({id:'solar',sim:true,title:'Solar on Roofs and Facades',", "C.push({id:'solar',sim:true,title:'Solar on roofs and facades',"),
                 ("{act:'solar:run',label:so?'Run Again':'Run'", "{act:'solar:run',label:so?'Run again':'Run'"),
                 ("{act:'solar:colour',label:'Colour By',", "{act:'solar:colour',label:'Colour by',"),
                 ("C.push({id:'rain',sim:true,title:'Rain on Terrain',", "C.push({id:'rain',sim:true,title:'Rain on terrain',"),
                 ("{act:'rain:run',label:ra?'Run Again':'Run'", "{act:'rain:run',label:ra?'Run again':'Run'")):
    rep(old, new)

OLD_HTML = t[t.index("    return C;\n  }\n  function bimAnalyzeHtml(){"):t.index("  /* a button: run it, or open its settings in Properties */")]
rep(OLD_HTML, r"""    C.forEach(function(c){c.group=BIM_ANZ_GROUP_OF[c.id]||'model';});   /* __acad3dV148 */
    return C;
  }
  function bimAnzCountText(C){
    var n=C.filter(function(c){return c.state==='on'||c.state==='stale'||c.state==='busy';}).length;
    return C.length+' analyses'+(n?' · '+n+' on':'');
  }
  function bimAnzRowsHtml(C){
    return BIM_ANZ_GROUPS.map(function(g){
      var R=C.filter(function(c){return c.group===g[0];});
      return R.length?'<div class="a3d-anzgrp" data-anzgrp="'+g[0]+'"><div class="a3d-anzgrphd">'+g[1]+'</div><div class="a3d-anzlist">'+R.map(bimAnzCard).join('')+'</div></div>':'';
    }).join('')+'<div class="a3d-anzempty" hidden>Nothing matches</div>';
  }
  function bimAnalyzeHtml(){
    var C=bimAnzCards();
    return '<div class="a3d-anz"><div class="a3d-anzhead"><span class="a3d-anzttl0">Analyze</span><span class="a3d-anzcount">'+bimAnzCountText(C)+'</span></div>'+
      '<input type="search" class="a3d-anzsearch" data-anzsearch="1" placeholder="Search analyses" aria-label="Search analyses" autocomplete="off" value="'+bimEsc(A3D_ANZ.q||'')+'">'+
      '<div class="a3d-anzrows">'+bimAnzRowsHtml(C)+'</div></div>';
  }
  /* the search: rows by their name, what they say, their buttons and their group; in place */
  function bimAnzFilter(w){
    var q=String(A3D_ANZ.q||'').toLowerCase().replace(/^\s+|\s+$/g,''),G=w?w.querySelectorAll('[data-anzgrp]'):[],n=0,i,j,R,k,hd,hit,e;
    for(i=0;i<G.length;i++){
      hd=G[i].querySelector('.a3d-anzgrphd');R=G[i].querySelectorAll('[data-anzcard]');k=0;
      for(j=0;j<R.length;j++){
        hit=!q||(R[j].getAttribute('data-anzcard')+' '+R[j].textContent+' '+(hd?hd.textContent:'')).toLowerCase().indexOf(q)>=0;
        if(hit){R[j].removeAttribute('hidden');k++;}else R[j].setAttribute('hidden','');
      }
      if(k)G[i].removeAttribute('hidden');else G[i].setAttribute('hidden','');
      n+=k;
    }
    e=w?w.querySelector('.a3d-anzempty'):null;
    if(e){if(n)e.setAttribute('hidden','');else e.removeAttribute('hidden');}
    return n;
  }
  /* the panel again, when it is open: the rows only, so the search, its focus and the scroll stay */
  function bimAnalyzeRefresh(){
    var sh=document.getElementById('a3d-shell'),w=sh&&sh.dataset.tab==='analyze'?sh.querySelector('.a3d-analyze-wrap'):null;
    if(!w)return false;
    try{
      var rows=w.querySelector('.a3d-anzrows'),cnt=w.querySelector('.a3d-anzcount'),C;
      if(rows&&cnt){C=bimAnzCards();bimRenderInto(rows,bimAnzRowsHtml(C));cnt.textContent=bimAnzCountText(C);}
      else w.innerHTML=bimAnalyzeHtml();
      bimAnzFilter(w);
    }catch(eA){console.warn('[BIM] Analyze panel',eA);}
    return true;
  }
""")

rep("""    else if(k.indexOf('sim:clear:')===0)bimSimClear(k.slice(10));
    else return false;""", """    else if(k.indexOf('sim:clear:')===0)bimSimClear(k.slice(10));
    else if(k.indexOf('layer:')===0)bimResultLayerAdd(k.slice(6));   /* __acad3dV148 */
    else return false;""")

rep("""      abox.innerHTML=bimAnalyzeHtml();
      abox.addEventListener('click',function(ev){
        var b=ev.target&&ev.target.closest?ev.target.closest('[data-anzact]'):null;""", """      abox.innerHTML=bimAnalyzeHtml();
      bimAnzFilter(abox);   /* __acad3dV148: the search kept from before */
      abox.addEventListener('click',function(ev){
        var tg=ev.target&&ev.target.closest?ev.target.closest('[data-anztog]'):null;   /* __acad3dV148: a row opens and closes */
        if(tg){bimAnzToggle(tg.getAttribute('data-anztog'));return;}
        var b=ev.target&&ev.target.closest?ev.target.closest('[data-anzact]'):null;""")
rep("""        try{bimAnzAct(b.getAttribute('data-anzact'));}catch(eZ){console.warn('[BIM] Analyze',eZ);a3dToast('That did not work - see the console');}
      });
      panel.appendChild(abox);""", """        try{bimAnzAct(b.getAttribute('data-anzact'));}catch(eZ){console.warn('[BIM] Analyze',eZ);a3dToast('That did not work - see the console');}
      });
      abox.addEventListener('input',function(ev){
        var s=ev.target;
        if(s&&s.hasAttribute&&s.hasAttribute('data-anzsearch')){A3D_ANZ.q=s.value;bimAnzFilter(abox);}
      });
      abox.addEventListener('keydown',function(ev){
        var s=ev.target;
        if(s&&s.hasAttribute&&s.hasAttribute('data-anzsearch')&&ev.key==='Escape'&&s.value){ev.preventDefault();ev.stopPropagation();s.value='';A3D_ANZ.q='';bimAnzFilter(abox);}
      });
      panel.appendChild(abox);""")

# ---------------------------------------------------------------- drawing: the flow lines, the bands, shared
rep("""        ctx.save();ctx.strokeStyle='#1565c0';ctx.lineCap='round';
        var lm=Math.log(r.maxAcc+1),i,g,a,b;
        for(i=0;i<r.segs.length;i++){
          g=r.segs[i];a=toScreen([g[0],0,g[1]],V,W,H);b=toScreen([g[2],0,g[3]],V,W,H);
          if(!a||!b)continue;
          ctx.lineWidth=0.8+2.6*Math.log(g[4]+1)/lm;
          ctx.beginPath();ctx.moveTo(a[0],a[1]);ctx.lineTo(b[0],b[1]);ctx.stroke();
        }
        ctx.restore();
      }""", """        bimSimDrawFlow(ctx,V,W,H,r.segs,r.maxAcc,1);   /* __acad3dV148: shared with the rain's layers */
      }""")
rep("""      var s=A3D_SIM.sun;
      if(s&&s.show!==false){""", """      var s=A3D_SIM.sun;
      if(s&&s.show!==false&&!bimResHolds(s)){   /* __acad3dV148: a run kept as a layer is drawn as the layer */""")
rep("""      var r=A3D_SIM.rain;
      if(r&&r.show!==false){""", """      var r=A3D_SIM.rain;
      if(r&&r.show!==false&&!bimResHolds(r)){""")

rep("""        if(tb){
          ctx.save();ctx.globalAlpha*=0.55;
          for(j=0;j<tin.tris.length;j++){
            if(tb.tri[j]<0)continue;
            a=sp[tin.tris[j][0]];b=sp[tin.tris[j][1]];c=sp[tin.tris[j][2]];
            if(!a||!b||!c)continue;
            ctx.fillStyle=ctx.strokeStyle=tb.bands[tb.tri[j]].col;ctx.lineWidth=0.5;
            ctx.beginPath();ctx.moveTo(a[0],a[1]);ctx.lineTo(b[0],b[1]);ctx.lineTo(c[0],c[1]);ctx.closePath();ctx.fill();ctx.stroke();
          }
          ctx.restore();
          if(!legendFor||sel)""", """        if(tb){
          bimDrawBandTris(ctx,tin,tb,sp,0.55);   /* __acad3dV148: shared with the terrain's layers */
          if(!legendFor||sel)""")

ENGINE = r"""  /* ================= __acad3dV148: results as layers =================
     A result kept as a layer. Sun hours and rain are kept as they were when run -- their picture is
     saved with the project, so it opens offline and two runs (June and December, say) can be laid
     over each other. A terrain's slope, elevation, aspect or cut and fill follows its surface, so
     it is never out of date. Each layer has its visibility, its opacity and its place in the
     stack; the top of the list is drawn last, over the rest, as in any layers panel. */
  var A3D_RES_IMG={};
  var BIM_TVIEW_LABEL={slope:'Slope',elevation:'Elevation',aspect:'Aspect',cutfill:'Cut and fill'};
  function bimResLayers(){if(!Array.isArray(A3D.resultLayers))A3D.resultLayers=[];return A3D.resultLayers;}
  function bimResById(id){var L=bimResLayers(),i;for(i=0;i<L.length;i++)if(L[i].id===id)return L[i];return null;}
  function bimResOpacity(R){var v=R&&R.opacity;return typeof v==='number'&&v>=0.1&&v<=1?v:0.6;}
  /* a run that a layer keeps: drawn as that layer, not twice */
  function bimResHolds(s){
    if(!s||!s.runId)return false;
    var L=bimResLayers(),i;
    for(i=0;i<L.length;i++)if(L[i].run===s.runId)return true;
    return false;
  }
  function bimResNow(){var d=new Date();function p(n){return (n<10?'0':'')+n;}return d.getFullYear()+'-'+p(d.getMonth()+1)+'-'+p(d.getDate())+' '+p(d.getHours())+':'+p(d.getMinutes());}
  /* what a kept result depends on: the model, and for the sun the site's place -- not the date,
     which the layer keeps as its own */
  function bimResKeyFrom(stamp,kind){
    stamp=String(stamp||'');
    var i=stamp.indexOf(':'),j=i<0?-1:stamp.indexOf(':',i+1),st;
    if(i<0)return stamp;
    if(kind!=='sunhours')return stamp.slice(0,i);
    try{st=JSON.parse(stamp.slice(j+1));}catch(eK){st={};}
    return stamp.slice(0,i)+':'+stamp.slice(i+1,j)+':'+[st.lat,st.lon,st.tz].join(',');
  }
  function bimResKey(kind){return bimResKeyFrom(bimSimStamp(),kind);}
  function bimResStale(R){return !!(R&&R.kind!=='terrain'&&R.key&&R.key!==bimResKey(R.kind));}
  /* a terrain layer whose surface is gone, or no longer proposed */
  function bimResGone(R){
    if(!R)return true;
    if(R.kind!=='terrain')return false;
    var o=objById(R.src);
    return !(o&&o.t==='terrain'&&o.survey)||(R.mode==='cutfill'&&!o.grading);
  }
  /* a run's picture as text: one character a cell, the colour's place on the ramp */
  function bimResSunData(s){
    var n=s.nx*s.nz,m=BIM_SIM_RAMP.length,a=[],k;
    for(k=0;k<n;k++)a.push(s.roof[k]?'.':String(Math.min(m-1,Math.floor(Math.max(0,Math.min(1,s.day?s.hours[k]/s.day:0))*m))));
    return {x0:s.x0,z0:s.z0,cell:s.cell,nx:s.nx,nz:s.nz,ground:s.ground,date:s.date,day:s.day,min:s.min,max:s.max,sixPlus:s.sixPlus,cells:a.join('')};
  }
  function bimResRainData(r){
    var n=r.nx*r.nz,a=[],k;
    function r3(v){return Math.round(v*1000)/1000;}
    for(k=0;k<n;k++)a.push(r.pid[k]?'1':'0');
    return {x0:r.x0,z0:r.z0,cell:r.cell,nx:r.nx,nz:r.nz,cells:a.join(''),maxAcc:r.maxAcc,ponds:r.ponds.length,pondVolume:r.pondVolume,
      deepest:r.ponds.length?r.ponds[0].depth:0,threshold:r.threshold,segs:r.segs.map(function(g){return [r3(g[0]),r3(g[1]),r3(g[2]),r3(g[3]),Math.round(g[4]*100)/100];})};
  }
  /* Add as layer: sunhours, rain, terrain (the surface shown by slope, elevation or aspect, or
     opts.id and opts.mode), cutfill (a proposed surface's cut and fill) */
  function bimResultLayerAdd(kind,opts){
    opts=opts||{};
    var R=null,s=null,o=null,mode;
    if(kind==='sunhours'||kind==='rain'){
      s=kind==='sunhours'?A3D_SIM.sun:A3D_SIM.rain;
      if(!s){a3dToast('Run '+(kind==='sunhours'?'Sun hours':'Rain on terrain')+' first, then add it as a layer');return null;}
      if(bimResHolds(s)){a3dToast('This run is a layer already');return null;}
      R=kind==='sunhours'?{kind:'sunhours',name:'Sun hours, '+s.date,data:bimResSunData(s),opacity:0.6}:
        {kind:'rain',name:'Rain on '+s.name,src:s.terrain,data:bimResRainData(s),opacity:0.9};
    }else if(kind==='terrain'||kind==='cutfill'){
      o=opts.id?objById(opts.id):(kind==='cutfill'?A3D.objs.filter(function(x){return x.t==='terrain'&&x.grading;})[0]:bimAnzTerrainShown())||null;
      mode=kind==='cutfill'?'cutfill':String(opts.mode||(o&&o.tview)||'');
      if(!o||o.t!=='terrain'||!o.survey){a3dToast(kind==='cutfill'?'There is no proposed surface: GRADE a pad first':'Show a surface by slope, elevation or aspect first');return null;}
      if(!BIM_TVIEW_LABEL.hasOwnProperty(mode)||(mode==='cutfill'&&!o.grading)){a3dToast('A terrain layer shows slope, elevation or aspect, or a proposed surface\'s cut and fill');return null;}
      R={kind:'terrain',mode:mode,name:BIM_TVIEW_LABEL[mode]+', '+o.name,src:o.id,opacity:0.55};
    }else return null;
    pushUndo();
    R.id='res-'+Date.now().toString(36)+'-'+(A3D.seq++);
    R.visible=true;R.created=bimResNow();
    if(s){if(!s.runId)s.runId='run-'+Date.now().toString(36)+'-'+(A3D.seq++);R.run=s.runId;R.key=bimResKeyFrom(s.stamp,R.kind);}   /* as it was when it ran, not when it was added */
    bimResLayers().unshift(R);   /* a new layer goes on top */
    if(o&&o.tview===mode)delete o.tview;   /* the surface's own colours step aside for the layer's */
    A3D_LY.rsel='res:'+R.id;
    if(A3D_LY.secShut)delete A3D_LY.secShut.analysis;
    refreshLayers();refreshProps();paint();saveSoon();bimAnalyzeRefresh();
    a3dToast(R.name+' is a layer now, in Layers under Analysis');
    return R;
  }
  /* Update: run it again, on the layer's own date and surface */
  function bimResultLayerUpdate(id){
    var R=bimResById(id),r;
    if(!R)return false;
    if(R.kind==='terrain'){a3dToast(R.name+' follows its surface: it is up to date');return true;}
    if(R.kind==='sunhours'){r=bimSunHours({date:R.data&&R.data.date});if(r.error){a3dToast('Sun hours: '+r.error);return false;}}
    else{r=bimRainFlow(objById(R.src)?R.src:null);if(r.error){a3dToast('Rain flow: '+r.error);return false;}}
    pushUndo();
    R.data=R.kind==='sunhours'?bimResSunData(r):bimResRainData(r);
    if(R.kind==='rain')R.src=r.terrain;
    R.key=bimResKeyFrom(r.stamp,R.kind);R.updated=bimResNow();
    delete A3D_RES_IMG[R.id];
    refreshLayers();paint();saveSoon();bimAnalyzeRefresh();
    a3dToast(R.name+' updated');
    return true;
  }
  function bimResultLayerRemove(id){
    var L=bimResLayers(),i,nm;
    for(i=0;i<L.length;i++)if(L[i].id===id)break;
    if(i>=L.length)return false;
    pushUndo();
    nm=L[i].name;L.splice(i,1);delete A3D_RES_IMG[id];
    if(A3D_LY.rsel==='res:'+id)A3D_LY.rsel=null;
    refreshLayers();paint();saveSoon();bimAnalyzeRefresh();
    a3dToast(nm+' removed');
    return true;
  }
  function bimResultLayerSet(id,field,val){
    var R=bimResById(id),v;
    if(!R)return false;
    if(field==='visible')v=!!val&&val!=='false';
    else if(field==='opacity'){v=parseFloat(val);if(!isFinite(v)){a3dToast('Opacity is a percentage, 10 to 100');return false;}v=Math.max(0.1,Math.min(1,v>1?v/100:v));v=Math.round(v*100)/100;}
    else if(field==='name'){v=String(val==null?'':val).replace(/\s+/g,' ').replace(/^ | $/g,'').slice(0,60);if(!v){a3dToast('A layer needs a name');refreshLayers();return false;}}
    else return false;
    if(field==='visible'?(R.visible!==false)===v:R[field]===v)return true;
    pushUndo();
    R[field]=v;
    refreshLayers();paint();saveSoon();
    return true;
  }
  /* to: another layer's id (its place), or an index */
  function bimResultLayerMove(id,to){
    var L=bimResLayers(),i=-1,j=-1,k,R;
    for(k=0;k<L.length;k++){if(L[k].id===id)i=k;if(L[k].id===to)j=k;}
    if(typeof to==='number'&&isFinite(to))j=Math.max(0,Math.min(L.length-1,Math.round(to)));
    if(i<0||j<0||i===j)return false;
    pushUndo();
    R=L.splice(i,1)[0];L.splice(j,0,R);
    refreshLayers();paint();saveSoon();
    return true;
  }
  /* the layers from a file or a store: what can be drawn, the rest let go */
  function bimResValid(a){
    if(!Array.isArray(a))return [];
    return a.filter(function(R){
      if(!R||typeof R.id!=='string'||typeof R.name!=='string')return false;
      if(R.kind==='terrain')return typeof R.src==='string'&&/^(slope|elevation|aspect|cutfill)$/.test(R.mode);   /* a regex: this runs at start-up, before the table above is set */
      return (R.kind==='sunhours'||R.kind==='rain')&&!!R.data&&typeof R.data.cells==='string'&&R.data.cells.length===R.data.nx*R.data.nz&&
        isFinite(R.data.x0)&&isFinite(R.data.z0)&&R.data.cell>0;
    });
  }
  /* ---- drawing ---- */
  function bimDrawBandTris(ctx,tin,tb,sp,alpha){
    var j,a,b,c;
    ctx.save();ctx.globalAlpha*=alpha;
    for(j=0;j<tin.tris.length;j++){
      if(tb.tri[j]<0)continue;
      a=sp[tin.tris[j][0]];b=sp[tin.tris[j][1]];c=sp[tin.tris[j][2]];
      if(!a||!b||!c)continue;
      ctx.fillStyle=ctx.strokeStyle=tb.bands[tb.tri[j]].col;ctx.lineWidth=0.5;
      ctx.beginPath();ctx.moveTo(a[0],a[1]);ctx.lineTo(b[0],b[1]);ctx.lineTo(c[0],c[1]);ctx.closePath();ctx.fill();ctx.stroke();
    }
    ctx.restore();
  }
  function bimSimDrawFlow(ctx,V,W,H,segs,maxAcc,alpha){
    var lm=Math.log(maxAcc+1)||1,i,g,a,b;
    ctx.save();ctx.globalAlpha=alpha;ctx.strokeStyle='#1565c0';ctx.lineCap='round';
    for(i=0;i<segs.length;i++){
      g=segs[i];a=toScreen([g[0],0,g[1]],V,W,H);b=toScreen([g[2],0,g[3]],V,W,H);
      if(!a||!b)continue;
      ctx.lineWidth=0.8+2.6*Math.log(g[4]+1)/lm;
      ctx.beginPath();ctx.moveTo(a[0],a[1]);ctx.lineTo(b[0],b[1]);ctx.stroke();
    }
    ctx.restore();
  }
  function bimResImage(R){
    var c=A3D_RES_IMG[R.id],d=R.data,img;
    if(c&&c.d===d)return c.img;
    img=bimSimGridImage(d,R.kind==='sunhours'?function(k){var ch=d.cells.charAt(k);return ch==='.'?null:(BIM_SIM_RAMP[+ch]||null);}:function(k){return d.cells.charAt(k)==='1'?'#2f7fe0c0':null;});
    A3D_RES_IMG[R.id]={d:d,img:img};
    return img;
  }
  function bimResDraw(ctx,V,W,H,R){
    var op=bimResOpacity(R),d=R.data,o,tin,tb;
    if(R.kind==='sunhours'||R.kind==='rain'){
      if(!d||typeof d.cells!=='string')return false;
      bimSimDrawGrid(ctx,V,W,H,d,bimResImage(R),R.kind==='sunhours'?(d.ground||0):0,op);
      if(R.kind==='rain'&&Array.isArray(d.segs))bimSimDrawFlow(ctx,V,W,H,d.segs,d.maxAcc||0,op);
      return true;
    }
    if(R.kind!=='terrain'||bimResGone(R))return false;
    o=objById(R.src);tin=bimTerrainTin(o);
    tb=tin?(R.mode==='cutfill'?bimBandsOf(o,'cutfill'):bimTerrainBands(tin,R.mode)):null;
    if(!tb)return false;
    bimDrawBandTris(ctx,tin,tb,tin.P.map(function(p){return toScreen([p[0],0,p[1]],V,W,H);}),op);
    return true;
  }
  function drawResultLayers(ctx,V,W,H){
    A3D.lastResultDrawn=[];
    if(!bimCameraIsPlan())return;
    var L=bimResLayers(),i;
    for(i=L.length-1;i>=0;i--){
      if(L[i].visible===false)continue;
      try{if(bimResDraw(ctx,V,W,H,L[i]))A3D.lastResultDrawn.push(L[i].id);}
      catch(eR){console.warn('[BIM] A result layer could not be drawn',eR);}
    }
  }
"""
rep("""  /* the commands */
  function bimSunHoursCommand(opts){""", ENGINE + """  /* the commands */
  function bimSunHoursCommand(opts){""")

rep("""    if(!capMode)drawSimOverlays(ctx,V,W,H);  /* __acad3dV143: sun hours, ponds and flow lines */""",
    """    if(!capMode)drawSimOverlays(ctx,V,W,H);  /* __acad3dV143: sun hours, ponds and flow lines */
    if(!capMode)drawResultLayers(ctx,V,W,H); /* __acad3dV148: the results kept as layers, over the live ones */""")

# ---------------------------------------------------------------- saved: undo, the project, the file
rep("""site:A3D.site,roomScheme:A3D.roomScheme||'',classifications:A3D.classifications});
  }
  function pushUndo(){""", """site:A3D.site,roomScheme:A3D.roomScheme||'',classifications:A3D.classifications,resultLayers:A3D.resultLayers||[]});   /* __acad3dV148 */
  }
  function pushUndo(){""")
rep("""    A3D.classifications=Array.isArray(st.classifications)?st.classifications:[];
    bimEnsureTypes();""", """    A3D.classifications=Array.isArray(st.classifications)?st.classifications:[];
    if(Array.isArray(st.resultLayers))A3D.resultLayers=st.resultLayers;   /* __acad3dV148: a version from History has none, and keeps today's */
    bimEnsureTypes();""")
rep("""classifications:A3D.classifications,dataFeatures:A3D.dataFeatures||{},history:A3D.history||null}});   /* __acad3dV146 */""",
    """classifications:A3D.classifications,dataFeatures:A3D.dataFeatures||{},history:A3D.history||null,resultLayers:A3D.resultLayers||[]}});   /* __acad3dV146, __acad3dV148 */""")
rep("""classifications:A3D.classifications,dataFeatures:A3D.dataFeatures||{},history:A3D.history||null};   /* __acad3dV146 */""",
    """classifications:A3D.classifications,dataFeatures:A3D.dataFeatures||{},history:A3D.history||null,resultLayers:A3D.resultLayers||[]};   /* __acad3dV146, __acad3dV148 */""")
rep("""      A3D.history=bimHistValid(st&&st.history);   /* __acad3dV146: its history, or none */""",
    """      A3D.history=bimHistValid(st&&st.history);   /* __acad3dV146: its history, or none */
      A3D.resultLayers=bimResValid(st&&st.resultLayers);   /* __acad3dV148: its result layers, or none */
      A3D_RES_IMG={};""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
