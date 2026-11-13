import { A3D } from '../core/state.js';
import { pushUndo } from '../drawing/plan-mode-sketch.js';
import { A3D_PLOT } from '../layers/layer-rules.js';
import { bimEsc } from '../layers/layer-manager.js';
import { bimPropRow } from '../properties/palette.js';
import { paint } from '../map/terrain-3d.js';
import { saveSoon } from '../bim/region-regenerate.js';

/* __acad3dV197: colours by surface kind, in the shaded view and the rendered view alike. The project chooses (View,
   Colours; saved with it as A3D.site.colours): its own colours (the default), Study model or Natural, the owner's two
   palettes (2026-11-12). An object's kind is what the app already records on it: a map layer's kind (Site Context),
   a terrain, a BIM element's type, an IFC element's class. A map or city building's faces that look up (their normal
   over 0.25 up, a slope under about 75 degrees) are its roof, drawn in the roof colour through a second row of the
   scene's table (gpu-batches.js), so neither engine's shaders change. Imports with their own materials (glTF,
   SketchUp) and anything of no known kind keep their own colour. A colour lens, the Analyze workspace's look and plot
   by layer come first. docs/research/research-surface-kinds.md. */
  var BIM_SK_PAL={
    study:{name:'Study model',walls:'#f4f2ee',roofs:'#b9bcc2',ground:'#e7e1d3',water:'#9cc3e6',green:'#b9d9a8',trees:'#6fa86a',
      roads:'#d0cfcb',glass:'#bcd6e6',rail:'#c4bdb4',airports:'#dddcd8',power:'#c9cbce',landuse:'#ece7dc',floor:'#e4e1da',
      door:'#d9cbb5',structure:'#dcdcd8',stair:'#e9e6df',ceiling:'#f7f6f3'},
    natural:{name:'Natural',walls:'#e8e1d4',roofs:'#9c4f3c',ground:'#c9b48a',water:'#4f8fd6',green:'#7cb36b',trees:'#3f7d3f',
      roads:'#8a8f98',glass:'#9fc4dc',rail:'#7d6f62',airports:'#9a9ea5',power:'#a7abb1',landuse:'#d3c497',floor:'#bfae94',
      door:'#8a6a4a',structure:'#b4b1ab',stair:'#cbbfa9',ceiling:'#f1ede6'}};
  var BIM_SK_ROOF_NY=0.25;
  /* the context kinds Site Context records, as palette keys */
  var BIM_SK_CTX={buildings:'walls',roads:'roads',water:'water',green:'green',trees:'trees',rail:'rail',airports:'airports',
    power:'power',landuse:'landuse',terrain:'ground'};
  var BIM_SK_BIM={wall:'walls',floor:'floor',roof:'roofs',door:'door',window:'glass',column:'structure',beam:'structure',
    footing:'structure',stripfooting:'structure',stair:'stair',ceiling:'ceiling'};
  var BIM_SK_IFC=[[/^IfcRoof/,'roofs'],[/^Ifc(Window|CurtainWall|Plate)/,'glass'],[/^IfcDoor/,'door'],
    [/^Ifc(Column|Beam|Member|Footing|Pile|ReinforcingBar|Tendon)/,'structure'],[/^Ifc(Stair|Ramp|Railing)/,'stair'],
    [/^Ifc(Slab|Covering)/,'floor'],[/^IfcWall/,'walls'],[/^Ifc(Site|Geographic|Earthworks)/,'ground']];
  /* the project's palette now, or null (its own colours, or plot by layer) */
  function bimSkPalette(){
    var k=A3D.site&&A3D.site.colours;
    if(!k||!BIM_SK_PAL.hasOwnProperty(k)||A3D_PLOT.on)return null;
    return BIM_SK_PAL[k];
  }
  /* an object's kind as a palette key, or null */
  function bimSkKey(o){
    if(!o)return null;
    var c=o.context,b=o.bim,i;
    if(c&&c.kind&&BIM_SK_CTX.hasOwnProperty(c.kind))return BIM_SK_CTX[c.kind];
    if(o.t==='terrain')return 'ground';
    if(o.gltf||o.skp)return null;
    if(b&&b.ifcType){for(i=0;i<BIM_SK_IFC.length;i++)if(BIM_SK_IFC[i][0].test(b.ifcType))return BIM_SK_IFC[i][1];return null;}
    if(b&&b.type&&BIM_SK_BIM.hasOwnProperty(b.type))return BIM_SK_BIM[b.type];
    return null;
  }
  /* an object's colour by its kind under the project's palette, or null */
  function bimSkCol(o){
    var P=bimSkPalette(),k;
    if(!P)return null;
    k=bimSkKey(o);
    return k&&P.hasOwnProperty(k)?P[k]:null;
  }
  /* whether an object's upward faces are a roof: a map or city building */
  function bimSkRoofy(o){return !!(o&&o.context&&o.context.kind==='buildings');}
  function bimSkRoofCol(){var P=bimSkPalette();return P?P.roofs:null;}
  /* the View row */
  function bimSkPropsHtml(){
    var k=(A3D.site&&A3D.site.colours)||'',o='<option value=""'+(BIM_SK_PAL.hasOwnProperty(k)?'':' selected')+'>Own colours</option>',p;
    for(p in BIM_SK_PAL)if(BIM_SK_PAL.hasOwnProperty(p))o+='<option value="'+p+'"'+(k===p?' selected':'')+'>'+bimEsc(BIM_SK_PAL[p].name)+'</option>';
    return bimPropRow('Colours','<select data-propmodel="colours" title="Roofs, walls, ground, water and trees by kind, in both views">'+o+'</select>');
  }
  function bimSkSet(v){
    v=String(v||'');
    if(v&&!BIM_SK_PAL.hasOwnProperty(v))return false;
    if(!A3D.site)return false;
    if((A3D.site.colours||'')===v)return true;
    pushUndo();
    if(v)A3D.site.colours=v;else delete A3D.site.colours;
    paint();saveSoon();
    return true;
  }
export {
  BIM_SK_PAL, BIM_SK_ROOF_NY, bimSkCol, bimSkKey, bimSkPalette, bimSkPropsHtml, bimSkRoofCol, bimSkRoofy,
  bimSkSet
};
