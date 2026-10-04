"""patch_phase141a.py -- V141: a shorter right panel, and an Analyze tab.

The owner: "clean up the right side panels because it is too much as we add more stuff", and
"adding analyze below assets". With nothing selected, Properties held nine groups, about 2,460 px:

- Properties with nothing selected gets tabs -- Project | Site | View | Analysis -- each showing only
  its own groups (the others stay in the page, hidden, so every field keeps its handler):
  - Project: Identity Data (project, client, site), Statistics;
  - Site: Location (true north, latitude, longitude, UTC offset, the sun's date and time -- moved
    out of Identity Data), Map, Site Context, Data Layers;
  - View: View;
  - Analysis: Floor Loads, Analysis, Areas by Usage, Usages.
  The tab is remembered (per viewer). A command that opens a group (USAGES, COLOURBY, DATALAYERS,
  FINDDATA) turns to its tab.
- The left rail gets Analyze, below Assets: every analysis the app has, each with what it shows
  now and its buttons -- the frame (ANALYZE), the sun and shadows (SUNSTUDY), colour by, areas by
  usage, survey checks, buildings' LODs and solids, statistics. Settings opens the group in
  Properties, on its tab. ANALYSES opens the tab."""
NAME = 'patch_phase141a.py'
BASE = '8865255cbd70859646657afb7270f847db226977c180eae4084d9226e8f39b9d'
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


# ---- the tabs in Properties ----
rep("""    rows+=bimPropRow('True North (deg)','<input type="number" step="any" data-propmodel="truenorth" value="'+bimTrueNorthDeg()+'">');   /* __acad3dV103 */
    var sunS=bimSunSettings();   /* __acad3dV107: where the site is, and the moment studied */""",
    """    var loc='';   /* __acad3dV141: where the site is, in its own group on the Site tab */
    loc+=bimPropRow('True North (deg)','<input type="number" step="any" data-propmodel="truenorth" value="'+bimTrueNorthDeg()+'">');   /* __acad3dV103 */
    var sunS=bimSunSettings();   /* __acad3dV107: where the site is, and the moment studied */""")
for a in ("""    rows+=bimPropRow('Latitude (deg N)',""", """    rows+=bimPropRow('Longitude (deg E)',""", """    rows+=bimPropRow('UTC Offset (h)',""",
          """    rows+=bimPropRow('Sun Date',""", """    rows+=bimPropRow('Sun Time',""", """    rows+=bimPropText('Sun',bimSunText(bimSunNow()));"""):
    rep(a, a.replace('    rows+=', '    loc+='))
rep("""    h+=bimDataFeatureHtml();   /* __acad3dV134: the data clicked on the plan, first */
    h+=bimPropGroup('Identity Data',rows);
    h+=bimPropGroup('Map',bimMapPropsHtml());   /* __acad3dV132 */
    h+=bimPropGroup('Site Context',bimCtxModelHtml());   /* __acad3dV133 */
    h+=bimPropGroup('Data Layers',bimDataModelHtml());   /* __acad3dV134 */""",
    """    h+=bimDataFeatureHtml();   /* __acad3dV134: the data clicked on the plan, first */
    h+=bimPropTabsHtml();   /* __acad3dV141: Project | Site | View | Analysis */
    h+=bimPTab('project',bimPropGroup('Identity Data',rows));
    h+=bimPTab('site',bimPropGroup('Location',loc));   /* __acad3dV141 */
    h+=bimPTab('site',bimPropGroup('Map',bimMapPropsHtml()));   /* __acad3dV132 */
    h+=bimPTab('site',bimPropGroup('Site Context',bimCtxModelHtml()));   /* __acad3dV133 */
    h+=bimPTab('site',bimPropGroup('Data Layers',bimDataModelHtml()));   /* __acad3dV134 */""")
rep("""    h+=bimPropGroup('View',vrows);
""", """    h+=bimPTab('view',bimPropGroup('View',vrows));   /* __acad3dV141 */
""")
rep("""      h+=bimPropGroup('Floor Loads: '+bimEsc(lvA.name),lrows);
    }
    h+=bimAnalysisPropsHtml();   /* __acad3dV125: the model's Analysis page, beside its floor loads */
    h+=bimUsageAreasHtml(null,'Areas by Usage');   /* __acad3dV131 */
    h+=bimPropGroup('Usages',bimUsageLibraryHtml());
    h+=bimPropGroup('Statistics',srows);
    return h;""", """      h+=bimPTab('analysis',bimPropGroup('Floor Loads: '+bimEsc(lvA.name),lrows));   /* __acad3dV141 */
    }
    h+=bimPTab('analysis',bimAnalysisPropsHtml());   /* __acad3dV125: the model's Analysis page, beside its floor loads */
    h+=bimPTab('analysis',bimUsageAreasHtml(null,'Areas by Usage'));   /* __acad3dV131 */
    h+=bimPTab('analysis',bimPropGroup('Usages',bimUsageLibraryHtml()));
    h+=bimPTab('project',bimPropGroup('Statistics',srows));
    return h;""")

TABS = r"""  /* ================= __acad3dV141: Properties' tabs, with nothing selected =================
     The model's groups, sorted into four tabs. Every tab's groups are in the page and the others
     hidden, so each field keeps its handler and a command can reach it; the tab shown is the
     viewer's, remembered in this browser. */
  var BIM_PTABS=[{id:'project',label:'Project'},{id:'site',label:'Site'},{id:'view',label:'View'},{id:'analysis',label:'Analysis'}];
  var BIM_PTAB_KEY='acad3dPropTab';
  var A3D_PTAB=(function(){try{var v=localStorage.getItem(BIM_PTAB_KEY);return /^(project|site|view|analysis)$/.test(v||'')?v:'project';}catch(eT){return 'project';}})();
  function bimPTab(tab,html){
    if(!html)return '';
    return '<div class="a3d-ptabpane'+(tab===A3D_PTAB?' on':'')+'" data-ptab="'+tab+'">'+html+'</div>';
  }
  function bimPropTabsHtml(){
    return '<div class="a3d-ptabs" role="tablist">'+BIM_PTABS.map(function(b){
      return '<button type="button" role="tab" class="a3d-ptabbtn'+(b.id===A3D_PTAB?' on':'')+'" data-ptabbtn="'+b.id+'" aria-selected="'+(b.id===A3D_PTAB)+'">'+b.label+'</button>';
    }).join('')+'</div>';
  }
  /* the tab a model group is on; null for a group that is not tabbed */
  function bimPropTabOf(name){
    name=String(name||'');
    if(name==='Identity Data'||name==='Statistics')return 'project';
    if(name==='Location'||name==='Map'||name==='Site Context'||name==='Data Layers')return 'site';
    if(name==='View')return 'view';
    if(name.indexOf('Floor Loads')===0||name==='Analysis'||name==='Areas by Usage'||name==='Usages')return 'analysis';
    return null;
  }
  /* show a tab, in place: no re-render, so nothing typed is lost */
  function bimSetPropTab(tab){
    if(!/^(project|site|view|analysis)$/.test(String(tab)))return false;
    A3D_PTAB=tab;
    try{localStorage.setItem(BIM_PTAB_KEY,tab);}catch(eS){}
    if(el.propsbody){
      var P=el.propsbody.querySelectorAll('.a3d-ptabpane'),B=el.propsbody.querySelectorAll('.a3d-ptabbtn'),i;
      for(i=0;i<P.length;i++)P[i].classList.toggle('on',P[i].getAttribute('data-ptab')===tab);
      for(i=0;i<B.length;i++){var on=B[i].getAttribute('data-ptabbtn')===tab;B[i].classList.toggle('on',on);B[i].setAttribute('aria-selected',String(on));}
    }
    return true;
  }
  /* a command's way to a model group: nothing selected, the group open, on its tab */
  function bimPropReveal(name){
    var tb=bimPropTabOf(name);
    A3D_PROP_GROUPS_OPEN[name]=true;
    if(tb){A3D_PTAB=tb;try{localStorage.setItem(BIM_PTAB_KEY,tb);}catch(eS){}}
    return tb;
  }
  function bimPropTabClick(ev){
    var b=ev.target&&ev.target.closest?ev.target.closest('[data-ptabbtn]'):null;
    if(!b)return false;
    bimSetPropTab(b.getAttribute('data-ptabbtn'));
    return true;
  }
  /* ================= __acad3dV141: the Analyze tab ================= */
  var A3D_ANZ={lod:null};
  function bimAnzCard(id,title,status,acts,state){
    return '<div class="a3d-anzcard" data-anzcard="'+id+'"><div class="a3d-anzhd"><span class="a3d-anzttl">'+bimEsc(title)+'</span>'+
      (state?'<span class="a3d-anzstate a3d-anzstate-'+state+'">'+(state==='on'?'On':state==='warn'?'Check':state==='fail'?'Problems':'Off')+'</span>':'')+'</div>'+
      '<div class="a3d-anzst">'+bimEsc(status)+'</div><div class="a3d-anzacts">'+acts.map(function(a){
        return '<button type="button" class="a3d-anzbtn'+(a.pri?' pri':'')+'" data-anzact="'+a.act+'"'+(a.off?' disabled title="'+bimEsc(a.off)+'"':(a.tip?' title="'+bimEsc(a.tip)+'"':''))+'>'+bimEsc(a.label)+'</button>';
      }).join('')+'</div></div>';
  }
  /* each analysis: what it shows now, and its buttons */
  function bimAnzCards(){
    var C=[],i,o,nC=0,nB=0,nU=0,nTer=0,sv={pass:0,warn:0,fail:0},lods={};
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(bimIsFrameMember(o)){if(o.bim.type==='column')nC++;else nB++;}
      if(o.usage)nU++;
      if(o.t==='terrain'&&o.survey){nTer++;try{var rs=bimSurveyCheck(o);if(rs)sv[rs.verdict]=(sv[rs.verdict]||0)+1;}catch(eS){}}
      var L=bimLodOf(o);if(L)lods[L.lod]=(lods[L.lod]||0)+1;
    }
    var fr=nC+nB;
    C.push({id:'structure',title:'Structure',state:A3D_STRUCT.show?'on':'off',
      status:fr?nC+' column'+(nC===1?'':'s')+', '+nB+' beam'+(nB===1?'':'s')+(A3D_STRUCT.show?': forces and deflection shown':''):'No frame yet: place columns and beams',
      acts:[{act:'structure:run',label:A3D_STRUCT.show?'Run Again':'Run',pri:true,off:fr?'':'Place columns and beams first'},
        {act:'structure:off',label:'Hide',off:A3D_STRUCT.show?'':'Not shown'},{act:'open:Analysis',label:'Settings',off:fr?'':'Place columns and beams first'}]});
    var sun=bimSunNow();
    C.push({id:'sun',title:'Sun and Shadows',state:A3D.showSun?'on':'off',
      status:sun.missing?'Set the site '+sun.missing.join(', ')+' (Site: Location)':(sun.settings.time+' on '+sun.settings.date+(sun.elevation>0?', the sun at '+sun.elevation.toFixed(1)+'°':', the sun below the horizon')),
      acts:[{act:'sun:toggle',label:A3D.showSun?'Hide':'Show',pri:!A3D.showSun},{act:'open:Location',label:'Settings'}]});
    var ls=bimLensSettings();
    C.push({id:'lens',title:'Colour By',state:ls.by?'on':'off',status:ls.by?(BIM_LENS_LABEL[ls.by]||ls.by)+(ls.by==='prop'&&ls.prop?': '+ls.prop:''):'Off: colour the model by usage, level, type or any property',
      acts:[{act:'open:View',label:'Settings',pri:true}]});
    var us=bimUsageSummary(null);
    C.push({id:'areas',title:'Areas by Usage',state:null,status:us.rows.length?us.rows.length+' usage'+(us.rows.length===1?'':'s')+' on '+nU+' object'+(nU===1?'':'s')+', GBA '+bimDispNum(us.total.GBA,2)+' m²':'No usages given yet',
      acts:[{act:'open:Areas by Usage',label:'Open',pri:true},{act:'open:Usages',label:'Usages'}]});
    C.push({id:'survey',title:'Survey Check',state:nTer?(sv.fail?'fail':sv.warn?'warn':'on'):null,
      status:nTer?nTer+' surface'+(nTer===1?'':'s')+': '+sv.pass+' pass, '+sv.warn+' warn, '+sv.fail+' fail':'No survey surface yet: make one with SURVEY',
      acts:[{act:'survey:run',label:'Check',pri:true,off:nTer?'':'No survey surface yet'}]});
    var lk=Object.keys(lods).sort(),nb=0;lk.forEach(function(k){nb+=lods[k];});
    var last=A3D_ANZ.lod;
    C.push({id:'lod',title:'Buildings: LOD and Solids',state:last?(last.bad.length?'fail':'on'):null,
      status:nb?nb+' '+(nb===1?'building or city object':'buildings and city objects')+' ('+lk.map(function(k){return lods[k]+' LOD'+k;}).join(', ')+')'+(last?'; last check: '+last.valid+' valid'+(last.bad.length?', '+last.bad.length+' with problems':''):''):'No buildings yet: get them with Site Context, or import CityJSON',
      acts:[{act:'lod:run',label:'Check',pri:true,off:nb?'':'No buildings yet'},{act:'lod:cityjson',label:'Export CityJSON',off:nb?'':'No buildings yet'}]});
    C.push({id:'stats',title:'Statistics',state:null,status:A3D.objs.length+' object'+(A3D.objs.length===1?'':'s')+', '+A3D.levels.length+' level'+(A3D.levels.length===1?'':'s')+', '+A3D.sheets.length+' sheet'+(A3D.sheets.length===1?'':'s'),
      acts:[{act:'open:Statistics',label:'Open'}]});
    return C;
  }
  function bimAnalyzeHtml(){
    var C=bimAnzCards();
    return '<div class="a3d-anz"><div class="a3d-anzhead"><span class="a3d-anzttl0">Analyze</span><span class="a3d-anzcount">'+C.length+' analyses</span></div>'+
      '<div class="a3d-anzlist">'+C.map(function(c){return bimAnzCard(c.id,c.title,c.status,c.acts,c.state);}).join('')+'</div></div>';
  }
  /* the panel again, when it is open */
  function bimAnalyzeRefresh(){
    var sh=document.getElementById('a3d-shell'),w=sh&&sh.dataset.tab==='analyze'?sh.querySelector('.a3d-analyze-wrap'):null;
    if(!w)return false;
    try{w.innerHTML=bimAnalyzeHtml();}catch(eA){console.warn('[BIM] Analyze panel',eA);}
    return true;
  }
  /* a button: run it, or open its settings in Properties */
  function bimAnzAct(a){
    var k=String(a||''),g;
    if(k.indexOf('open:')===0){
      g=k.slice(5);
      A3D.sel=null;A3D.sel2=null;A3D.selSet=[];
      bimPropReveal(g);
      refreshTree();refreshProps();paint();
      var gEl=null,all=el.propsbody?el.propsbody.querySelectorAll('[data-a3dpgrp]'):[],i;
      for(i=0;i<all.length;i++)if(all[i].getAttribute('data-a3dpgrp').indexOf(g)===0){gEl=all[i];break;}
      if(gEl){try{gEl.scrollIntoView({block:'start'});}catch(eS){}}
      bimAnalyzeRefresh();
      return true;
    }
    if(k==='structure:run')bimAnalyzeCommand();
    else if(k==='structure:off')bimAnalyzeOff();
    else if(k==='sun:toggle')bimToggleSun();
    else if(k==='survey:run')bimSurveyCheckCommand();
    else if(k==='lod:run')bimLodCheck();
    else if(k==='lod:cityjson')bimCityJsonExport();
    else return false;
    bimAnalyzeRefresh();
    return true;
  }
  function bimAnalyzeCommandTab(){bimShellSetTab('analyze');return true;}
"""
rep("""  /* __acad3dV73: the no-selection inspector.""", TABS + """  /* __acad3dV73: the no-selection inspector.""")

# commands that open a model group turn to its tab
rep("""    A3D.sel=null;A3D.sel2=null;A3D.selSet=[];
    A3D_PROP_GROUPS_OPEN['Usages']=true;""", """    A3D.sel=null;A3D.sel2=null;A3D.selSet=[];
    bimPropReveal('Usages');   /* __acad3dV141: on the Analysis tab */""")
rep("""    A3D.sel=null;A3D.sel2=null;A3D.selSet=[];
    A3D_PROP_GROUPS_OPEN['View']=true;""", """    A3D.sel=null;A3D.sel2=null;A3D.selSet=[];
    bimPropReveal('View');   /* __acad3dV141 */""")
rep("""    A3D.sel=null;A3D.sel2=null;A3D.selSet=[];
    A3D_PROP_GROUPS_OPEN['Data Layers']=true;""", """    A3D.sel=null;A3D.sel2=null;A3D.selSet=[];
    bimPropReveal('Data Layers');   /* __acad3dV141: on the Site tab */""")
rep("""    if(sun.missing)a3dToast('Sun study: set the site '+sun.missing.join(', ')+' in Properties, with nothing selected');""",
    """    if(sun.missing)a3dToast('Sun study: set the site '+sun.missing.join(', ')+' in Properties, with nothing selected (Site: Location)');""")
rep("""    a3dToast(B.length+' building'+(B.length===1?'':'s')+' ('+ls+'): '+ok+' valid'+""",
    """    A3D_ANZ.lod={valid:ok,bad:badL.slice()};   /* __acad3dV141: the Analyze tab shows the last check */
    a3dToast(B.length+' building'+(B.length===1?'':'s')+' ('+ls+'): '+ok+' valid'+""")

# the Analyze panel refreshes with Properties
rep("""    bimSyncStatusHint();
    if(!el.propsbody)return;
    var o=objById(A3D.sel);""", """    bimSyncStatusHint();
    bimAnalyzeRefresh();   /* __acad3dV141 */
    if(!el.propsbody)return;
    var o=objById(A3D.sel);""")

# ---- the rail: Analyze below Assets ----
rep("""      '<button type="button" class="a3d-railbtn" data-tab="assets" title="Assets" aria-label="Assets">'+
      bimRailIcon('assets')+'</button>'+""", """      '<button type="button" class="a3d-railbtn" data-tab="assets" title="Assets" aria-label="Assets">'+
      bimRailIcon('assets')+'</button>'+
      '<button type="button" class="a3d-railbtn" data-tab="analyze" title="Analyze" aria-label="Analyze">'+   /* __acad3dV141 */
      bimRailIcon('analyze')+'</button>'+""")
rep("""    assets:'<path d="m9 2 1.8 4.2L15 8l-4.2 1.8L9 14l-1.8-4.2L3 8l4.2-1.8z"/>'
  };""", """    assets:'<path d="m9 2 1.8 4.2L15 8l-4.2 1.8L9 14l-1.8-4.2L3 8l4.2-1.8z"/>',
    /* __acad3dV141: bars and a trend, the Analyze tab */
    analyze:'<path d="M2.5 15.5h13"/><path d="M4.5 13V9.5M8 13V6.5M11.5 13V8.5M15 13V4"/><path d="M3.5 7.5 7.5 4l3.5 2.5 4.5-4" stroke-dasharray="1.6 1.4"/>'
  };""")
rep("""    if(shell.dataset.tab!=='assets'){
      var stale=panel.querySelector('.a3d-assets-wrap');
      if(stale){stale.parentNode.removeChild(stale);did=true;}
    }""", """    if(shell.dataset.tab!=='assets'){
      var stale=panel.querySelector('.a3d-assets-wrap');
      if(stale){stale.parentNode.removeChild(stale);did=true;}
    }
    if(shell.dataset.tab==='analyze'&&!panel.querySelector('.a3d-analyze-wrap')){   /* __acad3dV141 */
      var abox=document.createElement('div');
      abox.className='a3d-tabbody a3d-analyze-wrap';
      abox.innerHTML=bimAnalyzeHtml();
      abox.addEventListener('click',function(ev){
        var b=ev.target&&ev.target.closest?ev.target.closest('[data-anzact]'):null;
        if(!b||b.disabled)return;
        try{bimAnzAct(b.getAttribute('data-anzact'));}catch(eZ){console.warn('[BIM] Analyze',eZ);a3dToast('That did not work - see the console');}
      });
      panel.appendChild(abox);
      did=true;
    }
    if(shell.dataset.tab!=='analyze'){
      var astale=panel.querySelector('.a3d-analyze-wrap');
      if(astale){astale.parentNode.removeChild(astale);did=true;}
    }""")

# the tab strip's clicks
rep("""    /* __acad3dV138: the survey check */
    if(el.propsbody)el.propsbody.addEventListener('change',function(ev){""",
    """    /* __acad3dV141: Properties' tabs */
    if(el.propsbody)el.propsbody.addEventListener('click',function(ev){
      try{bimPropTabClick(ev);}catch(eTB){console.warn('[BIM] Properties tab',eTB);}
    });
    /* __acad3dV138: the survey check */
    if(el.propsbody)el.propsbody.addEventListener('change',function(ev){""")

# the shell audit claims the new controls
rep("""    {sel:'[data-a3dasdel]',why:'removes a model, block or template the user added to the library, after asking'},""",
    """    {sel:'[data-a3dasdel]',why:'removes a model, block or template the user added to the library, after asking'},
    /* __acad3dV141: the Analyze tab -- each driven by the V141 suite before it was claimed */
    {sel:'.a3d-railbtn[data-tab="analyze"]',why:'Analyze tab: every analysis, what it shows now, run it or open its settings'},
    {sel:'[data-anzact]',why:'an analysis: run it, show or hide it, or open its settings in Properties'},""")
# commands
rep("""    ['ANALYZE',['ANALYSE','AN'],'analyze','Solve the frame and show its forces and deflection over the model'],""",
    """    ['ANALYZE',['ANALYSE','AN'],'analyze','Solve the frame and show its forces and deflection over the model'],
    ['ANALYSES',['ANALYZEPANEL','ANALYSISPANEL'],'analyses','The Analyze tab: every analysis, what it shows now, and its settings'],   /* __acad3dV141 */""")
rep("""    analyze:function(){bimAnalyzeCommand();},                    /* __acad3dV125 */""",
    """    analyze:function(){bimAnalyzeCommand();},                    /* __acad3dV125 */
    analyses:function(){bimAnalyzeCommandTab();},                 /* __acad3dV141 */""")
rep("""    LODCHECK:'lod level""", """    ANALYSES:'analysis analyses analyze dashboard results checks studies simulation sun shadow structure areas survey',   /* __acad3dV141 */
    LODCHECK:'lod level""")

# styles
rep(""".a3d-lodtag{""", """.a3d-ptabs{display:flex;gap:2px;margin:0 0 10px;padding:3px;border-radius:8px;background:rgba(255,255,255,.05);position:sticky;top:0;z-index:2}
.a3d-ptabbtn{flex:1;border:0;border-radius:6px;padding:5px 4px;background:transparent;color:#9aa3ad;font:inherit;font-size:12px;cursor:pointer}
.a3d-ptabbtn:hover{color:#fff;background:rgba(255,255,255,.06)}
.a3d-ptabbtn.on{background:rgba(255,255,255,.14);color:#fff;font-weight:600}
.a3d-ptabpane{display:none}.a3d-ptabpane.on{display:block}
body.light-theme .a3d-ptabs{background:rgba(0,0,0,.05)}
body.light-theme .a3d-ptabbtn{color:#6b7280}
body.light-theme .a3d-ptabbtn.on{background:#fff;color:#111}
#a3d-shell[data-tab="analyze"] .a3d-projhead{flex-shrink:0}
#a3d-shell[data-tab="analyze"] .a3d-analyze-wrap{flex:1 1 auto;min-height:0}
.a3d-anz{display:flex;flex-direction:column;min-height:0;flex:1;overflow:auto;padding:10px 12px 16px}
.a3d-anzhead{display:flex;align-items:baseline;justify-content:space-between;margin:2px 0 10px}
.a3d-anzttl0{font-weight:700;font-size:14px}
.a3d-anzcount{color:#8a96a3;font-size:12px}
.a3d-anzlist{display:flex;flex-direction:column;gap:8px}
.a3d-anzcard{border:1px solid rgba(255,255,255,.1);border-radius:9px;padding:9px 10px;background:rgba(255,255,255,.03)}
.a3d-anzhd{display:flex;align-items:center;justify-content:space-between;gap:6px}
.a3d-anzttl{font-weight:600;font-size:13px}
.a3d-anzstate{font-size:11px;padding:1px 6px;border-radius:9px;background:rgba(255,255,255,.08);color:#9aa3ad}
.a3d-anzstate-on{background:rgba(76,175,80,.18);color:#81c784}
.a3d-anzstate-warn{background:rgba(255,183,77,.18);color:#ffb74d}
.a3d-anzstate-fail{background:rgba(239,83,80,.18);color:#ef9a9a}
.a3d-anzst{color:#aab4bf;font-size:12px;margin:4px 0 7px;line-height:1.35}
.a3d-anzacts{display:flex;flex-wrap:wrap;gap:5px}
.a3d-anzbtn{border:1px solid rgba(255,255,255,.14);border-radius:6px;padding:3px 9px;background:transparent;color:#dfe5ea;font:inherit;font-size:12px;cursor:pointer}
.a3d-anzbtn:hover{background:rgba(255,255,255,.08)}
.a3d-anzbtn.pri{background:#2f6fd6;border-color:#2f6fd6;color:#fff}
.a3d-anzbtn:disabled{opacity:.45;cursor:default}
body.light-theme .a3d-anzcard{border-color:rgba(0,0,0,.1);background:#fff}
body.light-theme .a3d-anzst{color:#555}
body.light-theme .a3d-anzbtn{border-color:rgba(0,0,0,.15);color:#222}
body.light-theme .a3d-anzbtn.pri{color:#fff}
.a3d-lodtag{""")

# hooks
rep("""  /* __acad3dV140: LOD2 roofs */""", """  /* __acad3dV141: tabs and the Analyze tab */
  window.__a3dPropTab=function(){return A3D_PTAB;};
  window.__a3dSetPropTab=function(t){return bimSetPropTab(t);};
  window.__a3dPropTabOf=function(n){return bimPropTabOf(n);};
  window.__a3dAnalyzeCards=function(){return JSON.parse(JSON.stringify(bimAnzCards()));};
  window.__a3dAnalyzeAct=function(a){return bimAnzAct(a);};
  window.__acad3dV141='proptabs,locationgroup,tabremembered,tabreveal,analyzerail,analyzecards,analyzeopen,analyzerun,analysescommand';
  /* __acad3dV140: LOD2 roofs */""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
