"""patch_phase128d.py -- V128: the search's engine hooks, the type-anywhere test, and the marker.

window.__a3dCommandSearch / __a3dCommandRecent / __a3dCommandRun are what the command search (the
shell) draws and runs through; __a3dTypeAnywhere is the one answer to "may a letter typed on the
drawing open the search" -- not in a field, not while a tool takes points or options, a dialog is
open, a face is held, a gizmo value is typed, a sheet or a slideshow or the Start page is on
screen, or a drag is under way. __a3dDockSearch (V71's) now reads the one search."""
NAME = 'patch_phase128d.py'
BASE = '4d3a63ee56eda35a91c61c45da67df92fab37704faeab6dc79655c747c975bb5'
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
        sys.exit('ABORT: %d occurrences, expected %d: %r' % (c, n, old[:90]))
    t = t.replace(old, new)


rep("""  window.__a3dDockSearch=function(q){
    var sp=document.querySelector('#a3d-dock [data-dockpop="__search"]');
    if(!sp)return null;
    if(!sp.classList.contains('open')){
      var sb=document.getElementById('a3d-dsearch');
      if(sb)sb.click();
    }
    var n=bimRenderDockSearch(q);
    var res=document.getElementById('a3d-dsearchres');
    var acts=[],els=res?res.querySelectorAll('[data-a3dr]'):[],i;
    for(i=0;i<els.length;i++)acts.push(els[i].getAttribute('data-a3dr'));
    return {matches:n,shown:acts};
  };""", """  /* __acad3dV128: the dock's search is the command search -- what it matches, and the ribbon
     actions among the matches */
  window.__a3dDockSearch=function(q){
    var r=bimCmdSearch(q,0),acts=[],i;
    for(i=0;i<r.length;i++)if(r[i].act)acts.push(r[i].act);
    return {matches:r.length,shown:acts};
  };""")
rep("""  window.__a3dCmdSupported=function(act){return !!BIM_CMD_MAP[act];};""", """  window.__a3dCmdSupported=function(act){return !!BIM_CMD_MAP[act];};
  /* __acad3dV128: the command search */
  window.__a3dCommandSearch=function(q,limit){
    try{return bimCmdSearch(q,limit);}catch(eQ){console.warn('[BIM] The command search failed',eQ);return [];}
  };
  window.__a3dCommandRecent=function(k){
    try{return bimCmdRecent(k);}catch(eR){console.warn('[BIM] The recent commands could not be read',eR);return [];}
  };
  window.__a3dCommandRun=function(id){
    try{return bimCmdRun(id);}catch(eX){console.warn('[BIM] Command failed: '+id,eX);a3dToast('That command could not run');return false;}
  };
  window.__a3dCommandCatalog=function(){return bimCmdCatalog().map(function(it){return bimCmdPublic(it);});};
  window.__a3dRunAct=function(act){return bimRunAct(act)!==false;};
  window.__a3dCommandUsageClear=function(){try{localStorage.removeItem(BIM_CMD_USE_KEY);}catch(eC){}return true;};
  window.__a3dTypeAnywhere=function(ev){
    try{
      if(!A3D.on||!ev||ev.ctrlKey||ev.metaKey||ev.altKey||!/^[A-Za-z?]$/.test(ev.key||''))return false;
      if(bimKeyForControl(ev))return false;
      if(bimStartShowing()||bimSheetOnScreen()||A3D_SLIDESHOW.on||el.dlg)return false;
      if(A3D.sk||A3D.face||A3D.facePick||A3D.conPick||A3D.zoomWindow||A3D_TYPING.active||drag||bimTypingDrag())return false;
      if(document.getElementById('a3d-gizmenu'))return false;
      var rp=document.getElementById('a3d-rupop');if(rp&&rp.classList.contains('open'))return false;
      return true;
    }catch(eT){console.warn('[BIM] Type-anywhere check failed',eT);return false;}
  };
  window.__acad3dV128='commandcatalog,ribbonmerged,aliases,synonyms,keysfromsheet,ribbonplace,layeredmatch,fuzzy,typo,'+
    'keychordsearch,frequency,recent,unavailablereason,typeanywhere,tabcycle,shortcutmode,ariacombobox,docksearchunified,'+
    'ribbontooltips,shortcutsheetsearch';""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
