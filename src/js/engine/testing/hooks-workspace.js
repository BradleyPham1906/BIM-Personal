  /* __acad3dV171b: the analysis workspace, for the suite */
  window.__acad3dV171b='workspace,enter,leave,focus,ticks,layers,undo,kept,afterrun,traffic,bar,list,panel,overview,chart,key,look,lightdark,ground,ctxtones,mapgrey,words,legendplace,dockhidden,toasttop,phone,chips,details,command,open,rowfit';
  window.__acad3dV171c='oneanalyze,tab,tableave,prevtab,list,categories,rows,findcount,redflag,overview,category,findings,analyses,catdata,seealso,analysis,itfound,answers,card,cardacts,props,back,search,phone,fold,noanztog,noshow';
  window.__a3dAw=function(){var S=bimAwState(),L=bimAwLook(),pk=A3D_AW.pick,sh=document.getElementById('a3d-shell'),pn=el.propsbody?el.propsbody.querySelector('[data-awpanel]'):null;
    return {on:!!A3D_AW.on,focus:S.focus,add:S.add.slice(),now:bimAwFocusNow(),look:L?(L.light?'light':'dark'):null,bg:bimAwBgHex(),
      pick:pk?pk.k+':'+pk.id:null,props:!!A3D_AW.props,prev:A3D_AW.prev,tab:sh?sh.getAttribute('data-tab'):null,panel:pn?pn.getAttribute('data-awpanel'):null,pend:!!A3D_AW.pend,
      shown:BIM_DG_AN.filter(function(A){return bimAwShown(A.id);}).map(function(A){return A.id;}),
      run:BIM_DG_AN.filter(function(A){return !!bimDgState().runs[A.id];}).map(function(A){return A.id;})};};
  window.__a3dAwEnter=function(f){return f===undefined?bimAwEnter():bimAwEnter(f);};
  window.__a3dAwLeave=function(){return bimAwLeave();};
  window.__a3dAwFocus=function(a){return bimAwFocus(a);};
  window.__a3dAwTick=function(a){return bimAwTick(a);};
  window.__a3dAwCtxCol=function(id){var o=objById(id);return o?bimAwCtxCol(o):null;};
  window.__a3dAwInk=function(c){return bimAwInk(c);};
  window.__a3dAwSel=function(){return (A3D.selSet||[]).slice();};
  window.__a3dAwMvLight=function(){return bimTrLight();};
  window.__a3dAwPick=function(k,id){return bimAwPick(k,id);};   /* __acad3dV171c */
  window.__a3dAwFinds=function(a){return (BIM_AW_FINDS[a]||[]).slice();};
  /* the older suites' view of a run: out of the workspace, each analysis shown as a run showed it before V171b */
  window.__a3dAwClassic=function(){
    if(A3D_AW.on)bimAwLeave();
    var D=bimDgState(),n=0;
    BIM_DG_AN.forEach(function(A){var ly=bimLayerById(D.layers[A.id]);if(ly&&D.runs[A.id]&&(ly.visible!==false)!==!A.hidden){ly.visible=!A.hidden;n++;}});
    var S=bimAwState();S.focus=null;   /* __acad3dV171c: the ticks as the layers show them, so a tick hides one */
    S.add=BIM_DG_AN.filter(function(A){return !!bimLayerById(D.layers[A.id])&&!!D.runs[A.id]&&!A.hidden;}).map(function(A){return A.id;});
    if(n)bimLayerChanged();
    return n;
  };
