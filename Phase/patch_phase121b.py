"""patch_phase121b.py -- V121: changing a layer, by AutoCAD's rules, through one set of functions.

A layer was changed by six small functions, each doing its part and none of them checking anything:
two layers could share a name, the current layer could be deleted (its objects moved to whichever
layer happened to be first), and turning a layer off left its objects selected -- so a Delete or a
nudge acted on objects nobody could see. The Properties panel's Layer field wrote the object's
layer directly.

Now every change goes through bimLayerSet, bimLayerNew, bimLayerDelete, bimLayerMakeCurrent or
bimObjSetLayer. Each is one undo step, and each refuses what AutoCAD refuses and says why:

  - a name must be new (AutoCAD's names are not case-sensitive) and free of < > / \\ " : ; ? * | , = `;
  - the current layer cannot be frozen, deleted, or moved under a frozen layer, and a frozen layer
    cannot be made current;
  - the first layer (AutoCAD's layer 0) cannot be deleted, nor a layer that holds objects -- the
    old delete moved them to whichever layer came first -- and a deleted layer's sub-layers move up;
  - a layer cannot be put under itself or under one of its own sub-layers.

A new layer takes its appearance -- color, linetype, lineweight, transparency, plot -- from the
layer it is made from, as AutoCAD's New Layer takes the selected layer's. Whatever a change makes
unpickable (off, frozen, locked) leaves the selection.

The linetypes are AutoCAD's acadiso.lin set, kept as their definitions in millimetres on paper so
the drawing, the plots and the DXF derive their patterns from one table; the lineweights are
AutoCAD's list, in millimetres."""
NAME = 'patch_phase121b.py'
BASE = 'e11c439eba0c73c96b84d2b5a1c4633138e08b5f27dc86477f41eae6396d056d'
import re
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
# ---- the old six functions become the rules, in one place
span("  function addLayer(name,color){\n", "  var BIM_EYE_ON=", r"""  /* ================= __acad3dV121: changing a layer, by AutoCAD's rules =================

     Every change to a layer goes through bimLayerSet, bimLayerNew, bimLayerDelete,
     bimLayerMakeCurrent or bimObjSetLayer -- the Layers panel, the Layer Properties Manager, the
     Properties panel and the commands alike. Each is one undo step; each refuses what AutoCAD
     refuses, and says why. */

  /* AutoCAD's acadiso.lin set, as its definitions, in millimetres on paper: a positive number is a
     dash, a negative one a gap, 0 a dot. The canvas, the plots and the DXF each derive their
     pattern from this one table. */
  var BIM_LINETYPES=[
    {name:'Continuous',desc:'Solid line',pat:[]},
    {name:'DASHED',desc:'Dashed __ __ __ __ __',pat:[12.7,-6.35]},
    {name:'HIDDEN',desc:'Hidden _ _ _ _ _ _ _',pat:[6.35,-3.175]},
    {name:'CENTER',desc:'Center ____ _ ____ _ ____',pat:[31.75,-6.35,6.35,-6.35]},
    {name:'PHANTOM',desc:'Phantom _____ _ _ _____ _ _',pat:[31.75,-6.35,6.35,-6.35,6.35,-6.35]},
    {name:'DOT',desc:'Dot . . . . . . . .',pat:[0,-6.35]},
    {name:'DASHDOT',desc:'Dash dot __ . __ . __ .',pat:[12.7,-6.35,0,-6.35]},
    {name:'BORDER',desc:'Border __ __ . __ __ .',pat:[12.7,-6.35,12.7,-6.35,0,-6.35]},
    {name:'DIVIDE',desc:'Divide __ . . __ . .',pat:[12.7,-6.35,0,-6.35,0,-6.35]}
  ];
  /* AutoCAD's lineweights, in millimetres. A layer's lineweight is one of these, or null: Default. */
  var BIM_LINEWEIGHTS=[0,0.05,0.09,0.13,0.15,0.18,0.2,0.25,0.3,0.35,0.4,0.5,0.53,0.6,0.7,0.8,0.9,1,1.06,1.2,1.4,1.58,2,2.11];
  var BIM_LAYER_BADCHARS=/[<>\/\\":;?*|,=`]/;
  function bimLinetypeDef(name){
    var i,n=String(name==null?'':name).toLowerCase();
    for(i=0;i<BIM_LINETYPES.length;i++)if(BIM_LINETYPES[i].name.toLowerCase()===n)return BIM_LINETYPES[i];
    return null;
  }
  function bimLayerByName(name,exceptId){
    var i,n=String(name==null?'':name).replace(/^\s+|\s+$/g,'').toLowerCase();
    for(i=0;i<A3D.layers.length;i++)
      if(A3D.layers[i].id!==exceptId&&String(A3D.layers[i].name).toLowerCase()===n)return A3D.layers[i];
    return null;
  }
  /* true when layer `ancestorId` is `ly` itself or any layer above it */
  function bimLayerUnder(ly,ancestorId){
    var ch=bimLayerChain(ly),i;
    for(i=0;i<ch.length;i++)if(ch[i].id===ancestorId)return true;
    return false;
  }
  function bimLayerNameCheck(name,exceptId){
    var n=String(name==null?'':name).replace(/^\s+|\s+$/g,'');
    if(!n)return 'A layer needs a name';
    if(n.length>64)return 'A layer name is 64 characters at most';
    if(BIM_LAYER_BADCHARS.test(n))return 'A layer name cannot contain < > / \\ " : ; ? * | , = or `';
    if(bimLayerByName(n,exceptId))return 'There is already a layer called '+n;
    return '';
  }
  function bimLayerUniqueName(base){
    var n=1;
    while(bimLayerByName(base+' '+n))n++;
    return base+' '+n;
  }
  /* what can no longer be picked leaves the selection -- a Delete or a nudge must not act on objects
     nobody can see or is allowed to touch */
  function bimLayerDropUnpickable(){
    var o;
    if(A3D.sel&&(o=objById(A3D.sel))&&!bimLayerPickable(o))A3D.sel=null;
    if(A3D.sel2&&(o=objById(A3D.sel2))&&!bimLayerPickable(o))A3D.sel2=null;
    if(A3D.selSet&&A3D.selSet.length)A3D.selSet=A3D.selSet.filter(function(id){var q=objById(id);return !q||bimLayerPickable(q);});
  }
  function bimLayerChanged(){
    bimLayerDropUnpickable();
    refreshLayers();refreshTree();paint();saveSoon();
  }
  function bimLayerRefuse(msg){
    a3dToast(msg);
    return false;
  }
  function bimLayerSet(id,field,val){
    var ly=bimLayerById(id),err,v;
    if(!ly){console.warn('[BIM] No layer '+id);return bimLayerRefuse('That layer no longer exists');}
    var cur=bimLayerById(A3D.activeLayer);
    if(field==='name'){
      v=String(val==null?'':val).replace(/^\s+|\s+$/g,'');
      if(v===ly.name)return true;
      err=bimLayerNameCheck(v,ly.id);
      if(err)return bimLayerRefuse(err);
    }else if(field==='color'){
      v=String(val||'').toLowerCase();
      if(!/^#[0-9a-f]{6}$/.test(v))return bimLayerRefuse('A layer color is a colour such as #7f9db8');
    }else if(field==='visible'||field==='frozen'||field==='locked'||field==='plot'){
      v=!!val;
      if(field==='frozen'&&v&&cur&&bimLayerUnder(cur,ly.id))
        return bimLayerRefuse(cur.id===ly.id?'The current layer cannot be frozen: make another layer current first'
                                            :'This layer holds the current layer, which cannot be frozen');
    }else if(field==='linetype'){
      var lt=bimLinetypeDef(val);
      if(!lt)return bimLayerRefuse('Unknown linetype: '+val);
      v=lt.name;
    }else if(field==='lineweight'){
      if(val===null||val===''||val==='default'||val===undefined)v=null;
      else{
        v=+val;
        if(BIM_LINEWEIGHTS.indexOf(v)<0)return bimLayerRefuse('Not one of AutoCAD\'s lineweights: '+val);
      }
    }else if(field==='transparency'){
      v=Math.round(+val);
      if(!isFinite(v)||v<0||v>90)return bimLayerRefuse('Transparency is 0 to 90');
    }else if(field==='description'){
      v=String(val==null?'':val).slice(0,200);
    }else if(field==='parent'){
      v=(val===null||val===''||val===undefined)?null:String(val);
      if(v!==null){
        var P=bimLayerById(v);
        if(!P)return bimLayerRefuse('That layer no longer exists');
        if(bimLayerUnder(P,ly.id))return bimLayerRefuse('A layer cannot go under itself or one of its own sub-layers');
        if(cur&&bimLayerUnder(cur,ly.id)&&bimLayerEff(P).frozen)
          return bimLayerRefuse('The current layer cannot go under a frozen layer');
      }
    }else{
      console.warn('[BIM] Unknown layer field '+field);
      return bimLayerRefuse('That is not a layer property');
    }
    var was;   /* what the layer reads as now, by the same tolerant rules its flags are read by */
    if(field==='visible')was=(ly.visible!==false);
    else if(field==='plot')was=(ly.plot!==false);
    else if(field==='frozen'||field==='locked')was=!!ly[field];
    else if(field==='lineweight'||field==='parent')was=(ly[field]===undefined)?null:ly[field];
    else if(field==='linetype')was=(bimLinetypeDef(ly.linetype)||BIM_LINETYPES[0]).name;
    else if(field==='transparency')was=isFinite(ly.transparency)?+ly.transparency:0;
    else if(field==='description')was=(typeof ly.description==='string')?ly.description:'';
    else was=ly[field];
    if(was===v)return true;
    pushUndo();
    ly[field]=v;
    if(field==='visible'&&!v&&cur&&bimLayerUnder(cur,ly.id))a3dToast('The current layer is off: what you draw on it will not show until it is on');
    bimLayerChanged();
    return true;
  }
  /* opts: {name, parent, from (a layer to take the appearance of), color, current} */
  function bimLayerNew(opts){
    opts=opts||{};
    var name=(opts.name==null||opts.name==='')?bimLayerUniqueName('Layer'):String(opts.name).replace(/^\s+|\s+$/g,'');
    var err=bimLayerNameCheck(name,null);
    if(err){bimLayerRefuse(err);return null;}
    var par=opts.parent?bimLayerById(opts.parent):null;
    if(opts.parent&&!par){bimLayerRefuse('That layer no longer exists');return null;}
    var src=opts.from?bimLayerById(opts.from):par;
    pushUndo();
    var lyr={id:'layer-'+Date.now().toString(36)+'-'+(A3D.seq++),name:name,
      color:(opts.color&&/^#[0-9a-fA-F]{6}$/.test(opts.color))?opts.color.toLowerCase():(src?src.color:bimNextLayerColor()),
      visible:true,locked:false,frozen:false,
      linetype:(src&&bimLinetypeDef(src.linetype))?bimLinetypeDef(src.linetype).name:'Continuous',
      lineweight:(src&&src.lineweight!==undefined)?src.lineweight:null,
      transparency:(src&&isFinite(src.transparency))?src.transparency:0,
      plot:!(src&&src.plot===false),
      description:'',parent:par?par.id:null};
    A3D.layers.push(lyr);
    if(opts.current)A3D.activeLayer=lyr.id;
    bimLayerChanged();
    return lyr;
  }
  /* AutoCAD's Delete Layer refuses layer 0, the current layer and a layer that holds objects. The
     first layer here is layer 0's counterpart: it is where an object whose layer is gone is read to
     be, so it always exists. A deleted layer's sub-layers move up to its own parent. */
  function bimLayerDelete(id){
    var ly=bimLayerById(id),i,n=0;
    if(!ly)return bimLayerRefuse('That layer no longer exists');
    if(ly===A3D.layers[0])return bimLayerRefuse(ly.name+' is the first layer, which (as AutoCAD\'s layer 0) cannot be deleted');
    if(id===A3D.activeLayer)return bimLayerRefuse('The current layer cannot be deleted: make another layer current first');
    for(i=0;i<A3D.objs.length;i++)if(bimLayerOf(A3D.objs[i])===ly)n++;
    if(n)return bimLayerRefuse(ly.name+' holds '+n+' object'+(n===1?'':'s')+': move '+(n===1?'it':'them')+' to another layer first');
    pushUndo();
    var kids=0;
    for(i=0;i<A3D.layers.length;i++)if(A3D.layers[i].parent===id){A3D.layers[i].parent=ly.parent||null;kids++;}
    A3D.layers.splice(A3D.layers.indexOf(ly),1);
    bimLayerChanged();
    a3dToast('Layer '+ly.name+' deleted'+(kids?'; '+kids+' sub-layer'+(kids===1?'':'s')+' moved up':''));
    return true;
  }
  function bimLayerMakeCurrent(id){
    var ly=bimLayerById(id);
    if(!ly)return bimLayerRefuse('That layer no longer exists');
    if(bimLayerEff(ly).frozen)return bimLayerRefuse('A frozen layer cannot be current: thaw it first');
    if(A3D.activeLayer===id)return true;
    A3D.activeLayer=id;
    refreshLayers();refreshProps();saveSoon();
    return true;
  }
  function bimObjSetLayer(objId,layerId){
    var o=objById(objId),ly=bimLayerById(layerId);
    if(!o)return false;
    if(!ly)return bimLayerRefuse('That layer no longer exists');
    if(bimLayerOf(o)===ly&&o.layer===ly.id)return true;
    pushUndo();
    o.layer=ly.id;
    bimLayerChanged();
    return true;
  }
  /* The names the rest of the file has always called. A layer made by an import or a standard name
     that already exists is that layer -- the import's objects join it -- as AutoCAD merges them. */
  function addLayer(name,color){
    var ex=name?bimLayerByName(name):null;
    if(ex){bimLayerMakeCurrent(ex.id);return ex;}
    return bimLayerNew({name:name||null,color:color,current:true});
  }
  function setActiveLayer(id){return bimLayerMakeCurrent(id);}
""", 37)

# ---- the Properties panel's Layer field goes through the same door
rep("      }else if(f==='layer'){\n        pushUndo();\n        o.layer=inp.value;\n        refreshLayers();paint();saveSoon();\n",
    "      }else if(f==='layer'){\n        bimObjSetLayer(o.id,inp.value);   /* __acad3dV121 */\n")

# ---- the hidden layer rows and the Project Browser's layer toggles call the rules too, until V121c
#      replaces both with the Layers panel
rep("      if(del2){removeLayer(del2.getAttribute('data-lyrdel'));ev.stopPropagation();return;}\n",
    "      if(del2){bimLayerDelete(del2.getAttribute('data-lyrdel'));ev.stopPropagation();return;}\n")
rep("      if(vis){toggleLayerVisible(vis.getAttribute('data-lyrvis'));ev.stopPropagation();return;}\n",
    "      if(vis){var lv=bimLayerById(vis.getAttribute('data-lyrvis'));if(lv)bimLayerSet(lv.id,'visible',lv.visible===false);ev.stopPropagation();return;}\n")
rep("      if(lock){toggleLayerLock(lock.getAttribute('data-lyrlock'));ev.stopPropagation();return;}\n",
    "      if(lock){var lk2=bimLayerById(lock.getAttribute('data-lyrlock'));if(lk2)bimLayerSet(lk2.id,'locked',!lk2.locked);ev.stopPropagation();return;}\n")
rep("      if(nm2!=null)renameLayer(lid,nm2);\n", "      if(nm2!=null)bimLayerSet(lid,'name',nm2);\n")
rep("      if((b=cl('[data-a3dblayerlock]'))){ev.stopPropagation();toggleLayerLock(b.getAttribute('data-a3dblayerlock'));refreshBrowser();return;}\n",
    "      if((b=cl('[data-a3dblayerlock]'))){ev.stopPropagation();var bl=bimLayerById(b.getAttribute('data-a3dblayerlock'));if(bl)bimLayerSet(bl.id,'locked',!bl.locked);return;}\n")
rep("      if((b=cl('[data-a3dblayervis]'))){ev.stopPropagation();toggleLayerVisible(b.getAttribute('data-a3dblayervis'));refreshBrowser();return;}\n",
    "      if((b=cl('[data-a3dblayervis]'))){ev.stopPropagation();var bv=bimLayerById(b.getAttribute('data-a3dblayervis'));if(bv)bimLayerSet(bv.id,'visible',bv.visible===false);return;}\n")

# ---- nothing is left of the old functions, and nothing writes a layer around the rules
code = re.sub(r'/\*.*?\*/', '', t, flags=re.S)
for dead in ('toggleLayerVisible', 'toggleLayerLock', 'renameLayer', 'removeLayer'):
    if re.search(r'(?<![\w.])' + dead + r'\(', code):
        sys.exit('ABORT: %s is still called' % dead)
if re.search(r'o\.layer\s*=\s*inp\.value', code):
    sys.exit('ABORT: the Properties Layer field still writes around the rules')
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
