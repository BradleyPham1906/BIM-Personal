  /* ================= __acad3dV124: the Assets library =================
     The owner, in V119: Assets "should be blocks templates premade for easy drag and drop into the
     project not an overview of stuff". Models, blocks and templates first, as tiles; annotation, and
     then what goes ON something -- materials, wall types, patterns -- folded. Every tile and row does
     what its label says: a row with no live target is disabled and says why. */
  var A3D_ASSETS_UI={q:'',closed:{materials:true,sections:true,walltypes:true,patterns:true}};
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
      act('import','Import','Import an OBJ or STL model into the library, or a SketchUp file\'s components as blocks',true,'')+
      act('block','Block','Save the selection to the library as a block',selIds.length>0,'Select the objects to save as a block')+
      act('model','Model','Save the selected solids to the library as one model',hasSolid,'Select a solid to save as a model')+
      act('template','Template','Save this project to the library as a template for new projects',true,'')+
      '</div></div>';
    h+='<div class="a3d-asnote">Drag onto the drawing to place it there, or click to place it at the centre of the view. '+(sel
        ? 'Selected: <b>'+bimEsc(sel.name)+'</b>'
        : 'Materials, sections, wall types and patterns go on the selection, or on what they are dropped on.')+'</div>';
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
        (e.builtin?'':'<button type="button" class="a3d-asdel" data-a3dasdel="'+bimEsc(e.id)+'" title="Remove from the library" aria-label="Remove '+bimEsc(e.name)+' from the library">\u00d7</button>')+
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
    /* __acad3dV169: people, cycles, vehicles, parking and trees, sized from the registry */
    body='';
    for(i=0;i<BIM_ENT.length;i++){
      if(!bimAssetMatch(q,[BIM_ENT[i].name,BIM_ENT[i].cat,'asset','people','scale','entourage']))continue;
      body+=tile('asset:'+BIM_ENT[i].k,bimEntLib(BIM_ENT[i]),BIM_ENT[i].cat,true,'');
    }
    h+=grp('entourage','People, cycles, vehicles, parking and trees',BIM_ENT.length+' item(s)',body,true);
    // Blocks
    var blocks=bimLibEntries('block');body='';
    for(i=0;i<blocks.length;i++){
      if(!bimAssetMatch(q,[blocks[i].name||'',blocks[i].category||'',blocks[i].source||'','block']))continue;   /* __acad3dV163: and where it came from */
      body+=tile('block:'+blocks[i].id,blocks[i],(blocks[i].category==='SketchUp'?'SketchUp, ':'')+(blocks[i].count||0)+' object(s)',true,'');
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
        solidSel?cards[i].kind+' \u00b7 '+cards[i].density+' kg/m\u00b3':'drag onto a solid, or select one',true,'');
    }
    h+=grp('materials','Materials',cards.length+' card(s)',body,false);
    // __acad3dV126: Sections -- the profiled column and beam types, onto a member of their kind
    var secs=[];
    try{bimEnsureTypes();['column','beam'].forEach(function(c){(A3D.types[c]||[]).forEach(function(ty){if(ty.params&&ty.params.profile)secs.push({cat:c,t:ty});});});}
    catch(eS){console.warn('[BIM] The section types could not be read',eS);secs=[];}
    body='';
    for(i=0;i<secs.length;i++){
      var sp=secs[i].t.params,sm=bimMaterialByName(sp.material||''),sbad=bimProfileProblem(sp.profile);
      if(!bimAssetMatch(q,[secs[i].t.name,secs[i].cat,'section',sp.material||'',BIM_PROFILE_SHAPES[sp.profile.shape]||'']))continue;
      body+=row('section',secs[i].cat+'/'+secs[i].t.id,secs[i].t.name,
        (sp.material?sp.material+' ':'')+secs[i].cat+(sm&&sm.density&&!sbad?' \u00b7 '+bimDispNum(bimProfileProps(sp.profile).A*sm.density,1)+' kg/m':''),
        !sbad,'its section cannot be read: '+sbad);
    }
    h+=grp('sections','Sections',secs.length+' section(s)',body,false);
    // Wall types -- made active for the next wall, and applied to the wall they go on
    var wts=[];
    try{bimEnsureTypes();wts=A3D.types.wall||[];}catch(eW){wts=[];}
    body='';
    for(i=0;i<wts.length;i++){
      if(!bimAssetMatch(q,[wts[i].name,'wall type']))continue;
      body+=row('walltype',wts[i].id,wts[i].name,(A3D.activeWallType===wts[i].id?'active \u00b7 ':'')+'make active',true,'');
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
    if(kind==='asset')return !!bimEntPlace(key,at||bimViewCentrePlan());   /* __acad3dV169 */
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
    if(kind==='section'){   /* __acad3dV126 */
      var sl=key.indexOf('/'),scat=key.slice(0,sl),sty=bimFindType(scat,key.slice(sl+1));
      if(!sty){a3dToast('That section is no longer in the project');return false;}
      var tg=drop?(o?[o]:[]):bimAssetSelIds().map(objById);
      tg=tg.filter(function(x){return x&&x.bim&&x.bim.type===scat;});
      if(!tg.length){
        a3dToast(drop?(o?sty.name+' is a '+scat+' section: drop it on a '+scat:'Drop a section on a '+scat)
                     :'Select a '+scat+', or drag '+sty.name+' onto one');
        return false;
      }
      pushUndo();
      var sok=[],sno=[];
      tg.forEach(function(x){if(bimAssignTypeTo(x,scat,sty.id))sok.push(x.name);else{sno.push(x.name);console.warn('[BIM] Section '+sty.id+' could not be applied to '+x.name);}});
      A3D.meshes={};refreshTree();refreshProps();paint();saveSoon();
      a3dToast(sok.length?(sok.length===1?sok[0]+' is now '+sty.name:sok.length+' '+scat+'s are now '+sty.name)+(sno.length?'; not '+sno.join(', '):'')
                         :sty.name+' could not be applied - see the console');
      return sok.length>0;
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
  /* The Assets tab, with one group unfolded and brought into view. */
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
  /* the four actions above the library */
  function bimAssetsAct(k){
    if(k==='import'){
      var inp=document.createElement('input');
      inp.type='file';inp.accept='.obj,.stl,.skp';
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
