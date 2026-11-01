#!/usr/bin/env python3
"""V172e, storage phase A2: the Assets library and templates kept in IndexedDB when localStorage refuses them; the
browser asked to keep the app's storage at the first Save.

reference/research-local-storage.md, the owner's decisions D1 (phase A) and D3 (persist() on the first explicit Save,
never on load; false is normal). V172d kept a project too large for localStorage in the database; the library and
the templates were left on localStorage alone, so a SketchUp import of large blocks, or a template of a large project,
still met the 5.2-million-character wall. They go the same way now, into the same store under their own keys
('lib:family', 'tpl:<id>'; project ids start 'doc-'), so the database keeps its version 1 and no other tab is asked
to close. What fits stays where it was.

Run from the repository root: python3 Phase/patch_v172e.py
"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from p171 import begin, rep, done   # noqa: E402

begin('4d8ba4c09774e5eeb455711cb940d5096608b9a0049f5e7d867f5f9bf861c0d9')   # V172d

F = 'js/engine/assets/family-library.js'
# ---- 1. the library: a pointer in its key names the database's copy, read after start
rep(F, "  var A3D_FAMLIB=bimLoadFamilyLibrary();\n",
    "  /* __acad3dV172e: the library kept in the browser's database ('lib:family'), its pointer in its key; while it is\n"
    "     read, saves wait and are made with it */\n"
    "  var A3D_FAMLIB_IDB=false,A3D_FAMLIB_LOADING=false,A3D_FAMLIB_DIRTY=false;\n"
    "  var A3D_FAMLIB=bimLoadFamilyLibrary();\n")
rep(F, "      if(raw){var parsed=JSON.parse(raw);if(Array.isArray(parsed))return parsed;}\n",
    "      if(raw){\n"
    "        var parsed=JSON.parse(raw);\n"
    "        if(Array.isArray(parsed))return parsed;\n"
    "        if(parsed&&parsed.idb===1){A3D_FAMLIB_IDB=true;A3D_FAMLIB_LOADING=true;return [];}   /* __acad3dV172e */\n"
    "      }\n")
rep(F,
    "  function bimSaveFamilyLibrary(){\n"
    "    try{\n"
    "      localStorage.setItem(FAMILY_LIB_KEY,JSON.stringify(A3D_FAMLIB));\n"
    "      if(A3D_FAMLIB_SAVE_FAILED){A3D_FAMLIB_SAVE_FAILED=false;a3dToast('Saving the Assets library works again');}\n"
    "      return true;\n"
    "    }catch(eS){\n"
    "      console.warn('[BIM] Could not persist family library: ',eS);\n"
    "      if(!A3D_FAMLIB_SAVE_FAILED){\n"
    "        A3D_FAMLIB_SAVE_FAILED=true;\n"
    "        a3dToast('The Assets library could not be saved: browser storage is full. New assets will be lost when the page reloads; remove assets you no longer need.');\n"
    "      }\n"
    "      return false;\n"
    "    }\n"
    "  }\n",
    "  /* __acad3dV172e: a library localStorage refuses goes to the browser's database, its pointer written once the\n"
    "     copy has committed; a failure of both is the toast. Returns true when stored, null when the database's\n"
    "     answer is still to come (or the library is still being read), false when it failed. */\n"
    "  function bimSaveFamilyLibrary(){\n"
    "    if(A3D_FAMLIB_LOADING){A3D_FAMLIB_DIRTY=true;return null;}\n"
    "    var s=JSON.stringify(A3D_FAMLIB),n=A3D_FAMLIB.length;\n"
    "    function failed(eS){\n"
    "      console.warn('[BIM] Could not persist family library: ',eS);\n"
    "      if(!A3D_FAMLIB_SAVE_FAILED){\n"
    "        A3D_FAMLIB_SAVE_FAILED=true;\n"
    "        a3dToast('The Assets library could not be saved: browser storage is full. New assets will be lost when the page reloads; remove assets you no longer need.');\n"
    "      }\n"
    "    }\n"
    "    function worked(){if(A3D_FAMLIB_SAVE_FAILED){A3D_FAMLIB_SAVE_FAILED=false;a3dToast('Saving the Assets library works again');}}\n"
    "    if(!A3D_FAMLIB_IDB){\n"
    "      try{localStorage.setItem(FAMILY_LIB_KEY,s);worked();return true;}\n"
    "      catch(eL){console.warn('[BIM] The Assets library does not fit in browser storage; it goes to the browser\\'s database.',eL);}\n"
    "    }\n"
    "    if(typeof bimIdbPut!=='function'){failed(new Error('no browser database'));return false;}\n"
    "    bimIdbPut('lib:family',{rec:s,saved:Date.now(),v:1},function(err){\n"
    "      if(err){failed(err);return;}\n"
    "      if(!A3D_FAMLIB_IDB){\n"
    "        try{localStorage.setItem(FAMILY_LIB_KEY,JSON.stringify({idb:1,key:'lib:family',count:n}));A3D_FAMLIB_IDB=true;}\n"
    "        catch(eP){failed(eP);return;}\n"
    "      }\n"
    "      worked();\n"
    "    });\n"
    "    return null;\n"
    "  }\n"
    "  /* __acad3dV172e: the library in the database, read after start; anything added meanwhile is kept after it */\n"
    "  function bimLibBootLoad(){\n"
    "    bimIdbGet('lib:family',function(err,v){\n"
    "      var arr=null;\n"
    "      if(!err&&v&&typeof v.rec==='string'){\n"
    "        try{arr=JSON.parse(v.rec);}catch(eJ){console.warn('[BIM] The Assets library in the browser\\'s database is not valid JSON.',eJ);}\n"
    "      }\n"
    "      if(!Array.isArray(arr)){\n"
    "        if(err)console.warn('[BIM] The browser\\'s database could not be read.',err);\n"
    "        a3dToast('The Assets library is kept in the browser\\'s database, which could not be read: nothing is saved over it.');\n"
    "        return;\n"
    "      }\n"
    "      var added=A3D_FAMLIB.splice(0,A3D_FAMLIB.length);\n"
    "      Array.prototype.push.apply(A3D_FAMLIB,arr.concat(added));\n"
    "      A3D_FAMLIB_LOADING=false;\n"
    "      if(A3D_FAMLIB_DIRTY||added.length){A3D_FAMLIB_DIRTY=false;bimSaveFamilyLibrary();}\n"
    "      try{refreshFamilyPanel();}catch(eR){console.warn('[BIM] The Assets panel could not be refreshed.',eR);}\n"
    "    });\n"
    "  }\n")
rep(F, "  /* ================= __acad3dV124: the Assets library =================\n",
    "  if(A3D_FAMLIB_LOADING)setTimeout(bimLibBootLoad,0);   /* __acad3dV172e */\n"
    "  /* ================= __acad3dV124: the Assets library =================\n")
rep(F,
    "      try{localStorage.removeItem(A3D_TEMPLATE_PREFIX+id);}\n"
    "      catch(eR){console.warn('[BIM] A template\\'s stored project could not be removed.',eR);}\n",
    "      try{localStorage.removeItem(A3D_TEMPLATE_PREFIX+id);}\n"
    "      catch(eR){console.warn('[BIM] A template\\'s stored project could not be removed.',eR);}\n"
    "      if(A3D_FAMLIB[idx].idb)bimIdbDel('tpl:'+id,function(eD){if(eD)console.warn('[BIM] A template\\'s copy in the browser\\'s database could not be removed: '+id,eD);});   /* __acad3dV172e */\n")

T = 'js/engine/assets/templates.js'
# ---- 2. templates: a project localStorage refuses is kept in the database under 'tpl:<id>'
rep(T,
    "    try{localStorage.setItem(A3D_TEMPLATE_PREFIX+id,JSON.stringify(rec));}\n"
    "    catch(eS){\n"
    "      console.warn('[BIM] The template could not be stored.',eS);\n"
    "      a3dToast('The template could not be saved: browser storage is full');\n"
    "      return null;\n"
    "    }\n",
    "    /* __acad3dV172e: a template localStorage refuses is kept in the browser's database; the entry goes again if the\n"
    "       database refuses it too */\n"
    "    var s=JSON.stringify(rec),inIdb=false;\n"
    "    try{localStorage.setItem(A3D_TEMPLATE_PREFIX+id,s);}\n"
    "    catch(eS){\n"
    "      console.warn('[BIM] The template does not fit in browser storage; it goes to the browser\\'s database.',eS);\n"
    "      inIdb=true;\n"
    "    }\n")
rep(T,
    "    entry.thumb=bimRecsThumb(rec.objs||[]);\n"
    "    A3D_FAMLIB.push(entry);\n"
    "    bimSaveFamilyLibrary();\n",
    "    entry.thumb=bimRecsThumb(rec.objs||[]);\n"
    "    if(inIdb){\n"
    "      entry.idb=1;\n"
    "      bimIdbPut('tpl:'+id,{rec:s,saved:Date.now(),v:1},function(err){\n"
    "        if(!err)return;\n"
    "        console.warn('[BIM] The template could not be stored.',err);\n"
    "        var i;for(i=A3D_FAMLIB.length-1;i>=0;i--)if(A3D_FAMLIB[i].id===id)A3D_FAMLIB.splice(i,1);\n"
    "        bimSaveFamilyLibrary();\n"
    "        try{refreshFamilyPanel();}catch(eR){console.warn('[BIM] The Assets panel could not be refreshed.',eR);}\n"
    "        a3dToast('The template could not be saved: browser storage is full');\n"
    "      });\n"
    "    }\n"
    "    A3D_FAMLIB.push(entry);\n"
    "    bimSaveFamilyLibrary();\n")
rep(T,
    "  function bimTemplateUse(entry){\n"
    "    if(!entry||bimAssetKind(entry)!=='template')return null;\n"
    "    var raw=null,rec=null;\n",
    "  function bimTemplateUse(entry){\n"
    "    if(!entry||bimAssetKind(entry)!=='template')return null;\n"
    "    /* __acad3dV172e: a template kept in the browser's database is read first; the project follows */\n"
    "    if(entry.idb){\n"
    "      bimIdbGet('tpl:'+entry.id,function(err,v){\n"
    "        var r=null;\n"
    "        if(!err&&v&&typeof v.rec==='string'){try{r=JSON.parse(v.rec);}catch(eJ){r=null;}}\n"
    "        if(!r||typeof r!=='object'){\n"
    "          if(err)console.warn('[BIM] The browser\\'s database could not be read.',err);\n"
    "          a3dToast('\"'+entry.name+'\" could not be used: its stored project could not be read');\n"
    "          return;\n"
    "        }\n"
    "        bimTemplateStart(entry,r);\n"
    "      });\n"
    "      return true;\n"
    "    }\n"
    "    var raw=null,rec=null;\n")
rep(T,
    "    if(!rec||typeof rec!=='object'){a3dToast('\"'+entry.name+'\" could not be used: its stored project is damaged');return null;}\n"
    "    if(!rec.titleBlock||typeof rec.titleBlock!=='object')rec.titleBlock={project:'',client:'',drawnBy:'',checkedBy:''};\n",
    "    if(!rec||typeof rec!=='object'){a3dToast('\"'+entry.name+'\" could not be used: its stored project is damaged');return null;}\n"
    "    return bimTemplateStart(entry,rec);\n"
    "  }\n"
    "  function bimTemplateStart(entry,rec){\n"
    "    if(!rec.titleBlock||typeof rec.titleBlock!=='object')rec.titleBlock={project:'',client:'',drawnBy:'',checkedBy:''};\n")

# ---- 3. D3: the browser asked to keep the app's storage, once, at the first Save
rep('js/engine/io/project-file.js',
    "      a3dToast('Project saved as '+bimFileStem()+'.acad3d.json ('+A3D.objs.length+' object(s))');\n"
    "    }catch(eS){console.warn('[BIM] Project export failed: ',eS);a3dToast('Project export failed: '+(eS&&eS.message?eS.message:eS));}\n"
    "  }\n",
    "      a3dToast('Project saved as '+bimFileStem()+'.acad3d.json ('+A3D.objs.length+' object(s))');\n"
    "      bimAskPersist();   /* __acad3dV172e */\n"
    "    }catch(eS){console.warn('[BIM] Project export failed: ',eS);a3dToast('Project export failed: '+(eS&&eS.message?eS.message:eS));}\n"
    "  }\n"
    "  /* __acad3dV172e: decision D3. The browser keeps best-effort storage only while it has room; persist() asks it to\n"
    "     keep this app's. Asked once, at the first Save -- a gesture, never on load (web.dev); Firefox shows a prompt,\n"
    "     Chrome and Safari answer silently, and false is the usual answer in a Safari tab, so it is not an error. */\n"
    "  var A3D_PERSIST={asked:false,granted:null};\n"
    "  function bimAskPersist(){\n"
    "    if(A3D_PERSIST.asked)return;\n"
    "    A3D_PERSIST.asked=true;\n"
    "    try{\n"
    "      if(!navigator.storage||typeof navigator.storage.persist!=='function')return;\n"
    "      navigator.storage.persisted().then(function(p){\n"
    "        if(p){A3D_PERSIST.granted=true;return null;}\n"
    "        return navigator.storage.persist().then(function(g){A3D_PERSIST.granted=!!g;});\n"
    "      })['catch'](function(eQ){console.warn('[BIM] The browser could not be asked to keep this app\\'s storage.',eQ);});\n"
    "    }catch(eP){console.warn('[BIM] The browser could not be asked to keep this app\\'s storage.',eP);}\n"
    "  }\n")

# ---- 4. the marker and the suites' window on it
rep('js/engine/testing/hooks-layers-sheets.js',
    "  window.__a3dSpill=function(){",
    "  window.__acad3dV172e='libidb,libpointer,libbootload,libmerge,tplidb,tpluse,tplremove,persistonsave';\n"
    "  window.__a3dLibStore=function(){return {idb:A3D_FAMLIB_IDB,loading:A3D_FAMLIB_LOADING,dirty:A3D_FAMLIB_DIRTY};};\n"
    "  window.__a3dPersist=function(){return {asked:A3D_PERSIST.asked,granted:A3D_PERSIST.granted};};\n"
    "  window.__a3dSpill=function(){")
done()
