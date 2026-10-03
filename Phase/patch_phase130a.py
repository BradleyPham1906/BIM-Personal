"""patch_phase130a.py -- V130: every tool in one panel, and a dock of the few used most.

The owner, on the V129 dock and panel: "this tool bar is very crowded. I say we combine it in the
shortcut table and use search, filter sorting. group the features and stuff here. and in the main
screen only show the keys one (those that most likely use the most)".

- The shortcuts panel becomes Tools and shortcuts: every ribbon tool (grouped by its tab, Revit's
  panels) and every key (grouped as before) in one list. The search covers both; Tools / Keys
  filters one kind; the list sorts by group, by name, or by use; On the dock lists the pinned.
- A tool row: its icon, name and what it does, the command to type, its keys, and a pin. A click
  runs the tool and puts the panel away.
- The dock is one row: the discipline, the pinned tools (a set per discipline, the likeliest to
  be used most until the user pins others), All tools, and the search. The More menus and the
  second row are gone: the panel is where the rest live.
- A tool run from the dock or the panel counts as a use, so Most used sorts by the whole app."""
NAME = 'patch_phase130a.py'
BASE = '54d61a42f944669ba375292066df6467a31643de8b852a04b6295252045ed4f3'
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


def between(start, end, new):
    """replace the text from start up to (not including) end, each found exactly once"""
    global t
    if t.count(start) != 1 or t.count(end) != 1:
        sys.exit('ABORT: span anchors %d/%d: %r' % (t.count(start), t.count(end), start[:60]))
    a = t.index(start)
    b = t.index(end)
    if b <= a:
        sys.exit('ABORT: span out of order: %r' % start[:60])
    t = t[:a] + esc(new) + t[b:]


# ---------------------------------------------------------------- the panel
between("  function bimShortcutsHtml(){", "  function bimRailStackHtml(){", r"""  /* __acad3dV130: tools and shortcuts -- every tool and every key in one list, the categories on
     the left (the ribbon's tabs, then the key groups), a filter by kind, a sort, and a pin for the
     dock. Every child of the list carries its place (data-rkord), so By group can put it back. */
  function bimShortcutsHtml(){
    var groups=bimShortcutGroups(),g,r,i,j,k,total=0,nav='',list='',ord=0,use=bimCmdUsage(),cat=bimCmdCatalog();
    var pins=bimDockPins(A3D_DISC_CUR),tabs=A3DR_TABS,seen={},nTools=0,nPinned=0,tnav='',tlist='';
    for(i=0;i<tabs.length;i++){
      var tab=tabs[i],gid='tool:'+tab.id,grs=a3drTabGroups(tab),rows='',n=0,gi,ai,a;
      for(gi=0;gi<grs.length;gi++)for(ai=0;ai<grs[gi].acts.length;ai++){
        a=grs[gi].acts[ai];
        if(seen[a])continue;   /* every ribbon action, even one the search leaves out (BIM_ACT_HIDE) */
        seen[a]=1;n++;
        var it=bimCatForAct(cat,a),off=a3drIsUnimpl(a),lab=a3drLabel(a),pinned=pins.indexOf(a)>=0;
        var desc=off?'Not built yet':((it&&it.desc)||BIM_ACT_DESC[a]||'');
        var ks=(it&&it.keys)||null,nuse=(it&&use[it.id]&&use[it.id].n)||0;
        if(pinned)nPinned++;
        rows+='<div class="a3d-rkrow a3d-rktool'+(off?' off':'')+'" data-rkg="'+gid+'" data-rkkind="tool" data-rkact="'+bimEsc(a)+'" data-rkord="'+(ord++)+'"'+
          ' data-rkname="'+bimEsc(String(lab).toLowerCase())+'" data-rkuse="'+nuse+'" data-rkpinned="'+(pinned?1:0)+'"'+
          ' data-rkhay="'+bimEsc((lab+' '+desc+' '+tab.name+' '+grs[gi].t+' '+(it?it.name+' '+it.aliases.join(' ')+' '+(it.terms||''):'')+' '+(ks?ks.join(' ')+' '+ks.join('+'):'')).toLowerCase())+'">'+
          '<button type="button" class="a3d-rkrun"'+(off?' disabled':' data-a3dr="'+bimEsc(a)+'"')+'>'+a3drIcon(a)+
          '<span class="a3d-rklab">'+bimEsc(lab)+'</span><span class="a3d-rkdesc">'+bimEsc(desc)+'</span></button>'+
          '<span class="a3d-rkcmd">'+(it?'type '+bimEsc(it.name):'')+'</span><span class="a3d-rkkeys">';
        if(ks)for(k=0;k<ks.length;k++)rows+=(k?'<span class="a3d-rkplus">+</span>':'')+'<kbd>'+bimEsc(ks[k])+'</kbd>';
        rows+='</span>'+(off?'<span class="a3d-rkpinx"></span>':'<button type="button" class="a3d-rkpin" data-rkpin="'+bimEsc(a)+'" aria-pressed="'+(pinned?'true':'false')+'"'+
          ' aria-label="'+bimEsc((pinned?'Take '+lab+' off the dock':'Put '+lab+' on the dock'))+'" title="'+(pinned?'On the dock: click to take it off':'Put it on the dock')+'">'+A3DR_PIN_ICON+'</button>')+'</div>';
      }
      if(!n)continue;
      nTools+=n;
      var dn=tab.disc?bimDiscName(tab.disc):'';
      tnav+='<button type="button" class="a3d-rkcat" data-rkcat="'+gid+'"><span>'+bimEsc(tab.name)+(dn&&dn!==tab.name?' <i>'+bimEsc(dn)+'</i>':'')+'</span><span class="a3d-rkn">'+n+'</span></button>';
      tlist+='<div class="a3d-rkgrp" data-rkg="'+gid+'" data-rkord="'+(ord++)+'">'+bimEsc(tab.name)+'</div>'+rows;
    }
    for(i=0;i<groups.length;i++){
      g=groups[i];total+=g.rows.length;
      nav+='<button type="button" class="a3d-rkcat" data-rkcat="'+bimEsc(g.grp)+'"><span>'+bimEsc(g.grp)+'</span><span class="a3d-rkn">'+g.rows.length+'</span></button>';
      list+='<div class="a3d-rkgrp" data-rkg="'+bimEsc(g.grp)+'" data-rkord="'+(ord++)+'">'+bimEsc(g.grp)+'</div>';
      if(g.note)list+='<div class="a3d-rkgnote" data-rkg="'+bimEsc(g.grp)+'" data-rkord="'+(ord++)+'">'+bimEsc(g.note)+'</div>';
      for(j=0;j<g.rows.length;j++){
        r=g.rows[j];
        var ru=(r.cmd&&use['cmd:'+r.cmd]&&use['cmd:'+r.cmd].n)||0;
        list+='<div class="a3d-rkrow" data-rkg="'+bimEsc(g.grp)+'" data-rkkind="key" data-rkord="'+(ord++)+'" data-rkname="'+bimEsc(r.label.toLowerCase())+'" data-rkuse="'+ru+'"'+
          ' data-rkhay="'+bimEsc((r.keys.join(' ')+' '+r.keys.join('+')+' '+r.label+' '+g.grp+' '+(r.cmd||'')).toLowerCase())+'">'+
          '<span class="a3d-rklab">'+bimEsc(r.label)+'</span>'+
          '<span class="a3d-rkcmd">'+(r.cmd?'type '+bimEsc(r.cmd):'')+'</span><span class="a3d-rkkeys">';
        for(k=0;k<r.keys.length;k++){
          if(k)list+='<span class="a3d-rkplus">'+(r.alt?'/':'+')+'</span>';   /* __acad3dV122: a slash between alternatives */
          list+='<kbd>'+bimEsc(r.keys[k])+'</kbd>';
        }
        list+='</span><span class="a3d-rkpinx"></span></div>';
      }
    }
    tlist=bimRkReorder(tlist);
    return '<div class="a3d-rkhead"><h2 class="a3d-rktitle">Tools and shortcuts</h2>'+
      '<input type="search" class="a3d-rkfind" placeholder="Search tools and keys: wall, undo, ctrl z, F8" aria-label="Search the tools and keyboard shortcuts" autocomplete="off" spellcheck="false">'+   /* __acad3dV128 */
      '<button type="button" class="a3d-rkclose" data-rkclose aria-label="Close the tools and shortcuts">×</button></div>'+
      '<div class="a3d-rkbar"><div class="a3d-rkkinds" role="group" aria-label="Show">'+
      '<button type="button" class="a3d-rkkind on" data-rkkindf="all" aria-pressed="true">All</button>'+
      '<button type="button" class="a3d-rkkind" data-rkkindf="tool" aria-pressed="false">Tools</button>'+
      '<button type="button" class="a3d-rkkind" data-rkkindf="key" aria-pressed="false">Keys</button></div>'+
      '<label class="a3d-rksortl">Sort <select class="a3d-rksort" aria-label="Sort the list">'+
      '<option value="group">By group</option><option value="name">By name</option><option value="used">Most used</option></select></label>'+
      '<span class="a3d-rkshown" aria-live="polite"></span></div>'+
      '<div class="a3d-rkbody"><nav class="a3d-rknav" aria-label="Categories">'+
      '<button type="button" class="a3d-rkcat on" data-rkcat="all" aria-pressed="true"><span>All</span><span class="a3d-rkn">'+(nTools+total)+'</span></button>'+
      '<button type="button" class="a3d-rkcat" data-rkcat="__pinned"><span>On the dock</span><span class="a3d-rkn a3d-rkpinn">'+nPinned+'</span></button>'+
      '<div class="a3d-rknavh">Tools</div>'+tnav+'<div class="a3d-rknavh">Keys</div>'+nav+
      '<div class="a3d-rknote">Pin a tool to put it on the dock. Every command by name: <kbd>'+bimEsc(A3D_MODKEY)+'</kbd>+<kbd>K</kbd>, or start typing on the drawing.</div></nav>'+
      '<div class="a3d-rukeys">'+tlist+list+'<div class="a3d-rkempty" hidden>Nothing matches. Try what it does, like “snap”, or a key, like “F8”.</div></div></div>';
  }
  /* the tools' rows were numbered before their header was: number the list again, as it stands */
  function bimRkReorder(html){
    var box=document.createElement('div'),i;
    box.innerHTML=html;
    for(i=0;i<box.children.length;i++)box.children[i].setAttribute('data-rkord',String(i));
    return box.innerHTML;
  }
  function bimDiscName(id){
    for(var i=0;i<A3D_DISCIPLINES.length;i++)if(A3D_DISCIPLINES[i].id===id)return A3D_DISCIPLINES[i].name;
    return id;
  }
  /* the catalogue's entry for a ribbon action: its own, or the typed command it runs */
  function bimCatForAct(cat,act){
    var cad=BIM_ACT_CMD[act],i;
    for(i=0;i<cat.length;i++)if((cad&&cat[i].cad===cad)||cat[i].act===act||cat[i].ribbon===act)return cat[i];
    return null;
  }
  /* By group puts every row back in its place; By name and Most used make one list */
  function bimSortShortcuts(p){
    var lst=p.querySelector('.a3d-rukeys');if(!lst)return;
    var how=p.getAttribute('data-rksort')||'group',em=lst.querySelector('.a3d-rkempty');
    var kids=Array.prototype.slice.call(lst.children).filter(function(e){return e!==em;});
    kids.sort(function(a,b){
      if(how==='group')return (+a.getAttribute('data-rkord'))-(+b.getAttribute('data-rkord'));
      var ar=a.classList.contains('a3d-rkrow'),br=b.classList.contains('a3d-rkrow');
      if(ar!==br)return ar?1:-1;   /* the headers, hidden, first */
      if(how==='used'){var du=(+b.getAttribute('data-rkuse')||0)-(+a.getAttribute('data-rkuse')||0);if(du)return du;}
      var an=a.getAttribute('data-rkname')||'',bn=b.getAttribute('data-rkname')||'';
      return an<bn?-1:(an>bn?1:0);
    });
    kids.forEach(function(e){lst.appendChild(e);});
    if(em)lst.appendChild(em);
    lst.scrollTop=0;
  }
""")

# the filter: the kind and the pinned, on top of V129's category and words
rep("""    var cat=p.getAttribute('data-rkcat')||'all',note=null;   /* __acad3dV129: the category chosen on the left */""",
    """    var cat=p.getAttribute('data-rkcat')||'all',note=null;   /* __acad3dV129: the category chosen on the left */
    var kind=p.getAttribute('data-rkkind')||'all',pinnedOnly=cat==='__pinned';   /* __acad3dV130: Tools or Keys, and On the dock */
    if(pinnedOnly)cat='all';""")
rep("""      e.hidden=!ok;if(ok){any=true;shown++;}""",
    """      if(ok&&kind!=='all'&&e.getAttribute('data-rkkind')!==kind)ok=false;
      if(ok&&pinnedOnly&&e.getAttribute('data-rkpinned')!=='1')ok=false;
      e.hidden=!ok;if(ok){any=true;shown++;}""")
rep("""    var em=p.querySelector('.a3d-rkempty');if(em)em.hidden=shown>0;
    return shown;""",
    """    var em=p.querySelector('.a3d-rkempty');if(em)em.hidden=shown>0;
    var sh=p.querySelector('.a3d-rkshown');if(sh)sh.textContent=shown+' shown';   /* __acad3dV130 */
    return shown;""")

# opening: All, all kinds, by group
rep("""    p.setAttribute('data-rkcat','all');
""", """    p.setAttribute('data-rkcat','all');
    p.setAttribute('data-rkkind','all');p.setAttribute('data-rksort','group');   /* __acad3dV130 */
""")
rep("""    var rkf=id==='help'?p.querySelector('.a3d-rkfind'):null;   /* __acad3dV128: ready to type into */""",
    """    if(id==='help')bimFilterShortcuts(p,'');   /* __acad3dV130: the count shown */
    var rkf=id==='help'?p.querySelector('.a3d-rkfind'):null;   /* __acad3dV128: ready to type into */""")

# clicks: a tool runs and the panel goes; a pin; the kind filter
rep("""        if(b){bimRailAction(b.getAttribute('data-a3druitem'));return;}
""", """        if(b){bimRailAction(b.getAttribute('data-a3druitem'));return;}
        /* __acad3dV130: a tool row runs (the document's dispatcher runs it) and the panel goes */
        if(ev.target&&ev.target.closest&&ev.target.closest('.a3d-rkrun[data-a3dr]')){bimCloseRailPop();return;}
        var pn=ev.target&&ev.target.closest?ev.target.closest('[data-rkpin]'):null;
        if(pn){bimToggleDockPin(p,pn.getAttribute('data-rkpin'));return;}
        var kf=ev.target&&ev.target.closest?ev.target.closest('[data-rkkindf]'):null;
        if(kf){
          var kbs=p.querySelectorAll('[data-rkkindf]'),kk;
          for(kk=0;kk<kbs.length;kk++){var kon=kbs[kk]===kf;kbs[kk].classList.toggle('on',kon);kbs[kk].setAttribute('aria-pressed',kon?'true':'false');}
          p.setAttribute('data-rkkind',kf.getAttribute('data-rkkindf'));
          var kfi=p.querySelector('.a3d-rkfind');bimFilterShortcuts(p,kfi?kfi.value:'');
          return;
        }
""")
rep("""        if(f)bimRailSet(f.getAttribute('data-a3druset'),f);
""", """        if(f)bimRailSet(f.getAttribute('data-a3druset'),f);
        if(ev.target&&ev.target.classList&&ev.target.classList.contains('a3d-rksort')){   /* __acad3dV130 */
          p.setAttribute('data-rksort',ev.target.value);bimSortShortcuts(p);
        }
""")

# ---------------------------------------------------------------- the dock
between("  function bimBuildDock(){", "  /* ================= __acad3dV128: one catalogue of every command", r"""  /* __acad3dV130: the dock is one row -- the discipline, the tools pinned for it, All tools and the
     search. Everything else is in the Tools and shortcuts panel. */
  function bimBuildDock(){
    var host=document.getElementById('a3d-dock');
    if(!host)return false;
    var cat=bimCmdCatalog(),pins=bimDockPins(A3D_DISC_CUR),i,a;
    var names=bimDockLabelsOn();   /* __acad3dV129: tool names under the icons, unless Icons only */
    host.classList.toggle('a3d-docklabels',names);
    var h='<div class="a3d-dockbody"><div class="a3d-dockrow a3d-dockone">'+
      '<select id="a3d-discsel" class="a3d-discsel" aria-label="Discipline: which tools the dock and the panel start with">'+
      (function(){var o='',d;for(d=0;d<A3D_DISCIPLINES.length;d++)
        o+='<option value="'+bimEsc(A3D_DISCIPLINES[d].id)+'"'+
          (A3D_DISCIPLINES[d].id===A3D_DISC_CUR?' selected':'')+'>'+
          bimEsc(A3D_DISCIPLINES[d].name)+'</option>';return o;})()+
      '</select><div class="a3d-dsep"></div>'+
      '<div class="a3d-dockgrp a3d-dockpins" data-dockgrp="__pins">';
    for(i=0;i<pins.length;i++){
      a=pins[i];
      h+='<button type="button" class="a3d-dbtn" data-a3dr="'+a+'" data-a3dtip="'+a+'" aria-label="'+
        bimEsc(a3drLabel(a)+bimActHint(a,cat))+'">'+a3drIcon(a)+
        (names?'<span class="a3d-dblbl">'+bimEsc(a3drLabel(a))+'</span>':'')+'</button>';
    }
    h+='</div><div class="a3d-dsep"></div>'+
      '<button type="button" class="a3d-dall" id="a3d-dall" data-a3dtip="__all" aria-label="All tools and shortcuts">'+A3DR_ALL_ICON+
      (names?'<span class="a3d-dblbl">All tools</span>':'')+'</button>'+
      '<button type="button" class="a3d-dsearchpill" id="a3d-dsearch" aria-label="Search tools and commands" data-a3dtip="__search">'+
      A3DR_SEARCH_ICON+'<span>Search</span><kbd>'+bimEsc(A3D_MODKEY)+' K</kbd></button>'+
      '</div></div>';
    bimRenderInto(host,h);   /* __acad3dV118: the Discipline dropdown keeps the focus */
    bimTipHide();bimBindDockTips(host);   /* __acad3dV129 */
    return true;
  }
  /* The tools on the dock when nobody has pinned any: the ones a person reaches for most, per
     discipline. A discipline added later (a domain pack) starts with its own tabs' first tools. */
  var A3D_DOCK_PIN_DEFAULTS={
    arch:['bim:wall','bim:door','bim:window','bim:floor','bim:column','bim:room','s:poly','bim:dim','m:dup'],
    struct:['bim:column','bim:beam','bim:floor','bim:brace','bim:footing','bim:grid','bim:level','bim:analyze','bim:dim']
  };
  var A3D_DOCK_PIN_MAX=12;
  function bimDockPins(disc){
    var p=bimLoadUIPanelPrefs(),set=p.dockPins&&p.dockPins[disc],known={},all=a3drAllCommands(),i,out=[];
    for(i=0;i<all.length;i++)known[all[i].act]=1;
    if(!set){
      set=A3D_DOCK_PIN_DEFAULTS[disc];
      if(!set){set=[];var tabs=a3drDockTabs(disc);for(i=0;i<tabs.length;i++)if(tabs[i].disc===disc)set=set.concat(a3drTabPrimary(tabs[i]));}
    }
    for(i=0;i<set.length&&out.length<A3D_DOCK_PIN_MAX;i++)if(known[set[i]]&&!a3drIsUnimpl(set[i])&&out.indexOf(set[i])<0)out.push(set[i]);
    return out;
  }
  function bimSetDockPin(act,on){
    var pins=bimDockPins(A3D_DISC_CUR),ix=pins.indexOf(act),lab=a3drLabel(act);
    if(on&&ix<0){
      if(pins.length>=A3D_DOCK_PIN_MAX){a3dToast('The dock holds '+A3D_DOCK_PIN_MAX+' tools: take one off first');return false;}
      pins.push(act);
    }else if(!on&&ix>=0)pins.splice(ix,1);
    else return true;
    var p=bimLoadUIPanelPrefs();p.dockPins=p.dockPins||{};p.dockPins[A3D_DISC_CUR]=pins;bimSaveUIPanelPrefs(p);
    bimBuildDock();
    a3dToast(on?lab+' is on the dock':lab+' is off the dock; it stays in All tools');
    return true;
  }
  function bimToggleDockPin(p,act){
    var row=p.querySelector('.a3d-rkrow[data-rkact="'+act+'"]'),on=!(row&&row.getAttribute('data-rkpinned')==='1');
    if(!bimSetDockPin(act,on))return false;
    var now=bimDockPins(A3D_DISC_CUR),rows=p.querySelectorAll('.a3d-rktool'),i;
    for(i=0;i<rows.length;i++){
      var a=rows[i].getAttribute('data-rkact'),pin=now.indexOf(a)>=0,b=rows[i].querySelector('[data-rkpin]'),l=a3drLabel(a);
      rows[i].setAttribute('data-rkpinned',pin?'1':'0');
      if(b){b.setAttribute('aria-pressed',pin?'true':'false');b.setAttribute('aria-label',pin?'Take '+l+' off the dock':'Put '+l+' on the dock');
        b.title=pin?'On the dock: click to take it off':'Put it on the dock';}
    }
    var pc=p.querySelector('.a3d-rkpinn');if(pc)pc.textContent=String(now.length);
    var f=p.querySelector('.a3d-rkfind');bimFilterShortcuts(p,f?f.value:'');
    return true;
  }
  /* the panel, from the dock's All tools, SHORTCUTS or ? -- opened once, never toggled shut */
  function bimOpenToolsPanel(){
    var hp=document.getElementById('a3d-rupop');
    if(hp&&hp.classList.contains('open')&&hp.getAttribute('data-for')==='help')return true;
    var b=document.querySelector('[data-a3drumenu="help"]');
    if(!b){a3dToast('The tools and shortcuts panel is not available here');return false;}
    b.click();
    return true;
  }
  /* a tool run from the dock or the panel is a use, as one run from the search is */
  function bimActUsed(act){
    var it=bimCatForAct(bimCmdCatalog(),act);
    if(it)bimCmdUsed(it.id);
  }
""")
rep("""    bimRunAct(b.getAttribute('data-a3dr'));
  });""", """    var ra=b.getAttribute('data-a3dr');
    if(bimRunAct(ra)!==false&&(b.closest('#a3d-dock')||b.closest('#a3d-rupop')))bimActUsed(ra);   /* __acad3dV130 */
  });""")

# the dock's own clicks: All tools
rep("""      /* __acad3dV128: the magnifier opens THE command search, not a second one */""",
    """      /* __acad3dV130: All tools opens the panel */
      if(ev.target&&ev.target.closest&&ev.target.closest('#a3d-dall')){ev.stopPropagation();bimCloseDockPops();bimOpenToolsPanel();return;}
      /* __acad3dV128: the magnifier opens THE command search, not a second one */""")

# SHORTCUTS is the same panel
rep("""    shortcuts:function(){
      var hp=document.getElementById('a3d-rupop');   /* __acad3dV129: already open, it stays open */
      if(hp&&hp.classList.contains('open')&&hp.getAttribute('data-for')==='help')return;
      var b=document.querySelector('[data-a3drumenu="help"]');
      if(!b){a3dToast('The shortcuts sheet is not available here');return;}
      b.click();
    }""", """    shortcuts:function(){
      bimOpenToolsPanel();   /* __acad3dV130: the panel; already open, it stays open (the one guard is there) */
    }""")

# the tooltip for All tools
rep("""    if(spec.indexOf('__more:')===0)""",
    """    if(spec==='__all')return {name:'All tools and shortcuts',keys:['?'],desc:'Every tool and key: search, filter, sort, and pin tools to the dock',type:[],where:''};   /* __acad3dV130 */
    if(spec.indexOf('__more:')===0)""")

# icons
rep("""  var A3DR_SEARCH_ICON=ric(""", """  var A3DR_ALL_ICON=ric('<rect x="4" y="4" width="6" height="6" rx="1"/><rect x="14" y="4" width="6" height="6" rx="1"/><rect x="4" y="14" width="6" height="6" rx="1"/><rect x="14" y="14" width="6" height="6" rx="1"/>');   /* __acad3dV130 */
  var A3DR_PIN_ICON=ric('<path d="M12 3.5l2.6 5.3 5.9.9-4.3 4.1 1 5.8-5.2-2.7-5.2 2.7 1-5.8-4.3-4.1 5.9-.9z"/>');
  var A3DR_SEARCH_ICON=ric(""")

# ---------------------------------------------------------------- styles
rep(""".a3d-rukeys [hidden]{display:none!important}""", """.a3d-rukeys [hidden]{display:none!important}
.a3d-rkbar{display:flex;align-items:center;gap:14px;padding:8px 16px;border-bottom:1px solid #343a41;flex:0 0 auto;font-size:12px;color:#9aa3ad}
.a3d-rkkinds{display:flex;background:#1c2024;border:1px solid #3a4048;border-radius:7px;padding:2px}
.a3d-rkkind{border:0;background:transparent;color:#c3cad2;font:inherit;font-size:12px;padding:4px 12px;border-radius:5px;cursor:pointer}
.a3d-rkkind.on{background:#2c477d;color:#fff}
.a3d-rksortl{display:flex;align-items:center;gap:6px}
.a3d-rksort{background:#1c2024;border:1px solid #3a4048;color:#dfe4ea;border-radius:6px;font:inherit;font-size:12px;padding:3px 6px}
.a3d-rkshown{margin-left:auto}
.a3d-rknavh{font-size:10px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:#7d8590;padding:10px 10px 3px}
#a3d-rupop.a3d-rksheet .a3d-rkcat{min-height:28px;font-size:12.5px}
.a3d-rkcat i{font-style:normal;font-size:10.5px;color:#7d8590;margin-left:4px}
#a3d-rupop.a3d-rksheet .a3d-rukeys .a3d-rkrow{grid-template-columns:minmax(0,1fr) auto minmax(90px,auto) 30px}
.a3d-rkrun{display:flex;align-items:center;gap:10px;min-width:0;background:transparent;border:0;padding:0;margin:0;color:inherit;font:inherit;text-align:left;cursor:pointer}
.a3d-rkrun svg{width:18px;height:18px;flex:0 0 auto;color:#aab2bd}
.a3d-rkrun .a3d-rklab{flex:0 0 auto}
.a3d-rkdesc{color:#8b949e;font-size:12px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;min-width:0}
.a3d-rktool:hover .a3d-rklab{color:#fff}
.a3d-rktool.off .a3d-rkrun{cursor:default;opacity:.5}
.a3d-rkpin{width:28px;height:28px;display:grid;place-items:center;border:0;border-radius:6px;background:transparent;color:#59616b;cursor:pointer;padding:0}
.a3d-rkpin svg{width:15px;height:15px}
.a3d-rkpin:hover{background:#2f353c;color:#dfe4ea}
.a3d-rkpin[aria-pressed="true"]{color:#f2c94c}
.a3d-rkpin[aria-pressed="true"] svg{fill:currentColor}
#a3d-rupop[data-rksort="name"] .a3d-rkgrp,#a3d-rupop[data-rksort="name"] .a3d-rkgnote,#a3d-rupop[data-rksort="used"] .a3d-rkgrp,#a3d-rupop[data-rksort="used"] .a3d-rkgnote{display:none!important}
.a3d-dockpins{flex-direction:row!important;align-items:center;gap:1px!important}
.a3d-dockone{gap:4px}
.a3d-dall{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;width:34px;height:32px;background:transparent;border:1px solid transparent;border-radius:5px;color:#c3cad2;cursor:pointer;padding:0;flex:0 0 auto;font:inherit}
.a3d-dall svg{width:18px;height:18px}
.a3d-dall:hover{background:#2f353c;color:#fff}
#a3d-dock.a3d-docklabels .a3d-dall{width:60px;height:38px}
#a3d-dock.a3d-docklabels .a3d-dall svg{width:16px;height:16px}
.a3d-dall:focus-visible{outline:2px solid #4ea1ff;outline-offset:1px}
#a3d-dock .a3d-dsearchpill{flex:0 0 auto;min-width:0;margin-left:6px}
body.light-theme .a3d-rkkind{color:#30343b}body.light-theme .a3d-rkkind.on{background:#dbe7ff;color:#12305f}body.light-theme .a3d-rkkinds,body.light-theme .a3d-rksort{background:#fff;border-color:#c9ced6;color:#202124}
body.light-theme .a3d-rkdesc{color:#5f6670}body.light-theme .a3d-dall{color:#30343b}""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
