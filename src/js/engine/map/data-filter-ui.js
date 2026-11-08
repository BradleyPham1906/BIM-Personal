import { el } from '../core/state.js';
import { pushUndo } from '../drawing/plan-mode-sketch.js';
import { bimLayersPanelRefresh } from '../layers/analysis-data-rows.js';
import { bimEsc } from '../layers/layer-manager.js';
import { refreshProps } from '../site-analysis/panel.js';
import { bimFltClause, bimFltParse, bimFltTest } from './layer-filter.js';
import { bimDataAttrKeys } from './colour-lens.js';
import { bimDataById, bimDataFeats } from './data-layers.js';
import { paint } from './terrain-3d.js';
import { saveSoon } from '../bim/region-regenerate.js';
import { a3dToast } from '../bim/csg-booleans.js';


  /* ================= __acad3dV173b: a data layer's filter and labels, applied and set =================
     L.filter is CQL2 text (map/layer-filter.js), L.label one field or a template (map/data-labels.js).
     A filter limits what is drawn, picked, classified and labelled, as ArcGIS's definition query
     does. Each is one undo step through bimDataSet. In Properties: the filter as text, a clause
     builder for phone and tablet that writes it, and the label. */
  var A3D_DFLT={memo:{}};
  /* which features pass: {pass, n, of, error, warn}, or null when the layer has no filter */
  function bimDataMask(L){
    var F,m,p,pass=[],n=0,i;
    if(!L||!L.filter)return null;
    F=bimDataFeats(L.id);m=A3D_DFLT.memo[L.id];
    if(m&&m.text===L.filter&&m.F===F)return m.res;
    p=bimFltParse(L.filter);
    if(p.error){m={text:L.filter,F:F,res:null,error:p.error};A3D_DFLT.memo[L.id]=m;return null;}   /* a broken filter from a file draws all, and says so */
    for(i=0;i<F.length;i++){pass.push(bimFltTest(p.tree,F[i]&&F[i].p));if(pass[i])n++;}
    A3D_DFLT.memo[L.id]={text:L.filter,F:F,res:{pass:pass,n:n,of:F.length,warn:p.warn}};
    return A3D_DFLT.memo[L.id].res;
  }
  function bimDataMaskError(L){var m;bimDataMask(L);m=L&&A3D_DFLT.memo[L.id];return m&&m.text===L.filter?m.error||'':'';}
  function bimDataPasses(L,fi){var m=bimDataMask(L);return !m||!!m.pass[fi];}
  /* the filter or the label set: a filter that does not read is refused with where it fails */
  function bimDataFltSet(id,field,val){
    var L=bimDataById(id),v,p,keys,miss=[],i;
    if(!L)return false;
    v=String(val==null?'':val).replace(/^\s+|\s+$/g,'');
    if(field==='filter'&&v){
      p=bimFltParse(v);
      if(p.error){a3dToast('Filter: '+p.error);refreshProps();return false;}
      v=p.text;
      keys=bimDataAttrKeys(id);
      for(i=0;i<p.fields.length;i++)if(keys.indexOf(p.fields[i])<0)miss.push(p.fields[i]);
    }
    if(field==='label')v=v.slice(0,200);
    if((L[field]||'')===v)return true;
    pushUndo();
    if(v)L[field]=v;else delete L[field];
    delete A3D_DFLT.memo[id];
    refreshProps();paint();saveSoon();bimLayersPanelRefresh();
    if(field==='filter'){
      var m=bimDataMask(L);
      a3dToast(!v?L.name+': no filter':L.name+': '+m.n+' of '+m.of+' features pass'+(miss.length?'. Not a field of the layer: '+miss.join(', '):'')+(m.warn?'. '+m.warn:''));
    }
    return true;
  }
  /* the line in Layers and Properties: how many pass */
  function bimDataFilterText(L){
    var m,e;
    if(!L.filter)return '';
    e=bimDataMaskError(L);
    if(e)return 'Filter not applied: '+e;
    m=bimDataMask(L);
    return m?'Filter: '+m.n+' of '+m.of+' features':'';
  }
  /* the builder writes one clause, joined to the filter with AND or OR */
  function bimDataFltAdd(id){
    var L=bimDataById(id),q=function(k){return el.propsbody?el.propsbody.querySelector('[data-propdflt="'+k+':'+id+'"]'):null;},f=q('f'),o=q('o'),v=q('v'),j=q('j'),cl;
    if(!L||!f||!o)return false;
    cl=bimFltClause(f.value,o.value,v?v.value:'');
    if(!cl){a3dToast('Pick a field, an operator and a value');return false;}
    return bimDataFltSet(id,'filter',L.filter?'('+L.filter+') '+(j&&j.value==='OR'?'OR':'AND')+' '+cl:cl);
  }
  var BIM_DFLT_OPS=[['=','is'],['<>','is not'],['<','less than'],['<=','at most'],['>','more than'],['>=','at least'],['contains','contains'],['like','is like (% _)'],['in','is one of (a, b)'],['null','is empty'],['notnull','is not empty']];
  function bimDataFltHtml(L){
    var id=bimEsc(L.id),keys=bimDataAttrKeys(L.id),r='',o='',i,ft;
    if(!keys.length)return '';
    function row(label,html){return '<div class="a3d-prow a3d-dllens"><div class="a3d-plabel">'+label+'</div><div class="a3d-pval">'+html+'</div></div>';}
    r+=row('Filter','<input type="text" data-propdata="filter:'+id+'" value="'+bimEsc(L.filter||'')+'" spellcheck="false" placeholder="ZONE = \'CMX-3\' AND AREA > 500" aria-label="Filter of '+bimEsc(L.name)+', as CQL2" title="CQL2: = <> < > LIKE IN BETWEEN IS NULL, joined with AND, OR, NOT">');
    ft=bimDataFilterText(L);
    if(ft)r+=row('','<span class="a3d-pstatic'+(bimDataMaskError(L)?' a3d-uerr':'')+'">'+bimEsc(ft)+'</span>');
    for(i=0;i<keys.length;i++)o+='<option value="'+bimEsc(keys[i])+'">'+bimEsc(keys[i])+'</option>';
    var ops='';for(i=0;i<BIM_DFLT_OPS.length;i++)ops+='<option value="'+bimEsc(BIM_DFLT_OPS[i][0])+'">'+bimEsc(BIM_DFLT_OPS[i][1])+'</option>';
    r+=row('Add a clause','<div class="a3d-ukv">'+(L.filter?'<select data-propdflt="j:'+id+'" aria-label="Join"><option value="AND">and</option><option value="OR">or</option></select>':'')+
      '<select data-propdflt="f:'+id+'" aria-label="Field">'+o+'</select><select data-propdflt="o:'+id+'" aria-label="Operator">'+ops+'</select></div>');
    r+=row('','<div class="a3d-ukv"><input type="text" data-propdflt="v:'+id+'" spellcheck="false" placeholder="value" aria-label="Value">'+
      '<button type="button" class="a3d-pedit" data-propdataact="fltadd:'+id+'">Add</button>'+(L.filter?'<button type="button" class="a3d-pedit" data-propdataact="fltclr:'+id+'">Clear</button>':'')+'</div>');
    r+=row('Labels','<input type="text" data-propdata="label:'+id+'" value="'+bimEsc(L.label||'')+'" spellcheck="false" list="a3d-dlab-'+id+'" placeholder="a field, or {NAME} ({AREA} m2)" aria-label="Label of '+bimEsc(L.name)+'">'+
      '<datalist id="a3d-dlab-'+id+'">'+o+'</datalist>');
    return r;
  }
export { bimDataFilterText, bimDataFltAdd, bimDataFltHtml, bimDataFltSet, bimDataMask, bimDataPasses };
