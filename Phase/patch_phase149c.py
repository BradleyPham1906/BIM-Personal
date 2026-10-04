"""patch_phase149c.py -- V149: Find an address on a phone.

The owner, on a phone: "when searching for address, it keep saying type an address or a place to
find. Basically useless button." Find read the address field, and the field kept nothing of its
own: a tap on Find takes the focus from the field, the keyboard goes, the screen changes size,
Properties is drawn again, and the field comes back empty -- so Find found nothing to look up.
What is typed is now kept as it is typed; the field is drawn with it, and Find falls back to it."""
NAME = 'patch_phase149c.py'
BASE = '9525be80653cedf945e9d8661814826fa4496877e247ee0fa7f7dd943dbe9599'
import hashlib, pathlib, sys
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')
raw = P.read_bytes()
h0 = hashlib.sha256(raw).hexdigest()
if h0 != BASE:
    sys.exit('ABORT: baseline %s, expected %s' % (h0, BASE))
t = raw.decode('utf-8')


def rep(old, new, n=1):
    global t
    c = t.count(old)
    if c != n:
        sys.exit('ABORT: %d occurrences, expected %d: %r' % (c, n, old[:90]))
    t = t.replace(old, new)


rep("""<input type="text" data-propmap="addr" value="'+bimEsc((A3D.site&&A3D.site.address)||'')+""",
    """<input type="text" data-propmap="addr" enterkeyhint="search" value="'+bimEsc(A3D_MAP_DRAFT!==null?A3D_MAP_DRAFT:((A3D.site&&A3D.site.address)||''))+""")
rep("""    if(a==='find'){var q=el.propsbody.querySelector('[data-propmap="addr"]');bimMapFind(q?q.value:'');return true;}""",
    """    if(a==='find'){var q=el.propsbody.querySelector('[data-propmap="addr"]'),qv=q?q.value:'';
      if(!/\\S/.test(qv)&&A3D_MAP_DRAFT)qv=A3D_MAP_DRAFT;   /* __acad3dV149c: the field drawn again empty under the tap */
      bimMapFind(qv);return true;}""")
rep("""  function bimMapFind(q){""", """  /* __acad3dV149c: the address as it is typed. Properties is drawn again when the screen changes
     size -- on a phone, when the keyboard goes as Find is tapped -- and a field that kept nothing of
     its own came back empty. */
  var A3D_MAP_DRAFT=null;
  function bimMapFind(q){""")
rep("""      var a=ev.target&&ev.target.closest?ev.target.closest('[data-propmap="addr"]'):null;
      if(!a||ev.key!=='Enter')return;""", """      var a=ev.target&&ev.target.closest?ev.target.closest('[data-propmap="addr"]'):null;
      if(!a||(ev.key!=='Enter'&&ev.keyCode!==13))return;""")
rep("""    if(el.propsbody)el.propsbody.addEventListener('keydown',function(ev){
      var a=ev.target&&ev.target.closest?ev.target.closest('[data-propmap="addr"]'):null;""",
    """    if(el.propsbody)el.propsbody.addEventListener('input',function(ev){   /* __acad3dV149c: kept as typed */
      var a=ev.target&&ev.target.closest?ev.target.closest('[data-propmap="addr"]'):null;
      if(a)A3D_MAP_DRAFT=a.value;
    });
    if(el.propsbody)el.propsbody.addEventListener('keydown',function(ev){
      var a=ev.target&&ev.target.closest?ev.target.closest('[data-propmap="addr"]'):null;""")
rep("""  window.__acad3dV149='typing16,""", """  window.__a3dMapDraft=function(){return A3D_MAP_DRAFT;};
  window.__acad3dV149='addrdraft,typing16,""")
out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
