  /* __acad3dV171b: the analysis workspace, for the suite */
  window.__acad3dV171b='workspace,enter,leave,focus,ticks,layers,undo,kept,afterrun,traffic,bar,list,panel,overview,chart,key,look,lightdark,ground,ctxtones,mapgrey,words,legendplace,dockhidden,toasttop,phone,chips,details,command,open,rowfit';
  window.__a3dAw=function(){var S=bimAwState(),L=bimAwLook();
    return {on:!!A3D_AW.on,focus:S.focus,add:S.add.slice(),now:bimAwFocusNow(),look:L?(L.light?'light':'dark'):null,bg:bimAwBgHex(),
      shown:BIM_DG_AN.filter(function(A){return bimAwShown(A.id);}).map(function(A){return A.id;}),
      run:BIM_DG_AN.filter(function(A){return !!bimDgState().runs[A.id];}).map(function(A){return A.id;})};};
  window.__a3dAwEnter=function(f){return f===undefined?bimAwEnter():bimAwEnter(f);};
  window.__a3dAwLeave=function(){return bimAwLeave();};
  window.__a3dAwFocus=function(a){return bimAwFocus(a);};
  window.__a3dAwTick=function(a){return bimAwTick(a);};
  window.__a3dAwCtxCol=function(id){var o=objById(id);return o?bimAwCtxCol(o):null;};
  window.__a3dAwInk=function(c){return bimAwInk(c);};
  window.__a3dAwSel=function(){return (A3D.selSet||[]).slice();};
  window.__a3dAwMvLight=function(){return bimMvLight();};
  window.__a3dAwGroups=function(){return BIM_AW_GROUPS.map(function(G){return {id:G.id,name:G.name,an:G.an.slice()};});};
  /* the older suites' view of a run: out of the workspace, each analysis shown as a run showed it before V171b */
  window.__a3dAwClassic=function(){
    if(A3D_AW.on)bimAwLeave();
    var D=bimDgState(),n=0;
    BIM_DG_AN.forEach(function(A){var ly=bimLayerById(D.layers[A.id]);if(ly&&D.runs[A.id]&&(ly.visible!==false)!==!A.hidden){ly.visible=!A.hidden;n++;}});
    var S=bimAwState();S.focus=null;S.add=[];
    if(n)bimLayerChanged();
    return n;
  };
