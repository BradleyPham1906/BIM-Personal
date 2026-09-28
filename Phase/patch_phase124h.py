"""patch_phase124h.py -- V124: a copy follows what it was copied with, never the original's sources.

Found by falsifying V124's block links. A copy made by bimDuplicateObject (Ctrl+D, the gizmo's
Ctrl-drag copy, ARRAYRECT, a block insert) is the original's record copied and moved. Where that
record holds a link to another object, the copy held the SAME link -- so it followed the ORIGINAL's
source:

  - a hatch traced inside a sketch keeps a region: a seed point and the shapes that bound it. Its
    copy kept the original's seed and the original's sketch, so the moment that sketch was edited the
    copy re-traced ONTO the original -- measured in V123: Ctrl+D a hatch, drag a corner of its
    sketch, and the copy jumps across the drawing onto the original. Every region-traced dependent
    that is copied as a record (hatches; ceilings) did the same;
  - other copy paths build a fresh record and drop a room's or floor's source silently, so an inserted
    room did not follow its inserted wall (bug 1 of this phase).

One rule now, bimRelinkCopies, run by every path that copies by translation. It reads each link from
the ORIGINAL record (A3D_BLOCK_LINKS and the region), points it at the copy of its target when the
target was copied in the same operation, and drops it when it was not -- the copy is then a shape
of its own, as a copy of a room alone always was. A region is re-seeded where the copy is, in the
copy's own frame, on the copy's plane. The block insert announces links dropped; the other copy
paths say so too, since before this the copy silently followed something it was not bounded by.

The polar array builds its copies from transformed geometry and carries no link or region, so it
does not need this."""
NAME = 'patch_phase124h.py'
BASE = '74d1afae5017c2cfd29a03d17e9c29bc9a29f6050743087efc011995a4bd1496'
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


# ---- the rule, beside the block code that first needed it
rep("""  function bimLinkGet(o,path){""", r"""  /* __acad3dV124: every copy made by translation is relinked here. pairs is [[original, copy], ...]
     for ONE copy operation; (dx, dz) is how far it moved in plan, dY how far up. Each link is read
     from the ORIGINAL -- a copy path decides what it carries, and a link it dropped or kept by
     accident must not decide what the copy follows. A link to an object copied in the same
     operation points at that object's copy; any other link is dropped. Returns how many were
     dropped. */
  function bimRelinkCopies(pairs,dx,dz,dY){
    var map={},cut=0,i,j;
    dx=dx||0;dz=dz||0;dY=dY||0;
    for(i=0;i<pairs.length;i++)map[pairs[i][0].id]=pairs[i][1].id;
    for(i=0;i<pairs.length;i++){
      var from=pairs[i][0],c=pairs[i][1];
      for(j=0;j<A3D_BLOCK_LINKS.length;j++){
        var path=A3D_BLOCK_LINKS[j];
        if(path.length===2&&!c[path[0]])continue;
        var v=bimLinkGet(from,path);
        if(v===undefined||v===null||v===''){
          /* nothing to carry -- and nothing the copy may keep of its own */
          if(bimLinkGet(c,path))bimLinkSet(c,path,null);
          continue;
        }
        if(map[v]){
          bimLinkSet(c,path,map[v]);
          /* a source carries its kind beside it */
          if(path[path.length-1]==='sourceId')bimLinkSet(c,path.slice(0,-1).concat(['sourceType']),bimLinkGet(from,path.slice(0,-1).concat(['sourceType'])));
        }else{bimLinkSet(c,path,null);cut++;}
      }
      /* a traced region: its seed and the shapes that bound it */
      if(bimIsRegionDep(from)){
        var mem=[],k,ms=from.region.members||[];
        for(k=0;k<ms.length;k++)if(map[ms[k]])mem.push(map[ms[k]]);
        if(mem.length){
          var q0=bimObjOffset(from),q1=bimObjOffset(c),rg=bimCloneRegion(from.region);
          rg.seed=[rg.seed[0]+q0[0]-q1[0]+dx,rg.seed[1]+q0[2]-q1[2]+dz];
          rg.y=(rg.y||0)+q0[1]-q1[1]+dY;
          rg.members=mem;rg.sig='';
          c.region=rg;
        }else{
          if(c.region)c.region=null;
          cut++;
        }
      }else if(c.region){
        c.region=null;
      }
    }
    return cut;
  }
  function bimLinkGet(o,path){""")

# ---- the block insert runs it (its own loop, 124c's, goes)
rep("""    /* The links are read from the SAVED record, not from the copy: a copy does not carry every link
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
""", """    /* the links, read from the SAVED records (bimRelinkCopies) */
    var cut=bimRelinkCopies(made.map(function(c,k){return [from[k],c];}),dx,dz,dY);
""")

# ---- Ctrl+D
rep("""    pushUndo();
    var newIds=[],i;
    for(i=0;i<ids.length;i++){
      var o=objById(ids[i]);
      if(!o)continue;
      var copy=bimDuplicateObject(o,1,1);
      if(copy){A3D.objs.push(copy);newIds.push(copy.id);}
    }
    if(!newIds.length){a3dToast('Nothing could be duplicated (unsupported object type)');return;}
    A3D.selSet=newIds;
    A3D.sel=newIds[0];A3D.sel2=null;
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast('Duplicated '+newIds.length+' object(s)');""", """    pushUndo();
    var newIds=[],pairs=[],i;
    for(i=0;i<ids.length;i++){
      var o=objById(ids[i]);
      if(!o)continue;
      var copy=bimDuplicateObject(o,1,1);
      if(copy){A3D.objs.push(copy);newIds.push(copy.id);pairs.push([o,copy]);}
    }
    if(!newIds.length){a3dToast('Nothing could be duplicated (unsupported object type)');return;}
    var cut=bimRelinkCopies(pairs,1,1,0);   /* __acad3dV124 */
    A3D.selSet=newIds;
    A3D.sel=newIds[0];A3D.sel2=null;
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast('Duplicated '+newIds.length+' object(s)'+bimRelinkNote(cut));""")

# ---- the gizmo's Ctrl-drag copy (made where the original is; the drag then moves it)
rep("""    var made=[],i,prevSel=A3D.sel,prevSet=(A3D.selSet||[]).slice();
    for(i=0;i<ids.length;i++){
      var o=objById(ids[i]);
      if(!o)continue;
      var c=bimDuplicateObject(o,0,0);
      if(c){A3D.objs.push(c);made.push(c.id);}
    }""", """    var made=[],pairs=[],i,prevSel=A3D.sel,prevSet=(A3D.selSet||[]).slice();
    for(i=0;i<ids.length;i++){
      var o=objById(ids[i]);
      if(!o)continue;
      var c=bimDuplicateObject(o,0,0);
      if(c){A3D.objs.push(c);made.push(c.id);pairs.push([o,c]);}
    }
    var cut=pairs.length?bimRelinkCopies(pairs,0,0,0):0;   /* __acad3dV124 */""")
rep("""    a3dToast('Copying '+made.length+' object(s) - the originals stay where they are');""",
    """    a3dToast('Copying '+made.length+' object(s) - the originals stay where they are'+bimRelinkNote(cut));""")

# ---- ARRAYRECT: each step of the array is one copy operation
rep("""    for(i=0;i<ids.length;i++){
      var o=objById(ids[i]);
      if(!o)continue;
      for(k=1;k<n;k++){
        var copy=bimDuplicateObject(o,ax*k,az*k);
        if(copy){A3D.objs.push(copy);newIds.push(copy.id);}
      }
    }
    if(!newIds.length){a3dToast('Array failed: unsupported object type(s)');return;}
    A3D.selSet=ids.concat(newIds);
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast('Array created '+newIds.length+' cop'+(newIds.length===1?'y':'ies'));""",
    """    var steps={},cut=0;   /* __acad3dV124: the copies of one step are relinked among themselves */
    for(i=0;i<ids.length;i++){
      var o=objById(ids[i]);
      if(!o)continue;
      for(k=1;k<n;k++){
        var copy=bimDuplicateObject(o,ax*k,az*k);
        if(copy){A3D.objs.push(copy);newIds.push(copy.id);(steps[k]=steps[k]||[]).push([o,copy]);}
      }
    }
    if(!newIds.length){a3dToast('Array failed: unsupported object type(s)');return;}
    for(k=1;k<n;k++)if(steps[k])cut+=bimRelinkCopies(steps[k],ax*k,az*k,0);
    A3D.selSet=ids.concat(newIds);
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast('Array created '+newIds.length+' cop'+(newIds.length===1?'y':'ies')+bimRelinkNote(cut));""")

# ---- what a copy's toast says when it dropped a link
rep("""  function bimLinkGet(o,path){""", """  function bimRelinkNote(cut){
    return cut?'; '+cut+' link(s) to shapes that were not copied with them were not kept -- the copies are shapes of their own':'';
  }
  function bimLinkGet(o,path){""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
