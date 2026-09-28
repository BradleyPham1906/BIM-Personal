"""patch_phase84c.py -- two leftovers the V84 suite exposed.

The standing instruction is: "you need to make sure we dont have any left over and they gotta
work in the new version." Building the V84 suite turned up two things that were already broken
and that no previous suite could see:

  1. A SAVED 2D VIEW BELONGED TO NO GROUP. The Project Browser builds its 3D Views group from
     views.filter(v => !v.flat && !v.section) and its Sections group from views.filter(v =>
     v.section). A view saved from a plan or an elevation is flat and is not a section, so it
     matched neither and appeared nowhere. Measured at boot, on the shipped build:

         save attempt: {'btn': True, 'clicked': True}
         views now:    {'rows': 0, 'del': 0}

     The view was really created -- it shows in the palette list -- it just had no home in the
     tree. Every earlier suite that saved a view happened to do it from the 3D view, which is
     why this survived 38 suites.

  2. THE TWO .a3d-bdel BUTTONS WERE NEVER CLAIMED in the V80 shell audit. Not because they are
     dead -- probe84b drove the sheet one with a real pointer and watched the sheet count go
     1 -> 0 -- but because no suite had ever had BOTH a saved view and a sheet in existence when
     the audit ran, so the audit had never seen the rows. They are real controls, so they are
     claimed rather than removed; the whitelist did its job by flagging them.
"""

import hashlib
import pathlib
import sys

SRC = pathlib.Path(__file__).resolve().parent / 'canvas_v10.html'
BASE = '759c3064ea09093af4b8201a8db19c16f3007abe616d11df8673600a9592edce'

src = SRC.read_bytes()
have = hashlib.sha256(src).hexdigest()
if have != BASE:
    print('ABORT: baseline mismatch\n  expected %s\n  found    %s' % (BASE, have))
    sys.exit(1)
print('baseline ok: %s (%d bytes)' % (have[:16], len(src)))

text = src.decode('utf-8')
edits = 0


def sub(old, new, label, count=1):
    global text, edits
    n = text.count(old)
    if n != count:
        print('ABORT: %s: expected %d occurrence(s), found %d' % (label, count, n))
        sys.exit(1)
    text = text.replace(old, new, count)
    edits += 1
    print('  edit %d ok: %s' % (edits, label))


# ------------------------------------------------------------------ 1. the group is open by default
OLD_OPEN = ("  var A3D_BROWSER_OPEN={views:true,floorplans:true,view3d:true,elevations:true,"
            "sections:true,")
NEW_OPEN = ("  var A3D_BROWSER_OPEN={views:true,floorplans:true,view3d:true,views2d:true,"
            "elevations:true,sections:true,")
sub(OLD_OPEN, NEW_OPEN, 'the 2D Views group is open by default')

# ------------------------------------------------------------------ 2. the group itself
OLD_ELEV_GRP = "      h+=bimBrowserGroup('elevations','Elevations',4,1);"
NEW_ELEV_GRP = """      /* __acad3dV84: a saved view whose camera is FLAT and which is not a section matched
         neither of the groups above -- 3D Views filters it out for being flat, Sections for not
         being a section -- so a view saved from a plan or an elevation landed in the palette
         list and nowhere in the Project Browser at all. Measured on the shipped build: save a
         view at boot, get zero browser rows. */
      var v2=A3D.views.filter(function(v){return !!v.flat&&!v.section;});
      h+=bimBrowserGroup('views2d','2D Views',v2.length,1);
      if(O.views2d){
        if(!v2.length)h+='<div class="a3d-bempty" style="padding-left:30px">none yet</div>';
        for(i=0;i<v2.length;i++)
          h+=bimBrowserLeaf(v2[i].name,{data:'data-a3dbviewgo="'+v2[i].id+'"',
            sel:(A3D.activeViewId===v2[i].id),ico:'\\u25b1'},2,
            '<button class="a3d-bdel" data-a3dbviewdel="'+v2[i].id+'" title="Delete view">\\u00d7</button>');
      }
      h+=bimBrowserGroup('elevations','Elevations',4,1);"""
sub(OLD_ELEV_GRP, NEW_ELEV_GRP, 'saved 2D views get a group in the Project Browser')

# ------------------------------------------------------------------ 3. claim the delete buttons
OLD_CLAIM = "    {sel:'.a3d-btgl',why:'toggles object lock in the browser'},"
NEW_CLAIM = """    {sel:'.a3d-btgl',why:'toggles object lock in the browser'},
    /* __acad3dV84: claimed, not removed -- both are wired and were driven with a real pointer
       before being claimed. They went unseen until now because no suite had ever had a saved
       view AND a sheet in existence at the moment the audit ran. */
    {sel:'.a3d-bdel',why:'deletes a saved view or a sheet from the Project Browser'},"""
sub(OLD_CLAIM, NEW_CLAIM, 'the Project Browser delete buttons are claimed in the shell audit')

out = text.encode('utf-8')
SRC.write_bytes(out)
print('\n%d edits applied' % edits)
print('bytes : %d -> %d (%+d)' % (len(src), len(out), len(out) - len(src)))
print('sha256: %s' % hashlib.sha256(out).hexdigest())
