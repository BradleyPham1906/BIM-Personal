#!/usr/bin/env python3
"""V167d: Properties, Site, Standards -- the place, the date, each standard in force, overrides, packs.

- The place the standards follow: from the address search, or set by hand (a country, a region, a
  district, a city), with a warning when the site has moved away from where it was found.
- The date they are in force on (blank is today).
- Each standard the app applies, by area: the edition in force and how (in force here,
  international, applied outside its place, chosen, the app's assumption), the level its source was
  read at, its values with their sources; a value overridden with a reason, or reset; an edition
  chosen where there is more than one.
- The codes in force for the place that the app does not apply yet (the catalogue).
- Standards packs: load a file, see its SHA-256, its publisher and every difference before it
  applies; Apply or Cancel; remove one later.
- STANDARDS opens it.

Run from the repository root: python3 Phase/patch_phase167d.py
"""
import hashlib, pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
BASE = 'ddc459f6b12abed5fc7f506acb79a27b7befa254dae8fc86332460e2257e23ec'   # after patch_phase167c.py

raw = SRC.read_bytes()
sha = hashlib.sha256(raw).hexdigest()
if sha != BASE:
    sys.exit('BASE mismatch: %s (expected %s)' % (sha, BASE))
s = raw.decode('utf-8')
before = len(raw)


def rep(old, new, count=1):
    global s
    n = s.count(old)
    if n != count:
        sys.exit('expected %d of %r, found %d' % (count, old[:90], n))
    s = s.replace(old, new)


def js_ascii(t):
    return ''.join(c if ord(c) < 128 else '\\u%04x' % ord(c) for c in t)


UI = r'''  /* ================= __acad3dV167: Properties, Site, Standards ================= */
  var A3D_STD_UI={open:{},edit:null,place:false,pending:null};
  var BIM_STD_AREAS=['Transit and walking','Roads and noise','Cycling','Air','Flood and ground','Buildings','Structure','Site context','Climate'];
  function bimStdCap(t){t=String(t||'');return t.charAt(0).toUpperCase()+t.slice(1);}
  function bimStdBadge(E){
    var lv=E&&E.lv?E.lv:'U',how=E?E.how:'none';
    return '<span class="a3d-stdlv lv-'+bimEsc(lv)+'" title="'+bimEsc(BIM_STD_LV[lv]||'')+'">'+bimEsc(lv)+'</span>'+
      '<span class="a3d-stdhow h-'+bimEsc(how)+'">'+bimEsc((BIM_STD_HOW[how]||how)+(E&&E.at&&how==='adopted'?': '+E.at:''))+'</span>';
  }
  function bimStdSrcHtml(src){
    if(!src)return '';
    return '<div class="a3d-stdsrc">Source: '+bimEsc(src.t||'')+(src.w?'; '+bimEsc(src.w):'')+' ('+bimEsc(BIM_STD_LV[src.lv]||src.lv||'')+(src.read?', read '+bimEsc(src.read):'')+')'+
      (src.u?' <a href="'+bimEsc(src.u)+'" target="_blank" rel="noopener">open</a>':'')+'</div>';
  }
  /* a table, shortly: its rows, or its keys and values */
  function bimStdTableText(x){
    var v=x.v,out=[],k;
    if(Array.isArray(v))v.forEach(function(r){out.push(Array.isArray(r)?r.map(function(c){return c===null?'and over':String(c);}).join(' '):(r&&typeof r==='object'?JSON.stringify(r):String(r)));});
    else if(v&&typeof v==='object')for(k in v)if(v.hasOwnProperty(k))out.push(k+': '+(v[k]&&typeof v[k]==='object'?(v[k].name||JSON.stringify(v[k])):String(v[k])));
    var t=out.join('; ');
    return t.length>360?t.slice(0,357)+'...':t;
  }
  function bimStdValuesHtml(t){
    var r=bimStdResolve(t),e=r&&r.ed,h='';
    if(!e)return bimPropText('',r?r.why:'');
    if(r.how==='outside')h+=bimPropRow('','<span class="a3d-pstatic a3d-stdwarn">Applied outside its place ('+bimEsc(e.where||'its own place')+'): '+bimEsc(r.why)+'</span>');
    (e.v||[]).forEach(function(x){
      var key=t+'|'+x.n,o=bimStdOvOf(t,x.n),val;
      if(x.t)val='<span class="a3d-pstatic">'+bimEsc(bimStdTableText(x))+'</span> <span class="a3d-stdnote">a table: a pack changes it</span>';
      else if(A3D_STD_UI.edit===key)val='<div class="a3d-ukv a3d-stdov"><input type="number" step="any" data-propstd="ovv" value="'+bimEsc(String(o?o.v:x.v))+'" aria-label="'+bimEsc(x.say||x.n)+'">'+
        '<input type="text" data-propstd="ovwhy" value="'+bimEsc(o?o.why:'')+'" placeholder="Why: shown on every result that uses it" maxlength="200" aria-label="Why it is overridden">'+
        '<button type="button" class="a3d-pedit" data-propstdact="ovsave:'+bimEsc(key)+'">Save</button><button type="button" class="a3d-pedit" data-propstdact="ovcancel">Cancel</button></div>';
      else val='<span class="a3d-pstatic'+(o?' a3d-stdovd':'')+'" data-stdval="'+bimEsc(key)+'">'+bimEsc(bimStdFmt(o?o.v:x.v,x.u))+(o?' (overridden: '+o.why+'; the standard has '+bimStdFmt(x.v,x.u)+')':'')+'</span> '+
        (o?'<button type="button" class="a3d-pedit" data-propstdact="ovreset:'+bimEsc(key)+'">Reset</button>':'<button type="button" class="a3d-pedit" data-propstdact="ov:'+bimEsc(key)+'">Override</button>');
      h+=bimPropRow(bimStdCap(x.say||x.n),val+(x.src?'<div class="a3d-stdnote">'+bimEsc(x.src)+(x.lv?' ('+bimEsc(BIM_STD_LV[x.lv]||x.lv)+')':'')+'</div>':''));
    });
    h+=bimPropRow('',bimStdSrcHtml(e.src));
    return h;
  }
  function bimStdPropsHtml(){
    var r='',P=bimStdPlace(),U=A3D_STD_UI,S=bimStdS(),R=bimStdRecs(),areas={};
    r+=bimPropRow('Place','<span class="a3d-pstatic" data-stdplace="1">'+bimEsc(P?bimStdPlaceName(P)+' ('+[P.cc,P.r,P.d8||P.d6].filter(function(x){return !!x;}).join(', ').toUpperCase()+')':'Not set: each standard is applied as the app\'s default, and says so')+'</span> '+
      '<button type="button" class="a3d-pedit" data-propstdact="place">'+(P?'Change':'Set')+'</button>'+(P?' <button type="button" class="a3d-pedit" data-propstdact="placeclear">Clear</button>':''));
    if(P)r+=bimPropText('',(P.src==='search'?'From the address search, ':'Set by hand, ')+P.at);
    if(bimStdPlaceMoved())r+=bimPropRow('','<span class="a3d-pstatic a3d-uerr">The site has moved since its place was found: find the address again, or set the place</span>');
    if(U.place){
      var q=P||{};
      r+=bimPropRow('Country','<input type="text" data-propstd="cc" value="'+bimEsc((q.cc||'').toUpperCase())+'" placeholder="US, GB, DE" maxlength="2" aria-label="Country, two letters">');
      r+=bimPropRow('Region','<input type="text" data-propstd="r" value="'+bimEsc((q.r||'').toUpperCase())+'" placeholder="US-PA, GB-ENG (optional)" maxlength="6" aria-label="Region, ISO 3166-2">');
      r+=bimPropRow('District','<input type="text" data-propstd="d8" value="'+bimEsc((q.d8||q.d6||'').toUpperCase())+'" placeholder="GB-WSM (optional)" maxlength="6" aria-label="District, ISO 3166-2">');
      r+=bimPropRow('City','<input type="text" data-propstd="city" value="'+bimEsc(q.city||'')+'" placeholder="Philadelphia (optional)" maxlength="80" aria-label="City">');
      r+=bimPropRow('','<button type="button" class="a3d-pedit" data-propstdact="placesave">Save</button> <button type="button" class="a3d-pedit" data-propstdact="placecancel">Cancel</button>');
    }
    r+=bimPropRow('In force on','<input type="date" data-propstd="date" value="'+bimEsc(S.date||'')+'" aria-label="The date the standards are in force on; blank is today"> <span class="a3d-pstatic">'+(S.date?'':'today')+'</span>');
    R.filter(function(x){return !x.cat;}).forEach(function(x){(areas[x.area]||(areas[x.area]=[])).push(x);});
    BIM_STD_AREAS.concat(Object.keys(areas).filter(function(a){return BIM_STD_AREAS.indexOf(a)<0;})).forEach(function(a){
      if(!areas[a])return;
      r+='<div class="a3d-stdarea">'+bimEsc(a)+'</div>';
      areas[a].forEach(function(x){
        var E=bimStdEdition(x.id),open=!!U.open[x.id],pick='';
        if(x.eds.length>1){
          pick='<select data-propstd="pick:'+bimEsc(x.id)+'" aria-label="The edition of '+bimEsc(x.title)+'"><option value="">By place and date</option>'+
            x.eds.map(function(e){return '<option value="'+bimEsc(e.id)+'"'+((S.pick||{})[x.id]===e.id?' selected':'')+'>'+bimEsc(e.name)+'</option>';}).join('')+'</select>';
        }
        r+='<div class="a3d-prow a3d-stdrow" data-stdtopic="'+bimEsc(x.id)+'"><div class="a3d-plabel">'+bimEsc(x.title)+'</div><div class="a3d-pval">'+
          '<span class="a3d-pstatic">'+bimEsc(E&&E.name?E.name:'None in force')+(E&&E.ov.length?' ('+E.ov.length+' overridden)':'')+'</span> '+bimStdBadge(E)+
          ' <button type="button" class="a3d-pedit" data-propstdact="open:'+bimEsc(x.id)+'" aria-expanded="'+(open?'true':'false')+'">'+(open?'Hide':'Values')+'</button>'+
          (pick?'<div class="a3d-stdpick">'+pick+'</div>':'')+'<div class="a3d-stdnote">Used by: '+bimEsc(x.use||'')+'</div></div></div>';
        if(open)r+='<div class="a3d-stdvals" data-stdvals="'+bimEsc(x.id)+'">'+bimStdValuesHtml(x.id)+'</div>';
      });
    });
    /* the codes in force here that the app does not apply yet */
    var C=R.filter(function(x){return x.cat;}).map(function(x){return {x:x,E:bimStdEdition(x.id)};}).filter(function(c){return c.E&&c.E.id&&(c.E.how==='adopted'||c.E.how==='international');});
    r+='<div class="a3d-stdarea">In force here, not applied by the app yet</div>';
    if(!P)r+=bimPropText('','Set the place to list the codes in force there');
    else if(!C.length)r+=bimPropText('','None recorded for '+bimStdPlaceName(P));
    else C.forEach(function(c){
      r+='<div class="a3d-prow a3d-stdrow a3d-stdcat" data-stdcat="'+bimEsc(c.x.id)+'"><div class="a3d-plabel">'+bimEsc(c.x.title)+'</div><div class="a3d-pval"><span class="a3d-pstatic">'+bimEsc(c.E.name)+'</span> '+bimStdBadge(c.E)+
        '<div class="a3d-stdnote">'+bimEsc(c.x.pub+(c.x.access?'; '+c.x.access:''))+'</div>'+bimStdSrcHtml(c.E.src)+'</div></div>';
    });
    /* the project's packs, and one being looked at before it applies */
    r+='<div class="a3d-stdarea">Standards packs</div>';
    (S.packs||[]).forEach(function(p){
      r+=bimPropRow(p.name,'<span class="a3d-pstatic" title="SHA-256 '+bimEsc(p.sha)+'">'+bimEsc(p.pub+', unsigned; SHA-256 '+p.sha.slice(0,16)+'...; applied '+p.at)+'</span> <button type="button" class="a3d-pedit" data-propstdact="packremove:'+bimEsc(p.sha)+'">Remove</button>');
    });
    if(!(S.packs||[]).length&&!U.pending)r+=bimPropText('','None: the editions are the app\'s own');
    if(U.pending){
      var D=U.pending.diff;
      if(!D.ok)r+=bimPropRow('','<span class="a3d-pstatic a3d-uerr" data-stdpackerr="1">'+bimEsc(U.pending.file+': '+D.err)+'</span> <button type="button" class="a3d-pedit" data-propstdact="packcancel">Close</button>');
      else{
        r+='<div class="a3d-stdpack" data-stdpack="'+bimEsc(D.sha)+'">'+bimPropText('Pack',D.name+' ('+U.pending.file+')')+bimPropText('Publisher',D.pub+(D.date?', '+D.date:'')+'; unsigned: its origin is the file you chose')+
          bimPropRow('SHA-256','<span class="a3d-pstatic a3d-stdsha">'+bimEsc(D.sha)+'</span>');
        D.topics.forEach(function(t){
          var ch=t.changes.map(function(c){return (c.say||c.n)+': '+(c.from===null?'new':JSON.stringify(c.from))+' to '+JSON.stringify(c.to)+(c.u?' '+c.u:'');}).join('; ');
          r+=bimPropRow(t.title,'<span class="a3d-pstatic">'+bimEsc('Adds '+t.adds.join(', ')+'. '+(t.before===t.after?'The edition in force stays '+(t.after||'none')+'.':'The edition in force becomes '+(t.after||'none')+' ('+(BIM_STD_HOW[t.afterHow]||t.afterHow)+'), was '+(t.before||'none')+'.')+
            (ch?' Changes: '+ch+'.':'')+(t.applied?'':' Not applied by the app yet.'))+'</span>');
        });
        r+=bimPropRow('','<button type="button" class="a3d-pedit" data-propstdact="packapply">Apply</button> <button type="button" class="a3d-pedit" data-propstdact="packcancel">Cancel</button>')+'</div>';
      }
    }
    r+=bimPropRow('','<button type="button" class="a3d-pedit" data-propstdact="packload">Load a pack ...</button>');
    return r;
  }
  /* a pack file: read, looked at, nothing applied until Apply */
  function bimStdPackPick(){
    var inp=document.createElement('input');
    inp.type='file';inp.accept='.json,application/json';inp.style.display='none';
    inp.addEventListener('change',function(){
      var f=inp.files&&inp.files[0];
      if(inp.parentNode)inp.parentNode.removeChild(inp);
      if(!f)return;
      if(f.size>BIM_STD_PACK_MAX){a3dToast(f.name+' is larger than 1 MB: not a standards pack');return;}
      var rd=new FileReader();
      rd.onload=function(){try{bimStdPackLook(String(rd.result||''),f.name);}catch(eL){console.warn('[BIM] The pack could not be read',eL);a3dToast('The pack could not be read - see the console');}};
      rd.onerror=function(){console.warn('[BIM] The pack file could not be read',rd.error);a3dToast(f.name+' could not be read');};
      rd.readAsText(f);
    });
    document.body.appendChild(inp);
    inp.click();
  }
  function bimStdPackLook(text,file){
    A3D_STD_UI.pending={text:text,file:String(file||'pack.json').slice(0,120),diff:bimStdPackDiff(text)};
    bimPropReveal('Standards');refreshProps();
    var D=A3D_STD_UI.pending.diff;
    a3dToast(D.ok?'The pack '+D.name+': '+D.topics.length+' topic'+(D.topics.length===1?'':'s')+'; look at what it changes, then Apply or Cancel':'Not a pack the app can apply: '+D.err);
    return D;
  }
  function bimStdPropChange(ev){
    var f=ev.target&&ev.target.closest?ev.target.closest('[data-propstd]'):null;
    if(!f)return false;
    var k=f.getAttribute('data-propstd');
    if(k==='date')return bimStdSetDate(f.value);
    if(k.indexOf('pick:')===0)return bimStdPick(k.slice(5),f.value||null);
    return true;   /* the place's and an override's fields are read by Save */
  }
  function bimStdPropVal(k){var e=el.propsbody&&el.propsbody.querySelector('[data-propstd="'+k+'"]');return e?e.value:'';}
  function bimStdPropClick(ev){
    var bt=ev.target&&ev.target.closest?ev.target.closest('[data-propstdact]'):null;
    if(!bt)return false;
    var a=bt.getAttribute('data-propstdact'),i=a.indexOf(':'),c=i<0?a:a.slice(0,i),v=i<0?'':a.slice(i+1),U=A3D_STD_UI,j;
    if(c==='place'){U.place=true;refreshProps();return true;}
    if(c==='placecancel'){U.place=false;refreshProps();return true;}
    if(c==='placeclear'){U.place=false;bimStdSetPlace(null);return true;}
    if(c==='placesave'){
      var d=bimStdPropVal('d8'),cc=bimStdPropVal('cc');
      if(bimStdSetPlace({cc:cc,r:bimStdPropVal('r'),d8:d,city:bimStdPropVal('city'),ccn:'',rn:''},'hand'))U.place=false;
      refreshProps();return true;
    }
    if(c==='open'){U.open[v]=!U.open[v];if(!U.open[v]&&U.edit&&U.edit.indexOf(v+'|')===0)U.edit=null;refreshProps();return true;}
    if(c==='ov'){U.edit=v;refreshProps();var inp=el.propsbody&&el.propsbody.querySelector('[data-propstd="ovv"]');if(inp){try{inp.focus();}catch(eF){}}return true;}
    if(c==='ovcancel'){U.edit=null;refreshProps();return true;}
    if(c==='ovsave'){j=v.indexOf('|');if(bimStdOverride(v.slice(0,j),v.slice(j+1),bimStdPropVal('ovv'),bimStdPropVal('ovwhy')))U.edit=null;refreshProps();return true;}
    if(c==='ovreset'){j=v.indexOf('|');bimStdClear(v.slice(0,j),v.slice(j+1));return true;}
    if(c==='packload'){bimStdPackPick();return true;}
    if(c==='packcancel'){U.pending=null;refreshProps();return true;}
    if(c==='packapply'){var P=U.pending;if(P&&P.diff&&P.diff.ok){var D=bimStdPackApply(P.text);if(D&&D.ok)U.pending=null;}refreshProps();return true;}
    if(c==='packremove'){bimStdPackRemove(v);return true;}
    return false;
  }
  function bimStdCommand(){
    A3D.sel=null;A3D.sel2=null;A3D.selSet=[];
    bimPropReveal('Standards');
    refreshTree();refreshProps();paint();
    var g=el.propsbody&&el.propsbody.querySelector('[data-a3dpgrp="Standards"]');
    if(g){try{g.scrollIntoView({block:'start'});}catch(eS){}}
    var P=bimStdPlace();
    a3dToast('The standards are in Properties, Site: '+(P?'in force for '+bimStdPlaceName(P):'no place set, so each is applied as the app\'s default and says so'));
    return true;
  }
'''
rep("  /* ================= __acad3dV132: the map in Properties, the address, site data ================= */",
    js_ascii(UI) + "  /* ================= __acad3dV132: the map in Properties, the address, site data ================= */")

# the group, on the Site tab
rep("    h+=bimPTab('site',bimPropGroup('Data Layers',bimDataModelHtml()));   /* __acad3dV134 */",
    "    h+=bimPTab('site',bimPropGroup('Data Layers',bimDataModelHtml()));   /* __acad3dV134 */\n"
    "    h+=bimPTab('site',bimPropGroup('Standards',bimStdPropsHtml()));   /* __acad3dV167 */")
rep("    if(name==='Location'||name==='Map'||name==='Site Context'||name==='Data Layers')return 'site';",
    "    if(name==='Location'||name==='Map'||name==='Site Context'||name==='Data Layers'||name==='Standards')return 'site';   /* __acad3dV167: Standards */")

# its listeners, beside the data layers'
rep("    /* __acad3dV134: the Data Layers group and a data feature */\n",
    "    /* __acad3dV167: the Standards group */\n"
    "    if(el.propsbody)el.propsbody.addEventListener('change',function(ev){\n"
    "      try{bimStdPropChange(ev);}catch(eSC){console.warn('[BIM] Standards setting failed',eSC);a3dToast('That could not be changed - see the console');}\n"
    "    });\n"
    "    if(el.propsbody)el.propsbody.addEventListener('click',function(ev){\n"
    "      try{bimStdPropClick(ev);}catch(eSK){console.warn('[BIM] Standards action failed',eSK);a3dToast('That did not work - see the console');}\n"
    "    });\n"
    "    if(el.propsbody)el.propsbody.addEventListener('keydown',function(ev){\n"
    "      var f=ev.target&&ev.target.closest?ev.target.closest('[data-propstd=\"ovv\"],[data-propstd=\"ovwhy\"]'):null;\n"
    "      if(!f||ev.key!=='Enter'||!A3D_STD_UI.edit)return;\n"
    "      ev.preventDefault();ev.stopPropagation();\n"
    "      try{var j=A3D_STD_UI.edit.indexOf('|');if(bimStdOverride(A3D_STD_UI.edit.slice(0,j),A3D_STD_UI.edit.slice(j+1),bimStdPropVal('ovv'),bimStdPropVal('ovwhy')))A3D_STD_UI.edit=null;refreshProps();}\n"
    "      catch(eSE){console.warn('[BIM] The override could not be saved',eSE);a3dToast('The override could not be saved - see the console');}\n"
    "    });\n"
    "    /* __acad3dV134: the Data Layers group and a data feature */\n")

# the command
rep("    ['FINDADDRESS',['ADDRESS','GEOCODE'],'findaddress','Find an address on OpenStreetMap and put the site there: model 0,0'],",
    "    ['FINDADDRESS',['ADDRESS','GEOCODE'],'findaddress','Find an address on OpenStreetMap and put the site there: model 0,0'],\n"
    "    ['STANDARDS',['STANDARDSREGISTRY','CODES','STDS'],'standards','Standards: the editions in force for the site\\'s place and date, their sources, overrides with a reason, the codes in force there, and standards packs, in Properties, Site'],   /* __acad3dV167 */")
rep("    findaddress:function(){openFindAddressDlg();},",
    "    findaddress:function(){openFindAddressDlg();},\n"
    "    standards:function(){bimStdCommand();},                      /* __acad3dV167 */")

# the look of it
CSS = r'''  .a3d-pgbody .a3d-prow.a3d-stdrow,.a3d-pgbody .a3d-stdvals .a3d-prow{display:block;padding:4px 0}
  .a3d-pgbody .a3d-stdrow .a3d-plabel,.a3d-pgbody .a3d-stdvals .a3d-plabel{white-space:normal;overflow:visible;text-overflow:clip;margin-bottom:2px}
  .a3d-pgbody .a3d-stdrow .a3d-plabel{font-weight:600;color:inherit}
  .a3d-pgbody .a3d-stdrow .a3d-pval,.a3d-pgbody .a3d-stdvals .a3d-pval{text-align:left}
  .a3d-stdarea{font-size:11px;font-weight:600;letter-spacing:.02em;color:#8a96a3;margin:10px 0 2px;text-transform:uppercase}
  .a3d-stdlv{display:inline-block;min-width:16px;padding:0 4px;margin-left:4px;border-radius:3px;font-size:10px;font-weight:700;text-align:center;line-height:16px;background:#3a4450;color:#e6ebf0}
  .a3d-stdlv.lv-P{background:#1f6f4f;color:#fff}.a3d-stdlv.lv-S{background:#6b5a1e;color:#fff}.a3d-stdlv.lv-U{background:#7a2e2e;color:#fff}.a3d-stdlv.lv-A{background:#3d4a73;color:#fff}
  .a3d-stdhow{display:inline-block;margin-left:4px;font-size:10.5px;color:#9aa7b4}
  .a3d-stdhow.h-outside{color:#e0a64b}
  .a3d-stdwarn{color:#e0a64b}
  .a3d-stdovd{color:#e0a64b}
  .a3d-stdnote,.a3d-stdsrc{font-size:10.5px;line-height:1.4;color:#8a96a3;margin-top:2px;overflow-wrap:anywhere}
  .a3d-stdsrc a{color:#7fb2e5}
  .a3d-stdvals{margin:0 0 6px 10px;border-left:2px solid #3a4450;padding-left:6px}
  .a3d-stdpick select{max-width:100%;margin-top:3px}
  .a3d-stdov{flex-wrap:wrap;gap:4px}
  .a3d-stdov input[type=number]{width:90px}
  .a3d-stdov input[type=text]{flex:1 1 140px;min-width:0}
  .a3d-stdsha{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:10.5px;overflow-wrap:anywhere}
  .a3d-stdpack{border:1px solid #3a4450;border-radius:4px;padding:4px 6px;margin:4px 0}
  body.light-theme .a3d-stdhow,body.light-theme .a3d-stdnote,body.light-theme .a3d-stdsrc,body.light-theme .a3d-stdarea{color:#5f6b78}
  body.light-theme .a3d-stdhow.h-outside,body.light-theme .a3d-stdwarn,body.light-theme .a3d-stdovd{color:#9a5b00}
  body.light-theme .a3d-stdsrc a{color:#1f5fa8}
  body.light-theme .a3d-stdvals{border-left-color:#d4d9df}
  body.light-theme .a3d-stdpack{border-color:#d4d9df}
  @media (pointer:coarse){.a3d-stdov input[type=number],.a3d-stdov input[type=text]{min-height:36px;font-size:16px}}
'''
rep(".a3d-safstd{", js_ascii(CSS) + ".a3d-safstd{")

out = s.encode('utf-8')
na0 = sum(1 for c in raw.decode('utf-8') if ord(c) > 127)
na1 = sum(1 for c in s if ord(c) > 127)
if na1 > na0:
    sys.exit('the patch added %d non-ASCII characters' % (na1 - na0))
SRC.write_bytes(out)
print('bytes', before, '->', len(out))
print('sha256', hashlib.sha256(out).hexdigest())
