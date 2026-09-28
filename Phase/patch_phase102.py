"""patch_phase102.py -- __acad3dV102: a structural catalogue -- beam and footing types.

First phase of the structural track. The type system (V38-V40) already gives walls, floors,
ceilings and columns named types that instances reference, an Edit Type dialog, and "change the
type, every instance rebuilds". Beams had no types at all, and there were no footings.

Added as TYPE_CATS categories, so every piece of existing type machinery serves them unchanged:
  beam          Concrete Beam      width x depth       250x450 300x500 300x600 400x700
  footing       Isolated Footing   width x length x thickness   1200 / 1500 / 2000 square
  stripfooting  Wall Foundation    width x thickness   600x300 800x400 1000x450
The column catalogue gains 500x500, 600x600 and 300x600 for new projects (a saved project keeps
the types it has).

Properties now shows a Type selector for EVERY typed category, not only walls -- selecting a type
rebuilds the instance through the same path the Edit Type dialog uses.
"""
import hashlib, pathlib
SRC = pathlib.Path('canvas_v10.html')
BASE = '78dcde05a1f7b4921e62fe9b1d83b305277441c5fa2dcca0fb928b4d180b83ce'
txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'
EDITS = [
    ("""    {id:'ct-200x400',name:'200 x 400mm',params:{width:0.2,depth:0.4,material:'Concrete'}}
  ];
  var TYPE_CATS={""",
     """    {id:'ct-200x400',name:'200 x 400mm',params:{width:0.2,depth:0.4,material:'Concrete'}},
    {id:'ct-500',name:'500 x 500mm',params:{width:0.5,depth:0.5,material:'Concrete'}},        /* __acad3dV102 */
    {id:'ct-600',name:'600 x 600mm',params:{width:0.6,depth:0.6,material:'Concrete'}},
    {id:'ct-300x600',name:'300 x 600mm',params:{width:0.3,depth:0.6,material:'Concrete'}}
  ];
  /* __acad3dV102: the structural catalogue */
  var BEAM_TYPE_DEFAULTS=[
    {id:'bt-250x450',name:'250 x 450mm',params:{width:0.25,depth:0.45,material:'Concrete'}},
    {id:'bt-300x500',name:'300 x 500mm',params:{width:0.3,depth:0.5,material:'Concrete'}},
    {id:'bt-300x600',name:'300 x 600mm',params:{width:0.3,depth:0.6,material:'Concrete'}},
    {id:'bt-400x700',name:'400 x 700mm',params:{width:0.4,depth:0.7,material:'Concrete'}}
  ];
  var FOOTING_TYPE_DEFAULTS=[
    {id:'ft-iso1200',name:'1200 x 1200 x 400mm',params:{width:1.2,length:1.2,thickness:0.4,material:'Concrete'}},
    {id:'ft-iso1500',name:'1500 x 1500 x 500mm',params:{width:1.5,length:1.5,thickness:0.5,material:'Concrete'}},
    {id:'ft-iso2000',name:'2000 x 2000 x 600mm',params:{width:2.0,length:2.0,thickness:0.6,material:'Concrete'}}
  ];
  var STRIP_TYPE_DEFAULTS=[
    {id:'sf-600x300',name:'600 x 300mm',params:{width:0.6,thickness:0.3,material:'Concrete'}},
    {id:'sf-800x400',name:'800 x 400mm',params:{width:0.8,thickness:0.4,material:'Concrete'}},
    {id:'sf-1000x450',name:'1000 x 450mm',params:{width:1.0,thickness:0.45,material:'Concrete'}}
  ];
  var TYPE_CATS={"""),
    ("""    column: {label:'Columns',  family:'Rectangular Column', defaults:COL_TYPE_DEFAULTS,   typeParams:['width','depth']}
  };""",
     """    column: {label:'Columns',  family:'Rectangular Column', defaults:COL_TYPE_DEFAULTS,   typeParams:['width','depth']},
    beam:   {label:'Beams',    family:'Concrete Beam',      defaults:BEAM_TYPE_DEFAULTS,  typeParams:['width','depth']},        /* __acad3dV102 */
    footing:{label:'Isolated Footings',family:'Isolated Footing',defaults:FOOTING_TYPE_DEFAULTS,typeParams:['width','length','thickness']},
    stripfooting:{label:'Wall Foundations',family:'Wall Foundation',defaults:STRIP_TYPE_DEFAULTS,typeParams:['width','thickness']}
  };"""),
    ("""      o.mesh=r4.mesh;o.bim.width=t.params.width;o.bim.depth=t.params.depth;
      return true;
    }
    return false;
  }""",
     """      o.mesh=r4.mesh;o.bim.width=t.params.width;o.bim.depth=t.params.depth;
      bimAfterWallRebuild(o);   /* __acad3dV102: a footing under it follows */
      return true;
    }
    if(cat==='beam'){   /* __acad3dV102 */
      if(!o.bim.p1||!o.bim.p2)return false;
      var r5=bimBuildBeamGeometry(o.bim.p1,o.bim.p2,o.bim.topY,t.params.width,t.params.depth);
      if(r5.error)return false;
      o.mesh=r5.mesh;o.bim.width=t.params.width;o.bim.depth=t.params.depth;o.bim.baseY=r5.bim.baseY;
      return true;
    }
    if(cat==='footing'||cat==='stripfooting'){   /* __acad3dV102 */
      var k2;
      for(k2 in t.params)if(t.params.hasOwnProperty(k2)&&k2!=='material')o.bim[k2]=t.params[k2];
      return bimRebuildFooting(o);
    }
    return false;
  }"""),
    # generic Type selector in Properties
    ("""    cons+=bimPropText('Level',lvlName);""",
     """    /* __acad3dV102: a Type selector for every typed category (walls keep their own row above) */
    if(o.bim&&TYPE_CATS[o.bim.type]&&o.bim.type!=='wall'){
      bimEnsureTypes();
      var cur=bimEnsureObjType(o);
      cons+=bimPropRow('Type','<select data-propf="objtype">'+
        A3D.types[o.bim.type].map(function(x){return '<option value="'+x.id+'"'+(cur&&cur.id===x.id?' selected':'')+'>'+bimEsc(x.name)+'</option>';}).join('')+
        '</select>');
    }
    cons+=bimPropText('Level',lvlName);"""),
    ("""      }else if(f==='walltype'){
        bimSetWallTypeOf(o,inp.value);""",
     """      }else if(f==='walltype'){
        bimSetWallTypeOf(o,inp.value);
      }else if(f==='objtype'){   /* __acad3dV102 */
        if(!o.bim||!TYPE_CATS[o.bim.type]){a3dToast('This object has no type');return;}
        pushUndo();
        if(bimAssignTypeTo(o,o.bim.type,inp.value)){
          A3D.meshes={};refreshTree();paint();saveSoon();
          a3dToast(o.name+' is now '+(bimTypeNameOf(o)||'the selected type'));
        }else{
          a3dToast('That type could not be applied to '+o.name+' - see the console');
          console.warn('[BIM] Type change failed for '+o.name,inp.value);
        }"""),
]
for old, new in EDITS:
    assert txt.count(old) == 1, 'anchor count %d for %r' % (txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
