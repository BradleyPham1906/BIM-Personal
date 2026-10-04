"""patch_phase144b.py -- V144: terrain in the app.

- Properties: a Terrain Analysis group on a surface -- colour it by slope, elevation or the way it
  faces, the area in each band, its breaklines and its boundary (each with Remove), triangles kept
  from LandXML (Re-triangulate), Export LandXML.
- The plan: a surface coloured by its bands, with a legend; breaklines drawn bold, the boundary
  dashed, the survey points outside it hollow.
- Commands: BREAKLINE, TERRAINBOUNDARY, SLOPEMAP, ELEVATIONMAP, ASPECTMAP, TERRAINANALYSISOFF,
  LANDXMLOUT, LANDXMLIN; IMPORTCAD reads .xml / .landxml as LandXML.
- An Analyze card: Terrain. The hooks, the version and the marker."""
NAME = 'patch_phase144b.py'
BASE = 'e5aaaeb9edaa52f68ffb95f4f3fb60522c4265c81f76b69409b065be37fa4637'
import hashlib, pathlib, sys
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')
raw = P.read_bytes()
h0 = hashlib.sha256(raw).hexdigest()
if h0 != BASE:
    sys.exit('ABORT: baseline %s, expected %s' % (h0, BASE))
t = raw.decode('utf-8')


def esc(s):
    return ''.join(ch if ord(ch) < 128 else '\\u%04x' % ord(ch) for ch in s)


def rep(old, new, n=1):
    global t
    new = esc(new)
    c = t.count(old)
    if c != n:
        sys.exit('ABORT: %d occurrences, expected %d: %r' % (c, n, old[:90]))
    t = t.replace(old, new)


# ---- the engine's UI helpers: the view command, the Properties group, the legend ----
rep("""  /* ================= __acad3dV138: verify the survey ================= */""",
    """  /* SLOPEMAP / ELEVATIONMAP / ASPECTMAP / TERRAINANALYSISOFF: the selected surfaces, else every one */
  function bimTerrainViewCommand(mode){
    var T=(A3D.selSet||[]).map(objById).filter(function(o){return o&&o.t==='terrain'&&o.survey;});
    if(!T.length)T=A3D.objs.filter(function(o){return o.t==='terrain'&&o.survey;});
    if(!T.length){a3dToast('There is no terrain surface: make one with SURVEY, or import LandXML');return null;}
    T.forEach(function(o){bimTerrainSetView(o,mode);});
    if(!mode){a3dToast('The terrain is no longer coloured');return [];}
    var b=bimTerrainBands(bimTerrainTin(T[0]),mode),top=b.bands.slice().sort(function(x,y){return y.area-x.area;})[0];
    a3dToast(T[0].name+(T.length>1?' and '+(T.length-1)+' more':'')+' coloured by '+mode+(top&&top.area>0?'; most of it '+top.label+' ('+Math.round(top.share*100)+'%)':'')+
      (bimCameraIsPlan()?'':' -- shown in plan'));
    return T.map(function(o){return o.id;});
  }
  function bimTerrainPropsHtml(o){
    var tin=null,r='',v=o.tview||'',b,i,nb=(o.breaklines||[]).length,ns=bimSurveyBreaklines(o).length,nOut;
    try{tin=bimTerrainTin(o);}catch(eT){console.warn('[BIM] terrain',eT);}
    if(!tin)return bimPropText('Analysis','the surface could not be triangulated');
    r+=bimPropRow('Colour By','<select data-propf="terrview">'+[['','None'],['slope','Slope'],['elevation','Elevation'],['aspect','Aspect (the way it faces)']].map(function(m){
      return '<option value="'+m[0]+'"'+(m[0]===v?' selected':'')+'>'+m[1]+'</option>';}).join('')+'</select>');
    if(v){
      b=bimTerrainBands(tin,v);
      r+='<div class="a3d-terrbands" data-terrbands="'+v+'">'+b.bands.map(function(x,k){
        return '<div class="a3d-terrband'+(x.area>0?'':' a3d-terrband-0')+'" data-band="'+k+'"><i style="background:'+x.col+'"></i><span class="a3d-terrbl">'+bimEsc(x.label)+'</span>'+
          '<span class="a3d-terrba">'+bimDispNum(x.area,1)+' m\\u00b2 &middot; '+Math.round(x.share*100)+'%</span></div>';}).join('')+'</div>';
    }
    r+=bimPropRow('Breaklines','<span class="a3d-pstatic" data-terrrow="breaklines">'+(nb||ns?(nb?nb+' drawn':'')+(nb&&ns?', ':'')+(ns?ns+' from the survey\\'s codes':'')+'; '+tin.constraints.length+' segment'+(tin.constraints.length===1?'':'s')+' held'+
      (tin.unforced.length?'; '+tin.unforced.length+' not: '+bimEsc(tin.unforced[0].why):''):'None: select a polyline, then BREAKLINE')+'</span>'+(nb?' <button data-propf="terrdrop:breaklines">Remove</button>':''));
    nOut=tin.outside?Object.keys(tin.outside).length:0;
    r+=bimPropRow('Boundary','<span class="a3d-pstatic" data-terrrow="boundary">'+(o.boundary&&o.boundary.length>=3?o.boundary.length+' corners, '+bimDispNum(bimPolyArea(o.boundary),1)+' m\\u00b2'+(nOut?'; '+nOut+' survey point'+(nOut===1?'':'s')+' outside, left out':''):'None: select a closed polyline, then TERRAINBOUNDARY')+'</span>'+
      (o.boundary?' <button data-propf="terrdrop:boundary">Remove</button>':''));
    if(o.faces)r+=bimPropRow('Triangles','<span class="a3d-pstatic" data-terrrow="faces">'+o.faces.length+' kept from '+bimEsc((o.source&&o.source.file)||'LandXML')+'</span> <button data-propf="terrdrop:faces">Re-triangulate</button>');
    r+=bimPropRow('LandXML','<button data-propf="terrlandxml">Export LandXML</button>');
    return r;
  }
  /* the legend of the coloured surface in plan: bottom left, over the drawing */
  function bimTerrainLegend(ctx,W,H,d){
    var rows=d.bands.filter(function(b){return b.area>0;}),lh=16,pad=8,w=0,i,h,x=12,y;
    if(!rows.length)return null;
    ctx.save();ctx.globalAlpha=1;ctx.font='11px sans-serif';ctx.textAlign='left';ctx.setLineDash([]);
    var title=d.name+': '+(d.view==='aspect'?'aspect':d.view);
    w=ctx.measureText(title).width;
    rows.forEach(function(b){var s=b.label+'  '+bimDispNum(b.area,0)+' m\\u00b2';b.txt=s;w=Math.max(w,ctx.measureText(s).width+18);});
    w+=pad*2;h=pad*2+lh*(rows.length+1);var sr=bimSafeViewRect();x=sr.x+12;y=sr.y+sr.h-12-h;
    ctx.fillStyle='rgba(22,25,29,0.88)';ctx.fillRect(x,y,w,h);ctx.strokeStyle='rgba(255,255,255,0.12)';ctx.strokeRect(x+0.5,y+0.5,w-1,h-1);
    ctx.textBaseline='middle';ctx.fillStyle='#e8edf2';ctx.fillText(title,x+pad,y+pad+lh/2);
    for(i=0;i<rows.length;i++){
      ctx.fillStyle=rows[i].col;ctx.fillRect(x+pad,y+pad+lh*(i+1)+3,12,lh-6);
      ctx.fillStyle='#c9d1d9';ctx.fillText(rows[i].txt,x+pad+18,y+pad+lh*(i+1)+lh/2);
    }
    ctx.restore();
    return {x:x,y:y,w:w,h:h,rows:rows.map(function(b){return b.label;})};
  }
  /* ================= __acad3dV138: verify the survey ================= */""")

# ---- the plan ----
rep("""        sp=tin.P.map(function(p){return toScreen([p[0],0,p[1]],V,W,H);});
        ctx.setLineDash([]);ctx.lineWidth=0.6;ctx.strokeStyle=sel?'rgba(78,161,255,0.35)':'rgba(176,133,89,0.2)';""",
    """        sp=tin.P.map(function(p){return toScreen([p[0],0,p[1]],V,W,H);});
        var tb=o.tview?bimTerrainBands(tin,o.tview):null;   /* __acad3dV144: coloured by its bands */
        if(tb){
          ctx.save();ctx.globalAlpha*=0.55;
          for(j=0;j<tin.tris.length;j++){
            if(tb.tri[j]<0)continue;
            a=sp[tin.tris[j][0]];b=sp[tin.tris[j][1]];c=sp[tin.tris[j][2]];
            if(!a||!b||!c)continue;
            ctx.fillStyle=ctx.strokeStyle=tb.bands[tb.tri[j]].col;ctx.lineWidth=0.5;
            ctx.beginPath();ctx.moveTo(a[0],a[1]);ctx.lineTo(b[0],b[1]);ctx.lineTo(c[0],c[1]);ctx.closePath();ctx.fill();ctx.stroke();
          }
          ctx.restore();
          if(!legendFor||sel)legendFor={name:o.name,view:o.tview,bands:tb.bands};
        }
        ctx.setLineDash([]);ctx.lineWidth=0.6;ctx.strokeStyle=sel?'rgba(78,161,255,0.35)':'rgba(176,133,89,0.2)';""")
rep("""        ctx.fillStyle=sel?'#4ea1ff':'#d9b38c';
        for(j=0;j<sp.length;j++)if(sp[j])ctx.fillRect(sp[j][0]-1.5,sp[j][1]-1.5,3,3);
        drawn.push({id:o.id,step:step,levels:cs.map(function(x){return x.level;}),segments:nseg,triangles:tin.tris.length});""",
    """        /* __acad3dV144: breaklines bold, the boundary dashed */
        if(tin.constraints.length){
          ctx.setLineDash([]);ctx.lineWidth=1.8;ctx.strokeStyle=sel?'#82c0ff':'#e0795a';ctx.beginPath();
          for(j=0;j<tin.constraints.length;j++){a=sp[tin.constraints[j][0]];b=sp[tin.constraints[j][1]];if(a&&b){ctx.moveTo(a[0],a[1]);ctx.lineTo(b[0],b[1]);}}
          ctx.stroke();
        }
        if(o.boundary&&o.boundary.length>=3){
          var tq=bimObjOffset(o);
          ctx.setLineDash([7,4]);ctx.lineWidth=1.4;ctx.strokeStyle=sel?'#4ea1ff':'#f0d0a8';ctx.beginPath();
          for(j=0;j<=o.boundary.length;j++){a=toScreen([o.boundary[j%o.boundary.length][0]+tq[0],0,o.boundary[j%o.boundary.length][1]+tq[2]],V,W,H);if(!a)continue;if(j)ctx.lineTo(a[0],a[1]);else ctx.moveTo(a[0],a[1]);}
          ctx.stroke();ctx.setLineDash([]);
        }
        ctx.fillStyle=sel?'#4ea1ff':'#d9b38c';ctx.strokeStyle=ctx.fillStyle;ctx.lineWidth=1;
        for(j=0;j<sp.length;j++)if(sp[j]){if(tin.outside&&tin.outside[j])ctx.strokeRect(sp[j][0]-1.5,sp[j][1]-1.5,3,3);else ctx.fillRect(sp[j][0]-1.5,sp[j][1]-1.5,3,3);}
        drawn.push({id:o.id,step:step,levels:cs.map(function(x){return x.level;}),segments:nseg,triangles:tin.tris.length,
          view:o.tview||'',bands:tb?tb.bands.map(function(x){return {label:x.label,col:x.col,area:x.area};}):null,constraints:tin.constraints.length,boundary:!!(o.boundary&&o.boundary.length>=3)});""")
rep("""    var drawn=[],i,j,k,s,o,tin,step,cs,sel,sp,a,b,c,best,bl,L,txt,ang,nseg;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(o.t!=='terrain')continue;""", """    var drawn=[],i,j,k,s,o,tin,step,cs,sel,sp,a,b,c,best,bl,L,txt,ang,nseg,legendFor=null;
    A3D.lastTerrainLegend=null;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(o.t!=='terrain')continue;""")
rep("""      ctx.restore();
    }
    A3D.lastTerrainDrawn=drawn;
  }""", """      ctx.restore();
    }
    if(legendFor){try{A3D.lastTerrainLegend=bimTerrainLegend(ctx,W,H,legendFor);}catch(eL){console.warn('[BIM] terrain legend',eL);}}   /* __acad3dV144 */
    A3D.lastTerrainDrawn=drawn;
  }""")

# ---- Properties ----
rep("""    if(o.t==='terrain'&&o.survey)h+=bimPropGroup('Survey Check',bimSurveyCheckHtml(o));   /* __acad3dV138 */""",
    """    if(o.t==='terrain'&&o.survey)h+=bimPropGroup('Survey Check',bimSurveyCheckHtml(o));   /* __acad3dV138 */
    if(o.t==='terrain'&&o.survey)h+=bimPropGroup('Terrain Analysis',bimTerrainPropsHtml(o));   /* __acad3dV144 */""")
rep("""      if(f==='editclass'){openClassificationDlg();return;}""", """      if(f==='editclass'){openClassificationDlg();return;}
      if(f.indexOf('terrdrop:')===0){var tdo=objById(A3D.sel);if(tdo)bimTerrainEdit(tdo,f.slice(9));return;}   /* __acad3dV144 */
      if(f==='terrlandxml'){var tlo=objById(A3D.sel);if(tlo)bimLandXmlExport([tlo.id]);return;}""")
rep("""      if(f==='terrint'){bimSetTerrainInterval(o,inp.value);return;}   /* __acad3dV108 */""",
    """      if(f==='terrint'){bimSetTerrainInterval(o,inp.value);return;}   /* __acad3dV108 */
      if(f==='terrview'){bimTerrainSetView(o,inp.value);return;}      /* __acad3dV144 */""")

# ---- Analyze ----
rep("""      acts:[{act:'survey:run',label:'Check',pri:true,off:nTer?'':'No survey surface yet'}]});""",
    """      acts:[{act:'survey:run',label:'Check',pri:true,off:nTer?'':'No survey surface yet'}]});
    /* __acad3dV144: terrain analysis */
    var TT=A3D.objs.filter(function(o){return o.t==='terrain'&&o.survey;}),tv=TT.filter(function(o){return o.tview;})[0],tvs='';
    if(tv){try{var tvb=bimTerrainBands(bimTerrainTin(tv),tv.tview),tvt=tvb.bands.slice().sort(function(x,y){return y.area-x.area;})[0];
      tvs=tv.name+' coloured by '+tv.tview+(tvt&&tvt.area>0?': most of it '+tvt.label+' ('+Math.round(tvt.share*100)+'%)':'');}catch(eTv){tvs=tv.name+' could not be measured';}}
    C.push({id:'terrain',title:'Terrain: Slope, Elevation, Aspect',state:TT.length?(tv?'on':'off'):null,
      status:TT.length?(tvs||TT.length+' surface'+(TT.length===1?'':'s')+': colour by slope, elevation or the way the ground faces'):'No terrain yet: make one with SURVEY, or import LandXML',
      acts:[{act:'terrain:slope',label:'Slope',pri:true,off:TT.length?'':'No terrain yet'},{act:'terrain:elevation',label:'Elevation',off:TT.length?'':'No terrain yet'},
        {act:'terrain:aspect',label:'Aspect',off:TT.length?'':'No terrain yet'},{act:'terrain:off',label:'Off',off:tv?'':'Not coloured'},
        {act:'terrain:landxml',label:'Export LandXML',off:TT.length?'':'No terrain yet'}]});""")
rep("""    else if(k==='survey:run')bimSurveyCheckCommand();""", """    else if(k==='survey:run')bimSurveyCheckCommand();
    else if(k==='terrain:landxml')bimLandXmlExport(null);   /* __acad3dV144 */
    else if(k.indexOf('terrain:')===0)bimTerrainViewCommand(k==='terrain:off'?'':k.slice(8));""")

# ---- commands ----
rep("""    ['SURVEYCHECK',['VERIFYSURVEY','QA'],""", """    ['BREAKLINE',['BRK','BREAKLINES'],'breakline','Hold the selected polylines in the terrain surface as breaklines: the triangles follow them'],   /* __acad3dV144 */
    ['TERRAINBOUNDARY',['TINBOUNDARY','SURFACEBOUNDARY'],'terrainboundary','Trim the terrain surface to the selected closed polyline'],
    ['SLOPEMAP',['SLOPE','SLOPEANALYSIS','GRADEANALYSIS'],'slopemap','Colour the terrain by slope in bands (0 to 2%, 2 to 5%, 5 to 8.33% ...), with the area of each'],
    ['ELEVATIONMAP',['ELEVATIONBANDS','HYPSOMETRIC'],'elevationmap','Colour the terrain by elevation, in seven bands, with the area of each'],
    ['ASPECTMAP',['ASPECT','ASPECTANALYSIS'],'aspectmap','Colour the terrain by the way it faces: north, north-east, east ...'],
    ['TERRAINANALYSISOFF',['TERRAINOFF'],'terrainviewoff','Stop colouring the terrain'],
    ['LANDXMLOUT',['EXPORTLANDXML','LANDXML'],'landxmlout','Export the terrain surfaces as LandXML 1.2: points, triangles, breaklines and boundary, in the survey\\'s own coordinates'],
    ['LANDXMLIN',['IMPORTLANDXML'],'landxmlin','Import the TIN surfaces of a LandXML file, keeping their own triangles'],
    ['SURVEYCHECK',['VERIFYSURVEY','QA'],""")
rep("""    surveycheck:function(){bimSurveyCheckCommand();},  /* __acad3dV138 */""", """    surveycheck:function(){bimSurveyCheckCommand();},  /* __acad3dV138 */
    breakline:function(){bimBreaklineCommand();},      /* __acad3dV144 */
    terrainboundary:function(){bimBoundaryCommand();},
    slopemap:function(){bimTerrainViewCommand('slope');},
    elevationmap:function(){bimTerrainViewCommand('elevation');},
    aspectmap:function(){bimTerrainViewCommand('aspect');},
    terrainviewoff:function(){bimTerrainViewCommand('');},
    landxmlout:function(){bimLandXmlExport(null);},
    landxmlin:function(){bimLandXmlPick();},""")
rep("""    CITYJSONIN:'cityjson citygml 3d city model import buildings lod 3dbag',""", """    CITYJSONIN:'cityjson citygml 3d city model import buildings lod 3dbag',
    BREAKLINE:'breakline terrain tin ridge ditch kerb curb edge constraint surface',   /* __acad3dV144 */
    TERRAINBOUNDARY:'terrain tin surface boundary trim clip outer limit',
    SLOPEMAP:'slope analysis gradient grade percent steepness terrain bands',
    ELEVATIONMAP:'elevation height bands terrain hypsometric tint colour',
    ASPECTMAP:'aspect orientation facing direction north south terrain slope',
    TERRAINANALYSISOFF:'terrain analysis colour off clear',
    LANDXMLOUT:'landxml civil 3d export tin surface survey xml',
    LANDXMLIN:'landxml civil 3d import tin surface survey xml',""")

# ---- import ----
rep("""    }else if(ext==='geojson'||ext==='kml'||ext==='kmz'){   /* __acad3dV132: site data */""",
    """    }else if(ext==='xml'||ext==='landxml'){   /* __acad3dV144: LandXML */
      reader.onload=function(ev){try{bimLandXmlImport(ev.target.result,name);}catch(eI){console.warn('[BIM] LandXML import crashed:',eI);a3dToast('LandXML import failed: '+(eI&&eI.message?eI.message:eI));}};
      reader.readAsText(file);
    }else if(ext==='geojson'||ext==='kml'||ext==='kmz'){   /* __acad3dV132: site data */""")
rep("""accept=".dxf,.ifc,.obj,.stl,.json,.geojson,.kml,.cityjson" """, """accept=".dxf,.ifc,.obj,.stl,.json,.geojson,.kml,.cityjson,.xml,.landxml" """)
rep(""".geojson and .kml site data, .city.json CityJSON)');""", """.geojson and .kml site data, .city.json CityJSON, .xml LandXML)');""")

rep(""".a3d-lodtag{""", """.a3d-terrbands{margin:2px 0 8px;display:flex;flex-direction:column;gap:2px}
.a3d-terrband{display:flex;align-items:center;gap:7px;font-size:11px;color:#c9d1d9}
.a3d-terrband i{width:12px;height:10px;border-radius:2px;flex:none}.a3d-terrbl{flex:1}.a3d-terrba{color:#9aa5b0}
.a3d-terrband-0{opacity:.45}
.a3d-lodtag{""")

# ---- hooks ----
rep("""  window.__a3dTinHeightAt=function(tid,x,z){""", """  window.__a3dTerrainBands=function(id,mode){var o=objById(id);if(!o||o.t!=='terrain')return null;var b=bimTerrainBands(bimTerrainTin(o),mode);
    return b?{bands:b.bands.map(function(x){return {label:x.label,col:x.col,area:x.area,share:x.share};}),tri:b.tri,total:b.total}:null;};
  window.__a3dLandXmlDoc=function(ids){return bimLandXmlDoc(ids||null);};
  window.__a3dLandXmlImport=function(text,name){return bimLandXmlImport(text,name||'test.xml');};
  window.__a3dBreakline=function(){return bimBreaklineCommand();};
  window.__a3dTerrainBoundary=function(){return bimBoundaryCommand();};
  window.__a3dTerrainSetView=function(id,mode){return bimTerrainSetView(objById(id),mode);};
  window.__a3dTerrainEdit=function(id,what){return bimTerrainEdit(objById(id),what);};
  window.__a3dTerrainView=function(mode){return bimTerrainViewCommand(mode);};
  window.__a3dModelToSurvey=function(id,x,z,y){return bimModelToSurvey(objById(id),x,z,y);};
  window.__a3dTerrainLegend=function(){return A3D.lastTerrainLegend||null;};
  window.__a3dTinHeightAt=function(tid,x,z){""")

rep("""  window.__a3dTerrainTin=function(id){var o=objById(id),t=o?bimTerrainTin(o):null;return t?{P:t.P,H:t.H,tris:t.tris}:null;};""",
    """  window.__a3dTerrainTin=function(id){var o=objById(id),t=o?bimTerrainTin(o):null;   /* __acad3dV144: and its breaklines, boundary, own faces */
    return t?{P:t.P,H:t.H,tris:t.tris,constraints:t.constraints,unforced:t.unforced,outside:t.outside?Object.keys(t.outside).map(Number):[],ownFaces:t.ownFaces}:null;};""")
rep("""  var BIM_APP_VERSION={v:'V143',date:'2026-10-04'};   /* __acad3dV143 */""", """  var BIM_APP_VERSION={v:'V144',date:'2026-10-04'};   /* __acad3dV144 */""")
rep("""  window.__acad3dV143='""", """  window.__acad3dV144='breaklines,surveybreaklines,boundary,ownfaces,slopebands,elevationbands,aspectbands,terrainlegend,landxmlout,landxmlin,terraincard,terraincommands';
  window.__acad3dV143='""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
