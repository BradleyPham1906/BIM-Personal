"""patch_phase87d.py -- Phase 87 part 4: wiring.

Command registry rows, the BIM command table, the ribbon buttons, the test hooks and the marker.
Nothing here computes geometry; it is the layer that makes Phase 87 reachable.
"""
import hashlib, pathlib, sys

BASE = 'fc1b2cfdac848f88f0bd552e39b29f487533c24f0bd008a3a17dccd85a45f7e1'
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')

src = P.read_text(encoding='utf-8')
h0 = hashlib.sha256(src.encode('utf-8')).hexdigest()
assert h0 == BASE, 'baseline hash mismatch: %s' % h0
b0 = len(src.encode('utf-8'))

reps = []

# ---- 1. registry rows. The palette pool() filters by __a3dCmdSupported, so a row only appears
#         once its act exists in the BIM table -- which is why ROTATE and SCALE have to stop
#         pointing at the retired whiteboard's rot90/scaleUp before they can ever be offered.
OLD_ROWS = """    ['CHAMFER',['CHA'],'chamfer','Chamfer two lines'],['EXPLODE',['X'],'explode','Explode into segments'],
    ['MOVE',['M'],'moveTool','Move selection'],['COPY',['CO','CP'],'duplicate','Copy selection'],
    ['ROTATE',['RO'],'rot90','Rotate 90 CW'],['ROTATECCW',['RCC'],'rotCCW','Rotate 90 CCW'],
    ['ROTATE0',['RZ'],'rot0','Reset rotation'],['SCALE',['SC','SCU'],'scaleUp','Scale to 125%'],"""
NEW_ROWS = """    ['CHAMFER',['CHA'],'chamfer','Chamfer a corner between two walls'],['EXPLODE',['X'],'explode','Explode into segments'],
    ['MOVE',['M'],'moveTool','Move selection'],['COPY',['CO','CP'],'duplicate','Copy selection'],
    ['BREAK',['BR'],'break','Break a wall between two points'],
    ['BREAKATPOINT',['BRP','BREAKAT'],'breakat','Split a wall at one point'],
    ['LENGTHEN',['LEN'],'lengthen','Change a wall length at one end'],
    ['JOIN',['J'],'join','Join two colinear walls into one'],
    ['ALIGN',['AL'],'align','Align objects to the first selected'],
    ['ARRAYRECT',['AR','ARRAY','ARRAYCLASSIC'],'arrayRect','Rectangular array'],
    ['ARRAYPOLAR',['ARP'],'arrayPolar','Polar array'],
    ['ROTATE',['RO'],'rotate','Rotate about a base point'],['ROTATECCW',['RCC'],'rotCCW','Rotate 90 CCW'],
    ['ROTATE0',['RZ'],'rot0','Reset rotation'],['SCALE',['SC','SCU'],'scale','Scale about a base point'],"""
reps.append((OLD_ROWS, NEW_ROWS, 1))

OLD_FILLET = """['FILLET',['F'],'fillet','Fillet two lines'],"""
NEW_FILLET = """['FILLET',['F'],'fillet','Fillet two walls (radius 0)'],"""
reps.append((OLD_FILLET, NEW_FILLET, 1))

# ---- 2. the BIM command table -----------------------------------------------------------
OLD_MAP = """    trim:function(){startTrimTool();},
    mirror:function(){startMirrorTool();},"""
NEW_MAP = """    trim:function(){startTrimTool();},
    /* __acad3dV87. Three of these -- rotate, arrayRect, arrayPolar -- are not new work: the
       tools existed and ran from the ribbon, and the command line simply could not reach them
       because their registry rows still pointed at the retired whiteboard's acts. A working
       tool that no command can start is the same leftover as a control that no longer does
       anything, so they are wired here rather than left for a later phase to rediscover. */
    extend:function(){startExtendTool();},
    'break':function(){startBreakTool(false);},
    breakat:function(){startBreakTool(true);},
    lengthen:function(){startLengthenTool();},
    chamfer:function(){startChamferTool();},
    fillet:function(){applyFilletCorner();},
    scale:function(){startScaleTool();},
    rotate:function(){startRotateTool();},
    arrayRect:function(){openArrayDlg();},
    arrayPolar:function(){startPolarArrayTool();},
    align:function(){openAlignDlg();},
    join:function(){applyMergeWalls();},
    mirror:function(){startMirrorTool();},"""
reps.append((OLD_MAP, NEW_MAP, 1))

# ---- 3. ribbon icons ---------------------------------------------------------------------
OLD_IC = """    'bim:joinwalls':ric('<path d="M4 4v9a7 7 0 0 0 7 7h9"/><path d="M14 17l6 3M20 20l-3-6"/>'),"""
NEW_IC = """    'bim:joinwalls':ric('<path d="M4 4v9a7 7 0 0 0 7 7h9"/><path d="M14 17l6 3M20 20l-3-6"/>'),
    'bim:extend':ric('<path d="M3 12h11"/><path d="M11 8l4 4-4 4"/><path d="M19 4v16"/>'),
    'bim:fillet':ric('<path d="M4 20V10a6 6 0 0 1 6-6h10"/>'),
    'bim:chamfer':ric('<path d="M4 20v-8l8-8h8"/>'),
    'bim:break':ric('<path d="M3 12h6M15 12h6"/><path d="M11 7l-2 10M13 7l-2 10"/>'),
    'bim:lengthen':ric('<path d="M3 12h14"/><path d="M13 8l4 4-4 4"/><path d="M3 7v10"/>'),
    'bim:scale':ric('<rect x="3" y="12" width="9" height="9"/><path d="M12 12L21 3"/><path d="M15 3h6v6"/>'),"""
reps.append((OLD_IC, NEW_IC, 1))

# ---- 4. ribbon labels ---------------------------------------------------------------------
OLD_LBL = """'bim:joinwalls':'Join Walls',"""
NEW_LBL = """'bim:joinwalls':'Join Walls','bim:extend':'Extend','bim:fillet':'Fillet','bim:chamfer':'Chamfer','bim:break':'Break','bim:lengthen':'Lengthen','bim:scale':'Scale',"""
reps.append((OLD_LBL, NEW_LBL, 1))

# ---- 5. ribbon dispatch -------------------------------------------------------------------
OLD_DISP = """    if(act==='bim:joinwalls'){applyWallJoin();return;}"""
NEW_DISP = """    if(act==='bim:joinwalls'){applyWallJoin();return;}
    if(act==='bim:extend'){startExtendTool();return;}
    if(act==='bim:fillet'){applyFilletCorner();return;}
    if(act==='bim:chamfer'){startChamferTool();return;}
    if(act==='bim:break'){startBreakTool(false);return;}
    if(act==='bim:lengthen'){startLengthenTool();return;}
    if(act==='bim:scale'){startScaleTool();return;}"""
reps.append((OLD_DISP, NEW_DISP, 1))

# ---- 6. the two Modify panels -------------------------------------------------------------
OLD_G1 = """      {t:'Modify',small:['bim:trim','bim:offset','bim:align','bim:mirror','bim:rotate','m:array','bim:polararray','m:dup','m:del']},"""
NEW_G1 = """      {t:'Modify',small:['bim:trim','bim:extend','bim:fillet','bim:chamfer','bim:break','bim:lengthen','bim:scale','bim:offset','bim:align','bim:mirror','bim:rotate','m:array','bim:polararray','m:dup','m:del']},"""
reps.append((OLD_G1, NEW_G1, 1))

OLD_G2 = """      ],small:['m:array','bim:polararray','bim:joinwalls','bim:mergewalls','m:del','m:desel','bim:trim','bim:offset','bim:align','bim:clonelinked','bim:syncclones']},"""
NEW_G2 = """      ],small:['m:array','bim:polararray','bim:joinwalls','bim:mergewalls','m:del','m:desel','bim:trim','bim:extend','bim:fillet','bim:chamfer','bim:break','bim:lengthen','bim:scale','bim:offset','bim:align','bim:clonelinked','bim:syncclones']},"""
reps.append((OLD_G2, NEW_G2, 1))

# ---- 7. test hooks and the marker ---------------------------------------------------------
OLD_HOOK = """  window.__acad3dV86='palettewired,linetool,autocadcoords,autocadprompts,closeundo,repeatlast';"""
NEW_HOOK = """  /* __acad3dV87: the geometry core is exposed directly so the suite asserts on the POINTS a
     modify command produces, not on the picture drawn from them. */
  window.__a3dExtendPolyline=bimExtendPolyline;
  window.__a3dBreakPolyline=bimBreakPolyline;
  window.__a3dLengthenPolyline=bimLengthenPolyline;
  window.__a3dChamferPolylines=bimChamferPolylines;
  window.__a3dScalePoint=bimScalePoint;
  window.__a3dPolyLength=bimPolyLength;
  window.__a3dProjectOntoPolyline=bimProjectOntoPolyline;
  window.__a3dPlacePoint=function(gx,gz){skPlacePoint(gx,gz,null);};
  window.__a3dApplyExtend=bimApplyExtend;
  window.__a3dApplyBreak=bimApplyBreak;
  window.__a3dApplyLengthen=bimApplyLengthen;
  window.__a3dApplyChamfer=bimApplyChamfer;
  window.__a3dScaleSelection=bimScaleSelection;
  window.__a3dTypedPoint=bimCommitTypedPoint;
  window.__acad3dV87='extend,break,breakatpoint,lengthen,chamfer,scale,typedpointroutedthroughplace,filletradius0,rotateandarraycommandsreachable';
  window.__acad3dV86='palettewired,linetool,autocadcoords,autocadprompts,closeundo,repeatlast';"""
reps.append((OLD_HOOK, NEW_HOOK, 1))

out = src
for old, new, want in reps:
    got = out.count(old)
    assert got == want, 'occurrence count %d (wanted %d) for: %s' % (got, want, old[:70])
    out = out.replace(old, new, want)

assert out != src
b1 = len(out.encode('utf-8'))
P.write_text(out, encoding='utf-8')
print('%d replacements' % len(reps))
print('bytes before %d  after %d  (+%d)' % (b0, b1, b1 - b0))
print('sha256 %s' % hashlib.sha256(out.encode('utf-8')).hexdigest())
