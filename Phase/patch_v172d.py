#!/usr/bin/env python3
"""V172d, storage phase A1: a project too large for localStorage is kept in IndexedDB, with a pointer in its place.

reference/research-local-storage.md, the owner's decision D1 (2026-10-31): phase A, the IndexedDB project store. A1
is its first half: the active project and parked projects go to the browser's database when localStorage refuses
them, so a large model saves and can be switched away from; what fits stays where it was, so a small project boots
and switches exactly as before. A2 moves templates and the Assets library, then retires the old keys.

The new file src/js/engine/core/idb-store.js (from Phase/v172d_idb_store.js) sits between core/objects-save.js and
ui/project-tabs.js.

Run from the repository root: python3 Phase/patch_v172d.py
"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from p171 import begin, rep, write, done   # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent

begin('1dd1646f3e6b36424a41a7bab53c9a270c621ed0ae75c89d5c31d6240bd29e3f')   # V124b

# ---- 1. the new file, and its place in the order
write('js/engine/core/idb-store.js', (HERE / 'v172d_idb_store.js').read_text(encoding='utf-8'))
idx = ROOT / 'src' / 'index.html'
t = idx.read_text(encoding='utf-8')
a = '<!-- @include js/engine/core/objects-save.js -->\n'
assert t.count(a) == 1
idx.write_text(t.replace(a, a + '<!-- @include js/engine/core/idb-store.js -->\n'), encoding='utf-8')
lay = ROOT / 'tools' / 'app_layout.py'
t = lay.read_text(encoding='utf-8')
a = "    ('core/objects-save.js', '  function add3d(t,prm){'),\n"
assert t.count(a) == 1
lay.write_text(t.replace(a, a + "    ('core/idb-store.js', '  /* ================= __acad3dV172d: the browser\\'s database, for a project too large for localStorage'),\n"), encoding='utf-8')

# ---- 2. boot: a pointer names the project; its record is read from the database after start
rep('js/engine/core/state.js',
    "  var A3D_BOOT_DOC=null;\n",
    "  var A3D_BOOT_DOC=null;\n"
    "  var A3D_BOOT_IDB=null;   /* __acad3dV172d: the project on screen is in the browser's database (core/idb-store.js) */\n")
rep('js/engine/core/state.js',
    "      var st=JSON.parse(raw);\n"
    "      bimApplyStoredState(st);\n",
    "      var st=JSON.parse(raw);\n"
    "      /* __acad3dV172d: a pointer in place of the record: its name now, the record once the database is read */\n"
    "      if(st&&st.idb===1&&typeof st.docId==='string'&&!Array.isArray(st.objs)){\n"
    "        A3D_BOOT_IDB=st.docId;\n"
    "        if(st.titleBlock&&typeof st.titleBlock.project==='string')A3D.titleBlock.project=st.titleBlock.project;\n"
    "      }else bimApplyStoredState(st);\n")

# ---- 3. save3d: localStorage while the record fits, else the database
rep('js/engine/core/objects-save.js',
    "  function save3d(){\n"
    "    var rec=bimProjectRecord();\n"
    "    rec.docId=A3D_DOCS.active;\n"
    "    try{\n"
    "      localStorage.setItem(LSK,JSON.stringify(rec));\n"
    "      if(A3D_SAVE_FAILED){A3D_SAVE_FAILED=false;a3dToast('Saving to browser storage works again');}\n"
    "    }catch(e1){\n"
    "      if(!A3D_SAVE_FAILED){\n"
    "        A3D_SAVE_FAILED=true;\n"
    "        console.warn('[BIM] The project could not be saved to browser storage.',e1);\n"
    "        a3dToast('This project could not be saved: browser storage is full. Use Save to keep a copy as a file.');\n"
    "      }\n"
    "    }\n"
    "  }\n",
    "  /* __acad3dV172d: a record localStorage refuses goes to the browser's database (core/idb-store.js), and stays\n"
    "     there while it is the project on screen; nothing saves while that record is still being read */\n"
    "  function save3d(){\n"
    "    if(A3D_SPILL&&A3D_SPILL.loading)return;\n"
    "    var rec=bimProjectRecord();\n"
    "    rec.docId=A3D_DOCS.active;\n"
    "    var s=JSON.stringify(rec);\n"
    "    if(!(A3D_SPILL&&A3D_SPILL.on)){\n"
    "      try{\n"
    "        localStorage.setItem(LSK,s);\n"
    "        if(A3D_SAVE_FAILED){A3D_SAVE_FAILED=false;a3dToast('Saving to browser storage works again');}\n"
    "        return;\n"
    "      }catch(e1){\n"
    "        console.warn('[BIM] The project does not fit in browser storage; it goes to the browser\\'s database.',e1);\n"
    "      }\n"
    "    }\n"
    "    bimSpillSave(rec.docId,s,rec);\n"
    "  }\n")

# ---- 4. the project list: a pointer names its project and counts it
rep('js/engine/ui/project-tabs.js',
    "        meta.objs=Array.isArray(st.objs)?st.objs.length:0;\n",
    "        meta.objs=Array.isArray(st.objs)?st.objs.length:(isFinite(st.count)?+st.count:0);   /* __acad3dV172d: a pointer's count */\n")

# ---- 5. switching: a record too large for its key is parked in the database; the next one goes there too
rep('js/engine/ui/project-tabs.js',
    "    var recA=bimProjectRecord();recA.docId=cur;\n"
    "    var sA=JSON.stringify(recA);\n",
    "    var recA=bimProjectRecord();recA.docId=cur;\n"
    "    var sA=JSON.stringify(recA);\n"
    "    /* __acad3dV172d: a project still being read from the database is parked as its pointer, never as the\n"
    "       fresh project the page started with */\n"
    "    if(A3D_SPILL.loading){try{sA=localStorage.getItem(LSK)||sA;}catch(eG){console.warn('[BIM] The pointer of the project on screen could not be read.',eG);}}\n")
rep('js/engine/ui/project-tabs.js',
    "    try{localStorage.setItem(A3D_DOC_PREFIX+cur,sA);}\n"
    "    catch(e1){console.warn('[BIM] The current project could not be parked in its own key.',e1);a3dToast(full);return false;}\n"
    "    try{localStorage.setItem(LSK,sB);}\n"
    "    catch(e2){\n"
    "      try{localStorage.removeItem(A3D_DOC_PREFIX+cur);}\n"
    "      catch(e3){console.warn('[BIM] A parked copy could not be removed after a failed switch.',e3);}\n"
    "      console.warn('[BIM] The next project could not be written to the active slot.',e2);\n"
    "      a3dToast(full);\n"
    "      return false;\n"
    "    }\n",
    "    try{localStorage.setItem(A3D_DOC_PREFIX+cur,sA);}\n"
    "    catch(e1){\n"
    "      /* __acad3dV172d: too large for its own key: the database, its pointer in the key */\n"
    "      console.warn('[BIM] The current project does not fit in its own key; it is parked in the browser\\'s database.',e1);\n"
    "      if(!bimParkInIdb(cur,sA,recA,A3D_DOC_PREFIX+cur)){a3dToast(full);return false;}\n"
    "    }\n"
    "    var spillB=false;\n"
    "    try{localStorage.setItem(LSK,sB);}\n"
    "    catch(e2){\n"
    "      /* __acad3dV172d: the next project does not fit the active slot: it is kept in the database */\n"
    "      console.warn('[BIM] The next project does not fit in browser storage; it is kept in the browser\\'s database.',e2);\n"
    "      spillB=true;\n"
    "    }\n")
rep('js/engine/ui/project-tabs.js',
    "    A3D_DOC_RT[cur]=stash;\n"
    "    A3D_DOCS.active=toId;\n",
    "    A3D_DOC_RT[cur]=stash;\n"
    "    A3D_DOCS.active=toId;\n"
    "    A3D_SPILL.on=spillB;A3D_SPILL.loading=false;   /* __acad3dV172d */\n"
    "    if(spillB){bimSpillSave(toId,sB,stB);bimSpillToast();}\n")

# ---- 6. opening a parked project kept in the database: read it, then switch
rep('js/engine/ui/project-tabs.js',
    "      if(!st||typeof st!=='object'){a3dToast('\"'+nm+'\" could not be opened: its stored data is damaged');return false;}\n"
    "      if(!bimDocsSwap(id,st,A3D_DOC_PREFIX+id))return false;\n",
    "      if(!st||typeof st!=='object'){a3dToast('\"'+nm+'\" could not be opened: its stored data is damaged');return false;}\n"
    "      if(bimIsIdbPointer(st)){bimDocsActivateIdb(id,nm);return true;}   /* __acad3dV172d */\n"
    "      if(!bimDocsSwap(id,st,A3D_DOC_PREFIX+id))return false;\n")
rep('js/engine/ui/project-tabs.js',
    "  function bimNextProjectName(){\n",
    "  /* __acad3dV172d: a parked project kept in the database is read first; the switch follows when it arrives. Once\n"
    "     it is on screen in localStorage, the database's copy is no longer needed. */\n"
    "  function bimDocsActivateIdb(id,nm){\n"
    "    bimIdbGet(id,function(err,v){\n"
    "      var st=null;\n"
    "      if(!err&&v&&typeof v.rec==='string'){\n"
    "        try{st=JSON.parse(v.rec);}catch(eJ){console.warn('[BIM] A project in the browser\\'s database is not valid JSON: '+id,eJ);}\n"
    "      }\n"
    "      if(!st||typeof st!=='object'){\n"
    "        if(err)console.warn('[BIM] The browser\\'s database could not be read.',err);\n"
    "        a3dToast('\"'+nm+'\" could not be opened: the browser\\'s database could not be read');\n"
    "        return;\n"
    "      }\n"
    "      if(!bimDocsSwap(id,st,A3D_DOC_PREFIX+id))return;\n"
    "      if(!A3D_SPILL.on)bimIdbDel(id,function(eD){if(eD)console.warn('[BIM] A project\\'s copy in the browser\\'s database could not be removed: '+id,eD);});\n"
    "      if(A3D_DOCS.open.indexOf(id)<0)A3D_DOCS.open.push(id);\n"
    "      bimDocsSave();\n"
    "      bimDocsNotify('activate',id);\n"
    "    });\n"
    "  }\n"
    "  function bimNextProjectName(){\n")

# ---- 7. deleting a project deletes its database copy
rep('js/engine/assets/templates.js',
    "    A3D_DOCS.docs=A3D_DOCS.docs.filter(function(e){return e.id!==id;});\n"
    "    delete A3D_DOC_RT[id];\n",
    "    bimIdbDel(id,function(eD){if(eD)console.warn('[BIM] A project\\'s copy in the browser\\'s database could not be removed: '+id,eD);});   /* __acad3dV172d */\n"
    "    A3D_DOCS.docs=A3D_DOCS.docs.filter(function(e){return e.id!==id;});\n"
    "    delete A3D_DOC_RT[id];\n")

# ---- 8. the marker and the suites' window on it
rep('js/engine/testing/hooks-layers-sheets.js',
    "  window.__a3dTitleBlockSet=function(tb){",
    "  /* __acad3dV172d: where the project on screen is kept */\n"
    "  window.__acad3dV172d='idbstore,spill,pointer,bootload,bootguard,parkidb,activateidb,removeidb,hiddenflush,listcount';\n"
    "  window.__a3dSpill=function(){return {on:A3D_SPILL.on,loading:A3D_SPILL.loading,busy:A3D_SPILL.busy,next:!!A3D_SPILL.next};};\n"
    "  window.__a3dTitleBlockSet=function(tb){")
done()
