"""falsify_phase172e.py -- break the V172e build one way at a time, keeping the marker.
Variant names are lower case: the runner reads no other (V126). Each names, in its comment, the check
of tests/bim_phase172e_idb_library_templates_browser_tests.py that should catch it."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    'lib_no_spill': [("    if(typeof bimIdbPut!=='function'){failed(new Error('no browser database'));return false;}\n", "    failed(new Error('refused'));return false;\n")],   # its key holds a pointer
    'lib_always_spill': [("    if(!A3D_FAMLIB_IDB){\n      try{localStorage.setItem(FAMILY_LIB_KEY,s);worked();return true;}", "    if(0){\n      try{localStorage.setItem(FAMILY_LIB_KEY,s);worked();return true;}")],   # a small library is saved whole in its key
    'lib_pointer_first': [("    bimIdbPut('lib:family',{rec:s,saved:Date.now(),v:1},function(err){\n      if(err){failed(err);return;}\n", "    try{localStorage.setItem(FAMILY_LIB_KEY,JSON.stringify({idb:1,key:'lib:family',count:n}));}catch(eF){}\n    bimIdbPut('lib:family',{rec:s,saved:Date.now(),v:1},function(err){\n      if(err){failed(err);return;}\n")],   # the library's pointer is written after its copy has committed
    'lib_not_read': [("  if(A3D_FAMLIB_LOADING)setTimeout(bimLibBootLoad,0);   /* __acad3dV172e */\n", "")],   # a reload reads the library back from the database
    'lib_pointer_as_list': [("        if(parsed&&parsed.idb===1){A3D_FAMLIB_IDB=true;A3D_FAMLIB_LOADING=true;return [];}   /* __acad3dV172e */\n", "")],   # a reload reads the library back
    'lib_save_while_loading': [("    if(A3D_FAMLIB_LOADING){A3D_FAMLIB_DIRTY=true;return null;}\n", "")],   # nothing saves over the library while it is read
    'lib_added_lost': [("      Array.prototype.push.apply(A3D_FAMLIB,arr.concat(added));\n", "      Array.prototype.push.apply(A3D_FAMLIB,arr);\n")],   # what is added while it is read is kept
    'tpl_refused': [("      console.warn('[BIM] The template does not fit in browser storage; it goes to the browser\\'s database.',eS);\n      inIdb=true;\n", "      a3dToast('The template could not be saved: browser storage is full');return null;\n")],   # the template is saved
    'tpl_use_raw': [("    if(entry.idb){\n      bimIdbGet('tpl:'+entry.id,", "    if(0){\n      bimIdbGet('tpl:'+entry.id,")],   # using it opens a new project with the template's model
    'tpl_remove_keeps': [("      if(A3D_FAMLIB[idx].idb)bimIdbDel('tpl:'+id,", "      if(0)bimIdbDel('tpl:'+id,")],   # removing it removes its copy
    'tpl_entry_left': [("        var i;for(i=A3D_FAMLIB.length-1;i>=0;i--)if(A3D_FAMLIB[i].id===id)A3D_FAMLIB.splice(i,1);\n", "")],   # its entry is not left in the library
    'idb_sync_answer': [("      if(err){setTimeout(function(){done(err);},0);return;}\n", "      if(err){done(err);return;}\n")],   # every database answer comes after the call has returned
    'persist_on_load': [("  var A3D_PERSIST={asked:false,granted:null};\n", "  var A3D_PERSIST={asked:false,granted:null};setTimeout(function(){bimAskPersist();},0);\n")],   # the browser is not asked to keep storage on load
    'persist_every_save': [("    if(A3D_PERSIST.asked)return;\n    A3D_PERSIST.asked=true;\n", "    A3D_PERSIST.asked=true;\n")],   # a second Save does not ask again
    'persist_never': [("      bimAskPersist();   /* __acad3dV172e */\n", "")],   # the first Save asks
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV172e' in txt
out.write_text(txt, encoding='utf-8')
