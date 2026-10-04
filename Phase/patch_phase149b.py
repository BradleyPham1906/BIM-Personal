"""patch_phase149b.py -- V149: typing on a phone.

The owner, on a phone: "Cannot enter the find address on the phone. When typing something it
keeps zooming in then i have to zoom out ... This might happen across the app."

- iOS Safari zooms the page in on any field whose text is smaller than 16 px when it takes the
  focus, and does not zoom back out. Every field in the app was 11 to 13 px. On a touch screen
  every text field, number field, search, select and text area is now 16 px, so nothing zooms.
- The on-screen keyboard covered the bottom sheet the address field is in. The keyboard's height
  (from visualViewport) now lifts the Properties sheet and the left drawer above it, and the field
  tapped is scrolled into the middle of what is left."""
NAME = 'patch_phase149b.py'
BASE = 'bbb4cb220e6e7a837cba822cf35c56e7287b2bfec8e2d82208dfd3367cba5ebc'
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


rep("""@media(pointer:coarse){body.a3d-tier-overlay #a3d-rail .a3d-railbtn,body.a3d-tier-overlay #a3d-rail .a3d-paneltoggle{min-width:44px;min-height:44px}}""",
    """@media(pointer:coarse){body.a3d-tier-overlay #a3d-rail .a3d-railbtn,body.a3d-tier-overlay #a3d-rail .a3d-paneltoggle{min-width:44px;min-height:44px}}
/* __acad3dV149b: iOS zooms the page in on a field under 16 px when it takes the focus, and stays
   zoomed. On a touch screen every field is 16 px. */
@media(pointer:coarse){input:not([type=checkbox]):not([type=radio]):not([type=range]):not([type=color]):not([type=file]),select,textarea{font-size:16px!important}}
/* __acad3dV149b: the on-screen keyboard (--a3d-kb, its height) lifts what is fixed to the bottom */
body.a3d-tier-phone #a3d-leftpanel{bottom:calc(58px + env(safe-area-inset-bottom,0px) + var(--a3d-kb,0px))}
body.a3d-kb-up.a3d-tier-phone #a3d-leftpanel{bottom:var(--a3d-kb,0px)}
body.a3d-kb-up.a3d-props-right #a3d-right{bottom:var(--a3d-kb,0px)!important;max-height:calc(100% - var(--a3d-kb,0px) - var(--a3d-top-h,44px))}""")

rep("""body.a3d-tier-phone #a3d-leftpanel{left:0;bottom:calc(58px + env(safe-area-inset-bottom,0px));width:min(360px,88vw);""",
    """body.a3d-tier-phone #a3d-leftpanel{left:0;width:min(360px,88vw);""")   # its bottom is set below, with the keyboard's height

rep("""  window.__a3dShellApplyTier=function(){return bimShellApplyTier();};""",
    """  window.__a3dShellApplyTier=function(){return bimShellApplyTier();};
  window.__a3dKbFit=function(kb){return bimKbFit(kb);};   /* __acad3dV149b */""")

rep("""    window.addEventListener('resize',function(){bimShellApplyTier();});""",
    """    window.addEventListener('resize',function(){bimShellApplyTier();});
    /* __acad3dV149b: the keyboard, and the field it would cover */
    if(window.visualViewport){
      window.visualViewport.addEventListener('resize',function(){bimKbFit();});
      window.visualViewport.addEventListener('scroll',function(){bimKbFit();});
    }
    document.addEventListener('focusin',function(ev){
      var f=ev.target;
      if(!bimShellOverlay()||!f||!f.matches||!f.matches('input,select,textarea'))return;
      setTimeout(function(){bimKbFit();try{f.scrollIntoView({block:'center',inline:'nearest'});}catch(eSI){}},280);
    });
    document.addEventListener('focusout',function(){setTimeout(function(){bimKbFit();},300);});""")

rep("""  /* the phone's More: the rail's tools, over the tab bar */""",
    """  /* __acad3dV149b: the on-screen keyboard's height, from the visual viewport (or given, for a test):
     what is fixed to the bottom of the screen sits on it rather than under it */
  function bimKbFit(kb){
    var vv=window.visualViewport,b=document.body;
    if(kb===undefined)kb=vv?Math.max(0,window.innerHeight-vv.height-vv.offsetTop):0;
    kb=Math.round(+kb||0);
    if(kb<80)kb=0;   /* a browser's bar showing and hiding is not a keyboard */
    document.documentElement.style.setProperty('--a3d-kb',kb+'px');
    if(b)b.classList.toggle('a3d-kb-up',kb>0);
    return kb;
  }
  /* the phone's More: the rail's tools, over the tab bar */""")

rep("""  window.__acad3dV149='tierphone,""", """  window.__acad3dV149='typing16,keyboardlift,focusscroll,tierphone,""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
