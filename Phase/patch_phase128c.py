"""patch_phase128c.py -- V128: one search, and every place that shows a command teaches its name.

- The dock's magnifier opened a search of its own, over the ribbon's tools only. It now opens THE
  search -- the same one Ctrl+K and typing on the drawing open -- so there is one place to look.
- Every ribbon button's tooltip ends with the command to type for it: "Wall . Architecture . type
  WALL or WA" (Revit and AutoCAD show a tool's shortcut in its tooltip). A tool learnt by clicking
  is a tool that can then be typed.
- The shortcut sheet (SHORTCUTS, the rail's ? button) gains a search box, focused when it opens:
  what a key does or the key itself ("undo", "ctrl", "F8"). A group with nothing left is hidden.
  Escape clears the box, then closes the sheet. Its last line says where every command's keys and
  aliases are: the command search."""
NAME = 'patch_phase128c.py'
BASE = '075266f2b6958b8514e1e15ac7166d06eb0778225f9c6a69f6da9378a6f4344c'
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


# ---- the dock's magnifier opens the one search
rep("""      '<button class="a3d-dbtn" id="a3d-dsearch" title="Find a command (every discipline)">'+""",
    """      '<button class="a3d-dbtn" id="a3d-dsearch" title="Search every command and tool (Ctrl+K, or start typing on the drawing)">'+""")
rep("""      var sbtn=ev.target&&ev.target.closest?ev.target.closest('#a3d-dsearch'):null;
      if(sbtn){
        ev.stopPropagation();
        var sp=host.querySelector('[data-dockpop="__search"]');
        var sOpen=sp&&sp.classList.contains('open');
        bimCloseDockPops();
        if(sp&&!sOpen){
          sp.classList.add('open');
          var sr=sbtn.getBoundingClientRect(),spr=sp.getBoundingClientRect();
          var stop=sr.top-spr.height-6;
          if(stop<8)stop=Math.min(sr.bottom+6,window.innerHeight-spr.height-8);
          var sleft=sr.left+sr.width/2-spr.width/2;
          if(sleft<8)sleft=8;
          if(sleft+spr.width>window.innerWidth-8)sleft=Math.max(8,window.innerWidth-spr.width-8);
          sp.style.top=Math.round(Math.max(8,stop))+'px';
          sp.style.left=Math.round(sleft)+'px';
          var si=document.getElementById('a3d-dsearchin');
          if(si){si.value='';bimRenderDockSearch('');si.focus();}
        }
        return;
      }
      if(ev.target&&ev.target.closest&&ev.target.closest('#a3d-dsearchin'))return;""",
    """      /* __acad3dV128: the magnifier opens THE command search, not a second one */
      var sbtn=ev.target&&ev.target.closest?ev.target.closest('#a3d-dsearch'):null;
      if(sbtn){
        ev.stopPropagation();
        bimCloseDockPops();
        if(window.openPalette)window.openPalette();
        return;
      }""")
rep("""    host.addEventListener('input',function(ev){
      if(ev.target&&ev.target.id==='a3d-dsearchin')bimRenderDockSearch(ev.target.value);
    });
""", "")
rep("""    /* __acad3dV71: the command search. At a hundred commands an icon grid still works; at three
       hundred it does not, and no amount of grouping saves it. Search spans EVERY discipline,
       not just the active one, so filtering the dock by domain never puts a tool out of reach --
       which is what lets the discipline filter be aggressive. */
    pops+='<div class="a3d-dockpop a3d-searchpop" data-dockpop="__search">'+
      '<input type="text" id="a3d-dsearchin" placeholder="Find a command">'+
      '<div id="a3d-dsearchres"></div></div>';
    bimRenderInto(host,h+'</div>'+pops);   /* __acad3dV118: the Discipline dropdown keeps the focus */
    bimRenderDockSearch('');
    return true;""", """    /* __acad3dV71: search spans EVERY discipline, so the dock's filter can be aggressive -- since
       V128 that search is the command search (the magnifier opens it). */
    bimRenderInto(host,h+'</div>'+pops);   /* __acad3dV118: the Discipline dropdown keeps the focus */
    return true;""")
a = t.index('  function bimRenderDockSearch(q){')
b = t.index('  function bimCloseDockPops(){')
assert t.count('  function bimRenderDockSearch(q){') == 1 and b > a and b - a < 1600
t = t[:a] + t[b:]
rep("""#a3d-dsearchin{width:100%;box-sizing:border-box;background:#1c2024;border:1px solid #3a4048;color:#dfe4ea;border-radius:5px;padding:6px 8px;font-size:12px;font-family:inherit;margin-bottom:5px}
#a3d-dsearchres{max-height:46vh;overflow:auto}
""", "")
rep(""".a3d-searchpop{min-width:290px;padding:7px}
.a3d-dockwhere{margin-left:auto;padding-left:12px;color:#7f858c;font-size:10px}
""", "")

# ---- every ribbon button says the command to type for it
rep("""        for(i=0;i<prim.length;i++)
          h+='<button class="a3d-dbtn" data-a3dr="'+prim[i]+'" title="'+
            bimEsc(a3drLabel(prim[i])+'  \\u00b7  '+tab.name)+'">'+a3drIcon(prim[i])+'</button>';""",
    """        for(i=0;i<prim.length;i++)
          h+='<button class="a3d-dbtn" data-a3dr="'+prim[i]+'" title="'+
            bimEsc(a3drLabel(prim[i])+'  \\u00b7  '+tab.name+bimActHint(prim[i],cat))+'">'+a3drIcon(prim[i])+'</button>';""")
rep("""    var h='<div class="a3d-dockbody">',pops='',r,g,tab,prim,i,grps,gi,ai,act;""",
    """    var h='<div class="a3d-dockbody">',pops='',r,g,tab,prim,i,grps,gi,ai,act,cat=bimCmdCatalog();   /* __acad3dV128 */""")
rep("""            pops+='<div class="a3d-dockitem'+(a3drIsUnimpl(act)?' a3dr-dis':'')+'" data-a3dr="'+act+'"'+
              (a3drIsUnimpl(act)?' title="Not implemented yet"':'')+'>'+a3drIcon(act)+""",
    """            pops+='<div class="a3d-dockitem'+(a3drIsUnimpl(act)?' a3dr-dis':'')+'" data-a3dr="'+act+'"'+
              (a3drIsUnimpl(act)?' title="Not implemented yet"':(bimActHint(act,cat)?' title="'+bimEsc(a3drLabel(act)+bimActHint(act,cat))+'"':''))+'>'+a3drIcon(act)+""")
rep("""  var A3DR_SEARCH_ICON=ric(""", """  /* __acad3dV128: the command a ribbon action answers to when typed: "  . type WALL or WA" */
  function bimActHint(act,cat){
    var cad=BIM_ACT_CMD[act],i,it;
    for(i=0;i<cat.length;i++){
      it=cat[i];
      if((cad&&it.cad===cad)||it.act===act||it.ribbon===act)return '  \\u00b7  type '+it.name+(it.aliases.length?' or '+it.aliases[0]:'');
    }
    return '';
  }
  var A3DR_SEARCH_ICON=ric(""")

# ---- the shortcut sheet, searchable
rep("""    var h='<div class="a3d-ruhd">Keyboard shortcuts</div><div class="a3d-rukeys">',g,r,i,j,k;""",
    """    var h='<div class="a3d-ruhd">Keyboard shortcuts</div>'+
      '<input type="search" class="a3d-rkfind" placeholder="Search: what it does, or a key (Ctrl+Z, F8)" aria-label="Search the keyboard shortcuts" autocomplete="off" spellcheck="false">'+   /* __acad3dV128 */
      '<div class="a3d-rukeys">',g,r,i,j,k;""")
rep("""        h+='<div class="a3d-rkrow"><span class="a3d-rkkeys">';""",
    """        h+='<div class="a3d-rkrow" data-rkhay="'+bimEsc((r.keys.join(' ')+' '+r.keys.join('+')+' '+r.label+' '+g.grp).toLowerCase())+'"><span class="a3d-rkkeys">';""")
rep("""        h+='</span><span class="a3d-rklab">'+bimEsc(r.label)+'</span></div>';
      }
    }
    return h+'</div>';""", """        h+='</span><span class="a3d-rklab">'+bimEsc(r.label)+'</span></div>';
      }
    }
    return h+'<div class="a3d-rkempty" hidden>No shortcut matches</div></div>'+
      '<div class="a3d-rknote">Every command, its alias and its keys: <kbd>'+bimEsc(A3D_MODKEY)+'</kbd>+<kbd>K</kbd>, or start typing a command on the drawing.</div>';""")
rep("""  function bimOpenRailMenu(id,btn){""", """  /* __acad3dV128: the sheet's search -- a row stays when every word typed is in its keys, its
     label or its group; Ctrl and Cmd read as one */
  function bimFilterShortcuts(p,q){
    var norm=function(s){return String(s).toLowerCase().replace(/cmd|ctrl|control|meta|\\u2318/g,'mod');};
    var words=norm(q).split(/\\s+/).filter(function(w){return !!w;}),kids=p.querySelectorAll('.a3d-rukeys > *'),i,grp=null,any=false,shown=0;
    for(i=0;i<kids.length;i++){
      var e=kids[i];
      if(e.classList.contains('a3d-rkgrp')){if(grp)grp.hidden=!any;grp=e;any=false;continue;}
      if(!e.classList.contains('a3d-rkrow'))continue;
      var hay=norm(e.getAttribute('data-rkhay')||''),ok=words.every(function(w){return hay.indexOf(w)>=0;});
      e.hidden=!ok;if(ok){any=true;shown++;}
    }
    if(grp)grp.hidden=!any;
    var em=p.querySelector('.a3d-rkempty');if(em)em.hidden=shown>0;
    return shown;
  }
  function bimOpenRailMenu(id,btn){""")
rep("""    p.style.left=Math.round(left)+'px';
    p.style.top=Math.round(top)+'px';
    return true;
  }
  function bimRailSet(spec,field){""", """    p.style.left=Math.round(left)+'px';
    p.style.top=Math.round(top)+'px';
    var rkf=id==='help'?p.querySelector('.a3d-rkfind'):null;   /* __acad3dV128: ready to type into */
    if(rkf){try{rkf.focus({preventScroll:true});}catch(eFo){}}
    return true;
  }
  function bimRailSet(spec,field){""")
rep("""      p.addEventListener('change',function(ev){
        var f=ev.target&&ev.target.closest?ev.target.closest('[data-a3druset]'):null;
        if(f)bimRailSet(f.getAttribute('data-a3druset'),f);
      });""", """      p.addEventListener('change',function(ev){
        var f=ev.target&&ev.target.closest?ev.target.closest('[data-a3druset]'):null;
        if(f)bimRailSet(f.getAttribute('data-a3druset'),f);
      });
      /* __acad3dV128: the shortcut sheet's search box */
      p.addEventListener('input',function(ev){
        if(ev.target&&ev.target.classList&&ev.target.classList.contains('a3d-rkfind'))bimFilterShortcuts(p,ev.target.value);
      });
      p.addEventListener('keydown',function(ev){
        if(!(ev.target&&ev.target.classList&&ev.target.classList.contains('a3d-rkfind'))||ev.key!=='Escape')return;
        ev.preventDefault();ev.stopPropagation();
        if(ev.target.value){ev.target.value='';bimFilterShortcuts(p,'');}
        else{bimCloseRailPop();try{ev.target.blur();}catch(eBl){}}
      });""")
rep(""".a3d-rklab{flex:1;color:#c3cad2;font-size:11.5px;line-height:1.35}""",
    """.a3d-rklab{flex:1;color:#c3cad2;font-size:11.5px;line-height:1.35}.a3d-rkfind{display:block;box-sizing:border-box;width:calc(100% - 8px);margin:0 4px 4px;background:#1c2024;border:1px solid #3a4048;color:#e6eaef;border-radius:6px;padding:6px 8px;font:inherit;font-size:11.5px}.a3d-rkfind:focus{outline:none;border-color:#4ea1ff}.a3d-rkempty{padding:10px 8px;color:#7d8590;font-size:11px}.a3d-rukeys [hidden]{display:none!important}.a3d-rknote{border-top:1px solid #343a41;margin:6px 4px 0;padding:7px 4px 3px;color:#8b949e;font-size:10.5px;line-height:1.4}.a3d-rknote kbd{font:600 9.5px/1 Inter,system-ui,sans-serif;color:#c7ced6;background:#1c2024;border:1px solid #3a4048;border-radius:3px;padding:2px 4px}body.light-theme .a3d-rkfind{background:#fff;border-color:#c9ced4;color:#222}""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
