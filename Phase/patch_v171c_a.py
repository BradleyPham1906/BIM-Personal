#!/usr/bin/env python3
"""V171c: one Analyze. The owner, after V171b: "The analyze should be combined with the site analysis. It should not be
two separate hubs. We need to integrate these two systems into one. And also, like, the wordings and the conclusions of
each site analysis panels, I think they should be on the right panel when you open the site analysis and hit a certain
analysis on the right panel, it will show an overview."

Analyze and the analysis workspace become one place. Analyze's tab opens the workspace and leaving the tab leaves it;
the bar's cross goes back to the tab Analyze was opened from. The left is one list: the site and Analyze site,
Overview, the ten categories, each a row with the analyses that answer it under it, and the model's own analyses. The
words are on the right, where Properties is while nothing is selected: the overview (the site, the red flags, every
category's findings counted, what the run fetched); a category (its question, what was found, its analyses, its data);
an analysis in the model (V171b's panel, and the findings it draws); one of the model's analyses (its state, its
settings, its buttons). A button that opens the model's Properties leaves a way back to the analysis above them.

What the hub had and the list no longer draws goes: the rows that opened in place and their remembered state, the
categories' bodies in the list, the run's steps under the button (the overview has them), Show and Hide on a row (its
tick), the analyses' Open (Analyze is the workspace). Run from the repository root:
    python3 Phase/patch_v171c_a.py <analysis-workspace.js>
"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import p171   # noqa: E402
from p171 import begin, rep, write, done   # noqa: E402


def ascii_js(t):
    return ''.join(c if ord(c) < 128 else '\\u%04x' % ord(c) for c in t)


def between(path, a, b, new):
    """Replace the text from anchor a up to (not including) anchor b, each found exactly once, a before b."""
    s = p171._text(path)
    if s.count(a) != 1 or s.count(b) != 1:
        sys.exit('src/%s: anchors %r (%d) and %r (%d)' % (path, a[:60], s.count(a), b[:60], s.count(b)))
    i, j = s.index(a), s.index(b)
    if not i < j:
        sys.exit('src/%s: %r after %r' % (path, a[:60], b[:60]))
    p171._files[path] = s[:i] + new + s[j:]


AW_JS = ascii_js(pathlib.Path(sys.argv[1]).read_text(encoding='utf-8'))

begin('bb5bd5879e9a580e7178e274a83b2ec0421f24c4238cc9b6e5bef2bb8abcae13')   # V171b, as merged

# ---- the workspace, Analyze itself ----
write('js/engine/site-analysis/analysis-workspace.js', AW_JS, replace=True)

# ---- Analyze's tab opens it, another tab leaves it ----
T = 'js/engine/ui/tool-palette.js'
rep(T, "  function bimShellSetTab(t){\n    var sh=document.getElementById('a3d-shell');\n    if(!sh)return false;\n    sh.classList.remove('collapsed');\n",
       "  function bimShellSetTab(t){\n    var sh=document.getElementById('a3d-shell'),was;\n    if(!sh)return false;\n    was=sh.getAttribute('data-tab');\n    sh.classList.remove('collapsed');\n")
rep(T, "    catch(eT){console.warn('[BIM] Shell tab render failed',eT);a3dToast('That panel could not be drawn');}\n    return true;\n  }\n  function bimBuildShell(){",
       "    catch(eT){console.warn('[BIM] Shell tab render failed',eT);a3dToast('That panel could not be drawn');}\n"
       "    bimAwTab(t,was);   /* __acad3dV171c: Analyze is the workspace, opened and left with its tab */\n"
       "    return true;\n  }\n  function bimBuildShell(){")

# ---- Analyze's list: the workspace's, its search over it ----
A = 'js/engine/analysis/analyze-tab.js'
rep(A, "  var A3D_ANZ={lod:null,open:bimAnzOpenLoad(),q:'',pend:false};   /* __acad3dV148: the rows open, and the search; __acad3dV162: a refresh held while a field is typed in */",
       "  var A3D_ANZ={lod:null,q:'',pend:false};   /* __acad3dV148: the search; __acad3dV162: a refresh held while a field is typed in */")
between(A, "  /* a category opened, and brought into view; a search that hides it is cleared */\n",
        "  /* __acad3dV148: a row, not a card.",
        "  /* a category, on the right, its row in the list in view; a search that hides it is cleared. __acad3dV171c: picked,\n"
        "     where it was opened in the list */\n"
        "  function bimSaGoto(id){\n"
        "    if(!bimSaCat(id))return false;\n"
        "    A3D_ANZ.q='';\n"
        "    bimAwPick('cat',id);\n"
        "    return !!document.querySelector('.a3d-analyze-wrap [data-sacat=\"'+id+'\"]');\n"
        "  }\n")
rep(A, "  /* __acad3dV148: a row, not a card. Its name, what it shows, its state and its first action on one\n"
       "     line; the whole status, the legend and every other action a click away. A row is opened by the\n"
       "     viewer, and stays open, in this browser. */\n",
       "  /* __acad3dV148: a row, not a card. __acad3dV171c: a row of the list, its name and its state; what it says,\n"
       "     its settings and its buttons on the right when it is picked */\n")
between(A, "  var BIM_ANZ_KEY='acad3dAnzOpen';\n", "  function bimAnzStateText(s){", "")
between(A, "  function bimAnzCard(c){\n", "  /* each analysis: what it shows now, and its buttons */\n", "")
between(A, "  /* __acad3dV162: under the search, in the order the work goes.", "  /* every word asked for starts a word of the text: rain is not in terrain */\n", "")
between(A, "  /* __acad3dV162: the search, over everything, in place.", "  /* a button: run it, or open its settings in Properties */\n",
        "  /* __acad3dV162: the search, in place. __acad3dV171c: over the list. A category asked for by its own words -- its\n"
        "     name, its question, where its data is, what was found -- shows whole; otherwise the analyses in it that match,\n"
        "     by their name, what they show, what they report and their buttons */\n"
        "  function bimAnzFilter(w){\n"
        "    var q=String(A3D_ANZ.q||'').toLowerCase().replace(/^\\s+|\\s+$/g,''),root=w?w.querySelector('.a3d-awl'):null,n=0,C={},K,i,j,R,k,c,nm,whole,hit,e,ov;\n"
        "    if(!root)return 0;\n"
        "    function show(x,v){if(v)x.removeAttribute('hidden');else x.setAttribute('hidden','');}\n"
        "    root.classList.toggle('q',!!q);\n"
        "    if(q)bimAnzCards().forEach(function(x){C[x.id]=x;});\n"
        "    ov=root.querySelector('.a3d-awl-ov');\n"
        "    if(ov)show(ov,!q);\n"
        "    K=root.querySelectorAll('[data-sacat],[data-anzgrp]');\n"
        "    for(i=0;i<K.length;i++){\n"
        "      c=bimSaCat(K[i].getAttribute('data-sacat'));nm=c?c.n:'Model';\n"
        "      whole=!q||(!!c&&bimAnzWordsHit(q,c.n+' '+c.q+' '+(BIM_SA_SEE[c.id]?BIM_SA_SEE[c.id][1]:'')+' '+bimSaOf(c.id).map(function(f){return f.title+' '+f.value+' '+bimSaPair(BIM_SA_CLS,f.cls)+' '+f.source;}).join(' ')));\n"
        "      R=K[i].querySelectorAll('[data-anzcard]');k=0;\n"
        "      for(j=0;j<R.length;j++){hit=whole||bimAnzWordsHit(q,bimAwRowWords(C[R[j].getAttribute('data-anzcard')],nm));show(R[j],hit);if(hit)k++;}\n"
        "      show(K[i],whole||k>0);\n"
        "      if(q)n+=k+(whole&&c?1:0);\n"
        "    }\n"
        "    e=root.querySelector('.a3d-anzempty');\n"
        "    if(e)show(e,!!q&&!n);\n"
        "    return n;\n"
        "  }\n"
        "  /* the list again, when Analyze is open: the search, its focus and the scroll stay.\n"
        "     __acad3dV162: not under a field being typed in, whose words would go -- then when it is left. */\n"
        "  function bimAnalyzeRefresh(force){\n"
        "    var sh=document.getElementById('a3d-shell'),w=sh&&sh.dataset.tab==='analyze'?sh.querySelector('.a3d-analyze-wrap'):null,a=document.activeElement;\n"
        "    if(!w)return false;\n"
        "    if(!force&&a&&w.contains(a)&&/^(INPUT|TEXTAREA|SELECT)$/.test(a.tagName)&&!a.hasAttribute('data-anzsearch')&&a.type!=='checkbox'&&a.type!=='file'){A3D_ANZ.pend=true;return false;}\n"
        "    A3D_ANZ.pend=false;\n"
        "    try{bimRenderInto(w,bimAwListHtml());bimAnzFilter(w);}   /* __acad3dV171c: one list, the workspace's */\n"
        "    catch(eA){console.warn('[BIM] Analyze panel',eA);}\n"
        "    return true;\n"
        "  }\n")
rep(A, "  function bimPropReveal(name){\n    var tb=bimPropTabOf(name);\n    A3D_PROP_GROUPS_OPEN[name]=true;\n",
       "  function bimPropReveal(name){\n    var tb=bimPropTabOf(name);\n    A3D_PROP_GROUPS_OPEN[name]=true;\n"
       "    if(A3D_AW.on)A3D_AW.props=true;   /* __acad3dV171c: in Analyze, the model's Properties, and a way back to the analysis above them */\n")

# ---- the list's box: its rows' buttons, the search, the site's part ----
L = 'js/engine/assets/library-drag.js'
rep(L, "    if(shell.dataset.tab==='analyze'&&!panel.querySelector('.a3d-analyze-wrap')){   /* __acad3dV141; __acad3dV162: the site analysis in it, one list */\n",
       "    if(shell.dataset.tab==='analyze'&&!panel.querySelector('.a3d-analyze-wrap')){   /* __acad3dV141; __acad3dV162: the site analysis in it, one list; __acad3dV171c: the workspace's */\n")
rep(L, "      abox.innerHTML=bimAnalyzeHtml();\n", "      abox.innerHTML=bimAwListHtml();\n")
rep(L, "      abox.addEventListener('click',function(ev){\n"
       "        var tg=ev.target&&ev.target.closest?ev.target.closest('[data-anztog]'):null;   /* __acad3dV148: a row opens and closes */\n"
       "        if(tg){bimAnzToggle(tg.getAttribute('data-anztog'));return;}\n"
       "        var b=",
       "      abox.addEventListener('click',function(ev){\n"
       "        var b=")
rep(L, "      bimSaWire(abox);   /* __acad3dV158 */\n      bimAnzWireFields(abox);   /* __acad3dV166b */\n", "      bimSaWire(abox);   /* __acad3dV158 */\n")
# ---- Properties: Analyze's panel while nothing is selected, or a pick was made since the selection ----
F = 'js/engine/site-analysis/panel.js'
rep(F, "    if(!el.propsbody)return;\n    var o=objById(A3D.sel);\n    var gP=o?null:bimSelectedGrid();   /* __acad3dV98 */\n",
       "    if(!el.propsbody)return;\n"
       "    if(bimAwOwns()){bimAwRender();return;}   /* __acad3dV171b: the one analysis; __acad3dV171c: or what was picked */\n"
       "    var o=objById(A3D.sel);\n    var gP=o?null:bimSelectedGrid();   /* __acad3dV98 */\n")
rep(F, "      if(A3D_AW.on){bimRenderInto(el.propsbody,bimAwPanelHtml());return;}   /* __acad3dV171b: the one analysis */\n", "")
P = 'js/engine/structure/analysis-properties.js'
between(P, "  /* __acad3dV166b: the settings in a row change the model at once, so the list is drawn again with the\n",
        "  /* SUPPORT and LOAD: Properties, opened at the field they name */\n", "")

# ---- the categories: their bodies on the right now ----
S = 'js/engine/site-analysis/panel.js'
between(S, "  function bimSaCatHtml(c,i,C){\n", "  /* __acad3dV162: Location's data: where the site is, and its context (V133) */\n", "")
between(S, "  function bimSaWire(w){\n", "  function bimSaAct(a){\n",
        "  /* the site's part of Analyze's list: its buttons, and Enter in the address runs it. __acad3dV171c: a category's\n"
        "     buttons and the zoning's fields are on the right (bimAwWire) */\n"
        "  function bimSaWire(w){\n"
        "    w.addEventListener('click',function(ev){\n"
        "      var b=ev.target&&ev.target.closest?ev.target.closest('[data-saact]'):null;\n"
        "      if(!b||b.disabled)return;\n"
        "      try{bimSaAct(b.getAttribute('data-saact'));}catch(eS){console.warn('[BIM] Site analysis',eS);a3dToast('That did not work - see the console');}\n"
        "    });\n"
        "    /* __acad3dV164: Enter in the address runs it */\n"
        "    w.addEventListener('keydown',function(ev){\n"
        "      var e=ev.target;\n"
        "      if(ev.key!=='Enter'||!e||!e.getAttribute||!e.getAttribute('data-saaddr'))return;\n"
        "      ev.preventDefault();\n"
        "      try{bimSaAct('analyze');}catch(eS){console.warn('[BIM] Site analysis',eS);a3dToast('That did not work - see the console');}\n"
        "    });\n"
        "  }\n")
rep(S, "  /* __acad3dV162: the site analysis is in Analyze's one list; its refresh is that list's */\n  function bimSaRefresh(force){return bimAnalyzeRefresh(force);}\n",
       "  /* __acad3dV162: the site analysis is in Analyze's one list; its refresh is that list's. __acad3dV171c: and the right's,\n"
       "     which shows a category's data as it arrives, and the run's steps */\n"
       "  function bimSaRefresh(force){var r=bimAnalyzeRefresh(force);if(A3D_AW.on)refreshProps();return r;}\n")
W = 'js/engine/site-analysis/workspace.js'
between(W, "  var A3D_SA={open:", "  function bimSaPair(L,k){", "")

# ---- Analyze site: its steps in the overview; an analysis's row, its state ----
G = 'js/engine/site-analysis/analyze-site.js'
rep(G, "    for(i=0;i<s.length;i++)if(s[i].id===id){s[i].state=state;s[i].text=String(text==null?'':text).slice(0,400);}\n    bimAnalyzeRefresh(true);\n",
       "    for(i=0;i<s.length;i++)if(s[i].id===id){s[i].state=state;s[i].text=String(text==null?'':text).slice(0,400);}\n    bimSaRefresh(true);   /* __acad3dV171c: the list's line and the overview's steps */\n")
between(G, "  /* the top of Analyze: where the site is, the button, and what the last run brought */\n",
        "  /* ---- each analysis drawn in the model, a row in its category ---- */\n", "")
between(G, "  function bimDgLegendHtml(rows){\n", "  function bimDgCards(){\n",
        "  /* __acad3dV171c: a row of the list, with its state; its key, its note, its source and its buttons are its panel's\n"
        "     (bimAwAnHtml) */\n")
rep(G, "      var R=D.runs[A.id],L=bimDgDiags(A.id),ly=bimLayerById(D.layers[A.id]),on=!!(ly&&bimLayerEff(ly).on),ed=L.filter(bimDgEdited).length;\n",
       "      var R=D.runs[A.id],L=bimDgDiags(A.id),on=bimAwShown(A.id),ed=L.filter(bimDgEdited).length;\n")
rep(G, "      var SC=R?bimDgStdChanged(A.id):{run:[],data:[]},stale=!!(SC.run.length||SC.data.length),sx=bimDgStdText(A.id);\n",
       "      var SC=R?bimDgStdChanged(A.id):{run:[],data:[]},stale=!!(SC.run.length||SC.data.length);\n")
rep(G, "      if(stale)st+='. Out of date: '+(SC.run.length?bimStdChangedText(SC.run)+' since it ran: Run again':'')+(SC.run.length&&SC.data.length?'; ':'')+(SC.data.length?bimStdChangedText(SC.data)+' since '+BIM_STD_DATA[SC.kind].name+' was fetched: Analyze site again':'');\n",
       "      if(stale)st+='. '+bimDgStaleText(SC);\n")
rep(G, "  function bimDgCards(){\n",
       "  /* __acad3dV167: what changed since an analysis ran, and what brings it up to date; __acad3dV171c: its row and its panel say it */\n"
       "  function bimDgStaleText(SC){\n"
       "    return 'Out of date: '+(SC.run.length?bimStdChangedText(SC.run)+' since it ran: Run again':'')+(SC.run.length&&SC.data.length?'; ':'')+\n"
       "      (SC.data.length?bimStdChangedText(SC.data)+' since '+BIM_STD_DATA[SC.kind].name+' was fetched: Analyze site again':'');\n"
       "  }\n"
       "  function bimDgCards(){\n")
between(G, "      var card={id:'dg'+A.id,title:A.name,state:", "      return A.id==='traffic'?bimTrCard(card):card;",
        "      var card={id:'dg'+A.id,title:A.name,state:!R?null:(stale?'stale':(L.length?(on?'on':'off'):'warn')),status:st};\n")
rep(G, "    var i=v.indexOf(':'),c=v.slice(0,i),a=v.slice(i+1),D=bimDgState(),L,ly;\n", "    var i=v.indexOf(':'),c=v.slice(0,i),a=v.slice(i+1),L;\n")
between(G, "    if(c==='show'){\n", "    return false;\n  }\n", "")

R = 'js/engine/simulation/traffic-ui.js'
between(R, "  /* the card V164 makes for the analysis, with the simulation's own part */\n", "  /* ---- Run: the elements, from the plan and the run so far ---- */\n",
        "  /* the row V164 makes for the analysis, with the simulation's state; its settings are in its panel (V171c) */\n"
        "  function bimTrCard(card){\n"
        "    var s=bimTrSettings();\n"
        "    card.status=(s.on?(A3D_TR.run?'Playing: ':'On: Play to run it. '):'')+card.status;\n"
        "    if(s.on&&card.state!=='stale')card.state=A3D_TR.run?'on':(card.state||'on');\n"
        "    return card;\n"
        "  }\n")

# ---- what an analysis is drawn in is kept with it: for the map under it outside Analyze; what moves follows Analyze's ground ----
rep('js/engine/site-analysis/movement-analyses.js',
    "  function bimMvLight(){var L=bimAwLook();if(L)return L.light;var s=bimMapSettings().style;return s==='street'||s==='custom';}   /* __acad3dV171b: the workspace's ground is the mode's */\n",
    "  /* __acad3dV171c: the colours an analysis is drawn in are kept with its elements: those for the map under them outside\n"
    "     Analyze, now that every run is inside it; what moves is drawn live, on Analyze's ground in its mode (bimTrLight) */\n"
    "  function bimMvLight(){var s=bimMapSettings().style;return s==='street'||s==='custom';}\n")
rep('js/engine/simulation/traffic-draw.js', "  function bimTrDraw(ctx,V,W,H){\n",
    "  /* __acad3dV171b: the cars and walkers on Analyze's ground take its mode's colours, elsewhere the map's */\n"
    "  function bimTrLight(){var L=bimAwLook();return L?L.light:bimMvLight();}\n"
    "  function bimTrDraw(ctx,V,W,H){\n")
rep('js/engine/simulation/traffic-draw.js', "    var K=bimMvLight()?BIM_TR_COL.lt:BIM_TR_COL.dk,", "    var K=bimTrLight()?BIM_TR_COL.lt:BIM_TR_COL.dk,")
M = 'js/engine/commands/command-map.js'
rep(M, "    traffic:function(){if(bimTrCommand(true))bimAwTraffic();else{bimAnzView();bimSaGoto('access');}},   /* __acad3dV171; __acad3dV171b: in focus in the workspace */",
       "    traffic:function(){if(bimTrCommand(true))bimAwTraffic();else bimSaGoto('access');},   /* __acad3dV171; __acad3dV171b: in focus in the workspace */")

# ---- the suite's hooks ----
H = 'js/engine/testing/hooks-workspace.js'
rep(H, "  window.__a3dAw=function(){var S=bimAwState(),L=bimAwLook();\n"
       "    return {on:!!A3D_AW.on,focus:S.focus,add:S.add.slice(),now:bimAwFocusNow(),look:L?(L.light?'light':'dark'):null,bg:bimAwBgHex(),\n",
       "  window.__acad3dV171c='oneanalyze,tab,tableave,prevtab,list,categories,rows,findcount,redflag,overview,category,findings,analyses,"
       "catdata,seealso,analysis,itfound,answers,card,cardacts,props,back,search,phone,fold,noanztog,noshow';\n"
       "  window.__a3dAw=function(){var S=bimAwState(),L=bimAwLook(),pk=A3D_AW.pick,sh=document.getElementById('a3d-shell'),pn=el.propsbody?el.propsbody.querySelector('[data-awpanel]'):null;\n"
       "    return {on:!!A3D_AW.on,focus:S.focus,add:S.add.slice(),now:bimAwFocusNow(),look:L?(L.light?'light':'dark'):null,bg:bimAwBgHex(),\n"
       "      pick:pk?pk.k+':'+pk.id:null,props:!!A3D_AW.props,prev:A3D_AW.prev,tab:sh?sh.getAttribute('data-tab'):null,panel:pn?pn.getAttribute('data-awpanel'):null,pend:!!A3D_AW.pend,\n")
rep(H, "  window.__a3dAwMvLight=function(){return bimMvLight();};\n", "  window.__a3dAwMvLight=function(){return bimTrLight();};\n")
rep(H, "  window.__a3dAwGroups=function(){return BIM_AW_GROUPS.map(function(G){return {id:G.id,name:G.name,an:G.an.slice()};});};\n",
       "  window.__a3dAwPick=function(k,id){return bimAwPick(k,id);};   /* __acad3dV171c */\n"
       "  window.__a3dAwFinds=function(a){return (BIM_AW_FINDS[a]||[]).slice();};\n")
rep(H, "    var S=bimAwState();S.focus=null;S.add=[];\n",
       "    var S=bimAwState();S.focus=null;   /* __acad3dV171c: the ticks as the layers show them, so a tick hides one */\n"
       "    S.add=BIM_DG_AN.filter(function(A){return !!bimLayerById(D.layers[A.id])&&!!D.runs[A.id]&&!A.hidden;}).map(function(A){return A.id;});\n")
C = 'js/engine/testing/hooks-commands-site.js'
rep(C, "  window.__a3dAnzToggle=function(id,on){return bimAnzToggle(id,on);};\n", "")
between(C, "  window.__a3dAnzOpenAll=function(on){", "  window.__a3dAnzSearch=function(q){\n", "")

# ---- the look of the list and the panel ----
K = 'css/site-analysis/workspace.css'
rep(K, ".a3d-awbar-x:focus-visible,.a3d-awbar-d:focus-visible,.a3d-awchip:focus-visible,.a3d-awl-nm:focus-visible,.a3d-awl-back:focus-visible{outline:2px solid #4ea1ff;outline-offset:1px}",
       ".a3d-awbar-x:focus-visible,.a3d-awbar-d:focus-visible,.a3d-awchip:focus-visible,.a3d-awl-nm:focus-visible,.a3d-awl-cat:focus-visible,.a3d-awl-lk:focus-visible,"
       ".a3d-awp-cat:focus-visible,.a3d-awp-an:focus-visible,.a3d-awp-flag:focus-visible{outline:2px solid #4ea1ff;outline-offset:1px}")
between(K, "/* the left: the analyses */\n", "/* the right: the one analysis */\n",
        "/* the left: __acad3dV171c, Analyze's one list: the site, Overview, the ten categories with their analyses, the model's */\n"
        ".a3d-awl{padding:6px 8px 18px;font-size:12.5px}\n"
        ".a3d-awl-hd{display:flex;align-items:baseline;justify-content:space-between;gap:8px;margin:2px 2px 8px}\n"
        ".a3d-awl-ttl{font-weight:650;font-size:14px}\n"
        ".a3d-awl-site{display:flex;flex-direction:column;gap:6px;margin:8px 0 8px;padding:10px;border-radius:9px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08)}\n"
        ".a3d-awl-place{font-size:12px;font-weight:500;line-height:1.35;overflow-wrap:anywhere}\n"
        ".a3d-awl-addr{display:block;width:100%;box-sizing:border-box;background:#1f2327;border:1px solid #3a4048;border-radius:6px;color:#e6eaef;padding:4px 8px;min-height:30px;font:inherit;font-size:12.5px}\n"
        ".a3d-awl-addr:focus{border-color:#4ea1ff;outline:0}\n"
        ".a3d-awl-bd,.a3d-awl-run{font-size:11.5px;color:#8a96a3;line-height:1.4}\n"
        ".a3d-awl-lk{border:0;background:transparent;color:#4ea1ff;font:inherit;padding:0;cursor:pointer}\n"
        ".a3d-awl-lk:hover{text-decoration:underline}\n"
        ".a3d-awl .a3d-awl-go{min-height:32px;font-size:12.5px;font-weight:600}\n"
        ".a3d-awl-grp{margin-top:4px}\n"
        ".a3d-awl-grp,.a3d-awl-row{scroll-margin-top:44px}\n"
        ".a3d-awl-grphd{font-size:10.5px;font-weight:650;letter-spacing:.07em;text-transform:uppercase;color:#8a96a3;margin:12px 6px 3px}\n"
        ".a3d-awl-cat{display:flex;align-items:center;gap:8px;width:100%;min-height:34px;padding:0 8px 0 4px;border:0;border-radius:7px;background:transparent;color:inherit;\n"
        "  font:inherit;font-weight:600;text-align:left;cursor:pointer}\n"
        ".a3d-awl-cat:hover,.a3d-awl-row:hover{background:rgba(255,255,255,.045)}\n"
        ".a3d-awl-no{flex:0 0 20px;font-size:11px;color:#8a96a3;text-align:center;font-variant-numeric:tabular-nums}\n"
        ".a3d-awl-cn{flex:1 1 auto;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}\n"
        ".a3d-awl-fn{flex:0 0 auto;font-size:11px;font-weight:500;color:#8a96a3;font-variant-numeric:tabular-nums}\n"
        ".a3d-awl-rf{flex:0 0 auto;min-width:16px;height:16px;padding:0 4px;box-sizing:border-box;border-radius:8px;background:#e5484d;color:#fff;font-size:10.5px;font-weight:650;line-height:16px;text-align:center}\n"
        ".a3d-awl-row{display:flex;align-items:center;gap:8px;min-height:30px;padding:0 8px 0 32px;border-radius:7px}\n"
        ".a3d-awl-tick{flex:0 0 auto;margin:0;width:14px;height:14px;accent-color:#4ea1ff;cursor:pointer}\n"
        ".a3d-awl-sw{flex:0 0 auto;width:10px;height:10px;border-radius:3px}\n"
        ".a3d-awl-dot{flex:0 0 auto;width:8px;height:8px;margin:0 21px 0 3px;box-sizing:border-box;border-radius:50%;border:1.5px solid #6b7280}\n"
        ".a3d-awl-nm{flex:1 1 auto;min-width:0;border:0;background:transparent;color:inherit;font:inherit;text-align:left;padding:6px 0;cursor:pointer;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}\n"
        ".a3d-awl-st{flex:0 0 auto;font-size:10.5px;color:#8a96a3;white-space:nowrap}\n"
        "button.a3d-awl-row{width:100%;border:0;background:transparent;color:inherit;font:inherit;cursor:pointer;text-align:left;justify-content:space-between}\n"
        ".a3d-awl-ov{padding-left:8px;font-weight:600}\n"
        ".a3d-awl-ov .a3d-awl-nm{flex:0 0 auto}\n"
        ".a3d-awl-ov .a3d-awl-st{min-width:0;overflow:hidden;text-overflow:ellipsis}\n"
        ".a3d-awl-row.pick,.a3d-awl-cat.pick,.a3d-awl-row.pick:hover,.a3d-awl-cat.pick:hover{background:#e8edf2;color:#111418}\n"
        ".a3d-awl-row.pick .a3d-awl-st,.a3d-awl-cat.pick .a3d-awl-no,.a3d-awl-cat.pick .a3d-awl-fn{color:#4b5563}\n"
        ".a3d-awl-row.focus .a3d-awl-nm,.a3d-awl-row.add .a3d-awl-nm{font-weight:600}\n"
        ".a3d-awl-row.focus:not(.pick){box-shadow:inset 3px 0 0 #4ea1ff}\n"
        ".a3d-awl-row.none .a3d-awl-nm,.a3d-awl-row.none .a3d-awl-sw{opacity:.45}\n"
        ".a3d-awl-row.stale .a3d-awl-st{color:#e0a43a}\n"
        "@media(pointer:coarse){.a3d-awl-cat,.a3d-awl-row{min-height:44px}.a3d-awl-addr{min-height:38px;font-size:16px}.a3d-awl .a3d-awl-go{min-height:40px}}\n"
        "body.light-theme .a3d-awl,body.light-theme .a3d-awp{color:#1f2328}\n"
        "body.light-theme .a3d-awl-site{background:rgba(0,0,0,.03);border-color:rgba(0,0,0,.08)}\n"
        "body.light-theme .a3d-awl-addr{background:#fff;border-color:#c9ced4;color:#222}\n"
        "body.light-theme .a3d-awl-bd,body.light-theme .a3d-awl-run,body.light-theme .a3d-awl-grphd,body.light-theme .a3d-awl-no,body.light-theme .a3d-awl-fn,body.light-theme .a3d-awl-st{color:#6b7280}\n"
        "body.light-theme .a3d-awl-lk{color:#1f5fa8}\n"
        "body.light-theme .a3d-awl-cat:hover,body.light-theme .a3d-awl-row:hover{background:rgba(0,0,0,.04)}\n"
        "body.light-theme .a3d-awl-row.pick,body.light-theme .a3d-awl-cat.pick,body.light-theme .a3d-awl-row.pick:hover,body.light-theme .a3d-awl-cat.pick:hover{background:#1f2328;color:#fff}\n"
        "body.light-theme .a3d-awl-row.pick .a3d-awl-st,body.light-theme .a3d-awl-cat.pick .a3d-awl-no,body.light-theme .a3d-awl-cat.pick .a3d-awl-fn{color:#c9ced4}\n"
        "body.light-theme .a3d-awl-row.focus:not(.pick){box-shadow:inset 3px 0 0 #1f5fa8}\n"
        "body.light-theme .a3d-awl-row.stale .a3d-awl-st{color:#9a5b00}\n")
rep(K, "/* an analysis's row in Analyze: its name keeps room beside a long first button (Traffic's \"Stop the simulation\") */\n"
       ".a3d-anzhd>.a3d-anzbtn{flex:0 1 auto;min-width:0;overflow:hidden;text-overflow:ellipsis}\n",
       "/* __acad3dV171c: what is picked: a category's number, the red flags, the categories, a category's analyses, the way back */\n"
       ".a3d-awp-no{flex:0 0 auto;min-width:26px;height:26px;padding:0 6px;box-sizing:border-box;border-radius:7px;background:rgba(255,255,255,.08);font-weight:650;font-size:13px;line-height:26px;text-align:center}\n"
       ".a3d-awp-flags,.a3d-awp-cats,.a3d-awp-ans{display:flex;flex-direction:column;gap:2px}\n"
       ".a3d-awp-flag{display:flex;gap:6px;align-items:baseline;text-align:left;border:0;border-left:3px solid #e5484d;background:rgba(229,72,77,.1);color:inherit;font:inherit;font-size:12px;\n"
       "  line-height:1.4;padding:6px 8px;border-radius:0 7px 7px 0;cursor:pointer}\n"
       ".a3d-awp-cat{display:grid;grid-template-columns:22px 1fr;column-gap:4px;text-align:left;border:0;background:transparent;color:inherit;font:inherit;padding:5px 6px;border-radius:7px;cursor:pointer}\n"
       ".a3d-awp-catno{grid-row:1 / 3;font-size:11px;color:#8a96a3;font-variant-numeric:tabular-nums;padding-top:2px}\n"
       ".a3d-awp-catn{font-weight:500}\n"
       ".a3d-awp-catf{font-size:11px;color:#8a96a3}\n"
       ".a3d-awp-catf.rf{color:#ef8a8d}\n"
       ".a3d-awp-an{display:flex;align-items:center;gap:8px;min-width:0;text-align:left;border:0;background:transparent;color:inherit;font:inherit;padding:6px;border-radius:7px;cursor:pointer}\n"
       ".a3d-awp-an i{flex:0 0 auto;width:10px;height:10px;border-radius:3px}\n"
       ".a3d-awp-an i.o{width:8px;height:8px;box-sizing:border-box;border-radius:50%;border:1.5px solid #6b7280;margin:0 1px}\n"
       ".a3d-awp-ann{flex:1 1 auto;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}\n"
       ".a3d-awp-anst{flex:0 0 auto;font-size:11px;color:#8a96a3}\n"
       ".a3d-awp-an:disabled{opacity:.5;cursor:default}\n"
       ".a3d-awp-cat:hover,.a3d-awp-an:hover{background:rgba(255,255,255,.05)}\n"
       ".a3d-awp-an:disabled:hover{background:transparent}\n"
       ".a3d-awp-in{margin:14px 0 0;font-size:11.5px;color:#8a96a3}\n"
       ".a3d-awp .a3d-awp-stale{color:#e0a43a}\n"
       "body.light-theme .a3d-awp .a3d-awp-stale{color:#9a5b00}\n"
       ".a3d-awp-backrow{margin:2px 0 10px}\n"
       ".a3d-awp .a3d-safind{margin-bottom:8px}\n"
       ".a3d-awp .a3d-clsec{margin-top:16px}\n"
       ".a3d-awp .a3d-salink{margin-top:12px}\n"
       "body.light-theme .a3d-awp-no{background:rgba(0,0,0,.06)}\n"
       "body.light-theme .a3d-awp-flag{background:rgba(229,72,77,.08)}\n"
       "body.light-theme .a3d-awp-catno,body.light-theme .a3d-awp-catf,body.light-theme .a3d-awp-anst,body.light-theme .a3d-awp-in{color:#6b7280}\n"
       "body.light-theme .a3d-awp-catf.rf{color:#b42318}\n"
       "body.light-theme .a3d-awp-cat:hover,body.light-theme .a3d-awp-an:hover{background:rgba(0,0,0,.04)}\n")

# ---- the hub's rules nothing draws now (V120 reads them as dead) ----
DEAD = [
    ('css/panels/properties-analyze.css', '.a3d-anzhead{display:flex;align-items:baseline;justify-content:space-between;gap:8px;margin:2px 2px 8px}'),
    ('css/panels/properties-analyze.css', '.a3d-anzttl0{font-weight:650;font-size:13px}'),
    ('css/panels/properties-analyze.css', '.a3d-anzgrphd{font-size:11px;font-weight:600;color:#8a96a3;padding:12px 4px 4px}'),
    ('css/panels/properties-analyze.css', '.a3d-anzlist{display:flex;flex-direction:column;gap:1px}'),
    ('css/panels/properties-analyze.css', '.a3d-anzcard{border-radius:7px;min-width:0}'),
    ('css/panels/properties-analyze.css', '.a3d-anzcard.open{background:rgba(255,255,255,.035)}'),
    ('css/panels/properties-analyze.css', '.a3d-anzhd{display:flex;align-items:center;gap:6px;min-height:36px;padding:0 4px 0 0;border-radius:7px;min-width:0}'),
    ('css/panels/properties-analyze.css', '.a3d-anzhd:hover{background:rgba(255,255,255,.045)}'),
    ('css/panels/properties-analyze.css', '.a3d-anztog{flex:1 1 auto;min-width:0;display:flex;align-items:center;gap:4px;background:transparent;border:0;padding:4px 0 4px 2px;margin:0;color:inherit;font:inherit;text-align:left;cursor:pointer}'),
    ('css/panels/properties-analyze.css', '.a3d-anztog:focus-visible{outline:2px solid #4ea1ff;outline-offset:-2px;border-radius:6px}'),
    ('css/panels/properties-analyze.css', '.a3d-anzchev{flex:0 0 16px;width:16px;height:16px;display:grid;place-items:center;color:#8b949e;transition:transform .12s}'),
    ('css/panels/properties-analyze.css', '.a3d-anzcard.open>.a3d-anzhd .a3d-anzchev{transform:rotate(90deg)}   /* __acad3dV162: its own, not a row inside it */'),
    ('css/panels/properties-analyze.css', '.a3d-anzname{display:flex;flex-direction:column;min-width:0;flex:1 1 auto}'),
    ('css/panels/properties-analyze.css', '.a3d-anzttl{font-weight:500;font-size:12.5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}'),
    ('css/panels/properties-analyze.css', '.a3d-anzsum{font-size:11px;color:#8a96a3;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-top:1px}'),
    ('css/panels/properties-analyze.css', '.a3d-anzcard.open>.a3d-anzhd .a3d-anzsum{display:none}'),
    ('css/panels/properties-analyze.css', '.a3d-anzbody{display:none;padding:0 8px 10px 22px}'),
    ('css/panels/properties-analyze.css', '.a3d-anzcard.open>.a3d-anzbody{display:block}'),
    ('css/panels/properties-analyze.css', '.a3d-anzst{color:#aab4bf;font-size:12px;margin:0 0 8px;line-height:1.4}'),
    ('css/panels/properties-analyze.css', '.a3d-anzacts{display:flex;flex-wrap:wrap;gap:5px}'),
    ('css/panels/properties-analyze.css', '.a3d-anzhd{min-height:46px}'),
    ('css/panels/properties-analyze.css', '.a3d-anztog{padding:6px 0 6px 2px}'),
    ('css/panels/properties-analyze.css', '.a3d-anzttl{font-size:13.5px}'),
    ('css/panels/properties-analyze.css', '.a3d-anzsum{font-size:12px}'),
    ('css/panels/properties-analyze.css', '.a3d-anzchev{flex-basis:22px;width:22px}'),
    ('css/panels/properties-analyze.css', 'body.light-theme .a3d-anzcard.open{background:rgba(0,0,0,.035)}'),
    ('css/panels/properties-analyze.css', 'body.light-theme .a3d-anzhd:hover{background:rgba(0,0,0,.04)}'),
    ('css/panels/properties-analyze.css', 'body.light-theme .a3d-anzst{color:#555}'),
    ('css/site-analysis/boards.css', '.a3d-sarun{border-top:0;padding-top:2px}'),
    ('css/site-analysis/boards.css', '.a3d-sarun .a3d-sago{min-height:30px;padding:0 14px;font-size:12.5px;font-weight:600}'),
    ('css/site-analysis/boards.css', '.a3d-sarun .a3d-saval .a3d-anzbtn{margin:2px 4px 2px 0}'),
    ('css/site-analysis/boards.css', '.a3d-sasteps{list-style:none;margin:8px 0 0;padding:0;display:flex;flex-direction:column;gap:5px}'),
    ('css/site-analysis/boards.css', '.a3d-sastep{display:grid;grid-template-columns:10px minmax(0,1fr) auto;column-gap:7px;align-items:center;font-size:12px;line-height:1.35;color:#d5dae0}'),
    ('css/site-analysis/boards.css', '.a3d-sastepic{width:8px;height:8px;border-radius:50%;box-sizing:border-box;border:1px solid #6b7785}'),
    ('css/site-analysis/boards.css', '.a3d-sastep.s-ok .a3d-sastepic{background:#30a46c;border-color:#30a46c}'),
    ('css/site-analysis/boards.css', '.a3d-sastep.s-fail .a3d-sastepic{background:#e5484d;border-color:#e5484d}'),
    ('css/site-analysis/boards.css', '.a3d-sastep.s-busy .a3d-sastepic{background:#f5a524;border-color:#f5a524;animation:a3d-sapulse .8s ease-in-out infinite alternate}'),
    ('css/site-analysis/boards.css', '.a3d-sastep.s-part .a3d-sastepic{background:#f5a524;border-color:#f5a524}'),
    ('css/site-analysis/boards.css', '.a3d-sastep.s-skip .a3d-sastepic{background:#6b7785}'),
    ('css/site-analysis/boards.css', '.a3d-sastepst{font-size:10.5px;color:#8a96a3;white-space:nowrap}'),
    ('css/site-analysis/boards.css', '.a3d-sastep.s-fail .a3d-sastepst{color:#ef8a8d}'),
    ('css/site-analysis/boards.css', '.a3d-sastep.s-part .a3d-sastepst{color:#f5b54a}'),
    ('css/site-analysis/boards.css', '.a3d-sastept{grid-column:2/4;font-size:11px;color:#8a96a3;overflow-wrap:anywhere}'),
    ('css/site-analysis/boards.css', '@keyframes a3d-sapulse{from{opacity:.35}to{opacity:1}}'),
    ('css/site-analysis/boards.css', '@media (prefers-reduced-motion:reduce){.a3d-sastep.s-busy .a3d-sastepic{animation:none}}'),
    ('css/site-analysis/boards.css', '.a3d-dgleg{display:flex;flex-wrap:wrap;gap:4px 10px;margin:4px 0 4px;font-size:11px;color:#c9d1d9}'),
    ('css/site-analysis/boards.css', '.a3d-dglegi{display:inline-flex;align-items:center;gap:5px}'),
    ('css/site-analysis/boards.css', '.a3d-dglegi i{display:inline-block;width:12px;height:8px;border-radius:2px;flex:none}'),
    ('css/site-analysis/boards.css', '.a3d-dglegi i.k-line,.a3d-dglegi i.k-dash{height:0;border-radius:0;border-top:2px solid currentColor}'),
    ('css/site-analysis/boards.css', '.a3d-dglegi i.k-dash{border-top-style:dashed}'),
    ('css/site-analysis/boards.css', '.a3d-dglegi i.k-dot{width:8px;height:8px;border-radius:50%}'),
    ('css/site-analysis/boards.css', '.a3d-sasec{border-top:1px solid rgba(255,255,255,.08);padding:8px 2px 10px}'),
    ('css/site-analysis/boards.css', '.a3d-sarow{display:flex;align-items:center;gap:8px;margin:0 0 6px;font-size:12px}'),
    ('css/site-analysis/boards.css', '.a3d-sarow>label,.a3d-sarow>.a3d-salab{flex:0 0 74px;color:#8a96a3;font-size:11.5px}'),
    ('css/site-analysis/boards.css', '.a3d-sarow>select,.a3d-sarow>input,.a3d-sarow>textarea,.a3d-sarow>.a3d-saval{flex:1 1 auto;min-width:0}'),
    ('css/site-analysis/boards.css', '.a3d-saval{color:#d5dae0;font-size:12px;line-height:1.35}'),
    ('css/site-analysis/boards.css', '.a3d-saflags{margin:0 0 6px;padding:7px 9px;border-radius:7px;background:rgba(229,72,77,.12);border:1px solid rgba(229,72,77,.35)}'),
    ('css/site-analysis/boards.css', '.a3d-saflags .a3d-sasechd{color:#ef9a9a;margin-bottom:4px}'),
    ('css/site-analysis/boards.css', '.a3d-saflag{font-size:12px;color:#f3c4c4;margin:2px 0}'),
    ('css/site-analysis/boards.css', '.a3d-sacat>.a3d-anzbody{padding-left:20px}'),
    ('css/site-analysis/boards.css', '.a3d-anz.q .a3d-sacat.qhit>.a3d-anzbody{display:block}'),
    ('css/site-analysis/boards.css', '.a3d-anz.q .a3d-sacat.qhit>.a3d-anzhd .a3d-anzchev{transform:rotate(90deg)}'),
    ('css/site-analysis/boards.css', '.a3d-anz.q .a3d-sacat.qhit>.a3d-anzhd .a3d-anzsum{display:none}'),
    ('css/site-analysis/boards.css', '.a3d-satools{margin:0 -4px 4px;padding:2px 0;border-radius:7px}'),
    ('css/site-analysis/boards.css', '.a3d-satools .a3d-anzbody{padding-left:22px}'),
    ('css/workspace/components.css', '.a3d-sacat{scroll-margin-top:44px}'),
    ('css/workspace/components.css', '.a3d-saq{color:#8a96a3;font-size:11.5px;margin:0 0 8px;line-height:1.4}'),
    ('css/workspace/components.css', '.a3d-sachkhd{font-size:11px;color:#8a96a3;margin:8px 0 4px}'),
    ('css/workspace/components.css', '.a3d-sanote{font-size:11.5px;color:#8a96a3;margin:0 0 6px;line-height:1.4}'),
    ('css/workspace/components.css', '.a3d-sarun .a3d-sago{min-height:40px}'),
    ('css/workspace/components.css', 'body.light-theme .a3d-sasec{border-top-color:rgba(0,0,0,.08)}'),
    ('css/workspace/components.css', 'body.light-theme .a3d-saflags{background:rgba(229,72,77,.08)}'),
    ('css/workspace/components.css', 'body.light-theme .a3d-saflag{color:#9b1c20}'),
    ('css/site-analysis/boards.css', '/* __acad3dV162: a category holds its analyses, its data and its findings; a search opens what it finds */'),
]
for f_, l_ in DEAD:
    rep(f_, l_ + '\n', '')
rep('css/site-analysis/boards.css', "/* __acad3dV164: Analyze site, what each source brought, and the analyses' legends */\n",
    "/* __acad3dV164: a category's data. __acad3dV171c: Analyze site's steps are in the overview, each analysis's key in its panel */\n")
rep('css/workspace/components.css', "body.light-theme .a3d-saval,body.light-theme .a3d-safv,body.light-theme .a3d-sastep,body.light-theme .a3d-dgleg{color:#333}",
    "body.light-theme .a3d-safv{color:#333}")
rep('css/workspace/components.css', "body.light-theme .a3d-sastept,body.light-theme .a3d-sastepst,body.light-theme .a3d-saq,body.light-theme .a3d-safm,body.light-theme .a3d-sanote,body.light-theme .a3d-sasechd,body.light-theme .a3d-sachkhd,body.light-theme .a3d-sarow>label,body.light-theme .a3d-sarow>.a3d-salab{color:#6b737c}",
    "body.light-theme .a3d-safm,body.light-theme .a3d-sasechd{color:#6b737c}")
rep('css/panels/properties-analyze.css', "body.light-theme .a3d-anzsum,body.light-theme .a3d-anzgrphd,body.light-theme .a3d-anzcount{color:#6b737c}",
    "body.light-theme .a3d-anzcount{color:#6b737c}")
rep('css/panels/properties-analyze.css', "/* __acad3dV148: Analyze, a list of rows in four groups */",
    "/* __acad3dV148: Analyze, a list of rows; __acad3dV171c: the workspace's, in site-analysis/workspace.css */")

done()
