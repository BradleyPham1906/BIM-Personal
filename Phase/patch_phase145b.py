"""patch_phase145b.py -- V145: grading in the app.

- A pad's Properties: its cut and fill slopes, and the surface it is graded into.
- A proposed surface's Properties: a Grading group (its existing surface, its pads, cut, fill and
  net, out of date or not, Grade Again, Spot the Pad Corners); Colour By cut and fill.
- Slope Arrows on any surface; a point's spot elevation.
- The plan: the proposed surface's contours green, the existing one under it dashed, arrows, spots.
- Commands: GRADE, CUTFILL, CUTFILLMAP, SPOTELEV, SLOPEARROWS. A Grading card in Analyze.
- The hooks, the version and the marker."""
NAME = 'patch_phase145b.py'
BASE = '7492b766ed04e66478d8ecebac9148c8fec5fab062e206ccadb9781a89696cfa'
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


UI = r"""  /* __acad3dV145: a proposed surface's Grading group */
  function bimGradePropsHtml(o){
    var g=o.grading,e=objById(g.existing),v=g.volume||null,r='',st=bimGradeStale(o);
    r+=bimPropText('Existing',e?e.name:'(gone)');
    g.pads.forEach(function(p){
      r+=bimPropText('Pad',p.name+' at '+bimDispNum(p.elev,3)+' m; cut '+bimDispNum(p.cut,2)+':1, fill '+bimDispNum(p.fill,2)+':1'+
        (p.offSurface?'; '+p.offSurface+' slope'+(p.offSurface===1?'':'s')+' run off the surface':''));
    });
    if(v){
      r+='<div data-graderow="cut">'+bimPropText('Cut',bimDispNum(v.cut,2)+' m³ over '+bimDispNum(v.cutArea,1)+' m²')+'</div>';
      r+='<div data-graderow="fill">'+bimPropText('Fill',bimDispNum(v.fill,2)+' m³ over '+bimDispNum(v.fillArea,1)+' m²')+'</div>';
      r+='<div data-graderow="net">'+bimPropText('Net',v.net>=0?bimDispNum(v.net,2)+' m³ to take away':bimDispNum(-v.net,2)+' m³ to bring in')+'</div>';
    }
    if(g.overlaps&&g.overlaps.length)r+=bimPropText('Overlap','the slopes of '+g.overlaps.join('; ')+' overlap: grade them apart, or check the surface there');
    if(g.dropped)r+=bimPropText('Breaklines',g.dropped+' of the existing surface\'s breaklines cross the grading and are left out');
    r+=bimPropRow('Grading','<span class="a3d-pstatic" data-graderow="state">'+(st?'Out of date: the pads or the existing surface have changed':'Up to date')+'</span> '+
      '<button data-propf="regrade">'+(st?'Grade Again':'Regrade')+'</button>');
    r+=bimPropRow('Spots','<button data-propf="gradespots">Spot the Pad Corners</button>');
    return r;
  }
  /* downhill arrows on the triangles big enough on screen to hold one; the slope beside the bigger */
  function bimDrawSlopeArrows(ctx,tin,V,W,H,sel){
    var out=[],t,n=0;
    ctx.save();ctx.setLineDash([]);ctx.globalAlpha=1;ctx.strokeStyle=ctx.fillStyle=sel?'#82c0ff':'#5fa8d3';ctx.lineWidth=1.2;
    ctx.font='10px sans-serif';ctx.textAlign='center';ctx.textBaseline='middle';
    for(t=0;t<tin.tris.length;t++){
      var tr=tin.tris[t],A=tin.P[tr[0]],B=tin.P[tr[1]],C=tin.P[tr[2]],pl=bimPlane3(A,B,C,tin.H[tr[0]],tin.H[tr[1]],tin.H[tr[2]]);
      if(!pl)continue;
      var s=Math.sqrt(pl[0]*pl[0]+pl[1]*pl[1]);
      if(s<0.005)continue;   /* under 0.5%: flat */
      var cx=(A[0]+B[0]+C[0])/3,cz=(A[1]+B[1]+C[1])/3,dx=-pl[0]/s,dz=-pl[1]/s;
      var sa=toScreen([A[0],0,A[1]],V,W,H),sb=toScreen([B[0],0,B[1]],V,W,H),sc=toScreen([C[0],0,C[1]],V,W,H),c0=toScreen([cx,0,cz],V,W,H),c1=toScreen([cx+dx,0,cz+dz],V,W,H);
      if(!sa||!sb||!sc||!c0||!c1)continue;
      var sz=Math.sqrt(Math.abs((sb[0]-sa[0])*(sc[1]-sa[1])-(sc[0]-sa[0])*(sb[1]-sa[1]))/2);
      if(sz<16)continue;
      var vx=c1[0]-c0[0],vy=c1[1]-c0[1],vl=Math.sqrt(vx*vx+vy*vy);
      if(!(vl>1e-9))continue;
      vx/=vl;vy/=vl;
      var L=Math.min(9,sz*0.3),hx=c0[0]+vx*L,hy=c0[1]+vy*L;
      ctx.beginPath();ctx.moveTo(c0[0]-vx*L,c0[1]-vy*L);ctx.lineTo(hx,hy);
      ctx.moveTo(hx,hy);ctx.lineTo(hx-vx*5-vy*3,hy-vy*5+vx*3);ctx.moveTo(hx,hy);ctx.lineTo(hx-vx*5+vy*3,hy-vy*5-vx*3);ctx.stroke();
      if(sz>56)ctx.fillText(bimDispNum(s*100,1)+'%',c0[0]-vy*11,c0[1]+vx*11);
      n++;
      if(out.length<400)out.push({x:cx,z:cz,dx:dx,dz:dz,slope:s*100});
    }
    ctx.restore();
    return {count:n,list:out};
  }
  /* each spot point's height, from the surface under it, beside it on a leader */
  function bimDrawSpots(ctx,V,W,H){
    var out=[],i,o;
    ctx.save();ctx.setLineDash([]);ctx.globalAlpha=1;ctx.font='11px sans-serif';ctx.textAlign='left';ctx.textBaseline='middle';
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(!o.spot||!bimIsPoint(o)||!bimLayerShown(o))continue;
      var e=bimSpotElev(o),s=toScreen([e.x,0,e.z],V,W,H);
      if(!s)continue;
      var txt=e.h===null?'no surface':e.h.toFixed(2),w=ctx.measureText(txt).width,lx=s[0]+12,ly=s[1]-12;
      ctx.strokeStyle='#ffd479';ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(s[0],s[1]);ctx.lineTo(lx,ly);ctx.lineTo(lx+w+6,ly);ctx.stroke();
      ctx.fillStyle='rgba(22,25,29,0.85)';ctx.fillRect(lx,ly-13,w+6,12);
      ctx.fillStyle='#ffe7a8';ctx.fillText(txt,lx+3,ly-7);
      out.push({id:o.id,h:e.h,surface:e.surface,text:txt});
    }
    ctx.restore();
    return out;
  }
"""

rep("""  /* the legend of the coloured surface in plan: bottom left, over the drawing */""",
    UI + """  /* the legend of the coloured surface in plan: bottom left, over the drawing */""")
rep("""    var title=d.name+': '+(d.view==='aspect'?'aspect':d.view);""", """    var title=d.name+': '+(d.view==='cutfill'?'cut and fill':d.view);   /* __acad3dV145 */""")

# ---- Properties ----
rep("""['aspect','Aspect (the way it faces)']].map(function(m){""",
    """['aspect','Aspect (the way it faces)']].concat(o.grading?[['cutfill','Cut and fill (against the existing)']]:[]).map(function(m){   /* __acad3dV145 */""")
rep("""      b=bimTerrainBands(tin,v);
      r+='<div class="a3d-terrbands" data-terrbands="'+v+'">'""", """      b=v==='cutfill'?bimBandsOf(o,v):bimTerrainBands(tin,v);   /* __acad3dV145 */
      if(b)r+='<div class="a3d-terrbands" data-terrbands="'+v+'">'""")
rep("""    r+=bimPropRow('Breaklines','<span class="a3d-pstatic" data-terrrow="breaklines">'""",
    """    r+=bimPropRow('Slope Arrows','<input type="checkbox" data-propf="terrarrows"'+(o.arrows?' checked':'')+'>');   /* __acad3dV145 */
    r+=bimPropRow('Breaklines','<span class="a3d-pstatic" data-terrrow="breaklines">'""")
rep("""    if(o.t==='terrain'&&o.survey)h+=bimPropGroup('Terrain Analysis',bimTerrainPropsHtml(o));   /* __acad3dV144 */""",
    """    if(o.t==='terrain'&&o.survey)h+=bimPropGroup('Terrain Analysis',bimTerrainPropsHtml(o));   /* __acad3dV144 */
    if(o.t==='terrain'&&o.grading)h+=bimPropGroup('Grading',bimGradePropsHtml(o));            /* __acad3dV145 */""")
rep("""        dims+=bimPropRow('Pad Elevation (m)','<input type="number" step="any" data-propf="gradeelev" value="'+(isFinite(parseFloat(o.gradeElev))?o.gradeElev:'')+'" placeholder="not a pad">');""",
    """        dims+=bimPropRow('Pad Elevation (m)','<input type="number" step="any" data-propf="gradeelev" value="'+(isFinite(parseFloat(o.gradeElev))?o.gradeElev:'')+'" placeholder="not a pad">');
        if(bimIsPad(o)){   /* __acad3dV145: its slopes, and the surface it is graded into */
          dims+=bimPropRow('Cut Slope (H:V)','<input type="number" step="any" min="0" data-propf="cutslope" value="'+(isFinite(parseFloat(o.cutSlope))?o.cutSlope:'')+'" placeholder="'+BIM_GRADE.cut+' (2:1)">');
          dims+=bimPropRow('Fill Slope (H:V)','<input type="number" step="any" min="0" data-propf="fillslope" value="'+(isFinite(parseFloat(o.fillSlope))?o.fillSlope:'')+'" placeholder="'+BIM_GRADE.fill+' (2:1)">');
          var gby=bimGradedBy(o);
          dims+=bimPropText('Graded',gby?gby.name+(bimGradeStale(gby)?' (out of date: GRADE again)':''):'not yet: GRADE');
        }""")
rep("""      dims+=bimPropText('Y',o.pts[0][1].toFixed(3));
    }else if(o.t==='terrain'){""", """      dims+=bimPropText('Y',o.pts[0][1].toFixed(3));
      if(o.spot){var spe=bimSpotElev(o);dims+=bimPropText('Spot Elevation',spe.h===null?'not over a surface':bimDispNum(spe.h,3)+' m on '+spe.name);}   /* __acad3dV145 */
    }else if(o.t==='terrain'){""")
rep("""      if(f==='terrview'){bimTerrainSetView(o,inp.value);return;}      /* __acad3dV144 */""",
    """      if(f==='terrview'){bimTerrainSetView(o,inp.value);return;}      /* __acad3dV144 */
      if(f==='cutslope'||f==='fillslope'){bimSetPadSlope(o,f,inp.value);return;}   /* __acad3dV145 */
      if(f==='terrarrows'){bimSetSlopeArrows(o,inp.checked);return;}""")
rep("""      if(f==='terrlandxml'){var tlo=objById(A3D.sel);if(tlo)bimLandXmlExport([tlo.id]);return;}""",
    """      if(f==='terrlandxml'){var tlo=objById(A3D.sel);if(tlo)bimLandXmlExport([tlo.id]);return;}
      if(f==='regrade'){bimRegrade(objById(A3D.sel));return;}   /* __acad3dV145 */
      if(f==='gradespots'){bimGradeSpots(objById(A3D.sel));return;}""")
rep("""  function bimSetGradeElev(o,val){""", """  /* __acad3dV145: a pad's cut or fill slope, as horizontal units per vertical unit */
  function bimSetPadSlope(o,which,val){
    var v=String(val==null?'':val).replace(/^\\s+|\\s+$/g,''),n=parseFloat(v),key=which==='cutslope'?'cutSlope':'fillSlope';
    if(!bimIsPad(o))return false;
    if(v!==''&&!(isFinite(n)&&n>0&&n<=100)){a3dToast('A slope is the horizontal run for a rise of one, over 0 (2 is 2:1)');refreshProps();return false;}
    if(v===''?o[key]==null:o[key]===n)return true;
    pushUndo();
    if(v==='')delete o[key];else o[key]=n;
    refreshProps();paint();saveSoon();bimAnalyzeRefresh();
    return true;
  }
  function bimSetGradeElev(o,val){""")

# ---- the plan ----
rep("""    A3D.lastTerrainDrawn=null;
    if(!bimCameraIsPlan())return;   /* __acad3dV119: flat is not plan -- an elevation is flat */""",
    """    A3D.lastTerrainDrawn=null;A3D.lastSpotsDrawn=null;   /* __acad3dV145 */
    if(!bimCameraIsPlan())return;   /* __acad3dV119: flat is not plan -- an elevation is flat */""")
rep("""        var tb=o.tview?bimTerrainBands(tin,o.tview):null;   /* __acad3dV144: coloured by its bands */""",
    """        var tb=o.tview?(o.tview==='cutfill'?bimBandsOf(o,'cutfill'):bimTerrainBands(tin,o.tview)):null;   /* __acad3dV144: coloured by its bands */
        var sup=!o.grading&&!!bimTerrainSuperseded(o);   /* __acad3dV145: an existing surface under a proposed one */""")
rep("""          ctx.lineWidth=cs[j].index?1.5:0.8;ctx.strokeStyle=sel?'#4ea1ff':(cs[j].index?'#c89a6a':'#8f7050');""",
    """          ctx.lineWidth=cs[j].index?1.5:0.8;ctx.strokeStyle=sel?'#4ea1ff':o.grading?(cs[j].index?'#a5d47f':'#6f9a52'):(cs[j].index?'#c89a6a':'#8f7050');
          ctx.setLineDash(sup?[5,4]:[]);   /* __acad3dV145: proposed green, the existing under it dashed */""")
rep("""        /* __acad3dV144: breaklines bold, the boundary dashed */
        if(tin.constraints.length){
          ctx.setLineDash([]);ctx.lineWidth=1.8;ctx.strokeStyle=sel?'#82c0ff':'#e0795a';ctx.beginPath();""",
    """        ctx.setLineDash([]);
        /* __acad3dV144: breaklines bold, the boundary dashed */
        if(tin.constraints.length){
          ctx.setLineDash([]);ctx.lineWidth=o.grading?0.9:1.8;ctx.strokeStyle=sel?'#82c0ff':o.grading?'#9ccc65':'#e0795a';ctx.beginPath();""")
rep("""        drawn.push({id:o.id,step:step,levels:cs.map(function(x){return x.level;}),segments:nseg,triangles:tin.tris.length,""",
    """        var arrows=o.arrows?bimDrawSlopeArrows(ctx,tin,V,W,H,sel):null;   /* __acad3dV145 */
        drawn.push({id:o.id,step:step,levels:cs.map(function(x){return x.level;}),segments:nseg,triangles:tin.tris.length,arrows:arrows,grading:!!o.grading,dashed:sup,""")
rep("""    if(legendFor){try{A3D.lastTerrainLegend=""", """    try{A3D.lastSpotsDrawn=bimDrawSpots(ctx,V,W,H);}catch(eS){console.warn('[BIM] spot elevations',eS);}   /* __acad3dV145 */
    if(legendFor){try{A3D.lastTerrainLegend=""")

# ---- Analyze ----
rep("""    if(tv){try{var tvb=bimTerrainBands(bimTerrainTin(tv),tv.tview),""", """    if(tv){try{var tvb=bimBandsOf(tv,tv.tview),""")
rep("""        {act:'terrain:landxml',label:'Export LandXML',off:TT.length?'':'No terrain yet'}]});""",
    """        {act:'terrain:landxml',label:'Export LandXML',off:TT.length?'':'No terrain yet'}]});
    /* __acad3dV145: grading */
    var GP=A3D.objs.filter(bimIsPad),GS=A3D.objs.filter(function(o){return o.t==='terrain'&&o.grading;}),gs0=GS[0],gv=gs0&&gs0.grading.volume,gst=gs0&&bimGradeStale(gs0);
    C.push({id:'grading',title:'Grading: Cut and Fill',state:gs0?(gst?'stale':'on'):(GP.length?'off':null),
      status:gs0?gs0.name+(gv?': cut '+bimDispNum(gv.cut,1)+' m³, fill '+bimDispNum(gv.fill,1)+' m³, net '+(gv.net>=0?bimDispNum(gv.net,1)+' m³ to take away':bimDispNum(-gv.net,1)+' m³ to bring in'):'')+
        (gst?' (the pads or the ground have changed since)':''):
        (GP.length?GP.length+' pad'+(GP.length===1?'':'s')+' ready: Grade runs their slopes out to the ground':'No pads yet: give a closed outline a Pad Elevation'),
      acts:[{act:'grade:run',label:gs0?'Grade Again':'Grade',pri:true,off:GP.length?'':'No pads yet'},{act:'grade:map',label:'Cut and Fill Map',off:gs0?'':'Grade first'},
        {act:'grade:arrows',label:'Slope Arrows',off:TT.length?'':'No terrain yet'}]});""")
rep("""    else if(k==='terrain:landxml')bimLandXmlExport(null);   /* __acad3dV144 */""",
    """    else if(k==='terrain:landxml')bimLandXmlExport(null);   /* __acad3dV144 */
    else if(k==='grade:run')bimGradeCommand();   /* __acad3dV145 */
    else if(k==='grade:map')bimCutFillMapCommand();
    else if(k==='grade:arrows')bimSlopeArrowsCommand();""")

# ---- commands ----
rep("""    ['BREAKLINE',['BRK','BREAKLINES'],""", """    ['GRADE',['GRADING','DAYLIGHT','GRADEPADS'],'grade','Grade the pads onto the ground: cut and fill slopes run out to the daylight line, into a proposed surface'],   /* __acad3dV145 */
    ['CUTFILL',['VOLUMES','TINVOLUME','SURFACEVOLUME'],'cutfill','Cut and fill between two surfaces (the existing one first), or of every proposed surface against its existing one'],
    ['CUTFILLMAP',['CUTFILLCOLOUR','CUTFILLCOLOR'],'cutfillmap','Colour the proposed surface by how deep it cuts or fills'],
    ['SPOTELEV',['SPOT','SPOTELEVATION','SPOTHEIGHT'],'spotelev','Label the selected points with the height of the surface under them'],
    ['SLOPEARROWS',['ARROWS','FLOWARROWS'],'slopearrows','Show or hide arrows down the slope of the terrain, with its percentage'],
    ['BREAKLINE',['BRK','BREAKLINES'],""")
rep("""    breakline:function(){bimBreaklineCommand();},      /* __acad3dV144 */""", """    breakline:function(){bimBreaklineCommand();},      /* __acad3dV144 */
    grade:function(){bimGradeCommand();},              /* __acad3dV145 */
    cutfill:function(){bimCutFillCommand();},
    cutfillmap:function(){bimCutFillMapCommand();},
    spotelev:function(){bimSpotCommand();},
    slopearrows:function(){bimSlopeArrowsCommand();},""")
rep("""    BREAKLINE:'breakline terrain tin ridge ditch kerb curb edge constraint surface',   /* __acad3dV144 */""",
    """    BREAKLINE:'breakline terrain tin ridge ditch kerb curb edge constraint surface',   /* __acad3dV144 */
    GRADE:'grading pad daylight slope cut fill embankment batter earthwork proposed surface site',   /* __acad3dV145 */
    CUTFILL:'cut fill volume earthwork quantities excavation embankment surface comparison tin',
    CUTFILLMAP:'cut fill map depth colour earthwork heat',
    SPOTELEV:'spot elevation height level label point grade',
    SLOPEARROWS:'slope arrows drainage direction fall flow percent grade',""")

# ---- hooks ----
rep("""  window.__a3dTerrainBands=function(id,mode){var o=objById(id);if(!o||o.t!=='terrain')return null;var b=bimTerrainBands(bimTerrainTin(o),mode);""",
    """  window.__a3dTerrainBands=function(id,mode){var o=objById(id);if(!o||o.t!=='terrain')return null;var b=bimBandsOf(o,mode);   /* __acad3dV145: and cutfill */""")
rep("""  window.__a3dTerrainLegend=function(){""", """  window.__a3dGrade=function(padIds,terId){   /* __acad3dV145 */
    var pads=(padIds||[]).map(objById).filter(bimIsPad);if(!pads.length)pads=A3D.objs.filter(bimIsPad);
    var ter=bimGradeExistingFor(pads,terId?objById(terId):null);if(!ter)return {error:'no existing surface under the pads'};
    return JSON.parse(JSON.stringify(bimGrade(pads,ter)));
  };
  window.__a3dGradeInfo=function(id){var o=objById(id);return o&&o.grading?{grading:JSON.parse(JSON.stringify(o.grading)),stale:bimGradeStale(o),name:o.name}:null;};
  window.__a3dGradeSpokes=function(padId,terId){
    var pad=objById(padId),ter=objById(terId);if(!bimIsPad(pad)||!ter)return null;var r=bimGradePad(pad,bimTinIndexOf(ter));if(r.error)return r;
    return {P:r.P,Z:r.Z,slopes:r.slopes,ring:r.ring,spokes:r.spokes.map(function(s){return {p:s.p,u:s.u,k:s.k,valley:!!s.valley,corner:s.corner===undefined?null:s.corner,
      r:s.r.off?{off:true}:{t:s.r.t,end:s.r.end,h:s.r.h,kind:s.r.kind,dir:s.r.dir}};})};
  };
  window.__a3dTinVolume=function(a,b){var A=objById(a),B=objById(b);return A&&B?bimTinVolume(bimTerrainTin(A),bimTerrainTin(B)):null;};
  window.__a3dSetPadSlope=function(id,which,v){return bimSetPadSlope(objById(id),which,v);};
  window.__a3dSpotsShown=function(){return A3D.lastSpotsDrawn||null;};
  window.__a3dSpotElev=function(id){var o=objById(id);return bimIsPoint(o)?bimSpotElev(o):null;};
  window.__a3dTerrainLegend=function(){""")
rep("""  var BIM_APP_VERSION={v:'V144',date:'2026-10-04'};   /* __acad3dV144 */""", """  var BIM_APP_VERSION={v:'V145',date:'2026-10-04'};   /* __acad3dV145 */""")
rep("""  window.__acad3dV144='""", """  window.__acad3dV145='daylight,fans,valleys,proposedsurface,regrade,tinvolume,cutfillbands,cutfillmap,spotelevations,slopearrows,gradingcard,gradecommands';
  window.__acad3dV144='""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
