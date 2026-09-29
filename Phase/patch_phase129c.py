"""patch_phase129c.py -- V129: test hooks and the marker."""
NAME = 'patch_phase129c.py'
BASE = '1ce04e5c7e356d79ff21ec69d93503ca4cf202dcd0c7a39ef7bf8716e43c0e5d'
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


rep("""  window.__acad3dV128='commandcatalog,""", """  /* __acad3dV129: the shortcuts panel and the dock's names */
  window.__a3dDockTip=function(spec){return bimDockTipData(spec);};
  window.__a3dDockTipShown=function(){var e=document.getElementById('a3d-tip');return e&&e.classList.contains('show')?e.textContent:null;};
  window.__a3dDockLabels=function(on){if(on!==undefined)bimSetDockLabels(!!on);return bimDockLabelsOn();};
  window.__acad3dV129='shortcutspanel,centred,categories,keysright,typingpoints,questionkey,docknames,grouplabels,'+
    'docktooltips,tooltipdelay,tooltipfocus,morebutton,searchpill,appearancetoggle';
  window.__acad3dV128='commandcatalog,""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
