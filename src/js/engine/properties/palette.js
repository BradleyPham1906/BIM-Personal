  // ---- __acad3dV36: Revit-shaped Properties palette. Revit's palette is: a type selector header
  // (thumbnail + "Family: Type" + Edit Type), then COLLAPSIBLE parameter groups (Constraints,
  // Graphics, Dimensions, Identity Data) in a two-column name/value grid, with read-only
  // parameters greyed rather than hidden, and Apply at the bottom. The previous flat list of
  // rows carried the same data but none of that structure.
  /* __acad3dV66: group open/closed defaults. Absent name => open, so every group added since
     V36 has silently defaulted open. In the docked (single-column) shell the two Phase 51
     appearance groups are 7-9 rows each and pushed the Project Browser ~1400px down the scroll
     on selection, so they default closed: they are override editors, consulted deliberately,
     not read at a glance like Constraints/Dimensions. The user's toggle still persists for the
     session via bimPropGroupToggle. */
  var A3D_PROP_GROUPS_OPEN={Constraints:true,Graphics:true,Dimensions:true,'Sketch Constraints':true,'Identity Data':true,Other:true,
    'Graphics — Technical':false,'Graphics — Presentation':false,Standards:false};   /* __acad3dV167i: long; STANDARDS opens it */
  function bimPropGroupToggle(g){
    A3D_PROP_GROUPS_OPEN[g]=!A3D_PROP_GROUPS_OPEN[g];
    refreshProps();
  }
  /* ================= __acad3dV77: one number format for the whole palette =================

     The panel had four conventions at once: raw floats in editable fields ("2.175438380956253"),
     a unit in the value on some rows ("14.000 m"), a unit in the label on others ("Volume (m3)"),
     and per-row decimal counts chosen ad hoc. Revit has one convention -- unit in the LABEL, bare
     number in the value, at the project's display precision -- and a value column is only
     scannable if every row obeys it.

     DISPLAY ONLY. The model keeps full precision; this is what the input SHOWS. Editing a field
     writes the typed value, so rounding here can never round the model. That is also how Revit
     behaves: the palette shows 2.175 while the element is still at 2.1754383809. */
  var BIM_UNITS={
    m:  {label:'m',  scale:1,    dp:3},
    cm: {label:'cm', scale:100,  dp:1},
    mm: {label:'mm', scale:1000, dp:0}
  };
  /* Project display units. Persisted with the project (see bimUnitState/bimApplyUnitState), and
     deliberately a PROJECT setting rather than a constant: this app is meant for bridge and
     structural work as well as buildings, and a 90 m span and a 6 mm plate cannot both be read
     at three decimals of a metre. */
  var A3D_UNITS={key:'m',dp:null};
  function bimUnitDef(){return BIM_UNITS[A3D_UNITS.key]||BIM_UNITS.m;}
  function bimUnitLabel(){return bimUnitDef().label;}
  function bimUnitDp(){
    return (A3D_UNITS.dp===null||A3D_UNITS.dp===undefined)?bimUnitDef().dp:A3D_UNITS.dp;
  }
  /* A LENGTH in metres, as the project wants to see it: converted, rounded, and with trailing
     zeros trimmed so a whole number reads as "3" rather than "3.000". */
  function bimDispLen(vMetres){
    if(vMetres===null||vMetres===undefined||!isFinite(vMetres))return '\u2014';
    return bimTrimNum((vMetres*bimUnitDef().scale).toFixed(bimUnitDp()));
  }
  /* A plain number at a stated precision -- for quantities that are NOT lengths (areas, volumes,
     ratios, densities), which must not be scaled by the length unit. */
  function bimDispNum(v,dp){
    if(v===null||v===undefined||!isFinite(v))return '\u2014';
    return bimTrimNum(Number(v).toFixed(dp===undefined?3:dp));
  }
  function bimTrimNum(s){
    if(s.indexOf('.')<0)return s;
    s=s.replace(/0+$/,'').replace(/\.$/,'');
    return s===''||s==='-'?'0':s;
  }
  /* A label with its unit, the way Revit writes them: "Thickness (mm)", never "Thickness" with
     "300 mm" in the value column. */
  function bimLenLabel(label){return label+' ('+bimUnitLabel()+')';}
  /* An editable LENGTH row. The input carries the DISPLAYED value in project units; the change
     handler converts back to metres, so what the user types is what the model gets. step is
     derived from the display precision so the spinner moves by one visible increment rather than
     by an invisible fraction. */
  function bimPropLen(label,valueMetres,field,min){
    var d=bimUnitDp(),step=d>0?('0.'+new Array(d).join('0')+'1'):'1';
    return bimPropRow(bimLenLabel(label),
      '<input type="number" step="'+step+'"'+(min!==undefined?' min="'+(min*bimUnitDef().scale)+'"':'')+
      ' data-propf="'+field+'" data-proplen="1" value="'+bimDispLen(valueMetres)+'">');
  }
  function bimPropLenText(label,valueMetres){
    return bimPropText(bimLenLabel(label),bimDispLen(valueMetres));
  }
  /* The metres value a bimPropLen input now holds. One place converts back, so a new length field
     cannot be added with the conversion forgotten. */
  function bimLenInputToMetres(raw){
    var v=parseFloat(raw);
    if(!isFinite(v))return null;
    return v/bimUnitDef().scale;
  }
  function bimSetUnits(key,dp){
    if(key&&BIM_UNITS[key])A3D_UNITS.key=key;
    if(dp!==undefined&&dp!==null){
      dp=parseInt(dp,10);
      if(isFinite(dp))A3D_UNITS.dp=Math.max(0,Math.min(4,dp));
    }
    refreshProps();paint();saveSoon();
    return {key:A3D_UNITS.key,dp:bimUnitDp()};
  }
  function bimPropRow(label,valueHtml,readOnly){
    return '<div class="a3d-prow'+(readOnly?' ro':'')+'">'+
      '<div class="a3d-plabel">'+bimEsc(label)+'</div>'+
      '<div class="a3d-pval">'+valueHtml+'</div></div>';
  }
  function bimPropText(label,val,readOnly){
    return bimPropRow(label,'<span class="a3d-pstatic">'+bimEsc(String(val))+'</span>',readOnly!==false);
  }
  function bimPropGroup(name,rowsHtml){
    if(!rowsHtml)return '';
    var open=A3D_PROP_GROUPS_OPEN[name]!==false;
    return '<div class="a3d-pgrp" data-a3dpgrp="'+bimEsc(name)+'">'+bimEsc(name)+
      '<span class="a3d-pgcar">'+(open?'\u25b4':'\u25be')+'</span></div>'+
      (open?'<div class="a3d-pgbody">'+rowsHtml+'</div>':'');
  }
  function bimObjTypeLabel(o){
    if(bimIsDiag(o))return 'Site analysis : '+((bimDgAn(o.dg.a)||{}).name||'Diagram');   /* __acad3dV164 */
    if(o&&o.t==='terrain')return 'Topography : TIN Surface';   /* __acad3dV108 */
    if(o.bim&&o.bim.type){
      var t=o.bim.type;
      if(t==='wall'){var tn=bimTypeNameOf(o);return 'Walls : '+(tn||('Basic Wall '+(o.bim.thickness?(Math.round(o.bim.thickness*1000)+'mm'):'')));}
      if(t==='floor')return 'Floors : Generic Floor';
      if(t==='ceiling')return 'Ceilings : Generic Ceiling';
      if(t==='roof')return 'Roofs : Basic Roof';
      if(t==='column')return 'Columns : Rectangular Column';
      if(t==='stair')return 'Stairs : Assembled Stair';
      if(t==='door')return 'Doors : Single-Flush';
      if(t==='window')return 'Windows : Fixed';
      if(t==='familyInstance')return (o.bim.category||'Generic Models')+' : '+(o.bim.familyName||o.name);
      return t.charAt(0).toUpperCase()+t.slice(1);
    }
    if(o.t==='room')return 'Rooms : Room';
    if(o.t==='roomtag')return 'Room Tags : Room Tag';   /* __acad3dV101 */
    if(bimIsProperty(o))return 'Site : Property Line';   /* __acad3dV103 */
    if(bimIsAlignment(o))return 'Site : Alignment';       /* __acad3dV127 */
    if(bimIsFooting(o))return 'Structural Foundations : '+(bimTypeNameOf(o)||(o.bim.type==='footing'?'Isolated Footing':'Wall Foundation'));   /* __acad3dV102 */
    if(o.bim&&o.bim.structural==='foundation')return 'Structural Foundations : Foundation Slab';
    if(o.t==='dim')return 'Dimensions : '+(bimDimKind(o)==='linear'?'Linear':bimDimKind(o).charAt(0).toUpperCase()+bimDimKind(o).slice(1));
    if(o.t==='text')return 'Text Notes : Text';
    if(bimIsHatch(o))return 'Patterns : Hatches';           /* __acad3dV96 */
    if(bimIsCline(o))return 'Lines : Construction Lines';   /* __acad3dV94 */
    if(bimIsPoint(o))return 'Points : Nodes';   /* __acad3dV93 */
    if(o.t==='sketch')return 'Lines : Model Lines';
    return (TYPES[o.t]&&TYPES[o.t].n)?('Generic Models : '+TYPES[o.t].n):'Generic Models';
  }
