"""patch_phase131b.py -- V131: usages and live areas, in Properties and the commands.

- A room, a floor or a mass has a Usage page: the usage (for every selected room, floor and mass at
  once), and what it comes to -- floors, GBA, GFA, NSA, and each of the usage's formulas.
- With nothing selected, Properties shows the project's Areas by Usage, and the Usages: each one's
  colour, name, ratios and floor-to-floor height, its parameters and formulas, a formula's error
  said where it is written; add, remove.
- USAGE (US) opens the selection's usage; USAGES the library. Both are on the ribbon (Room & Area,
  and a Program panel in Massing & Site), so the tools panel and the search list them."""
NAME = 'patch_phase131b.py'
BASE = 'ca912a9c7758c24fe0968e02ae0a832b8a834c6c3484ece16cfe63098ce2efb9'
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


UI = r"""  /* ================= __acad3dV131: usages in Properties ================= */
  var A3D_USAGE_OPEN=null;   /* the usage whose fields are open in the library, by id */
  function bimUsageSelTargets(){
    var ids=(A3D.selSet&&A3D.selSet.length)?A3D.selSet:(A3D.sel?[A3D.sel]:[]);
    return ids.filter(function(id){return !!bimUsageTarget(objById(id));});
  }
  function bimUsagePct(x){return String(Math.round(x*1000)/10)+'%';}
  function bimUsageNum(v){return String(Math.round(v*100)/100);}
  function bimUsageArea(v){return bimDispNum(v,2)+' m²';}
  function bimUsageSwatch(col){return '<span class="a3d-uswatch" style="background:'+bimEsc(col)+'"></span>';}
  /* the names a formula can read at its place in the usage, and the first it reads that it cannot */
  function bimUsageFormulaProblem(u,j){
    var f=u.formulas[j],pz=bimExprParse(f.expr),known={},k,bad=null;
    if(pz.error)return pz.error;
    for(k in BIM_EXPR_NAMES)if(BIM_EXPR_NAMES.hasOwnProperty(k))known[k]=1;
    (u.params||[]).forEach(function(p){known[String(p.key).toLowerCase()]=1;});
    for(k=0;k<j;k++)known[String(u.formulas[k].key).toLowerCase()]=1;
    (function walk(nd){
      if(bad||!nd)return;
      if(nd.v!==undefined&&!known[nd.v.toLowerCase()])bad='unknown name '+nd.v;
      if(nd.neg)walk(nd.neg);
      if(nd.a){walk(nd.a);walk(nd.b);}
      if(nd.args)nd.args.forEach(walk);
    })(pz.ast);
    return bad;
  }
  function bimUsageOptionsHtml(cur){
    var h='<option value=""'+(cur===''?' selected':'')+'>None</option>';
    bimUsages().forEach(function(u){h+='<option value="'+bimEsc(u.id)+'"'+(u.id===cur?' selected':'')+'>'+bimEsc(u.name)+'</option>';});
    if(cur==='__mixed')h+='<option value="__mixed" selected disabled>Mixed</option>';
    return h;
  }
  /* the Usage page of a room, a floor or a mass */
  function bimUsagePropsHtml(o){
    var tg=bimUsageSelTargets(),many=tg.length>1,u=o.usage?bimUsageById(o.usage):null,r='',k;
    var same=tg.every(function(id){var x=objById(id);return (x.usage||'')===(o.usage||'');});
    r+=bimPropRow(many?'Usage ('+tg.length+' selected)':'Usage',
      '<select data-propusage="set">'+bimUsageOptionsHtml(same?(o.usage||''):'__mixed')+'</select>');
    if(!many&&u){
      var m=bimUsageMeasure(o);
      if(m.kind==='mass')r+=bimPropText('Floors',m.levels+' at '+bimUsageNum(u.ftf)+' m, '+bimDispNum(m.height,2)+' m tall');
      if(m.kind!=='room'){
        r+=bimPropText('GBA',bimUsageArea(m.GBA));
        r+=bimPropText('GFA',bimUsageArea(m.GFA)+' ('+bimUsagePct(u.gfa)+' of GBA)');
      }
      r+=bimPropText('NSA',bimUsageArea(m.NSA)+(m.netMeasured?' (the room, measured)':' ('+bimUsagePct(u.nsa)+' of GFA)'));
      for(k in m.values)if(m.values.hasOwnProperty(k))r+=bimPropText(k,m.errors[k]?('error: '+m.errors[k]):bimUsageNum(m.values[k]));
    }
    var h=bimPropGroup('Usage',r);
    if(many)h+=bimUsageAreasHtml(tg,'Areas: the Selection');
    return h;
  }
  /* the areas by usage, as a Properties group */
  function bimUsageAreasHtml(ids,title){
    var s=bimUsageSummary(ids),r='';
    if(!s.rows.length)r+=bimPropText('None yet',ids?'nothing selected has a usage':'give a room, a floor or a mass a usage');
    s.rows.forEach(function(g){
      var k,v=[];
      for(k in g.values)if(g.values.hasOwnProperty(k))v.push(k+' '+bimUsageNum(g.values[k]));
      r+='<div class="a3d-prow ro a3d-uarea"><div class="a3d-plabel">'+bimUsageSwatch(g.color)+bimEsc(g.name)+'</div>'+
        '<div class="a3d-pval"><span class="a3d-pstatic">'+g.count+' · GBA '+bimDispNum(g.GBA,2)+' · GFA '+bimDispNum(g.GFA,2)+
        ' · NSA '+bimDispNum(g.NSA,2)+' m²'+(v.length?'<br>'+bimEsc(v.join(', ')):'')+(g.errors?'<br>'+g.errors+' formula error'+(g.errors===1?'':'s'):'')+'</span></div></div>';
    });
    if(s.rows.length>1)r+=bimPropText('Total','GBA '+bimDispNum(s.total.GBA,2)+' · GFA '+bimDispNum(s.total.GFA,2)+' · NSA '+bimDispNum(s.total.NSA,2)+' m²');
    return bimPropGroup(title,r);
  }
  /* the library: one line per usage, the open one's fields under it */
  function bimUsageLibraryHtml(){
    var L=bimUsages(),r='',i,j,u,id;
    for(i=0;i<L.length;i++){
      u=L[i];id=bimEsc(u.id);
      r+='<div class="a3d-prow a3d-uhead"><div class="a3d-plabel">'+bimUsageSwatch(u.color)+bimEsc(u.name)+'</div><div class="a3d-pval">'+
        '<span class="a3d-pstatic">GFA '+bimUsagePct(u.gfa)+' · NSA '+bimUsagePct(u.nsa)+' · '+bimUsageNum(u.ftf)+' m</span> '+
        '<button type="button" class="a3d-pedit" data-propusageact="open:'+id+'" aria-expanded="'+(A3D_USAGE_OPEN===u.id?'true':'false')+'">'+(A3D_USAGE_OPEN===u.id?'Done':'Edit')+'</button></div></div>';
      if(A3D_USAGE_OPEN!==u.id)continue;
      r+=bimPropRow('Name','<input type="color" data-propusage="u:'+id+':color" value="'+bimEsc(u.color)+'" aria-label="Colour"> '+
        '<input type="text" data-propusage="u:'+id+':name" value="'+bimEsc(u.name)+'" style="width:62%">');
      r+=bimPropRow('GBA → GFA (%)','<input type="number" step="any" min="0" max="100" data-propusage="u:'+id+':gfa" value="'+bimUsageNum(u.gfa*100)+'">');
      r+=bimPropRow('GFA → NSA (%)','<input type="number" step="any" min="0" max="100" data-propusage="u:'+id+':nsa" value="'+bimUsageNum(u.nsa*100)+'">');
      r+=bimPropRow('Floor to Floor (m)','<input type="number" step="any" min="1" max="20" data-propusage="u:'+id+':ftf" value="'+bimUsageNum(u.ftf)+'">');
      for(j=0;j<(u.params||[]).length;j++)
        r+=bimPropRow('Parameter','<div class="a3d-ukv"><input type="text" data-propusage="p:'+id+':'+j+':key" value="'+bimEsc(u.params[j].key)+'" aria-label="Name">'+
          '<span>=</span><input type="number" step="any" data-propusage="p:'+id+':'+j+':value" value="'+bimEsc(u.params[j].value)+'" aria-label="Value">'+
          '<button type="button" class="a3d-bdel" data-propusageact="pdel:'+id+':'+j+'" title="Remove this parameter">×</button></div>');
      for(j=0;j<(u.formulas||[]).length;j++){
        var fp=bimUsageFormulaProblem(u,j);
        r+=bimPropRow('Formula','<div class="a3d-ukv"><input type="text" data-propusage="f:'+id+':'+j+':key" value="'+bimEsc(u.formulas[j].key)+'" aria-label="Name"><span>=</span>'+
          '<button type="button" class="a3d-bdel" data-propusageact="fdel:'+id+':'+j+'" title="Remove this formula">×</button></div>'+
          '<input type="text" class="a3d-uexpr" data-propusage="f:'+id+':'+j+':expr" value="'+bimEsc(u.formulas[j].expr)+'" aria-label="Formula" spellcheck="false">'+
          (fp?'<div class="a3d-uerr" role="alert">'+bimEsc(fp)+'</div>':''));
      }
      r+=bimPropRow('','<button type="button" class="a3d-pedit" data-propusageact="padd:'+id+'">Add parameter</button> '+
        '<button type="button" class="a3d-pedit" data-propusageact="fadd:'+id+'">Add formula</button> '+
        '<button type="button" class="a3d-pedit" data-propusageact="udel:'+id+'">Remove usage</button>');
    }
    r+=bimPropRow('','<button type="button" class="a3d-pedit" data-propusageact="uadd">Add usage</button>');
    return r;
  }
  /* one change to one usage, one undo step; refused with its reason, nothing changed */
  function bimUsageEdit(id,fn){
    var L=bimUsages(),ix=-1,i;
    for(i=0;i<L.length;i++)if(L[i].id===id)ix=i;
    if(ix<0){a3dToast('That usage is gone');refreshProps();return false;}
    var c=JSON.parse(JSON.stringify(L[ix])),err=fn(c);
    if(err){a3dToast(err);refreshProps();return false;}
    pushUndo();
    bimUsages()[ix]=c;
    refreshTree();refreshProps();paint();saveSoon();
    return true;
  }
  function bimUsageUniqueKey(u,base){
    var n=1,k=base;
    while(bimUsageKeyProblem(u,k,null))k=base+(++n);
    return k;
  }
  function bimUsageAssign(ids,usageId){
    var u=usageId?bimUsageById(usageId):null,n=0;
    if(usageId&&!u){a3dToast('There is no such usage');return 0;}
    var objs=ids.map(objById).filter(function(o){return !!bimUsageTarget(o);});
    if(!objs.length){a3dToast('Select a room, a floor or a mass to give it a usage');return 0;}
    pushUndo();
    objs.forEach(function(o){if(u)o.usage=u.id;else delete o.usage;n++;});
    refreshTree();refreshProps();paint();saveSoon();
    a3dToast(u?(u.name+' given to '+n+' object'+(n===1?'':'s')):('Usage cleared on '+n+' object'+(n===1?'':'s')));
    return n;
  }
  function bimUsageAdd(name){
    var L=bimUsages(),base=String(name||'Usage').slice(0,40)||'Usage',nm=base,n=1,i;
    function taken(x){for(i=0;i<L.length;i++)if(L[i].name.toLowerCase()===x.toLowerCase())return true;return false;}
    while(taken(nm))nm=base+' '+(++n);
    pushUndo();
    var u={id:'use-'+Date.now().toString(36)+'-'+(A3D.seq++),name:nm,color:BIM_SCHEME_COLS[L.length%BIM_SCHEME_COLS.length],
      gfa:0.9,nsa:0.8,ftf:3.2,params:[],formulas:[]};
    L.push(u);
    A3D_USAGE_OPEN=u.id;
    refreshTree();refreshProps();saveSoon();
    return u.id;
  }
  function bimUsageRemove(id){
    var L=bimUsages(),ix=-1,i,n=0;
    for(i=0;i<L.length;i++)if(L[i].id===id)ix=i;
    if(ix<0)return false;
    pushUndo();
    var nm=L[ix].name;
    L.splice(ix,1);
    for(i=0;i<A3D.objs.length;i++)if(A3D.objs[i].usage===id){delete A3D.objs[i].usage;n++;}
    if(A3D_USAGE_OPEN===id)A3D_USAGE_OPEN=null;
    refreshTree();refreshProps();paint();saveSoon();
    a3dToast(nm+' removed'+(n?'; '+n+' object'+(n===1?' has':'s have')+' no usage now':''));
    return true;
  }
  function bimUsagePropChange(ev){
    var f=ev.target&&ev.target.closest?ev.target.closest('[data-propusage]'):null;
    if(!f)return false;
    var k=f.getAttribute('data-propusage'),v=f.value;
    if(k==='set'){if(v!=='__mixed')bimUsageAssign(bimUsageSelTargets(),v||null);return true;}
    var b=k.split(':'),kind=b[0],id=b[1];
    if(kind==='u')return bimUsageEdit(id,function(u){
      var fld=b[2],x;
      if(fld==='name'){
        x=String(v||'').replace(/\s+/g,' ').replace(/^ | $/g,'').slice(0,40);
        if(!x)return 'A usage needs a name';
        if(bimUsages().some(function(o){return o.id!==u.id&&o.name.toLowerCase()===x.toLowerCase();}))return 'There is already a usage called '+x;
        u.name=x;return;
      }
      if(fld==='color'){if(!/^#[0-9a-fA-F]{6}$/.test(v))return 'That is not a colour';u.color=v.toLowerCase();return;}
      x=parseFloat(v);
      if(!isFinite(x))return 'That must be a number';
      if(fld==='gfa'||fld==='nsa'){if(x<0||x>100)return 'A ratio is from 0 to 100%';u[fld]=x/100;return;}
      if(fld==='ftf'){if(x<1||x>20)return 'A floor-to-floor height is from 1 to 20 m';u.ftf=x;return;}
      return 'Unknown field';
    });
    var j=parseInt(b[2],10),part=b[3];
    if(kind==='p')return bimUsageEdit(id,function(u){
      var p=u.params[j];if(!p)return 'That parameter is gone';
      if(part==='key'){var e=bimUsageKeyProblem(u,v,p);if(e)return e;p.key=v;return;}
      var x=parseFloat(v);if(!isFinite(x))return 'A parameter is a number';p.value=x;
    });
    if(kind==='f')return bimUsageEdit(id,function(u){
      var fo=u.formulas[j];if(!fo)return 'That formula is gone';
      if(part==='key'){var e=bimUsageKeyProblem(u,v,fo);if(e)return e;fo.key=v;return;}
      fo.expr=String(v||'').slice(0,200);   /* kept even when it does not read yet: its error is shown */
    });
    return false;
  }
  function bimUsagePropClick(ev){
    var bt=ev.target&&ev.target.closest?ev.target.closest('[data-propusageact]'):null;
    if(!bt)return false;
    var a=bt.getAttribute('data-propusageact'),b=a.split(':'),id=b[1],j=parseInt(b[2],10);
    if(a==='uadd'){bimUsageAdd('Usage');a3dToast('Usage added: name it and set its ratios');return true;}
    if(b[0]==='open'){A3D_USAGE_OPEN=(A3D_USAGE_OPEN===id)?null:id;refreshProps();return true;}
    if(b[0]==='udel'){bimUsageRemove(id);return true;}
    if(b[0]==='padd')return bimUsageEdit(id,function(u){u.params=u.params||[];u.params.push({key:bimUsageUniqueKey(u,'rate'),value:0});});
    if(b[0]==='fadd')return bimUsageEdit(id,function(u){u.formulas=u.formulas||[];u.formulas.push({key:bimUsageUniqueKey(u,'value'),expr:'GFA'});});
    if(b[0]==='pdel')return bimUsageEdit(id,function(u){if(!u.params[j])return 'That parameter is gone';u.params.splice(j,1);});
    if(b[0]==='fdel')return bimUsageEdit(id,function(u){if(!u.formulas[j])return 'That formula is gone';u.formulas.splice(j,1);});
    return false;
  }
  /* USAGE: the selection's usage, in Properties; with nothing to give one to, the library */
  function bimUsageCommand(){
    var tg=bimUsageSelTargets();
    if(!tg.length){
      a3dToast('Select a room, a floor or a mass to give it a usage. The usages are below.');
      bimUsageLibraryCommand(true);
      return false;
    }
    A3D_PROP_GROUPS_OPEN['Usage']=true;
    refreshProps();
    var s=el.propsbody&&el.propsbody.querySelector('[data-propusage="set"]');
    if(s){try{s.focus();s.scrollIntoView({block:'nearest'});}catch(eF){}}
    return true;
  }
  /* USAGES: the library, with nothing selected */
  function bimUsageLibraryCommand(quiet){
    A3D.sel=null;A3D.sel2=null;A3D.selSet=[];
    A3D_PROP_GROUPS_OPEN['Usages']=true;
    refreshTree();refreshProps();paint();
    var g=el.propsbody&&el.propsbody.querySelector('[data-a3dpgrp="Usages"]');
    if(g){try{g.scrollIntoView({block:'start'});}catch(eS){}}
    if(!quiet)a3dToast('The usages are in Properties: Edit one to change its ratios, parameters and formulas');
    return true;
  }
"""

rep("""  /* __acad3dV73: the no-selection inspector. Project and Site are editable and write to the""",
    UI + """  /* __acad3dV73: the no-selection inspector. Project and Site are editable and write to the""")

# the model page: the areas, then the library
rep("""    h+=bimPropGroup('Statistics',srows);
    return h;""", """    h+=bimUsageAreasHtml(null,'Areas by Usage');   /* __acad3dV131 */
    h+=bimPropGroup('Usages',bimUsageLibraryHtml());
    h+=bimPropGroup('Statistics',srows);
    return h;""")
# an object's page
rep("""    if(bimIsAlignment(o))h+=bimAlignPropsHtml(o);       /* __acad3dV127 */""",
    """    if(bimIsAlignment(o))h+=bimAlignPropsHtml(o);       /* __acad3dV127 */
    if(bimUsageTarget(o))h+=bimUsagePropsHtml(o);       /* __acad3dV131 */""")
# its events
rep("""    /* __acad3dV127: the Alignment and Profile pages */""", """    /* __acad3dV131: the Usage page and the usages */
    if(el.propsbody)el.propsbody.addEventListener('change',function(ev){
      try{bimUsagePropChange(ev);}catch(eUC){console.warn('[BIM] Usage edit failed',eUC);a3dToast('That could not be changed - see the console');}
    });
    if(el.propsbody)el.propsbody.addEventListener('click',function(ev){
      try{bimUsagePropClick(ev);}catch(eUK){console.warn('[BIM] Usage edit failed',eUK);a3dToast('That could not be changed - see the console');}
    });
    /* __acad3dV127: the Alignment and Profile pages */""")

# ---- commands, ribbon, search
rep("""    ['INSERT',['I','DDINSERT'],'blockinsert',""", """    /* __acad3dV131: usages */
    ['USAGE',['US'],'usage','Give the selected rooms, floors or masses a usage (Residential, Office...); with none selected, the usages'],
    ['USAGES',['USES','PROGRAM'],'usages','The usages: each one\\'s colour, area ratios, floor-to-floor height, parameters and formulas'],
    ['INSERT',['I','DDINSERT'],'blockinsert',""")
rep("""    alignment:function(){bimAlignmentCommand();},""", """    alignment:function(){bimAlignmentCommand();},
    usage:function(){bimUsageCommand();},                        /* __acad3dV131 */
    usages:function(){bimUsageLibraryCommand();},""")
rep("""    if(act==='bim:alignment'){bimAlignmentCommand();return;}""", """    if(act==='bim:alignment'){bimAlignmentCommand();return;}
    if(act==='bim:usage'){bimUsageCommand();return;}                    /* __acad3dV131 */
    if(act==='bim:usages'){bimUsageLibraryCommand();return;}""")
rep("""'bim:alignment':'alignment','bim:roof'""", """'bim:alignment':'alignment','bim:usage':'usage','bim:usages':'usages','bim:roof'""")
rep("""'bim:truenorth':'True North','bim:alignment':'Alignment',""", """'bim:truenorth':'True North','bim:alignment':'Alignment','bim:usage':'Usage','bim:usages':'Usages',""")
rep("""      {t:'Room & Area',small:['bim:room','bim:tagroom','bim:tagallrooms']},""",
    """      {t:'Room & Area',small:['bim:room','bim:tagroom','bim:tagallrooms','bim:usage']},   /* __acad3dV131: Usage */""")
rep("""      {t:'Conceptual Mass',small:['box','cyl','sphere','cone','torus']},""",
    """      {t:'Conceptual Mass',small:['box','cyl','sphere','cone','torus']},
      {t:'Program',small:['bim:usage','bim:usages']},   /* __acad3dV131 */""")
rep("""ANALYZE:'structural frame solve stiffness forces moments deflection',""",
    """ANALYZE:'structural frame solve stiffness forces moments deflection',
    USAGE:'program use department gross floor area gfa gba nsa net saleable lettable yield efficiency residential office retail',   /* __acad3dV131 */
    USAGES:'program library gross net area ratios efficiency formulas parameters units',""")
rep("""    'bim:alignment':ric(""", """    'bim:usage':ric('<rect x="5" y="4" width="14" height="5" rx="1"/><rect x="5" y="10" width="14" height="5" rx="1"/><rect x="5" y="16" width="14" height="4" rx="1"/><path d="M8 6.5h4M8 12.5h7"/>'),   /* __acad3dV131 */
    'bim:usages':ric('<rect x="4" y="4" width="5" height="5" rx="1"/><path d="M12 6.5h8"/><rect x="4" y="10" width="5" height="5" rx="1"/><path d="M12 12.5h8"/><rect x="4" y="16" width="5" height="4" rx="1"/><path d="M12 18h8"/>'),
    'bim:alignment':ric(""")

# ---- styles
rep(""".a3d-rukeys [hidden]{display:none!important}""", """.a3d-rukeys [hidden]{display:none!important}
.a3d-uswatch{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:6px;vertical-align:-1px;border:1px solid rgba(0,0,0,.35);flex:0 0 auto}
.a3d-uhead .a3d-plabel{font-weight:600}
.a3d-uarea .a3d-pstatic{line-height:1.45}
.a3d-uerr{color:#ff9b8f;font-size:11px;margin-top:3px}
.a3d-ukv{display:flex;align-items:center;gap:4px}
.a3d-ukv input{flex:1 1 0;min-width:0;width:auto}
.a3d-ukv span{color:#8b949e}
.a3d-uexpr{display:block;width:100%;box-sizing:border-box;margin-top:4px;font-family:ui-monospace,Menlo,monospace}
body.light-theme .a3d-uerr{color:#b3261e}""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
