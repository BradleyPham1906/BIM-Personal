"""patch_phase96c.py -- __acad3dV96: HATCH and HATCHEDIT, reachable.

HATCH has had a registry row since the Canvas era -- ['HATCH',['H','BH'],'hatch',...] -- and no
BIM_CMD_MAP entry, so in the BIM workspace the V86 palette filter has been correctly hiding it
and typing H has done nothing. The row pointed at the retired whiteboard's hatch, which works on
state.wires and cannot see A3D.objs at all.

Two ways in, because both are one line of code given what V95 built:

  - a closed sketch or room is SELECTED   -> hatch that boundary directly;
  - nothing useful is selected            -> pick internal points, one hatch per click, with
                                             bimTraceBoundary finding the region.

The pattern list in the dialog is DERIVED from BIM_HATCH_PATTERNS and bimPatternLabel, so it
cannot offer a pattern the renderer does not know, and it cannot miss one that is added later.

GRADIENT is deliberately absent. There is no gradient renderer in this build, and a command that
opens a dialog and produces nothing is the decorative control Product Principle 1 forbids.
"""
import hashlib, pathlib

SRC = pathlib.Path('canvas_v10.html')
BASE = 'e4f6409d08af6892a670566a281bf3961bfcc969f8d97a6dc6636a39a8397af9'

txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'

EDITS = [
    ("""  var BIM_COORD_TOOLS={line:1,poly:1,wall:1,rect:1,stair:1,arc:1,circle:1,polygon:1,point:1,xline:1,boundary:1};""",
     """  var BIM_COORD_TOOLS={line:1,poly:1,wall:1,rect:1,stair:1,arc:1,circle:1,polygon:1,point:1,xline:1,boundary:1,hatch:1};"""),

    ("""polygon:'Polygon',point:'Point',xline:'Construction line',boundary:'Boundary',poly:'Polyline',""",
     """polygon:'Polygon',point:'Point',xline:'Construction line',boundary:'Boundary',hatch:'Hatch',poly:'Polyline',"""),

    ("""  /* __acad3dV95 */
  function startBoundaryTool(){""",
     """  /* __acad3dV96: what is selected that could be hatched directly. A closed sketch and a room
     are both already a closed ring; anything else means "pick a point instead". */
  function bimHatchableSelection(){
    var o=A3D.sel?objById(A3D.sel):null;
    if(!o)return null;
    if(o.t==='sketch'&&!bimIsPoint(o)&&o.closed!==false&&o.pts&&o.pts.length>=2)
      return {pts:o.pts,bulges:o.bulges||null,y:o.y,from:o.name};
    if(o.t==='room'&&o.pts&&o.pts.length>=3)
      return {pts:o.pts,bulges:null,y:o.y,from:o.name};
    return null;
  }
  function bimHatchDefaults(){
    var o=A3D.sel?objById(A3D.sel):null;
    if(bimIsHatch(o))
      return {pattern:o.pattern,patternScale:o.patternScale,patternAngle:o.patternAngle,
              patternColor:o.patternColor};
    return {pattern:(A3D.lastHatch&&A3D.lastHatch.pattern)||'diagonal',
            patternScale:(A3D.lastHatch&&A3D.lastHatch.patternScale)||1,
            patternAngle:(A3D.lastHatch&&A3D.lastHatch.patternAngle)||0,
            patternColor:(A3D.lastHatch&&A3D.lastHatch.patternColor)||'#555555'};
  }
  function bimHatchPatternOptions(sel){
    /* Derived from the renderer's own list, so the dialog cannot offer a pattern nothing draws
       and cannot miss one added later. 'none' is left out: a hatch with no pattern is not a
       hatch, it is a deletion. */
    var out='',i,n;
    for(i=0;i<BIM_HATCH_PATTERNS.length;i++){
      n=BIM_HATCH_PATTERNS[i];
      if(n==='none')continue;
      out+='<option value="'+n+'"'+(n===sel?' selected':'')+'>'+bimEsc(bimPatternLabel(n))+'</option>';
    }
    return out;
  }
  function bimOpenHatchDlg(mode){
    var editing=(mode==='edit');
    var target=editing?objById(A3D.sel):null;
    if(editing&&!bimIsHatch(target)){a3dToast('Hatchedit: select a hatch first');return;}
    var d0=bimHatchDefaults(),selObj=editing?null:bimHatchableSelection();
    closeDlg();
    var d=document.createElement('div');
    d.className='a3d-dlg';
    d.innerHTML='<div class="a3d-dlghd">'+(editing?'Hatch edit':'Hatch')+'</div><div class="a3d-dlgbody">'+
      '<div class="a3d-dlgrow"><label>Pattern</label><select data-a3dp="pat">'+
      bimHatchPatternOptions(d0.pattern)+'</select></div>'+
      '<div class="a3d-dlgrow"><label>Angle (deg)</label><input type="number" step="any" data-a3dp="ang" value="'+(d0.patternAngle||0)+'"></div>'+
      '<div class="a3d-dlgrow"><label>Scale</label><input type="number" step="any" min="0.1" max="8" data-a3dp="sc" value="'+(d0.patternScale||1)+'"></div>'+
      '<div class="a3d-propnote">'+
      (editing?('Changing '+bimEsc(target.name)+'.')
             :(selObj?('Filling '+bimEsc(selObj.from)+' directly.')
                     :'Nothing closed is selected, so you will pick internal points; each click hatches the region around it.'))+
      '</div><div id="a3d-dlgerr" class="a3d-dlgerr"></div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="ok">OK</button></div>';
    el.root.appendChild(d);el.dlg=d;
    function submit(){
      var pat=d.querySelector('[data-a3dp="pat"]').value;
      var ang=parseFloat(d.querySelector('[data-a3dp="ang"]').value);
      var sc=parseFloat(d.querySelector('[data-a3dp="sc"]').value);
      var eb=document.getElementById('a3d-dlgerr');
      if(!isFinite(ang)){eb.textContent='Angle must be a number of degrees';return;}
      if(!isFinite(sc)||sc<0.1||sc>8){eb.textContent='Scale must be between 0.1 and 8';return;}
      if(!bimPatternDraws(pat)){eb.textContent='That pattern has nothing to draw';return;}
      var opts={pattern:pat,patternAngle:ang,patternScale:sc,patternColor:d0.patternColor};
      A3D.lastHatch=opts;
      closeDlg();
      if(editing){bimApplyHatchEdit(target.id,opts);return;}
      if(selObj){
        pushUndo();
        var ho=bimAddHatch(selObj.pts,selObj.bulges,selObj.y,opts);
        if(!ho){a3dToast('Hatch: that boundary could not be used');return;}
        A3D.sel=ho.id;A3D.sel2=null;
        refreshTree();refreshHud();paint();saveSoon();
        a3dToast(ho.name+' created on '+selObj.from+', area '+bimHatchArea(ho).toFixed(3)+' m2');
        return;
      }
      startHatchTool(opts);
    }
    d.addEventListener('click',function(ev){var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;if(!b)return;if(b.getAttribute('data-a3dlg')==='ok')submit();else closeDlg();});
    d.addEventListener('keydown',function(ev){if(ev.key==='Enter'){ev.preventDefault();ev.stopPropagation();submit();}else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();}});
  }
  function bimApplyHatchEdit(id,opts){
    var o=objById(id);
    if(!bimIsHatch(o)){a3dToast('Hatchedit: select a hatch first');return null;}
    pushUndo();
    o.pattern=opts.pattern;
    o.patternAngle=((opts.patternAngle%180)+180)%180;
    o.patternScale=Math.max(0.1,Math.min(8,opts.patternScale));
    if(opts.patternColor)o.patternColor=opts.patternColor;
    refreshTree();refreshProps();paint();saveSoon();
    a3dToast(o.name+': '+bimPatternLabel(o.pattern)+' at '+o.patternAngle.toFixed(1)+
      ' deg, scale '+o.patternScale.toFixed(2));
    return o;
  }
  function startHatchTool(opts){
    bimEnterDraftingMode();
    var lvl=bimGetActiveLevel();
    A3D.sk={tool:'hatch',pts:[],y:lvl.elev,on:null,hatch:opts||bimHatchDefaults()};
    bimSyncStatusHint();
    paint();
    a3dToast('Hatch: click inside a region to fill it; Escape when finished');
  }
  function bimApplyHatchAt(pt,y,opts){
    var edges=bimBoundaryEdges(y,{walls:true,sketches:true,clines:true});
    if(!edges.length){a3dToast('Hatch: there is nothing on this plan to bound a region');return null;}
    var res=bimTraceBoundary(edges,pt);
    if(res.error){a3dToast('Hatch: '+res.error);return null;}
    pushUndo();
    var o=bimAddHatch(res.pts,res.bulges,y,opts);
    if(!o){a3dToast('Hatch: that region could not be filled');return null;}
    A3D.sel=o.id;A3D.sel2=null;
    refreshTree();refreshHud();paint();saveSoon();
    var msg=o.name+' created, area '+bimHatchArea(o).toFixed(3)+' m2';
    if(res.islands)
      msg+=' - NOTE: this region has something inside it, and the hatch has no hole, so it '+
           'covers the island too';
    a3dToast(msg);
    return o;
  }
  /* __acad3dV95 */
  function startBoundaryTool(){"""),

    ("""    if(sk.tool==='boundary'){                   /* __acad3dV95 */""",
     """    if(sk.tool==='hatch'){                      /* __acad3dV96 */
      bimApplyHatchAt([gx,gz],sk.y,sk.hatch);
      return;                                   /* sk stays live: HATCH keeps filling */
    }
    if(sk.tool==='boundary'){                   /* __acad3dV95 */"""),

    ("""    if(sk.tool==='boundary')return 'Pick an internal point (Escape when finished):';  /* __acad3dV95 */""",
     """    if(sk.tool==='hatch')return 'Pick an internal point to hatch (Escape when finished):'; /* __acad3dV96 */
    if(sk.tool==='boundary')return 'Pick an internal point (Escape when finished):';  /* __acad3dV95 */"""),

    ("""    ['BOUNDARY',['BO','BPOLY'],'boundary','Trace the closed region around a picked point'],""",
     """    ['HATCHEDIT',['HE'],'hatchedit','Change a hatch pattern, angle or scale'],
    ['BOUNDARY',['BO','BPOLY'],'boundary','Trace the closed region around a picked point'],"""),

    ("""    boundary:function(){startBoundaryTool();},/* __acad3dV95 */""",
     """    hatch:function(){bimOpenHatchDlg('new');},     /* __acad3dV96 */
    hatchedit:function(){bimOpenHatchDlg('edit');},/* __acad3dV96 */
    boundary:function(){startBoundaryTool();},/* __acad3dV95 */"""),

    ("""  /* __acad3dV95 */
  window.__a3dBulgedSignedArea=bimBulgedSignedArea;""",
     """  /* __acad3dV96 */
  window.__a3dPatternRotation=bimPatternRotation;
  window.__a3dPatternSvgDef=bimPatternSvgDef;
  window.__a3dIsHatch=function(id){return bimIsHatch(objById(id));};
  window.__a3dHatchGraphics=function(id){var o=objById(id);return o?bimHatchGraphics(o):null;};
  window.__a3dHatchArea=function(id){var o=objById(id);return o?bimHatchArea(o):null;};
  window.__a3dAddHatch=function(pts,bulges,y,opts){
    var o=bimAddHatch(pts,bulges,y,opts);
    if(o){refreshTree();paint();}
    return o?o.id:null;
  };
  window.__a3dApplyHatchAt=function(pt,y,opts){
    var o=bimApplyHatchAt(pt,y,opts||bimHatchDefaults());
    return o?o.id:null;
  };
  window.__a3dApplyHatchEdit=function(id,opts){
    var o=bimApplyHatchEdit(id,opts);
    return o?o.id:null;
  };
  window.__a3dHatchPatternNames=function(){
    return BIM_HATCH_PATTERNS.filter(function(n){return n!=='none';});
  };
  window.__acad3dV96='hatchobject,patternangle,onegraphicsfieldvalidator,materialangleheeded,hatchcommand,hatchedit,bothmodes';
  /* __acad3dV95 */
  window.__a3dBulgedSignedArea=bimBulgedSignedArea;"""),
]

for old, new in EDITS:
    assert txt.count(old) == 1, 'anchor count %d for %r' % (txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)

SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
