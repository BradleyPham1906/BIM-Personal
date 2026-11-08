import { A3D } from '../core/state.js';
import { pushUndo } from '../drawing/plan-mode-sketch.js';
import { bimLayerOf } from './layer-rules.js';
import { A3D_LY, bimLyRowHtml } from './layers-panel.js';
import { bimLyDataRowHtml, bimLyResRowHtml, refreshLayers } from './analysis-data-rows.js';
import { bimEsc } from './layer-manager.js';
import { bimResLayers } from '../analysis/results-layers.js';
import { refreshProps } from '../site-analysis/panel.js';
import { bimMapHost } from '../map/map-tiles.js';
import { A3D_DATA, bimDataById, bimDataList } from '../map/data-layers.js';
import { paint } from '../map/terrain-3d.js';
import { saveSoon } from '../bim/region-regenerate.js';
import { objById } from '../bim/csg-booleans.js';


  /* ================= __acad3dV173c: Layers, listed by drawing order, source or selection =================
     ArcGIS Pro's Contents pane lists one map's layers by drawing order, by data source and by
     selection; the rail's Layers tab does the same over the app's own stores (the owner's D1). The
     kinds draw in a fixed order, which paint sets, and each kind reorders within itself (D2); a data
     layer's list puts the layer drawn on top at the top, as the results' list does (D3), the stored
     order kept. The view is the panel's own state: neither saved nor undone. */
  var BIM_LY_LISTBY=[['order','Drawing order'],['source','Source'],['selection','Selection']];
  function bimLyListBy(){var v=A3D_LY.listBy;return v==='source'||v==='selection'?v:'order';}
  function bimLyListBySet(v){
    A3D_LY.listBy=v==='source'||v==='selection'?v:'order';
    refreshLayers();
    return A3D_LY.listBy;
  }
  function bimLyListBySelect(){
    var o='',i;
    for(i=0;i<BIM_LY_LISTBY.length;i++)o+='<option value="'+BIM_LY_LISTBY[i][0]+'"'+(bimLyListBy()===BIM_LY_LISTBY[i][0]?' selected':'')+'>'+BIM_LY_LISTBY[i][1]+'</option>';
    return '<label class="a3d-lyby"><span>List by</span><select data-lylistby="1" aria-label="List the layers by">'+o+'</select></label>';
  }
  /* the data layers top-first: the last stored draws on top, so it is listed first */
  function bimDataListTopFirst(){return bimDataList().slice().reverse();}
  /* a data layer moved to another's place in the list: one undo step, as a result layer's move */
  function bimDataLayerMove(id,to){
    var L=bimDataList(),i=-1,j=-1,k,D;
    for(k=0;k<L.length;k++){if(L[k].id===id)i=k;if(L[k].id===to)j=k;}
    if(i<0||j<0||i===j)return false;
    pushUndo();
    D=L.splice(i,1)[0];L.splice(j,0,D);
    refreshLayers();refreshProps();paint();saveSoon();
    return true;
  }
  function bimLyGroupHtml(label,n,body){
    return '<div class="a3d-lysec"><div class="a3d-lysechd"><span class="a3d-lycar"></span><span class="a3d-lystat" aria-hidden="true"></span>'+
      '<span class="a3d-lynm a3d-lysecttl">'+bimEsc(label)+'</span><span class="a3d-lycnt">'+(n||'')+'</span></div>'+body+'</div>';
  }
  /* by source: data layers by the server they come from, result layers by the run that made them,
     the site analyses with their sources, and the model's own layers */
  function bimLyBySourceHtml(f){
    var h='',hosts={},order=[],k,sa=[],ml=0,i,R,rb='',L;
    function hit(s){return !f||String(s).toLowerCase().indexOf(f)>=0;}
    bimDataListTopFirst().forEach(function(D){
      if(!hit(D.name))return;
      k=bimMapHost(D.url);
      if(!hosts[k]){hosts[k]={rows:'',n:0,bad:0};order.push(k);}
      hosts[k].rows+=bimLyDataRowHtml(D);hosts[k].n++;if(D.status&&D.status.error)hosts[k].bad++;
    });
    for(i=0;i<order.length;i++)h+=bimLyGroupHtml(order[i]+(hosts[order[i]].bad?' ('+hosts[order[i]].bad+' failed)':''),hosts[order[i]].n,hosts[order[i]].rows);
    R=bimResLayers();
    for(i=0;i<R.length;i++)if(hit(R[i].name))rb+=bimLyResRowHtml(R[i]);
    if(rb)h+=bimLyGroupHtml('Made in the model (Analyze)',R.length,rb);
    for(i=0;i<A3D.layers.length;i++){
      L=A3D.layers[i];
      if(/^Site analysis - /.test(L.name||'')){if(hit(L.name))sa.push(L);}
      else ml++;
    }
    if(sa.length)h+=bimLyGroupHtml('Site analyses (OpenStreetMap and the sources each names)',sa.length,
      sa.map(function(l){return bimLyRowHtml(l,1,0,0,false,A3D_LY.sel,A3D.activeLayer);}).join(''));
    h+=bimLyGroupHtml('The model',ml,'<div class="a3d-lyempty a3d-lyhint">'+ml+' layer'+(ml===1?'':'s')+' drawn here, with no outside source: Drawing order lists them</div>');
    return h;
  }
  /* by selection: each layer holding what is selected, with how many */
  function bimLySelectionCounts(){
    var ids=(A3D.selSet&&A3D.selSet.length)?A3D.selSet:(A3D.sel?[A3D.sel]:[]),m={},i,o,ly;
    for(i=0;i<ids.length;i++){o=objById(ids[i]);ly=o?bimLayerOf(o):null;if(ly)m[ly.id]=(m[ly.id]||0)+1;}
    return m;
  }
  function bimLyBySelectionHtml(f){
    var m=bimLySelectionCounts(),h='',n=0,i,L,s,D;
    function hit(x){return !f||String(x).toLowerCase().indexOf(f)>=0;}
    for(i=0;i<A3D.layers.length;i++){
      L=A3D.layers[i];
      if(!m[L.id]||!hit(L.name))continue;
      h+=bimLyRowHtml(L,0,m[L.id],0,false,A3D_LY.sel,A3D.activeLayer);n+=m[L.id];
    }
    s=A3D_DATA.sel;D=s?bimDataById(s.layer):null;
    if(D&&hit(D.name)){h+=bimLyGroupHtml('Data',1,bimLyDataRowHtml(D));n++;}
    return n?h:'<div class="a3d-lyempty">Nothing is selected: pick objects in the model, or a feature of a data layer</div>';
  }
  /* the list under the header for the views other than drawing order */
  function bimLyListByHtml(f){
    var v=bimLyListBy();
    if(v==='source')return bimLyBySourceHtml(f);
    if(v==='selection')return bimLyBySelectionHtml(f);
    return '';
  }
export {
  bimDataLayerMove, bimDataListTopFirst, bimLyListBy, bimLyListByHtml, bimLyListBySelect, bimLyListBySet
};
