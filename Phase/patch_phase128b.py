"""patch_phase128b.py -- V128: the command search, and a command line that listens everywhere.

The palette becomes the search over the catalogue (128a):

- Each row shows the command's name, with the letters that matched in bold; what it does; where it
  sits on the ribbon; its alias; its keyboard shortcut. The shortcut on every row is what teaches
  the shortcuts (VS Code, Linear); the ribbon place teaches where the button is (Blender's path).
- Opened empty, it lists the commands used most recently first, then every command, with the count.
  Typing narrows it; a one-letter typo is offered last, under "Did you mean".
- ? searches the keyboard shortcuts instead -- by what they do or by the key: "?ctrl", "?f8".
- A command that cannot run here says why in its row ("works on the model, not a sheet").
- Tab and Shift+Tab cycle the rows, as AutoCAD's command line does; the arrows move; Enter runs.
- The ARIA combobox pattern: the input owns the focus and names the active row.

And AutoCAD's type-anywhere: with no field focused and nothing listening for the key -- no tool
taking points, no dialog, no held face -- a letter typed on the drawing opens the search with that
letter in it. L, Enter draws a line; WA, Enter a wall. Ctrl+K still opens it empty."""
NAME = 'patch_phase128b.py'
BASE = '08ecbf851e362609aaab0276f4a75370421cec9aef9071143d9539e4b3ac2463'
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


# ---- the palette, replaced whole: the span is checked by its hash, so a changed original aborts
A0, B0 = '  function buildPalette(){', '  buildPalette();\n'
assert t.count(A0) == 1 and t.count(B0) == 1
a = t.index(A0); b = t.index(B0) + len(B0)
OLD_SHA = '703043086827e81a11507410e1d6fbe6da04ee7988502521d272d9fa13d4dbb1'
if hashlib.sha256(t[a:b].encode('utf-8')).hexdigest() != OLD_SHA:
    sys.exit('ABORT: the palette block is not the one this patch replaces')
NEW = r"""  /* __acad3dV128: the command search. The engine owns the catalogue (every command and every ribbon
     tool, window.__a3dCommandSearch) and runs an entry (window.__a3dCommandRun); this draws it. */
  window.__wsRegistry=REGISTRY;
  function buildPalette(){
    var pal=document.createElement('div'); pal.id='a3d-cmdpal';
    pal.setAttribute('role','dialog'); pal.setAttribute('aria-label','Command search');
    pal.innerHTML='<div class="a3d-cmdinput"><span aria-hidden="true">&gt;_</span><input placeholder="Search commands, tools and shortcuts — or type a command: L, WA, TRIM" aria-label="Search commands, tools and shortcuts" role="combobox" aria-expanded="true" aria-controls="a3d-cmdlist" aria-autocomplete="list" autocomplete="off" spellcheck="false"></div>'+
      '<div class="a3d-cmdresults" id="a3d-cmdlist" role="listbox" aria-label="Commands"></div>'+
      '<div class="a3d-cmdfoot"><span><kbd>↑</kbd><kbd>↓</kbd> or <kbd>Tab</kbd> choose</span><span><kbd>Enter</kbd> run</span>'+
      '<span><kbd>?</kbd> keyboard shortcuts</span><span><kbd>Esc</kbd> close</span><span class="a3d-cmdcount"></span></div>';
    document.body.appendChild(pal);
    var input=pal.querySelector('input'), results=pal.querySelector('.a3d-cmdresults'), count=pal.querySelector('.a3d-cmdcount');
    var rows=[], active=0;
    function escH(s){return String(s==null?'':s).replace(/[&<>"]/g,function(ch){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[ch];});}
    function nameHtml(c){
      var n=c.name,on={},h='',i;
      if(!c.hl||!c.hl.length)return escH(n);
      for(i=0;i<c.hl.length;i++)on[c.hl[i]]=1;
      for(i=0;i<n.length;i++)h+=on[i]?'<b class="a3d-cmdhl">'+escH(n.charAt(i))+'</b>':escH(n.charAt(i));
      return h;
    }
    function kbdHtml(k,alt){
      return (k&&k.length)?'<span class="a3d-cmdkbd">'+k.map(function(x){return '<kbd>'+escH(x)+'</kbd>';}).join(alt?'<i>/</i>':'<i>+</i>')+'</span>':'';
    }
    function rowHtml(c,i){
      var meta='';
      if(c.off)meta+='<span class="a3d-cmdoff">'+escH(c.off)+'</span>';
      else if(c.where&&c.where.length)meta+='<span class="a3d-cmdwhere" title="On the ribbon: '+escH(c.where.join('; '))+'">'+escH(c.where[0])+(c.where.length>1?' +'+(c.where.length-1):'')+'</span>';
      if(c.aliases&&c.aliases.length)meta+='<span class="a3d-cmdkey" title="Also typed as '+escH(c.aliases.join(', '))+'">'+escH(c.aliases[0])+'</span>';
      meta+=kbdHtml(c.keys);
      return '<div class="a3d-cmdrow'+(c.off?' a3d-cmdrowoff':'')+'" role="option" id="a3d-cmdopt-'+i+'" aria-selected="false" data-idx="'+i+'">'+
        '<span class="a3d-cmdmain"><span class="a3d-cmdname">'+nameHtml(c)+'</span><span class="a3d-cmddesc"> — '+escH(c.desc)+'</span></span>'+
        '<span class="a3d-cmdmeta">'+meta+'</span></div>';
    }
    /* ? -- the keyboard shortcuts, searched by what they do or by the key itself */
    function keyRows(q){
      var g=window.__a3dShortcuts?window.__a3dShortcuts():[],out=[],norm=function(s){return String(s).toLowerCase().replace(/cmd|ctrl|control|meta|⌘/g,'mod');};
      var words=norm(q).split(/\s+/).filter(function(w){return !!w;});
      g.forEach(function(grp){grp.rows.forEach(function(r){
        var hay=norm(r.keys.join(' ')+' '+r.keys.join('+')+' '+r.label+' '+grp.grp);
        if(words.every(function(w){return hay.indexOf(w)>=0;}))out.push({kind:'key',keys:r.keys,alt:!!r.alt,desc:r.label,grp:grp.grp,cmd:r.cmd||null});
      });});
      return out;
    }
    function keyRowHtml(c,i){
      return '<div class="a3d-cmdrow a3d-cmdkeyrow" role="option" id="a3d-cmdopt-'+i+'" aria-selected="false" data-idx="'+i+'">'+
        '<span class="a3d-cmdmain"><span class="a3d-cmdname">'+kbdHtml(c.keys,c.alt)+'</span><span class="a3d-cmddesc"> — '+escH(c.desc)+'</span></span>'+
        '<span class="a3d-cmdmeta"><span class="a3d-cmdwhere">'+escH(c.grp)+'</span>'+(c.cmd?'<span class="a3d-cmdkey">'+escH(c.cmd)+'</span>':'')+'</span></div>';
    }
    function draw(){
      var q=input.value.trim(),h='',i;
      if(q.charAt(0)==='?'){
        rows=keyRows(q.slice(1).trim());
        if(rows.length)h+='<div class="a3d-cmdhd">Keyboard shortcuts</div>';
        for(i=0;i<rows.length;i++)h+=keyRowHtml(rows[i],i);
        count.textContent=rows.length+' shortcut'+(rows.length===1?'':'s');
        if(!rows.length)h='<div class="a3d-cmdrow a3d-cmdnone">No matching shortcut</div>';
      }else{
        var res=window.__a3dCommandSearch?window.__a3dCommandSearch(q,q?80:0):[];
        var rec=(!q&&window.__a3dCommandRecent)?window.__a3dCommandRecent(5):[],seen={},typoAt=-1;
        rec.forEach(function(c){seen[c.id]=1;});
        var rest=res.filter(function(c){return !seen[c.id];});
        rows=rec.concat(rest);
        for(i=0;i<rows.length;i++){
          if(i===0&&rec.length)h+='<div class="a3d-cmdhd">Recently used</div>';
          if(i===rec.length&&rec.length)h+='<div class="a3d-cmdhd">All commands</div>';
          if(rows[i].typo&&typoAt<0){typoAt=i;h+='<div class="a3d-cmdhd">Did you mean</div>';}
          h+=rowHtml(rows[i],i);
        }
        count.textContent=q?(res.length+' match'+(res.length===1?'':'es')):(res.length+' commands');
        if(!rows.length)h='<div class="a3d-cmdrow a3d-cmdnone">No matching command — try fewer letters, or ? for the keyboard shortcuts</div>';
      }
      results.innerHTML=h;
      active=0;
      highlight();
    }
    function highlight(){
      var els=results.querySelectorAll('.a3d-cmdrow[data-idx]'),i,cur=null;
      for(i=0;i<els.length;i++){
        var on=(+els[i].getAttribute('data-idx')===active);
        els[i].classList.toggle('active',on);els[i].setAttribute('aria-selected',on?'true':'false');
        if(on)cur=els[i];
      }
      if(cur){input.setAttribute('aria-activedescendant',cur.id);try{cur.scrollIntoView({block:'nearest'});}catch(eS){}}
      else input.removeAttribute('aria-activedescendant');
    }
    /* __acad3dV86: hand the keyboard back to the drawing.

       The BIM key chain begins "if the event target is an INPUT, return", so leaving focus in
       the palette's hidden input meant every keystroke AFTER a command was swallowed: the tool
       started, and then typing a coordinate, pressing C to close or pressing Escape to cancel
       all did nothing at all. Measured: activeElement was INPUT and the typing buffer stayed
       empty. A command line that keeps the keyboard after it runs is not a command line. */
    function closePal(){
      pal.classList.remove('show');
      try{input.blur();}catch(eB){}
      try{if(document.activeElement===input)document.body.focus();}catch(eF){}
    }
    function runIdx(i){
      var c=rows[i]; if(!c) return;
      closePal();
      if(c.kind==='key'){
        if(c.cmd&&window.__a3dCommandRun){if(!window.__a3dCommandRun('cmd:'+c.cmd)&&window.__a3dToast)window.__a3dToast(c.cmd+' is not available here');}
        else if(window.__a3dToast)window.__a3dToast('Press '+c.keys.join(c.alt?' or ':'+')+' on the drawing: '+c.desc);
        return;
      }
      /* A command that cannot run says so, instead of closing the palette over nothing. */
      var ok=window.__a3dCommandRun?window.__a3dCommandRun(c.id):runCadAct(c.cad);
      if(!ok&&window.__a3dToast)window.__a3dToast(c.name+' is not available here'+(c.off?': '+c.off:''));   /* __acad3dV120 */
    }
    input.addEventListener('input',draw);
    input.addEventListener('keydown',function(e){
      var n=rows.length;
      if(e.key==='ArrowDown'){active=Math.min(n-1,active+1);highlight();e.preventDefault();}
      else if(e.key==='ArrowUp'){active=Math.max(0,active-1);highlight();e.preventDefault();}
      else if(e.key==='Tab'){if(n){active=(active+(e.shiftKey?n-1:1))%n;highlight();}e.preventDefault();}   /* AutoCAD: Tab cycles */
      else if(e.key==='Enter'){runIdx(active);e.preventDefault();e.stopPropagation();}
      else if(e.key==='Escape'){closePal();}
    });
    results.addEventListener('pointerdown',function(e){
      var row=e.target.closest('.a3d-cmdrow'); if(!row||row.dataset.idx===undefined) return;
      e.preventDefault(); e.stopPropagation();
      runIdx(+row.dataset.idx);
    });
    draw();
    /* __acad3dV113: Ctrl+K opens the palette; Escape, or a pointer outside it, closes it.
       window.openPalette and window.closePalette are what the suites drive. */
    function openPal(initial){
      pal.classList.add('show');
      input.value=(typeof initial==='string')?initial:'';
      draw();
      /* the caret goes in at once, so the letters typed after the first land in the search too */
      try{input.focus();input.setSelectionRange(input.value.length,input.value.length);}catch(eO){}
      setTimeout(function(){try{if(pal.classList.contains('show')&&document.activeElement!==input)input.focus();}catch(eO2){}},20);
    }
    window.openPalette=openPal;
    window.closePalette=closePal;
    document.addEventListener('keydown',function(e){
      if((e.metaKey||e.ctrlKey)&&e.key&&e.key.toLowerCase()==='k'){e.preventDefault();openPal();return;}
      if(e.key==='Escape'&&pal.classList.contains('show')){closePal();return;}
      /* __acad3dV128: AutoCAD's command line takes a letter typed on the drawing. The engine's
         key chain has already run (window, capture) and has not claimed the key; the engine says
         whether anything else is listening for it -- a tool, a dialog, a held face -- and only
         when nothing is does the letter open the search. */
      if(!pal.classList.contains('show')&&!e.defaultPrevented&&!e.isComposing&&window.__a3dTypeAnywhere&&window.__a3dTypeAnywhere(e)){
        e.preventDefault();openPal(e.key);
      }
    });
    document.addEventListener('pointerdown',function(e){
      if(!pal.classList.contains('show'))return;
      if(!e.target.closest('#a3d-cmdpal'))closePal();
    },true);
    window.__wsPaletteCount=REGISTRY.length;
    window.__wsPaletteOwner='acadWorkspaceV1';
  }
  buildPalette();
"""
t = t[:a] + esc(NEW) + t[b:]

# ---- the look: wider, room for the ribbon place and the keys, and the same in the light theme
rep("""#a3d-cmdpal{position:fixed;left:50%;top:88px;transform:translateX(-50%) translateY(-10px);width:min(430px,calc(100vw - 32px));""",
    """#a3d-cmdpal{position:fixed;left:50%;top:88px;transform:translateX(-50%) translateY(-10px);width:min(680px,calc(100vw - 32px));""")
rep("""body.light-theme #a3d-cmdpal .a3d-cmdrow{color:#30343b}""", """body.light-theme #a3d-cmdpal .a3d-cmdrow{color:#30343b}
/* __acad3dV128: the command search's rows -- name, what it does, where it is, its alias and keys */
#a3d-cmdpal .a3d-cmdresults{max-height:min(52vh,480px);overflow-y:auto;overscroll-behavior:contain}
#a3d-cmdpal .a3d-cmdrow{gap:12px;padding:7px 10px}
#a3d-cmdpal .a3d-cmdmain{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
#a3d-cmdpal .a3d-cmddesc{opacity:.5;font-weight:500}
#a3d-cmdpal .a3d-cmdhl{color:#56ffa6;font-weight:850}
#a3d-cmdpal .a3d-cmdmeta{display:flex;align-items:center;gap:8px;flex:0 0 auto;font-weight:600}
#a3d-cmdpal .a3d-cmdwhere{font-size:10.5px;color:rgba(196,211,237,.5);max-width:190px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
#a3d-cmdpal .a3d-cmdoff{font-size:10.5px;color:#e8a87c}
#a3d-cmdpal .a3d-cmdrowoff .a3d-cmdname{opacity:.6}
#a3d-cmdpal kbd{font:inherit;font-size:10.5px;font-weight:700;padding:1px 5px;border-radius:4px;border:1px solid rgba(196,211,237,.28);color:rgba(196,211,237,.85);background:rgba(255,255,255,.04)}
#a3d-cmdpal .a3d-cmdkbd i{font-style:normal;opacity:.5;margin:0 2px;font-size:10px}
#a3d-cmdpal .a3d-cmdhd{font-size:10px;letter-spacing:.07em;text-transform:uppercase;color:rgba(196,211,237,.45);padding:8px 10px 3px;font-weight:800}
#a3d-cmdpal .a3d-cmdnone{cursor:default;font-weight:600}
#a3d-cmdpal .a3d-cmdfoot{display:flex;gap:14px;flex-wrap:wrap;align-items:center;padding:8px 6px 2px;border-top:1px solid rgba(196,211,237,.1);margin-top:6px;font-size:10.5px;color:rgba(196,211,237,.5)}
#a3d-cmdpal .a3d-cmdfoot kbd{margin-right:2px}
#a3d-cmdpal .a3d-cmdcount{margin-left:auto}
body.light-theme #a3d-cmdpal .a3d-cmdhl{color:#0f8a4c}
body.light-theme #a3d-cmdpal .a3d-cmdwhere,body.light-theme #a3d-cmdpal .a3d-cmdhd,body.light-theme #a3d-cmdpal .a3d-cmdfoot{color:rgba(32,33,36,.55)}
body.light-theme #a3d-cmdpal kbd{color:#30343b;border-color:rgba(0,0,0,.18);background:rgba(0,0,0,.03)}
body.light-theme #a3d-cmdpal .a3d-cmdoff{color:#b45a1c}
body.light-theme #a3d-cmdpal .a3d-cmdfoot{border-top-color:rgba(0,0,0,.08)}""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
