import { A3D } from '../core/state.js';
import { A3D_PLOT } from '../layers/layer-rules.js';
import { bimResMetaText, bimResSwatch } from '../layers/analysis-data-rows.js';
import { bimEsc } from '../layers/layer-manager.js';
import { A3D_UNITS, bimDispNum, bimPropGroup, bimPropRow, bimPropText } from '../properties/palette.js';
import { BIM_SIM_RAMP } from '../analysis/simulation.js';
import {
  bimResById, bimResGone, bimResLayers, bimResStale, bimResultLayerUpdate
} from '../analysis/results-layers.js';
import { bimClbE } from '../site-analysis/climate-board.js';
import { A3D_REV } from '../core/objects-save.js';
import { bimBuildRoomSchedule, bimLevelAreas } from '../views/schedules.js';
import { bimLtMenuOpen } from './layout-tabs.js';
import { bimFigEntry, bimFigSrc } from './board-figures.js';
import { bimBobBox, bimBobFind } from './board-objects.js';
import { bimLvFormat } from './live-text.js';
import { bimLiveMarks } from './live-sources.js';
import {
  bimLbBars, bimLbHist, bimLbHistSvg, bimLbKpiFind, bimLbKpiLabels, bimLbSort, bimLbTableHtml, bimLbTotals
} from './live-board.js';
import { bimBdsAttr, bimBdsComp, bimBdsPos, bimBdsPx } from './board-design.js';
import { bimBdeAdd, bimBdeWork } from './board-design-edit.js';
import { a3dToast } from '../bim/csg-booleans.js';



  /* ================= __acad3dV175b: schedules, single indicators and result charts on a board =================
     docs/research/research-presentation-live.md (D1, D2, D3, D8, D13) and docs/work-orders/v175/SPEC-v175b.md.
     Three kinds of board object drawn from the model each time the board is, saving only what they show:
       sched   a table of the model: rooms, or areas by level (n.src), sorted by a column (n.sk, n.sd);
       kpi     one card of a site board's indicator row (n.f, the row's figure; n.lab, the card's label);
       rchart  one result layer (n.res; n.nm, its name when placed): its text, and Sun hours' histogram.
     A kept result is never run again by a board (D3): out of date, it is drawn with the amber mark and Properties
     has Run again. A source that was removed says what it was bound to and is a dash on paper (D8). The pure
     parts (sorting, totals, the markup) are sheets/live-board.js, built by Cline from the work orders. */
  var A3D_LBD={sig:'',rows:{}};
  /* a schedule's columns: {k, t (heading), kind (bimLvFormat's)} */
  function bimLbdCols(src){
    if(src==='levels')return [{k:'level',t:'Level',kind:'text'},{k:'gross',t:'Gross area',kind:'area'},{k:'net',t:'Room area',kind:'area'},
      {k:'eff',t:'Efficiency',kind:'pct'}];
    return [{k:'number',t:'Number',kind:'text'},{k:'name',t:'Name',kind:'text'},{k:'level',t:'Level',kind:'text'},{k:'area',t:'Area',kind:'area'},
      {k:'occupants',t:'Occupants',kind:'count'}];
  }
  function bimLbdSchedName(src){return src==='levels'?'Areas by level':'Rooms';}
  /* a schedule's rows, read once per revision of the model */
  function bimLbdRows(src){
    var sig=A3D_REV+'|'+A3D_UNITS.key,R;
    if(sig!==A3D_LBD.sig){A3D_LBD.sig=sig;A3D_LBD.rows={};}
    if(A3D_LBD.rows.hasOwnProperty(src))return A3D_LBD.rows[src];
    if(src==='levels')R=A3D.levels.map(function(L){
      var a=bimLevelAreas(L.id);
      return {level:L.name,gross:a.gross===null?'':a.gross,net:a.net>0?a.net:'',eff:a.efficiency===null?'':Math.round(a.efficiency*10)/10};
    });
    else R=bimBuildRoomSchedule().map(function(r){
      return {number:r.number||'',name:r.name||'',level:r.level||'',area:typeof r.area==='number'&&isFinite(r.area)?r.area:'',
        occupants:typeof r.occupants==='number'?r.occupants:''};
    });
    A3D_LBD.rows[src]=R;
    return R;
  }
  function bimLbdCell(v,kind){return v===''||v===null||v===undefined?'':bimLvFormat(v,kind,null);}
  /* ---- what each kind shows: {st ('ok', 'none', 'gone', 'stale'), why: [reasons], html} ---- */
  function bimLbdSched(n){
    var cols=bimLbdCols(n.src),rows=bimLbdRows(n.src),T,foot=null,any=false,R={st:'ok',why:[],html:''};
    if(n.sk&&cols.some(function(c){return c.k===n.sk;}))rows=bimLbSort(rows,n.sk,!!n.sd);
    T=bimLbTotals(rows,cols);
    T.forEach(function(v){if(v!=='')any=true;});
    if(any&&rows.length){
      foot=T.map(function(v,i){return bimLbdCell(v,cols[i].kind);});
      if(cols[0].kind==='text')foot[0]='Total';
    }
    if(!rows.length){R.st='none';R.why.push(n.src==='levels'?'Not computed: there are no levels':'Not computed: there are no rooms yet');}
    R.html=bimLbTableHtml(cols.map(function(c){return c.t;}),rows.map(function(r){return cols.map(function(c){return bimLbdCell(r[c.k],c.kind);});}),foot,bimClbE);
    return R;
  }
  /* the indicator rows the site boards draw now, read once per render (ctx.caps): {f, name, kpis: [html]} */
  function bimLbdKpiRows(ctx){
    return ['clim.kpis','zn.kpis','acc.kpis','ppl.kpis'].map(function(f){
      var E=bimFigEntry(f),P=null;
      try{P=bimFigSrc(ctx,f,null);}catch(eK){console.warn('[BIM] The indicators of '+f+' could not be read',eK);}
      return {f:f,name:E?E.name:f,kpis:P&&P.kpis?P.kpis:[]};
    });
  }
  function bimLbdKpi(n,ctx){
    var E=bimFigEntry(n.f),P=null,i,R={st:'ok',why:[],html:''};
    try{P=E?bimFigSrc(ctx,n.f,null):null;}catch(eK){console.warn('[BIM] The indicators of '+n.f+' could not be read',eK);}
    if(!P||!P.kpis||!P.kpis.length){R.st='none';R.why.push('Not computed: '+(E?E.name:'these indicators')+' are not worked out yet (Site analysis)');return R;}
    i=bimLbKpiFind(P.kpis,n.lab);
    if(i<0){R.st='gone';R.why.push('Source removed: '+n.lab);return R;}
    R.html='<section class="a3d-clb-kpis a3d-clb-dkpi" style="--n:1">'+P.kpis[i]+'</section>';
    return R;
  }
  function bimLbdChart(n){
    var Rl=bimResById(n.res),R={st:'ok',why:[],html:''},d,C,h='';
    if(!Rl||bimResGone(Rl)){R.st='gone';R.why.push('Source removed: '+(n.nm||'a result layer'));return R;}
    if(bimResStale(Rl)){R.st='stale';R.why.push('Out of date: the model has changed since '+Rl.name+' ran');}
    d=Rl.data;
    if(Rl.kind==='sunhours'&&d&&typeof d.cells==='string'){
      C=bimLbHist(d.cells,BIM_SIM_RAMP.length);
      h+='<div class="a3d-clb-dhist">'+bimLbHistSvg(bimLbBars(C,200,60,2),BIM_SIM_RAMP,200,60)+'</div>'+
        '<div class="a3d-clb-dax"><span>0 h</span><span>Hours of direct sun, '+bimClbE(d.date||'')+'</span><span>'+bimClbE(bimDispNum(d.day,1))+' h</span></div>';
    }else h+='<div class="a3d-clb-dramp" style="background:'+bimResSwatch(Rl)+'"></div>';
    R.html='<div class="a3d-clb-dch">'+h+'<p class="a3d-clb-dmeta">'+bimClbE(bimResMetaText(Rl))+'</p></div>';
    return R;
  }
  /* what one of the three shows, for drawing and for Print's list */
  function bimLbdState(n,ctx){
    try{
      if(n.t==='sched')return bimLbdSched(n);
      if(n.t==='kpi')return bimLbdKpi(n,ctx||{caps:{},narrow:false});
      if(n.t==='rchart')return bimLbdChart(n);
    }catch(eS){console.warn('[BIM] A board object could not be drawn from the model: '+n.t,eS);return {st:'none',why:['Not computed: see the console'],html:''};}
    return null;
  }
  /* its title: its own, or the source's name */
  function bimLbdTitle(n){
    var Rl,E;
    if(n.t==='sched')return n.ttl||bimLbdSchedName(n.src);
    if(n.t==='rchart'){if(n.ttl)return n.ttl;Rl=bimResById(n.res);return Rl?Rl.name:(n.nm||'Result chart');}
    if(n.t==='kpi'){E=bimFigEntry(n.f);return E?E.name:'Indicator';}
    return '';
  }
  /* drawn on the board: in Edit the reason and the marks; on paper a dash where there is nothing to show */
  function bimLbdHtml(n,ox,oy,ctx){
    var S=bimLbdState(n,ctx),paper=A3D_PLOT.on||!ctx.edit,body,t;
    if(!S)return '';
    if(S.st==='none'||S.st==='gone')body='<div class="a3d-clb-dlbx">'+(paper?'—':bimClbE(S.why[0]||''))+'</div>';
    else body=S.html;
    t=n.t==='kpi'?'':'<div class="a3d-clb-dlbt">'+bimClbE(bimLbdTitle(n))+'</div>';
    return '<div'+bimBdsAttr(n,'a3d-clb-dlb '+n.t,ctx)+' style="'+bimBdsPos(bimBobBox(n),ox,oy)+'font-size:'+bimBdsPx(2.6)+'px;'+bimBdsComp(n,ctx)+'">'+t+body+
      (paper?'':bimLiveMarks({ov:false,changed:false,unknown:[],st:S.st,why:S.why}))+'</div>';
  }
  /* ---- in Edit: the Draw menu's three entries ---- */
  function bimLbdSchedMenu(x,y){
    bimLtMenuOpen(x,y,[['Rooms','rooms'],['Areas by level','levels']],function(src){
      bimBdeAdd('sched',{src:src,w:src==='levels'?110:150,h:50});
    });
    return true;
  }
  function bimLbdKpiMenu(x,y){
    var items=[],ctx={caps:{},narrow:false};
    bimLbdKpiRows(ctx).forEach(function(G){
      var L=bimLbKpiLabels(G.kpis);
      if(!L.length)return;
      if(items.length)items.push('-');
      L.forEach(function(lab,i){items.push([G.name+': '+lab,G.f+'#'+i]);});
    });
    if(!items.length){a3dToast('No indicators yet: work out a site board in Site analysis (climate, zoning, access) first');return false;}
    bimLtMenuOpen(x,y,items,function(a){
      var m=/^(.+)#(\d+)$/.exec(a),G,lab;
      if(!m)return;
      bimLbdKpiRows({caps:{},narrow:false}).forEach(function(q){if(q.f===m[1])G=q;});
      lab=G?bimLbKpiLabels(G.kpis)[+m[2]]:null;
      if(lab)bimBdeAdd('kpi',{f:m[1],lab:lab,w:45,h:26});
    });
    return true;
  }
  function bimLbdChartMenu(x,y){
    var L=bimResLayers();
    if(!L.length){a3dToast('No result layers yet: run an analysis (Sun hours, Rain on terrain, a terrain view) and Add as layer');return false;}
    bimLtMenuOpen(x,y,L.map(function(R){return [R.name,R.id];}),function(id){
      var R=bimResById(id);
      if(R)bimBdeAdd('rchart',{res:R.id,nm:R.name.slice(0,80),w:90,h:R.kind==='sunhours'?62:40});
    });
    return true;
  }
  /* Run again, for a result chart that is out of date: its layer updated, never by the board itself (D3) */
  function bimLbdRun(id){
    var W=bimBdeWork(),f=W?bimBobFind(W.objs,id):null;
    if(!f||f.n.t!=='rchart'||!bimResById(f.n.res))return false;
    return bimResultLayerUpdate(f.n.res);
  }
  /* ---- the Properties panel, for one selected object of the three ---- */
  function bimLbdPropsHtml(n){
    var S,g='',cols,acts='';
    if(n.t!=='sched'&&n.t!=='kpi'&&n.t!=='rchart')return '';
    S=bimLbdState(n,null);
    if(n.t==='sched'){
      cols=bimLbdCols(n.src);
      g+=bimPropText('Source',bimLbdSchedName(n.src),true);
      g+=bimPropRow('Title','<input type="text" data-bdf="ttl" maxlength="80" value="'+bimEsc(n.ttl||'')+'" placeholder="'+bimEsc(bimLbdSchedName(n.src))+'">');
      g+=bimPropRow('Sorted by','<select data-bdf="sk"><option value="">The model\'s order</option>'+cols.map(function(c){return '<option value="'+bimEsc(c.k)+'"'+(n.sk===c.k?' selected':'')+'>'+bimEsc(c.t)+'</option>';}).join('')+'</select>');
      g+=bimPropRow('Descending','<input type="checkbox" data-bdf="sd"'+(n.sd?' checked':'')+'>');
    }else if(n.t==='kpi'){
      g+=bimPropText('Source',bimLbdTitle(n)+': '+n.lab,true);
    }else{
      g+=bimPropText('Source',(bimResById(n.res)||{name:n.nm||'-'}).name,true);
      g+=bimPropRow('Title','<input type="text" data-bdf="ttl" maxlength="80" value="'+bimEsc(n.ttl||'')+'" placeholder="'+bimEsc(bimLbdTitle(n))+'">');
      if(S&&S.st==='stale')acts+='<button type="button" class="a3d-pedit" data-bdact="lv-resrun" title="Run the analysis again on the model as it is now">Run again</button>';
    }
    if(S)S.why.forEach(function(w){g+='<div class="a3d-pnote">'+bimEsc(w)+'</div>';});
    if(acts)g+='<div class="a3d-bdeacts">'+acts+'</div>';
    g+='<div class="a3d-pnote">It is drawn from the project each time the board is. A board never runs an analysis again by itself. Its marks show in Edit and are never printed.</div>';
    return bimPropGroup('Live',g);
  }
export {
  bimLbdChartMenu, bimLbdCols, bimLbdHtml, bimLbdKpiMenu, bimLbdPropsHtml, bimLbdRows, bimLbdRun,
  bimLbdSchedMenu, bimLbdState, bimLbdTitle
};
