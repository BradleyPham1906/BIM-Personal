"""falsify_phase172d.py -- break the V172d build one way at a time, keeping the marker.
Variant names are lower case: the runner reads no other (V126). Each names, in its comment, the check
of tests/bim_phase172d_idb_projects_browser_tests.py that should catch it."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    'no_spill': [("    bimSpillSave(rec.docId,s,rec);\n  }\n", "    if(!A3D_SAVE_FAILED){A3D_SAVE_FAILED=true;a3dToast('This project could not be saved: browser storage is full. Use Save to keep a copy as a file.');}\n  }\n")],   # acad3dV1 holds a pointer to the project
    'always_spill': [("    if(!(A3D_SPILL&&A3D_SPILL.on)){\n      try{\n        localStorage.setItem(LSK,s);", "    if(0){\n      try{\n        localStorage.setItem(LSK,s);")],   # a small project is saved whole in acad3dV1
    'pointer_first': [("    A3D_SPILL.busy=true;\n    bimIdbPut(id,", "    A3D_SPILL.busy=true;\n    try{localStorage.setItem(LSK,bimIdbPointer(id,rec));}catch(eF){}\n    bimIdbPut(id,")],   # the pointer is written ... after the record has committed
    'no_count': [("      count:rec&&Array.isArray(rec.objs)?rec.objs.length:0,saved:Date.now()});", "      saved:Date.now()});")],   # the pointer counts its objects
    'toast_each_save': [("    if(A3D_SPILL.told)return;\n", "")],   # without a second toast
    'boot_ignores_pointer': [("  if(A3D_BOOT_IDB)setTimeout(bimSpillBootLoad,0);\n", "")],   # the 23 walls are back after a reload
    'no_boot_guard': [("    if(A3D_SPILL&&A3D_SPILL.loading)return;\n", "")],   # save3d writes nothing while ... being read
    'stays_loading': [("        bimLoadProjectRecord(st);\n        A3D_SPILL.loading=false;\n", "        bimLoadProjectRecord(st);\n")],   # kept in the database, and read
    'park_fails': [("      if(!bimParkInIdb(cur,sA,recA,A3D_DOC_PREFIX+cur)){a3dToast(full);return false;}\n", "      a3dToast(full);return false;\n")],   # the large project is parked as a pointer in its key
    'activate_raw_pointer': [("      if(bimIsIdbPointer(st)){bimDocsActivateIdb(id,nm);return true;}   /* __acad3dV172d */\n", "")],   # opening it again reads the parked model back
    'list_count_lost': [("        meta.objs=Array.isArray(st.objs)?st.objs.length:(isFinite(st.count)?+st.count:0);", "        meta.objs=Array.isArray(st.objs)?st.objs.length:0;")],   # the list counts the parked project
    'remove_keeps_idb': [("    bimIdbDel(id,function(eD){if(eD)console.warn('[BIM] A project\\'s copy in the browser\\'s database could not be removed: '+id,eD);});   /* __acad3dV172d */\n", "")],   # the database no longer holds the deleted project
    'spill_flag_kept': [("    A3D_SPILL.on=spillB;A3D_SPILL.loading=false;   /* __acad3dV172d */\n", "    A3D_SPILL.loading=false;\n")],   # the new, small project is saved whole in acad3dV1
    'no_hidden_flush': [("    if(document.hidden&&saveT){clearTimeout(saveT);saveT=null;save3d();}\n", "    if(0){}\n")],   # a waiting autosave is written when the page is hidden
    'versionchange_open': [("      db.onversionchange=function(){\n        db.close();\n", "      db.onversionchange=function(){\n")],   # a connection another tab's upgrade asks for is closed
    'db_named_generic': [("var A3D_IDB_NAME='BIM-Personal'", "var A3D_IDB_NAME='app'")],   # one database, named for the app
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV172d' in txt
out.write_text(txt, encoding='utf-8')
