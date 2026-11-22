  /* ================= __acad3dV268: material cards, as FreeCAD's Material workbench keeps them =================
     V120's library is five fixed cards. FreeCAD's material cards are a library a user edits: physical properties
     (linear elastic: density, Young's modulus, Poisson's ratio, strengths), thermal ones (conductivity, specific heat,
     expansion), an appearance (diffuse colour, transparency), each a .FCMat file. Here:
     - the project carries its own cards (A3D.matCards, saved with it), beside the built-in ones; a project card of a
       built-in's name stands in for it;
     - MATERIALS (MAT, MATBROWSEROPEN) lists them: new, duplicate, edit, delete, assign to the selection (its material,
       and its colour from the card's appearance), import and export .FCMat;
     - .FCMat is FreeCAD 1.0's format (YAML: General, Models, AppearanceModels, each model by its UUID; read from
       FreeCAD's own src/Mod/Material/Resources at 170926f, 2026-11-22). Older cards (an INI of Key = value) are read
       too. Units are read as written (kg/m^3, MPa, GPa, W/m/K, J/kg/K, m/m/K, µm/m/K) and kept in the app's.
     The built-in cards' values are V120's, which match FreeCAD's generic cards; the thermal values added to Steel and
     the expansion added to Glass are FreeCAD's Steel-Generic and Glass-Generic (read the same day). The parse, the
     units and the writer are pure, tested without a page. */
  var BIM_FCMAT_MODELS={linear:['LinearElastic','7b561d1d-fb9b-44f6-9da9-56a4f74d7536'],thermal:['Thermal','9959d007-a970-4ea7-bae4-3eb1b8b883c7'],
    standard:['MaterialStandard','1e2c0088-904a-4537-925f-64064c07d700'],render:['BasicRendering','f006c7e4-35b7-43d5-bbf9-c5d572309e6e']};
  /* [the card's key, the label, the app's unit, FreeCAD's key, its model] */
  var BIM_MAT_FIELDS=[
    ['density','Density','kg/m³','Density','linear'],
    ['youngsModulus','Young’s modulus','GPa','YoungsModulus','linear'],
    ['poissonRatio','Poisson’s ratio','','PoissonRatio','linear'],
    ['yieldStrength','Yield strength','MPa','YieldStrength','linear'],
    ['tensileStrength','Ultimate tensile strength','MPa','UltimateTensileStrength','linear'],
    ['conductivity','Thermal conductivity','W/m·K','ThermalConductivity','thermal'],
    ['specificHeat','Specific heat','J/kg·K','SpecificHeat','thermal'],
    ['expansion','Thermal expansion','µm/m·K','ThermalExpansionCoefficient','thermal']];
  /* what FreeCAD's generic cards add to V120's (see above) */
  var BIM_MAT_BUILTIN_EXTRA={Steel:{conductivity:50,specificHeat:500,expansion:12},Glass:{expansion:9,transparency:0.6}};
  /* ---------- pure: units ---------- */
  /* A FreeCAD quantity ("210 GPa", "0.000012 m/m/K") in the app's unit for that field, or null. */
  function bimMatQty(field,s){
    var m=/^\s*(-?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)\s*(.*)$/.exec(String(s==null?'':s));
    if(!m)return null;
    var v=parseFloat(m[1]),u=m[2].replace(/\s+/g,'').replace('µ','u').replace('μ','u').toLowerCase();
    if(!isFinite(v))return null;
    if(field==='density')return u==='g/cm^3'||u==='g/cm3'?v*1000:v;
    if(field==='youngsModulus')return u==='mpa'?v/1000:u==='kpa'?v/1e6:u==='pa'?v/1e9:v;   /* GPa */
    if(field==='yieldStrength'||field==='tensileStrength')return u==='gpa'?v*1000:u==='kpa'?v/1000:u==='pa'?v/1e6:v;   /* MPa */
    if(field==='specificHeat')return u==='kj/kg/k'?v*1000:v;
    if(field==='expansion')return (u==='m/m/k'||u==='1/k'||u==='/k')?v*1e6:v;   /* um/m/K */
    return v;
  }
  /* "(r, g, b, a)" with 0..1 parts to #rrggbb, and back */
  function bimMatColorFromFc(s){
    var m=/\(\s*([0-9.]+)\s*,\s*([0-9.]+)\s*,\s*([0-9.]+)/.exec(String(s||''));
    if(!m)return null;
    return '#'+[m[1],m[2],m[3]].map(function(x){var n=Math.max(0,Math.min(255,Math.round(parseFloat(x)*255)));return (n<16?'0':'')+n.toString(16);}).join('');
  }
  function bimMatColorToFc(hex){
    var n=parseInt(String(hex||'#cccccc').slice(1),16);
    return '('+[(n>>16)&255,(n>>8)&255,n&255].map(function(c){return (c/255).toFixed(4);}).join(', ')+', 1.0)';
  }
  /* ---------- pure: .FCMat ---------- */
  /* A card from an .FCMat file's text: FreeCAD 1.0's YAML, or the older INI. Pure. */
  function bimFcmatParse(text){
    var lines=String(text||'').split(/\r?\n/),vals={},i;
    for(i=0;i<lines.length;i++){
      var L=lines[i];
      if(/^\s*[#;]/.test(L))continue;
      var m=/^\s*([A-Za-z][A-Za-z0-9]*)\s*[:=]\s*(.*?)\s*$/.exec(L);
      if(!m||m[2]==='')continue;
      var v=m[2],q=/^(["'])(.*)\1$/.exec(v);
      if(q)v=q[1]==='"'?q[2].replace(/\\(["\\])/g,'$1'):q[2].replace(/''/g,"'");   /* YAML's quoting undone */
      if(!(m[1] in vals))vals[m[1]]=v;   /* the first: General's Name before any model's */
    }
    if(!vals.Name)return {error:'No material name in the file'};
    var card={name:String(vals.Name).slice(0,80),kind:String(vals.KindOfMaterial||vals.Father||'Custom').slice(0,40),custom:true},k;
    for(k=0;k<BIM_MAT_FIELDS.length;k++){
      var F=BIM_MAT_FIELDS[k],raw=vals[F[3]];
      if(raw==null)continue;
      var q=bimMatQty(F[0],raw);
      if(q==null)continue;
      card[F[0]]=F[0]==='youngsModulus'?(+q.toPrecision(6))+' GPa':+q.toPrecision(8);   /* E as V120 keeps it */
    }
    var col=bimMatColorFromFc(vals.DiffuseColor);
    if(col)card.color=col;
    if(vals.Transparency!=null&&isFinite(parseFloat(vals.Transparency)))card.transparency=Math.max(0,Math.min(1,parseFloat(vals.Transparency)));
    if(vals.Description)card.description=String(vals.Description).slice(0,300);
    return card;
  }
  function bimMatYamlStr(s){return '"'+String(s).replace(/\\/g,'\\\\').replace(/"/g,'\\"')+'"';}
  /* A card as FreeCAD 1.0's .FCMat. Pure, but for the UUID it is given. */
  function bimFcmatWrite(card,uuid){
    var out=['---','# Written by BIM-Personal (MATERIALS)','General:','  UUID: '+bimMatYamlStr(uuid),'  Name: '+bimMatYamlStr(card.name)];
    if(card.description)out.push('  Description: '+bimMatYamlStr(card.description));
    out.push('Models:');
    out.push('  '+BIM_FCMAT_MODELS.standard[0]+':','    UUID: \''+BIM_FCMAT_MODELS.standard[1]+'\'','    KindOfMaterial: '+bimMatYamlStr(card.kind||'Custom'));
    ['linear','thermal'].forEach(function(model){
      var rows=[],k;
      for(k=0;k<BIM_MAT_FIELDS.length;k++){
        var F=BIM_MAT_FIELDS[k];
        if(F[4]!==model)continue;
        var v=F[0]==='youngsModulus'?bimMatQty('youngsModulus',card.youngsModulus):card[F[0]];
        if(v==null||v===''||!isFinite(v))continue;
        var unit={density:' kg/m^3',youngsModulus:' GPa',poissonRatio:'',yieldStrength:' MPa',tensileStrength:' MPa',conductivity:' W/m/K',specificHeat:' J/kg/K',expansion:' µm/m/K'}[F[0]];
        rows.push('    '+F[3]+': '+bimMatYamlStr(+(+v).toPrecision(8)+unit));
      }
      if(rows.length)out.push('  '+BIM_FCMAT_MODELS[model][0]+':','    UUID: \''+BIM_FCMAT_MODELS[model][1]+'\'');
      out.push.apply(out,rows);
    });
    out.push('AppearanceModels:','  '+BIM_FCMAT_MODELS.render[0]+':','    UUID: \''+BIM_FCMAT_MODELS.render[1]+'\'',
      '    DiffuseColor: '+bimMatYamlStr(bimMatColorToFc(card.color)),'    Transparency: '+bimMatYamlStr(String(card.transparency||0)));
    return out.join('\n')+'\n';
  }
  /* A card as the user typed it: a name, numbers where given. Pure. */
  function bimMatCardValid(c){
    if(!c||typeof c.name!=='string'||!c.name.replace(/\s+/g,''))return {error:'A material needs a name'};
    var out={name:c.name.replace(/^\s+|\s+$/g,'').slice(0,80),kind:String(c.kind||'Custom').slice(0,40)||'Custom',custom:true},k;
    for(k=0;k<BIM_MAT_FIELDS.length;k++){
      var f=BIM_MAT_FIELDS[k][0],v=c[f];
      if(v==null||v==='')continue;
      if(f==='youngsModulus'){var g=typeof v==='number'?v:bimMatQty(f,/[a-z]/i.test(String(v))?v:v+' GPa');if(g!=null&&g>0)out[f]=(+g.toPrecision(6))+' GPa';continue;}
      v=+v;
      if(!isFinite(v)||v<0)return {error:BIM_MAT_FIELDS[k][1]+' must be a number, not negative'};
      if(f==='poissonRatio'&&v>=0.5)return {error:'Poisson’s ratio is below 0.5'};
      out[f]=v;
    }
    if(/^#[0-9a-f]{6}$/i.test(String(c.color||'')))out.color=String(c.color).toLowerCase();
    if(c.transparency!=null&&isFinite(+c.transparency))out.transparency=Math.max(0,Math.min(1,+c.transparency));
    if(c.hatch&&typeof c.hatch==='object')out.hatch={angle:+c.hatch.angle||0,gap:+c.hatch.gap||10,cross:!!c.hatch.cross};
    if(c.description)out.description=String(c.description).slice(0,300);
    return out;
  }
  function bimMatCardsValid(list){
    var out=[],seen={},i;
    if(!Array.isArray(list))return [];
    for(i=0;i<list.length;i++){var c=bimMatCardValid(list[i]);if(!c.error&&!seen[c.name]){seen[c.name]=1;out.push(c);}}
    return out;
  }
  /* The library: the built-in cards (with what FreeCAD's generic ones add), then the project's; a project card of a
     built-in's name stands in for it. Pure on its inputs. */
  function bimMatLibrary(builtin,project){
    var out=[],by={},i;
    for(i=0;i<builtin.length;i++){
      var b=JSON.parse(JSON.stringify(builtin[i])),x=BIM_MAT_BUILTIN_EXTRA[b.name],k;
      if(x)for(k in x)if(b[k]==null)b[k]=x[k];
      by[b.name]=out.length;out.push(b);
    }
    for(i=0;i<(project||[]).length;i++){
      var p=JSON.parse(JSON.stringify(project[i]));
      if(by[p.name]!=null){var base=out[by[p.name]];out[by[p.name]]=p;if(!p.hatch&&base.hatch)p.hatch=base.hatch;}
      else{by[p.name]=out.length;out.push(p);}
    }
    return out;
  }
export {
  BIM_MAT_FIELDS, bimFcmatParse, bimFcmatWrite, bimMatCardValid, bimMatCardsValid, bimMatLibrary, bimMatQty
};
