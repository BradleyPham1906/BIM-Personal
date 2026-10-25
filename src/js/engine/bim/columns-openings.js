  function bimGetFloorProfile(){
    var o=objById(A3D.sel);
    if(!o)return null;
    /* __acad3dV97: through the source contract, in world coordinates, and carrying the
       source so the floor follows it. This read a moved sketch at its old position and
       recorded nothing about where the profile came from. */
    if((o.t==='sketch'&&!bimIsPoint(o))||
       (o.t==='solid'&&o.bim&&o.bim.type==='wall'&&o.bim.closed)){
      var sb=bimSourceBoundaryWorld(o);
      if(sb.error)return null;
      return {pts:sketchCCW(sb.ring),y:sb.y,sourceType:sb.type,sourceId:o.id};
    }
    return null;
  }
  function startFloorTool(){
    // Floor originally required a pre-SELECTED closed wall/sketch, while Room, Ceiling and Roof
    // all use click-inside-a-boundary. That inconsistency surfaced immediately in real browser
    // testing (drawing a wall, making a Room, then Floor silently did nothing because the Room
    // was now the selection). Floor now accepts either: it uses the current selection if that
    // already yields a valid profile, otherwise it falls back to the same click-inside flow --
    // which also gives it multi-wall-loop detection for free, via bimFindRoomBoundaryAt.
    closeDlg();
    var prof=bimGetFloorProfile();
    if(prof){openFloorDlg(prof);return;}
    bimEnterDraftingMode();
    var lvl=bimGetActiveLevel();
    A3D.sk={tool:'floor',pts:[],y:lvl.elev,on:null};
    a3dToast('Floor: click inside an enclosed wall loop or closed sketch on '+lvl.name);
    paint();
  }
  function startColumnTool(){
    closeDlg();
    bimEnterDraftingMode();
    var lvl=bimGetActiveLevel();
    A3D.sk={tool:'column',pts:[],y:lvl.elev,on:null};
    a3dToast('Column: click a point to place a column on '+lvl.name);
    paint();
  }
  function openColumnDlg(pt,y0){
    closeDlg();
    var lvl=bimGetActiveLevel();
    var d=document.createElement('div');
    d.className='a3d-dlg';
    d.innerHTML='<div class="a3d-dlghd">Column parameters</div>'+
      '<div class="a3d-dlgbody">'+
      '<div class="a3d-dlgrow"><label>Width</label><input type="number" step="any" min="0.02" data-a3dp="w" value="0.4"></div>'+
      '<div class="a3d-dlgrow"><label>Depth</label><input type="number" step="any" min="0.02" data-a3dp="d" value="0.4"></div>'+
      '<div class="a3d-dlgrow"><label>Height</label><input type="number" step="any" min="0.1" data-a3dp="h" value="'+lvl.height+'"></div>'+
      '<div id="a3d-dlgerr" class="a3d-dlgerr"></div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="ok">OK</button></div>';
    el.root.appendChild(d);
    el.dlg=d;
    var wI=d.querySelector('[data-a3dp="w"]'),dI=d.querySelector('[data-a3dp="d"]'),hI=d.querySelector('[data-a3dp="h"]');
    function submit(){
      var w=parseFloat(wI.value),dep=parseFloat(dI.value),h=parseFloat(hI.value);
      var eb=document.getElementById('a3d-dlgerr');
      if(!isFinite(w)||w<=0){eb.textContent='Width must be a positive number';return;}
      if(!isFinite(dep)||dep<=0){eb.textContent='Depth must be a positive number';return;}
      if(!isFinite(h)||h<=0){eb.textContent='Height must be a positive number';return;}
      closeDlg();
      buildColumnSolid(pt,y0,w,dep,h);
    }
    d.addEventListener('click',function(ev){
      var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;
      if(!b)return;
      if(b.getAttribute('data-a3dlg')==='ok')submit();else closeDlg();
    });
    d.addEventListener('keydown',function(ev){
      if(ev.key==='Enter'){ev.preventDefault();ev.stopPropagation();submit();}
      else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();}
    });
    wI.focus();wI.select();
  }
  /* __acad3dV81: rot is the column's orientation about the vertical axis, in radians.

     Before this, a column had no orientation at all, so every rebuild -- including the one
     inside a ROTATION -- drew its footprint axis-aligned at the new centre. A rectangular column
     therefore orbited the rotation centre without ever turning, and a column standing on that
     centre did not move at all: measured, a 0.4 x 1.2 column rotated 45 degrees came back with
     byte-identical geometry. A square column hides the fault entirely, which is why it lasted.

     Defaulting to 0 keeps every existing column and every saved project reading exactly as
     before. */
  /* __acad3dV102: the one turned rectangle -- column and footing builders and every exporter */
  function bimRectFootprint(center,w,dep,rot){
    var hw=w/2,hd=dep/2;
    var quad=[[-hw,-hd],[hw,-hd],[hw,hd],[-hw,hd]];
    var th=rot||0,cs=Math.cos(th),sn=Math.sin(th),qi;
    for(qi=0;qi<quad.length;qi++){
      var qx=quad[qi][0],qz=quad[qi][1];
      quad[qi]=[center[0]+qx*cs-qz*sn,center[1]+qx*sn+qz*cs];
    }
    return quad;
  }
  function bimBuildColumnGeometry(center,y0,w,dep,h,rot,sec){
    /* __acad3dV126: a section, swept up the column and turned with it */
    if(sec){
      var sp=bimProfileProblem(sec);
      if(sp)return {error:'The column\'s section cannot be built: '+sp};
      if(!(h>0))return {error:'Column height must be positive'};
      var c=Math.cos(rot||0),sn=Math.sin(rot||0);
      return {mesh:bimSweepMesh(sec,h,function(y,z,s){return [center[0]+y*c-z*sn,y0+s,center[1]+y*sn+z*c];})};
    }
    var quad=bimRectFootprint(center,w,dep,rot);
    var mesh;
    try{mesh=padMesh(sketchCCW(quad),y0,h);}
    catch(eC){return {error:'Column build failed: '+(eC&&eC.message?eC.message:eC)};}
    if(!mesh||!mesh.f||mesh.f.length<4)return {error:'Column produced an empty solid'};
    return {mesh:mesh};
  }
  function buildColumnSolid(pt,y0,w,dep,h,rot){
    var res=bimBuildColumnGeometry(pt,y0,w,dep,h,rot);
    if(res.error){a3dToast(res.error);return null;}
    pushUndo();
    A3D.counts.column=(A3D.counts.column||0)+1;
    var o={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'solid',name:'Column_'+A3D.counts.column,col:'#8a8f96',pos:[0,0,0],mesh:res.mesh,
      bim:{type:'column',width:w,depth:dep,height:h,baseY:y0,levelId:A3D.activeLevel,center:[pt[0],pt[1]],rotation:rot||0}};
    A3D.objs.push(o);
    A3D.sel=o.id;A3D.sel2=null;
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast(o.name+' created');
    return o;
  }
  function bimRebuildColumn(o,newW,newDep,newH){
    if(!o||!o.bim||o.bim.type!=='column')return false;
    // __acad3dV81: orientation is carried through a resize; editing width must not straighten it.
    /* __acad3dV126: a section's size is the section's */
    if(o.bim.section&&(Math.abs(newW-o.bim.width)>1e-9||Math.abs(newDep-o.bim.depth)>1e-9)){
      a3dToast(o.name+'\'s size is set by its section ('+(bimTypeNameOf(o)||'its type')+'): choose another type to change it');
      return false;
    }
    var res=bimBuildColumnGeometry(o.bim.center,o.bim.baseY,newW,newDep,newH,o.bim.rotation||0,o.bim.section||null);
    if(res.error){a3dToast(res.error);return false;}
    pushUndo();
    o.mesh=res.mesh;
    o.bim.width=newW;o.bim.depth=newDep;o.bim.height=newH;
    bimAfterWallRebuild(o);   // __acad3dV53: sync any linked clone of this column
    refreshTree();paint();saveSoon();
    a3dToast(o.name+' updated');
    return true;
  }
  var FLOOR_MATERIALS=['Concrete Slab','Timber Deck','Steel Deck','Composite Slab'];
  function bimFindWallSegmentAt(wallObj,clickXZ){
    if(!wallObj||!wallObj.bim||!wallObj.bim.centerline||!wallObj.bim.centerline.length)return null;
    var cl=wallObj.bim.centerline,n=cl.length,closed=wallObj.bim.closed;
    var segCount=closed?n:n-1,i,best=null;
    for(i=0;i<segCount;i++){
      var a=cl[i],b=cl[(i+1)%n];
      var dx=b[0]-a[0],dz=b[1]-a[1];
      var len2=dx*dx+dz*dz;
      var t=len2>1e-9?(((clickXZ[0]-a[0])*dx+(clickXZ[1]-a[1])*dz)/len2):0;
      t=Math.max(0.08,Math.min(0.92,t));
      var cx=a[0]+t*dx,cz=a[1]+t*dz;
      var ddx=clickXZ[0]-cx,ddz=clickXZ[1]-cz;
      var d=Math.sqrt(ddx*ddx+ddz*ddz);
      if(!best||d<best.d)best={a:a,b:b,t:t,center:[cx,cz],d:d};
    }
    return best;
  }
  function bimFindWallNear(xz,y0){
    var i,o,best=null,bestSeg=null;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(o.t!=='solid'||!o.bim||o.bim.type!=='wall')continue;
      if(Math.abs(o.bim.baseY-y0)>0.5)continue;
      var seg=bimFindWallSegmentAt(o,xz);
      if(seg&&seg.d<1.5&&(!bestSeg||seg.d<bestSeg.d)){bestSeg=seg;best=o;}
    }
    if(!best)return null;
    return {wall:best,seg:bestSeg};
  }
  function bimBuildOpeningBoxPoly(center,dirXZ,width,thickness,sillY,height){
    var nx=-dirXZ[1],nz=dirXZ[0];
    var hw=width/2,ht=thickness/2+0.05;
    return [
      [center[0]-dirXZ[0]*hw-nx*ht,center[1]-dirXZ[1]*hw-nz*ht],
      [center[0]+dirXZ[0]*hw-nx*ht,center[1]+dirXZ[1]*hw-nz*ht],
      [center[0]+dirXZ[0]*hw+nx*ht,center[1]+dirXZ[1]*hw+nz*ht],
      [center[0]-dirXZ[0]*hw+nx*ht,center[1]-dirXZ[1]*hw+nz*ht]
    ];
  }
  /* __acad3dV62 -- the openings a wall carries, described as parameters rather than as the mesh
     they have already been cut into. One place builds this list so the "cut a new opening" path
     and the "re-cut after a rebuild" path cannot drift apart. `strict` marks a spec that came
     from an EXISTING marker: such a spec must still land within BIM_OPENING_REPLACE_TOL of where
     it was authored or it is skipped rather than silently relocated (the rule the re-cut path
     has always applied); a brand-new opening the user is placing right now has no prior position
     to honour and is not strict. */
  function bimOpeningSpecsFor(wall){
    var out=[],i;
    for(i=0;i<A3D.objs.length;i++){
      var o=A3D.objs[i];
      if(o.t!=='opening'||!o.bim||o.bim.hostWallId!==wall.id)continue;
      out.push({op:o,width:o.bim.width,height:o.bim.height,sillHeight:o.bim.sillHeight||0,
                center:o.bim.center,strict:true});
    }
    return out;
  }
  /* __acad3dV62 -- BUG FIX, and the reason this function replaces the old one-opening-at-a-time
     path entirely.

     What was wrong: cutting an opening used to run csgSubtract against the wall's CURRENT mesh.
     For the first opening that mesh is the clean, freshly-built wall prism and the cut is
     correct. For the second opening the "current mesh" is the OUTPUT of the first BSP cut --
     a surface carrying T-junctions and sliver faces -- and feeding a BSP kernel its own output
     is exactly where naive CSG breaks down. Measured on the plain case of an 8 m wall with two
     0.9 m doors: after the second cut the solid came back at 7.200 m3, the volume of the UNCUT
     wall, with an open (non-closed) shell -- the second boolean had destroyed the first hole and
     produced garbage, while the app still reported "Door opening cut into Wall_1" and the model
     tree still listed both openings. Two openings in one wall is not an exotic case; it is what
     nearly every real wall looks like, and nothing reported the failure.

     What this does instead: every opening on the wall -- the ones already there and the one being
     added -- is resolved back to parameters, the wall's base solid is REGENERATED from its own
     centreline/thickness/height/alignment (bimBuildWallGeometry, the same call every other wall
     edit already rebuilds from, so nothing that survives a thickness edit is lost here either),
     and all the opening boxes are subtracted in a SINGLE boolean. The kernel therefore never
     sees its own output as input, no matter how many openings a wall accumulates. The opening
     boxes are handed to csgSubtract as one concatenated polygon set: they are disjoint closed
     solids, and a BSP built from several disjoint closed solids classifies points against their
     union correctly, so this needs no separate (and, per the stair-railing note above, unreliable)
     BSP union pass first.

     Fail-safe, per this project's rule that a code path must never hand back corrupt geometry:
     the result must pass bimMeshClosureCheck (closed, not corrupt) AND must have LESS volume than
     the uncut base -- the second test is what would have caught the old bug, since the broken
     result's giveaway was a volume that had gone back UP to the uncut figure. On any failure this
     returns an error and the caller leaves the wall untouched. */
  function bimCutOpeningsIntoWall(wall,specs){
    var b=wall&&wall.bim;
    if(!b||b.type!=='wall')return {error:'Openings can only be cut into a wall'};
    if(!b.centerline||!b.centerline.length)
      return {error:'This wall has no parametric data (likely imported) — openings cannot be cut into it'};
    var base=bimBuildWallGeometry(b.centerline,b.baseY,b.height,b.thickness,b.align,b.closed,b.bulges);
    if(base.error)return {error:base.error};
    var cut=[],skipped=[],cutPolys=[],i,k;
    for(i=0;i<specs.length;i++){
      var sp=specs[i];
      if(!sp||!Array.isArray(sp.center)){skipped.push({spec:sp,reason:'it has no recorded position'});continue;}
      if(!(sp.width>0)||!(sp.height>0)){skipped.push({spec:sp,reason:'its width or height is not a positive number'});continue;}
      var seg=bimFindWallSegmentAt(wall,sp.center);
      if(!seg){skipped.push({spec:sp,reason:'the wall has no centreline segment to host it'});continue;}
      if(sp.strict){
        var ddx=seg.center[0]-sp.center[0],ddz=seg.center[1]-sp.center[1];
        var off=Math.sqrt(ddx*ddx+ddz*ddz);
        if(off>BIM_OPENING_REPLACE_TOL){
          skipped.push({spec:sp,reason:'it no longer lies on this wall (nearest valid position is '+off.toFixed(3)+' m away). It was NOT moved there'});
          continue;
        }
      }
      var sill=sp.sillHeight||0;
      var dx=seg.b[0]-seg.a[0],dz=seg.b[1]-seg.a[1],len=Math.sqrt(dx*dx+dz*dz)||1;
      var dir=[dx/len,dz/len];
      try{
        var openPoly=sketchCCW(bimBuildOpeningBoxPoly(seg.center,dir,sp.width,b.thickness,b.baseY+sill,sp.height));
        var openMesh=padMesh(openPoly,b.baseY+sill,sp.height);
        var openPolys=meshPolys({mesh:openMesh,pos:[0,0,0]});
        for(k=0;k<openPolys.length;k++)cutPolys.push(openPolys[k]);
      }catch(eO){
        skipped.push({spec:sp,reason:'its solid could not be built: '+(eO&&eO.message?eO.message:eO)});
        continue;
      }
      cut.push({spec:sp,center:seg.center,dir:dir});
    }
    var baseChk=bimMeshClosureCheck(base.mesh);
    if(!cutPolys.length)return {mesh:base.mesh,cut:cut,skipped:skipped,vol:baseChk.vol,baseVol:baseChk.vol};
    var nm;
    try{
      nm=polysToMesh(csgSubtract(meshPolys({mesh:base.mesh,pos:[0,0,0]}),cutPolys));
    }catch(eD){
      return {error:'Opening cut failed: '+(eD&&eD.message?eD.message:eD)};
    }
    if(!nm||!nm.f||nm.f.length<4)return {error:'Opening cut produced an empty result'};
    var chk=bimMeshClosureCheck(nm);
    if(chk.corrupt||!chk.closed)
      return {error:'Opening cut produced an invalid solid (failed its own topology check) — the wall was left unchanged'};
    if(!(chk.vol<baseChk.vol-1e-9))
      return {error:'Opening cut removed no material — the wall was left unchanged'};
    return {mesh:nm,cut:cut,skipped:skipped,vol:chk.vol,baseVol:baseChk.vol};
  }
  function bimBuildWallOpening(wallObj,clickXZ,width,height,sillHeight){
    var seg=bimFindWallSegmentAt(wallObj,clickXZ);
    if(!seg)return {error:'Could not find a wall segment near that point'};
    /* __acad3dV62: the new opening is cut together with every opening this wall already carries,
       out of a regenerated base solid -- see bimCutOpeningsIntoWall for why re-cutting all of
       them is what makes the second and later openings correct. */
    var fresh={width:width,height:height,sillHeight:sillHeight||0,center:seg.center,strict:false};
    var res=bimCutOpeningsIntoWall(wallObj,bimOpeningSpecsFor(wallObj).concat([fresh]));
    if(res.error)return res;
    var mine=null,i;
    for(i=0;i<res.cut.length;i++)if(res.cut[i].spec===fresh)mine=res.cut[i];
    if(!mine)return {error:'That opening does not fit on this wall at that point'};
    for(i=0;i<res.skipped.length;i++){
      if(res.skipped[i].spec===fresh)continue;
      console.warn('[BIM] While cutting the new opening, '+
        ((res.skipped[i].spec&&res.skipped[i].spec.op&&res.skipped[i].spec.op.name)||'an existing opening')+
        ' could not be re-cut into '+wallObj.name+': '+res.skipped[i].reason+
        ' (its marker is kept, so undo restores a consistent state).');
    }
    /* Every entry in res.skipped is an EXISTING opening (had the new one been skipped, `mine`
       would be null and this function would already have returned an error above). Such an
       opening would silently vanish from the solid while its marker stayed in the tree, so the
       count is handed back for the caller to surface rather than left for the user to spot in
       the 3D view. */
    return {mesh:res.mesh,center:mine.center,dir:mine.dir,skipped:res.skipped,lost:res.skipped.length};
  }
  function startDoorTool(){
    closeDlg();
    bimEnterDraftingMode();
    A3D.sk={tool:'door',pts:[],y:bimGetActiveLevel().elev,on:null};
    a3dToast('Door: click a point along an existing wall');
    paint();
  }
  function startWindowTool(){
    closeDlg();
    bimEnterDraftingMode();
    A3D.sk={tool:'window',pts:[],y:bimGetActiveLevel().elev,on:null};
    a3dToast('Window: click a point along an existing wall');
    paint();
  }
  function openDoorDlg(hit,clickXZ){
    closeDlg();
    var d=document.createElement('div');
    d.className='a3d-dlg';
    d.innerHTML='<div class="a3d-dlghd">Door parameters</div>'+
      '<div class="a3d-dlgbody">'+
      '<div class="a3d-dlgrow"><label>Width</label><input type="number" step="any" min="0.3" data-a3dp="w" value="0.9"></div>'+
      '<div class="a3d-dlgrow"><label>Height</label><input type="number" step="any" min="0.5" data-a3dp="h" value="2.1"></div>'+
      '<div id="a3d-dlgerr" class="a3d-dlgerr"></div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="ok">OK</button></div>';
    el.root.appendChild(d);
    el.dlg=d;
    var wI=d.querySelector('[data-a3dp="w"]'),hI=d.querySelector('[data-a3dp="h"]');
    function submit(){
      var w=parseFloat(wI.value),h=parseFloat(hI.value);
      var eb=document.getElementById('a3d-dlgerr');
      if(!isFinite(w)||w<=0){eb.textContent='Width must be a positive number';return;}
      if(!isFinite(h)||h<=0){eb.textContent='Height must be a positive number';return;}
      closeDlg();
      buildDoorOpening(hit.wall,clickXZ,w,h);
    }
    d.addEventListener('click',function(ev){
      var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;
      if(!b)return;
      if(b.getAttribute('data-a3dlg')==='ok')submit();else closeDlg();
    });
    d.addEventListener('keydown',function(ev){
      if(ev.key==='Enter'){ev.preventDefault();ev.stopPropagation();submit();}
      else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();}
    });
    wI.focus();wI.select();
  }
  function openWindowDlg(hit,clickXZ){
    closeDlg();
    var d=document.createElement('div');
    d.className='a3d-dlg';
    d.innerHTML='<div class="a3d-dlghd">Window parameters</div>'+
      '<div class="a3d-dlgbody">'+
      '<div class="a3d-dlgrow"><label>Width</label><input type="number" step="any" min="0.3" data-a3dp="w" value="1.2"></div>'+
      '<div class="a3d-dlgrow"><label>Height</label><input type="number" step="any" min="0.3" data-a3dp="h" value="1.2"></div>'+
      '<div class="a3d-dlgrow"><label>Sill height</label><input type="number" step="any" min="0" data-a3dp="s" value="0.9"></div>'+
      '<div id="a3d-dlgerr" class="a3d-dlgerr"></div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="ok">OK</button></div>';
    el.root.appendChild(d);
    el.dlg=d;
    var wI=d.querySelector('[data-a3dp="w"]'),hI=d.querySelector('[data-a3dp="h"]'),sI=d.querySelector('[data-a3dp="s"]');
    function submit(){
      var w=parseFloat(wI.value),h=parseFloat(hI.value),s=parseFloat(sI.value);
      var eb=document.getElementById('a3d-dlgerr');
      if(!isFinite(w)||w<=0){eb.textContent='Width must be a positive number';return;}
      if(!isFinite(h)||h<=0){eb.textContent='Height must be a positive number';return;}
      if(!isFinite(s)||s<0){eb.textContent='Sill height must be zero or positive';return;}
      closeDlg();
      buildWindowOpening(hit.wall,clickXZ,w,h,s);
    }
    d.addEventListener('click',function(ev){
      var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;
      if(!b)return;
      if(b.getAttribute('data-a3dlg')==='ok')submit();else closeDlg();
    });
    d.addEventListener('keydown',function(ev){
      if(ev.key==='Enter'){ev.preventDefault();ev.stopPropagation();submit();}
      else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();}
    });
    wI.focus();wI.select();
  }
  function buildDoorOpening(wall,clickXZ,width,height){
    var res=bimBuildWallOpening(wall,clickXZ,width,height,0);
    if(res.error){a3dToast(res.error);return null;}
    pushUndo();
    wall.mesh=res.mesh;
    A3D.counts.door=(A3D.counts.door||0)+1;
    var marker={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'opening',name:'Door_'+A3D.counts.door,layer:wall.layer,
      bim:{type:'door',hostWallId:wall.id,center:res.center,dir:res.dir,width:width,height:height,sillHeight:0}};
    A3D.objs.push(marker);
    A3D.sel=wall.id;A3D.sel2=null;
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast('Door opening cut into '+wall.name);
    // __acad3dV62: an opening already on this wall that could not be re-applied is reported here
    // rather than quietly disappearing from the solid while its marker stays in the tree.
    if(res.lost)a3dToast(res.lost+' existing opening'+(res.lost===1?'':'s')+' could not be re-cut - see console, or undo');
    return marker;
  }
  function buildWindowOpening(wall,clickXZ,width,height,sillHeight){
    var res=bimBuildWallOpening(wall,clickXZ,width,height,sillHeight);
    if(res.error){a3dToast(res.error);return null;}
    pushUndo();
    wall.mesh=res.mesh;
    A3D.counts.window=(A3D.counts.window||0)+1;
    var marker={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'opening',name:'Window_'+A3D.counts.window,layer:wall.layer,
      bim:{type:'window',hostWallId:wall.id,center:res.center,dir:res.dir,width:width,height:height,sillHeight:sillHeight}};
    A3D.objs.push(marker);
    A3D.sel=wall.id;A3D.sel2=null;
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast('Window opening cut into '+wall.name);
    if(res.lost)a3dToast(res.lost+' existing opening'+(res.lost===1?'':'s')+' could not be re-cut - see console, or undo');
    return marker;
  }
  function openFloorDlg(prof){
    closeDlg();
    var lvl=bimGetActiveLevel();
    var d=document.createElement('div');
    d.className='a3d-dlg';
    var opts='',i;
    for(i=0;i<FLOOR_MATERIALS.length;i++)opts+='<option value="'+FLOOR_MATERIALS[i]+'">'+FLOOR_MATERIALS[i]+'</option>';
    d.innerHTML='<div class="a3d-dlghd">Floor parameters</div>'+
      '<div class="a3d-dlgbody">'+
      '<div class="a3d-dlgrow"><label>Thickness</label><input type="number" step="any" min="0.02" data-a3dp="thk" value="0.2"></div>'+
      '<div class="a3d-dlgrow"><label>Material</label><select data-a3dp="mat">'+opts+'</select></div>'+
      '<div id="a3d-dlgerr" class="a3d-dlgerr"></div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="ok">OK</button></div>';
    el.root.appendChild(d);
    el.dlg=d;
    var thkI=d.querySelector('[data-a3dp="thk"]'),matI=d.querySelector('[data-a3dp="mat"]');
    function submit(){
      var thk=parseFloat(thkI.value),mat=matI.value;
      var eb=document.getElementById('a3d-dlgerr');
      if(!isFinite(thk)||thk<=0){eb.textContent='Thickness must be a positive number';return;}
      closeDlg();
      buildFloorSolid(prof,thk,mat,lvl);
    }
    d.addEventListener('click',function(ev){
      var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;
      if(!b)return;
      if(b.getAttribute('data-a3dlg')==='ok')submit();else closeDlg();
    });
    d.addEventListener('keydown',function(ev){
      if(ev.key==='Enter'){ev.preventDefault();ev.stopPropagation();submit();}
      else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();}
    });
    thkI.focus();thkI.select();
  }
