"""patch_phase99c.py -- __acad3dV99: every tool that traces a region records it.

The owner's direction: "room should not just be bounded by walls but the shape they are bounded
to." Room, Floor, Ceiling and Roof picked a single closed sketch or wall first and fell back to
tracing WALLS only. They now trace the region under the click from every shape on the plan --
walls, sketches and construction lines -- and keep the single-source path only when the region
really is one closed shape and nothing else. A region-traced result carries its seed, plane and
members, so it follows those shapes afterwards. The hatch pick records the same.
"""
import hashlib, pathlib

SRC = pathlib.Path('canvas_v10.html')
BASE = '856cd62bfd197bb48b3bfc09b57b73a106e053ab09113a872cef9b383c63088e'

txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'

EDITS = [
    ("""    if(candidates.length){
      candidates.sort(function(a,b){return bimPolyArea(a.pts)-bimPolyArea(b.pts);});
      return candidates[0];
    }
    var face=bimFindEnclosingWallFace(pt,y0);
    if(face){
      var wh=0,j;
      for(j=0;j<A3D.objs.length;j++){
        var wo=A3D.objs[j];
        if(wo.t==='solid'&&wo.bim&&wo.bim.type==='wall'&&wo.bim.height&&Math.abs(wo.bim.baseY-y0)<=0.5){wh=wo.bim.height;break;}
      }
      return {pts:face.pts,y:y0,sourceType:'wallgroup',sourceId:null,wallHeight:wh};
    }
    return null;
  }""",
     """    if(candidates.length)candidates.sort(function(a,b){return bimPolyArea(a.pts)-bimPolyArea(b.pts);});
    /* __acad3dV99: the region under the click, from EVERY shape on the plan. A single closed
       source still wins when the region is that shape and nothing else -- it then follows that
       one object exactly as it did in V97 (a closed wall keeps its inner face). */
    var reg;
    try{reg=bimRegionTraceAt(pt,y0,BIM_REGION_WANT.all);}
    catch(eRg){console.warn('[BIM] Region trace for a room failed',eRg);reg={error:'trace failed'};}
    if(candidates.length&&(reg.error||(reg.srcIds.length===1&&reg.srcIds[0]===candidates[0].sourceId)))
      return candidates[0];
    if(!reg.error){
      var wh=0,j,wo,allW=reg.srcIds.length>0;
      for(j=0;j<reg.srcIds.length;j++){
        wo=objById(reg.srcIds[j]);
        if(wo&&wo.t==='solid'&&wo.bim&&wo.bim.type==='wall'){if(!wh&&wo.bim.height)wh=wo.bim.height;}
        else allW=false;
      }
      return {pts:reg.ring,y:y0,sourceType:allW?'wallgroup':'region',sourceId:null,wallHeight:wh,
              rawPts:reg.pts,bulges:reg.bulges,islands:reg.islands,
              region:{seed:[pt[0],pt[1]],y:y0,want:'all',members:reg.srcIds.slice(),sig:reg.sig,open:false}};
    }
    if(candidates.length)return candidates[0];
    return null;
  }"""),
    ("""      sourceType:boundary.sourceType,sourceId:boundary.sourceId,layer:A3D.activeLayer};
    A3D.objs.push(o);""",
     """      sourceType:boundary.sourceType,sourceId:boundary.sourceId,layer:A3D.activeLayer};
    if(boundary.region)o.region=bimCloneRegion(boundary.region);   /* __acad3dV99 */
    A3D.objs.push(o);"""),
    ("""      openFloorDlg({pts:sketchCCW(flB.pts),y:flB.y,sourceType:flB.sourceType,sourceId:flB.sourceId});   /* __acad3dV97 */""",
     """      openFloorDlg({pts:sketchCCW(flB.pts),y:flB.y,sourceType:flB.sourceType,sourceId:flB.sourceId,
                    region:flB.region||null});   /* __acad3dV97, region __acad3dV99 */"""),
    ("""    if(prof.sourceId&&(prof.sourceType==='sketch'||prof.sourceType==='wall')){   /* __acad3dV97 */
      o.sourceId=prof.sourceId;o.sourceType=prof.sourceType;
    }""",
     """    if(prof.sourceId&&(prof.sourceType==='sketch'||prof.sourceType==='wall')){   /* __acad3dV97 */
      o.sourceId=prof.sourceId;o.sourceType=prof.sourceType;
    }else if(prof.region){   /* __acad3dV99 */
      o.region=bimCloneRegion(prof.region);o.sourceType=prof.sourceType;o.sourceId=null;
    }"""),
    ("""    if(boundary.sourceId&&(boundary.sourceType==='sketch'||boundary.sourceType==='wall')){   /* __acad3dV97 */
      o.sourceId=boundary.sourceId;o.sourceType=boundary.sourceType;
    }""",
     """    if(boundary.sourceId&&(boundary.sourceType==='sketch'||boundary.sourceType==='wall')){   /* __acad3dV97 */
      o.sourceId=boundary.sourceId;o.sourceType=boundary.sourceType;
    }else if(boundary.region){   /* __acad3dV99 */
      o.region=bimCloneRegion(boundary.region);o.sourceType=boundary.sourceType;o.sourceId=null;
    }"""),
    ("""    var o={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'solid',name:'Roof_'+A3D.counts.roof,col:'#a3766a',pos:[0,0,0],mesh:res.mesh,bim:res.bim,layer:A3D.activeLayer};
    A3D.objs.push(o);""",
     """    var o={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'solid',name:'Roof_'+A3D.counts.roof,col:'#a3766a',pos:[0,0,0],mesh:res.mesh,bim:res.bim,layer:A3D.activeLayer};
    if(boundary.region&&!boundary.sourceId){   /* __acad3dV99 */
      o.region=bimCloneRegion(boundary.region);o.sourceType=boundary.sourceType;o.sourceId=null;
    }
    A3D.objs.push(o);"""),
    ("""    pushUndo();
    var o=bimAddHatch(res.pts,res.bulges,y,opts);
    if(!o){a3dToast('Hatch: that region could not be filled');return null;}""",
     """    pushUndo();
    var o=bimAddHatch(res.pts,res.bulges,y,opts);
    if(!o){a3dToast('Hatch: that region could not be filled');return null;}
    /* __acad3dV99: an associative hatch -- it follows the shapes that bound it */
    o.region={seed:[pt[0],pt[1]],y:y,want:'all',members:(res.srcIds||[]).slice(),
              sig:bimEdgesSig(edges),open:false};
    o.sourceType='region';o.sourceId=null;"""),
]

for old, new in EDITS:
    assert txt.count(old) == 1, 'anchor count %d for %r' % (txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)

SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
