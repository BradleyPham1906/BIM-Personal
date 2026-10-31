  /* ================= __acad3dV172: the site analysis tools in the analysis workspace =================
     The owner (2026-10-27): the tools live in the analysis workspace. A Tools group in its left list, a row for each
     tool and one for History; a tool opens on the right where an analysis opens, in the geoprocessing pane's shape:
     what it does, its parameters with their messages, Run, the last run's status, messages and results, its layer on
     the plan, how it works, and its runs in History. */
  function bimTlOrder(){return ['buffer','distance','slopecls','exclude','suit','locate','synth','capacity'].map(bimTlTool).filter(function(t){return !!t;});}
  function bimTlLastRun(tool){var H=bimTlState().history,i;for(i=0;i<H.length;i++)if(H[i].tool===tool)return H[i];return null;}
  /* the left: the group, a row a tool, then History */
  function bimTlRowState(h){return h?(h.st==='fail'?{c:'fail',s:'Failed'}:h.st==='warn'?{c:'warn',s:'Warnings'}:{c:'on',s:'Done'}):null;}
  function bimTlListHtml(pk){
    var H=bimTlState().history,h='<div class="a3d-awl-grp" data-anzgrp="tools"><div class="a3d-awl-grphd">Tools</div>';
    bimTlOrder().forEach(function(t){
      var p=!!(pk&&pk.k==='tool'&&pk.id===t.id),s=bimTlRowState(bimTlLastRun(t.id));
      h+='<div class="a3d-awl-row a3d-awl-tool'+(p?' pick':'')+'" data-anzcard="tl'+t.id+'" data-tlrow="'+t.id+'">'+
        '<i class="a3d-awl-dot" aria-hidden="true"></i>'+
        '<button type="button" class="a3d-awl-nm" data-anzact="aw:tool:'+t.id+'" aria-pressed="'+p+'">'+bimEsc(t.name)+'</button>'+
        (s?'<span class="a3d-anzstate a3d-anzstate-'+s.c+'">'+s.s+'</span>':'')+'</div>';
    });
    var p=!!(pk&&pk.k==='tool'&&pk.id==='history');
    h+='<div class="a3d-awl-row a3d-awl-tool'+(p?' pick':'')+'" data-anzcard="tlhistory" data-tlrow="history">'+
      '<i class="a3d-awl-dot" aria-hidden="true"></i><button type="button" class="a3d-awl-nm" data-anzact="aw:tool:history" aria-pressed="'+p+'">History</button>'+
      '<span class="a3d-awl-st">'+(H.length?H.length+' run'+(H.length===1?'':'s'):'No runs yet')+'</span></div>';
    return h+'</div>';
  }
  /* the search's words for a row */
  function bimTlCards(){
    var C=bimTlOrder().map(function(t){return {id:'tl'+t.id,title:t.name,status:t.sum+' '+t.how,extra:t.params.map(function(p){return p.label;}).join(' '),acts:[]};});
    C.push({id:'tlhistory',title:'History',status:'Every run of a tool, its parameters, status and messages; open it again or run it again',extra:'',acts:[]});
    return C;
  }
  /* ---- the right: one tool ---- */
  function bimTlMsgHtml(m){return '<li class="a3d-tl-m '+(m.t==='err'?'err':m.t==='warn'?'warn':'info')+'">'+bimEsc(m.s)+'</li>';}
  function bimTlFieldMsg(E,W,id){
    var e=E[id],w=W[id];
    return e?'<span class="a3d-tl-msg err" role="alert">'+bimEsc(e)+'</span>':w?'<span class="a3d-tl-msg warn">'+bimEsc(w)+'</span>':'';
  }
  function bimTlInputHtml(key,p,v,E,unit){
    var bad=!!E;
    if(p==='num')return '<span class="a3d-tl-in"><input type="text" inputmode="decimal" autocomplete="off" data-tlf="'+bimEsc(key)+'" value="'+(v===null||v===undefined||(typeof v==='number'&&!isFinite(v))?'':bimEsc(String(v)))+'"'+
      (bad?' aria-invalid="true"':'')+'>'+(unit?'<span class="a3d-tl-u">'+bimEsc(unit)+'</span>':'')+'</span>';
    return '';
  }
  function bimTlSelHtml(key,O,v,bad){
    return '<select data-tlf="'+bimEsc(key)+'"'+(bad?' aria-invalid="true"':'')+'>'+O.map(function(o){return '<option value="'+bimEsc(o[0])+'"'+(o[0]===v?' selected':'')+'>'+bimEsc(o[1])+'</option>';}).join('')+
      (v&&!O.some(function(o){return o[0]===v;})?'<option value="'+bimEsc(v)+'" selected>No longer there</option>':'')+'</select>';
  }
  function bimTlParamHtml(t,p,P,C,G){
    var key=t.id+'|'+p.id,v=P[p.id],e=C.E[p.id],lbl='<span class="a3d-tl-l">'+bimEsc(p.label)+(p.req?'<i class="a3d-tl-req" title="Required">*</i>':'')+'</span>',h;
    if(p.t==='bool')return '<label class="a3d-tl-f a3d-tl-b" data-tlp="'+p.id+'"><input type="checkbox" data-tlf="'+bimEsc(key)+'"'+(v?' checked':'')+'><span class="a3d-tl-l">'+bimEsc(p.label)+'</span>'+bimTlFieldMsg(C.E,C.W,p.id)+'</label>';
    if(p.t==='num')h=bimTlInputHtml(key,'num',v,e,p.unit);
    else h=bimTlSelHtml(key,bimTlOpts(p,P,G),v||'',!!e);
    return '<label class="a3d-tl-f" data-tlp="'+p.id+'">'+lbl+h+bimTlFieldMsg(C.E,C.W,p.id)+(p.help?'<span class="a3d-tl-help">'+bimEsc(p.help)+'</span>':'')+'</label>';
  }
  /* the criteria: one block each, the fields its transform takes */
  function bimTlCritHtml(t,p,P,C){
    var sc=bimTlScale(P);
    return '<div class="a3d-tl-crits" data-tlp="crit">'+p.crit.map(function(c){
      var o=P.crit[c.id],k=t.id+'|crit|'+c.id+'|',e=C.E['crit.'+c.id],h='<div class="a3d-tl-crit'+(o.on?' on':'')+'" data-tlcrit="'+c.id+'">'+
        '<label class="a3d-tl-b"><input type="checkbox" data-tlf="'+k+'on"'+(o.on?' checked':'')+'><span class="a3d-tl-cn">'+bimEsc(c.name)+'</span>'+(c.unit?'<span class="a3d-tl-u">('+bimEsc(c.unit)+')</span>':'')+'</label>';
      if(o.on){
        h+='<div class="a3d-tl-cf">'+
          '<label>Transform'+bimTlSelHtml(k+'how',c.kind==='cat'?BIM_TL_HOW_C:BIM_TL_HOW_V,o.how,false)+'</label>'+
          '<label>Weight'+bimTlInputHtml(k+'w','num',o.w,null,P.weightBy==='pct'?'%':'\u00d7')+'</label>';
        if(o.how==='linear')h+='<label>Better'+bimTlSelHtml(k+'dir',[['down','Lower'],['up','Higher']],o.dir,false)+'</label>';
        if(o.how==='linear'||o.how==='small'||o.how==='large'||o.how==='near')
          h+='<label>Lower threshold'+bimTlInputHtml(k+'lo','num',o.lo,null,c.unit)+'</label><label>Upper threshold'+bimTlInputHtml(k+'hi','num',o.hi,null,c.unit)+'</label>';
        if(o.how==='small'||o.how==='large'||o.how==='near')
          h+='<label>Midpoint'+bimTlInputHtml(k+'mid','num',o.mid,null,c.unit)+'</label><label>Spread'+bimTlInputHtml(k+'spread','num',o.spread,null,'')+'</label>';
        if(o.how==='classes')h+='<label class="w">Breaks, in order'+bimTlInputHtml(k+'breaks','num',o.breaks,null,c.unit).replace('inputmode="decimal" ','')+'</label>'+
          '<label class="w">Values, one more than the breaks ('+sc[0]+' to '+sc[1]+')'+bimTlInputHtml(k+'vals','num',o.vals,null,'').replace('inputmode="decimal" ','')+'</label>';
        if(o.how==='cats')h+='<label class="w">Values by class, '+bimEsc(bimLandSlope().map(function(x){return x[3];}).join(', '))+' (blank: spread over the scale)'+bimTlInputHtml(k+'vals','num',o.vals,null,'').replace('inputmode="decimal" ','')+'</label>';
        h+='</div>';
      }
      return h+(e?'<span class="a3d-tl-msg err" role="alert">'+bimEsc(e)+'</span>':'')+'</div>';
    }).join('')+'</div>';
  }
  function bimTlLayerOf(h){var L=bimResLayers(),i;if(!h||!h.layer)return null;for(i=0;i<L.length;i++)if(L[i].id===h.layer)return L[i];return null;}
  function bimTlRunHtml(h){
    var R=bimTlLayerOf(h),s='<div class="a3d-tl-st '+h.st+'" data-tlst="'+h.st+'">'+bimEsc(BIM_TL_ST[h.st])+' <span>'+bimEsc(h.at+', '+(h.ms<1000?h.ms+' ms':bimDispNum(h.ms/1000,1)+' s'))+'</span></div>';
    if(h.msgs&&h.msgs.length)s+='<ul class="a3d-tl-msgs">'+h.msgs.map(bimTlMsgHtml).join('')+'</ul>';
    if(h.stats&&h.stats.length)s+='<div class="a3d-awp-rows a3d-tl-stats">'+h.stats.map(function(r){return '<div class="a3d-awp-r"><span>'+bimEsc(r[0])+'</span><b>'+bimEsc(r[1])+'</b></div>';}).join('')+'</div>';
    if(R){
      s+='<div class="a3d-tl-lay"><span>On the plan: '+bimEsc(R.name)+(bimTlStale(R)?' (out of date: the lot has changed)':'')+'</span>'+
        bimAwBtn('tl:show:'+R.id,R.visible===false?'Show':'Hide',false)+'</div>';
      var d=R.data;
      if(d&&d.keys&&d.keys.length)s+=bimAwKeyHtml(d.keys.map(function(k){return {name:k.name,col:k.col,kind:'fill'};}));
    }else if(h.layer)s+='<p class="a3d-awp-note">Its layer was removed from Layers.</p>';
    if(h.std&&h.std.list&&h.std.list.length)s+='<p class="a3d-awp-note a3d-awp-std">'+bimEsc('Standards: '+h.std.list.map(function(x){return bimStdUsedText(bimStdTopicOf(x.t));}).join('; '))+'</p>';
    return s;
  }
  function bimTlHistRow(h,all){
    var t=bimTlTool(h.tool);
    return '<div class="a3d-tl-h '+h.st+'" data-tlh="'+bimEsc(h.id)+'"><div class="a3d-tl-hn"><b>'+bimEsc(all?(t?t.name:h.tool):h.at)+'</b><span>'+bimEsc((all?h.at+' \u00b7 ':'')+BIM_TL_ST[h.st]+(h.label?' \u00b7 '+h.label:''))+'</span></div>'+
      '<div class="a3d-tl-ha">'+bimAwBtn('tl:open:'+h.id,'Open',false)+bimAwBtn('tl:rerun:'+h.id,'Run again',false)+(all?bimAwBtn('tl:forget:'+h.id,'Remove',false):'')+'</div></div>';
  }
  function bimTlPanelHtml(id){
    if(id==='history')return bimTlHistoryHtml();
    var t=bimTlTool(id),G=bimTlGrid(),P=bimTlParams(t),C=bimTlCheck(t,P,G),last=bimTlLastRun(t.id),H=bimTlState().history.filter(function(x){return x.tool===t.id;}),h;
    h='<div class="a3d-awp a3d-sa a3d-tl" data-awpanel="tool:'+t.id+'">'+bimAwHd(null,0,t.name,'Tools'+(last?' \u00b7 last run '+last.at:''))+
      '<p class="a3d-awp-about">'+bimEsc(t.sum)+'</p>';
    h+=bimAwSec('Parameters');
    if(!t.params.length)h+='<p class="a3d-awp-note">None: its classes are the standards registry\'s ('+bimEsc(bimStdUsedText('land.slope'))+').</p>';
    h+='<div class="a3d-tl-form">'+t.params.map(function(p){return p.t==='crit'?bimTlCritHtml(t,p,P,C):bimTlParamHtml(t,p,P,C,G);}).join('')+'</div>';
    if(C.E._)h+='<p class="a3d-tl-msg err" role="alert">'+bimEsc(C.E._)+'</p>';
    if(C.W._)h+='<p class="a3d-tl-msg warn">'+bimEsc(C.W._)+'</p>';
    h+='<div class="a3d-awp-acts">'+bimAwBtn('tl:run:'+t.id,'Run',true,C.err?C.first:'')+
      (t.id==='capacity'?bimAwBtn('tl:wetlands',bimTlState().wetlands&&!bimTlState().wetlands.error?'Get wetlands again':'Get wetlands',false,A3D_TL.fetching?'Fetching ...':''):'')+
      bimAwBtn('tl:reset:'+t.id,'Reset parameters',false)+'</div>';
    if(last)h+=bimAwSec('Last run')+bimTlRunHtml(last);
    h+=bimAwSec('How it works')+'<p class="a3d-awp-note">'+bimEsc(t.how)+'</p>'+
      '<p class="a3d-awp-note">'+bimEsc('Its extent: '+bimTlExtentText(G)+'.')+'</p>';
    if(H.length)h+=bimAwSec('Its runs')+'<div class="a3d-tl-hist">'+H.slice(0,5).map(function(x){return bimTlHistRow(x,false);}).join('')+'</div>';
    return h+'</div>';
  }
  function bimTlHistoryHtml(){
    var H=bimTlState().history;
    return '<div class="a3d-awp a3d-sa a3d-tl" data-awpanel="tool:history">'+bimAwHd(null,0,'History','Tools \u00b7 '+(H.length?H.length+' run'+(H.length===1?'':'s'):'no runs yet'))+
      '<p class="a3d-awp-about">Every run of a tool, newest first, kept with the project: open one to see the tool with its parameters, run it again, or remove it. A removed run\'s layer stays in Layers.</p>'+
      (H.length?'<div class="a3d-tl-hist">'+H.map(function(x){return bimTlHistRow(x,true);}).join('')+'</div>':'<p class="a3d-awp-note">No runs yet: pick a tool above and Run it.</p>')+'</div>';
  }
  /* ---- the panel's buttons ---- */
  function bimTlAct(a){
    var i=a.indexOf(':'),c=i<0?a:a.slice(0,i),v=i<0?'':a.slice(i+1),R;
    if(c==='run'){var h=bimTlRun(v);return !!(h&&!h.error);}
    if(c==='open')return bimTlOpen(v);
    if(c==='rerun'){var r=bimTlRerun(v);return !!(r&&!r.error);}
    if(c==='forget')return bimTlForget(v);
    if(c==='show'){R=bimResById(v);if(!R)return false;return bimResultLayerSet(v,'visible',R.visible===false);}
    if(c==='reset'){var T=bimTlState();delete T.params[v];saveSoon();a3dToast('The parameters are back to their defaults');return true;}
    if(c==='wetlands'){
      if(A3D_TL.fetching)return false;
      A3D_TL.fetching=true;
      bimTlWetlandsFetch(function(ok){A3D_TL.fetching=false;var W=bimTlState().wetlands;
        if(ok)a3dToast(W&&W.outside?'The National Wetlands Inventory maps US sites only':'Wetlands: '+((W&&W.f)?W.f.length:0)+' mapped within the extent'+(W&&W.more?' (more than the service returns at once)':''));
        try{if(A3D_AW.on)bimAwRefresh();}catch(eR){console.warn('[BIM] Analyze refresh',eR);}});
      return true;
    }
    return false;
  }
  /* a command: Analyze open with the tool on the right */
  function bimTlCommand(id){bimAwEnter();return bimAwPick('tool',id);}
