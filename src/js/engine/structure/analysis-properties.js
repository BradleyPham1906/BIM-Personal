  /* ================= __acad3dV125: the analysis in Properties ================= */
  function bimLoadLabel(ld){
    var s=ld.lc+'  ';
    if(ld.kind==='line')s+=bimDispNum(ld.v,2)+' kN/m along the beam';
    else if(ld.kind==='point')s+=bimDispNum(ld.v,2)+' kN at '+bimDispNum(ld.at,3)+' m';
    else s+=bimDispNum(ld.v,2)+' kN along '+(ld.dir==='z'?'Z':'X')+' at the top';
    return s;
  }
  function bimOpt(v,label,cur){return '<option value="'+v+'"'+(v===cur?' selected':'')+'>'+bimEsc(label)+'</option>';}
  /* __acad3dV126: the section's rows -- the numbers the analysis uses */
  function bimSectionPropsRows(o){
    var pf=bimMemberSection(o),pq=bimProfileProblem(pf),rows='';
    if(pq)return bimPropText('Section','Cannot be read: '+pq);
    var pp=bimProfileProps(pf),mat=bimMemberMaterial(o),tn=bimTypeNameOf(o);
    rows+=bimPropText('Section',(pf.shape!=='rect'&&tn?tn+' \u00b7 ':'')+BIM_PROFILE_SHAPES[pf.shape]);
    rows+=bimPropText('Area (cm\u00b2)',bimDispNum(pp.A*1e4,2));
    rows+=bimPropText('Iz (cm\u2074)',bimDispNum(pp.Iz*1e8,1));
    rows+=bimPropText('Iy (cm\u2074)',bimDispNum(pp.Iy*1e8,1));
    rows+=bimPropText('J (cm\u2074)',bimDispNum(pp.J*1e8,1));
    rows+=bimPropText('Mass (kg/m)',mat&&mat.density?bimDispNum(pp.A*mat.density,1)+' ('+mat.name+')':'\u2014');
    rows+=bimPropText('Basis',pf.shape==='rect'?'Solid rectangle':'Nominal dimensions; fillets not modelled');
    return rows;
  }
  function bimStructPropsHtml(o){
    var st=bimStructOf(o),rows=bimSectionPropsRows(o),i;
    if(o.bim.type==='column'){
      var auto=bimColumnSupport(o,o.bim.baseY+bimObjOffset(o)[1],true);
      var autoTxt='Automatic ('+(auto.kind?(auto.kind==='fixed'?'Fixed':'Pinned')+', '+auto.why:'none: '+auto.why)+')';
      rows+=bimPropRow('Support at base','<select data-propstr="support">'+bimOpt('',autoTxt,st.support||'')+
        bimOpt('fixed','Fixed',st.support)+bimOpt('pinned','Pinned',st.support)+bimOpt('free','Free (not held)',st.support)+'</select>');
    }else{
      rows+=bimPropRow('End connections','<select data-propstr="ends">'+bimOpt('','Rigid (moment)',st.ends==='pinned'?'x':'')+
        bimOpt('pinned','Pinned (shear only)',st.ends)+'</select>');
    }
    var loads=st.loads||[];
    for(i=0;i<loads.length;i++)
      rows+=bimPropRow('Load '+(i+1),'<span class="a3d-pstatic">'+bimEsc(bimLoadLabel(loads[i]))+'</span>'+
        '<button type="button" class="a3d-bdel" data-propstrdel="'+i+'" title="Remove this load">\u00d7</button>');
    /* the new-load row renders from a draft kept per member, so a re-render of the panel -- which any
       change in it may cause -- cannot throw away what is being typed */
    var kinds=o.bim.type==='column'?['lateral']:['line','point'],dr=bimLoadDraft(o);
    if(kinds.indexOf(dr.kind)<0)dr.kind=kinds[0];
    rows+=bimPropRow('New load','<select data-propstrnew="lc">'+bimOpt('D','Dead (D)',dr.lc)+bimOpt('L','Live (L)',dr.lc)+'</select>');
    rows+=bimPropRow('Kind','<select data-propstrnew="kind">'+kinds.map(function(k){return bimOpt(k,BIM_LOAD_KINDS[k],dr.kind);}).join('')+'</select>');
    rows+=bimPropRow('Value','<input type="number" step="any" data-propstrnew="v" value="'+bimEsc(dr.v)+'" placeholder="'+(o.bim.type==='column'?'kN':'kN/m or kN')+'">');
    if(o.bim.type==='column')rows+=bimPropRow('Direction','<select data-propstrnew="dir">'+bimOpt('x','Along X',dr.dir)+bimOpt('z','Along Z',dr.dir)+'</select>');
    else rows+=bimPropRow('At (m from start)','<input type="number" step="any" min="0" data-propstrnew="at" value="'+bimEsc(dr.at)+'" placeholder="point loads">');
    rows+=bimPropRow('','<button type="button" class="a3d-pedit" data-propstract="addload">Add load</button>');
    return bimPropGroup('Structural',rows);
  }
  function bimLoadDraft(o){
    var d=A3D_STRUCT.draft;
    if(!d||d.id!==o.id)d=A3D_STRUCT.draft={id:o.id,lc:'D',kind:'',v:'',at:'',dir:'x'};
    return d;
  }
  /* read first, in the capture phase, before any handler can re-render the panel */
  function bimLoadDraftInput(ev){
    var f=ev.target&&ev.target.getAttribute?ev.target.getAttribute('data-propstrnew'):null;
    var o=objById(A3D.sel);
    if(!f||!bimIsFrameMember(o))return;
    bimLoadDraft(o)[f]=ev.target.value;
  }
  /* __acad3dV166b: Frame analysis's settings and results, and the active level's floor loads, in its
     row in Analyze. They were Properties' Analysis page (V125) and its Floor Loads (V106). The fields
     keep their keys (data-propstr), so one handler serves them; the floor loads' are data-anzload. */
  function bimAnzField(id,label,ctl){return '<div class="a3d-anzfld"><label class="a3d-anzlab" for="a3d-anzf-'+id+'">'+bimEsc(label)+'</label>'+ctl+'</div>';}
  function bimAnzKv(rows){return '<dl class="a3d-anzkv">'+rows.map(function(r){return '<dt>'+bimEsc(r[0])+'</dt><dd>'+bimEsc(r[1])+'</dd>';}).join('')+'</dl>';}
  function bimAnzFrameHtml(){
    var h='',cur=A3D_STRUCT.show?(A3D_STRUCT.diagram||'M'):'off',nC=0,nB=0,i,lvA=null,kv=[];
    for(i=0;i<A3D.objs.length;i++)if(bimIsFrameMember(A3D.objs[i])){if(A3D.objs[i].bim.type==='column')nC++;else nB++;}
    if(nC||nB){
      h+='<div class="a3d-anzform">'+
        bimAnzField('combo','Combination','<select id="a3d-anzf-combo" data-propstr="combo">'+bimCombos().map(function(c){return bimOpt(c.name,c.name,A3D_STRUCT.combo);}).join('')+'</select>')+
        bimAnzField('selfweight','Self-weight','<select id="a3d-anzf-selfweight" data-propstr="selfweight">'+bimOpt('1','Included in D',A3D_STRUCT.selfWeight?'1':'0')+bimOpt('0','Not included',A3D_STRUCT.selfWeight?'1':'0')+'</select>')+
        bimAnzField('display','Display','<select id="a3d-anzf-display" data-propstr="display">'+bimOpt('off','Off',cur)+bimOpt('M','Bending moment',cur)+bimOpt('N','Axial force',cur)+bimOpt('V','Shear',cur)+'</select>')+
        bimAnzField('deflected','Deflected shape','<select id="a3d-anzf-deflected" data-propstr="deflected">'+bimOpt('1','Shown',A3D_STRUCT.deflected?'1':'0')+bimOpt('0','Hidden',A3D_STRUCT.deflected?'1':'0')+'</select>')+
        '</div>';
      kv.push(['Basis',(bimCombo(A3D_STRUCT.combo)||bimCombos()[0]).why]);
      var r=A3D_STRUCT.res;
      if(r&&r.error)kv.push(['Result',r.error]);
      else{
        var c=bimStructCurrent();
        if(c){
          var hd=bimStructHeadline(c);
          kv.push(['Largest moment',hd.moment?hd.moment.v.toFixed(1)+' kN\u00b7m, '+hd.moment.name:'none']);
          kv.push(['Largest deflection',hd.defl?(hd.defl.v*1000).toFixed(1)+' mm'+(hd.ratio?' (L/'+hd.ratio+')':'')+', '+hd.defl.name:'none']);
          kv.push(['Equilibrium',hd.balanced?'Balanced, '+hd.load.toFixed(1)+' kN':'NOT balanced: loads '+hd.load.toFixed(1)+', reactions '+hd.reaction.toFixed(1)+' kN']);
        }else kv.push(['Result',r?'Out of date: run it again':'Run it to solve the frame']);
      }
      kv.push(['Not included','Floor loads, wind, seismic']);
      h+=bimAnzKv(kv);
    }
    for(i=0;i<A3D.levels.length;i++)if(A3D.levels[i].id===A3D.activeLevel)lvA=A3D.levels[i];
    if(lvA){
      h+='<div class="a3d-anzsub">Floor loads on '+bimEsc(lvA.name)+'</div>'+
        '<div class="a3d-anzform">'+
        bimAnzField('dl','Dead (kPa)','<input type="number" step="any" min="0" inputmode="decimal" id="a3d-anzf-dl" data-anzload="dl" value="'+(lvA.dl==null?'':lvA.dl)+'" placeholder="not set" title="Dead load on '+bimEsc(lvA.name)+', kPa: slab self-weight plus superimposed">')+
        bimAnzField('ll','Live (kPa)','<input type="number" step="any" min="0" inputmode="decimal" id="a3d-anzf-ll" data-anzload="ll" value="'+(lvA.ll==null?'':lvA.ll)+'" placeholder="not set" title="Live load on '+bimEsc(lvA.name)+', kPa, unreduced">')+
        '</div><div class="a3d-anzcap">What this level\'s floors and roof put on the columns under them, in the Column Loads schedule and TRIBAREA. The active level is set in Properties, View.</div>';
    }
    return h;
  }
  /* __acad3dV166b: the project's areas by usage, in Areas by usage's row: each usage, then the total */
  function bimAnzAreasHtml(){
    var s=bimUsageSummary(null),h='';
    if(!s.rows.length)return '<div class="a3d-anzcap">Give a room, a floor or a mass a usage in its Properties (USAGE).</div>';
    s.rows.forEach(function(g){
      var k,v=[];
      for(k in g.values)if(g.values.hasOwnProperty(k))v.push(k+' '+bimUsageNum(g.values[k]));
      h+='<div class="a3d-anzarea" data-anzarea="'+bimEsc(g.usage)+'"><div class="a3d-anzareahd">'+bimUsageSwatch(g.color)+'<span class="a3d-anzareanm">'+bimEsc(g.name)+'</span>'+
        '<span class="a3d-anzarean">'+g.count+'</span></div>'+
        '<div class="a3d-anzareav">GBA '+bimDispNum(g.GBA,2)+' \u00b7 GFA '+bimDispNum(g.GFA,2)+' \u00b7 NSA '+bimDispNum(g.NSA,2)+' m\u00b2</div>'+
        (v.length?'<div class="a3d-anzareav">'+bimEsc(v.join(', '))+'</div>':'')+
        (g.errors?'<div class="a3d-anzareav a3d-anzareaerr">'+g.errors+' formula error'+(g.errors===1?'':'s')+'</div>':'')+'</div>';
    });
    if(s.rows.length>1)h+='<div class="a3d-anzarea a3d-anzareatot"><div class="a3d-anzareahd"><span class="a3d-anzareanm">Total</span></div>'+
      '<div class="a3d-anzareav">GBA '+bimDispNum(s.total.GBA,2)+' \u00b7 GFA '+bimDispNum(s.total.GFA,2)+' \u00b7 NSA '+bimDispNum(s.total.NSA,2)+' m\u00b2</div></div>';
    return h;
  }
  /* SUPPORT and LOAD: Properties, opened at the field they name */
  function bimStructFocus(what){
    var o=objById(A3D.sel);
    if(what==='support'&&!(o&&o.bim&&o.bim.type==='column')){a3dToast('Select a column: SUPPORT sets how its base is held');return false;}
    if(what==='load'&&!bimIsFrameMember(o)){a3dToast('Select a beam or a column: LOAD adds a load to it');return false;}
    A3D_PROP_GROUPS_OPEN['Structural']=true;
    refreshProps();
    var f=document.querySelector(what==='support'?'[data-propstr="support"]':'[data-propstrnew="v"]');
    if(f){if(f.scrollIntoView)f.scrollIntoView({block:'center'});f.focus();}
    a3dToast(what==='support'?'Set the support at the base of '+o.name+' in Properties':'Add a load to '+o.name+' in Properties');
    return true;
  }
  function bimStructEdit(o,fn){
    pushUndo();
    var st=JSON.parse(JSON.stringify(bimStructOf(o)));
    fn(st);
    o.bim.struct=st;
    refreshProps();paint();saveSoon();
  }
  function bimStructPropChange(ev){
    var el2=ev.target&&ev.target.closest?ev.target.closest('[data-propstr]'):null;
    if(!el2)return false;
    var k=el2.getAttribute('data-propstr'),v=el2.value,o=objById(A3D.sel);
    if(k==='combo'||k==='selfweight'){
      if(k==='combo'&&bimCombo(v))A3D_STRUCT.combo=v;
      if(k==='selfweight')A3D_STRUCT.selfWeight=(v==='1');
      if(A3D_STRUCT.show)bimStructAnalyze();
      refreshProps();paint();return true;
    }
    if(k==='display'){
      if(v==='off'){bimAnalyzeOff();return true;}
      A3D_STRUCT.diagram=v;
      if(!A3D_STRUCT.show)bimAnalyzeCommand();else{paint();refreshProps();}
      return true;
    }
    if(k==='deflected'){A3D_STRUCT.deflected=(v==='1');paint();refreshProps();return true;}
    if(!bimIsFrameMember(o))return true;
    if(k==='support')bimStructEdit(o,function(st){if(BIM_SUPPORTS.indexOf(v)>=0)st.support=v;else delete st.support;});
    else if(k==='ends')bimStructEdit(o,function(st){if(v==='pinned')st.ends='pinned';else delete st.ends;});
    return true;
  }
  function bimStructPropClick(ev){
    var o=objById(A3D.sel);
    var del=ev.target&&ev.target.closest?ev.target.closest('[data-propstrdel]'):null;
    if(del&&bimIsFrameMember(o)){
      var ix=parseInt(del.getAttribute('data-propstrdel'),10);
      bimStructEdit(o,function(st){if(st.loads&&st.loads[ix])st.loads.splice(ix,1);});
      a3dToast('Load removed from '+o.name);
      return true;
    }
    var add=ev.target&&ev.target.closest?ev.target.closest('[data-propstract="addload"]'):null;
    if(!add||!bimIsFrameMember(o))return false;
    var dr=bimLoadDraft(o);
    var ld={lc:dr.lc,kind:dr.kind||(o.bim.type==='column'?'lateral':'line'),v:parseFloat(dr.v)};
    if(ld.kind==='point')ld.at=parseFloat(dr.at);
    if(ld.kind==='lateral')ld.dir=dr.dir;
    var bad=bimLoadProblem(o,ld);
    if(bad){a3dToast(bad);return true;}
    dr.v='';dr.at='';
    bimStructEdit(o,function(st){(st.loads=st.loads||[]).push(ld);});
    a3dToast(bimLoadLabel(ld)+' added to '+o.name);
    return true;
  }
  function bimToggleTrib(){
    A3D.showTrib=!A3D.showTrib;
    paint();
    if(!A3D.showTrib){a3dToast('Tributary areas hidden');return false;}
    var res=bimColumnLoads(),t=null,k;
    for(k=0;k<res.levels.length;k++)if(res.levels[k].levelId===A3D.activeLevel)t=res.levels[k];
    if(!t)a3dToast('Tributary areas: no floor or roof on this level, and no column under it');
    else if(!t.columns)a3dToast('No column carries the '+t.slabArea.toFixed(2)+' m² of slab on this level');
    else a3dToast('Tributary areas: '+t.onColumns.toFixed(2)+' of '+t.slabArea.toFixed(2)+' m² on '+t.columns+' column'+(t.columns===1?'':'s')+' below');
    return true;
  }
  function bimBuildColumnSchedule(){
    return A3D.objs.filter(function(o){return o.t==='solid'&&o.bim&&o.bim.type==='column';}).map(function(o){
      return bimMergeRow(bimMatRow(o),{name:o.name,width:o.bim.width,depth:o.bim.depth,height:o.bim.height,level:bimLevelName(o.bim.levelId)});
    });
  }
  var SCHEDULE_DEFS={
    room:{label:'Rooms',build:bimBuildRoomSchedule,cols:[{key:'number',label:'Number'},{key:'name',label:'Name'},{key:'level',label:'Level'},{key:'area',label:'Area (m\u00b2)',fmt:2},{key:'dept',label:'Department'},{key:'occupancy',label:'Occupancy'},{key:'loadFactor',label:'Load Factor (m²/person)',fmt:2},{key:'loadBasis',label:'Basis'},{key:'loadSrc',label:'Factor Source'},{key:'occupants',label:'Occupant Load'},{key:'finishFloor',label:'Floor'},{key:'finishWall',label:'Wall'},{key:'finishCeiling',label:'Ceiling'},{key:'source',label:'Source'}]},
    door:{label:'Doors',build:bimBuildDoorSchedule,cols:[{key:'name',label:'Name'},{key:'hostWall',label:'Host Wall'},{key:'width',label:'Width (m)',fmt:2},{key:'height',label:'Height (m)',fmt:2}]},
    window:{label:'Windows',build:bimBuildWindowSchedule,cols:[{key:'name',label:'Name'},{key:'hostWall',label:'Host Wall'},{key:'width',label:'Width (m)',fmt:2},{key:'height',label:'Height (m)',fmt:2},{key:'sillHeight',label:'Sill (m)',fmt:2}]},
    wall:{label:'Walls',build:bimBuildWallSchedule,cols:[{key:'name',label:'Name'},{key:'level',label:'Level'},{key:'length',label:'Length (m)',fmt:2},{key:'thickness',label:'Thickness (m)',fmt:2},{key:'height',label:'Height (m)',fmt:2},{key:'area',label:'Area (m\u00b2)',fmt:2}].concat(BIM_MAT_COLS)},
    ceiling:{label:'Ceilings',build:bimBuildCeilingSchedule,cols:[{key:'name',label:'Name'},{key:'level',label:'Level'},{key:'area',label:'Area (m\u00b2)',fmt:2},{key:'height',label:'Height (m)',fmt:2},{key:'thickness',label:'Thickness (m)',fmt:3}].concat(BIM_MAT_COLS)},
    column:{label:'Columns',build:bimBuildColumnSchedule,cols:[{key:'name',label:'Name'},{key:'level',label:'Level'},{key:'width',label:'Width (m)',fmt:2},{key:'depth',label:'Depth (m)',fmt:2},{key:'height',label:'Height (m)',fmt:2}].concat(BIM_MAT_COLS)},
    colload:{label:'Column Loads',build:function(){return bimColumnLoads().rows;},cols:[{key:'name',label:'Column'},{key:'grid',label:'Grid'},{key:'level',label:'Level'},{key:'supports',label:'Carries'},{key:'tribArea',label:'Tributary (m²)',fmt:2},{key:'floorD',label:'Floor D (kN)',fmt:1},{key:'floorL',label:'Floor L (kN)',fmt:1},{key:'axialD',label:'Axial D, slabs only (kN)',fmt:1},{key:'axialL',label:'Axial L, unreduced (kN)',fmt:1},{key:'service',label:'D+L (kN)',fmt:1},{key:'factored',label:'1.2D+1.6L (kN)',fmt:1},{key:'carriedBy',label:'On'},{key:'note',label:'Note'}]},   /* __acad3dV106 */
    earthwork:{label:'Earthwork',build:bimEarthwork,cols:[{key:'pad',label:'Pad'},{key:'surface',label:'Surface'},{key:'padElev',label:'Pad Elevation (m)',fmt:3},{key:'padArea',label:'Pad Area (m\u00b2)',fmt:2},{key:'onSurface',label:'Measured (m\u00b2)',fmt:2},{key:'cut',label:'Cut (m\u00b3)',fmt:2},{key:'fill',label:'Fill (m\u00b3)',fmt:2},{key:'net',label:'Net Cut (m\u00b3)',fmt:2},{key:'method',label:'Method'},{key:'note',label:'Note'}]},   /* __acad3dV108 */
    footing:{label:'Isolated Footings',build:function(){return bimBuildFootingSchedule('footing');},cols:[{key:'name',label:'Name'},{key:'type',label:'Type'},{key:'host',label:'Under'},{key:'width',label:'Width (m)',fmt:2},{key:'length',label:'Length (m)',fmt:2},{key:'thickness',label:'Thickness (m)',fmt:2},{key:'volume',label:'Concrete (m\u00b3)',fmt:3},{key:'level',label:'Level'}]},   /* __acad3dV102 */
    stripfooting:{label:'Wall Foundations',build:function(){return bimBuildFootingSchedule('stripfooting');},cols:[{key:'name',label:'Name'},{key:'type',label:'Type'},{key:'host',label:'Under'},{key:'length',label:'Length (m)',fmt:2},{key:'width',label:'Width (m)',fmt:2},{key:'thickness',label:'Thickness (m)',fmt:2},{key:'volume',label:'Concrete (m\u00b3)',fmt:3},{key:'level',label:'Level'}]},
    beam:{label:'Beams',build:bimBuildBeamSchedule,cols:[{key:'name',label:'Name'},{key:'level',label:'Level'},{key:'span',label:'Span (m)',fmt:2},{key:'width',label:'Width (m)',fmt:2},{key:'depth',label:'Depth (m)',fmt:2},{key:'topY',label:'Top elev (m)',fmt:3}].concat(BIM_MAT_COLS)},
    memberforces:{label:'Member Forces',build:bimMemberForceRows,cols:[{key:'member',label:'Member'},{key:'kind',label:'Kind'},{key:'combo',label:'Combination'},{key:'length',label:'Length (m)',fmt:2},{key:'tension',label:'Tension (kN)',fmt:1},{key:'compression',label:'Compression (kN)',fmt:1},{key:'shear',label:'Shear (kN)',fmt:1},{key:'mz',label:'Moment, major (kN\u00b7m)',fmt:1},{key:'my',label:'Moment, minor (kN\u00b7m)',fmt:1},{key:'defl',label:'Deflection (mm)',fmt:1},{key:'ratio',label:'Span / deflection'},{key:'note',label:'Note'}]},   /* __acad3dV125 */
    alignment:{label:'Alignment',build:bimAlignScheduleRows,cols:[{key:'alignment',label:'Alignment'},{key:'pi',label:'PI'},{key:'station',label:'Station'},{key:'delta',label:'Deflection (\u00b0)'},{key:'turn',label:'Turn'},{key:'radius',label:'Radius (m)',fmt:3},{key:'tangent',label:'T (m)',fmt:3},{key:'length',label:'L (m)',fmt:3},{key:'external',label:'E (m)',fmt:3},{key:'pc',label:'PC'},{key:'pt',label:'PT'},{key:'note',label:'Note'}]},   /* __acad3dV127 */
    profile:{label:'Profile',build:bimProfileScheduleRows,cols:[{key:'alignment',label:'Alignment'},{key:'pvi',label:'PVI'},{key:'station',label:'Station'},{key:'elev',label:'Elevation (m)',fmt:3},{key:'gin',label:'Grade in (%)',fmt:3},{key:'gout',label:'Grade out (%)',fmt:3},{key:'L',label:'Curve L (m)',fmt:2},{key:'K',label:'K',fmt:2},{key:'kind',label:'Curve'},{key:'turn',label:'High / low point'},{key:'note',label:'Note'}]},
    reactions:{label:'Reactions',build:bimReactionRows,cols:[{key:'at',label:'At'},{key:'support',label:'Support'},{key:'combo',label:'Combination'},{key:'fx',label:'Fx (kN)',fmt:1},{key:'fy',label:'Fy (kN)',fmt:1},{key:'fz',label:'Fz (kN)',fmt:1},{key:'mx',label:'Mx (kN\u00b7m)',fmt:1},{key:'my',label:'My (kN\u00b7m)',fmt:1},{key:'mz',label:'Mz (kN\u00b7m)',fmt:1},{key:'note',label:'Note'}]},
    usage:{label:'Areas by Usage',build:bimUsageScheduleRows,cols:[{key:'usage',label:'Usage'},{key:'level',label:'Level'},{key:'objects',label:'Objects'},{key:'gba',label:'GBA (m\u00b2)',fmt:2},{key:'gfa',label:'GFA (m\u00b2)',fmt:2},{key:'nsa',label:'NSA (m\u00b2)',fmt:2},{key:'values',label:'Formulas'}]},   /* __acad3dV131 */
    arealevel:{label:'Areas by Level',build:bimBuildAreaSchedule,cols:[{key:'level',label:'Level'},{key:'gross',label:'Gross (m\u00b2)',fmt:2},{key:'net',label:'Net (m\u00b2)',fmt:2},{key:'efficiency',label:'Efficiency (%)',fmt:1},{key:'rooms',label:'Rooms'},{key:'occupants',label:'Occupant Load'},{key:'note',label:'Note'}]}   /* __acad3dV105b */
  };
  /* __acad3dV74: schedules are a REGISTRY now, not a literal plus two hand-kept lists.

     The bug that forced this: SCHEDULE_DEFS had seven entries and the Project Browser listed
     six from a hardcoded array that omitted 'beam'. Since the only other chooser
     (#a3d-schedcat) is display:none, the Beams schedule was unreachable -- built, columned and
     CSV-exportable, with no way for a user to open it. Adding 'beam' to the literal would fix
     today and drift again on the next schedule; deriving every list from SCHEDULE_DEFS fixes
     the class, and is the same change that lets a domain pack register its own.

     A registered schedule needs nothing else: the renderer, the CSV export and the Project
     Browser all read this one object. BIM_MAT_COLS is published alongside so a domain that
     wants the Material / Volume / Mass takeoff columns reuses the same three rather than
     inventing a parallel set that formats differently. */
  function bimScheduleKeys(){
    var out=[],k;
    for(k in SCHEDULE_DEFS)if(SCHEDULE_DEFS.hasOwnProperty(k))out.push(k);
    return out;
  }
  function bimRegisterSchedule(spec){
    if(!spec||!spec.id||typeof spec.build!=='function')return false;
    if(!spec.cols||!spec.cols.length)return false;
    SCHEDULE_DEFS[spec.id]={label:spec.label||spec.id,build:spec.build,cols:spec.cols.slice()};
    bimSyncScheduleCats();
    if(el.browser)refreshBrowser();
    return true;
  }
  /* The category select is hidden (the Project Browser is the chooser), but it is still the
     element refreshSchedule and the CSV export read their category from -- so it has to carry
     every registered id or a registered schedule could be listed and then fail to open. */
  function bimSyncScheduleCats(){
    if(!el.schedcat)return;
    var keys=bimScheduleKeys(),h='',i,cur=el.schedcat.value;
    for(i=0;i<keys.length;i++)
      h+='<option value="'+bimEsc(keys[i])+'">'+bimEsc(SCHEDULE_DEFS[keys[i]].label)+'</option>';
    if(el.schedcat.innerHTML!==h){
      el.schedcat.innerHTML=h;
      if(cur&&SCHEDULE_DEFS[cur])el.schedcat.value=cur;
    }
  }
  function bimFmtScheduleValue(v,fmt){
    if(v===null||v===undefined)return '\u2014';
    if(fmt&&typeof v==='number')return v.toFixed(fmt);
    return String(v);
  }
  function bimScheduleToCSV(rows,columns){
    function esc(v){
      if(v===null||v===undefined)return '';
      var s=String(v);
      if(s.indexOf(',')>=0||s.indexOf('"')>=0||s.indexOf('\n')>=0)return '"'+s.replace(/"/g,'""')+'"';
      return s;
    }
    var lines=[columns.map(function(c){return esc(c.label);}).join(',')],i;
    for(i=0;i<rows.length;i++)lines.push(columns.map(function(c){return esc(rows[i][c.key]);}).join(','));
    return lines.join('\r\n');
  }
  function refreshSchedule(){
    if(!el.schedbody)return;
    var cat=el.schedcat?el.schedcat.value:'room';
    var def=SCHEDULE_DEFS[cat];
    if(!def){el.schedbody.innerHTML='';return;}
    var rows=def.build();
    if(!rows.length){el.schedbody.innerHTML='<div class="a3d-propnote">No '+def.label.toLowerCase()+' in the model yet.</div>';return;}
    var h='<table class="a3d-schedtbl"><thead><tr>';
    var i,j;
    for(j=0;j<def.cols.length;j++)h+='<th>'+def.cols[j].label+'</th>';
    h+='</tr></thead><tbody>';
    for(i=0;i<rows.length;i++){
      h+='<tr>';
      for(j=0;j<def.cols.length;j++)h+='<td>'+bimFmtScheduleValue(rows[i][def.cols[j].key],def.cols[j].fmt)+'</td>';
      h+='</tr>';
    }
    h+='</tbody></table><div class="a3d-propnote">'+rows.length+' '+def.label.toLowerCase()+'</div>';
    el.schedbody.innerHTML=h;
  }
  function bimExportScheduleCSV(){
    var cat=el.schedcat?el.schedcat.value:'room';
    var def=SCHEDULE_DEFS[cat];
    if(!def)return;
    var rows=def.build();
    if(!rows.length){a3dToast('No '+def.label.toLowerCase()+' to export');return;}
    var csv=bimScheduleToCSV(rows,def.cols);
    bimTriggerDownload(csv,bimFileStem()+'-'+def.label.toLowerCase()+'_schedule.csv','text/csv');
    a3dToast('Exported '+bimFileStem()+'-'+def.label.toLowerCase()+'_schedule.csv ('+rows.length+' rows)');
  }
