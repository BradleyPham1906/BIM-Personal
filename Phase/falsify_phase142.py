"""falsify_phase142.py -- break the V142 build one way at a time, keeping the marker.

Each variant takes back one thing V142 does, and the V142 suite must fail on every one of them.
Variant names are lower case: the runner reads no other (V126)."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    'version_stale': [("  var BIM_APP_VERSION={v:'V142',", "  var BIM_APP_VERSION={v:'V141',")],
    'no_version_row': [("    srows+=bimPropRow('Version','<span class=\"a3d-pstatic\">'+bimVersionHtml()+'</span>');   /* __acad3dV142 */\n", "")],
    'notes_link_no_anchor': [("bimDocsUrl('changelog.html',BIM_APP_VERSION.v.toLowerCase()))+'\" target=\"_blank\" rel=\"noopener\" data-docslink=\"notes\">'",
                              "bimDocsUrl('changelog.html'))+'\" target=\"_blank\" rel=\"noopener\" data-docslink=\"notes\">'")],
    'docs_base_wrong': [("  var BIM_DOCS_BASE='docs/';", "  var BIM_DOCS_BASE='documentation/';")],
    'docs_command_unwired': [("    docs:function(){bimDocsOpen('index.html');},                  /* __acad3dV142 */\n", "")],
    'releasenotes_to_index': [("    releasenotes:function(){bimDocsOpen('changelog.html',BIM_APP_VERSION.v.toLowerCase());},", "    releasenotes:function(){bimDocsOpen('index.html');},")],
    'f1_ignored': [("      else if(e.key==='F1'){   /* __acad3dV142: the highlighted command's page in the guide */", "      else if(false){")],
    'f1_keeps_search_open': [("        if(hc&&hc.kind!=='key'&&window.__a3dDocsOpen){closePal();window.__a3dDocsOpen('commands.html',hc.id);}",
                              "        if(hc&&hc.kind!=='key'&&window.__a3dDocsOpen){window.__a3dDocsOpen('commands.html',hc.id);}")],
    'f1_no_anchor': [("window.__a3dDocsOpen('commands.html',hc.id);}", "window.__a3dDocsOpen('commands.html');}")],
    'anchor_raw_id': [("  function bimDocsAnchor(id){return String(id||'').replace(/[^A-Za-z0-9_-]+/g,'-');}", "  function bimDocsAnchor(id){return String(id||'');}")],
    'no_search_words': [("    DOCS:'help documentation manual guide tutorial learn how reference f1',   /* __acad3dV142 */\n", "")],
    'catalog_changed': [("    ['RELEASENOTES',['VERSION','WHATSNEW'],'releasenotes','What changed in this version, and every version before it'],",
                         "    ['RELEASENOTES',['VERSION','WHATSNEW'],'releasenotes','What changed'],")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV142' in txt
out.write_text(txt, encoding='utf-8')
