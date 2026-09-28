"""falsify_phase121b.py -- break the V121b build one way at a time, keeping the marker.

Each variant takes back one thing V121b does -- which stored entries go, which stay, and where the
interface theme lives -- and the V121b suite must fail on every one of them."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    'list_missing_key': [("'acadLayoutsV1','acadBlocksV1','acadDockV1','canvas-grid'];", "'acadLayoutsV1','acadBlocksV1','canvas-grid'];")],
    'clears_everything': [("  var A3D_CANVAS_CLEARED=bimClearCanvasStorage();\n",
                           "  var A3D_CANVAS_CLEARED=bimClearCanvasStorage();try{localStorage.clear();}catch(eZ){}\n")],
    'removes_app_key': [("'acadLayoutsV1','acadBlocksV1','acadDockV1','canvas-grid'];", "'acadLayoutsV1','acadBlocksV1','acadDockV1','canvas-grid','acad3dDocsV1'];")],
    'removal_by_pattern': [("    var gone=[],i,k;\n    for(i=0;i<A3D_CANVAS_KEYS.length;i++){\n",
                            "    var gone=[],i,k,z;\n    for(z=localStorage.length-1;z>=0;z--)if(/^another-/.test(localStorage.key(z)))localStorage.removeItem(localStorage.key(z));\n"
                            "    for(i=0;i<A3D_CANVAS_KEYS.length;i++){\n")],
    'cleanup_not_run': [("  var A3D_CANVAS_CLEARED=bimClearCanvasStorage();\n", "  var A3D_CANVAS_CLEARED=[];\n")],
    'silent_removal': [("    if(gone.length)a3dToast('Removed the old canvas\\'s saved data from this browser ('+gone.length+' entr'+(gone.length===1?'y':'ies')+')');\n", "")],
    'theme_not_applied': [("    if(v==='light'||v==='dark')document.body.classList.toggle('light-theme',v==='light');\n", "")],
    'theme_written_old_name': [("        bimThemeStore(light);   /* __acad3dV121b: under the app's own name, and read back at every start */\n",
                                "        try{localStorage.setItem('canvas-theme',light?'light':'dark');}catch(eL){}\n")],
    'no_carry_over': [("        if(v===null&&(old==='light'||old==='dark')){v=old;localStorage.setItem(A3D_THEME_KEY,v);}\n", "")],
    'old_name_kept': [("        localStorage.removeItem('canvas-theme');\n", "")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV121b' in txt
out.write_text(txt, encoding='utf-8')
