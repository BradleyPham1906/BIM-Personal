import { UNDO_STACK, bimObjOffset, pushUndo } from '../drawing/plan-mode-sketch.js';
import { bimLayerOf } from './layer-rules.js';
import { BIM_LINETYPES, BIM_LINEWEIGHTS, bimLinetypeDef } from './select-change.js';
import { bimEsc } from './layer-manager.js';
import { bimPropRow } from '../properties/palette.js';
import { refreshProps } from '../site-analysis/panel.js';
import { toScreen } from '../io/import-entry.js';
import { paint } from '../map/terrain-3d.js';
import { saveSoon } from '../bim/region-regenerate.js';
import { a3dToast } from '../bim/csg-booleans.js';

  /* ================= __acad3dV257: an object's own colour, linetype and lineweight (D5) =================
     AutoCAD gives every object three appearance properties that are ByLayer unless set: a line takes its layer's
     colour, linetype and lineweight until it is given its own. Here they are o.color (#rrggbb), o.linetype (one of
     BIM_LINETYPES' names) and o.lineweight (one of BIM_LINEWEIGHTS, millimetres); a missing key is ByLayer.
     (o.col is not one of them: every sketch has always carried a default col, so it cannot say "set by hand".)
     bimLayerLook reads them through bimObjLook; Properties sets them through bimObjLookSet; the DXF and DWG
     readers fill o.color from an entity's own colour, and MATCHPROP copies all three. */
  function bimObjLook(o,ly){
    var lt=o&&o.linetype&&bimLinetypeDef(o.linetype);
    return {
      color:(o&&/^#[0-9a-fA-F]{6}$/.test(o.color||''))?o.color:((ly&&/^#[0-9a-fA-F]{6}$/.test(ly.color||''))?ly.color:'#5ec4b8'),
      linetype:lt?lt.name:((ly&&bimLinetypeDef(ly.linetype))?bimLinetypeDef(ly.linetype).name:'Continuous'),
      lineweight:(o&&typeof o.lineweight==='number'&&BIM_LINEWEIGHTS.indexOf(o.lineweight)>=0)?o.lineweight:(ly?ly.lineweight:null)
    };
  }
  /* One of the three, from a Properties field: '' or 'ByLayer' clears it. Returns an error text or ''. */
  function bimObjLookSet(o,field,val){
    var v=String(val==null?'':val).replace(/^\s+|\s+$/g,''),bylayer=(v===''||/^bylayer$/i.test(v));
    if(field==='color'){
      if(!bylayer&&!/^#[0-9a-fA-F]{6}$/.test(v))return 'A colour is ByLayer or one such as #ff8800';
      if(bylayer)delete o.color;else o.color=v.toLowerCase();
    }else if(field==='linetype'){
      var lt=bylayer?null:bimLinetypeDef(v);
      if(!bylayer&&!lt)return 'Unknown linetype: '+v;
      if(bylayer)delete o.linetype;else o.linetype=lt.name;
    }else if(field==='lineweight'){
      var n=+v;
      if(!bylayer&&BIM_LINEWEIGHTS.indexOf(n)<0)return 'Not one of AutoCAD\'s lineweights: '+v;
      if(bylayer)delete o.lineweight;else o.lineweight=n;
    }else return 'Not an appearance property: '+field;
    return '';
  }
  function bimObjLookApply(o,field,val){
    pushUndo();
    var err=bimObjLookSet(o,field,val);
    if(err){UNDO_STACK.pop();a3dToast(err);refreshProps();return false;}
    paint();saveSoon();refreshProps();
    return true;
  }
  /* The three Properties rows, each ByLayer or the object's own. */
  function bimObjLookRows(o){
    var h='',i,ly=bimLayerOf(o),L=bimObjLook({},ly);
    var col=/^#[0-9a-fA-F]{6}$/.test(o.color||'');
    h+=bimPropRow('Color','<select data-propf="objcolor-mode"><option value="bylayer"'+(col?'':' selected')+'>ByLayer ('+bimEsc(L.color)+')</option>'+
      '<option value="own"'+(col?' selected':'')+'>Its own</option></select>'+
      (col?' <input type="color" data-propf="objcolor" value="'+bimEsc(o.color)+'" aria-label="Its colour">':''));
    var lto='<option value="ByLayer"'+(o.linetype?'':' selected')+'>ByLayer ('+bimEsc(L.linetype)+')</option>';
    for(i=0;i<BIM_LINETYPES.length;i++)lto+='<option value="'+BIM_LINETYPES[i].name+'"'+(o.linetype===BIM_LINETYPES[i].name?' selected':'')+'>'+BIM_LINETYPES[i].name+'</option>';
    h+=bimPropRow('Linetype','<select data-propf="objlinetype">'+lto+'</select>');
    var lwo='<option value="ByLayer"'+(typeof o.lineweight==='number'?'':' selected')+'>ByLayer ('+(L.lineweight==null?'Default':L.lineweight.toFixed(2)+' mm')+')</option>';
    for(i=0;i<BIM_LINEWEIGHTS.length;i++)lwo+='<option value="'+BIM_LINEWEIGHTS[i]+'"'+(o.lineweight===BIM_LINEWEIGHTS[i]?' selected':'')+'>'+BIM_LINEWEIGHTS[i].toFixed(2)+' mm</option>';
    h+=bimPropRow('Lineweight','<select data-propf="objlineweight">'+lwo+'</select>');
    h+=bimPropRow('Global width (m)','<input type="number" min="0" step="any" data-propf="plwidth" value="'+(o.plWidth>0?o.plWidth:0)+'">');   /* __acad3dV265 */
    return h;
  }
  /* A Properties change to one of them; true when the field was one of the three. */
  function bimObjLookField(o,f,inp){
    if(f==='objcolor-mode'){
      if(inp.value==='own')return bimObjLookApply(o,'color',bimObjLook({},bimLayerOf(o)).color)||true;
      return bimObjLookApply(o,'color','ByLayer')||true;
    }
    if(f==='objcolor'){bimObjLookApply(o,'color',inp.value);return true;}
    if(f==='objlinetype'){bimObjLookApply(o,'linetype',inp.value);return true;}
    if(f==='objlineweight'){bimObjLookApply(o,'lineweight',inp.value);return true;}
    if(f==='plwidth'){   /* __acad3dV265 */
      var w=parseFloat(inp.value);
      if(!(w>=0)){a3dToast('A width is zero or more');refreshProps();return true;}
      pushUndo();if(w>0)o.plWidth=w;else delete o.plWidth;paint();saveSoon();refreshProps();return true;
    }
    return false;
  }
  /* __acad3dV265: a polyline's global width (o.plWidth, metres), drawn at drawing scale as AutoCAD draws a wide
     polyline; never thinner than the line it would otherwise be. */
  function bimWideLook(lk,o,V,W,H){
    var q=bimObjOffset(o),p=o.pts[0],a=toScreen([p[0]+q[0],(o.y||0)+q[1],p[1]+q[2]],V,W,H),b=toScreen([p[0]+q[0]+1,(o.y||0)+q[1],p[1]+q[2]],V,W,H);
    var ppm=Math.sqrt(Math.pow(b[0]-a[0],2)+Math.pow(b[1]-a[1],2)),r={},k;
    for(k in lk)if(lk.hasOwnProperty(k))r[k]=lk[k];
    r.width=Math.max(lk.width,o.plWidth*ppm);
    r.plWidth=o.plWidth;
    return r;
  }
export { bimObjLook, bimObjLookField, bimObjLookRows, bimWideLook };
