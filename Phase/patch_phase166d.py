"""patch_phase166d.py -- V166b: the right panel's Analysis tab, gone; its settings in Analyze.

  Properties   three tabs with nothing selected: Project, Site, View. A tab remembered as Analysis
               opens on Project.
  Analyze      Frame analysis holds the frame's settings and results, and the active level's floor
               loads, in its row; Areas by usage holds the project's areas by usage. Their fields
               are wired in Analyze, and the search finds a row by its settings' names.
  Usages       the project's own, on Project.
"""
import hashlib, pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
BASE = '1a7fe75e5c64d6d666c4ef9ae6a1fb0b60cd4b4714a47487e83270f6a5b33ccf'   # V166, after patch_phase166c.py

raw = SRC.read_bytes()
sha = hashlib.sha256(raw).hexdigest()
if sha != BASE:
    sys.exit('baseline sha mismatch: %s' % sha)
txt = raw.decode('utf-8')
assert '__acad3dV166b' not in txt, 'already patched'


def rep(old, new, count=1):
    global txt
    n = txt.count(old)
    assert n == count, 'anchor count %d (wanted %d): %r' % (n, count, old[:80])
    txt = txt.replace(old, new)


# ---- Properties: three tabs ----
rep("""  /* ================= __acad3dV141: Properties' tabs, with nothing selected =================
     The model's groups, sorted into four tabs. Every tab's groups are in the page and the others
     hidden, so each field keeps its handler and a command can reach it; the tab shown is the
     viewer's, remembered in this browser. */
  var BIM_PTABS=[{id:'project',label:'Project'},{id:'site',label:'Site'},{id:'view',label:'View'},{id:'analysis',label:'Analysis'}];
  var BIM_PTAB_KEY='acad3dPropTab';
  var A3D_PTAB=(function(){try{var v=localStorage.getItem(BIM_PTAB_KEY);return /^(project|site|view|analysis)$/.test(v||'')?v:'project';}catch(eT){return 'project';}})();
""", """  /* ================= __acad3dV141: Properties' tabs, with nothing selected =================
     The model's groups, sorted into tabs. Every tab's groups are in the page and the others
     hidden, so each field keeps its handler and a command can reach it; the tab shown is the
     viewer's, remembered in this browser.
     __acad3dV166b: three tabs. The Analysis tab was Analyze's settings, left behind when Analyze moved
     to the left; they are in Analyze now, in the rows they set, and the usages are on Project. */
  var BIM_PTABS=[{id:'project',label:'Project'},{id:'site',label:'Site'},{id:'view',label:'View'}];
  var BIM_PTAB_KEY='acad3dPropTab';
  function bimPTabOk(t){return BIM_PTABS.some(function(b){return b.id===t;});}
  var A3D_PTAB=(function(){try{var v=localStorage.getItem(BIM_PTAB_KEY);return bimPTabOk(v)?v:'project';}catch(eT){return 'project';}})();
""")
rep("""    if(name==='Identity Data'||name==='Statistics'||name==='History')return 'project';   /* __acad3dV146: History */
""", """    if(name==='Identity Data'||name==='Usages'||name==='Statistics'||name==='History')return 'project';   /* __acad3dV146: History; __acad3dV166b: Usages */
""")
rep("""    if(name.indexOf('Floor Loads')===0||name==='Analysis'||name==='Areas by Usage'||name==='Usages')return 'analysis';
""", "")
rep("""    if(!/^(project|site|view|analysis)$/.test(String(tab)))return false;
""", """    if(!bimPTabOk(String(tab)))return false;
""")

# ---- the no-selection groups: the Analysis tab's are gone ----
rep("""    h+=bimPropTabsHtml();   /* __acad3dV141: Project | Site | View | Analysis */
""", """    h+=bimPropTabsHtml();   /* __acad3dV141: Project | Site | View */
""")
rep("""    /* __acad3dV106: the ACTIVE level's floor loads -- what its floors and roof put on the columns
       under them. Here, with the model's level picker, because the Levels rows are not on screen. */
    var lvA=null;
    for(i=0;i<A3D.levels.length;i++)if(A3D.levels[i].id===A3D.activeLevel)lvA=A3D.levels[i];
    if(lvA){
      var lrows=bimPropRow('Dead (kPa)','<input type="number" step="any" min="0" data-propmodel="dl" value="'+(lvA.dl==null?'':lvA.dl)+'" placeholder="not set" title="Dead load on '+bimEsc(lvA.name)+', kPa: slab self-weight plus superimposed">');
      lrows+=bimPropRow('Live (kPa)','<input type="number" step="any" min="0" data-propmodel="ll" value="'+(lvA.ll==null?'':lvA.ll)+'" placeholder="not set" title="Live load on '+bimEsc(lvA.name)+', kPa, unreduced">');
      h+=bimPTab('analysis',bimPropGroup('Floor Loads: '+bimEsc(lvA.name),lrows));   /* __acad3dV141 */
    }
    h+=bimPTab('analysis',bimAnalysisPropsHtml());   /* __acad3dV125: the model's Analysis page, beside its floor loads */
    h+=bimPTab('analysis',bimUsageAreasHtml(null,'Areas by Usage'));   /* __acad3dV131 */
    h+=bimPTab('analysis',bimPropGroup('Usages',bimUsageLibraryHtml()));
""", """    /* __acad3dV166b: the active level's floor loads and the frame's settings are in Analyze's Frame
       analysis, the project's areas by usage in its Areas by usage. The usages are the project's own --
       the rooms, floors and masses take them, Colour by and the schedules read them -- so they are here. */
    h+=bimPTab('project',bimPropGroup('Usages',bimUsageLibraryHtml()));   /* __acad3dV131 */
""")
rep("""    bimPropReveal('Usages');   /* __acad3dV141: on the Analysis tab */
""", """    bimPropReveal('Usages');   /* __acad3dV141; __acad3dV166b: on the Project tab */
""")
# Properties' handler for the floor loads it no longer shows
rep("""        if(mk==='dl'||mk==='ll'){updateLevel(A3D.activeLevel,mk,mv);return;}   /* __acad3dV106 */
""", "")

# ---- the frame's settings, and the floor loads, as Analyze shows them ----
rep("""  function bimAnalysisPropsHtml(){
    var rows='',cur=A3D_STRUCT.show?(A3D_STRUCT.diagram||'M'):'off',nC=0,nB=0,i;
    for(i=0;i<A3D.objs.length;i++)if(bimIsFrameMember(A3D.objs[i])){if(A3D.objs[i].bim.type==='column')nC++;else nB++;}
    if(!nC&&!nB)return '';
    rows+=bimPropText('Frame',nC+' column(s), '+nB+' beam(s)');
    rows+=bimPropText('Basis',(bimCombo(A3D_STRUCT.combo)||BIM_COMBOS[0]).why);
    rows+=bimPropRow('Combination','<select data-propstr="combo">'+BIM_COMBOS.map(function(c){return bimOpt(c.name,c.name,A3D_STRUCT.combo);}).join('')+'</select>');
    rows+=bimPropRow('Self-weight','<select data-propstr="selfweight">'+bimOpt('1','Included in D',A3D_STRUCT.selfWeight?'1':'0')+bimOpt('0','Not included',A3D_STRUCT.selfWeight?'1':'0')+'</select>');
    rows+=bimPropRow('Display','<select data-propstr="display">'+bimOpt('off','Off',cur)+bimOpt('M','Bending moment',cur)+bimOpt('N','Axial force',cur)+bimOpt('V','Shear',cur)+'</select>');
    rows+=bimPropRow('Deflected shape','<select data-propstr="deflected">'+bimOpt('1','Shown',A3D_STRUCT.deflected?'1':'0')+bimOpt('0','Hidden',A3D_STRUCT.deflected?'1':'0')+'</select>');
    var r=A3D_STRUCT.res;
    if(r&&r.error)rows+=bimPropText('Result',r.error);
    else{
      var c=bimStructCurrent();
      if(c){
        var hd=bimStructHeadline(c);
        rows+=bimPropText('Largest moment',hd.moment?hd.moment.v.toFixed(1)+' kN\\u00b7m, '+hd.moment.name:'none');
        rows+=bimPropText('Largest deflection',hd.defl?(hd.defl.v*1000).toFixed(1)+' mm'+(hd.ratio?' (L/'+hd.ratio+')':'')+', '+hd.defl.name:'none');
        rows+=bimPropText('Equilibrium',hd.balanced?'Balanced, '+hd.load.toFixed(1)+' kN':'NOT balanced: loads '+hd.load.toFixed(1)+', reactions '+hd.reaction.toFixed(1)+' kN');
      }else rows+=bimPropText('Result',r?'Out of date: run ANALYZE':'Run ANALYZE to solve the frame');
    }
    rows+=bimPropText('Not included','Floor loads, wind, seismic');
    return bimPropGroup('Analysis',rows);
  }
""", r"""  /* __acad3dV166b: Frame analysis's settings and results, and the active level's floor loads, in its
     row in Analyze. They were Properties' Analysis page (V125) and its Floor Loads (V106). The fields
     keep their keys (data-propstr), so one handler serves them; the floor loads' are data-anzload. */
  function bimAnzField(id,label,ctl){return '<div class="a3d-anzfld"><label class="a3d-anzlab" for="a3d-anzf-'+id+'">'+bimEsc(label)+'</label>'+ctl+'</div>';}
  function bimAnzKv(rows){return '<dl class="a3d-anzkv">'+rows.map(function(r){return '<dt>'+bimEsc(r[0])+'</dt><dd>'+bimEsc(r[1])+'</dd>';}).join('')+'</dl>';}
  function bimAnzFrameHtml(){
    var h='',cur=A3D_STRUCT.show?(A3D_STRUCT.diagram||'M'):'off',nC=0,nB=0,i,lvA=null,kv=[];
    for(i=0;i<A3D.objs.length;i++)if(bimIsFrameMember(A3D.objs[i])){if(A3D.objs[i].bim.type==='column')nC++;else nB++;}
    if(nC||nB){
      h+='<div class="a3d-anzform">'+
        bimAnzField('combo','Combination','<select id="a3d-anzf-combo" data-propstr="combo">'+BIM_COMBOS.map(function(c){return bimOpt(c.name,c.name,A3D_STRUCT.combo);}).join('')+'</select>')+
        bimAnzField('selfweight','Self-weight','<select id="a3d-anzf-selfweight" data-propstr="selfweight">'+bimOpt('1','Included in D',A3D_STRUCT.selfWeight?'1':'0')+bimOpt('0','Not included',A3D_STRUCT.selfWeight?'1':'0')+'</select>')+
        bimAnzField('display','Display','<select id="a3d-anzf-display" data-propstr="display">'+bimOpt('off','Off',cur)+bimOpt('M','Bending moment',cur)+bimOpt('N','Axial force',cur)+bimOpt('V','Shear',cur)+'</select>')+
        bimAnzField('deflected','Deflected shape','<select id="a3d-anzf-deflected" data-propstr="deflected">'+bimOpt('1','Shown',A3D_STRUCT.deflected?'1':'0')+bimOpt('0','Hidden',A3D_STRUCT.deflected?'1':'0')+'</select>')+
        '</div>';
      kv.push(['Basis',(bimCombo(A3D_STRUCT.combo)||BIM_COMBOS[0]).why]);
      var r=A3D_STRUCT.res;
      if(r&&r.error)kv.push(['Result',r.error]);
      else{
        var c=bimStructCurrent();
        if(c){
          var hd=bimStructHeadline(c);
          kv.push(['Largest moment',hd.moment?hd.moment.v.toFixed(1)+' kN\u00b7m, '+hd.moment.name:'none']);
          kv.push(['Largest deflection',hd.defl?(hd.defl.v*1000).toFixed(1)+' mm'+(hd.ratio?' (L/'+hd.ratio+')':'')+', '+hd.defl.name:'none']);
          kv.push(['Equilibrium',hd.balanced?'Balanced, '+hd.load.toFixed(1)+' kN':'NOT balanced: loads '+hd.load.toFixed(1)+', reactions '+hd.reaction.toFixed(1)+' kN']);
        }else kv.push(['Result',r?'Out of date: run it again':'Run it to solve the frame']);
      }
      kv.push(['Not included','Floor loads, wind, seismic']);
      h+=bimAnzKv(kv);
    }
    for(i=0;i<A3D.levels.length;i++)if(A3D.levels[i].id===A3D.activeLevel)lvA=A3D.levels[i];
    if(lvA){
      h+='<div class="a3d-anzsub">Floor loads on '+bimEsc(lvA.name)+'</div>'+
        '<div class="a3d-anzform">'+
        bimAnzField('dl','Dead (kPa)','<input type="number" step="any" min="0" inputmode="decimal" id="a3d-anzf-dl" data-anzload="dl" value="'+(lvA.dl==null?'':lvA.dl)+'" placeholder="not set" title="Dead load on '+bimEsc(lvA.name)+', kPa: slab self-weight plus superimposed">')+
        bimAnzField('ll','Live (kPa)','<input type="number" step="any" min="0" inputmode="decimal" id="a3d-anzf-ll" data-anzload="ll" value="'+(lvA.ll==null?'':lvA.ll)+'" placeholder="not set" title="Live load on '+bimEsc(lvA.name)+', kPa, unreduced">')+
        '</div><div class="a3d-anzcap">What this level\'s floors and roof put on the columns under them, in the Column Loads schedule and TRIBAREA. The active level is set in Properties, View.</div>';
    }
    return h;
  }
  /* __acad3dV166b: the project's areas by usage, in Areas by usage's row: each usage, then the total */
  function bimAnzAreasHtml(){
    var s=bimUsageSummary(null),h='';
    if(!s.rows.length)return '<div class="a3d-anzcap">Give a room, a floor or a mass a usage in its Properties (USAGE).</div>';
    s.rows.forEach(function(g){
      var k,v=[];
      for(k in g.values)if(g.values.hasOwnProperty(k))v.push(k+' '+bimUsageNum(g.values[k]));
      h+='<div class="a3d-anzarea" data-anzarea="'+bimEsc(g.usage)+'"><div class="a3d-anzareahd">'+bimUsageSwatch(g.color)+'<span class="a3d-anzareanm">'+bimEsc(g.name)+'</span>'+
        '<span class="a3d-anzarean">'+g.count+'</span></div>'+
        '<div class="a3d-anzareav">GBA '+bimDispNum(g.GBA,2)+' \u00b7 GFA '+bimDispNum(g.GFA,2)+' \u00b7 NSA '+bimDispNum(g.NSA,2)+' m\u00b2</div>'+
        (v.length?'<div class="a3d-anzareav">'+bimEsc(v.join(', '))+'</div>':'')+
        (g.errors?'<div class="a3d-anzareav a3d-anzareaerr">'+g.errors+' formula error'+(g.errors===1?'':'s')+'</div>':'')+'</div>';
    });
    if(s.rows.length>1)h+='<div class="a3d-anzarea a3d-anzareatot"><div class="a3d-anzareahd"><span class="a3d-anzareanm">Total</span></div>'+
      '<div class="a3d-anzareav">GBA '+bimDispNum(s.total.GBA,2)+' \u00b7 GFA '+bimDispNum(s.total.GFA,2)+' \u00b7 NSA '+bimDispNum(s.total.NSA,2)+' m\u00b2</div></div>';
    return h;
  }
  /* __acad3dV166b: the settings in a row change the model at once, so the list is drawn again with the
     field kept; a refresh held for a field (V162) is for words not yet committed */
  function bimAnzWireFields(w){
    w.addEventListener('change',function(ev){
      var e=ev.target,k;
      if(!e||!e.getAttribute)return;
      try{
        if(e.hasAttribute('data-propstr')){bimStructPropChange(ev);bimAnalyzeRefresh(true);return;}
        if((k=e.getAttribute('data-anzload'))){updateLevel(A3D.activeLevel,k,e.value);bimAnalyzeRefresh(true);}
      }catch(eF){console.warn('[BIM] Analyze setting failed',eF);a3dToast('That setting could not be changed - see the console');}
    });
  }
""")

# ---- the two rows ----
rep("""      acts:[{act:'structure:run',label:A3D_STRUCT.show?'Run again':'Run',pri:true,off:fr?'':'Place columns and beams first'},
        {act:'structure:off',label:'Hide',off:A3D_STRUCT.show?'':'Not shown'},{act:'open:Analysis',label:'Settings',off:fr?'':'Place columns and beams first'}]});
""", """      extra:bimAnzFrameHtml(),   /* __acad3dV166b: its settings, and the floor loads, in the row */
      acts:[{act:'structure:run',label:A3D_STRUCT.show?'Run again':'Run',pri:true,off:fr?'':'Place columns and beams first'},
        {act:'structure:off',label:'Hide',off:A3D_STRUCT.show?'':'Not shown'}]});
""")
rep("""      acts:[{act:'open:Areas by Usage',label:'Open',pri:true},{act:'open:Usages',label:'Usages'}]});
""", """      extra:bimAnzAreasHtml(),   /* __acad3dV166b: the areas, in the row; the usages are in Properties, Project */
      acts:[{act:'open:Usages',label:'Usages'}]});
""")
# the search reads a row's settings' names too
rep("""  function bimAnzRowText(r,more){return r.getAttribute('data-anzcard')+' '+bimAnzTexts(r,'.a3d-anzttl,.a3d-anzst,.a3d-anzbtn')+' '+(more||'');}
""", """  function bimAnzRowText(r,more){return r.getAttribute('data-anzcard')+' '+bimAnzTexts(r,'.a3d-anzttl,.a3d-anzst,.a3d-anzbtn,.a3d-anzlab,.a3d-anzsub')+' '+(more||'');}   /* __acad3dV166b: its settings' names */
""")
rep("""      bimSaWire(abox);   /* __acad3dV158 */
""", """      bimSaWire(abox);   /* __acad3dV158 */
      bimAnzWireFields(abox);   /* __acad3dV166b */
""")

# ---- the rows' settings, styled as Analyze's fields are ----
rep(""".a3d-anzramp{display:flex;flex:1;height:8px;border-radius:3px;overflow:hidden}.a3d-anzramp i{flex:1}
""", r""".a3d-anzramp{display:flex;flex:1;height:8px;border-radius:3px;overflow:hidden}.a3d-anzramp i{flex:1}
/* __acad3dV166b: a row's settings and readings, in Analyze */
/* a label and its field side by side where the row has room, the field under its label where not */
.a3d-anzform{display:flex;flex-direction:column;gap:6px;margin:0 0 8px}
.a3d-anzfld{display:flex;flex-wrap:wrap;align-items:center;gap:3px 8px;min-width:0}
.a3d-anzlab{flex:1 0 96px;font-size:11.5px;color:#8a96a3;min-width:0;overflow-wrap:anywhere}
.a3d-anzfld>select,.a3d-anzfld>input{flex:1 1 140px;min-width:0;width:auto}
.a3d-sa .a3d-anzform input[type=number]{box-sizing:border-box;background:#1f2327;border:1px solid #3a4048;border-radius:6px;color:#e6eaef;padding:3px 7px;min-height:26px;font:inherit;font-size:12px}
.a3d-anzkv{display:grid;grid-template-columns:minmax(0,42fr) minmax(0,58fr);gap:3px 8px;margin:0 0 8px;font-size:11.5px;line-height:1.35}
.a3d-anzkv dt{color:#8a96a3;margin:0;min-width:0}
.a3d-anzkv dd{margin:0;color:#d5dae0;min-width:0;overflow-wrap:anywhere;font-variant-numeric:tabular-nums}
.a3d-anzsub{font-size:11.5px;font-weight:600;color:#c9d1d9;border-top:1px solid rgba(255,255,255,.08);padding-top:8px;margin:2px 0 6px}
.a3d-anzcap{font-size:11px;color:#8a96a3;line-height:1.4;margin:0 0 8px}
.a3d-anzarea{padding:5px 0;border-bottom:1px solid rgba(255,255,255,.06);min-width:0}
.a3d-anzarea:last-child{border-bottom:0;margin-bottom:6px}
.a3d-anzareahd{display:flex;align-items:center;gap:0;font-size:12px;color:#d5dae0;min-width:0}
.a3d-anzareanm{flex:1 1 auto;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.a3d-anzarean{flex:0 0 auto;font-size:11px;color:#8a96a3;margin-left:8px;font-variant-numeric:tabular-nums}
.a3d-anzareav{font-size:11px;color:#9aa5b0;margin:2px 0 0 16px;font-variant-numeric:tabular-nums;overflow-wrap:anywhere}
.a3d-anzareatot .a3d-anzareahd{font-weight:600}.a3d-anzareatot .a3d-anzareav{margin-left:0}
.a3d-anzareaerr{color:#ef8a8d}
@media(pointer:coarse){.a3d-sa .a3d-anzform input[type=number]{min-height:36px;font-size:16px}.a3d-anzlab,.a3d-anzkv{font-size:12.5px}}
body.light-theme .a3d-sa .a3d-anzform input[type=number]{background:#fff;border-color:#c9ced4;color:#222}
body.light-theme .a3d-anzlab,body.light-theme .a3d-anzkv dt,body.light-theme .a3d-anzcap,body.light-theme .a3d-anzarean{color:#5f6770}
body.light-theme .a3d-anzkv dd,body.light-theme .a3d-anzsub,body.light-theme .a3d-anzareahd{color:#222}
body.light-theme .a3d-anzareav{color:#4b535c}
body.light-theme .a3d-anzsub,body.light-theme .a3d-anzarea{border-color:rgba(0,0,0,.09)}
body.light-theme .a3d-anzareaerr{color:#b42318}
""")

out = txt.encode('utf-8')
SRC.write_bytes(out)
print('patch_phase166d applied:', hashlib.sha256(out).hexdigest(), len(out))
