import { pushUndo } from '../drawing/plan-mode-sketch.js';
import { bimLayersPanelRefresh } from '../layers/analysis-data-rows.js';
import { bimEsc } from '../layers/layer-manager.js';
import { refreshProps } from '../site-analysis/panel.js';
import { BIM_CLS_LABEL, BIM_CLS_MAXK, BIM_CLS_METHODS, bimClsBreaks } from './classify.js';
import { BIM_RAMPS, BIM_RAMP_ORDER, bimRampColours } from './colour-ramps.js';
import { BIM_LENS_MAX_ROWS, bimDataLensScale, bimLensRows } from './colour-lens.js';
import { bimDataById, bimDataFeats } from './data-layers.js';
import { paint } from './terrain-3d.js';
import { saveSoon } from '../bim/region-regenerate.js';
import { a3dToast } from '../bim/csg-booleans.js';


  /* ================= __acad3dV173a: a data layer's graduated colours =================
     A data layer coloured by a number is classified by one of map/classify.js's methods into
     classes, each a colour of a ColorBrewer ramp (map/colour-ramps.js). The settings are kept
     on the layer as L.cls = {method, k, ramp, rev, step, centre, breaks}, each change one undo
     step through bimDataSet; what is missing reads as the owner's defaults (D4, D5 in
     docs/research/research-contents-pane.md): natural breaks, 5 classes, a class centred on the
     mean. A text attribute keeps V136's categories. */
  var BIM_DCLS_STEPS=[1,0.5,1/3,0.25];
  var BIM_DCLS_STEP_LABEL=['1 standard deviation','1/2 standard deviation','1/3 standard deviation','1/4 standard deviation'];
  var BIM_DCLS_MAXBREAKS=BIM_CLS_MAXK-1;
  var A3D_DCLS={memo:{}};
  /* the settings, every field read safely: a project file may carry anything */
  function bimDataClsSettings(L){
    var c=L&&L.cls&&typeof L.cls==='object'?L.cls:{},o={},k=Math.round(+c.k),i,b=[],t;
    o.method=BIM_CLS_METHODS.indexOf(c.method)>=0?c.method:'natural';
    o.k=isFinite(k)&&k>=1?Math.min(BIM_CLS_MAXK,k):5;
    o.ramp=typeof c.ramp==='string'&&BIM_RAMPS.hasOwnProperty(c.ramp)?c.ramp:'YlOrRd';
    o.rev=c.rev===true;
    o.step=1;
    for(i=0;i<BIM_DCLS_STEPS.length;i++)if(Math.abs(+c.step-BIM_DCLS_STEPS[i])<0.01)o.step=BIM_DCLS_STEPS[i];
    o.centre=c.centre==='break'?'break':'class';
    if(Array.isArray(c.breaks))for(i=0;i<c.breaks.length&&b.length<BIM_DCLS_MAXBREAKS;i++){t=c.breaks[i];if(typeof t==='number'&&isFinite(t)&&b.indexOf(t)<0)b.push(t);}   /* only numbers: +null would be a break at 0 */
    o.breaks=b.sort(function(p,q){return p-q;});
    return o;
  }
  /* the classes over a layer's numbers, kept until the settings, the attribute or the features change */
  function bimDataClassify(L,nums){
    var st=bimDataClsSettings(L),F=bimDataFeats(L.id),key=JSON.stringify(st)+'|'+L.by+'|'+(L.filter||'')+'|'+nums.length,   /* __acad3dV173b: the filter too */m=A3D_DCLS.memo[L.id],res,note='';
    if(m&&m.key===key&&m.F===F)return m.res;
    res=bimClsBreaks(nums,st.method,{k:st.k,step:st.step,centre:st.centre,breaks:st.breaks});
    if(res.error){
      note=res.error+'; shown in equal interval instead';
      res=bimClsBreaks(nums,'equal',{k:st.k});
      if(res.error)return null;
      res.note=res.note?note+'. '+res.note:note;
      res.fellBack=st.method;
    }
    res.st=st;
    res.cols=bimRampColours(st.ramp,res.breaks.length,st.rev);
    A3D_DCLS.memo[L.id]={key:key,F:F,res:res};
    return res;
  }
  /* the lens's number scale, its bins made from the classes: bimLensPick reads sc.breaks */
  function bimDataClsScale(L,nums){
    var res=bimDataClassify(L,nums),bins=[],i;
    if(!res)return null;
    for(i=0;i<res.breaks.length;i++)bins.push({lo:i?res.breaks[i-1]:res.lo,hi:res.breaks[i],col:res.cols[i],n:0});
    return {kind:'num',lo:res.lo,hi:res.hi,bins:bins,breaks:res.breaks,cls:res};
  }
  /* one field of L.cls: the change is one undo step; a value refused is said and changes nothing */
  function bimDataClsSet(id,field,val){
    var L=bimDataById(id),st,v,i,parts,t,cur;
    if(!L)return false;
    st=bimDataClsSettings(L);
    function no(msg){a3dToast(msg);refreshProps();return false;}
    if(field==='method'){v=String(val||'');if(BIM_CLS_METHODS.indexOf(v)<0)return no('There is no classification called '+v);}
    else if(field==='k'){v=Math.round(parseFloat(val));if(!isFinite(v)||v<1||v>BIM_CLS_MAXK)return no('Classes: a whole number from 1 to '+BIM_CLS_MAXK);}
    else if(field==='ramp'){v=String(val||'');if(!BIM_RAMPS.hasOwnProperty(v))return no('There is no colour ramp called '+v);}
    else if(field==='rev'){v=val===true||val==='true';}
    else if(field==='step'){
      v=null;for(i=0;i<BIM_DCLS_STEPS.length;i++)if(Math.abs(parseFloat(val)-BIM_DCLS_STEPS[i])<0.01)v=BIM_DCLS_STEPS[i];
      if(v===null)return no('The interval is 1, 1/2, 1/3 or 1/4 of a standard deviation');
    }
    else if(field==='centre'){v=val==='break'?'break':'class';}
    else if(field==='breaks'){
      parts=String(val==null?'':val).split(/[\s,;]+/);v=[];
      for(i=0;i<parts.length;i++){
        if(!parts[i])continue;
        t=parseFloat(parts[i]);
        if(!/^-?(\d+\.?\d*|\.\d+)([eE][-+]?\d+)?$/.test(parts[i])||!isFinite(t))return no('Breaks are numbers with commas between them: '+parts[i]+' is not one');
        if(v.indexOf(t)<0)v.push(t);
      }
      if(v.length>BIM_DCLS_MAXBREAKS)return no('At most '+BIM_DCLS_MAXBREAKS+' breaks ('+BIM_CLS_MAXK+' classes)');
      v.sort(function(p,q){return p-q;});
    }
    else return false;
    cur=st[field];
    if(field==='breaks'?(JSON.stringify(cur)===JSON.stringify(v)&&st.method==='manual'):cur===v)return true;
    pushUndo();
    if(!L.cls||typeof L.cls!=='object')L.cls={};
    /* Manual starts from the breaks shown, as ArcGIS does; typing breaks makes the method Manual */
    if(field==='method'&&v==='manual'&&!st.breaks.length){
      var sh=A3D_DCLS.memo[L.id]&&A3D_DCLS.memo[L.id].res;
      if(sh&&sh.breaks)L.cls.breaks=sh.breaks.slice(0,-1);
    }
    if(field==='breaks')L.cls.method='manual';
    L.cls[field]=v;
    delete A3D_DCLS.memo[L.id];
    refreshProps();paint();saveSoon();bimLayersPanelRefresh();
    return true;
  }
  /* the layer's colours as a swatch for its row in Layers: its colour, or its classes or categories */
  function bimDataSwatch(L){
    var col=/^#[0-9a-fA-F]{6}$/.test(L.color||'')?L.color:'#7f9db8',ds,c=[],i;
    if(!L.by)return col;
    try{ds=bimDataLensScale(L);}catch(e){console.warn('[BIM] data layer swatch',e);return col;}
    if(!ds||!ds.scale)return col;
    if(ds.scale.kind==='num')for(i=0;i<ds.scale.bins.length;i++)c.push(ds.scale.bins[i].col);
    else for(i=0;i<ds.scale.list.length&&i<8;i++)c.push(ds.scale.cats[ds.scale.list[i]].col);
    return c.length>1?'linear-gradient(90deg,'+c.join(',')+')':c.length?c[0]:col;
  }
  /* its legend patches, under the row in Layers, as the result layers have */
  function bimDataLegendHtml(L){
    var ds,rows,h='',i,more;
    if(!L.by)return '';
    try{ds=bimDataLensScale(L);}catch(e){console.warn('[BIM] data layer legend',e);return '';}
    rows=ds?bimLensRows(ds.scale,ds.none):[];
    if(!rows.length)return '';
    more=rows.length>BIM_LENS_MAX_ROWS?rows.length-BIM_LENS_MAX_ROWS+1:0;
    if(more)rows=rows.slice(0,BIM_LENS_MAX_ROWS-1);
    for(i=0;i<rows.length;i++)h+='<span><i style="background:'+bimEsc(rows[i].col)+'"></i>'+bimEsc(rows[i].name)+' ('+rows[i].n+')</span>';
    if(more)h+='<span>and '+more+' more</span>';
    return '<div class="a3d-lyleg" title="'+bimEsc(bimDataLegendTitle(L,ds))+'">'+h+'</div>';
  }
  function bimDataLegendTitle(L,ds){
    var c=ds&&ds.scale&&ds.scale.cls;
    return L.name+': '+L.by+(c?' ('+BIM_CLS_LABEL[c.fellBack?'equal':c.method]+', '+c.k+' class'+(c.k===1?'':'es')+')':'');
  }
  /* Properties: the method, the classes, the ramp, and what the classification says of itself */
  function bimDataSymHtml(L){
    var ds,c,st,id=bimEsc(L.id),r='',o='',i,j,ctl;
    if(!L.by)return '';
    try{ds=bimDataLensScale(L);}catch(e){console.warn('[BIM] data layer symbology',e);return '';}
    c=ds&&ds.scale&&ds.scale.cls;
    if(!c)return '';
    st=c.st;
    function row(label,html){return '<div class="a3d-prow a3d-dllens"><div class="a3d-plabel">'+label+'</div><div class="a3d-pval">'+html+'</div></div>';}
    for(i=0;i<BIM_CLS_METHODS.length;i++)o+='<option value="'+BIM_CLS_METHODS[i]+'"'+(st.method===BIM_CLS_METHODS[i]?' selected':'')+'>'+BIM_CLS_LABEL[BIM_CLS_METHODS[i]]+'</option>';
    r+=row('Method','<select data-propdata="cls-method:'+id+'" aria-label="Classification of '+bimEsc(L.name)+'">'+o+'</select>');
    if(st.method==='stddev'){
      o='';for(i=0;i<BIM_DCLS_STEPS.length;i++)o+='<option value="'+BIM_DCLS_STEPS[i]+'"'+(st.step===BIM_DCLS_STEPS[i]?' selected':'')+'>'+BIM_DCLS_STEP_LABEL[i]+'</option>';
      r+=row('Interval','<select data-propdata="cls-step:'+id+'" aria-label="Class width">'+o+'</select>');
      r+=row('The mean','<select data-propdata="cls-centre:'+id+'" aria-label="Where the mean falls"><option value="class"'+(st.centre==='class'?' selected':'')+'>The centre of a class</option>'+
        '<option value="break"'+(st.centre==='break'?' selected':'')+'>A break</option></select>');
    }else if(st.method==='manual'){
      r+=row('Breaks','<input type="text" data-propdata="cls-breaks:'+id+'" value="'+bimEsc(st.breaks.join(', '))+'" spellcheck="false" aria-label="Breaks, the upper bound of each class but the last" title="The upper bound of each class but the last, with commas between">');
    }else{
      r+=row('Classes','<input type="number" min="1" max="'+BIM_CLS_MAXK+'" step="1" data-propdata="cls-k:'+id+'" value="'+st.k+'" aria-label="Number of classes">');
    }
    o='';for(i=0;i<BIM_RAMP_ORDER.length;i++){j=BIM_RAMP_ORDER[i];o+='<option value="'+j+'"'+(st.ramp===j?' selected':'')+'>'+bimEsc(BIM_RAMPS[j].label)+'</option>';}
    ctl='<div class="a3d-ukv"><select data-propdata="cls-ramp:'+id+'" aria-label="Colour ramp">'+o+'</select>'+
      '<label class="a3d-ctxk"><input type="checkbox" data-propdata="cls-rev:'+id+'"'+(st.rev?' checked':'')+'> Reverse</label></div>';
    r+=row('Colours',ctl);
    r+=row('Fit','<span class="a3d-pstatic" title="Goodness of variance fit: 1 when every class holds one value">'+
      bimEsc('GVF '+(Math.round(c.gvf*1000)/1000)+'; '+c.k+' class'+(c.k===1?'':'es')+' over '+c.n+' value'+(c.n===1?'':'s')+(ds.none?', '+ds.none+' with none':''))+'</span>');
    if(c.note)r+=row('','<span class="a3d-pstatic'+(c.fellBack?' a3d-uerr':'')+'">'+bimEsc(c.note)+'</span>');
    return r;
  }
export {
  bimDataClsScale, bimDataClsSet, bimDataLegendHtml, bimDataLegendTitle, bimDataSwatch, bimDataSymHtml
};
