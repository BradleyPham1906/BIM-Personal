"""
Phase 74 -- schedules become a registry, and the Beams schedule becomes reachable.

THE BUG FOUND WHILE BUILDING THIS. SCHEDULE_DEFS carries seven schedules. The Project Browser
listed six:

    var schedKeys=['room','door','window','wall','ceiling','column'];   // no 'beam'

and the only other way to choose one, #a3d-schedcat, is display:none. So the Beams schedule was
built, columned, CSV-exportable -- and unreachable from the interface. A tool that exists but
cannot be reached is the same failure as one that does not work (Product Principle 1).

Deriving both lists from SCHEDULE_DEFS fixes that by construction rather than by adding 'beam' to
a literal that will drift again, and is the same change that makes registration possible at all.

Anchored search-and-replace. Every anchor is asserted to match an EXACT expected count.
"""
import io, sys, hashlib

PATH = 'canvas_v10.html'
EXPECT_SHA = 'bcc5b8c592df9b7d830dc61835d51c52b85ba0b3e644c1e9eccc9affe3d8eca9'

src = io.open(PATH, encoding='utf-8').read()
raw = io.open(PATH, 'rb').read()
got = hashlib.sha256(raw).hexdigest()
if got != EXPECT_SHA:
    sys.exit('baseline sha mismatch: %s' % got)
print('baseline ok: %d bytes, %s' % (len(raw), got[:16]))

patches = []


def P(name, old, new, count=1):
    patches.append((name, old, new, count))


# --------------------------------------------------------------- 1. the registry + registration
P('code.registry',
  "  function bimFmtScheduleValue(v,fmt){",
  "  /* __acad3dV74: schedules are a REGISTRY now, not a literal plus two hand-kept lists.\n"
  "\n"
  "     The bug that forced this: SCHEDULE_DEFS had seven entries and the Project Browser listed\n"
  "     six from a hardcoded array that omitted 'beam'. Since the only other chooser\n"
  "     (#a3d-schedcat) is display:none, the Beams schedule was unreachable -- built, columned and\n"
  "     CSV-exportable, with no way for a user to open it. Adding 'beam' to the literal would fix\n"
  "     today and drift again on the next schedule; deriving every list from SCHEDULE_DEFS fixes\n"
  "     the class, and is the same change that lets a domain pack register its own.\n"
  "\n"
  "     A registered schedule needs nothing else: the renderer, the CSV export and the Project\n"
  "     Browser all read this one object. BIM_MAT_COLS is published alongside so a domain that\n"
  "     wants the Material / Volume / Mass takeoff columns reuses the same three rather than\n"
  "     inventing a parallel set that formats differently. */\n"
  "  function bimScheduleKeys(){\n"
  "    var out=[],k;\n"
  "    for(k in SCHEDULE_DEFS)if(SCHEDULE_DEFS.hasOwnProperty(k))out.push(k);\n"
  "    return out;\n"
  "  }\n"
  "  function bimRegisterSchedule(spec){\n"
  "    if(!spec||!spec.id||typeof spec.build!=='function')return false;\n"
  "    if(!spec.cols||!spec.cols.length)return false;\n"
  "    SCHEDULE_DEFS[spec.id]={label:spec.label||spec.id,build:spec.build,cols:spec.cols.slice()};\n"
  "    bimSyncScheduleCats();\n"
  "    if(el.browser)refreshBrowser();\n"
  "    return true;\n"
  "  }\n"
  "  /* The category select is hidden (the Project Browser is the chooser), but it is still the\n"
  "     element refreshSchedule and the CSV export read their category from -- so it has to carry\n"
  "     every registered id or a registered schedule could be listed and then fail to open. */\n"
  "  function bimSyncScheduleCats(){\n"
  "    if(!el.schedcat)return;\n"
  "    var keys=bimScheduleKeys(),h='',i,cur=el.schedcat.value;\n"
  "    for(i=0;i<keys.length;i++)\n"
  "      h+='<option value=\"'+bimEsc(keys[i])+'\">'+bimEsc(SCHEDULE_DEFS[keys[i]].label)+'</option>';\n"
  "    if(el.schedcat.innerHTML!==h){\n"
  "      el.schedcat.innerHTML=h;\n"
  "      if(cur&&SCHEDULE_DEFS[cur])el.schedcat.value=cur;\n"
  "    }\n"
  "  }\n"
  "  function bimFmtScheduleValue(v,fmt){")

# --------------------------------------------------------------- 2. browser lists every schedule
P('browser.keys',
  "    var schedKeys=['room','door','window','wall','ceiling','column'];",
  "    /* __acad3dV74: derived, not listed. The literal this replaced omitted 'beam', which made a\n"
  "       working schedule unreachable for as long as it existed. */\n"
  "    var schedKeys=bimScheduleKeys();")

P('sheetsource.keys',
  "    var schedKeys=['room','door','window','wall','ceiling','column','beam'];\n"
  "    schedKeys.forEach(function(k){\n"
  "      if(SCHEDULE_DEFS[k])out.push({kind:'schedule',refId:k,label:'Schedule: '+SCHEDULE_DEFS[k].label});\n"
  "    });",
  "    /* __acad3dV74: derived too -- a registered schedule has to be placeable on a sheet, or the\n"
  "       takeoff it produces cannot reach a drawing set. */\n"
  "    bimScheduleKeys().forEach(function(k){\n"
  "      out.push({kind:'schedule',refId:k,label:'Schedule: '+SCHEDULE_DEFS[k].label});\n"
  "    });")

# --------------------------------------------------------------- 3. select built from the registry
P('markup.select',
  "          '<select id=\"a3d-schedcat\" style=\"display:none\">'+\n"
  "            '<option value=\"room\">Rooms</option><option value=\"door\">Doors</option>'+\n"
  "            '<option value=\"window\">Windows</option><option value=\"wall\">Walls</option>'+\n"
  "            '<option value=\"ceiling\">Ceilings</option><option value=\"column\">Columns</option>'+\n"
  "            '<option value=\"beam\">Beams</option>'+\n"
  "          '</select>'+",
  "          /* __acad3dV74: options are generated from SCHEDULE_DEFS by bimSyncScheduleCats, so a\n"
  "             registered schedule cannot be listed in the browser and then fail to open here. */\n"
  "          '<select id=\"a3d-schedcat\" style=\"display:none\"></select>'+")

P('wire.syncsel',
  "    el.schedcat=root.querySelector('#a3d-schedcat');\n"
  "    if(el.schedcat)el.schedcat.addEventListener('change',function(){refreshSchedule();});",
  "    el.schedcat=root.querySelector('#a3d-schedcat');\n"
  "    bimSyncScheduleCats();\n"
  "    if(el.schedcat)el.schedcat.addEventListener('change',function(){refreshSchedule();});")

# --------------------------------------------------------------- apply
out = src
for name, old, new, count in patches:
    n = out.count(old)
    if n != count:
        sys.exit('ANCHOR %s matched %d times (need exactly %d)' % (name, n, count))
    out = out.replace(old, new)
    print('  applied %-20s x%d' % (name, count))

assert "schedKeys=['room'" not in out, 'the hardcoded browser list survives'
assert '<option value="beam">' not in out, 'the hardcoded option list survives'
assert 'bimRegisterSchedule' in out
io.open(PATH, 'w', encoding='utf-8').write(out)
nraw = io.open(PATH, 'rb').read()
print('\nwrote %d bytes (%+d)' % (len(nraw), len(nraw) - len(raw)))
print('sha256 %s' % hashlib.sha256(nraw).hexdigest())
