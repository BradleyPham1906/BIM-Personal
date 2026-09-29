"""patch_phase129a.py -- V129: the keyboard shortcuts as a panel you can find your way around.

The owner, with a screenshot of the V128 sheet: "lets clean up these shortcuts stuff on the UI/UX
becauase it kinda hard to navigate and things not very clear", and, of the mockup researched from
Figma's shortcut panel, Google Docs' Ctrl+/ dialog and Linear's ? sheet: "thats actually what i want".

The sheet was a popover squeezed beside the rail: the rail's own tooltip covered its search box; its
list and its footer each claimed the height, so the last rows sat under the footer; and it mixed keys
with the grammar of typing a point (x,y, d<a, 0-9), which are not keys at all. It becomes a panel:

- centred over the drawing, with a title, the search box and a close button along the top;
- the categories down the left -- All, then each group, with how many each holds -- one click
  narrows the list to that group, and the search narrows within it;
- one list, one scroll: what a shortcut does on the left, the command it runs ("type UNDO") beside
  it, the keys in a column of their own on the right;
- typing a point is its own group, "Typing points", with a line saying when it applies;
- ? on the drawing opens it (Linear's and GitHub's key), as the rail's ? button and SHORTCUTS do.

The table is still A3D_KEYS and the handlers' own tables (V85, V122): the panel draws them."""
NAME = 'patch_phase129a.py'
BASE = '930fe35a405b105c1357b9ff46a3a5c2584b2db6657bb3bf1ca22874b8b3cfb1'
import hashlib, pathlib, sys
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')
raw = P.read_bytes()
h0 = hashlib.sha256(raw).hexdigest()
if h0 != BASE:
    sys.exit('ABORT: baseline %s, expected %s' % (h0, BASE))
t = raw.decode('utf-8')


def esc(s):
    return ''.join(ch if ord(ch) < 128 else '\\u%04x' % ord(ch) for ch in s)


def rep(old, new, n=1):
    global t
    new = esc(new)
    c = t.count(old)
    if c != n:
        sys.exit('ABORT: %d occurrences, expected %d: %r' % (c, n, old[:90]))
    t = t.replace(old, new)


# ---- the table: typing a point is its own group; ? is listed
rep("""      {keys:['U'],k:null,label:'Undo the last point'},
      {keys:['x,y'],k:null,label:'Absolute point. @x,y is relative to the last point; # forces absolute'},
      {keys:['d<a'],k:null,label:'Polar point: distance, then angle. @5<45 is relative'},
      {keys:['0-9'],k:null,label:'A bare length draws that far along the current direction'},
      {keys:['Arrows'],k:null,label:'Nudge the selected object'}
    ]},""", """      {keys:['U'],k:null,label:'Undo the last point'},
      {keys:['Arrows'],k:null,label:'Nudge the selected object'}
    ]},
    /* __acad3dV129: the grammar of a typed point is not a key: a group of its own, saying when */
    {grp:'Typing points',note:'While a tool is taking points, type a position instead of clicking, then press Enter.',rows:[
      {keys:['x,y'],k:null,label:'Absolute point. @x,y is relative to the last point; # forces absolute'},
      {keys:['d<a'],k:null,label:'Polar point: distance, then angle. @5<45 is relative'},
      {keys:['0-9'],k:null,label:'A bare length draws that far along the current direction'}
    ]},""")
rep("""      {keys:[A3D_MODKEY,'K'],k:null,label:'Command search, or just start typing a command'}""",
    """      {keys:[A3D_MODKEY,'K'],k:null,label:'Command search, or just start typing a command'},
      {keys:['?'],k:null,label:'This panel: the keyboard shortcuts'}   /* __acad3dV129 */""")

# ---- the panel
a = t.index('  function bimShortcutsHtml(){')
b = t.index('  function bimRailStackHtml(){')
assert t.count('  function bimShortcutsHtml(){') == 1 and 0 < b - a < 2200
t = t[:a] + esc(r"""  /* __acad3dV129: the shortcuts panel -- the categories on the left, one list, the keys on the right */
  function bimShortcutsHtml(){
    var groups=bimShortcutGroups(),g,r,i,j,k,total=0,nav='',list='';   /* __acad3dV122 */
    for(i=0;i<groups.length;i++){
      g=groups[i];total+=g.rows.length;
      nav+='<button type="button" class="a3d-rkcat" data-rkcat="'+bimEsc(g.grp)+'"><span>'+bimEsc(g.grp)+'</span><span class="a3d-rkn">'+g.rows.length+'</span></button>';
      list+='<div class="a3d-rkgrp" data-rkg="'+bimEsc(g.grp)+'">'+bimEsc(g.grp)+'</div>';
      if(g.note)list+='<div class="a3d-rkgnote" data-rkg="'+bimEsc(g.grp)+'">'+bimEsc(g.note)+'</div>';
      for(j=0;j<g.rows.length;j++){
        r=g.rows[j];
        list+='<div class="a3d-rkrow" data-rkg="'+bimEsc(g.grp)+'" data-rkhay="'+bimEsc((r.keys.join(' ')+' '+r.keys.join('+')+' '+r.label+' '+g.grp+' '+(r.cmd||'')).toLowerCase())+'">'+
          '<span class="a3d-rklab">'+bimEsc(r.label)+'</span>'+
          '<span class="a3d-rkcmd">'+(r.cmd?'type '+bimEsc(r.cmd):'')+'</span><span class="a3d-rkkeys">';
        for(k=0;k<r.keys.length;k++){
          if(k)list+='<span class="a3d-rkplus">'+(r.alt?'/':'+')+'</span>';   /* __acad3dV122: a slash between alternatives */
          list+='<kbd>'+bimEsc(r.keys[k])+'</kbd>';
        }
        list+='</span></div>';
      }
    }
    return '<div class="a3d-rkhead"><h2 class="a3d-rktitle">Keyboard shortcuts</h2>'+
      '<input type="search" class="a3d-rkfind" placeholder="Search by what it does, or a key: undo, ctrl z, F8" aria-label="Search the keyboard shortcuts" autocomplete="off" spellcheck="false">'+   /* __acad3dV128 */
      '<button type="button" class="a3d-rkclose" data-rkclose aria-label="Close the keyboard shortcuts">×</button></div>'+
      '<div class="a3d-rkbody"><nav class="a3d-rknav" aria-label="Shortcut categories">'+
      '<button type="button" class="a3d-rkcat on" data-rkcat="all" aria-pressed="true"><span>All shortcuts</span><span class="a3d-rkn">'+total+'</span></button>'+nav+
      '<div class="a3d-rknote">Every command, its alias and its keys: <kbd>'+bimEsc(A3D_MODKEY)+'</kbd>+<kbd>K</kbd>, or start typing a command on the drawing.</div></nav>'+
      '<div class="a3d-rukeys">'+list+'<div class="a3d-rkempty" hidden>No shortcut matches. Try what it does, like “snap”, or a key, like “F8”.</div></div></div>';
  }
""") + t[b:]

# ---- the category narrows the list, as the search does
rep("""  function bimFilterShortcuts(p,q){
    var norm=function(s){return String(s).toLowerCase().replace(/cmd|ctrl|control|meta|\\u2318/g,'mod');};""",
    """  function bimFilterShortcuts(p,q){
    var norm=function(s){return String(s).toLowerCase().replace(/cmd|ctrl|control|meta|\\u2318/g,'mod');};
    var cat=p.getAttribute('data-rkcat')||'all',note=null;   /* __acad3dV129: the category chosen on the left */""")
rep("""      if(e.classList.contains('a3d-rkgrp')){if(grp)grp.hidden=!any;grp=e;any=false;continue;}
      if(!e.classList.contains('a3d-rkrow'))continue;
      var hay=norm(e.getAttribute('data-rkhay')||''),ok=words.every(function(w){return hay.indexOf(w)>=0;});""",
    """      if(e.classList.contains('a3d-rkgrp')){if(grp){grp.hidden=!any;if(note)note.hidden=!any;}grp=e;note=null;any=false;continue;}
      if(e.classList.contains('a3d-rkgnote')){note=e;continue;}
      if(!e.classList.contains('a3d-rkrow'))continue;
      var hay=norm(e.getAttribute('data-rkhay')||''),ok=(cat==='all'||e.getAttribute('data-rkg')===cat)&&words.every(function(w){return hay.indexOf(w)>=0;});""")
rep("""    if(grp)grp.hidden=!any;
    var em=p.querySelector('.a3d-rkempty');if(em)em.hidden=shown>0;""", """    if(grp){grp.hidden=!any;if(note)note.hidden=!any;}
    var em=p.querySelector('.a3d-rkempty');if(em)em.hidden=shown>0;""")

# ---- centred, and the categories and the close button work
rep("""    p.setAttribute('data-for',id);
    p.innerHTML=bimRailMenuHtml(id);""", """    p.setAttribute('data-for',id);
    p.classList.toggle('a3d-rksheet',id==='help');   /* __acad3dV129: the shortcuts are a panel, centred */
    p.setAttribute('data-rkcat','all');
    p.innerHTML=bimRailMenuHtml(id);""")
rep("""    if(top<8)top=8;
    p.style.left=Math.round(left)+'px';
    p.style.top=Math.round(top)+'px';
    var rkf=id==='help'?p.querySelector('.a3d-rkfind'):null;""", """    if(top<8)top=8;
    if(id==='help'){left=Math.max(8,(window.innerWidth-pw)/2);top=Math.max(8,(window.innerHeight-ph)/2);}   /* __acad3dV129 */
    p.style.left=Math.round(left)+'px';
    p.style.top=Math.round(top)+'px';
    var rkf=id==='help'?p.querySelector('.a3d-rkfind'):null;""")
rep("""      p.addEventListener('click',function(ev){
        var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3druitem]'):null;
        if(b){bimRailAction(b.getAttribute('data-a3druitem'));return;}""", """      p.addEventListener('click',function(ev){
        var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3druitem]'):null;
        if(b){bimRailAction(b.getAttribute('data-a3druitem'));return;}
        /* __acad3dV129: the shortcuts panel's categories and its close button */
        var rc=ev.target&&ev.target.closest?ev.target.closest('.a3d-rkcat[data-rkcat]'):null;
        if(rc){
          var cats=p.querySelectorAll('[data-rkcat]'),ci;
          for(ci=0;ci<cats.length;ci++){var on=cats[ci]===rc;cats[ci].classList.toggle('on',on);cats[ci].setAttribute('aria-pressed',on?'true':'false');}
          p.setAttribute('data-rkcat',rc.getAttribute('data-rkcat'));
          var rf=p.querySelector('.a3d-rkfind');
          bimFilterShortcuts(p,rf?rf.value:'');
          var lst=p.querySelector('.a3d-rukeys');if(lst)lst.scrollTop=0;
          /* a click leaves the typing where it was, in the search box; a key press (Tab, Enter) keeps its place */
          if(ev.detail&&rf){try{rf.focus({preventScroll:true});}catch(eRf){}}
          return;
        }
        if(ev.target&&ev.target.closest&&ev.target.closest('[data-rkclose]')){bimCloseRailPop();return;}""")
rep("""    shortcuts:function(){
      var b=document.querySelector('[data-a3drumenu="help"]');""", """    shortcuts:function(){
      var hp=document.getElementById('a3d-rupop');   /* __acad3dV129: already open, it stays open */
      if(hp&&hp.classList.contains('open')&&hp.getAttribute('data-for')==='help')return;
      var b=document.querySelector('[data-a3drumenu="help"]');""")

# ---- ? on the drawing opens it (the shell's key listener, beside type-anywhere)
rep("""      if(!pal.classList.contains('show')&&!e.defaultPrevented&&!e.isComposing&&window.__a3dTypeAnywhere&&window.__a3dTypeAnywhere(e)){
        e.preventDefault();openPal(e.key);""", """      if(!pal.classList.contains('show')&&!e.defaultPrevented&&!e.isComposing&&window.__a3dTypeAnywhere&&window.__a3dTypeAnywhere(e)){
        /* __acad3dV129: ? is the keyboard shortcuts panel (Linear's and GitHub's key) */
        if(e.key==='?'&&window.__a3dRunCmd){e.preventDefault();window.__a3dRunCmd('shortcuts');return;}
        e.preventDefault();openPal(e.key);""")

# ---- the look
rep(""".a3d-rukeys [hidden]{display:none!important}""", """.a3d-rukeys [hidden]{display:none!important}
#a3d-rupop.a3d-rksheet{width:min(880px,calc(100vw - 32px));height:min(600px,calc(100vh - 64px));padding:0;display:none;flex-direction:column;overflow:hidden;border-radius:12px;box-shadow:0 18px 50px rgba(0,0,0,.55)}
#a3d-rupop.a3d-rksheet.open{display:flex}
.a3d-rkhead{display:flex;align-items:center;gap:14px;padding:14px 16px;border-bottom:1px solid #343a41;flex:0 0 auto}
.a3d-rktitle{margin:0;font-size:15px;font-weight:600;color:#e6eaef;flex:0 0 auto}
#a3d-rupop.a3d-rksheet .a3d-rkfind{flex:1 1 auto;width:auto;margin:0;height:34px;font-size:13px;padding:0 12px;border-radius:8px}
.a3d-rkclose{width:34px;height:34px;flex:0 0 auto;border-radius:8px;border:1px solid #3a4048;background:transparent;color:#aab2bd;font:inherit;font-size:18px;line-height:1;cursor:pointer}
.a3d-rkclose:hover{background:#2f353c;color:#fff}
.a3d-rkbody{display:flex;flex:1 1 auto;min-height:0}
.a3d-rknav{width:190px;flex:0 0 auto;display:flex;flex-direction:column;gap:2px;padding:10px 8px;border-right:1px solid #343a41;overflow-y:auto;box-sizing:border-box}
.a3d-rkcat{display:flex;justify-content:space-between;align-items:center;width:100%;min-height:34px;padding:0 10px;border:0;border-radius:7px;background:transparent;color:#c3cad2;font:inherit;font-size:13px;cursor:pointer;text-align:left}
.a3d-rkcat:hover{background:#2a2f35;color:#fff}
.a3d-rkcat.on{background:#2c477d;color:#fff}
.a3d-rkn{font-size:11.5px;color:#8b949e}.a3d-rkcat.on .a3d-rkn{color:#c9dcff}
#a3d-rupop.a3d-rksheet .a3d-rknote{margin-top:auto;border-top:0;padding:10px 6px 2px;font-size:11.5px;line-height:1.5}
#a3d-rupop.a3d-rksheet .a3d-rukeys{flex:1 1 auto;min-width:0;max-height:none;overflow-y:auto;padding:4px 16px 16px}
#a3d-rupop.a3d-rksheet .a3d-rkgrp{font-size:11px;padding:16px 8px 6px}
.a3d-rkgnote{padding:0 8px 6px;font-size:12px;line-height:1.5;color:#9aa3ad}
#a3d-rupop.a3d-rksheet .a3d-rkrow{display:grid;grid-template-columns:minmax(0,1fr) auto minmax(90px,auto);align-items:center;gap:12px;padding:7px 8px;border-bottom:1px solid #2c3137;border-radius:0}
#a3d-rupop.a3d-rksheet .a3d-rklab{font-size:13px;color:#dfe4ea}
.a3d-rkcmd{font:500 11.5px/1 'IBM Plex Mono',ui-monospace,Menlo,monospace;color:#8fb8ff}
#a3d-rupop.a3d-rksheet .a3d-rkkeys{flex:none;justify-content:flex-end}
#a3d-rupop.a3d-rksheet .a3d-rkkeys kbd{font-size:11px;padding:4px 7px}
body.light-theme .a3d-rktitle{color:#202124}body.light-theme .a3d-rkcat{color:#30343b}body.light-theme .a3d-rkcat.on{background:#dbe7ff;color:#12305f}body.light-theme .a3d-rkcmd{color:#1f5fbf}""")


out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
