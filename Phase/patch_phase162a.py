"""patch_phase162a.py -- V162: one Analyze.

reference/research-one-analyze-boards.md. The owner: "you are splitting the analysis and site
analysis on 2 different layers. they should be just one ... im trying to make everything consistent
not sprawling everywhere". Analyze was two views behind a switch, Analyses and Site analysis. It is
one list now, in the order the work goes:
- the stages and Define (the boundary, the project, the questions), red flags first;
- the ten categories, each holding its analyses, its data and its findings:
  Location the site context; Legal zoning and yield; Landform the survey check, slope, elevation
  and aspect, and grading; Water the rain on the terrain; Climate the climate and risk data, sun and
  shadows, sun hours and solar; Access the access and people data; Environmental risk and People and
  place point to the data they share with Climate and Access;
- Model at the end: what reads the model itself (colour by, areas by usage, buildings LOD and
  solids, statistics, frame analysis).
One search over all of it: a category asked for by its own words shows whole, opened; otherwise the
analyses in it that match. The panel keeps .a3d-analyze-wrap and .a3d-sa-wrap on one element, so
everything that reached either half reaches it."""
NAME = 'patch_phase162a.py'
BASE = 'e987ca2c332be3de03923756aa1036933e82e9fd1312b02cd650384722ea04df'   # V161
import hashlib, pathlib, sys
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')
raw = P.read_bytes()
h0 = hashlib.sha256(raw).hexdigest()
if h0 != BASE:
    sys.exit('ABORT: baseline %s, expected %s' % (h0, BASE))
t = raw.decode('utf-8')


def rep(old, new, n=1):
    global t
    c = t.count(old)
    if c != n:
        sys.exit('ABORT: anchor count %d (want %d): %r' % (c, n, old[:80]))
    t = t.replace(old, new)


def span(start, end, new):
    """replace from start up to and including end (both unique from start on)"""
    global t
    if t.count(start) != 1:
        sys.exit('ABORT: span start count %d: %r' % (t.count(start), start[:80]))
    i = t.index(start)
    j = t.find(end, i)
    if j < 0:
        sys.exit('ABORT: span end not found: %r' % end[:80])
    t = t[:i] + new + t[j + len(end):]


# ---- the rows: a row's open state is its own, not its category's (rows sit inside categories now) ----
rep('.a3d-anzcard.open .a3d-anzchev{transform:rotate(90deg)}\n',
    '.a3d-anzcard.open>.a3d-anzhd .a3d-anzchev{transform:rotate(90deg)}   /* __acad3dV162: its own, not a row inside it */\n')
rep('.a3d-anzcard.open .a3d-anzsum{display:none}\n',
    '.a3d-anzcard.open>.a3d-anzhd .a3d-anzsum{display:none}\n')
rep('.a3d-anzcard.open .a3d-anzbody{display:block}\n',
    '.a3d-anzcard.open>.a3d-anzbody{display:block}\n')
rep('.a3d-sacat .a3d-anzbody{padding-left:20px}\n',
    '.a3d-sacat>.a3d-anzbody{padding-left:20px}\n'
    '/* __acad3dV162: a category holds its analyses, its data and its findings; a search opens what it finds */\n'
    '.a3d-anz.q .a3d-sacat.qhit>.a3d-anzbody{display:block}\n'
    '.a3d-anz.q .a3d-sacat.qhit>.a3d-anzhd .a3d-anzchev{transform:rotate(90deg)}\n'
    '.a3d-anz.q .a3d-sacat.qhit>.a3d-anzhd .a3d-anzsum{display:none}\n'
    '.a3d-satools{margin:0 -4px 4px;padding:2px 0;border-radius:7px}\n'
    '.a3d-satools .a3d-anzbody{padding-left:22px}\n'
    '.a3d-salink{display:flex;flex-wrap:wrap;align-items:center;gap:4px 8px;font-size:11.5px;color:#aab4bf;line-height:1.4;margin:2px 0 8px}\n'
    '.a3d-sacap{font-size:11.5px;color:#8a96a3;margin:-2px 2px 6px;line-height:1.4}\n'
    '/* the panel scrolls, not the list in it: the search stays at its top while the list goes under it */\n'
    '.a3d-analyze-wrap>.a3d-anz{overflow:visible}\n'
    '.a3d-sacat{scroll-margin-top:44px}\n'
    '.a3d-anz>.a3d-anzsearch{position:sticky;top:0;z-index:2;box-shadow:0 0 0 6px #2c2c2c}\n'
    'body.light-theme .a3d-anz>.a3d-anzsearch{box-shadow:0 0 0 6px #fff}\n'
    'body.light-theme .a3d-salink,body.light-theme .a3d-sacap{color:#555}\n')

# ---- the switch goes ----
span('.a3d-anzview{display:flex;gap:2px;padding:2px;margin:0 0 10px;border-radius:8px;background:rgba(255,255,255,.06)}\n',
     'body.light-theme .a3d-anzviewbtn[aria-selected="true"]{background:#fff;color:#111;box-shadow:0 1px 2px rgba(0,0,0,.15)}\n', '')

rep("""  var A3D_ANZ={lod:null,open:bimAnzOpenLoad(),q:'',view:(function(){try{return localStorage.getItem('acad3dAnzView')==='site'?'site':'analyses';}catch(eV){return 'analyses';}})()};   /* __acad3dV148: the rows open, and the search; __acad3dV159: the view */
""", """  var A3D_ANZ={lod:null,open:bimAnzOpenLoad(),q:'',pend:false};   /* __acad3dV148: the rows open, and the search; __acad3dV162: a refresh held while a field is typed in */
""")
span("  /* __acad3dV159: Analyses | Site analysis, the switch at the top of the Analyze tab */\n",
     "    return !!b;\n  }\n",
     r"""  /* __acad3dV162: one Analyze. The analyses and the site analysis were two views behind a switch;
     they are one list now. Opening it to either is opening it. */
  function bimAnzView(){
    bimShellSetTab('analyze');
    var p=document.getElementById('a3d-leftpanel');
    return !!(p&&p.querySelector('.a3d-analyze-wrap'));
  }
  /* a category opened, and brought into view; a search that hides it is cleared */
  function bimSaGoto(id){
    if(!bimSaCat(id))return false;
    bimAnzView();
    var w=document.querySelector('.a3d-analyze-wrap'),s=w?w.querySelector('[data-anzsearch]'):null,c;
    if(A3D_ANZ.q){A3D_ANZ.q='';if(s)s.value='';if(w)bimAnzFilter(w);}
    bimSaToggle(id,true);
    c=w?w.querySelector('[data-sacat="'+id+'"]'):null;
    if(c){try{c.scrollIntoView({block:'start',behavior:'smooth'});}catch(eS){c.scrollIntoView();}}
    return !!c;
  }
""")
rep("""  var BIM_ANZ_GROUPS=[['model','Model'],['site','Site and terrain'],['structure','Structure'],['env','Environment']];
  var BIM_ANZ_GROUP_OF={lens:'model',areas:'model',lod:'model',stats:'model',survey:'site',terrain:'site',grading:'site',rain:'site',structure:'structure',sun:'env',sunhours:'env',solar:'env'};
""", """  /* __acad3dV162: an analysis sits in the category it answers; what reads the model itself is Model */
  var BIM_ANZ_GROUP_OF={survey:'landform',terrain:'landform',grading:'landform',rain:'water',sun:'climate',sunhours:'climate',solar:'climate'};
  var BIM_ANZ_MODEL=['lens','areas','lod','stats','structure'];
""")

# ---- the list ----
span("  function bimAnzCountText(C){\n", "      '<div class=\"a3d-anzrows\">'+bimAnzRowsHtml(C)+'</div></div>';\n  }\n",
     r"""  function bimAnzCountText(C){
    var n=C.filter(function(c){return c.state==='on'||c.state==='stale'||c.state==='busy';}).length,F=bimSa().findings,r=0;
    F.forEach(function(f){if(f.cls==='redflag')r++;});
    return bimSaN(F.length,'finding')+(r?', '+bimSaN(r,'red flag'):'')+(n?' · '+n+' on':'');
  }
  /* __acad3dV162: under the search, in the order the work goes: the stages, red flags, Define, the
     ten categories with their analyses, data and findings, and the model */
  function bimAnzBodyHtml(C){
    var s=bimSa(),F=s.findings,R=F.filter(function(f){return f.cls==='redflag';}),P=A3D.objs.filter(bimIsProperty),bd,h;
    if(P.length){var g=bimPropertyGeometry(P[0]);bd=bimEsc(P[0].name)+', '+bimDispNum(g.area,1)+' m²';}
    else bd='None yet: <button type="button" class="a3d-anzbtn" data-saact="cmd:propertyshape">From a shape</button> <button type="button" class="a3d-anzbtn" data-saact="cmd:propertyline">From bearings</button>';
    h='<div data-anzsec="stages"><div class="a3d-sastages" role="group" aria-label="Stage">'+BIM_SA_STAGES.map(function(x,i){
        return '<button type="button" class="a3d-sastage'+(i===s.stage?' on':(i<s.stage?' done':''))+'" data-sastage="'+i+'" aria-pressed="'+(i===s.stage)+'" title="'+bimEsc(x[1])+'">'+i+' '+bimEsc(x[0])+'</button>';}).join('')+'</div>'+
      '<div class="a3d-sastagecap">'+bimEsc(BIM_SA_STAGES[s.stage][1])+'</div></div>';
    if(R.length)h+='<div class="a3d-saflags" data-anzsec="flags"><div class="a3d-sasechd">Red flags first</div>'+R.map(function(f){return '<div class="a3d-saflag">'+bimSaNumber(f)+' '+bimEsc(f.title)+(f.value?': '+bimEsc(f.value):'')+'</div>';}).join('')+'</div>';
    h+='<div class="a3d-sasec" data-anzsec="define"><div class="a3d-sasechd">Define</div>'+
      '<div class="a3d-sarow"><span class="a3d-salab">Boundary</span><span class="a3d-saval">'+bd+'</span></div>'+
      '<div class="a3d-sarow"><label for="a3d-saptype">Project</label><select id="a3d-saptype" data-saf="ptype">'+BIM_SA_TYPES.map(function(x){return '<option value="'+bimEsc(x)+'"'+(x===s.ptype?' selected':'')+'>'+(x?bimEsc(x):'Not set')+'</option>';}).join('')+'</select></div>'+
      '<div class="a3d-sarow"><label for="a3d-saq">Questions</label><textarea id="a3d-saq" data-saf="questions" maxlength="2000" placeholder="What must the analysis answer?">'+bimEsc(s.questions)+'</textarea></div>'+
      '<label class="a3d-sachk"><input type="checkbox" data-saf="pins"'+(s.pins?' checked':'')+'><span>Show the findings on the plan</span></label>'+
      '<div class="a3d-saacts"><button type="button" class="a3d-anzbtn pri" data-saact="fill" title="Location, context, property, terrain, sun, access: what the model knows, with its sources">Fill from the model</button></div></div>';
    h+='<div class="a3d-sasec" data-anzsec="cats"><div class="a3d-sasechd">The ten categories</div><div class="a3d-anzlist">'+BIM_SA_CATS.map(function(c,i){return bimSaCatHtml(c,i,C);}).join('')+'</div></div>';
    var M=BIM_ANZ_MODEL.map(function(id){return C.filter(function(c){return c.id===id;})[0];}).filter(function(c){return !!c;});
    h+='<div class="a3d-sasec a3d-anzgrp" data-anzgrp="model"><div class="a3d-sasechd a3d-anzgrphd">Model</div><div class="a3d-sacap">What the model itself shows; no site data needed.</div>'+
      '<div class="a3d-anzlist">'+M.map(bimAnzCard).join('')+'</div></div>';
    return h+'<div class="a3d-anzempty" hidden>Nothing matches</div>';
  }
  function bimAnalyzeHtml(){
    var C=bimAnzCards();
    return '<div class="a3d-anz a3d-sa"><div class="a3d-anzhead"><span class="a3d-anzttl0">Analyze</span><span class="a3d-anzcount">'+bimAnzCountText(C)+'</span></div>'+
      '<input type="search" class="a3d-anzsearch" data-anzsearch="1" placeholder="Search analyses, data and findings" aria-label="Search Analyze" autocomplete="off" value="'+bimEsc(A3D_ANZ.q||'')+'">'+
      '<div class="a3d-anzrows">'+bimAnzBodyHtml(C)+'</div></div>';
  }
""")

# ---- the search ----
span("  /* the search: rows by their name, what they say, their buttons and their group; in place */\n",
     "    return n;\n  }\n",
     r"""  /* __acad3dV162: the search, over everything, in place. A category asked for by its own words --
     its name, its question, its data, its findings, its checklist -- shows whole and opened; otherwise
     the analyses in it that match, by their name, what they say and their buttons. */
  /* an element's words, each text apart: its textContent runs "Define" and "Boundary" into one */
  function bimAnzText(el){
    var w=document.createTreeWalker(el,NodeFilter.SHOW_TEXT,null,false),s=[],n;
    while((n=w.nextNode()))s.push(n.nodeValue);
    return s.join(' ');
  }
  function bimAnzTexts(root,sel){return [].map.call(root.querySelectorAll(sel),bimAnzText).join(' ');}
  function bimAnzRowText(r,more){return r.getAttribute('data-anzcard')+' '+bimAnzTexts(r,'.a3d-anzttl,.a3d-anzst,.a3d-anzbtn')+' '+(more||'');}
  function bimAnzFilter(w){
    var q=String(A3D_ANZ.q||'').toLowerCase().replace(/^\s+|\s+$/g,''),root=w?w.querySelector('.a3d-anz'):null,n=0,i,j,S,K,G,R,k,on,name,whole,hit,e;
    if(!root)return 0;
    function show(x,v){if(v)x.removeAttribute('hidden');else x.setAttribute('hidden','');}
    root.classList.toggle('q',!!q);
    S=root.querySelectorAll('[data-anzsec="stages"],[data-anzsec="flags"],[data-anzsec="define"]');
    for(i=0;i<S.length;i++){
      on=!q||(S[i].getAttribute('data-anzsec')!=='stages'&&bimAnzWordsHit(q,bimAnzText(S[i])));
      show(S[i],on);if(q&&on)n++;
    }
    K=root.querySelectorAll('[data-sacat]');
    for(i=0;i<K.length;i++){
      name=(K[i].querySelector('.a3d-anzttl')||{textContent:''}).textContent;
      whole=!q||bimAnzWordsHit(q,name+' '+bimAnzTexts(K[i],'.a3d-saq,.a3d-clsec,.a3d-salink,.a3d-safind,.a3d-sachk'));
      R=K[i].querySelectorAll('[data-anzcard]');k=0;
      for(j=0;j<R.length;j++){hit=whole||bimAnzWordsHit(q,bimAnzRowText(R[j],name));show(R[j],hit);if(hit)k++;}
      on=whole||k>0;
      show(K[i],on);K[i].classList.toggle('qhit',!!q&&on);
      if(on)n+=1+k;
    }
    G=root.querySelectorAll('[data-anzgrp]');
    for(i=0;i<G.length;i++){
      name=(G[i].querySelector('.a3d-anzgrphd')||{textContent:''}).textContent;
      R=G[i].querySelectorAll('[data-anzcard]');k=0;
      for(j=0;j<R.length;j++){hit=!q||bimAnzWordsHit(q,bimAnzRowText(R[j],name));show(R[j],hit);if(hit)k++;}
      show(G[i],k>0);
      n+=k;
    }
    e=root.querySelector('.a3d-anzempty');
    if(e)show(e,!!q&&!n);
    return n;
  }
""")

# ---- the refresh: one, held while a field is typed in ----
span("  /* the panel again, when it is open: the rows only, so the search, its focus and the scroll stay */\n",
     "    return true;\n  }\n",
     r"""  /* the panel again, when it is open: the list only, so the search, its focus and the scroll stay.
     __acad3dV162: not under a field being typed in, whose words would go -- then when it is left. */
  function bimAnalyzeRefresh(force){
    var sh=document.getElementById('a3d-shell'),w=sh&&sh.dataset.tab==='analyze'?sh.querySelector('.a3d-analyze-wrap'):null,a=document.activeElement;
    if(!w)return false;
    if(!force&&a&&w.contains(a)&&/^(INPUT|TEXTAREA|SELECT)$/.test(a.tagName)&&!a.hasAttribute('data-anzsearch')&&a.type!=='checkbox'&&a.type!=='file'){A3D_ANZ.pend=true;return false;}
    A3D_ANZ.pend=false;
    try{
      var rows=w.querySelector('.a3d-anzrows'),cnt=w.querySelector('.a3d-anzcount'),C;
      if(rows&&cnt){C=bimAnzCards();bimRenderInto(rows,bimAnzBodyHtml(C));cnt.textContent=bimAnzCountText(C);}
      else w.innerHTML=bimAnalyzeHtml();
      bimAnzFilter(w);
    }catch(eA){console.warn('[BIM] Analyze panel',eA);}
    return true;
  }
""")

# ---- a category: its analyses, its data, its findings, its checklist ----
span("  function bimSaCatHtml(c,i){\n", "    return h;\n  }\n  function bimSaHtml(){\n",
     r"""  /* __acad3dV162: what each category holds besides its findings. Risk and People share the data
     Climate and Access fetch, and say where it is. */
  var BIM_SA_DATA={location:function(){return bimSaCtxHtml();},legal:function(){return bimZnSaHtml();},climate:function(){return bimClbSaHtml();},access:function(){return bimAccSaHtml();}};
  var BIM_SA_SEE={risk:['climate','Air quality and earthquakes come with the climate data'],people:['access','The census and the daily needs within a walk come with the access data']};
  function bimSaCatHtml(c,i,C){
    var s=bimSa(),F=bimSaOf(c.id),open=!!A3D_SA.open[c.id],nc=0,no=0,nr=0,cf=bimSaConfOf(c.id),j,dn=0,dat=BIM_SA_DATA[c.id],see=BIM_SA_SEE[c.id];
    var T=(C||[]).filter(function(x){return x.group===c.id;}),on=T.filter(function(x){return x.state==='on'||x.state==='stale'||x.state==='busy';});
    F.forEach(function(f){if(f.cls==='constraint')nc++;else if(f.cls==='opportunity')no++;else if(f.cls==='redflag')nr++;});
    for(j=0;j<c.desk.length;j++)if(s.checks[c.id+':d:'+j])dn++;
    for(j=0;j<c.visit.length;j++)if(s.checks[c.id+':v:'+j])dn++;
    var sum=F.length?bimSaN(F.length,'finding')+(nr?', '+bimSaN(nr,'red flag'):'')+(nc?', '+bimSaN(nc,'constraint'):'')+(no?', '+bimSaN(no,'opportunity','opportunities'):''):'No findings yet';
    sum+=' · '+dn+' of '+(c.desk.length+c.visit.length)+' checked';
    if(on.length)sum+=' · '+on.map(function(x){return x.title;}).join(', ')+' on';
    var stt=cf==='surveyed'?'on':cf==='site'?'on':cf==='desktop'?'warn':'',k;
    var h='<div class="a3d-anzcard a3d-sacat'+(open?' open':'')+'" data-sacat="'+c.id+'">'+
      '<div class="a3d-anzhd"><button type="button" class="a3d-anztog" data-satog="'+c.id+'" aria-expanded="'+open+'">'+
      '<span class="a3d-anzchev">'+BIM_ANZ_CHEV+'</span><span class="a3d-anzname"><span class="a3d-anzttl">'+(i+1)+'. '+bimEsc(c.n)+'</span>'+
      '<span class="a3d-anzsum">'+bimEsc(sum)+'</span></span></button>'+
      (cf?'<span class="a3d-anzstate a3d-anzstate-'+stt+'">'+bimEsc(bimSaPair(BIM_SA_CONF,cf))+'</span>':'')+'</div>'+
      '<div class="a3d-anzbody"><div class="a3d-saq">'+bimEsc(c.q)+'</div>';
    if(dat)h+=dat();
    if(see){for(k=0;k<BIM_SA_CATS.length;k++)if(BIM_SA_CATS[k].id===see[0])break;
      h+='<div class="a3d-salink">'+bimEsc(see[1])+'<button type="button" class="a3d-anzbtn" data-saact="goto:'+see[0]+'">'+(k+1)+'. '+bimEsc(BIM_SA_CATS[k].n)+'</button></div>';}
    if(T.length)h+='<div class="a3d-sachkhd">Analyses</div><div class="a3d-anzlist a3d-satools">'+T.map(bimAnzCard).join('')+'</div>';
    h+='<div class="a3d-sachkhd">Findings</div>'+(F.length?F.map(bimSaFindingHtml).join(''):'<div class="a3d-sanote">No findings yet.</div>')+
      '<div class="a3d-saacts"><button type="button" class="a3d-anzbtn" data-saact="add:'+c.id+'">Add finding</button></div>'+
      '<div class="a3d-sachkhd">At the desk</div>'+c.desk.map(function(t,k){var key=c.id+':d:'+k,on=!!s.checks[key];
        return '<label class="a3d-sachk'+(on?' on':'')+'"><input type="checkbox" data-sachk="'+key+'"'+(on?' checked':'')+'><span>'+bimEsc(t)+'</span></label>';}).join('')+
      '<div class="a3d-sachkhd">On site</div>'+c.visit.map(function(t,k){var key=c.id+':v:'+k,on=!!s.checks[key];
        return '<label class="a3d-sachk'+(on?' on':'')+'"><input type="checkbox" data-sachk="'+key+'"'+(on?' checked':'')+'><span>'+bimEsc(t)+'</span></label>';}).join('')+
      '</div></div>';
    return h;
  }
  /* __acad3dV162: Location's data: where the site is, and its context (V133) */
  function bimSaCtxHtml(){
    var c=A3D.site&&A3D.site.context&&A3D.site.context.last,st=bimSunSettings(),at='';
    if(bimSunNum(st.lat)&&bimSunNum(st.lon))at=Math.abs(st.lat).toFixed(4)+'° '+(st.lat<0?'S':'N')+', '+Math.abs(st.lon).toFixed(4)+'° '+(st.lon<0?'W':'E');
    return '<div class="a3d-clsec" data-ctxsec="1"><div class="a3d-sasechd">Site context</div>'+
      '<p class="a3d-clsum">'+(at?bimEsc('The site: '+at+'.'):'The site is not placed yet: give its latitude and longitude, or find its address, in Location.')+' '+
      (c?bimEsc('Context of '+c.date+': '+bimCtxCountsText(c.counts)+'.'):'The buildings, roads, water and trees around it, from OpenStreetMap, and the terrain: free, no account.')+'</p>'+
      '<div class="a3d-saacts"><button type="button" class="a3d-anzbtn'+(c?'':' pri')+'" data-saact="cmd:context">'+(c?'Get the context again':'Get the context')+'</button>'+
      '<button type="button" class="a3d-anzbtn" data-anzact="open:Location">Location</button></div></div>';
  }
  function bimSaHtmlV161(){
""")
# the V161 body of bimSaHtml is now unreachable: take it out whole
span("  function bimSaHtmlV161(){\n", "    return h;\n  }\n", "")
rep("""      b=t.closest('[data-anzview]');if(b){bimAnzView(b.getAttribute('data-anzview'));return;}   /* __acad3dV159 */
""", "")
rep("""    if(c==='fill')return bimSaFill();
""", """    if(c==='fill')return bimSaFill();
    if(c==='goto')return bimSaGoto(v);   /* __acad3dV162 */
""")
span("  /* the panel again: not while something in it has the focus, or what is typed would be lost */\n",
     "    return true;\n  }\n",
     "  /* __acad3dV162: the site analysis is in Analyze's one list; its refresh is that list's */\n"
     "  function bimSaRefresh(force){return bimAnalyzeRefresh(force);}\n")
rep("""    bimAnalyzeRefresh();   /* __acad3dV141 */
    bimSaRefresh();        /* __acad3dV158 */
""", """    bimAnalyzeRefresh();   /* __acad3dV141; __acad3dV162: the site analysis with it */
""")

# ---- the shell: one tab body ----
span("    var saView=shell.dataset.tab==='analyze'&&A3D_ANZ.view==='site';   /* __acad3dV159: one of Analyze's two views */\n",
     "      if(sstale){sstale.parentNode.removeChild(sstale);A3D_SA.edit=null;did=true;}\n    }\n",
     r"""    if(shell.dataset.tab==='analyze'&&!panel.querySelector('.a3d-analyze-wrap')){   /* __acad3dV141; __acad3dV162: the site analysis in it, one list */
      var abox=document.createElement('div');
      abox.className='a3d-tabbody a3d-analyze-wrap a3d-sa-wrap';
      abox.innerHTML=bimAnalyzeHtml();
      bimAnzFilter(abox);   /* __acad3dV148: the search kept from before */
      abox.addEventListener('click',function(ev){
        var tg=ev.target&&ev.target.closest?ev.target.closest('[data-anztog]'):null;   /* __acad3dV148: a row opens and closes */
        if(tg){bimAnzToggle(tg.getAttribute('data-anztog'));return;}
        var b=ev.target&&ev.target.closest?ev.target.closest('[data-anzact]'):null;
        if(!b||b.disabled)return;
        try{bimAnzAct(b.getAttribute('data-anzact'));}catch(eZ){console.warn('[BIM] Analyze',eZ);a3dToast('That did not work - see the console');}
      });
      abox.addEventListener('input',function(ev){
        var s=ev.target;
        if(s&&s.hasAttribute&&s.hasAttribute('data-anzsearch')){A3D_ANZ.q=s.value;bimAnzFilter(abox);}
      });
      abox.addEventListener('keydown',function(ev){
        var s=ev.target;
        if(s&&s.hasAttribute&&s.hasAttribute('data-anzsearch')&&ev.key==='Escape'&&s.value){ev.preventDefault();ev.stopPropagation();s.value='';A3D_ANZ.q='';bimAnzFilter(abox);}
      });
      /* a refresh held for a field being typed in happens when it is left */
      abox.addEventListener('focusout',function(){if(A3D_ANZ.pend)setTimeout(function(){if(A3D_ANZ.pend)bimAnalyzeRefresh();},0);});
      bimSaWire(abox);   /* __acad3dV158 */
      panel.appendChild(abox);
      did=true;
    }
    if(shell.dataset.tab!=='analyze'){
      var astale=panel.querySelector('.a3d-analyze-wrap');
      if(astale){astale.parentNode.removeChild(astale);A3D_SA.edit=null;A3D_ANZ.pend=false;did=true;}
    }
""")

# ---- commands and hooks ----
rep("""    siteanalysis:function(){bimAnzView('site');},                /* __acad3dV158; __acad3dV159: in Analyze */
    safill:function(){bimAnzView('site');bimSaFill();},
""", """    siteanalysis:function(){bimAnzView();},                      /* __acad3dV158; __acad3dV162: Analyze is one list */
    safill:function(){bimAnzView();bimSaFill();},
""")
rep("""    zoning:function(){bimAnzView('site');A3D_ZN.edit=true;bimSaRefresh(true);},   /* __acad3dV160 */
""", """    zoning:function(){A3D_ZN.edit=true;bimSaGoto('legal');bimSaRefresh(true);},   /* __acad3dV160; __acad3dV162: in Legal */
""")
rep("""    return w?[].filter.call(w.querySelectorAll('[data-anzcard]'),function(e){return !e.hasAttribute('hidden');}).map(function(e){return e.getAttribute('data-anzcard');}):null;
""", """    return w?[].filter.call(w.querySelectorAll('[data-anzcard]'),function(e){return !e.closest('[hidden]');}).map(function(e){return e.getAttribute('data-anzcard');}):null;   /* __acad3dV162: in a category the search hid too */
""")
rep("""  window.__a3dAnzOpenAll=function(on){bimAnzCards().forEach(function(c){bimAnzToggle(c.id,on!==false);});return Object.keys(A3D_ANZ.open).sort();};
""", """  window.__a3dAnzOpenAll=function(on){bimAnzCards().forEach(function(c){bimAnzToggle(c.id,on!==false);if(on!==false&&c.group!=='model')bimSaToggle(c.group,true);});return Object.keys(A3D_ANZ.open).sort();};   /* __acad3dV162: and the categories they sit in, so every row shows */
""")
rep("""  window.__a3dAnzView=function(v){if(v)return bimAnzView(v);return A3D_ANZ.view;};
""", """  window.__a3dAnzView=function(v){if(v)return bimAnzView();return 'analyze';};   /* __acad3dV162: one view; opening it to either opens it */
  window.__a3dSaGoto=function(id){return bimSaGoto(id);};
  window.__a3dAnalyzeRefresh=function(f){return bimAnalyzeRefresh(!!f);};
  window.__a3dAnzPending=function(){return A3D_ANZ.pend;};
  window.__a3dAnzCats=function(){return bimAnzCards().map(function(c){return {id:c.id,group:c.group};});};
""")

if t.count('__acad3dV162') < 10:
    sys.exit('ABORT: markers')
P.write_bytes(t.encode('utf-8'))
print('%s: %s -> %s (%d bytes)' % (NAME, h0[:12], hashlib.sha256(t.encode('utf-8')).hexdigest()[:12], len(t.encode('utf-8'))))
