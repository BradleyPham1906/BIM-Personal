"""patch_phase130b.py -- V130: the hooks the suite reads the tools panel and the dock through, and
the marker. __a3dDockOpenGroup, which opened a dock group's More menu, now opens the panel on that
group: the More menus are gone, and the panel is where a group's tools are."""
NAME = 'patch_phase130b.py'
BASE = '7499f538d6ac8015ec0ce0d9fb2682c53dc8c78a03465c93b70230430501be9a'
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


rep("""  window.__a3dDockOpenGroup=function(id){
    var c=document.querySelector('#a3d-dock [data-dockmore="'+id+'"]');
    if(!c)return false;
    c.click();
    var p=document.querySelector('#a3d-dock [data-dockpop="'+id+'"]');
    return !!(p&&p.classList.contains('open'));
  };""", """  window.__a3dDockOpenGroup=function(id){   /* __acad3dV130: the group, in the tools panel */
    if(!bimOpenToolsPanel())return false;
    var p=document.getElementById('a3d-rupop'),c=p&&p.querySelector('.a3d-rkcat[data-rkcat="tool:'+id+'"]');
    if(!c)return false;
    c.click();
    return p.classList.contains('open');
  };""")
rep("""  window.__acad3dV129='shortcutspanel,""", """  /* __acad3dV130: every tool in the panel, and the dock's pins */
  window.__a3dDockPins=function(disc){return bimDockPins(disc||A3D_DISC_CUR);};
  window.__a3dSetDockPin=function(act,on){return bimSetDockPin(act,!!on);};
  window.__a3dDockPinDefaults=function(){return JSON.parse(JSON.stringify(A3D_DOCK_PIN_DEFAULTS));};
  window.__a3dToolsPanel=function(){return bimOpenToolsPanel();};
  window.__a3dToolActions=function(){   /* every tool the panel lists: every action of every tab */
    var out={},i,g,j,grs;
    for(i=0;i<A3DR_TABS.length;i++){grs=a3drTabGroups(A3DR_TABS[i]);for(g=0;g<grs.length;g++)for(j=0;j<grs[g].acts.length;j++)out[grs[g].acts[j]]=1;}
    return Object.keys(out).sort();
  };
  window.__a3dCmdUsageOf=function(act){var it=bimCatForAct(bimCmdCatalog(),act),u=bimCmdUsage();return it&&u[it.id]?u[it.id].n:0;};
  window.__acad3dV130='toolspanel,everytool,toolgroups,kindfilter,sortgroupnameused,pinnedcategory,pintodock,pinsperdiscipline,'+
    'pindefaults,pinsremembered,rowruns,panelcloses,usefromdock,dockonerow,alltoolsbutton,compactsearch';
  window.__acad3dV129='shortcutspanel,""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
