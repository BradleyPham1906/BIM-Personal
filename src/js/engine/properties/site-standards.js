  /* ================= __acad3dV167: Properties, Site, Standards ================= */
  var A3D_STD_UI={open:{},edit:null,place:false,pending:null,draft:{}};
  /* __acad3dV167g: what is typed in the place's and an override's fields, until Save or Cancel */
  var BIM_STD_DRAFT_KEYS={cc:1,r:1,d8:1,city:1,ovv:1,ovwhy:1};
  function bimStdDraft(k,d){var D=A3D_STD_UI.draft;return D&&D.hasOwnProperty(k)?D[k]:d;}
  function bimStdDraftClear(keys){keys.forEach(function(k){delete A3D_STD_UI.draft[k];});}
  var BIM_STD_LV_CLS={P:'lv-P',S:'lv-S',U:'lv-U',A:'lv-A'};   /* __acad3dV167i: written whole, so V114 sees them made */
  var BIM_STD_AREAS=['Transit and walking','Roads and noise','Cycling','Air','Flood and ground','Buildings','Structure','Site context','Land and green','Assets','Traffic','Climate'];   /* __acad3dV171: Traffic; __acad3dV168: Land and green; __acad3dV169: Assets */
  function bimStdCap(t){t=String(t||'');return t.charAt(0).toUpperCase()+t.slice(1);}
  function bimStdBadge(E){
    var lv=E&&E.lv?E.lv:'U',how=E?E.how:'none';
    return '<span class="a3d-stdlv '+(BIM_STD_LV_CLS[lv]||'')+'" title="'+bimEsc(BIM_STD_LV[lv]||'')+'">'+bimEsc(lv)+'</span>'+
      '<span class="a3d-stdhow'+(how==='outside'?' h-outside':'')+'">'+bimEsc((BIM_STD_HOW[how]||how)+(E&&E.at&&how==='adopted'?': '+E.at:''))+'</span>';
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
      else if(A3D_STD_UI.edit===key)val='<div class="a3d-ukv a3d-stdov"><input type="number" step="any" data-propstd="ovv" value="'+bimEsc(bimStdDraft('ovv',String(o?o.v:x.v)))+'" aria-label="'+bimEsc(x.say||x.n)+'">'+
        '<input type="text" data-propstd="ovwhy" value="'+bimEsc(bimStdDraft('ovwhy',o?o.why:''))+'" placeholder="Why: shown on every result that uses it" maxlength="200" aria-label="Why it is overridden">'+
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
      r+=bimPropRow('Country','<input type="text" data-propstd="cc" value="'+bimEsc(bimStdDraft('cc',(q.cc||'').toUpperCase()))+'" placeholder="US, GB, DE" maxlength="2" aria-label="Country, two letters">');
      r+=bimPropRow('Region','<input type="text" data-propstd="r" value="'+bimEsc(bimStdDraft('r',(q.r||'').toUpperCase()))+'" placeholder="US-PA, GB-ENG (optional)" maxlength="6" aria-label="Region, ISO 3166-2">');
      r+=bimPropRow('District','<input type="text" data-propstd="d8" value="'+bimEsc(bimStdDraft('d8',(q.d8||q.d6||'').toUpperCase()))+'" placeholder="GB-WSM (optional)" maxlength="6" aria-label="District, ISO 3166-2">');
      r+=bimPropRow('City','<input type="text" data-propstd="city" value="'+bimEsc(bimStdDraft('city',q.city||''))+'" placeholder="Philadelphia (optional)" maxlength="80" aria-label="City">');
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
    bimPropReveal('Standards');bimStdSheet();refreshProps();
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
    if(BIM_STD_DRAFT_KEYS[k])A3D_STD_UI.draft[k]=f.value;
    return true;   /* the place's and an override's fields are read by Save */
  }
  function bimStdPropVal(k){var e=el.propsbody&&el.propsbody.querySelector('[data-propstd="'+k+'"]');return e?e.value:'';}
  function bimStdPropClick(ev){
    var bt=ev.target&&ev.target.closest?ev.target.closest('[data-propstdact]'):null;
    if(!bt)return false;
    var a=bt.getAttribute('data-propstdact'),i=a.indexOf(':'),c=i<0?a:a.slice(0,i),v=i<0?'':a.slice(i+1),U=A3D_STD_UI,j;
    if(c==='place'){U.place=true;bimStdDraftClear(['cc','r','d8','city']);refreshProps();return true;}
    if(c==='placecancel'){U.place=false;bimStdDraftClear(['cc','r','d8','city']);refreshProps();return true;}
    if(c==='placeclear'){U.place=false;bimStdDraftClear(['cc','r','d8','city']);bimStdSetPlace(null);return true;}
    if(c==='placesave'){
      var d=bimStdPropVal('d8'),cc=bimStdPropVal('cc');
      if(bimStdSetPlace({cc:cc,r:bimStdPropVal('r'),d8:d,city:bimStdPropVal('city'),ccn:'',rn:''},'hand')){U.place=false;bimStdDraftClear(['cc','r','d8','city']);}
      refreshProps();return true;
    }
    if(c==='open'){U.open[v]=!U.open[v];if(!U.open[v]&&U.edit&&U.edit.indexOf(v+'|')===0){U.edit=null;bimStdDraftClear(['ovv','ovwhy']);}refreshProps();return true;}
    if(c==='ov'){U.edit=v;bimStdDraftClear(['ovv','ovwhy']);refreshProps();var inp=el.propsbody&&el.propsbody.querySelector('[data-propstd="ovv"]');if(inp){try{inp.focus();}catch(eF){}}return true;}
    if(c==='ovcancel'){U.edit=null;bimStdDraftClear(['ovv','ovwhy']);refreshProps();return true;}
    if(c==='ovsave'){j=v.indexOf('|');if(bimStdOverride(v.slice(0,j),v.slice(j+1),bimStdPropVal('ovv'),bimStdPropVal('ovwhy'))){U.edit=null;bimStdDraftClear(['ovv','ovwhy']);}refreshProps();return true;}
    if(c==='ovreset'){j=v.indexOf('|');bimStdClear(v.slice(0,j),v.slice(j+1));return true;}
    if(c==='packload'){bimStdPackPick();return true;}
    if(c==='packcancel'){U.pending=null;refreshProps();return true;}
    if(c==='packapply'){var P=U.pending;if(P&&P.diff&&P.diff.ok){var D=bimStdPackApply(P.text);if(D&&D.ok)U.pending=null;}refreshProps();return true;}
    if(c==='packremove'){bimStdPackRemove(v);return true;}
    return false;
  }
  function bimStdSheet(){if(bimShellOverlay()){var rp=document.getElementById('a3d-right');if(rp)rp.classList.add('open');}}   /* __acad3dV167g: V151's way */
  function bimStdCommand(){
    A3D.sel=null;A3D.sel2=null;A3D.selSet=[];
    bimPropReveal('Standards');bimStdSheet();
    refreshTree();refreshProps();paint();
    var g=el.propsbody&&el.propsbody.querySelector('[data-a3dpgrp="Standards"]');
    if(g){try{g.scrollIntoView({block:'start'});}catch(eS){}}
    var P=bimStdPlace();
    a3dToast('The standards are in Properties, Site: '+(P?'in force for '+bimStdPlaceName(P):'no place set, so each is applied as the app\'s default and says so'));
    return true;
  }
