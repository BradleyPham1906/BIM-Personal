"""patch_phase130c.py -- V130: what the More menus leave behind, removed.

The dock's per-group More menus, their caret, the second row and the group labels are gone (130a).
What only they used goes with them, as V120's audit asks: the pop-up and caret rules, the dock
header's rules, the greyed-item class the menus alone carried, the row layout (a3drDockRows), the
menus' open/close code and their geometry hook. __a3dHitSizes measures All tools, the one control
that opens the rest, where it measured the caret."""
NAME = 'patch_phase130c.py'
BASE = '6fff1ac80086101c377f6ac0a949f6fb129fcc9d236092d890431c0891c5303c'
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


# ---- styles only the More menus, the caret, the old header and the group labels matched
for rule in [".a3d-dgtools{display:flex;align-items:center;gap:1px}\n",
             ".a3d-dglbl{font-size:9px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:#7d8590;line-height:1;white-space:nowrap}\n",
             "#a3d-dock.a3d-docklabels .a3d-dcar{width:40px;height:38px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;color:#aab2bd}\n",
             "#a3d-dock.a3d-docklabels .a3d-dcar svg{width:16px;height:16px}\n",
             ".a3d-dockhead .a3d-dockgrp{flex-direction:row;gap:6px;width:100%}\n",
             ".a3d-dcar:hover{color:#fff;background:#2f353c}\n",
             ".a3d-dockpop.open{display:block}\n",
             ".a3d-dockpoph{padding:7px 7px 3px;font-size:9.5px;font-weight:800;letter-spacing:.06em;color:#8d9196;text-transform:uppercase}\n",
             ".a3d-dockitem:hover{background:#2b3138}\n",
             ".a3d-dockitem svg{width:15px;height:15px;flex:0 0 auto;color:#9aa3ad}\n",
             ".a3d-dockhead{padding-bottom:2px;border-bottom:1px solid #30353c;margin-bottom:2px}\n",
             ".a3dr-dis{opacity:0.32;cursor:not-allowed}\n",
             ".a3dr-dis:hover{background:transparent}\n",
             ".a3d-dcar{height:34px}\n"]:
    rep(rule, "")
def drop_line(prefix):
    global t
    a = t.find(prefix)
    if a < 0 or t.count(prefix) != 1:
        sys.exit('ABORT: line %r found %d times' % (prefix[:50], t.count(prefix)))
    b = t.index('\n', a) + 1
    t = t[:a] + t[b:]
for pre in (".a3d-dcar{width:22px;height:32px;", ".a3d-dockpop{display:none;position:fixed;", ".a3d-dockitem{display:flex;align-items:center;gap:8px;"):
    drop_line(pre)
rep(".a3d-dbtn:hover .a3d-dblbl,.a3d-dcar:hover .a3d-dblbl{color:#fff}", ".a3d-dbtn:hover .a3d-dblbl,.a3d-dall:hover .a3d-dblbl{color:#fff}")
rep(".a3d-dbtn:focus-visible,.a3d-dcar:focus-visible,.a3d-dsearchpill:focus-visible{", ".a3d-dbtn:focus-visible,.a3d-dsearchpill:focus-visible{")

# ---- the row layout
rep("""  /* Rows are computed, not listed. Up to five groups per row, balanced so two rows never read
     as one long row with a stub under it; more than ten groups simply adds rows. */
  function a3drDockRows(tabs){
    var n=tabs.length;
    if(n<=3)return [tabs.slice()];
    var rows=Math.ceil(n/5),per=Math.ceil(n/rows),out=[],i;
    for(i=0;i<n;i+=per)out.push(tabs.slice(i,i+per));
    return out;
  }
""", "")

# ---- the menus' open and close
rep("""  function bimCloseDockPops(){
    var all=document.querySelectorAll('.a3d-dockpop.open'),i;
    for(i=0;i<all.length;i++)all[i].classList.remove('open');
  }
""", "")
a = t.index("      var car=ev.target&&ev.target.closest?ev.target.closest('[data-dockmore]'):null;")
b = t.index("      /* __acad3dV130: All tools opens the panel */")
t = t[:a] + t[b:]
rep("""ev.target.closest('#a3d-dall')){ev.stopPropagation();bimCloseDockPops();bimOpenToolsPanel();return;}""",
    """ev.target.closest('#a3d-dall')){ev.stopPropagation();bimOpenToolsPanel();return;}""")
rep("""        ev.stopPropagation();
        bimCloseDockPops();
        if(window.openPalette)window.openPalette();
        return;
      }
      /* Any other click inside the dock is a command; the document dispatcher runs it, and the
         popover closes so the drawing is not left behind a menu. */
      bimCloseDockPops();
    });
    document.addEventListener('click',function(ev){
      if(ev.target&&ev.target.closest&&ev.target.closest('#a3d-dock'))return;
      bimCloseDockPops();
    });""", """        ev.stopPropagation();
        if(window.openPalette)window.openPalette();
        return;
      }
      /* Any other click inside the dock is a command; the document dispatcher runs it. */
    });""")
rep("""    window.addEventListener('resize',bimCloseDockPops);
""", "")

# ---- the More buttons' tooltip: nothing carries a __more: spec any more
rep("""    if(spec.indexOf('__more:')===0)return {name:'More',keys:null,desc:'All '+spec.slice(7)+' tools',type:[],where:''};
""", "")

# ---- hooks
rep("""      buttons:grps[i].querySelectorAll('.a3d-dbtn').length,
      hasCaret:!!grps[i].querySelector('.a3d-dcar')});""", """      buttons:grps[i].querySelectorAll('.a3d-dbtn').length});""")
a = t.index("  window.__a3dDockPopGeom=function(id){")
b = t.index("  /* __acad3dV69: material test surface.")
t = t[:a] + t[b:]
rep("""      dockCaret:box('#a3d-dock .a3d-dcar'),""", """      dockAll:box('#a3d-dock .a3d-dall'),   /* __acad3dV130: the control that opens the rest */""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
