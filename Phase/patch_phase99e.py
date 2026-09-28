"""patch_phase99e.py -- __acad3dV99: what a region dependent follows is visible, and the old
"frozen snapshot" wording goes (law 1: no leftovers).

  * One function, bimFollowsText, says what an object follows. Room, hatch, floor, ceiling and
    roof all show it in Properties. The hatch row used to say it follows nothing because it was
    traced from the arrangement -- no longer true, so it now reads from the same function.
  * A room whose region is open says "(not enclosed)" on its plan label.
  * The V52 comment that documented multi-wall rooms as a frozen snapshot is rewritten.
  * Marker and test surface.
"""
import hashlib, pathlib

SRC = pathlib.Path('canvas_v10.html')
BASE = '3565f1096445313ff736b61ff15396e6b7c965a5591bab98a66834021d3d33bd'

txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'

EDITS = [
    ("""    }else if(o.t==='room'){
      dims+=bimPropText('Area (m\\u00b2)',bimDispNum(o.area,2));
      dims+=bimPropText('Perimeter Points',o.pts.length);""",
     """    }else if(o.t==='room'){
      dims+=bimPropText('Area (m\\u00b2)',bimDispNum(o.area,2));
      dims+=bimPropText('Perimeter Points',o.pts.length);
      dims+=bimPropText('Follows',bimFollowsText(o));   /* __acad3dV99 */"""),
    ("""      dims+=bimPropText('Follows',o.sourceId?(((objById(o.sourceId)||{}).name)||'(missing)'):
        'Nothing - traced from the arrangement, so there is no single source to follow');""",
     """      dims+=bimPropText('Follows',bimFollowsText(o));   /* __acad3dV99 */"""),
    ("""      if(o.bim.profile)dims+=bimPropText('Area (m\\u00b2)',bimDispNum(bimPolyArea(o.bim.profile),2));
    }else if(o.bim&&o.bim.type==='column'){""",
     """      if(o.bim.profile)dims+=bimPropText('Area (m\\u00b2)',bimDispNum(bimPolyArea(o.bim.profile),2));
      dims+=bimPropText('Follows',bimFollowsText(o));   /* __acad3dV99 */
    }else if(o.bim&&o.bim.type==='column'){"""),
    ("""      var line1=o.name,line2=o.area.toFixed(2)+' m\\u00b2';""",
     """      var line1=o.name,line2=o.area.toFixed(2)+' m\\u00b2'+
        ((bimIsRegionDep(o)&&o.region.open)?' (not enclosed)':'');   /* __acad3dV99 */"""),
    ("""     Only 'wall' and 'sketch' sourced rooms are live. A 'wallgroup'-sourced room (traced across
     several separate wall objects with no single source id) has no single node to depend on and
     was never reachable through the dependency graph in the first place -- bimGraphBuild only
     links a room when it has a real sourceId. That room stays a frozen snapshot, same as before
     this phase; a known, documented scope boundary, not an oversight. */""",
     """     __acad3dV99: a room traced from SEVERAL shapes is no longer a frozen snapshot. It is a
     region dependent (o.region), linked in the graph to every shape its trace walked, and
     re-traced from its seed through bimRegionBoundaryWorld -- see the V99 block below. */"""),
    ("""  /* World points into a dependent's own frame. */
  function bimToFrame(o,pts){""",
     """  /* __acad3dV99: what an object follows, in words, for Properties. One answer for every kind. */
  function bimFollowsText(o){
    if(!o)return '-';
    if(bimIsRegionDep(o)){
      var names=[],i,m,mem=o.region.members||[];
      for(i=0;i<mem.length;i++){m=objById(mem[i]);names.push(m?m.name:'(missing)');}
      return 'The region bounded by '+(names.length?names.join(', '):'nothing')+
        (o.region.open?' - NOT ENCLOSED, keeping its last shape':'');
    }
    var sid=bimGraphRoomSourceId(o);
    if(sid)return ((objById(sid)||{}).name)||'(missing)';
    return 'Nothing - it keeps its own shape';
  }
  /* World points into a dependent's own frame. */
  function bimToFrame(o,pts){"""),
    ("""  window.__acad3dV98='edgesource,annotpickfirst,annotallkinds,annotgrips,gridselect,gridgrips,griddrag,griddelete,gridprops';""",
     """  window.__acad3dV98='edgesource,annotpickfirst,annotallkinds,annotgrips,gridselect,gridgrips,griddrag,griddelete,gridprops';
  /* __acad3dV99: region dependents. */
  window.__a3dRegenerateRegions=bimRegenerateRegions;
  window.__a3dIsRegionDep=function(id){return bimIsRegionDep(objById(id));};
  window.__a3dRegionOf=function(id){var o=objById(id);return (o&&o.region)?JSON.parse(JSON.stringify(o.region)):null;};
  window.__a3dFollowsText=function(id){return bimFollowsText(objById(id));};
  window.__a3dApplyHatchAt=function(pt,y,opts){var o=bimApplyHatchAt(pt,y||0,opts||bimHatchDefaults());return o?o.id:null;};
  window.__acad3dV99='regiondependent,regiontrace,regiongraph,regionregen,regionopen,legacywallgroup,deletedsource,followstext';"""),
]

for old, new in EDITS:
    assert txt.count(old) == 1, 'anchor count %d for %r' % (txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)

SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
