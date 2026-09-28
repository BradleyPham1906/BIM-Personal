"""patch_phase123a.py -- V123: a typed or shown length is in the project's unit, and every handle says
what it takes.

The owner, before the Assets library: "geometry manipulation for objects, shapes and assets ... quite
limited for my push, pull, rotate when I click on these kinds of objects, even though we have the
gizmo ... look into Autodesk but also Rhinoceros by McNeel on how they do it."

Every tool studied finishes a gesture with a number: Rhino's gumball asks for a distance, an angle or
a factor, AutoCAD's dynamic input takes a distance, Revit's temporary dimension a size. The gizmo had
that since V112, and two faults in it:

1. A length was metres whatever the project was set to. The read-out wrote "500 mm" or "2 m" in a
   project set to centimetres, and a typed value was taken as metres: in a millimetre project, 500
   moved the selection half a kilometre. bimFmtLen's own comment said "the project's own unit". It is
   now, for every read-out and message that states a length; a typed length is divided by the
   project's scale on the way in. The same fault was in the coordinates typed while drawing
   (3,4 / @3,4 / 5<45 / a bare length), which read metres too, and is fixed with it.

2. A free move could not be typed at all ("a free move needs two numbers"). What a handle takes is
   now one function, bimGizmoValueKind: a length along an arrow, two along a plane square or the
   free-move square in a plan, three for the free-move square in 3D (the frame's X, Y and Z), an
   angle for a ring, a factor for a scale handle. The characters the typing accepts, the parser, the
   unit in the read-out and the commit all read it, so a comma is accepted exactly where two numbers
   are wanted."""
NAME = 'patch_phase123a.py'
BASE = '3d652e4282aff3f9c7f4f9017154a6d7cb4a1c7550c3b735b447cc30035f0b0c'
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

# 1. bimFmtLen: the project's unit and precision
rep("""  /* Distance in the project's own unit, at a precision that is readable rather than exact --
     the read-out is a guide during the gesture; Properties carries the authoritative number. */
  function bimFmtLen(d){
    var a=Math.abs(d);
    if(a<0.01)return '0 m';
    if(a<1)return (Math.round(d*1000))+' mm';
    return (Math.round(d*1000)/1000)+' m';
  }
""", """  /* Distance in the project's own unit, at a precision that is readable rather than exact --
     the read-out is a guide during the gesture; Properties carries the authoritative number.
     __acad3dV123: it said so and wrote metres and millimetres whatever the project was set to. It
     is the project's unit and precision now, through the function Properties shows a length with,
     so a read-out, every message that states a length and Properties give the same figure. */
  function bimFmtLen(d){
    var s=bimDispLen(d);
    if(s==='-0')s='0';
    return s+' '+bimUnitLabel();
  }
""")

# 2. the read-out while typing names the unit it is typed in
rep("""    if(typed!==null)return bimGizmoTypeLabel(dr)+'  '+typed+'_';""",
    """    if(typed!==null)return bimGizmoTypeLabel(dr)+'  '+typed+'_'+bimGizmoUnitSuffix(bimGizmoValueKind(dr));   /* __acad3dV123 */""")

# 3. a plane drag keeps the frame, which is what a typed X, Y, Z is measured along
rep("""    return {giz:true,gk:hit.kind,plane:hit.kind==='plane'?hit.plane.k:null,a:a.slice(),b:b.slice(),n:N,
            labA:la,labB:lb,snapWorld:snapWorld,O:g.origin.slice(),P0:P0,""",
    """    return {giz:true,gk:hit.kind,plane:hit.kind==='plane'?hit.plane.k:null,a:a.slice(),b:b.slice(),n:N,
            fr:g.frame,                                    /* __acad3dV123: what a typed X, Y, Z is along */
            labA:la,labB:lb,snapWorld:snapWorld,O:g.origin.slice(),P0:P0,""")

# 4. the typing: what a handle takes, one parser, one commit
span("  var A3D_GIZ_TYPE={active:false,buf:''};",
     "  /* Escape: the objects go back exactly where the press found them, and the gesture is over. */",
"""  var A3D_GIZ_TYPE={active:false,buf:''};
  function bimGizmoTyping(){return A3D_GIZ_TYPE.active?A3D_GIZ_TYPE.buf:null;}
  function bimGizmoTypeClear(){A3D_GIZ_TYPE.active=false;A3D_GIZ_TYPE.buf='';}
  /* __acad3dV123: the drag that is listening for a typed value, if any -- one test, read by the key
     handler, the key claim and the read-out. */
  function bimTypingDrag(){
    return (drag&&(drag.giz||drag.rot))?drag:null;
  }
  /* __acad3dV123: WHAT A HANDLE TAKES. A length along an arrow; two along a plane square, or along
     the free-move square in a plan; three along the gizmo's X, Y and Z for the free-move square in
     3D; an angle on a ring; a factor on a scale handle. The characters accepted while typing, the
     parser, the unit in the read-out and the commit all read this -- before V123 a free move could
     not be typed at all, because the commit had no case for it. */
  function bimGizmoValueKind(r){
    if(!r)return null;
    /* a drag record carries gk and snapWorld; a picked handle carries kind -- one rule for both, so
       what the hover hint promises is what the drag and the value box take */
    var k=r.gk||r.kind;
    if(r.rot||k==='tilt')return 'deg';
    if(k==='scale'||k==='uniform')return 'factor';
    if(k==='axis')return 'len';
    if(k==='plane')return 'len2';
    if(k==='centre')return (r.gk?r.snapWorld:!A3D.flat)?'len3':'len2';
    return null;
  }
  function bimGizmoValueCount(kind){return kind==='len2'?2:(kind==='len3'?3:1);}
  function bimGizmoUnitSuffix(kind){
    if(kind==='deg')return '\\u00b0';
    if(kind==='factor'||!kind)return '';
    return ' '+bimUnitLabel();
  }
  /* A typed value as numbers, lengths in metres. A length is typed in the project's unit: in a
     millimetre project 500 is half a metre. Before V123 it was taken as metres whatever the project
     showed, so 500 typed there moved the selection half a kilometre. X,Y on the free-move square in
     3D leaves Z at nought. */
  function bimGizmoParseValue(kind,text){
    if(!kind)return {error:'This handle is placed by dragging it'};
    var parts=String(text===undefined||text===null?'':text).split(','),nums=[],i,n=bimGizmoValueCount(kind);
    for(i=0;i<parts.length;i++){
      var p=parts[i].replace(/^\\s+|\\s+$/g,'');
      if(!/^[-+]?(\\d+\\.?\\d*|\\.\\d+)$/.test(p))return {error:'Not a number: '+(p||'(nothing)')};
      nums.push(parseFloat(p));
    }
    if(kind==='len3'&&nums.length===2)nums.push(0);
    if(nums.length!==n)
      return {error:kind==='len2'?'Type two numbers: X,Y':(kind==='len3'?'Type X,Y or X,Y,Z':'Type one number')};
    if(kind==='factor'&&!(nums[0]>0))return {error:'A scale factor has to be greater than zero'};
    if(kind==='len'||kind==='len2'||kind==='len3'){
      var sc=bimUnitDef().scale;
      for(i=0;i<nums.length;i++)nums[i]=nums[i]/sc;
    }
    return {v:nums};
  }
  /* One value, applied to the running drag rec (the global drag), however it was typed. keepSign is
     typing during a drag along an arrow: the gesture chose the direction and the number only
     replaces the distance, as V112 had it. A value with no gesture behind it keeps its own sign. */
  function bimGizmoApplyValue(rec,nums,keepSign){
    var kind=bimGizmoValueKind(rec);
    if(kind==='deg'){
      if(rec.rot){
        /* the read-out is Revit's sense; the model's own angle runs the other way about the vertical */
        bimGizmoRotateTo(-nums[0]*Math.PI/180);
        return {rot:true,ids:rec.ids,angle:rec.rotAngle,rotFailed:rec.rotFailed};
      }
      bimGizmoTiltTo(nums[0]*Math.PI/180);
      return {gk:'tilt',ids:rec.ids,tilt:rec.tiltAngle,failed:rec.gizFailed};
    }
    if(kind==='factor'){
      bimGizmoScaleTo(nums[0]);
      return {gk:'scale',ids:rec.ids,factor:rec.factor,failed:rec.gizFailed};
    }
    if(kind==='len'){
      bimGizmoAxisTo(keepSign?((rec.gizDist<0)?-1:1)*Math.abs(nums[0]):nums[0]);
      return {gk:'axis',ids:rec.ids,vec:rec.gizVec};
    }
    /* two or three lengths: along the square's own two axes, or the gizmo's X, Y and Z */
    var dirs=(kind==='len3'&&rec.fr)?[rec.fr.x,rec.fr.z,rec.fr.y]:[rec.a,rec.b],v=[0,0,0],i,k;
    for(i=0;i<dirs.length&&i<nums.length;i++)for(k=0;k<3;k++)v[k]+=dirs[i][k]*nums[i];
    rec.da=nums[0];rec.db=nums[1];rec.snapAt=null;rec.gizVec=v;
    bimGizmoSetPos(v);
    paint();saveSoon();
    return {gk:rec.gk,ids:rec.ids,vec:v};
  }
  /* __acad3dV123: whether a character goes into the value being typed -- digits and a point always,
     a minus at the start of a number, a comma between numbers only where the handle takes more than
     one. Every one of these characters is consumed while a drag listens, typed or not, so a stray
     minus cannot reach a shortcut; the claim below says the same. */
  function bimGizmoTypeChar(rec,k,buf){
    if(/^[0-9]$/.test(k)||k==='.')return true;
    if(k==='-')return !buf||buf.charAt(buf.length-1)===',';
    if(k!==',')return false;
    var n=bimGizmoValueCount(bimGizmoValueKind(rec));
    return n>1&&!!buf&&buf.charAt(buf.length-1)!==','&&buf.split(',').length<n;
  }
  function bimGizmoTypeKey(ev){
    var d=bimTypingDrag();
    if(!d)return false;
    var k=ev.key;
    /* __acad3dV112: Escape ends the gesture whatever is held down -- a Ctrl-drag copy and an
       Alt-drag of the pivot are exactly the drags most worth being able to call off, and testing
       the modifiers first meant neither of them could be. */
    if(k==='Escape'){bimGizmoCancelDrag();return true;}
    if(ev.ctrlKey||ev.metaKey||ev.altKey)return false;
    if(/^[0-9.,-]$/.test(k)){
      if(bimGizmoTypeChar(d,k,A3D_GIZ_TYPE.buf)){A3D_GIZ_TYPE.active=true;A3D_GIZ_TYPE.buf+=k;}
      paint();return true;
    }
    if(k==='Backspace'&&A3D_GIZ_TYPE.active){
      A3D_GIZ_TYPE.buf=A3D_GIZ_TYPE.buf.slice(0,-1);
      if(!A3D_GIZ_TYPE.buf)A3D_GIZ_TYPE.active=false;
      paint();return true;
    }
    if(k==='Enter'&&A3D_GIZ_TYPE.active)return bimGizmoTypedCommit();
    return false;
  }
  /* __acad3dV112: which keys a running gizmo drag is entitled to, asked by the workspace-era
     gates through __a3dWantsKey before they swallow one. Same predicate the handler above reads,
     so what is claimed and what is acted on cannot drift apart. */
  function bimGizmoWantsKey(ev){
    if(!bimTypingDrag())return false;
    var k=ev.key;
    if(k==='Escape')return true;
    if(ev.ctrlKey||ev.metaKey||ev.altKey)return false;
    return /^[0-9.,-]$/.test(k)||k==='Backspace'||k==='Enter';
  }
  function bimGizmoTypedCommit(){
    var d=bimTypingDrag(),text=A3D_GIZ_TYPE.buf;
    bimGizmoTypeClear();
    if(!d){paint();return true;}
    var p=bimGizmoParseValue(bimGizmoValueKind(d),text);
    if(p.error){a3dToast(p.error);paint();return true;}
    var summary=bimGizmoApplyValue(d,p.v,true);
    drag=null;
    bimGizmoEndDrag(summary);
    return true;
  }
""", 61)

# 5. coordinates typed while drawing are in the project's unit too -- the same fault, found by
#    looking for it (the second standing law)
rep("""     Returns a [x,z] ground point, or null when the string is not a coordinate -- the caller
     reports that rather than silently placing a point somewhere wrong. */
  function bimParseCoordInput(s,sk){
    if(!sk)return null;
    s=String(s||'').trim();
    if(!s)return null;
    var rel=false;""", """     Returns a [x,z] ground point, or null when the string is not a coordinate -- the caller
     reports that rather than silently placing a point somewhere wrong.

     __acad3dV123: lengths are typed in the project's unit, as AutoCAD reads them in drawing
     units. They were read as metres, so in a millimetre project 3000 drew a wall three kilometres
     long. An angle stays in degrees. */
  function bimParseCoordInput(s,sk){
    if(!sk)return null;
    s=String(s||'').trim();
    if(!s)return null;
    var rel=false,sc=bimUnitDef().scale;""")
rep("""      var t=b*Math.PI/180,vx=Math.cos(t)*a,vz=-Math.sin(t)*a;""",
    """      var t=b*Math.PI/180,vx=Math.cos(t)*a/sc,vz=-Math.sin(t)*a/sc;""")
rep("""      if(!isFinite(a)||!isFinite(b))return null;
      if(rel){if(!last)return null;return [last[0]+a,last[1]+b];}
      return [a,b];""", """      if(!isFinite(a)||!isFinite(b))return null;
      a/=sc;b/=sc;
      if(rel){if(!last)return null;return [last[0]+a,last[1]+b];}
      return [a,b];""")
rep("""    var d=parseFloat(s);
    if(!isFinite(d)||d<=0||!last)return null;
    var dir=sk.liveDir||[1,0];""", """    var d=parseFloat(s)/sc;
    if(!isFinite(d)||d<=0||!last)return null;
    var dir=sk.liveDir||[1,0];""")
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
