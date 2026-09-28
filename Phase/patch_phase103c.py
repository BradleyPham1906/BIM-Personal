"""patch_phase103c.py -- __acad3dV103: property Properties, setbacks, tools, exports, test surface.

  * Properties of a property: the point of beginning, every leg as the deed reads it, the closure
    (misclosure, precision, perimeter, area in m2 and ha), one setback field per side plus an
    "all sides" field, and the live list of setback violations.
  * Reached from a new Site panel on the Massing & Site tab (Property Line, Property from Shape,
    True North) and the command line (PROPERTYLINE / PROP, PROPERTYFROMSHAPE / PROPSH,
    TRUENORTH / TN, PROPERTYEDIT / PROPED).
  * Exported to DXF, SVG and the sheet as its closed line with each leg's bearing and distance.
"""
import hashlib, pathlib, re
SRC = pathlib.Path('canvas_v10.html')
BASE = '223672e64fca43ed722119183658bd38efadf65ef928c15418c79e92e58a41aa'
txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'

def js_ascii(v):
    return ''.join(c if ord(c) < 128 else '\\u%04x' % ord(c) for c in v)

EDITS = [
    ("""    }else if(bimIsFooting(o)){   /* __acad3dV102: sizes come from the type (Edit Type) */""",
     """    }else if(bimIsProperty(o)){   /* __acad3dV103: the survey, its closure, its setbacks */
      var pg=bimPropertyGeometry(o),li;
      dims+=bimPropText('Point of beginning',o.start[0].toFixed(3)+', '+o.start[1].toFixed(3));
      for(li=0;li<o.legs.length;li++)
        dims+=bimPropText('Leg '+(li+1),bimFormatBearing(o.legs[li].az)+'  '+o.legs[li].d.toFixed(3)+' m');
      dims+=bimPropText('Closure',pg.misclosure<0.0005?'Closes':('Misclosure '+pg.misclosure.toFixed(3)+' m (1:'+Math.round(pg.precision)+')'));
      dims+=bimPropText('Perimeter (m)',bimDispNum(pg.perimeter,3));
      dims+=bimPropText('Area (m²)',bimDispNum(pg.area,2));
      dims+=bimPropText('Area (ha)',bimDispNum(pg.area/10000,4));
      dims+=bimPropRow('Survey','<button class="a3d-pedit" data-propact="propedit">Edit legs...</button>');
      var sbr=bimPropRow('All sides (m)','<input type="number" step="any" min="0" data-propsetback="all" value="">');
      for(li=0;li<o.legs.length;li++)
        sbr+=bimPropRow('Side '+(li+1)+' (m)','<input type="number" step="any" min="0" data-propsetback="'+li+'" value="'+((o.setbacks&&o.setbacks[li])||0)+'">');
      if(pg.setback&&pg.setback.error)sbr+=bimPropText('Buildable area',pg.setback.error);
      else if(pg.setback)sbr+=bimPropText('Buildable area (m²)',bimDispNum(bimPolyArea(pg.setback.ring),2));
      var vio=bimSetbackViolations(o);
      sbr+=bimPropText('Violations',vio.list.length?vio.list.map(function(v){return v.name;}).join(', '):'None');
      h+=bimPropGroup('Setbacks',sbr);
    }else if(bimIsFooting(o)){   /* __acad3dV102: sizes come from the type (Edit Type) */"""),
    ("""    if(bimIsFooting(o))return 'Structural Foundations : '""",
     """    if(bimIsProperty(o))return 'Site : Property Line';   /* __acad3dV103 */
    if(bimIsFooting(o))return 'Structural Foundations : '"""),
    # setback and edit handlers
    ("""    /* __acad3dV101: a tag's own switch */""",
     """    /* __acad3dV103: setbacks, per side or all at once */
    if(el.propsbody)el.propsbody.addEventListener('change',function(ev){
      var si=ev.target&&ev.target.closest?ev.target.closest('[data-propsetback]'):null;
      if(!si)return;
      var po=objById(A3D.sel);
      if(!bimIsProperty(po))return;
      var sv=parseFloat(si.value);
      if(!isFinite(sv)||sv<0){a3dToast('A setback is a distance of 0 or more');refreshProps();return;}
      pushUndo();
      var sk_=si.getAttribute('data-propsetback'),k_;
      if(!po.setbacks||po.setbacks.length!==po.legs.length)po.setbacks=po.legs.map(function(){return 0;});
      if(sk_==='all'){for(k_=0;k_<po.setbacks.length;k_++)po.setbacks[k_]=sv;}
      else po.setbacks[parseInt(sk_,10)]=sv;
      refreshProps();paint();saveSoon();
      var sg=bimPropertyGeometry(po);
      if(sg.setback&&sg.setback.error)a3dToast(po.name+': '+sg.setback.error);
      else{var vv=bimSetbackViolations(po);if(vv.list.length)a3dToast(vv.list.length+' element(s) outside the setback: '+vv.list.map(function(v){return v.name;}).join(', '));}
    });
    if(el.propsbody)el.propsbody.addEventListener('click',function(ev){
      var pa=ev.target&&ev.target.closest?ev.target.closest('[data-propact="propedit"]'):null;
      if(!pa)return;
      var po=objById(A3D.sel);
      if(bimIsProperty(po))openPropertyDlg(po);
    });
    /* __acad3dV101: a tag's own switch */"""),
    # bounds
    ("""    else if(o.t==='text'||o.t==='roomtag')pts=[o.pt];   /* __acad3dV101 */""",
     """    else if(o.t==='text'||o.t==='roomtag')pts=[o.pt];   /* __acad3dV101 */
    else if(bimIsProperty(o)){   /* __acad3dV103: world points, so the offset below is taken off */
      var pq=bimObjOffset(o);
      pts=bimPropertyGeometry(o).ring.map(function(p){return [p[0]-pq[0],p[1]-pq[2]];});
    }"""),
    # ribbon
    ("""      {t:'Model by Face',small:['tube','prism','wedge','ellipsoid']}""",
     """      {t:'Model by Face',small:['tube','prism','wedge','ellipsoid']},
      {t:'Site',small:['bim:property','bim:propshape','bim:truenorth']}   /* __acad3dV103 */"""),
    ("""    'bim:footing':ric(""",
     """    'bim:property':ric('<path d="M3 17L8 4l13 5-4 11z" stroke-dasharray="5 2 1.5 2"/>'),   /* __acad3dV103 */
    'bim:propshape':ric('<rect x="4" y="5" width="15" height="13" stroke-dasharray="5 2 1.5 2"/><path d="M8 11h7"/>'),
    'bim:truenorth':ric('<circle cx="12" cy="12" r="8"/><path d="M12 5l3 9-3-2-3 2z"/>'),
    'bim:footing':ric("""),
    ("""'bim:foundwall':'Wall Foundation','bim:footing':'Isolated Footing',""",
     """'bim:foundwall':'Wall Foundation','bim:footing':'Isolated Footing','bim:property':'Property Line','bim:propshape':'Property from Shape','bim:truenorth':'True North',"""),
    ("""    if(act==='bim:foundslab'){startFoundationSlabTool();return;}""",
     """    if(act==='bim:foundslab'){startFoundationSlabTool();return;}
    if(act==='bim:property'){openPropertyDlg(null);return;}              /* __acad3dV103 */
    if(act==='bim:propshape'){bimPropertyFromSketch(objById(A3D.sel));return;}
    if(act==='bim:truenorth'){openTrueNorthDlg();return;}"""),
    ("""    foundslab:function(){startFoundationSlabTool();},""",
     """    foundslab:function(){startFoundationSlabTool();},
    propertyline:function(){openPropertyDlg(null);},                                   /* __acad3dV103 */
    propertyshape:function(){bimPropertyFromSketch(objById(A3D.sel));},
    propertyedit:function(){var o=objById(A3D.sel);if(bimIsProperty(o))openPropertyDlg(o);else a3dToast('Select a property line to edit');},
    truenorth:function(){openTrueNorthDlg();},"""),
    ("""    ['FOUNDATIONSLAB',['FS'],'foundslab','Foundation slab in an enclosed region'],""",
     """    ['FOUNDATIONSLAB',['FS'],'foundslab','Foundation slab in an enclosed region'],
    ['PROPERTYLINE',['PROP'],'propertyline','Property line from bearings and distances'],
    ['PROPERTYFROMSHAPE',['PROPSH'],'propertyshape','Property line from the selected closed shape'],
    ['PROPERTYEDIT',['PROPED'],'propertyedit','Edit the legs of the selected property line'],
    ['TRUENORTH',['TN'],'truenorth','Set the angle from project north to true north'],"""),
    # exports
    ("""      }else if(o.t==='roomtag'){   /* __acad3dV101 */
        if(bimAnnotDrawable(o))text(o.pt,bimRoomTagText(o),0.25,lay);""",
     """      }else if(bimIsProperty(o)){   /* __acad3dV103: WORLD points; %%d is the R12 degree mark */
        var pgD=bimPropertyGeometry(o),lk;
        poly(pgD.ring,true,lay);
        for(lk=0;lk<o.legs.length&&lk+1<pgD.pts.length;lk++)
          text([(pgD.pts[lk][0]+pgD.pts[lk+1][0])/2,(pgD.pts[lk][1]+pgD.pts[lk+1][1])/2],
               bimFormatBearing(o.legs[lk].az,'%%d')+' '+o.legs[lk].d.toFixed(2),0.25,lay);
      }else if(o.t==='roomtag'){   /* __acad3dV101 */
        if(bimAnnotDrawable(o))text(o.pt,bimRoomTagText(o),0.25,lay);"""),
    ("""      }else if(o.t==='roomtag'){   /* __acad3dV101 */
        if(bimAnnotDrawable(o))text(o.pt,bimRoomTagText(o),0.25,lay,o.id,rg);""",
     """      }else if(bimIsProperty(o)){   /* __acad3dV103 */
        var pgS=bimPropertyGeometry(o),lks;
        poly(pgS.ring,true,lay,o.id,rg,false);
        for(lks=0;lks<o.legs.length&&lks+1<pgS.pts.length;lks++)
          text([(pgS.pts[lks][0]+pgS.pts[lks+1][0])/2,(pgS.pts[lks][1]+pgS.pts[lks+1][1])/2],
               bimFormatBearing(o.legs[lks].az)+' '+o.legs[lks].d.toFixed(2),0.25,lay,o.id,rg);
      }else if(o.t==='roomtag'){   /* __acad3dV101 */
        if(bimAnnotDrawable(o))text(o.pt,bimRoomTagText(o),0.25,lay,o.id,rg);"""),
    ("""      }else if(o.t==='roomtag'){   /* __acad3dV101 */
        if(bimAnnotDrawable(o))txt(o.pt,bimRoomTagText(o),3.0,o.id,o.y,rg);""",
     """      }else if(bimIsProperty(o)){   /* __acad3dV103 */
        var pgV=bimPropertyGeometry(o),lkv;
        poly(pgV.ring,true,o.id,null,rg,false);
        for(lkv=0;lkv<o.legs.length&&lkv+1<pgV.pts.length;lkv++)
          txt([(pgV.pts[lkv][0]+pgV.pts[lkv+1][0])/2,(pgV.pts[lkv][1]+pgV.pts[lkv+1][1])/2],
              bimFormatBearing(o.legs[lkv].az)+' '+o.legs[lkv].d.toFixed(2),2.4,o.id,null,rg);
      }else if(o.t==='roomtag'){   /* __acad3dV101 */
        if(bimAnnotDrawable(o))txt(o.pt,bimRoomTagText(o),3.0,o.id,o.y,rg);"""),
    # marker and test surface
    ("""  window.__a3dRectFootprint=bimRectFootprint;""",
     """  window.__a3dRectFootprint=bimRectFootprint;
  /* __acad3dV103: site -- property lines, setbacks, true north. */
  window.__a3dParseBearing=bimParseBearing;
  window.__a3dFormatBearing=bimFormatBearing;
  window.__a3dParseLegs=bimParseLegs;
  window.__a3dTraverse=bimTraverse;
  window.__a3dLegsFromRing=bimLegsFromRing;
  window.__a3dSetbackRing=bimSetbackRing;
  window.__a3dPropertyGeometry=function(id){var o=objById(id);return bimIsProperty(o)?JSON.parse(JSON.stringify(bimPropertyGeometry(o))):null;};
  window.__a3dSetbackViolations=function(id){var o=objById(id);return bimIsProperty(o)?bimSetbackViolations(o).list:null;};
  window.__a3dPropertyFromSketch=function(id){var p=bimPropertyFromSketch(objById(id));return p?p.id:null;};
  window.__a3dSetTrueNorth=bimSetTrueNorth;
  window.__a3dNorthArrow=function(){return A3D.lastNorth?JSON.parse(JSON.stringify(A3D.lastNorth)):null;};
  window.__acad3dV103='bearings,traverse,closure,propertyline,propertyfromshape,setbacks,setbackviolations,truenorth,northarrow,propertyexport';"""),
]
EDITS = [(a, js_ascii(b)) for (a, b) in EDITS]
for old, new in EDITS:
    assert txt.count(old) == 1, 'anchor count %d for %r' % (txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
for name in ['__a3dParseBearing','__a3dFormatBearing','__a3dParseLegs','__a3dTraverse','__a3dLegsFromRing','__a3dSetbackRing',
             '__a3dPropertyGeometry','__a3dSetbackViolations','__a3dPropertyFromSketch','__a3dSetTrueNorth','__a3dNorthArrow']:
    n = len(re.findall(r'window\.' + re.escape(name) + r'\s*=', txt))
    assert n == 1, '%s defined %d times' % (name, n)
SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
