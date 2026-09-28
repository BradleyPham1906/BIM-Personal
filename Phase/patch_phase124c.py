"""patch_phase124c.py -- V124: blocks, and a model saved from a whole selection.

A BLOCK (AutoCAD's BLOCK and INSERT) is a set of objects saved to the library and inserted as
independent copies at a point. What is saved is each object's own record, so a wall comes back a
wall with its type, a room a room, a sketch a sketch -- not a mesh. Its base point is the centre of
the selection in plan; an insert puts that centre where it is dropped or clicked.

An insert is copies made the way every copy in this app is made (bimDuplicateObject), then:
  - moved up or down by the active level's elevation less the level the block was saved from, and
    placed on the active level -- a block saved on the ground floor and dropped on Level 2 sits on
    Level 2;
  - a layer this project does not have becomes the current layer;
  - every link between objects in the block is pointed at the new copies: a floor on a sketch
    follows the new sketch, a clone its new source. A link to something that was not saved with the
    block is dropped, and the insert says how many (law 7: a detach is announced).
Openings and room tags are not saved -- a copy cannot carry them (an opening is cut into its wall
when the wall is built; a tag is made for its room) -- and the save dialog says how many were left.
One undo step; what was inserted is left selected.

Save as Model now takes the whole selection: every selected solid, where it is, as one mesh. It took
only the first selected object before, so a table saved with its chairs came back a table."""
NAME = 'patch_phase124c.py'
BASE = '7099ded4cfb622262ba660208ff864207ed66921bbbef7c4ce07915f14b4f55a'
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


# ---- Save as Model: the whole selection, where it is
rep("""  function openSaveAsFamilyDlg(){
    var o=objById(A3D.sel);
    if(!o){a3dToast('Select an object first');return;}
    var m=meshOf(o);
    if(!m||!m.f||!m.f.length){a3dToast('This object has no geometry to save as a family');return;}
""", """  /* __acad3dV124: every selected solid, in world position, as one mesh -- so a table saved with its
     chairs comes back with them. It took only the first selected object before. */
  function bimSelectionMesh(ids){
    var parts=[],i,j;
    for(i=0;i<ids.length;i++){
      var so=objById(ids[i]);if(!so)continue;
      var sm=meshOf(so);if(!sm||!sm.f||!sm.f.length||!sm.v||!sm.v.length)continue;
      var q=bimObjOffset(so),v=[];
      for(j=0;j<sm.v.length;j++)v.push([sm.v[j][0]+q[0],sm.v[j][1]+q[1],sm.v[j][2]+q[2]]);
      parts.push({v:v,f:sm.f});
    }
    return parts.length?bimMergeMeshes(parts):null;
  }
  function openSaveAsFamilyDlg(){
    var o=objById(A3D.sel);
    if(!o){a3dToast('Select an object first');return;}
    var selIds=(A3D.selSet&&A3D.selSet.length)?A3D.selSet.slice():[o.id];
    var m=bimSelectionMesh(selIds);
    if(!m||!m.f||!m.f.length){a3dToast('Nothing selected has geometry to save as a model');return;}
""")
rep("""    d.innerHTML='<div class="a3d-dlghd">Save as Family</div>'+
      '<div class="a3d-dlgbody">'+
      '<div class="a3d-dlgrow"><label>Name</label><input type="text" data-a3dp="name" value="'+bimEsc(o.name)+'" maxlength="60"></div>'+""",
    """    d.innerHTML='<div class="a3d-dlghd">Save as Model</div>'+
      '<div class="a3d-dlgbody">'+
      '<div class="a3d-dlgrow"><label>Name</label><input type="text" data-a3dp="name" value="'+bimEsc(o.name)+'" maxlength="60"></div>'+""")
rep("""      var fam=bimFamilyLibraryAdd({name:name,category:cI.value,mesh:m});
      refreshFamilyPanel();
      a3dToast('Saved "'+fam.name+'" to the Family Library');""",
    """      var fam=bimFamilyLibraryAdd({name:name,category:cI.value,mesh:m});
      refreshFamilyPanel();
      a3dToast('Saved "'+fam.name+'" to the library'+(selIds.length>1?' ('+selIds.length+' objects as one model)':''));""")

# ---- blocks
rep("""  function startFamilyPlaceTool(famId){
""", r"""  /* ================= __acad3dV124: blocks =================
     A block is object RECORDS, not a mesh, so what comes back is what went in: a wall with its
     type, a room, a sketch. Inserted through bimDuplicateObject, the one way this app copies. */
  /* The links an object can hold to another, read and rewritten here and nowhere else in a block. */
  var A3D_BLOCK_LINKS=[['sourceId'],['linkSourceId'],['roomId'],['on'],['bim','sourceId'],['bim','hostWallId'],['bim','hostId']];
  /* what a block cannot carry: an opening is cut into its wall when the wall is built, a room tag is
     made for its room */
  function bimBlockSkips(o){
    return !o||o.t==='opening'||o.t==='roomtag';
  }
  function bimBlockLevelElev(o){
    var lid=bimObjectLevelId(o),i;
    if(lid)for(i=0;i<A3D.levels.length;i++)if(A3D.levels[i].id===lid)return A3D.levels[i].elev;
    return null;
  }
  /* The block a selection makes: the records it can carry, deep-copied, its base point (the centre
     of the selection in plan) and the elevation of the level it came from. */
  function bimBlockFromIds(ids){
    var recs=[],skipped=0,i,y0=null;
    for(i=0;i<ids.length;i++){
      var o=objById(ids[i]);
      if(!o)continue;
      if(bimBlockSkips(o)){skipped++;continue;}
      recs.push(JSON.parse(JSON.stringify(o)));
      if(y0===null)y0=bimBlockLevelElev(o);
    }
    if(!recs.length)return {recs:[],skipped:skipped};
    var b=bimWorldBounds(recs.map(function(r){return r.id;})),base;
    if(b)base=[(b.mn[0]+b.mx[0])/2,(b.mn[2]+b.mx[2])/2];
    else{
      var L=bimRecsPlanLines(recs),sx=0,sz=0,n=0,j,k;
      for(j=0;j<L.length;j++)for(k=0;k<L[j].length;k++){sx+=L[j][k][0];sz+=L[j][k][1];n++;}
      base=n?[sx/n,sz/n]:[0,0];
    }
    if(y0===null)y0=b?b.mn[1]:bimGetActiveLevel().elev;
    return {recs:recs,skipped:skipped,base:base,y0:y0};
  }
  function bimBlockSave(name,ids){
    var blk=bimBlockFromIds(ids||[]);
    if(!blk.recs.length)return null;
    var entry={id:'blk-'+Date.now().toString(36)+'-'+Math.floor(Math.random()*1e6),kind:'block',
      name:name,category:'Blocks',manufacturer:'',recs:blk.recs,base:blk.base,y0:blk.y0,
      count:blk.recs.length,createdAt:new Date().toISOString()};
    entry.thumb=bimRecsThumb(entry.recs);
    A3D_FAMLIB.push(entry);
    bimSaveFamilyLibrary();
    return entry;
  }
  function openSaveBlockDlg(){
    var ids=(A3D.selSet&&A3D.selSet.length)?A3D.selSet.slice():(A3D.sel?[A3D.sel]:[]);
    if(!ids.length){a3dToast('Select the objects to make a block of first');return;}
    var blk=bimBlockFromIds(ids);
    if(!blk.recs.length){a3dToast('None of the selected objects can be saved in a block (openings and room tags go with their wall and room)');return;}
    var first=objById(ids[0]);
    closeDlg();
    var d=document.createElement('div');
    d.className='a3d-dlg';
    d.innerHTML='<div class="a3d-dlghd">Save as Block</div>'+
      '<div class="a3d-dlgbody">'+
      '<div class="a3d-dlgrow"><label>Name</label><input type="text" data-a3dp="name" value="'+bimEsc(first?first.name+' block':'Block')+'" maxlength="60"></div>'+
      '<div class="a3d-propnote">'+blk.recs.length+' object(s). The base point is the centre of the selection: an insert puts it where you drop or click.'+
      (blk.skipped?' '+blk.skipped+' opening(s) or room tag(s) are not included: they go with their wall and room.':'')+'</div>'+
      '<div id="a3d-dlgerr" class="a3d-dlgerr"></div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="ok">Save</button></div>';
    el.root.appendChild(d);
    el.dlg=d;
    var nI=d.querySelector('[data-a3dp="name"]');
    function submit(){
      var name=nI.value.trim();
      var eb=document.getElementById('a3d-dlgerr');
      if(!name){eb.textContent='Enter a name';return;}
      closeDlg();
      var e=null;
      try{e=bimBlockSave(name,ids);}
      catch(eB){console.warn('[BIM] The block could not be saved.',eB);}
      if(!e){a3dToast('The block could not be saved');return;}
      refreshFamilyPanel();
      a3dToast('Saved block "'+e.name+'" ('+e.count+' object(s)) to the library');
    }
    d.addEventListener('click',function(ev){var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;if(!b)return;if(b.getAttribute('data-a3dlg')==='ok')submit();else closeDlg();});
    d.addEventListener('keydown',function(ev){if(ev.key==='Enter'){ev.preventDefault();ev.stopPropagation();submit();}else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();}});
    nI.focus();nI.select();
  }
  function bimLinkGet(o,path){
    return path.length===1?o[path[0]]:(o[path[0]]?o[path[0]][path[1]]:undefined);
  }
  function bimLinkSet(o,path,v){
    if(path.length===1)o[path[0]]=v;else if(o[path[0]])o[path[0]][path[1]]=v;
  }
  /* Insert a block with its base point at pt ([x, z] on the active level). Returns the new ids, or
     null when nothing could be made. One undo step. */
  function bimInsertBlock(entry,pt){
    if(!entry||bimAssetKind(entry)!=='block'||!entry.recs||!entry.recs.length){a3dToast('That block has nothing in it');return null;}
    var lvl=bimGetActiveLevel(),dx=pt[0]-entry.base[0],dz=pt[1]-entry.base[1];
    var dY=lvl.elev-(isFinite(entry.y0)?entry.y0:lvl.elev);
    pushUndo();
    var mark=UNDO_STACK[UNDO_STACK.length-1];
    var made=[],from=[],map={},failed=0,i,j;
    for(i=0;i<entry.recs.length;i++){
      var r=JSON.parse(JSON.stringify(entry.recs[i])),c=null;
      try{c=bimDuplicateObject(r,dx,dz);}
      catch(eD){console.warn('[BIM] A block member could not be copied: '+(r&&r.name),eD);c=null;}
      if(!c){failed++;continue;}
      map[r.id]=c.id;
      from.push(r);
      bimShiftObjectY(c,dY);
      if(c.bim&&c.bim.levelId!==undefined)c.bim.levelId=lvl.id;
      if(c.levelId!==undefined)c.levelId=lvl.id;
      if(!c.layer||!bimLayerById(c.layer))c.layer=A3D.activeLayer;
      made.push(c);
    }
    /* The links are read from the SAVED record, not from the copy: a copy does not carry every link
       (a room's copy keeps its outline and drops its source), and a link the copy lost would be a
       dependent that no longer follows what it was built on. */
    var cut=0;
    for(i=0;i<made.length;i++){
      for(j=0;j<A3D_BLOCK_LINKS.length;j++){
        var path=A3D_BLOCK_LINKS[j],v=bimLinkGet(from[i],path);
        if(v===undefined||v===null||v==='')continue;
        if(map[v]){
          if(path.length===2&&!made[i][path[0]])continue;
          bimLinkSet(made[i],path,map[v]);
          /* a source carries its kind beside it */
          if(path[path.length-1]==='sourceId')bimLinkSet(made[i],path.slice(0,-1).concat(['sourceType']),bimLinkGet(from[i],path.slice(0,-1).concat(['sourceType'])));
        }else{bimLinkSet(made[i],path,null);cut++;}
      }
    }
    if(!made.length){
      /* nothing was made, so the step this pushed would undo nothing */
      if(!undoSuspend&&UNDO_STACK.length&&UNDO_STACK[UNDO_STACK.length-1]===mark)UNDO_STACK.pop();
      a3dToast('Nothing in "'+entry.name+'" could be inserted');return null;
    }
    for(i=0;i<made.length;i++)A3D.objs.push(made[i]);
    A3D.meshes={};
    var ids=made.map(function(o){return o.id;});
    A3D.selSet=ids.slice();A3D.sel=ids[0];A3D.sel2=null;
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast('Inserted "'+entry.name+'" ('+made.length+' object(s))'+
      (failed?', '+failed+' could not be copied':'')+
      (cut?'; '+cut+' link(s) to objects outside the block were not kept':''));
    return ids;
  }
  function startFamilyPlaceTool(famId){
""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
