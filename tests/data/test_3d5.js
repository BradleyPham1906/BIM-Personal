/* test_3d5.js - Phase 42 assertions: level datum integrity, grid datums, beam engine.
   Evaluated inside the real page by bim_phase42_browser_tests.py, so it exercises the
   shipped code paths rather than a prototype copy. Returns {pass,fail,lines}. */
(function(){
  var pass=0,fail=0,lines=[];
  function ok(n,c,d){
    if(c){pass++;lines.push('  PASS  '+n+(d?' ('+d+')':''));}
    else{fail++;lines.push('  FAIL  '+n+(d?' ('+d+')':''));}
  }
  function near(a,b,t){return Math.abs(a-b)<=(t===undefined?1e-6:t);}
  function objs(){return window.__a3dState().objs;}
  function byName(n){var a=objs(),i;for(i=0;i<a.length;i++)if(a[i].name===n)return a[i];return null;}
  function meshY(o){var mn=1e9,mx=-1e9,i;for(i=0;i<o.mesh.v.length;i++){mn=Math.min(mn,o.mesh.v[i][1]);mx=Math.max(mx,o.mesh.v[i][1]);}return [mn,mx];}
  function topo(m){
    var und={},dir={},dup=0,bad=0,vol=0,i,k;
    m.f.forEach(function(f){
      for(i=0;i<f.length;i++){
        var a=f[i],b=f[(i+1)%f.length];
        if(a===b)bad++;
        var uk=Math.min(a,b)+'-'+Math.max(a,b);und[uk]=(und[uk]||0)+1;
        var dk=a+'>'+b;dir[dk]=(dir[dk]||0)+1;
      }
      for(i=1;i+1<f.length;i++){
        var A=m.v[f[0]],B=m.v[f[i]],C=m.v[f[i+1]];
        vol+=(A[0]*(B[1]*C[2]-B[2]*C[1])-A[1]*(B[0]*C[2]-B[2]*C[0])+A[2]*(B[0]*C[1]-B[1]*C[0]))/6;
      }
    });
    for(k in dir)if(dir[k]>1)dup++;
    for(k in und)if(und[k]!==2)bad++;
    return {dup:dup,bad:bad,vol:vol};
  }

  /* ---- 1. level height clamping ---- */
  lines.push('== 1. level height clamping ==');
  var L0=window.__a3dLevels()[0].id;
  window.__a3dAddLevel();
  var LV=window.__a3dLevels(),L1=LV[1].id;
  function setLvl(id,field,val){
    var i=document.querySelector('input[data-lvlf="'+field+'"][data-lvlid="'+id+'"]');
    i.value=String(val);
    i.dispatchEvent(new Event('change',{bubbles:true}));
  }
  function lvl(id){var a=window.__a3dLevels(),i;for(i=0;i<a.length;i++)if(a[i].id===id)return a[i];return null;}
  setLvl(L1,'height',-5);
  ok('negative level height is clamped to a positive value',lvl(L1).height>0,'h='+lvl(L1).height);
  setLvl(L1,'height',0);
  ok('zero level height is clamped to a positive value',lvl(L1).height>0,'h='+lvl(L1).height);
  setLvl(L1,'height','abc');
  ok('non-numeric level height does not corrupt the datum',isFinite(lvl(L1).height)&&lvl(L1).height>0,'h='+lvl(L1).height);
  setLvl(L1,'height',3);
  ok('valid level height is accepted verbatim',near(lvl(L1).height,3),'h='+lvl(L1).height);

  /* ---- 2. thick multi-segment wall boundary vertices ---- */
  lines.push('== 2. multi-segment wall core boundary ==');
  window.__a3dSetLevel(L0);
  window.__a3dWall([[0,0],[10,0],[10,8],[0,8]],0.4,3,'center',true);
  var W1=byName('Wall_1');
  ok('closed 4-segment wall produced a solid',!!(W1&&W1.mesh&&W1.mesh.f.length>=4),W1?W1.mesh.f.length+' faces':'none');
  var wt=topo(W1.mesh);
  ok('wall solid is a closed, coherently oriented manifold',wt.bad===0&&wt.dup===0,'bad='+wt.bad+' dup='+wt.dup);
  /* Centre-aligned 0.4 wall on a 10x8 centreline ring: plan area x height. */
  var wantWallVol=((10.4*8.4)-(9.6*7.6))*3;
  ok('wall volume equals ring plan area x height',near(wt.vol,wantWallVol,1e-6),wt.vol.toFixed(4)+' vs '+wantWallVol.toFixed(4));
  ok('wall has an inner loop offset by half thickness',
     !!(W1.bim.innerLoop&&W1.bim.innerLoop.length===4),
     W1.bim.innerLoop?W1.bim.innerLoop.length+' pts':'none');
  /* centre-aligned 0.4 wall on a 10x8 centreline: inner loop is 9.6 x 7.6 */
  var il=W1.bim.innerLoop,xs=il.map(function(p){return p[0];}),zs=il.map(function(p){return p[1];});
  var iw=Math.max.apply(null,xs)-Math.min.apply(null,xs),ih=Math.max.apply(null,zs)-Math.min.apply(null,zs);
  ok('inner boundary inset by half thickness on every segment',near(iw,9.6,1e-6)&&near(ih,7.6,1e-6),iw.toFixed(3)+' x '+ih.toFixed(3));
  ok('wall spans exactly its height in Z',near(meshY(W1)[1]-meshY(W1)[0],3),JSON.stringify(meshY(W1)));

  /* ---- 3. level change projection ---- */
  lines.push('== 3. level change projection ==');
  window.__a3dSetLevel(L1);
  window.__a3dWall([[20,0],[30,0],[30,8],[20,8]],0.3,3,'center',true);
  var W2=byName('Wall_2');
  ok('element created on Level 1 is seated at its elevation',near(W2.bim.baseY,lvl(L1).elev),'baseY='+W2.bim.baseY);
  var before=meshY(W2);
  setLvl(L1,'elev',9);
  var W2b=byName('Wall_2'),after=meshY(W2b);
  ok('moving a level datum moves its hosted geometry',near(after[0]-before[0],6)&&near(after[1]-before[1],6),
     JSON.stringify(before)+' -> '+JSON.stringify(after));
  ok('hosted baseY stays in lockstep with the datum',near(W2b.bim.baseY,9),'baseY='+W2b.bim.baseY);
  ok('elements on other levels are not disturbed',near(meshY(byName('Wall_1'))[0],0),JSON.stringify(meshY(byName('Wall_1'))));
  var onL1=window.__a3dObjectsOnLevel(L1);
  ok('level membership query returns only that level',onL1.length===1&&onL1[0]===W2b.id,onL1.length+' found');

  /* ---- 4. level deletion never orphans ---- */
  lines.push('== 4. level deletion adoption ==');
  document.querySelector('[data-lvldel="'+L1+'"]').click();
  var live=window.__a3dLevels().map(function(l){return l.id;});
  var orph=objs().filter(function(o){
    var id=(o.bim&&o.bim.levelId)||o.levelId;
    return id&&live.indexOf(id)<0;
  });
  ok('deleting a level leaves no orphaned elements',orph.length===0,orph.length+' orphans');
  ok('re-hosted element was moved onto its new datum',near(byName('Wall_2').bim.baseY,0),'baseY='+byName('Wall_2').bim.baseY);

  /* ---- 5. grid datums ---- */
  lines.push('== 5. grid datums ==');
  ok('grid naming starts at A',window.__a3dGridNextName()==='A',window.__a3dGridNextName());
  window.__a3dAddGrid([0,-5],[0,25]);
  window.__a3dAddGrid([10,-5],[10,25]);
  window.__a3dAddGrid([-5,5],[25,5]);
  var G=window.__a3dGrids();
  ok('three grids registered',G.length===3,G.length+'');
  ok('grid names continue the sequence',G[0].name==='A'&&G[1].name==='B'&&G[2].name==='C',G.map(function(g){return g.name;}).join(','));
  ok('degenerate grid is rejected',window.__a3dAddGrid([4,4],[4,4])===null&&window.__a3dGrids().length===3,window.__a3dGrids().length+'');
  var sp=window.__a3dGridSnapPoints();
  var keys=sp.map(function(p){return p[0].toFixed(3)+','+p[1].toFixed(3);});
  ok('grid intersections are snap targets',keys.indexOf('0.000,5.000')>=0&&keys.indexOf('10.000,5.000')>=0,keys.join(' | '));
  ok('parallel grids produce no intersection',window.__a3dSegIntersect([0,-5],[0,25],[10,-5],[10,25])===null);

  /* ---- 6. beam engine ---- */
  lines.push('== 6. beam engine ==');
  window.__a3dBeam([0,5],[10,5],0.25,0.5,'top');
  var B1=byName('Beam_1');
  ok('beam solid created along the grid line',!!(B1&&B1.mesh),B1?B1.mesh.f.length+' faces':'none');
  var bt=topo(B1.mesh);
  ok('beam is a closed manifold with outward winding',bt.bad===0&&bt.dup===0&&bt.vol>0,'bad='+bt.bad+' dup='+bt.dup+' vol='+bt.vol.toFixed(4));
  ok('beam volume equals span x width x depth',near(bt.vol,10*0.25*0.5,1e-6),bt.vol.toFixed(6)+' vs '+(10*0.25*0.5).toFixed(6));
  var by=meshY(B1);
  ok('beam hangs below its level by its depth',near(by[1],0)&&near(by[0],-0.5),JSON.stringify(by));
  ok('beam records its computed span',near(B1.bim.length,10),'L='+B1.bim.length);
  ok('zero-length beam is refused by the kernel',!!window.__a3dBeamGeometry([1,1],[1,1],0,0.25,0.5).error);
  ok('non-positive beam width is refused',!!window.__a3dBeamGeometry([0,0],[5,0],0,0,0.5).error);
  window.__a3dBeam([0,15],[10,15],0.3,0.6,'center');
  var B2=byName('Beam_2'),by2=meshY(B2);
  ok('centred justification straddles the level',near(by2[1],0.3)&&near(by2[0],-0.3),JSON.stringify(by2));
  ok('beam schedule reports both beams',window.__a3dBeamSchedule().length===2,window.__a3dBeamSchedule().length+'');

  /* ---- 7. persistence of datums ---- */
  lines.push('== 7. datum persistence ==');
  var envTxt=window.__a3dProjectEnvelope?window.__a3dProjectEnvelope():null;
  var env=envTxt?JSON.parse(envTxt):null;
  ok('project export carries grid datums',!!(env&&env.data&&env.data.grids&&env.data.grids.length===3),
     env&&env.data&&env.data.grids?env.data.grids.length+'':'missing');
  ok('project export carries level datums',!!(env&&env.data&&env.data.levels&&env.data.levels.length>=1),
     env&&env.data&&env.data.levels?env.data.levels.length+'':'missing');

  /* ---- 8. undo routing and datum restore ---- */
  lines.push('== 8. undo routing ==');
  var gA=window.__a3dGrids().length;
  window.__a3dAddGrid([30,-4],[30,20]);
  var gB=window.__a3dGrids().length;
  window.__a3dUndo();
  ok('undo removes a grid datum',window.__a3dGrids().length===gA,gB+' -> '+window.__a3dGrids().length);
  window.__a3dRedo();
  ok('redo restores a grid datum',window.__a3dGrids().length===gB,window.__a3dGrids().length+'');
  /* Ctrl+Z must reach the 3D workspace, not the Canvas document underneath it. */
  var gC=window.__a3dGrids().length;
  window.__a3dAddGrid([34,-4],[34,20]);
  if(document.activeElement&&document.activeElement.blur)document.activeElement.blur();
  window.dispatchEvent(new KeyboardEvent('keydown',{key:'z',ctrlKey:true,bubbles:true,cancelable:true}));
  ok('Ctrl+Z is routed to the BIM undo stack while the 3D workspace is active',
     window.__a3dGrids().length===gC,window.__a3dGrids().length+' vs '+gC);

  return {pass:pass,fail:fail,lines:lines};
})()
