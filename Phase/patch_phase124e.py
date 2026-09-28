"""patch_phase124e.py -- V124: the Assets tab is the library.

The owner, in V119: Assets "should be blocks templates premade for easy drag and drop into the
project not an overview of stuff". The tab was a list of text rows. It is now the library:

  - a search box, and four actions: Import (an OBJ or STL, with 124b's unit), Block (the selection),
    Model (the selected solids as one mesh), Template (this project);
  - Models, Blocks and Templates first, as tiles with a thumbnail; the starter set among the models;
    what the user added carries a remove button that asks first;
  - Annotation, Materials, Wall Types and Patterns after them. The last three go ON something rather
    than INTO the project, so they start folded; every group header folds and unfolds, and a search
    shows every group with a match whatever its fold.

A click places a model or inserts a block at the centre of the view -- where it can be seen, and
selected, so the next gesture moves it -- rather than at the level's origin, which could be off
screen. A template opens a new project. Dropping (124f) places at the drop point instead.

Materials and patterns stay live with nothing selected: they are also dropped on an object, which
needs no selection. A click with nothing selected says what to do and changes nothing.

bimAssetAction takes an optional drop -- {pt:[x, z], obj} -- so a click and a drop run the same code
and differ only in where and on what."""
NAME = 'patch_phase124e.py'
BASE = '263a3238533bf9920743d9e462d5bb24d8c8d7d2cc0f7697981b4b514513aac9'
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


def span(head, tail, new, lines):
    global t
    c = t.count(head)
    if c != 1:
        sys.exit('ABORT: span head %d occurrences, expected 1: %r' % (c, head[:90]))
    s = t.index(head)
    e = t.find(tail, s + len(head))
    if e < 0:
        sys.exit('ABORT: span tail not found: %r' % tail[:90])
    got = t[s:e].count('\n')
    if got != lines:
        sys.exit('ABORT: span is %d lines, expected %d' % (got, lines))
    t = t[:s] + esc(new) + t[e:]


# ---- 1. the panel, its actions and its refresh
span("  /* ---- the BIM asset libraries ----\n", "  /* The pass itself. Idempotent", r"""  /* ================= __acad3dV124: the Assets library =================
     The owner, in V119: Assets "should be blocks templates premade for easy drag and drop into the
     project not an overview of stuff". Models, blocks and templates first, as tiles; annotation, and
     then what goes ON something -- materials, wall types, patterns -- folded. Every tile and row does
     what its label says: a row with no live target is disabled and says why. */
  var A3D_ASSETS_UI={q:'',closed:{materials:true,walltypes:true,patterns:true}};
  function bimAssetMatch(q,words){
    if(!q)return true;
    return words.join(' ').toLowerCase().indexOf(q)>=0;
  }
  function bimAssetSelIds(){
    return (A3D.selSet&&A3D.selSet.length)?A3D.selSet.slice():(A3D.sel?[A3D.sel]:[]);
  }
  function bimAssetsHtml(){
    var selId=A3D.sel,sel=objById(selId),q=String(A3D_ASSETS_UI.q||'').trim().toLowerCase();
    var selIds=bimAssetSelIds(),hasSolid=false,i;
    for(i=0;i<selIds.length;i++){
      var so=objById(selIds[i]),sm=so?meshOf(so):null;
      if(sm&&sm.f&&sm.f.length){hasSolid=true;break;}
    }
    function act(k,label,tip,live,why){
      return '<button type="button" class="a3d-asact" data-a3dasact="'+k+'"'+(live?' title="'+bimEsc(tip)+'"':' disabled title="'+bimEsc(why)+'"')+'>'+bimEsc(label)+'</button>';
    }
    var h='<div class="a3d-assets">';
    h+='<div class="a3d-astools"><input type="search" class="a3d-assearch" data-a3dassearch placeholder="Search the library" value="'+bimEsc(A3D_ASSETS_UI.q||'')+'">'+
      '<div class="a3d-asacts">'+
      act('import','Import','Import an OBJ or STL model into the library',true,'')+
      act('block','Block','Save the selection to the library as a block',selIds.length>0,'Select the objects to save as a block')+
      act('model','Model','Save the selected solids to the library as one model',hasSolid,'Select a solid to save as a model')+
      act('template','Template','Save this project to the library as a template for new projects',true,'')+
      '</div></div>';
    h+='<div class="a3d-asnote">Drag onto the drawing to place it there, or click to place it at the centre of the view. '+(sel
        ? 'Selected: <b>'+bimEsc(sel.name)+'</b>'
        : 'Materials, wall types and patterns go on the selection, or on what they are dropped on.')+'</div>';
    var shown=0;
    function grp(id,title,sub,body,tiles){
      if(!body)return '';
      var shut=!!A3D_ASSETS_UI.closed[id]&&!q;
      return '<div class="a3d-asgrp'+(shut?' shut':'')+'" data-a3dassetgrp="'+id+'" role="button" tabindex="0" aria-expanded="'+(shut?'false':'true')+'">'+
        '<span>'+bimEsc(title)+'</span><span class="a3d-assub">'+bimEsc(sub)+'</span></div>'+
        '<div class="a3d-asbody'+(tiles?' a3d-astiles':'')+(shut?' shut':'')+'">'+body+'</div>';
    }
    function row(kind,key,label,meta,live,why){
      shown++;
      return '<button type="button" class="a3d-asrow'+(live?'':' off')+'" data-a3dassets="'+kind+':'+bimEsc(key)+'"'+
        (live?'':' disabled title="'+bimEsc(why)+'"')+'>'+
        '<span class="a3d-asnm">'+bimEsc(label)+'</span>'+
        '<span class="a3d-asmeta">'+bimEsc(live?meta:why)+'</span></button>';
    }
    function tile(spec,e,meta,live,why){
      shown++;
      var th=bimAssetThumb(e);
      return '<div class="a3d-ascell"><button type="button" class="a3d-astile'+(live?'':' off')+'" data-a3dassets="'+bimEsc(spec)+'"'+
        (live?' title="'+bimEsc(e.name+' -- drag onto the drawing, or click')+'"':' disabled title="'+bimEsc(why)+'"')+'>'+
        '<span class="a3d-asimg">'+(th?'<img src="'+th+'" alt="" draggable="false">':'')+'</span>'+
        '<span class="a3d-asnm">'+bimEsc(e.name||'(unnamed)')+'</span>'+
        '<span class="a3d-asmeta">'+bimEsc(live?meta:why)+'</span></button>'+
        (e.builtin?'':'<button type="button" class="a3d-asdel" data-a3dasdel="'+bimEsc(e.id)+'" title="Remove from the library" aria-label="Remove '+bimEsc(e.name)+' from the library">×</button>')+
        '</div>';
    }
    // Models: the user's first, then the starter set
    var models=bimLibEntries('model').concat(A3D_ASSET_BUILTINS),body='';
    for(i=0;i<models.length;i++){
      var fm=models[i].mesh,hasGeom=!!(fm&&fm.f&&fm.f.length);
      if(!bimAssetMatch(q,[models[i].name||'',models[i].category||'','model']))continue;
      /* A family whose mesh carries no faces places an object nobody can see: disabled, and says why. */
      body+=tile('family:'+models[i].id,models[i],(models[i].builtin?'Starter':(models[i].category||'Other')),hasGeom,'this family has no geometry');
    }
    if(!q&&!models.length)body='<div class="a3d-asempty">No models yet.</div>';
    h+=grp('families','Models',models.length+' item(s)',body,true);
    // Blocks
    var blocks=bimLibEntries('block');body='';
    for(i=0;i<blocks.length;i++){
      if(!bimAssetMatch(q,[blocks[i].name||'','block']))continue;
      body+=tile('block:'+blocks[i].id,blocks[i],(blocks[i].count||0)+' object(s)',true,'');
    }
    if(!q&&!blocks.length)body='<div class="a3d-asempty">No blocks yet: select objects and click Block.</div>';
    h+=grp('blocks','Blocks',blocks.length+' item(s)',body,true);
    // Templates
    var tpls=bimLibEntries('template');body='';
    for(i=0;i<tpls.length;i++){
      if(!bimAssetMatch(q,[tpls[i].name||'','template','project']))continue;
      body+=tile('template:'+tpls[i].id,tpls[i],'new project',true,'');
    }
    if(!q&&!tpls.length)body='<div class="a3d-asempty">No templates yet: click Template to keep this project as a start for new ones.</div>';
    h+=grp('templates','Templates',tpls.length+' item(s)',body,true);
    // Annotation -- placed, so none needs a selection
    body='';
    for(i=0;i<BIM_NOTE_KINDS.length;i++){
      if(!bimAssetMatch(q,[BIM_NOTE_KINDS[i].label,BIM_NOTE_KINDS[i].why,'annotation']))continue;
      body+=row('note',BIM_NOTE_KINDS[i].k,BIM_NOTE_KINDS[i].label,BIM_NOTE_KINDS[i].why,true,'');
    }
    h+=grp('annotation','Annotation',BIM_NOTE_KINDS.length+' item(s)',body,false);
    // Materials -- on the selected solid, or on the solid they are dropped on
    var cards=bimMaterialCards()||[],solidSel=!!(sel&&sel.t==='solid');
    body='';
    for(i=0;i<cards.length;i++){
      if(!bimAssetMatch(q,[cards[i].name,cards[i].kind,'material']))continue;
      body+=row('material',cards[i].name,cards[i].name,
        solidSel?cards[i].kind+' · '+cards[i].density+' kg/m³':'drag onto a solid, or select one',true,'');
    }
    h+=grp('materials','Materials',cards.length+' card(s)',body,false);
    // Wall types -- made active for the next wall, and applied to the wall they go on
    var wts=[];
    try{bimEnsureTypes();wts=A3D.types.wall||[];}catch(eW){wts=[];}
    body='';
    for(i=0;i<wts.length;i++){
      if(!bimAssetMatch(q,[wts[i].name,'wall type']))continue;
      body+=row('walltype',wts[i].id,wts[i].name,(A3D.activeWallType===wts[i].id?'active · ':'')+'make active',true,'');
    }
    h+=grp('walltypes','Wall Types',wts.length+' type(s)',body,false);
    // Patterns -- a presentation graphics override
    var pats=BIM_HATCH_PATTERNS||[];
    body='';
    for(i=0;i<pats.length;i++){
      if(!bimAssetMatch(q,[bimPatternLabel(pats[i]),'pattern hatch']))continue;
      body+=row('pattern',pats[i],bimPatternLabel(pats[i]),sel?'presentation fill':'drag onto an element, or select one',true,'');
    }
    h+=grp('patterns','Patterns',pats.length+' pattern(s)',body,false);
    if(q&&!shown)h+='<div class="a3d-asempty">Nothing in the library matches "'+bimEsc(A3D_ASSETS_UI.q)+'".</div>';
    h+='</div>';
    return h;
  }
  function bimWallTypeName(id){
    try{bimEnsureTypes();}catch(eT){}
    var a=(A3D.types&&A3D.types.wall)||[],i;
    for(i=0;i<a.length;i++)if(a[i].id===id)return a[i].name;
    return id;
  }
  /* the plan point at the centre of what can be seen, on the active level */
  function bimViewCentrePlan(){
    var s=bimSafeViewRect(),lvl=bimGetActiveLevel();
    var g=groundPoint(s.x+s.w/2,s.y+s.h/2,lvl?lvl.elev:0);
    if(!g){console.warn('[BIM] Could not un-project the view centre; using the origin.');return [0,0];}
    return [g[0],g[2]];
  }
  /* One path for a click and a drop. drop is {pt:[x, z], obj} -- where it was let go and what it was
     let go on -- or absent for a click, which places at the view centre and applies to the
     selection. */
  function bimAssetAction(spec,drop){
    var parts=spec.split(':'),kind=parts[0],key=parts.slice(1).join(':');
    var o=drop?(drop.obj||null):objById(A3D.sel);
    var at=drop&&drop.pt?drop.pt:null;
    if(kind==='note'){
      if(key==='image')return bimPlaceImageNote(at);
      return !!bimPlaceNoteAtViewCentre(key,null,at);
    }
    if(kind==='family'){
      var fam=bimFamilyLibraryGet(key);
      if(!fam){a3dToast('That model is no longer in the library');return false;}
      if(!(fam.mesh&&fam.mesh.f&&fam.mesh.f.length)){a3dToast('"'+fam.name+'" has no geometry to place');return false;}
      /* Left SELECTED, so the gizmo is already on it and the next gesture moves it. */
      bimPlaceFamilyInstance(fam,at||bimViewCentrePlan());
      return true;
    }
    if(kind==='block'){
      var blk=bimFamilyLibraryGet(key);
      if(!blk){a3dToast('That block is no longer in the library');return false;}
      return !!bimInsertBlock(blk,at||bimViewCentrePlan());
    }
    if(kind==='template'){
      var tpl=bimFamilyLibraryGet(key);
      if(!tpl){a3dToast('That template is no longer in the library');return false;}
      return !!bimTemplateUse(tpl);
    }
    if(kind==='material'){
      if(!o||o.t!=='solid'){a3dToast(drop?'Drop a material on a solid':'Select a solid, or drag the material onto one');return false;}
      pushUndo();
      if(!bimSetMaterial(o,key)){a3dToast('That material could not be assigned');return false;}
      refreshTree();refreshProps();paint();saveSoon();
      a3dToast(key+' assigned to '+o.name);
      return true;
    }
    if(kind==='walltype'){
      A3D.activeWallType=key;
      var nm=bimWallTypeName(key);
      if(o&&o.bim&&o.bim.type==='wall'){
        pushUndo();
        bimSetWallTypeOf(o,key);
        a3dToast(nm+' applied to '+o.name+', and is now the active wall type');
      }else{
        a3dToast(nm+' is now the active wall type');
      }
      refreshTree();refreshProps();refreshAssets();paint();saveSoon();
      return true;
    }
    if(kind==='pattern'){
      if(!o){a3dToast(drop?'Drop a pattern on an element':'Select an element, or drag the pattern onto one');return false;}
      pushUndo();
      bimSetGraphicsOverride(o,'presentation','pattern',key);
      refreshProps();paint();saveSoon();
      a3dToast(bimPatternLabel(key)+' applied to '+o.name+' (presentation)');
      return true;
    }
    return false;
  }
  /* the four actions above the library */
  function bimAssetsAct(k){
    if(k==='import'){
      var inp=document.createElement('input');
      inp.type='file';inp.accept='.obj,.stl';
      inp.onchange=function(){
        var f=inp.files&&inp.files[0];
        if(f)bimImportFamilyFile(f);
      };
      inp.click();
      return true;
    }
    if(k==='block'){openSaveBlockDlg();return true;}
    if(k==='model'){openSaveAsFamilyDlg();return true;}
    if(k==='template'){openSaveTemplateDlg();return true;}
    return false;
  }
  function bimAssetRemove(id){
    var e=bimFamilyLibraryGet(id);
    if(!e||e.builtin)return false;
    var kd=bimAssetKind(e);
    var what=kd==='template'?'Projects already made from it are not affected.':(kd==='block'?'Blocks already inserted are not affected.':'Models already placed are not affected.');
    if(!confirm('Remove "'+e.name+'" from the library? '+what))return false;
    if(!bimFamilyLibraryRemove(id))return false;
    refreshFamilyPanel();
    a3dToast('Removed "'+e.name+'" from the library');
    return true;
  }
  function refreshAssets(){
    var panel=document.getElementById('a3d-leftpanel');
    var shell=document.getElementById('a3d-shell');
    if(!panel||!shell||shell.dataset.tab!=='assets'||!A3D.on)return;
    var host=panel.querySelector('.a3d-assets');
    if(!host)return;
    /* a search re-renders the list as it is typed into, so the box keeps its focus and caret */
    var sI=host.querySelector('[data-a3dassearch]'),had=!!(sI&&document.activeElement===sI);
    var s0=had?sI.selectionStart:0,s1=had?sI.selectionEnd:0;
    var wrap=host.parentNode,top=wrap?wrap.scrollTop:0;
    var next=document.createElement('div');
    next.innerHTML=bimAssetsHtml();
    host.parentNode.replaceChild(next.firstChild,host);
    if(wrap)wrap.scrollTop=top;
    if(had){
      var nI=panel.querySelector('[data-a3dassearch]');
      if(nI){nI.focus();try{nI.setSelectionRange(s0,s1);}catch(eS){}}
    }
  }
""", 133)

# ---- 2. a note placed at a point, not only at the view centre
rep("""  function bimPlaceNoteAtViewCentre(kind,opts){
    var s=bimSafeViewRect();
    var lvl=bimGetActiveLevel();
    var g=groundPoint(s.x+s.w/2,s.y+s.h/2,lvl?lvl.elev:0);
    if(!g){""", """  function bimPlaceNoteAtViewCentre(kind,opts,atPt){
    var s=bimSafeViewRect();
    var lvl=bimGetActiveLevel();
    /* __acad3dV124: a note dropped from the library goes where it was dropped */
    var g=atPt?[atPt[0],lvl?lvl.elev:0,atPt[1]]:groundPoint(s.x+s.w/2,s.y+s.h/2,lvl?lvl.elev:0);
    if(!g){""")
rep("""  function bimPlaceImageNote(){""", """  function bimPlaceImageNote(atPt){""")
rep("""      rd.onload=function(){bimPlaceNoteAtViewCentre('image',{src:String(rd.result)});};""",
    """      rd.onload=function(){bimPlaceNoteAtViewCentre('image',{src:String(rd.result)},atPt);};""")

# ---- 3. the panel's own controls
rep("""    var shell=document.getElementById('a3d-shell');
    if(shell&&!shell.__a3dAssetsWired){
      shell.__a3dAssetsWired=true;
      shell.addEventListener('click',function(ev){
        var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dassets]'):null;
        if(!b||b.disabled)return;
        ev.preventDefault();ev.stopPropagation();
        try{bimAssetAction(b.getAttribute('data-a3dassets'));}
        catch(eA){console.warn('[BIM] Asset action failed',eA);a3dToast('That asset action failed — see the console');}
        refreshAssets();
      },true);
    }
""", """    var shell=document.getElementById('a3d-shell');
    if(shell&&!shell.__a3dAssetsWired){
      shell.__a3dAssetsWired=true;
      shell.addEventListener('click',function(ev){
        var cl=function(s){return ev.target&&ev.target.closest?ev.target.closest(s):null;};
        /* __acad3dV124: the library's own controls */
        var ab=cl('[data-a3dasact]'),db=cl('[data-a3dasdel]'),gh=cl('[data-a3dassetgrp]');
        if(ab||db||gh){
          ev.preventDefault();ev.stopPropagation();
          try{
            if(ab&&!ab.disabled)bimAssetsAct(ab.getAttribute('data-a3dasact'));
            else if(db)bimAssetRemove(db.getAttribute('data-a3dasdel'));
            else if(gh){var gid=gh.getAttribute('data-a3dassetgrp');A3D_ASSETS_UI.closed[gid]=!A3D_ASSETS_UI.closed[gid];refreshAssets();}
          }catch(eL){console.warn('[BIM] Library action failed',eL);a3dToast('That library action failed — see the console');}
          return;
        }
        var b=cl('[data-a3dassets]');
        if(!b||b.disabled)return;
        ev.preventDefault();ev.stopPropagation();
        try{bimAssetAction(b.getAttribute('data-a3dassets'));}
        catch(eA){console.warn('[BIM] Asset action failed',eA);a3dToast('That asset action failed — see the console');}
        refreshAssets();
      },true);
      shell.addEventListener('input',function(ev){   /* __acad3dV124: the search */
        var s=ev.target&&ev.target.matches&&ev.target.matches('[data-a3dassearch]')?ev.target:null;
        if(!s)return;
        A3D_ASSETS_UI.q=s.value;
        refreshAssets();
      });
      shell.addEventListener('keydown',function(ev){
        var tg=ev.target;
        if(tg&&tg.matches&&tg.matches('[data-a3dassearch]')&&ev.key==='Escape'&&tg.value){
          ev.preventDefault();ev.stopPropagation();tg.value='';A3D_ASSETS_UI.q='';refreshAssets();
          return;
        }
        if(tg&&tg.matches&&tg.matches('[data-a3dassetgrp]')&&(ev.key==='Enter'||ev.key===' ')){
          ev.preventDefault();ev.stopPropagation();tg.click();
        }
      },true);
    }
""")

# ---- 4. its look
rep(""".a3d-impprev{display:flex;""", """.a3d-astools{display:flex;flex-direction:column;gap:6px;margin-bottom:6px}
.a3d-assearch{width:100%;box-sizing:border-box;background:#1b1f24;border:1px solid #333a42;border-radius:6px;color:#dfe4ea;padding:6px 8px;font:inherit}
.a3d-assearch:focus{outline:none;border-color:#4d86c0}
.a3d-asacts{display:grid;grid-template-columns:repeat(4,1fr);gap:4px}
.a3d-asact{background:#262b31;border:1px solid #333a42;border-radius:5px;color:#d5dae0;padding:5px 2px;font:inherit;font-size:10.5px;cursor:pointer}
.a3d-asact:hover{background:#2f353c;border-color:#46505a}
.a3d-asact:disabled{opacity:.45;cursor:default}
.a3d-asgrp{cursor:pointer;user-select:none}
.a3d-asgrp>span:first-child::before{content:'\\25be';display:inline-block;width:12px;color:#7d8590}
.a3d-asgrp.shut>span:first-child::before{content:'\\25b8'}
.a3d-asbody.shut{display:none}
.a3d-astiles{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:6px}
.a3d-ascell{position:relative;min-width:0}
.a3d-astile{display:flex;flex-direction:column;align-items:stretch;width:100%;background:#22262b;border:1px solid #2f353c;border-radius:7px;padding:5px;color:#d5dae0;cursor:grab;font:inherit;text-align:left;touch-action:none}
.a3d-astile:hover{border-color:#4d86c0;background:#262b31}
.a3d-astile.off{opacity:.45;cursor:default}
.a3d-astile .a3d-asnm{margin-top:4px;font-size:11px}
.a3d-astile .a3d-asmeta{font-size:9.5px}
.a3d-asimg{display:block;height:64px;border-radius:5px;background:#1b1f24;overflow:hidden}
.a3d-asimg img{display:block;width:100%;height:100%;object-fit:contain;pointer-events:none}
.a3d-asdel{position:absolute;top:3px;right:3px;width:20px;height:20px;padding:0;border-radius:4px;border:1px solid #3a4048;background:rgba(27,31,36,.85);color:#9aa3ad;font-size:12px;line-height:1;cursor:pointer}
.a3d-asdel:hover{color:#e08080;border-color:#e08080}
.a3d-impprev{display:flex;""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
