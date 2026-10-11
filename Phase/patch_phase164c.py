"""patch_phase164c.py -- V164: Analyze site, one button; what was typed by hand goes from Analyze.

The owner: "all i want is button then the analysis run, then it leverage appropriate relevant data
from target api to analyze the site, then put that under analysis layers, built straight in the
model that i can interact with", and of the checklist: "remove that entirely from our site
analysis". So:
  Analyze site  needs only the site's place (its latitude and longitude, or an address); fetches the
                context, the climate with its time zone, the access and people, and the zoning where
                a council layer is loaded; draws every analysis (164a, 164b); lists each source as it
                arrives or fails; one undo step. ANALYZESITE runs it from the command line.
  the cards     each analysis drawn in the model is a row in its category: shown or hidden, run
                again, selected, reset, with its legend and source
  removed       the stages, the project type and questions, typed findings and their editing, the
                photographs, the pins on the plan and the checklists, with their hooks and the pin
                tool. Findings are the ones the data writes, read only. What a project stored stays
                in its file, unread.
"""
import hashlib, pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
BASE = 'bdcfa85bcc4d73049d45476a097fd783c8ca505a4fac402781b598235986088f'   # after patch_phase164b.py

raw = SRC.read_bytes()
sha = hashlib.sha256(raw).hexdigest()
if sha != BASE:
    sys.exit('baseline sha mismatch: %s' % sha)
txt = raw.decode('utf-8')
assert 'function bimDgRunAll(only){' in txt, 'run patch_phase164b.py first'


def rep(old, new, count=1):
    global txt
    n = txt.count(old)
    assert n == count, 'anchor count %d (wanted %d): %r' % (n, count, old[:80])
    txt = txt.replace(old, new)


def cut(start, end, new):
    """from start (kept out) up to end (kept), each found once"""
    global txt
    assert txt.count(start) == 1, 'start count %d: %r' % (txt.count(start), start[:80])
    a = txt.index(start)
    assert txt.count(end, a) >= 1, 'no end after start: %r' % end[:80]
    b = txt.index(end, a)
    txt = txt[:a] + new + txt[b:]


RUN = r"""  /* ================= __acad3dV164: Analyze site =================
     The owner: "all i want is button then the analysis run, then it leverage appropriate relevant
     data from target api to analyze the site, then put that under analysis layers". One button,
     needing only the site's place -- its latitude and longitude, or an address found on the map. It
     fetches what the place lets the app fetch, each from its free source: the context (OpenStreetMap,
     AWS Terrain Tiles), and after it the access and people (OpenStreetMap, the US Census), so the
     public Overpass servers are asked one thing at a time; the climate (Open-Meteo, CAMS, USGS) beside
     them, with the time zone; the zoning where a council's layer is loaded. Then every analysis is
     drawn. Each source is listed as it arrives, or with its reason when it fails, and what failed
     leaves the rest standing. One undo step: the snapshot taken as it starts -- or, when the address
     is found first, the one placing the site takes -- and every step after it held. An address not
     found leaves none. */
  var A3D_SITERUN={busy:false,steps:[]};
  var BIM_SITERUN_RADIUS=300;   /* far enough for the noise (CRTN holds to 300 m) and the views */
  var BIM_SITERUN_STEPS=[['place','The site'],['context','Context'],['climate','Climate and time zone'],['access','Access and people'],['zoning','Zoning'],['draw','The analyses, in the model']];
  var BIM_SITERUN_WORD={wait:'Waiting',busy:'Running',ok:'Done',part:'Partly',fail:'Failed',skip:'Skipped'};
  var BIM_SITERUN_CLS={wait:'s-wait',busy:'s-busy',ok:'s-ok',part:'s-part',fail:'s-fail',skip:'s-skip'};
  function bimSiteStep(id,state,text){
    var s=A3D_SITERUN.steps,i;
    for(i=0;i<s.length;i++)if(s[i].id===id){s[i].state=state;s[i].text=String(text==null?'':text).slice(0,400);}
    bimAnalyzeRefresh(true);
  }
  /* why a fetch would not start: it says so in the message it shows */
  function bimSiteToastText(){var t=document.getElementById('a3d-toast'),L=t?String(t.textContent||'').split('\n'):[];return L.length?L[L.length-1]:'';}
  function bimSitePlaceText(){
    var st=bimSunSettings(),at=Math.abs(st.lat).toFixed(5)+'° '+(st.lat<0?'S':'N')+', '+Math.abs(st.lon).toFixed(5)+'° '+(st.lon<0?'W':'E');
    return A3D.site&&A3D.site.address?String(A3D.site.address).slice(0,140)+' ('+at+')':at;
  }
  function bimSiteAddrFocus(){
    bimAnzView();
    var i=document.querySelector('.a3d-analyze-wrap [data-saaddr]');
    if(i){try{i.focus();}catch(eF){}}
  }
  function bimSiteAnalyze(q){
    if(A3D_SITERUN.busy){a3dToast('Analyze site is already running');return null;}
    var st=bimSunSettings(),placed=bimSunNum(st.lat)&&bimSunNum(st.lon),R;
    q=String(q==null?'':q).replace(/^\s+|\s+$/g,'');
    if(!placed&&!q){a3dToast('Where is the site? Type its address, or give its latitude and longitude in Properties, Site, Location');bimSiteAddrFocus();return null;}
    if(typeof fetch!=='function'){a3dToast('This browser cannot fetch: Analyze site gets its data from the web');return null;}
    R=A3D_SITERUN={busy:true,t0:Date.now(),held:false,steps:BIM_SITERUN_STEPS.map(function(s){return {id:s[0],name:s[1],state:'wait',text:''};})};
    function hold(){if(!R.held){R.held=true;bimUndoHold=true;}}
    if(placed){pushUndo();hold();}
    function finish(ok){
      if(R.held)bimUndoHold=false;
      R.busy=false;
      var D=bimDgState();
      D.last={date:bimSaToday(),ok:!!ok,steps:R.steps.map(function(s){return {id:s.id,name:s.name,state:s.state,text:s.text};})};
      refreshTree();refreshLayers();refreshProps();paint();saveSoon();
      bimAnalyzeRefresh(true);
      return {ok:!!ok,steps:D.last.steps};
    }
    bimSiteStep('place','busy',placed?'':'Finding '+q+' ...');
    var p0=placed?Promise.resolve({found:true}):(bimMapFind(q)||Promise.resolve({found:false,error:bimSiteToastText()}));
    return p0.then(function(f){
      if(!f||!f.found){
        bimSiteStep('place','fail',f&&f.error?f.error:'Nothing found for '+q+': try the street and the town, or give the latitude and longitude in Location');
        a3dToast('Analyze site: the site could not be found');
        return finish(false);
      }
      hold();   /* placing the site took the snapshot */
      bimSiteStep('place','ok',bimSitePlaceText());
      var cs=bimCtxSettings(),wid='';
      if(cs.radius<BIM_SITERUN_RADIUS){A3D.site.context=A3D.site.context||{};A3D.site.context.radius=BIM_SITERUN_RADIUS;wid='; the context radius is '+BIM_SITERUN_RADIUS+' m now (it was '+cs.radius+' m), for the noise and the views';}
      bimSiteStep('context','busy','Buildings, roads, water, green, trees, land use and terrain, '+Math.max(cs.radius,BIM_SITERUN_RADIUS)+' m around ...');
      bimSiteStep('climate','busy','Ten years of days, a year of hours, air quality, earthquakes ...');
      var pk=bimSiteOne('climate',bimClimFetch(),function(r){
        var got=[];
        if(r.climate)got.push('ten years of climate');if(r.hourly)got.push('a year of hourly wind and heat');if(r.air)got.push('air quality');
        if(r.quakes!==null&&r.quakes!==undefined)got.push(bimSaN(r.quakes,'earthquake')+' within 100 km');
        if(r.tz!==null&&r.tz!==undefined)got.push('UTC'+(r.tz>=0?'+':'−')+bimDispNum(Math.abs(r.tz),2)+(r.tzSet?'':' (the offset already given is kept)'));
        return [bimSiteState(got.length,r.errors),got.join(', ')+(r.errors&&r.errors.length?'. Not available: '+r.errors.join('; '):'')];
      });
      var pc=bimSiteOne('context',bimCtxFetch(),function(r){
        return [bimSiteState(r.counts?1:0,r.errors),r.counts?bimCtxCountsText(r.counts)+wid+(r.errors&&r.errors.length?'. Not available: '+r.errors.join('; '):''):'nothing came back'];
      }).then(function(){
        bimSiteStep('access','busy','Walk times to daily needs and transit, the streets, the census tract ...');
        return bimSiteOne('access',bimAccFetch(),function(r){
          var got=[];
          if(r.access)got.push('walk times, '+bimSaN(r.stops||0,'transit stop'));if(r.people)got.push('the census tract');if(r.outside)got.push('the census covers US sites only');
          return [bimSiteState(got.length,r.errors),got.join(', ')+(r.errors&&r.errors.length?'. Not available: '+r.errors.join('; '):'')];
        });
      });
      return Promise.all([pc,pk]).then(function(){
        bimSiteZoning();
        bimSiteStep('draw','busy','');
        var out=bimDgRunAll(),said=[],notes=[],n=0,bad;
        BIM_DG_AN.forEach(function(A){var r=out[A.id];if(!r)return;if(r.error)notes.push(A.name+': '+r.error);else if(r.total){n+=r.total;said.push(A.name.toLowerCase()+' '+r.total);}else if(r.note)notes.push(A.name+': '+r.note);});
        bimSaFill(true);
        bimSiteStep('draw',n?'ok':'fail',(n?bimSaN(n,'element')+' on Layers, Site analysis: '+said.join(', '):'Nothing to draw')+(notes.length?'. '+notes.join('. '):''));
        bad=R.steps.filter(function(s){return s.state==='fail';}).map(function(s){return s.name;});
        var res=finish(true);
        a3dToast('Analyze site: '+(n?bimSaN(n,'element')+' drawn in the model, on Layers, Site analysis':'nothing could be drawn')+'; one undo step'+(bad.length?'. Not available: '+bad.join(', '):''));
        return res;
      });
    }).then(null,function(e){
      console.warn('[BIM] Analyze site',e);
      a3dToast('Analyze site stopped - see the console');
      R.steps.forEach(function(s){if(s.state==='busy'||s.state==='wait'){s.state='fail';s.text='Stopped: '+String(e&&e.message||e).slice(0,160);}});
      return finish(false);
    });
  }
  /* what came back: all of it, part of it (some sources down, named), or none */
  function bimSiteState(got,errors){return !got?'fail':(errors&&errors.length?'part':'ok');}
  /* one fetch, its step marked by what came back; a fetch that would not start says why */
  function bimSiteOne(id,p,read){
    if(!p){bimSiteStep(id,'fail',bimSiteToastText()||'It did not start');return Promise.resolve(null);}
    return p.then(function(r){
      var v;
      try{v=r&&!r.error?read(r):['fail',(r&&r.error)||'nothing came back'];}
      catch(eR){console.warn('[BIM] Analyze site: '+id,eR);v=['fail','It could not be read - see the console'];}
      bimSiteStep(id,v[0],v[1]);
      return r;
    },function(e){bimSiteStep(id,'fail',String(e&&e.message||e).slice(0,200));return null;});
  }
  /* the zoning, where a council's layer loaded in Data Layers covers the property */
  function bimSiteZoning(){
    var DL=bimDataList(),f=null;
    if(!bimZnProperty()){bimSiteStep('zoning','skip','Needs the property line: draw it from a shape or from its bearings');return;}
    if(!DL.length){bimSiteStep('zoning','skip','No council layer loaded: add one in Properties, Site, Data Layers, and its zoning is read here');return;}
    try{f=bimZnFromLayer(false);}catch(eZ){console.warn('[BIM] Analyze site: zoning',eZ);}
    if(!f){bimSiteStep('zoning','skip','None of the '+bimSaN(DL.length,'loaded layer')+' gives the zoning at the property');return;}
    try{bimZnFromLayer(true);}catch(eZ2){console.warn('[BIM] Analyze site: zoning',eZ2);bimSiteStep('zoning','fail','It could not be read - see the console');return;}
    bimSiteStep('zoning','ok',bimZnFoundText(f)+' (from '+(f.district||f.far||f.height).layer+')');
  }
  /* the top of Analyze: where the site is, the button, and what the last run brought */
  function bimSiteRunHtml(){
    var st=bimSunSettings(),placed=bimSunNum(st.lat)&&bimSunNum(st.lon),D=bimDgState(),R=A3D_SITERUN,P=A3D.objs.filter(bimIsProperty),bd,h,steps;
    if(P.length){var g=bimPropertyGeometry(P[0]);bd=bimEsc(P[0].name)+', '+bimDispNum(g.area,1)+' m²';}
    else bd='None yet <button type="button" class="a3d-anzbtn" data-saact="cmd:propertyshape">From a shape</button> <button type="button" class="a3d-anzbtn" data-saact="cmd:propertyline">From bearings</button>';
    h='<div class="a3d-sasec a3d-sarun" data-anzsec="site"><div class="a3d-sasechd">Site</div>'+
      '<div class="a3d-sarow"><span class="a3d-salab">Place</span><span class="a3d-saval">'+(placed?bimEsc(bimSitePlaceText()):'Not placed yet')+'</span></div>';
    if(!placed)h+='<div class="a3d-sarow"><label for="a3d-saaddr">Address</label><input type="text" id="a3d-saaddr" data-saaddr="1" maxlength="200" enterkeyhint="search" autocomplete="off" placeholder="A street address or a place"></div>';
    h+='<div class="a3d-sarow"><span class="a3d-salab">Boundary</span><span class="a3d-saval">'+bd+'</span></div>'+
      '<div class="a3d-saacts"><button type="button" class="a3d-anzbtn pri a3d-sago" data-saact="analyze"'+(R.busy?' disabled':'')+'>'+(R.busy?'Analyzing ...':(D.last?'Analyze site again':'Analyze site'))+'</button>'+
      (D.last?'<button type="button" class="a3d-anzbtn" data-saact="dglegend" aria-pressed="'+(!D.legendOff)+'">'+(D.legendOff?'Show the legend':'Hide the legend')+'</button>':'')+'</div>'+
      '<div class="a3d-sacap">'+(D.last&&!R.busy?bimEsc('Last run '+D.last.date+'. Each analysis is on Layers, Site analysis: select an element to move, restyle or relabel it; what you change is kept when it runs again.'):
        'Gets what is around the site from free open data -- buildings, roads, terrain, climate, access, zoning -- and draws each analysis in the model, on Layers, Site analysis. One undo step.')+'</div>';
    steps=R.steps.length?R.steps:((D.last&&D.last.steps)||[]);
    if(steps.length)h+='<ol class="a3d-sasteps" data-sasteps="1">'+steps.map(function(s){
      return '<li class="a3d-sastep '+(BIM_SITERUN_CLS[s.state]||'s-wait')+'" data-sastep="'+bimEsc(s.id)+'"><span class="a3d-sastepic" aria-hidden="true"></span><span class="a3d-sastepn">'+bimEsc(s.name)+'</span>'+
        '<span class="a3d-sastepst">'+bimEsc(BIM_SITERUN_WORD[s.state]||s.state)+'</span>'+(s.text?'<span class="a3d-sastept">'+bimEsc(s.text)+'</span>':'')+'</li>';}).join('')+'</ol>';
    return h+'</div>';
  }
  /* ---- each analysis drawn in the model, a row in its category ---- */
  var BIM_DG_KEYCLS={fill:'k-fill',line:'k-line',dash:'k-dash',dot:'k-dot'};
  function bimDgLegendHtml(rows){
    if(!rows||!rows.length)return '';
    return '<div class="a3d-dgleg">'+rows.map(function(r){
      var st=(r.kind==='line'||r.kind==='dash')?'color:'+r.col:'background:'+r.col;
      return '<span class="a3d-dglegi"><i class="'+(BIM_DG_KEYCLS[r.kind]||'k-fill')+'" style="'+bimEsc(st)+'"></i>'+bimEsc(r.name)+'</span>';}).join('')+'</div>';
  }
  function bimDgCards(){
    var D=bimDgState();
    return BIM_DG_AN.map(function(A){
      var R=D.runs[A.id],L=bimDgDiags(A.id),ly=bimLayerById(D.layers[A.id]),on=!!(ly&&bimLayerEff(ly).on),ed=L.filter(bimDgEdited).length;
      var st=!R?'Not run yet: Analyze site draws it':(L.length?bimSaN(L.length,'element')+' on Site analysis - '+A.name+(ed?', '+ed+' changed by you':'')+', '+R.date:(R.note||'Nothing to draw'));
      return {id:'dg'+A.id,title:A.name,state:!R?null:(L.length?(on?'on':'off'):'warn'),status:st,
        extra:R?bimDgLegendHtml(R.legend)+(R.note&&L.length?'<div class="a3d-sacap">'+bimEsc(R.note)+'</div>':'')+(R.source?'<div class="a3d-sacap">Source: '+bimEsc(R.source)+'</div>':''):'',
        acts:[{act:'dg:show:'+A.id,label:on?'Hide':'Show',pri:!on&&L.length>0,off:L.length?'':'Nothing drawn yet'},
          {act:'dg:run:'+A.id,label:R?'Run again':'Run',tip:'From what the project holds now; Analyze site fetches the data again'},
          {act:'dg:select:'+A.id,label:'Select',off:L.length?'':'Nothing drawn yet'},
          {act:'dg:reset:'+A.id,label:'Reset',off:R?'':'Not run yet',tip:'As the analysis draws it: what you changed, copied or deleted on it goes back'}]};
    });
  }
  function bimDgAct(v){
    v=String(v||'');
    var i=v.indexOf(':'),c=v.slice(0,i),a=v.slice(i+1),D=bimDgState(),L,ly;
    if(i<0||!bimDgAn(a))return false;
    if(c==='run')return !!bimDgRunAll(a);
    if(c==='reset')return !!bimDgResetAnalysis(a);
    L=bimDgDiags(a);
    if(c==='select'){
      if(!L.length)return false;
      A3D.selSet=L.map(function(o){return o.id;});A3D.sel=A3D.selSet[0];A3D.sel2=null;
      refreshTree();refreshProps();paint();
      return true;
    }
    if(c==='show'){
      ly=bimLayerById(D.layers[a]);
      if(!ly)return false;
      if(bimLayerEff(ly).on)bimLayerSet(ly.id,'visible',false);
      else bimLayerChain(ly).forEach(function(x){if(x.visible===false)bimLayerSet(x.id,'visible',true);});   /* the layer and those above it */
      paint();
      return true;
    }
    return false;
  }
"""

# Analyze site, after the engine and the analyses, before the site analysis record
rep("  /* ================= __acad3dV158: Site analysis SA1, the workspace and the standard =================\n",
    RUN + "  /* ================= __acad3dV158: Site analysis SA1, the workspace and the standard =================\n")

# ---- the top of Analyze: the site and the button, where the stages and Define were ----
cut("  /* __acad3dV162: under the search, in the order the work goes: the stages, red flags, Define, the\n",
    "  function bimAnalyzeHtml(){\n",
    """  /* __acad3dV162: under the search, in the order the work goes. __acad3dV164: the site and Analyze
     site first, where the stages and Define were; then the red flags, the ten categories with their
     analyses, data and findings, and the model */
  function bimAnzBodyHtml(C){
    var F=bimSaShown(),R=F.filter(function(f){return f.cls==='redflag';}),h=bimSiteRunHtml();
    if(R.length)h+='<div class="a3d-saflags" data-anzsec="flags"><div class="a3d-sasechd">Red flags first</div>'+R.map(function(f){return '<div class="a3d-saflag">'+bimSaNumber(f)+' '+bimEsc(f.title)+(f.value?': '+bimEsc(f.value):'')+'</div>';}).join('')+'</div>';
    h+='<div class="a3d-sasec" data-anzsec="cats"><div class="a3d-sasechd">The ten categories</div><div class="a3d-anzlist">'+BIM_SA_CATS.map(function(c,i){return bimSaCatHtml(c,i,C);}).join('')+'</div></div>';
    var M=BIM_ANZ_MODEL.map(function(id){return C.filter(function(c){return c.id===id;})[0];}).filter(function(c){return !!c;});
    h+='<div class="a3d-sasec a3d-anzgrp" data-anzgrp="model"><div class="a3d-sasechd a3d-anzgrphd">Model</div><div class="a3d-sacap">What the model itself shows; no site data needed.</div>'+
      '<div class="a3d-anzlist">'+M.map(bimAnzCard).join('')+'</div></div>';
    return h+'<div class="a3d-anzempty" hidden>Nothing matches</div>';
  }
""")
rep("    var n=C.filter(function(c){return c.state==='on'||c.state==='stale'||c.state==='busy';}).length,F=bimSa().findings,r=0;\n",
    "    var n=C.filter(function(c){return c.state==='on'||c.state==='stale'||c.state==='busy';}).length,F=bimSaShown(),r=0;\n")
# a search: the site and its button stay; the red flags show when they match
rep("""    S=root.querySelectorAll('[data-anzsec="stages"],[data-anzsec="flags"],[data-anzsec="define"]');
    for(i=0;i<S.length;i++){
      on=!q||(S[i].getAttribute('data-anzsec')!=='stages'&&bimAnzWordsHit(q,bimAnzText(S[i])));
      show(S[i],on);if(q&&on)n++;
    }
""", """    S=root.querySelectorAll('[data-anzsec="flags"]');
    for(i=0;i<S.length;i++){
      on=!q||bimAnzWordsHit(q,bimAnzText(S[i]));
      show(S[i],on);if(q&&on)n++;
    }
""")
rep("bimAnzTexts(K[i],'.a3d-saq,.a3d-clsec,.a3d-salink,.a3d-safind,.a3d-sachk')",
    "bimAnzTexts(K[i],'.a3d-saq,.a3d-clsec,.a3d-salink,.a3d-safind')")

# ---- the analyses' rows, in their categories, first ----
rep("  var BIM_ANZ_GROUP_OF={survey:'landform',terrain:'landform',grading:'landform',rain:'water',sun:'climate',sunhours:'climate',solar:'climate'};\n",
    "  var BIM_ANZ_GROUP_OF={survey:'landform',terrain:'landform',grading:'landform',rain:'water',sun:'climate',sunhours:'climate',solar:'climate',\n"
    "    dgframe:'location',dgsun:'climate',dgshadow:'climate',dgwind:'climate',dgviews:'people',dgnoise:'risk'};   /* __acad3dV164: the analyses in the model */\n")
rep("    C.forEach(function(c){c.group=BIM_ANZ_GROUP_OF[c.id]||'model';});   /* __acad3dV148 */\n    return C;\n",
    "    C=bimDgCards().concat(C);   /* __acad3dV164: what Analyze site draws, first in its category */\n"
    "    C.forEach(function(c){c.group=BIM_ANZ_GROUP_OF[c.id]||'model';});   /* __acad3dV148 */\n    return C;\n")
rep("    else if(k.indexOf('layer:')===0)bimResultLayerAdd(k.slice(6));   /* __acad3dV148 */\n    else return false;\n",
    "    else if(k.indexOf('layer:')===0)bimResultLayerAdd(k.slice(6));   /* __acad3dV148 */\n"
    "    else if(k.indexOf('dg:')===0)bimDgAct(k.slice(3));   /* __acad3dV164 */\n    else return false;\n")

# ---- the record: no stages, no project type or questions, no checklists ----
cut("  /* ================= __acad3dV158: Site analysis SA1, the workspace and the standard =================\n",
    "  var BIM_SA_CATS=[\n",
    """  /* ================= __acad3dV158: Site analysis SA1, the workspace and the standard =================
     The standard is reference/research-site-analysis-process.md: ten fixed categories, and findings
     that each name a source, a date and how sure they are, classed as a constraint, an opportunity,
     a red flag or a fact. Kept with the project in A3D.site.analysis. __acad3dV164: the findings are
     the ones the data writes; the stages, the questions, typed findings, photographs, pins and
     checklists are gone from it, and what a project stored of them stays in its file, unread. */
""")
cut("    {id:'location',n:'Location and context',q:'Where it is, what surrounds it, figure-ground, land use.',\n",
    "  var BIM_SA_CLS=",
    """    {id:'location',n:'Location and context',q:'Where it is, what surrounds it, figure-ground, land use.'},
    {id:'legal',n:'Legal and regulatory',q:'Zoning, permitted uses, FAR, height, setbacks, coverage, parking, easements, ownership, heritage.'},
    {id:'landform',n:'Landform',q:'Topography, slope, aspect, relief, geology, soils.'},
    {id:'water',n:'Water',q:'Drainage, flood zones, water bodies, runoff.'},
    {id:'climate',n:'Climate',q:'Temperature, rain, climate zone, sun path, shadows, wind, solar.'},
    {id:'ecology',n:'Ecology',q:'Vegetation, trees, habitat, protected areas.'},
    {id:'risk',n:'Environmental risk',q:'Seismic, contamination, air quality, noise, wildfire.'},
    {id:'access',n:'Access and circulation',q:'Street hierarchy, street use, transit, walking and cycling, parking, entries.'},
    {id:'utilities',n:'Utilities',q:'Water, sewer, power, stormwater, telecoms.'},
    {id:'people',n:'People and place',q:'Demographics, amenities within a walk, history, views, landmarks, noise sources.'}];
""")
rep("  var BIM_SA_TYPES=['','Residential','Commercial','Mixed use','Industrial','Institutional','Public realm and landscape','Infrastructure','Other'];\n", "")
rep("  var BIM_SA_COL={neutral:'#8b949e',opportunity:'#30a46c',constraint:'#f5a524',redflag:'#e5484d'};\n  var BIM_SA_PHOTO_PX=960;\n", "")
rep("  var A3D_SA={edit:null,open:", "  var A3D_SA={open:")
rep("""    if(!(s.stage>=0&&s.stage<BIM_SA_STAGES.length))s.stage=0;
    if(typeof s.ptype!=='string')s.ptype='';
    if(typeof s.questions!=='string')s.questions='';
    if(!Array.isArray(s.findings))s.findings=[];
    if(!s.checks||typeof s.checks!=='object')s.checks={};
    if(!(s.seq>=0))s.seq=0;
    if(s.pins===undefined)s.pins=true;
    return s;
  }
""", """    if(!Array.isArray(s.findings))s.findings=[];
    if(!(s.seq>=0))s.seq=0;
    return s;
  }
  /* __acad3dV164: the findings shown -- those the data writes; one typed by hand before stays unread */
  function bimSaShown(){return bimSa().findings.filter(function(f){return !!f.auto;});}
""")
rep("""    var F=bimSa().findings,ci=-1,k=0,i;
    for(i=0;i<BIM_SA_CATS.length;i++)if(BIM_SA_CATS[i].id===f.cat)ci=i;""",
    """    var F=bimSaShown(),ci=-1,k=0,i;
    for(i=0;i<BIM_SA_CATS.length;i++)if(BIM_SA_CATS[i].id===f.cat)ci=i;""")
rep("  function bimSaOf(cat){return bimSa().findings.filter(function(f){return f.cat===cat;});}\n",
    "  function bimSaOf(cat){return bimSaShown().filter(function(f){return f.cat===cat;});}\n")
cut("  /* the highest confidence any of a category's findings has */\n", "  function bimSaNew(cat,f){\n", "")
rep("    if(s.stage<1)s.stage=1;\n    bimSaDone();\n", "    bimSaDone();\n")

# ---- the editing of findings, the photographs, the pins, the checklists: gone ----
cut("  /* ---- edits: each one undo step ---- */\n  function bimSaAdd(cat,f){\n", "  /* ---- the panel ---- */\n", "")
cut("  function bimSaOpt(L,cur){", "  /* __acad3dV162: what each category holds besides its findings.",
    """  /* __acad3dV164: a finding the data wrote, to read: its number, what it says, its class and source */
  function bimSaFindingHtml(f){
    var cl=bimSaPair(BIM_SA_CLS,f.cls);
    return '<div class="a3d-safind c-'+bimEsc(f.cls)+'" data-safind="'+bimEsc(f.id)+'">'+
      '<div class="a3d-safhd"><span class="a3d-safno">'+bimSaNumber(f)+'</span><span class="a3d-saftt">'+bimEsc(f.title)+'</span></div>'+
      (f.value?'<div class="a3d-safv">'+bimEsc(f.value)+'</div>':'')+
      '<div class="a3d-safm"><b class="k-'+bimEsc(f.cls)+'">'+bimEsc(cl)+(f.cls!=='neutral'?', '+bimSaPair(BIM_SA_SEV,String(f.sev)).toLowerCase():'')+'</b> \\u00b7 '+
      bimEsc(f.source||'no source given')+' \\u00b7 '+bimEsc(f.date)+'</div></div>';
  }
""")
cut("  function bimSaCatHtml(c,i,C){\n", "  /* __acad3dV162: Location's data: where the site is, and its context (V133) */\n",
    """  function bimSaCatHtml(c,i,C){
    var F=bimSaOf(c.id),open=!!A3D_SA.open[c.id],nc=0,no=0,nr=0,dat=BIM_SA_DATA[c.id],see=BIM_SA_SEE[c.id],k;
    var T=(C||[]).filter(function(x){return x.group===c.id;}),on=T.filter(function(x){return x.state==='on'||x.state==='stale'||x.state==='busy';});
    F.forEach(function(f){if(f.cls==='constraint')nc++;else if(f.cls==='opportunity')no++;else if(f.cls==='redflag')nr++;});
    var sum=F.length?bimSaN(F.length,'finding')+(nr?', '+bimSaN(nr,'red flag'):'')+(nc?', '+bimSaN(nc,'constraint'):'')+(no?', '+bimSaN(no,'opportunity','opportunities'):''):'No findings yet';
    if(on.length)sum+=' \\u00b7 '+on.map(function(x){return x.title;}).join(', ')+' on';
    var h='<div class="a3d-anzcard a3d-sacat'+(open?' open':'')+'" data-sacat="'+c.id+'">'+
      '<div class="a3d-anzhd"><button type="button" class="a3d-anztog" data-satog="'+c.id+'" aria-expanded="'+open+'">'+
      '<span class="a3d-anzchev">'+BIM_ANZ_CHEV+'</span><span class="a3d-anzname"><span class="a3d-anzttl">'+(i+1)+'. '+bimEsc(c.n)+'</span>'+
      '<span class="a3d-anzsum">'+bimEsc(sum)+'</span></span></button></div>'+
      '<div class="a3d-anzbody"><div class="a3d-saq">'+bimEsc(c.q)+'</div>';
    if(T.length)h+='<div class="a3d-sachkhd">Analyses</div><div class="a3d-anzlist a3d-satools">'+T.map(bimAnzCard).join('')+'</div>';
    if(dat)h+=dat();
    if(see){for(k=0;k<BIM_SA_CATS.length;k++)if(BIM_SA_CATS[k].id===see[0])break;
      h+='<div class="a3d-salink">'+bimEsc(see[1])+'<button type="button" class="a3d-anzbtn" data-saact="goto:'+see[0]+'">'+(k+1)+'. '+bimEsc(BIM_SA_CATS[k].n)+'</button></div>';}
    h+='<div class="a3d-sachkhd">Findings</div>'+(F.length?F.map(bimSaFindingHtml).join(''):'<div class="a3d-sanote">None yet: Analyze site writes them from the data.</div>')+
      '</div></div>';
    return h;
  }
""")
cut("  function bimSaWire(w){\n", "  function bimSaToggle(id,on){\n",
    """  function bimSaWire(w){
    w.addEventListener('click',function(ev){
      var t=ev.target&&ev.target.closest?ev.target:null,b;
      if(!t)return;
      b=t.closest('[data-satog]');if(b){bimSaToggle(b.getAttribute('data-satog'));return;}
      b=t.closest('[data-saact]');if(!b||b.disabled)return;
      try{bimSaAct(b.getAttribute('data-saact'));}catch(eS){console.warn('[BIM] Site analysis',eS);a3dToast('That did not work - see the console');}
    });
    w.addEventListener('change',function(ev){
      var e=ev.target,k;
      if(!e||!e.getAttribute)return;
      if((k=e.getAttribute('data-znf'))){bimZnSet(k,e.value);return;}   /* __acad3dV160 */
    });
    /* __acad3dV164: Enter in the address runs it */
    w.addEventListener('keydown',function(ev){
      var e=ev.target;
      if(ev.key!=='Enter'||!e||!e.getAttribute||!e.getAttribute('data-saaddr'))return;
      ev.preventDefault();
      try{bimSaAct('analyze');}catch(eS){console.warn('[BIM] Site analysis',eS);a3dToast('That did not work - see the console');}
    });
  }
""")
rep("""    if(c==='add')return bimSaAdd(v);
    if(c==='edit'){A3D_SA.edit=v;bimSaRefresh(true);return true;}
    if(c==='done'){A3D_SA.edit=null;bimSaRefresh(true);return true;}
    if(c==='del')return bimSaDel(v);
    if(c==='pin')return bimSaStartPin(v);
    if(c==='unpin')return bimSaPlace(v,null);
    if(c==='unphoto')return bimSaUnphoto(v);
""", """    if(c==='analyze'){   /* __acad3dV164 */
      var ai=document.querySelector('.a3d-analyze-wrap [data-saaddr]');
      return bimSiteAnalyze(ai?ai.value:'');
    }
    if(c==='dglegend'){var D=bimDgState();D.legendOff=!D.legendOff;saveSoon();paint();bimSaRefresh(true);return true;}
""")
rep("    if(c==='fill')return bimSaFill();\n", "")
cut("  /* the pins: a numbered circle in the finding's colour */\n  function drawSaPins(ctx,V,W,H){\n",
    "  /* __acad3dV73: the no-selection inspector.", "")
rep("    if(!capMode)drawSaPins(ctx,V,W,H);   /* __acad3dV158: the site analysis findings */\n", "")
rep("""    }else if(sk.tool==='sapin'){   /* __acad3dV158: a finding placed on the plan */
      var saF=sk.fid;
      A3D.sk=null;
      bimSaPlace(saF,[gx,gz]);
""", "")
rep("if(astale){astale.parentNode.removeChild(astale);A3D_SA.edit=null;A3D_ANZ.pend=false;did=true;}",
    "if(astale){astale.parentNode.removeChild(astale);A3D_ANZ.pend=false;did=true;}")

# ---- the hooks that served what went; Analyze site's for the tests ----
rep("  window.__a3dSaStandard=function(){return {stages:BIM_SA_STAGES.map(function(x){return x[0];}),cats:BIM_SA_CATS.map(function(c){return {id:c.id,n:c.n,desk:c.desk.length,visit:c.visit.length};})};};\n",
    "  window.__a3dSaStandard=function(){return {cats:BIM_SA_CATS.map(function(c){return {id:c.id,n:c.n};})};};   /* __acad3dV164: no stages, no checklists */\n")
rep("""  window.__a3dSaAdd=function(cat,f){return bimSaAdd(cat,f);};
  window.__a3dSaSet=function(id,k,v){return bimSaSet(id,k,v);};
  window.__a3dSaDel=function(id){return bimSaDel(id);};
  window.__a3dSaDefine=function(k,v){return bimSaSetDefine(k,v);};
  window.__a3dSaCheck=function(k,on){return bimSaCheck(k,on);};
  window.__a3dSaPlace=function(id,pt){return bimSaPlace(id,pt);};
  window.__a3dSaStartPin=function(id){return bimSaStartPin(id);};
  window.__a3dSaPhotoUrl=function(id,url){return bimSaPhotoFromUrl(id,url);};
  window.__a3dSaNumber=function(id){var f=bimSaFind(id);return f?bimSaNumber(f):null;};
  window.__a3dSaPins=function(){return (A3D.lastSaPins||[]).slice();};
  window.__a3dSaEdit=function(id){A3D_SA.edit=id||null;bimSaRefresh(true);return true;};
""", """  window.__a3dSaNumber=function(id){var f=bimSaFind(id);return f&&f.auto?bimSaNumber(f):null;};
  /* __acad3dV164: Analyze site and the analyses in the model */
  window.__a3dSiteRun=function(q){return bimSiteAnalyze(q);};
  window.__a3dSiteRunState=function(){return JSON.parse(JSON.stringify({busy:A3D_SITERUN.busy,steps:A3D_SITERUN.steps}));};
  window.__a3dDgRun=function(a){return bimDgRunAll(a||null);};
  window.__a3dDgState=function(){return JSON.parse(JSON.stringify(bimDgState()));};
  window.__a3dDgSite=function(){return JSON.parse(JSON.stringify(bimDgSite()));};
  window.__a3dDgList=function(a){return bimDgDiags(a||null).map(function(o){return {id:o.id,name:o.name,a:o.dg.a,k:o.dg.k,kind:o.dg.g.kind,layer:o.layer,edited:bimDgEdited(o),newer:!!o.dg.newer,orphan:!!o.dg.orphan,mine:!o.dg.gen};});};
  window.__a3dDgSet=function(id,f,v){return bimDgSet(objById(id),f,v);};
  window.__a3dDgReset=function(id){return bimDgReset(id);};
  window.__a3dDgResetAnalysis=function(a){return bimDgResetAnalysis(a);};
  window.__a3dDgAct=function(v){return bimDgAct(v);};
  window.__a3dDgPick=function(x,y){var o=bimPickDiag(x,y);return o?o.id:null;};
  window.__a3dDgHits=function(){return A3D_DG.hits.map(function(h){return {id:h.id,segs:h.segs.length,dots:h.dots.length,boxes:h.boxes.map(function(b){return b.slice();})};});};
  window.__a3dDgLegend=function(){return A3D_DG.legend?JSON.parse(JSON.stringify(A3D_DG.legend)):null;};
  window.__a3dDgCrtn=function(Q18,V,p,dcl,half){var L0=bimDgL0(Q18,V,p);return {L0:L0,at:bimDgLat(L0,dcl,half||0),reach:BIM_DG_NOISE_BANDS.map(function(b){return bimDgReach(L0,b[0],half||0);})};};
  window.__a3dDgRoadClass=function(hw){return bimDgRoadClass(hw);};
  window.__a3dDgBarrier=function(a,H,x){return bimDgBarrier(a,H,x);};
  window.__a3dUndoDepth=function(){return UNDO_STACK.length;};
  window.__a3dDgToScreen=function(p){var q=toScreen(p,camVecs(A3D.cam),cvW(),cvH());return [q[0],q[1],q[2]];};
  window.__acad3dV164='diagobjects,live,editable,keptedits,deletedstay,newer,orphans,copies,reset,resetanalysis,layers,sublayers,legend,underover,bandsbatched,pick,transform,props,'+
    'frame,sunpaths,sunnow,shadows,winds,seasons,secmean,strongest,rose,isovist,views,noise,crtn,fhwa,dinbands,rails,timezone,'+
    'analyzesite,address,steps,onestep,radius,zoningstep,cards,command,removedstages,removeddefine,removedtyped,removedphotos,removedpins,removedchecklists';
""")

# ---- the command; Fill from the model is in it now ----
rep("    ['SITEANALYSIS',['SA','SITEAN','SITEPROCESS'],'siteanalysis','Site analysis, in the Analyze tab: the standard process, ten categories, findings with their sources, on the plan'],",
    "    ['SITEANALYSIS',['SA','SITEAN','SITEPROCESS'],'siteanalysis','Site analysis, in the Analyze tab: Analyze site, the ten categories, the analyses drawn in the model and the findings with their sources'],")
rep("    ['SAFILL',['SITEANALYSISFILL','SAFROMMODEL'],'safill','Fill the site analysis from what the model already knows: location, context, property, terrain, sun, access'],\n",
    "    ['ANALYZESITE',['SITEANALYZE','RUNSITEANALYSIS','SAFILL','SITEANALYSISFILL','SAFROMMODEL'],'analyzesite','Analyze site: get what is around the site from free open data and draw each analysis in the model -- compass, sun paths, shadows, winds, views, noise -- on Layers, Site analysis; one undo step'],   /* __acad3dV164 */\n")
rep("    safill:function(){bimAnzView();bimSaFill();},\n",
    "    analyzesite:function(){bimAnzView();bimSiteAnalyze('');},   /* __acad3dV164 */\n")
rep("    CONTEXTREMOVE:'delete clear neighbours context',\n",
    "    CONTEXTREMOVE:'delete clear neighbours context',\n"
    "    ANALYZESITE:'site analysis analyze run one click diagrams sun path shadows wind rose views isovist noise compass distance rings layers climate context fill findings',   /* __acad3dV164 */\n")
rep("  var BIM_APP_VERSION={v:'V163',date:'2026-10-10'};   /* __acad3dV162; __acad3dV163 */",
    "  var BIM_APP_VERSION={v:'V164',date:'2026-10-11'};   /* __acad3dV162; __acad3dV163; __acad3dV164 */")

# ---- the look: the steps and the legends; the stages, checklists, editor and photographs go ----
rep(""".a3d-sastages{display:flex;flex-wrap:wrap;gap:3px;margin:0 0 4px}
.a3d-sastage{flex:1 0 auto;min-width:34px;border:1px solid rgba(255,255,255,.14);border-radius:6px;background:transparent;color:#9aa3ad;font:inherit;font-size:11px;padding:3px 6px;min-height:26px;cursor:pointer;white-space:nowrap}
.a3d-sastage.done{color:#81c784;border-color:rgba(129,199,132,.35)}
.a3d-sastage.on{background:#2f6fd6;border-color:#2f6fd6;color:#fff}
.a3d-sastagecap{font-size:11.5px;color:#aab4bf;margin:0 2px 10px;line-height:1.4}
""", """/* __acad3dV164: Analyze site, what each source brought, and the analyses' legends */
.a3d-sarun{border-top:0;padding-top:2px}
.a3d-sarun .a3d-sago{min-height:30px;padding:0 14px;font-size:12.5px;font-weight:600}
.a3d-sarun .a3d-saval .a3d-anzbtn{margin:2px 4px 2px 0}
.a3d-sasteps{list-style:none;margin:8px 0 0;padding:0;display:flex;flex-direction:column;gap:5px}
.a3d-sastep{display:grid;grid-template-columns:10px minmax(0,1fr) auto;column-gap:7px;align-items:center;font-size:12px;line-height:1.35;color:#d5dae0}
.a3d-sastepic{width:8px;height:8px;border-radius:50%;box-sizing:border-box;border:1px solid #6b7785}
.a3d-sastep.s-ok .a3d-sastepic{background:#30a46c;border-color:#30a46c}
.a3d-sastep.s-fail .a3d-sastepic{background:#e5484d;border-color:#e5484d}
.a3d-sastep.s-busy .a3d-sastepic{background:#f5a524;border-color:#f5a524;animation:a3d-sapulse .8s ease-in-out infinite alternate}
.a3d-sastep.s-part .a3d-sastepic{background:#f5a524;border-color:#f5a524}
.a3d-sastep.s-skip .a3d-sastepic{background:#6b7785}
.a3d-sastepst{font-size:10.5px;color:#8a96a3;white-space:nowrap}
.a3d-sastep.s-fail .a3d-sastepst{color:#ef8a8d}
.a3d-sastep.s-part .a3d-sastepst{color:#f5b54a}
.a3d-sastept{grid-column:2/4;font-size:11px;color:#8a96a3;overflow-wrap:anywhere}
@keyframes a3d-sapulse{from{opacity:.35}to{opacity:1}}
@media (prefers-reduced-motion:reduce){.a3d-sastep.s-busy .a3d-sastepic{animation:none}}
.a3d-dgleg{display:flex;flex-wrap:wrap;gap:4px 10px;margin:4px 0 4px;font-size:11px;color:#c9d1d9}
.a3d-dglegi{display:inline-flex;align-items:center;gap:5px}
.a3d-dglegi i{display:inline-block;width:12px;height:8px;border-radius:2px;flex:none}
.a3d-dglegi i.k-line,.a3d-dglegi i.k-dash{height:0;border-radius:0;border-top:2px solid currentColor}
.a3d-dglegi i.k-dash{border-top-style:dashed}
.a3d-dglegi i.k-dot{width:8px;height:8px;border-radius:50%}
""")
rep(".a3d-safph{display:block;max-width:100%;max-height:150px;border-radius:5px;margin:5px 0 2px}\n"
    ".a3d-safed{margin:6px 0 2px;padding:7px 8px;border-radius:6px;background:rgba(255,255,255,.04)}\n"
    ".a3d-sachk{display:flex;align-items:flex-start;gap:7px;font-size:12px;color:#c9d1d9;margin:0 0 4px;line-height:1.35;cursor:pointer}\n"
    ".a3d-sachk input{margin:2px 0 0;flex:none}\n"
    ".a3d-sachk.on span{color:#8a96a3;text-decoration:line-through}\n", "")
rep("@media(pointer:coarse){\n.a3d-sastage{min-height:36px;font-size:12.5px;padding:4px 10px}\n",
    "@media(pointer:coarse){\n.a3d-sarun .a3d-sago{min-height:40px}\n")
rep(".a3d-sachk{font-size:13.5px;min-height:30px}\n.a3d-sachk input{width:20px;height:20px}\n", "")
rep("body.light-theme .a3d-sastage{border-color:rgba(0,0,0,.15);color:#555}\n"
    "body.light-theme .a3d-sastage.on{color:#fff}\n"
    "body.light-theme .a3d-sastage.done{color:#2e7d32;border-color:rgba(46,125,50,.35)}\n", "")
rep("body.light-theme .a3d-saval,body.light-theme .a3d-safv,body.light-theme .a3d-sachk{color:#333}\n"
    "body.light-theme .a3d-sastagecap,body.light-theme .a3d-saq,",
    "body.light-theme .a3d-saval,body.light-theme .a3d-safv,body.light-theme .a3d-sastep,body.light-theme .a3d-dgleg{color:#333}\n"
    "body.light-theme .a3d-sastept,body.light-theme .a3d-sastepst,body.light-theme .a3d-saq,")
rep("body.light-theme .a3d-safed{background:rgba(0,0,0,.035)}\n", "")

rep("     its name, its question, its data, its findings, its checklist -- shows whole and opened; otherwise\n",
    "     its name, its question, its data, its findings -- shows whole and opened; otherwise\n")
rep("  /* an element's words, each text apart: its textContent runs \"Define\" and \"Boundary\" into one */\n",
    "  /* an element's words, each text apart: its textContent runs \"Place\" and \"Boundary\" into one */\n")

# the controls the audit knows: what went, gone; what came, claimed
rep("""    {sel:'[data-sastage]',why:'Site analysis: the stage the project is at'},
    {sel:'[data-satog]',why:'Site analysis: a category opens and closes'},
    {sel:'[data-saact]',why:'Site analysis: fill, add, edit, pin, photograph, delete; climate and risk'},
    {sel:'[data-saf]',why:'Site analysis: the project type, the questions, the pins switch'},
    {sel:'[data-saff]',why:'Site analysis: a field of a finding'},
    {sel:'[data-sachk]',why:'Site analysis: a checklist item'},
    {sel:'[data-saphoto]',why:'Site analysis: the photograph of a finding'},
""", """    {sel:'[data-satog]',why:'Site analysis: a category opens and closes'},
    {sel:'[data-saact]',why:'Site analysis: Analyze site, the legend, a category\\'s data and boards, the property line'},   /* __acad3dV164 */
    {sel:'[data-saaddr]',why:'Site analysis: the site\\'s address, found when Analyze site runs'},
    {sel:'[data-dgf]',why:'a site analysis element: its colour, line, opacity and labels'},
    {sel:'[data-dgact]',why:'a site analysis element: reset it to the analysis, or run the analysis again'},
""")

# nothing that went is still asked for
for gone in ['bimSaAdd(', 'bimSaSet(', 'bimSaDel(', 'bimSaSetDefine(', 'bimSaCheck(', 'bimSaPlace(', 'bimSaStartPin(',
             'bimSaPhotoFromUrl(', 'bimSaPhotoFile(', 'bimSaUnphoto(', 'drawSaPins(', 'BIM_SA_STAGES', 'BIM_SA_TYPES',
             'BIM_SA_PHOTO_PX', "'sapin'", 'A3D_SA.edit', 'lastSaPins', 'bimSaConfOf', 'bimSaOpt(', 'data-sachk', 'data-saff',
             'data-sastage', 'data-saphoto', 'a3d-sastage', 'a3d-sachk{', 'BIM_SA_COL', 'BIM_SA_FIELDS']:
    assert gone not in txt, 'still there: ' + gone

out = txt.encode('utf-8')
SRC.write_bytes(out)
print('wrote %s: %d bytes, sha256 %s' % (SRC, len(out), hashlib.sha256(out).hexdigest()))
