"""patch_phase124g.py -- V124: the commands, the ribbon's Component, the claims, the hooks, the marker.

  BLOCK   (B, BMAKE)                     save the selection to the library as a block
  INSERT  (I, DDINSERT)                  open the library at its blocks: drag one onto the drawing
  ASSETS  (ADCENTER, CONTENT, TOOLPALETTES)  open the library

The ribbon's Component button said "Place a family from the Project Browser > Families" and did
nothing else: it opens the library at its models now.

The shell audit claims the library's new controls, each driven by the V124 suite before it was
claimed, and the Assets tab's claim says what the tab is now."""
NAME = 'patch_phase124g.py'
BASE = '48217504afdf0e72ffe78dc8024cf99bf6381b85c9322539b471828c8429be62'
import hashlib, pathlib, sys
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')
raw = P.read_bytes()
h0 = hashlib.sha256(raw).hexdigest()
if h0 != BASE:
    sys.exit('ABORT: baseline %s, expected %s' % (h0, BASE))
t = raw.decode('utf-8')


def esc(s):
    return ''.join(ch if ord(ch) < 128 else '\\u%04x' % ord(ch) for ch in s)


def rep(old, new, n=1):
    global t
    new = esc(new)
    c = t.count(old)
    if c != n:
        sys.exit('ABORT: %d occurrences, expected %d: %r' % (c, n, old[:90]))
    t = t.replace(old, new)


# ---- commands
rep("""    ['PSPACE',['PS'],'pspace','Back to paper space on this sheet']
  ];""", """    ['PSPACE',['PS'],'pspace','Back to paper space on this sheet'],
    /* __acad3dV124: the library */
    ['BLOCK',['B','BMAKE'],'blockmake','Save the selection to the library as a block'],
    ['INSERT',['I','DDINSERT'],'blockinsert','Insert a block: drag it from the library onto the drawing'],
    ['ASSETS',['ADCENTER','CONTENT','TOOLPALETTES'],'assets','Open the Assets library of models, blocks and templates']
  ];""")
rep("""    presspull:function(){bimPressPullCommand();},   /* __acad3dV123 */
""", """    presspull:function(){bimPressPullCommand();},   /* __acad3dV123 */
    blockmake:function(){openSaveBlockDlg();},                   /* __acad3dV124 */
    blockinsert:function(){bimOpenLibraryAt('blocks');},
    assets:function(){bimOpenLibraryAt(null);},
""")

# ---- open the library, at a group
rep("""  /* the four actions above the library */""", """  /* The Assets tab, with one group unfolded and brought into view. */
  function bimOpenLibraryAt(gid){
    bimShellSetTab('assets');
    if(gid){
      A3D_ASSETS_UI.closed[gid]=false;
      refreshAssets();
      var gh=document.querySelector('#a3d-leftpanel [data-a3dassetgrp="'+gid+'"]');
      if(gh&&gh.scrollIntoView)gh.scrollIntoView({block:'start'});
    }
    if(gid==='blocks')a3dToast(bimLibEntries('block').length?'Drag a block onto the drawing, or click it to place it at the centre of the view'
      :'No blocks yet: select objects and run BLOCK');
    else if(gid==='families')a3dToast('Drag a model onto the drawing, or click it to place it at the centre of the view');
    return true;
  }
  /* the four actions above the library */""")

# ---- the ribbon's Component opens the library at its models
rep("""    if(act==='bim:component'){a3dToast('Place a family from the Project Browser > Families');return;}""",
    """    if(act==='bim:component'){bimOpenLibraryAt('families');return;}   /* __acad3dV124 */""")

# ---- claims
rep("""    {sel:'.a3d-railbtn[data-tab="assets"]',why:'Assets tab: the BIM asset libraries'},""",
    """    {sel:'.a3d-railbtn[data-tab="assets"]',why:'Assets tab: the library of models, blocks and templates, dragged into the project'},
    /* __acad3dV124: the library's controls -- each driven by the V124 suite before it was claimed */
    {sel:'[data-a3dasact]',why:'library action: import a model, save the selection as a block or a model, save the project as a template'},
    {sel:'[data-a3dasdel]',why:'removes a model, block or template the user added to the library, after asking'},""")
rep("""    {sel:'[data-a3dassets]',why:'BIM asset row'},
    {sel:'[data-a3dassetgrp]',why:'BIM asset group header'},""",
    """    {sel:'[data-a3dassets]',why:'a library item: click to place or apply it, or drag it onto the drawing'},
    {sel:'[data-a3dassetgrp]',why:'a library group header: folds and unfolds the group'},""")

# ---- hooks and the marker
rep("""  window.__acad3dV123='projectunits,""", """  /* __acad3dV124: the library, read and driven */
  window.__a3dLibrary=function(){
    var all=A3D_FAMLIB.concat(A3D_ASSET_BUILTINS);
    return all.map(function(e){
      return {id:e.id,kind:bimAssetKind(e),name:e.name,category:e.category,builtin:!!e.builtin,
        count:e.count||0,unit:e.unit||null,source:e.source||null,size:e.mesh&&e.mesh.size?e.mesh.size.slice():null,
        thumb:typeof e.thumb==='string'&&e.thumb.indexOf('data:image/png')===0};
    });
  };
  window.__a3dBlockSave=function(name,ids){
    var e=bimBlockSave(name,ids||bimAssetSelIds());
    if(e)refreshFamilyPanel();
    return e?e.id:null;
  };
  window.__a3dBlockInsert=function(id,x,z){return bimInsertBlock(bimFamilyLibraryGet(id),[x,z]);};
  window.__a3dTemplateSave=function(name){var e=bimTemplateSave(name);if(e)refreshFamilyPanel();return e?e.id:null;};
  window.__a3dTemplateUse=function(id){return bimTemplateUse(bimFamilyLibraryGet(id));};
  window.__a3dAssetDropAt=function(spec,cx,cy){return bimAssetDropAt(spec,cx,cy);};
  window.__a3dViewCentrePlan=function(){return bimViewCentrePlan();};
  window.__a3dImportGuess=function(mesh){return bimGuessImportUnit(mesh);};
  window.__a3dImportMesh=function(mesh,unit,zUp){return bimImportModelMesh(mesh,unit,!!zUp);};
  window.__a3dAssetsUI=function(){return {q:A3D_ASSETS_UI.q,closed:JSON.parse(JSON.stringify(A3D_ASSETS_UI.closed)),dragging:!!(A3D_ASDRAG&&A3D_ASDRAG.on)};};
  window.__acad3dV124='librarykinds,starterset,thumbnails,importunit,importupaxis,blocks,blocklinks,blocklevel,'+
    'selectionmodel,templates,librarypanel,librarysearch,folds,removeasks,clickatviewcentre,dragdrop,dropsnap,'+
    'droponobject,blockcommand,insertcommand,assetscommand,componentopenslibrary';
  window.__acad3dV123='projectunits,""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
