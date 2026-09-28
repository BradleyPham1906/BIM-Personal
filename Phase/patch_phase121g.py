"""patch_phase121g.py -- V121: every way of selecting asks the layers.

Four ways of selecting ignored them. SELECT ALL (Ctrl+A) took every object in the model -- on frozen
and locked layers too, so a Delete right after it erased what nobody could see or was allowed to
touch. The Project Browser's classification rows did the same. The Dependencies group in Properties
and the rows of Check Model selected whatever they named, on a locked layer or not; so did the hidden
object rows.

Now:
  - SELECT ALL and the classification rows take AutoCAD's ALL (SELECT, AutoCAD 2024 help: "all
    objects ... except those objects on frozen or on locked layers") -- a layer that is off is
    included, which is exactly why AutoCAD's users freeze a layer rather than turn it off when it
    must stay out of a selection. The toast says how many of the selection are on layers that are
    off, and how many were left out.
  - A list row that names one object -- the Layers panel, the Dependencies group, Check Model, the
    object rows -- refuses one on a layer that is off, frozen or locked, and says which, through
    one refusal.
  - The selection never holds an object on a frozen or locked layer: saveSoon, which every change
    passes through, drops one. An object drawn on a locked current layer is made there, as AutoCAD
    allows, and is not left selected, since it cannot be modified.
  - The transform gizmo moves what the selection holds, as the body drag and the nudge keys always
    did: an object on a layer that is off is in the selection only because SELECT ALL took it, and
    AutoCAD's MOVE moves it too."""
NAME = 'patch_phase121g.py'
BASE = '7b20f27b2ecee98850bd4252f3e9217df00f2a9a79cf944009b567433c65da90'
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
# ---- 1. the refusal and the rule, in one place, beside the layer questions
rep("""  function bimLayerSelectable(o){
    var s=bimObjLayerState(o);
    return !s.frozen&&!s.locked;
  }
""", r"""  function bimLayerSelectable(o){
    var s=bimObjLayerState(o);
    return !s.frozen&&!s.locked;
  }
  /* ================= __acad3dV121: selecting, by the layers =================
     A click, a window and a list row pick what is shown and unlocked (bimLayerPickable); a list row
     that names one object refuses the rest through bimLayerPickRefusal. SELECT ALL and every
     select-by-criteria take AutoCAD's ALL through bimSelectByRule, and say how many of the
     selection cannot be seen and how many were left out. The selection never holds an object on a
     frozen or locked layer: saveSoon drops one (bimLayerDropUnselectable). */
  function bimLayerPickRefusal(o){
    var s=bimObjLayerState(o);
    if(s.on&&!s.frozen&&!s.locked)return '';
    return o.name+' is on a layer that is '+(!s.on?'off':(s.frozen?'frozen':'locked'))+': it cannot be selected';
  }
  function bimSelectByRule(cands){
    var ids=[],hidden=0,out=0,i,o;
    for(i=0;i<cands.length;i++){
      o=cands[i];
      if(!bimLayerSelectable(o)){out++;continue;}
      ids.push(o.id);
      if(!bimLayerShown(o))hidden++;
    }
    A3D.selSet=ids;A3D.sel=ids.length?ids[0]:null;A3D.sel2=null;
    refreshTree();refreshProps();paint();
    a3dToast('Selected '+ids.length+' object(s)'+(hidden?', '+hidden+' of them on layers that are off':'')+
      (out?'; '+out+' on frozen or locked layers left out':''));
    return ids;
  }
  function bimLayerDropUnselectable(){
    var o,n=0,k;
    if(A3D.sel&&(o=objById(A3D.sel))&&!bimLayerSelectable(o)){A3D.sel=null;n++;}
    if(A3D.sel2&&(o=objById(A3D.sel2))&&!bimLayerSelectable(o)){A3D.sel2=null;n++;}
    if(A3D.selSet&&A3D.selSet.length){
      k=A3D.selSet.length;
      A3D.selSet=A3D.selSet.filter(function(id){var q=objById(id);return !q||bimLayerSelectable(q);});
      n+=k-A3D.selSet.length;
    }
    return n;
  }
""")

# ---- 2. SELECT ALL
rep("""    selAll:function(){
      A3D.selSet=A3D.objs.map(function(o){return o.id;});
      A3D.sel=A3D.selSet.length?A3D.selSet[0]:null;A3D.sel2=null;
      refreshTree();refreshProps();paint();
      a3dToast('Selected '+A3D.selSet.length+' object(s)');
    },
""", """    selAll:function(){bimSelectByRule(A3D.objs);},   /* __acad3dV121: AutoCAD's ALL -- frozen and locked layers left out */
""")

# ---- 3. the classification rows
rep("""        var matches=A3D.objs.filter(function(o){return o.classId===clsId;}).map(function(o){return o.id;});
        if(!matches.length){a3dToast('No objects use this classification');return;}
        A3D.selSet=matches;A3D.sel=matches[0];A3D.sel2=null;
        refreshTree();paint();
        a3dToast('Selected '+matches.length+' object(s)');
        return;
""", """        var matches=A3D.objs.filter(function(o){return o.classId===clsId;});
        if(!matches.length){a3dToast('No objects use this classification');return;}
        bimSelectByRule(matches);   /* __acad3dV121: as SELECT ALL, by the layers */
        return;
""")

# ---- 4. a row that names one object
rep("      if(r){A3D.sel=r.getAttribute('data-checkid');A3D.selSet=[A3D.sel];refreshTree();paint();return;}\n",
    "      if(r){\n"
    "        var cko=objById(r.getAttribute('data-checkid')),ckw=cko?bimLayerPickRefusal(cko):'';   /* __acad3dV121 */\n"
    "        if(!cko){a3dToast('That object no longer exists');return;}\n"
    "        if(ckw){a3dToast(ckw);return;}\n"
    "        A3D.sel=cko.id;A3D.selSet=[A3D.sel];refreshTree();paint();return;\n"
    "      }\n")
rep("""        if(!selObj){a3dToast('That element no longer exists');refreshProps();return;}
        A3D.sel=selObj.id;A3D.sel2=null;A3D.selSet=[selObj.id];
""", """        if(!selObj){a3dToast('That element no longer exists');refreshProps();return;}
        var dsw=bimLayerPickRefusal(selObj);   /* __acad3dV121 */
        if(dsw){a3dToast(dsw);return;}
        A3D.sel=selObj.id;A3D.sel2=null;A3D.selSet=[selObj.id];
""")
rep("""      if(!r)return;
      A3D.sel=r.getAttribute('data-a3did');
      A3D.selSet=A3D.sel?[A3D.sel]:[];
""", """      if(!r)return;
      var rwo=objById(r.getAttribute('data-a3did')),rww=rwo?bimLayerPickRefusal(rwo):'';   /* __acad3dV121 */
      if(rww){a3dToast(rww);return;}
      A3D.sel=r.getAttribute('data-a3did');
      A3D.selSet=A3D.sel?[A3D.sel]:[];
""")
rep("""    var s=bimObjLayerState(o);
    if(!s.on||s.frozen||s.locked){
      a3dToast(o.name+' is on a layer that is '+(!s.on?'off':(s.frozen?'frozen':'locked'))+': it cannot be selected');
      return;
    }
""", """    var why=bimLayerPickRefusal(o);   /* the one refusal */
    if(why){a3dToast(why);return;}
""")

# ---- 5. the selection never holds an object on a frozen or locked layer
rep("    bimAdoptLayers();   /* __acad3dV121 */\n",
    "    bimAdoptLayers();   /* __acad3dV121 */\n"
    "    if(bimLayerDropUnselectable()){refreshTree();refreshProps();paint();}   /* __acad3dV121 */\n")

# ---- 6. the gizmo moves what the selection holds, as the drag and the nudge do
rep("      if(!bimLayerPickable(o))return false;   /* __acad3dV121 */\n",
    "      if(!bimLayerSelectable(o))return false;   /* __acad3dV121: what the selection may hold */\n")

# ---- the checks
code = re.sub(r'/\*.*?\*/', '', t, flags=re.S)
if re.search(r'A3D\.selSet=A3D\.objs\.map', code):
    sys.exit('ABORT: SELECT ALL still takes every object')
m = re.search(r"\n  function bimGizmoIds\(\)\{.*?\n  \}", code, re.S)
if not m or 'bimLayerSelectable' not in m.group(0):
    sys.exit('ABORT: the gizmo does not ask what the selection may hold')
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
