"""patch_phase123g.py -- V123: a primitive's sizes in Properties, Push/Pull on the toolbar, the marker.

1. A box's size was nowhere to be seen once it was placed. Properties showed no Dimensions for a
   primitive at all, and a change handler for its parameters ('prm:') survived an earlier rewrite
   of the panel with no field left to call it -- the first standing law's worst case, a leftover
   that reads as finished. The Dimensions group now lists every parameter of a primitive: lengths in
   the project's unit (the handler converts them back through SCALE, the factor the parameters are
   kept in), the angle of a part cylinder and the sides of a prism as they are. Their names are the
   names a pushed face reads out ("Height", "Outer radius"). A changed size keeps the primitive's
   base where it stood -- the mesh is centred on its position, so a taller box used to sink below
   its level by half the change -- which is also what pulling its top does.
2. Push/Pull is on the toolbar, in the Drafting tab's Modify group and beside Pad and Pocket: it is
   PRESSPULL, the next click takes a face.
3. The phase marker."""
NAME = 'patch_phase123g.py'
BASE = '3f9d20b05eb228ea3d276a48bf705f92d5c770a68e545c3ecf91b5afcc8ea99c'
import hashlib, pathlib, sys
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')
raw = P.read_bytes()
h0 = hashlib.sha256(raw).hexdigest()
if h0 != BASE:
    sys.exit('ABORT: baseline %s, expected %s' % (h0, BASE))
t = raw.decode('utf-8')


def esc(s):
    """Non-ASCII in inserted text becomes a \\uXXXX escape, by code rather than by care (V103)."""
    return ''.join(ch if ord(ch) < 128 else '\\u%04x' % ord(ch) for ch in s)


def rep(old, new, n=1):
    global t
    new = esc(new)
    c = t.count(old)
    if c != n:
        sys.exit('ABORT: %d occurrences, expected %d: %r' % (c, n, old[:90]))
    t = t.replace(old, new)


def after_line(head, new):
    """Insert new text after the whole line that starts with head (head must be unique)."""
    global t
    c = t.count(head)
    if c != 1:
        sys.exit('ABORT: %d occurrences, expected 1: %r' % (c, head[:90]))
    e = t.index('\n', t.index(head)) + 1
    t = t[:e] + esc(new) + t[e:]


def span(head, tail, new, lines):
    """Replace from the start of head up to (not including) the first tail after it. The span may
    hold non-ASCII that cannot be retyped, so it is found by its ends; head must be unique, and the
    number of lines removed must be exactly what was measured, so a tail that matched somewhere
    unexpected cannot quietly take the wrong amount."""
    global t
    c = t.count(head)
    if c != 1:
        sys.exit('ABORT: span head %d occurrences, expected 1: %r' % (c, head[:90]))
    s = t.index(head)
    e = t.find(tail, s + len(head))
    if e < 0:
        sys.exit('ABORT: span tail not found after head: %r' % tail[:90])
    got = t[s:e].count('\n')
    if got != lines:
        sys.exit('ABORT: span covers %d lines, expected %d: %r' % (got, lines, head[:60]))
    t = t[:s] + esc(new) + t[e:]

# 1. a primitive's sizes in Properties
rep("""    }else if(o.t==='sketch'){
      dims+=bimPropText('Points',o.pts.length);""", """    }else if(!o.mesh&&o.prm&&TYPES[o.t]){
      /* __acad3dV123: a primitive's parameters, lengths in the project's unit -- a box's size was
         shown nowhere once it was placed. Named as a pushed face reads them out. */
      var tpP=TYPES[o.t],ppP=mergePrm(o.t,o.prm),pi;
      for(pi=0;pi<tpP.prm.length;pi++){
        var pn=tpP.prm[pi][0],pl=bimPrmLabel(o.t,pn);
        if(pn==='Angle')dims+=bimPropRow('Angle (\\u00b0)','<input type="number" step="any" min="1" max="360" data-propf="prm:Angle" value="'+bimDispNum(ppP.Angle,2)+'">');
        else if(pn==='Polygon')dims+=bimPropRow('Sides','<input type="number" step="1" min="3" data-propf="prm:Polygon" value="'+Math.round(ppP.Polygon)+'">');
        else dims+=bimPropLen(pl,ppP[pn]*SCALE,'prm:'+pn,0);
      }
    }else if(o.t==='sketch'){
      dims+=bimPropText('Points',o.pts.length);""")
rep("""      }else if(f.indexOf('prm:')===0){
        var pname=f.slice(4);
        var newPrm={},pk;
        for(pk in o.prm)if(o.prm.hasOwnProperty(pk))newPrm[pk]=o.prm[pk];
        newPrm[pname]=inp.value;
        var merged=mergePrm(o.t,newPrm);
        var verr=validatePrm(o.t,merged);
        if(verr){a3dToast(verr);refreshProps();return;}
        pushUndo();
        o.prm=merged;
        refreshTree();paint();saveSoon();
      }""", """      }else if(f.indexOf('prm:')===0){
        /* __acad3dV123: the Dimensions rows above call this again. A length arrives in metres (the
           data-proplen conversion at the top) and is kept in the parameter's own unit, SCALE. */
        var pname=f.slice(4);
        var newPrm={},pk,pval=parseFloat(inp.value);
        if(!isFinite(pval)){a3dToast('Must be a number');refreshProps();return;}
        if(pname!=='Angle'&&pname!=='Polygon')pval=pval/SCALE;
        for(pk in o.prm)if(o.prm.hasOwnProperty(pk))newPrm[pk]=o.prm[pk];
        newPrm[pname]=pval;
        var merged=mergePrm(o.t,newPrm);
        var verr=validatePrm(o.t,merged);
        if(verr){a3dToast(verr);refreshProps();return;}
        var base0=meshMinY(meshOf(o));
        pushUndo();
        o.prm=merged;
        /* the base stays where it stood: the mesh is centred on the position, so a taller box sank
           below its level by half the change -- pulling the top keeps the base too */
        var base1=meshMinY(meshOf(o));
        if(isFinite(base0)&&isFinite(base1)){if(!o.pos)o.pos=[0,0,0];o.pos[1]+=base0-base1;}
        refreshTree();refreshProps();paint();saveSoon();
      }""")
rep("""  function bimPrmDim(o,param){""", """  /* a primitive parameter's name, as Properties shows it and a pushed face reads it out */
  var BIM_PRM_LABELS={cone:{Radius1:'Bottom radius',Radius2:'Top radius'},torus:{Radius1:'Ring radius',Radius2:'Tube radius'},
    ellipsoid:{Radius1:'Vertical radius',Radius2:'Horizontal radius'},tube:{OuterRadius:'Outer radius',InnerRadius:'Inner radius'}};
  function bimPrmLabel(t,param){return (BIM_PRM_LABELS[t]&&BIM_PRM_LABELS[t][param])||param;}
  function bimPrmDim(o,param){""")

# 2. Push/Pull on the toolbar
rep("""    'bim:scale':ric('<rect x="3" y="12" width="9" height="9"/><path d="M12 12L21 3"/><path d="M15 3h6v6"/>'),""",
    """    'bim:scale':ric('<rect x="3" y="12" width="9" height="9"/><path d="M12 12L21 3"/><path d="M15 3h6v6"/>'),
    'bim:presspull':ric('<path d="M4 15l8-4 8 4-8 4z"/><path d="M4 15v3l8 4 8-4v-3"/><path d="M12 11V2M9 5l3-3 3 3"/>'),   /* __acad3dV123 */""")
rep("""      'bim:clonelinked':'Linked Clone','bim:syncclones':'Sync Clones',""",
    """      'bim:clonelinked':'Linked Clone','bim:syncclones':'Sync Clones','bim:presspull':'Push/Pull',   /* __acad3dV123 */""")
rep("""    if(act==='bim:scale'){startScaleTool();return;}""",
    """    if(act==='bim:scale'){startScaleTool();return;}
    if(act==='bim:presspull'){bimPressPullCommand();return;}   /* __acad3dV123 */""")
rep("""      {t:'Modify',small:['bim:trim','bim:extend','bim:fillet','bim:chamfer','bim:break','bim:lengthen','bim:scale','bim:offset','bim:align','bim:mirror','bim:rotate','m:array','bim:polararray','m:dup','m:del']},""",
    """      {t:'Modify',small:['bim:trim','bim:extend','bim:fillet','bim:chamfer','bim:break','bim:lengthen','bim:scale','bim:offset','bim:align','bim:mirror','bim:rotate','bim:presspull','m:array','bim:polararray','m:dup','m:del']},""")
rep("""      {t:'Sketch',small:['s:rect','s:circle','s:poly','p:pad','p:pocket']},""",
    """      {t:'Sketch',small:['s:rect','s:circle','s:poly','p:pad','p:pocket','bim:presspull']},""")

# 3. the marker
rep("""  window.__a3dPushValue=function(dist){return bimPushValue(dist);};""",
    """  window.__a3dPushValue=function(dist){return bimPushValue(dist);};
  /* a suite that counts undo steps starts each scene from an empty history: past UNDO_MAX a step
     pushes the oldest out and the depth stops moving */
  window.__a3dTestClearUndo=function(){UNDO_STACK.length=0;REDO_STACK.length=0;return true;};
  window.__acad3dV123='projectunits,valuekinds,clicktotype,valuebox,noundoonclick,copyonfirstmove,bodydragisgizmomove,'+
    'carrybim,copyatoffset,flooroutlineturns,padatsketch,faces,facekeys,presspull,pushpull,pushsnap,pushrange,'+
    'sketchpull,primitivedimensions';""")

# 4. what the read-outs say, for a suite
rep("""            factor:drag.factor||null,copies:drag.copies?drag.copies.ids.slice():null};""",
    """            factor:drag.factor||null,copies:drag.copies?drag.copies.ids.slice():null,
            readout:bimGizmoReadout(drag)};   /* __acad3dV123: what the read-out says, unit and all */""")
rep("""            kind:drag.f?drag.f.kind:null,fine:!!drag.fine};""",
    """            kind:drag.f?drag.f.kind:null,fine:!!drag.fine,readout:drag.f?bimPushReadout(drag):null};""")
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
