#!/usr/bin/env python3
"""V172d, patch b: found reading V115's full-store check against the new parking. When the key a large project is
parked in refused even its pointer, the record had already been sent to the database, and stayed there with nothing
pointing to it. The pointer goes first now: while it is written, acad3dV1 still holds the project on screen, so a crash
between the two leaves a parked pointer that boot drops as stale (V115), never a pointer to nothing. The database is
written only once the pointer is in.

Run from the repository root: python3 Phase/patch_v172d_b.py
"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from p171 import begin, rep, done   # noqa: E402

begin('9add9ac9b817771ceca4a25ba940419cf569b486243b0732d958ba83bab3e2c9')   # patch a

rep('js/engine/core/idb-store.js',
    "  /* a parked project too large for its own key: into the database, its pointer in the key */\n"
    "  function bimParkInIdb(id,s,rec,key){\n"
    "    /* a queued save of this project is older than what is parked now, and would be written after it */\n"
    "    if(A3D_SPILL.next&&A3D_SPILL.next.id===id)A3D_SPILL.next=null;\n"
    "    bimIdbPut(id,{rec:s,saved:Date.now(),v:1},function(err){\n"
    "      if(err){\n"
    "        console.warn('[BIM] A parked project could not be written to the browser\\'s database: '+id,err);\n"
    "        a3dToast('\"'+bimNameOf(rec&&rec.titleBlock)+'\" could not be stored: browser storage is full. Open it and use Save to keep a copy as a file.');\n"
    "      }\n"
    "    });\n"
    "    try{localStorage.setItem(key,bimIdbPointer(id,rec));return true;}\n"
    "    catch(eK){console.warn('[BIM] The pointer to a parked project could not be stored: '+id,eK);return false;}\n"
    "  }\n",
    "  /* a parked project too large for its own key: its pointer in the key, then the record into the database. The\n"
    "     pointer may go first: while it is written, acad3dV1 still holds this project, and boot drops a parked copy of\n"
    "     the project acad3dV1 names (V115), so a crash between the two loses nothing. */\n"
    "  function bimParkInIdb(id,s,rec,key){\n"
    "    try{localStorage.setItem(key,bimIdbPointer(id,rec));}\n"
    "    catch(eK){console.warn('[BIM] The pointer to a parked project could not be stored: '+id,eK);return false;}\n"
    "    /* a queued save of this project is older than what is parked now, and would be written after it */\n"
    "    if(A3D_SPILL.next&&A3D_SPILL.next.id===id)A3D_SPILL.next=null;\n"
    "    bimIdbPut(id,{rec:s,saved:Date.now(),v:1},function(err){\n"
    "      if(err){\n"
    "        console.warn('[BIM] A parked project could not be written to the browser\\'s database: '+id,err);\n"
    "        a3dToast('\"'+bimNameOf(rec&&rec.titleBlock)+'\" could not be stored: browser storage is full. Open it and use Save to keep a copy as a file.');\n"
    "      }\n"
    "    });\n"
    "    return true;\n"
    "  }\n")
done()
