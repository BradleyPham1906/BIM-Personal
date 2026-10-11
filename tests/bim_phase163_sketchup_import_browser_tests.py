#!/usr/bin/env python3
"""bim_phase163_sketchup_import_browser_tests.py -- V163: a SketchUp file opens as this app's objects.

The owner asked for openskp's code in the app and chose "Open .skp files": its reader goes in, and a
SketchUp file comes in as faces and solids, materials and textures, tags as layers, components as
blocks. The file opened is tests/skp/site_kit.skp, written by openskp's own writer from geometry
defined in tools/openskp/make_fixtures.mjs; what each object must be -- its bounds, area, colour,
tag, kind -- is site_kit.expected.json, worked out by that script from the same geometry, never read
back through the reader.

  1. THE READER: inlined as a script of its own before the engine, one global, its four functions,
     its three licences in the page; the marker and the version.
  2. THE FILE: the fixture is the file the expectations were made for; what a scan of it finds.
  3. THE OBJECTS: each placement and material one locked solid where SketchUp has it, its area and
     colour; a face once, not front and back; a mirrored placement the right way out; one undo step.
  4. THE LAYERS: the file's layer, a sub-layer per tag in its colour, the hidden tag off, the glass
     on a see-through sub-layer of its tag; the current layer unchanged; opened again, the same layers.
  5. THE BLOCKS: the named components in Assets, in their own frame; inserted where asked; the group
     not one; opened again, replaced, not doubled; the library's Import keeps blocks only.
  6. THE NAMES: SketchUp's own names in any language are not blocks; Make Unique's are.
  7. WHAT GOES WRONG: a cut-off file, not a SketchUp file, an empty one, no reader, the limits.
  8. THE WAYS IN: Import CAD, the SKPIN command, the Assets library's Import, the command search.
  9. PROPERTIES: where each object came from in the file.
 10. KEPT WITH THE PROJECT: a reload.
 11. A TABLET AND A PHONE.

The harness never waits without a bound (V123).
"""
import asyncio, base64, hashlib, json, pathlib, sys, traceback

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from bim_phase133_site_context_browser_tests import Checks, Stalled, within   # noqa: E402
from playwright.async_api import async_playwright   # noqa: E402

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'
HERE = pathlib.Path(__file__).resolve().parent
SKP = (HERE / 'skp' / 'site_kit.skp').read_bytes()
EXP = json.loads((HERE / 'skp' / 'site_kit.expected.json').read_text())
B64 = base64.b64encode(SKP).decode()
CK = Checks()
TOL = 1e-3


def near(a, b, tol=TOL):
    return a is not None and b is not None and abs(a - b) <= tol


def box_near(o, b, tol=TOL):
    return all(near(o['min'][k], b['min'][k], tol) and near(o['max'][k], b['max'][k], tol) for k in range(3))


async def run():
    ck = CK
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()

        async def open_page(vw, vh, ctx=None):
            ctx = ctx or await browser.new_context(viewport={'width': vw, 'height': vh})
            pg = await ctx.new_page()
            errs = []
            pg.on('pageerror', lambda e: errs.append(str(e)))
            await within(pg.goto('file://' + str(HTML)), 'goto')
            await pg.wait_for_timeout(2300)
            return ctx, pg, errs

        ctx, page, errs = await open_page(1440, 900)

        async def safe(js, arg=None, pg=None):
            pg = pg or page
            try:
                return await within(pg.evaluate(js, arg) if arg is not None else pg.evaluate(js), 'evaluate ' + js[:60].replace('\n', ' '))
            except Stalled:
                raise
            except Exception as e:
                print('      (evaluate failed: %s)' % str(e)[:200])
                return None

        async def imp(name='site_kit.skp', opt=None, b64=None, pg=None):
            return await safe("([b,n,o])=>window.__a3dSkpImport(b,n,o)", [B64 if b64 is None else b64, name, opt or {}], pg=pg) or {}

        async def skp_objs(pg=None):
            return await safe("()=>window.__a3dSkpObjects()", pg=pg) or []

        async def layers(pg=None):
            return await safe("()=>window.__a3dLayers()", pg=pg) or []

        async def lib(pg=None):
            return await safe("()=>window.__a3dLibrary()", pg=pg) or []

        async def toast(pg=None):
            return await safe("()=>{var t=document.getElementById('a3d-toast');return t?t.textContent:'';}", pg=pg) or ''

        async def clear_toast(pg=None):
            await safe("()=>{var t=document.getElementById('a3d-toast');if(t)t.textContent='';}", pg=pg)

        async def wait_for(js, arg=None, n=60, pg=None):
            for _ in range(n):
                v = await safe(js, arg, pg=pg)
                if v:
                    return v
                await (pg or page).wait_for_timeout(100)
            return None

        async def fresh():
            """an empty project and library: a browser context of its own (the app saves as a page
            unloads, so clearing the storage and reloading would bring the last project back)"""
            nonlocal ctx, page, errs
            old_errs = errs
            await ctx.close()
            ctx, page, errs = await open_page(1440, 900)
            errs.extend(old_errs)

        async def props_html(pg=None):
            return await safe("()=>{window.__a3dRefreshProps();var b=document.getElementById('a3d-propsbody');return b?b.innerHTML:'';}", pg=pg) or ''

        def by_name(objs, n):
            m = [o for o in objs if o['name'] == n]
            return m[0] if len(m) == 1 else None

        def exp_obj(n):
            return [e for e in EXP['objects'] if e['name'] == n][0]

        try:
            # ---------------------------------------------------------------------------------
            print("\n-- 1. the reader")
            sc = await safe("""()=>{var S=Array.prototype.slice.call(document.scripts),r=-1,e=-1,i;
                for(i=0;i<S.length;i++){var t=S[i].textContent||'';
                  if(t.indexOf('var OpenSkp=(function(){')>=0&&r<0)r=i;
                  if(t.indexOf('/* The BIM engine: the model and its objects')>=0&&e<0)e=i;}
                var R=r>=0?S[r].textContent:'';
                return {r:r,e:e,n:S.length,reader:R.indexOf('The BIM engine')<0,
                  mit:(R.match(/Permission is hereby granted, free of charge/g)||[]).length,
                  isc:R.indexOf('Permission to use, copy, modify, and/or distribute this software')>=0,
                  owners:['Ahsan Mehmood','Arjun Barrett','Mapbox'].filter(function(w){return R.indexOf('Copyright (c)')>=0&&R.indexOf(w)>=0;})};}""") or {}
            ck(sc.get('r', -1) >= 0 and sc.get('e', -1) == sc.get('r') + 1 and sc.get('reader'),
               "the reader is a script of its own, just before the engine's (%s)" % {k: sc.get(k) for k in ('r', 'e', 'n')})
            ck(sc.get('mit') == 2 and sc.get('isc') and sc.get('owners') == ['Ahsan Mehmood', 'Arjun Barrett', 'Mapbox'],
               "and carries openskp's and fflate's MIT notices and earcut's ISC notice, with their owners (%s)" % sc)
            api = await safe("()=>window.__a3dSkpReader()")
            ck(api == ['SkpParseError', 'buildInstancedScene', 'buildScene', 'parseSkp'], "OpenSkp offers its four functions (%s)" % api)
            glob = await safe("""()=>['SkpParseError','parseSkp','buildScene','buildInstancedScene','__extends','__generator','__assign','__spreadArray','earcut','unzipSync']
                .filter(function(k){return typeof window[k]!=='undefined';})""")
            ck(glob == [], "and leaves nothing else on the page: its helpers stay inside it (%s)" % glob)
            ck('skpimport' in (await safe("()=>window.__acad3dV163") or ''), "the V163 marker is there")
            ver = await safe("""()=>{var m=Array.prototype.map.call(document.scripts,function(s){return s.textContent;}).join('').match(/var BIM_APP_VERSION=\\{v:'(V\\d+)'/);return m?m[1]:null;}""")
            ck(ver == 'V163', "and the app says V163 (%s)" % ver)

            # ---------------------------------------------------------------------------------
            print("\n-- 2. the file")
            ck(hashlib.sha256(SKP).hexdigest() == EXP['sha256'], "site_kit.skp is the file its expectations were worked out for")
            scan = await safe("(b)=>window.__a3dSkpScan(b,'site_kit.skp')", B64) or {}
            ck(scan.get('format') == EXP['format'] and scan.get('zip') is False,
               "it was saved by %s, in the archive container (%s, zip %s)" % (EXP['format'], scan.get('format'), scan.get('zip')))
            ck(scan.get('parts') == len(EXP['objects']) and scan.get('blocks') == [b['name'] for b in EXP['blocks']],
               "a scan finds %d pieces and the components %s (%s, %s)" % (len(EXP['objects']), [b['name'] for b in EXP['blocks']], scan.get('parts'), scan.get('blocks')))
            ck(all((scan.get('tags') or {}).get(t, {}).get('color') == v['color'] and (scan.get('tags') or {}).get(t, {}).get('hidden') == v['hidden']
                   for t, v in EXP['tags'].items()),
               "and every tag's colour and visibility as the file has them (%s)" % scan.get('tags'))

            # ---------------------------------------------------------------------------------
            print("\n-- 3. the objects")
            await fresh()
            ly_before = await safe("()=>window.__a3dActiveLayer?window.__a3dActiveLayer():null")
            n_layers0 = len(await layers())
            n_objs0 = len(await safe("()=>window.__a3dObjects()") or [])
            r = await imp()
            objs = await skp_objs()
            ck(not r.get('error') and len(r.get('ids', [])) == len(EXP['objects']) and len(objs) == len(EXP['objects']),
               "%d objects come in (%s)" % (len(EXP['objects']), r.get('error') or len(objs)))
            ck(all(o['t'] == 'solid' and o['locked'] for o in objs), "each a locked solid, as an OBJ's and an IFC's are")
            for e in EXP['objects']:
                o = by_name(objs, e['name'])
                if not o:
                    ck(False, "%s comes in, once (%s)" % (e['name'], [x['name'] for x in objs]))
                    continue
                ck(box_near(o, e['bounds']), "%s is where SketchUp has it, in metres with north at -Z (%s .. %s)" % (
                    e['name'], [round(x, 4) for x in o['min']], [round(x, 4) for x in o['max']]))
                ck(near(o['area'], e['area']) and o['col'] == e['color'],
                   "  its area is %.4f m2 and its colour %s (%.4f, %s)" % (e['area'], e['color'], o['area'], o['col']))
                ck(o['skp']['kind'] == e['kind'] and o['skp']['material'] == e['material'] and o['skp']['texture'] == e.get('texture', '')
                   and (o['skp']['tag'] or None) == e['tag'] and near(o['skp']['opacity'], e.get('opacity', 1)),
                   "  it is a %s, %s%s, on %s (%s)" % (e['kind'], e['material'], ' with ' + e['texture'] if e.get('texture') else '',
                                                       e['tag'] or 'no tag', {k: o['skp'][k] for k in ('kind', 'material', 'texture', 'tag', 'opacity')}))
            # seven boxes of 12, the pane's 2, the slab's 8 round its hole, the tiles' 2 and the bare face's 2
            ck(sum(o['tris'] for o in objs) == r.get('triangles') == 98,
               "98 triangles in all: every face once, its back side not a second copy (%s, %s)" % (sum(o['tris'] for o in objs), r.get('triangles')))
            boxes = [o for o in objs if o['name'] in ('Group', 'Chair A', 'Chair B', 'Chair C', 'Chair D', 'Desk 1', 'Desk chair')]
            ck(len(boxes) == 7 and all(o['tris'] == 12 and o['verts'] == 8 for o in boxes),
               "a box is 12 triangles on 8 welded corners, its faces joined (%s)" % [(o['name'], o['tris'], o['verts']) for o in boxes])
            ca, cd = by_name(objs, 'Chair A'), by_name(objs, 'Chair D')
            v = exp_obj('Chair A')['volume']
            ck(ca and cd and near(abs(ca['vol']), v) and near(ca['vol'], cd['vol']),
               "the mirrored Chair D is the right way out: its volume %.4f m3 has Chair A's sign (%s, %s)" % (v, ca and round(ca['vol'], 4), cd and round(cd['vol'], 4)))
            chk = [await safe("(id)=>window.__a3dSolidCheck(id)", o['id']) for o in boxes]
            ck(all(c and c.get('valid') for c in chk), "and every box passes the solid check: closed, one piece, faces outward (%s)" % [
                (c or {}).get('valid') for c in chk])
            await safe("()=>window.__a3dUndo()")
            ck(len(await skp_objs()) == 0 and len(await layers()) == n_layers0 and len(await safe("()=>window.__a3dObjects()") or []) == n_objs0,
               "one Undo takes the whole file out, its layers with it")
            await safe("()=>window.__a3dRedo()")
            ck(len(await skp_objs()) == len(EXP['objects']), "and Redo puts it back")

            # ---------------------------------------------------------------------------------
            print("\n-- 4. the layers")
            L = await layers()
            byn = {l['name']: l for l in L}
            fl = byn.get('site_kit')
            ck(fl and not fl.get('parent'), "the file has a layer of its own, site_kit (%s)" % (fl and fl.get('parent')))
            for t, tv in EXP['tags'].items():
                tl = byn.get('site_kit - ' + t)
                ck(tl and fl and tl.get('parent') == fl['id'] and tl.get('color') == tv['color'] and (tl.get('visible') is not False) == (not tv['hidden']),
                   "the tag %s is a sub-layer of it, %s, %s (%s)" % (t, tv['color'], 'off' if tv['hidden'] else 'on',
                                                                    tl and {k: tl.get(k) for k in ('parent', 'color', 'visible')}))
            st = byn.get(EXP['seeThrough']['layer'])
            win = byn.get(EXP['seeThrough']['parent'])
            ck(st and win and st.get('parent') == win['id'] and st.get('transparency') == EXP['seeThrough']['transparency'],
               "the glass is on %s, under its tag, at %d%% (%s)" % (EXP['seeThrough']['layer'], EXP['seeThrough']['transparency'],
                                                                   st and {k: st.get(k) for k in ('parent', 'transparency')}))
            objs = await skp_objs()
            ck(by_name(objs, 'Pane 1') and by_name(objs, 'Pane 1')['layerName'] == EXP['seeThrough']['layer'], "and Pane 1 is on it")
            ck(all(by_name(objs, n) and by_name(objs, n)['layerName'] == 'site_kit' for n in ('Concrete faces', 'Tiles faces')),
               "untagged faces are on the file's layer itself")
            ck(by_name(objs, 'Chair C')['layerName'] == 'site_kit - Hidden stuff', "Chair C is on the tag SketchUp had off")
            ck(await safe("()=>window.__a3dActiveLayer?window.__a3dActiveLayer():null") == ly_before, "the current layer is still the current layer")
            n1 = len(await layers())
            r2 = await imp()
            ck(not r2.get('error') and len(await layers()) == n1 and r2.get('layers') == [],
               "opened again, it goes on the same layers, making none (%s)" % r2.get('layers'))
            await safe("()=>window.__a3dUndo()")
            await fresh()
            own = await safe("()=>window.__a3dLayerNew({name:'site_kit - Walls'})")
            if own:
                r3 = await imp()
                L3 = {l['name']: l for l in await layers()}
                ck('site_kit - Walls 2' in L3 and L3['site_kit - Walls 2'].get('parent') == L3['site_kit']['id']
                   and not L3['site_kit - Walls'].get('parent'),
                   "a project's own layer of the same name is not taken over: the tag gets site_kit - Walls 2 (%s)" % sorted(L3))
            else:
                ck(False, "the layer hook made a layer")

            # ---------------------------------------------------------------------------------
            print("\n-- 5. the blocks")
            await fresh()
            r = await imp()
            B = [e for e in await lib() if e['kind'] == 'block' and e['category'] == 'SketchUp']
            ck(sorted(e['name'] for e in B) == sorted(b['name'] for b in EXP['blocks']) and all(e['source'] == 'site_kit.skp' and e['thumb'] for e in B),
               "the named components are blocks in Assets, from site_kit.skp, with thumbnails (%s)" % [(e['name'], e['source'], e['thumb']) for e in B])
            ck('Group' not in [e['name'] for e in B] and 'Group#1' not in [e['name'] for e in B], "the group is not one")
            chair = [e for e in B if e['name'] == 'Chair']
            if chair:
                elev = (await safe("()=>window.__a3dActiveLevel()") or {}).get('elev', 0)
                ids = await safe("([id,x,z])=>window.__a3dBlockInsert(id,x,z)", [chair[0]['id'], 20, 30]) or []
                ins = [o for o in await skp_objs() if o['id'] in ids]
                bb = EXP['blocks'][0]['bounds']
                want = {'min': [bb['min'][0] + 20, bb['min'][1] + elev, bb['min'][2] + 30], 'max': [bb['max'][0] + 20, bb['max'][1] + elev, bb['max'][2] + 30]}
                ck(len(ins) == 1 and box_near(ins[0], want) and near(ins[0]['area'], EXP['blocks'][0]['area']),
                   "the Chair block goes in with its insertion point where asked (%s)" % (ins and [[round(x, 3) for x in ins[0]['min']], [round(x, 3) for x in ins[0]['max']]]))
                ck(ins and not ins[0]['locked'] and ins[0]['layerName'] == 'site_kit - Furniture',
                   "unlocked, on its tag's layer (%s)" % str(ins and (ins[0]['locked'], ins[0]['layerName'])))
                await safe("()=>window.__a3dUndo()")
            else:
                ck(False, "there is a Chair block")
            desk = [e for e in B if e['name'] == 'Desk']
            xd = [b for b in EXP['blocks'] if b['name'] == 'Desk'][0]
            if desk:
                ids = await safe("([id,x,z])=>window.__a3dBlockInsert(id,x,z)", [desk[0]['id'], -40, 5]) or []
                ins = [o for o in await skp_objs() if o['id'] in ids]
                mn = [min(o['min'][k] for o in ins) for k in range(3)] if ins else None
                mx = [max(o['max'][k] for o in ins) for k in range(3)] if ins else None
                want = {'min': [xd['bounds']['min'][0] - 40, xd['bounds']['min'][1] + elev, xd['bounds']['min'][2] + 5],
                        'max': [xd['bounds']['max'][0] - 40, xd['bounds']['max'][1] + elev, xd['bounds']['max'][2] + 5]}
                ck(len(ins) == xd['count'] and box_near({'min': mn, 'max': mx}, want) and near(sum(o['area'] for o in ins), xd['area']),
                   "the Desk block holds its top and the chair placed in it, in the desk's own frame (%s)" % (ins and [[round(x, 3) for x in mn], [round(x, 3) for x in mx]]))
                await safe("()=>window.__a3dUndo()")
            else:
                ck(False, "there is a Desk block")
            r2 = await imp()
            B2 = [e for e in await lib() if e['kind'] == 'block' and e['category'] == 'SketchUp']
            ck(len(B2) == len(B) and set(e['id'] for e in B2).isdisjoint(set(e['id'] for e in B)),
               "opened again, the file's blocks are replaced, not doubled (%d, %d)" % (len(B), len(B2)))
            stored = await safe("()=>{try{return JSON.parse(localStorage.getItem('acad3dFamilyLibrary')).filter(function(e){return e.category==='SketchUp';}).length;}catch(e){return -1;}}")
            ck(stored == len(B2), "and the library is saved with them (%s)" % stored)
            await fresh()
            n0 = len(await skp_objs())
            rb = await imp(opt={'blocksOnly': True})
            ck(not rb.get('error') and rb.get('ids') == [] and len(await skp_objs()) == n0 and sorted(rb.get('blocks', [])) == sorted(b['name'] for b in EXP['blocks']),
               "the library's Import keeps the components as blocks and places nothing (%s)" % {k: rb.get(k) for k in ('ids', 'blocks', 'error')})
            ck('3 components from site_kit.skp kept as blocks in Assets' in (rb.get('text') or ''), "and says so (%s)" % rb.get('text'))
            await safe("()=>window.__a3dSkpLimits({blockTris:5})")
            r1 = await imp()
            ck(r1.get('blocks') == ['Pane'] and '; 1 component kept as a block in Assets' in (r1.get('text') or '')
               and '2 components are over 5 triangles' in (r1.get('text') or ''),
               "one block is 'a block', one too large 'is' (%s)" % r1.get('text'))
            await safe("()=>window.__a3dUndo()")
            await safe("()=>window.__a3dSkpLimits({blockTris:6000})")

            # ---------------------------------------------------------------------------------
            print("\n-- 6. the names")
            G = lambda n, d=None: safe("([n,d])=>window.__a3dSkpGenerated(n,d)", [n, d or []])
            ck(await G('Group#1') is True and await G('Component#12') is True, "Group#1 and Component#12 are SketchUp's own names")
            ck(await G('Agrupar#2') is True and await G('Componente#1') is True and await G('Gruppe#3') is True,
               "so are a Portuguese file's Agrupar#2 and Componente#1, and a German Gruppe#3")
            ck(await G('Chair#1', ['Chair', 'Chair#1']) is False, "Chair#1 beside a Chair is Make Unique's copy, a component of its own")
            ck(await G('Chair') is False and await G('Wall #3 east') is False, "Chair and Wall #3 east are names someone gave")

            # ---------------------------------------------------------------------------------
            print("\n-- 7. what goes wrong")
            await fresh()
            n0 = len(await safe("()=>window.__a3dObjects()") or [])
            cut = await imp('cut.skp', b64=base64.b64encode(SKP[:len(SKP) // 2]).decode())
            ck(str(cut.get('error', '')).startswith('Could not read cut.skp as a SketchUp file: '),
               "a file cut off half way says it could not be read, and why (%s)" % cut.get('error'))
            junk = await imp('notes.skp', b64=base64.b64encode(b'not a sketchup model at all, just text' * 20).decode())
            ck(str(junk.get('error', '')).startswith('Could not read notes.skp as a SketchUp file'), "so does a file that is not SketchUp's (%s)" % junk.get('error'))
            empty = await imp('empty.skp', b64='')
            ck(empty.get('error') == 'empty.skp is empty', "an empty file says it is empty (%s)" % empty.get('error'))
            ck(len(await safe("()=>window.__a3dObjects()") or []) == n0 and len(await skp_objs()) == 0,
               "and none of them changes the model")
            gone = await safe("""([b])=>{var k=window.OpenSkp;window.OpenSkp=undefined;var r;try{r=window.__a3dSkpImport(b,'site_kit.skp');}finally{window.OpenSkp=k;}return r;}""", [B64]) or {}
            ck(str(gone.get('error', '')).startswith('The SketchUp reader did not load in this browser'), "with no reader, it says the reader did not load (%s)" % gone.get('error'))
            half = await safe("""([b])=>{var k=window.OpenSkp;window.OpenSkp={parseSkp:k.parseSkp};var r;try{r=window.__a3dSkpImport(b,'site_kit.skp');}finally{window.OpenSkp=k;}return r;}""", [B64]) or {}
            ck(str(half.get('error', '')).startswith('The SketchUp reader did not load in this browser'),
               "and so with an OpenSkp that lacks the reader's functions, rather than failing inside it (%s)" % half.get('error'))
            await safe("()=>window.__a3dSkpLimits({maxTris:40})")
            rt = await imp()
            ck(rt.get('truncated') is True and 0 < rt.get('triangles', 99) <= 40 and sum(o['tris'] for o in await skp_objs()) == rt.get('triangles')
               and 'stopped at 40 triangles' in (rt.get('text') or ''),
               "past its triangle limit it stops, keeps what it read, and says where (%s, %s)" % (rt.get('triangles'), rt.get('text')))
            await safe("()=>window.__a3dUndo()")
            await safe("()=>window.__a3dSkpLimits({maxTris:250000,blockTris:1})")
            rbt = await imp()
            ck(rbt.get('blocksTooBig') == 3 and rbt.get('blocks') == [] and 'too large to keep as a block' in (rbt.get('text') or ''),
               "a component over the block limit is not kept as a block, and it says so (%s)" % rbt.get('blocksTooBig'))
            await safe("()=>window.__a3dUndo()")
            await safe("()=>window.__a3dSkpLimits({blockTris:6000,blockChars:3000})")
            rbr = await imp()
            ck(rbr.get('blocksNoRoom', 0) >= 1 and 'did not fit in the library' in (rbr.get('text') or ''),
               "blocks past the library's room are left out, and it says so (%s)" % rbr.get('blocksNoRoom'))
            await safe("()=>window.__a3dUndo()")
            await safe("()=>window.__a3dSkpLimits({maxTris:250000,blockTris:6000,blockChars:1500000})")

            # ---------------------------------------------------------------------------------
            print("\n-- 8. the ways in")
            await fresh()
            acc = await safe("()=>document.getElementById('a3d-filein').getAttribute('accept')") or ''
            ck('.skp' in acc.split(','), "Import CAD takes .skp (%s)" % acc)
            await clear_toast()
            await page.set_input_files('#a3d-filein', files=[{'name': 'site_kit.skp', 'mimeType': 'application/octet-stream', 'buffer': SKP}])
            got = await wait_for("()=>window.__a3dSkpObjects().length")
            t = await toast()
            ck(got == len(EXP['objects']) and 'SketchUp: 11 objects from site_kit.skp (saved by SketchUp 2017) on the site_kit layer' in t,
               "and opens one, saying what came in (%s, %r)" % (got, t))
            await fresh()
            async with page.expect_file_chooser() as fc:
                await safe("()=>window.__a3dRunCmd('skpin')")
            ch = await fc.value
            ck(ch.element and await ch.element.get_attribute('accept') == '.skp', "SKPIN asks for a .skp file")
            await ch.set_files(files=[{'name': 'site_kit.skp', 'mimeType': 'application/octet-stream', 'buffer': SKP}])
            ck(await wait_for("()=>window.__a3dSkpObjects().length") == len(EXP['objects']), "and opens it")
            cat = [c for c in (await safe("()=>window.__a3dCommandCatalog()") or []) if c.get('name') == 'SKPIN']
            ck(len(cat) == 1, "SKPIN is in the command catalog (%s)" % cat)
            for q_ in ('sketchup', 'skp', 'importskp', '3d warehouse'):
                nm = [x['name'] for x in (await safe("(q)=>window.__a3dCommandSearch(q,5)", q_) or [])]
                ck('SKPIN' in nm[:3], "searching %r finds it (%s)" % (q_, nm))
            await fresh()
            facc = await safe("()=>document.getElementById('a3d-famfilein').getAttribute('accept')") or ''
            ck('.skp' in facc.split(','), "the library's Import takes .skp too (%s)" % facc)
            await page.set_input_files('#a3d-famfilein', files=[{'name': 'site_kit.skp', 'mimeType': 'application/octet-stream', 'buffer': SKP}])
            bl = await wait_for("()=>window.__a3dLibrary().filter(function(e){return e.category==='SketchUp';}).length")
            ck(bl == 3 and len(await skp_objs()) == 0, "and keeps the file's components as blocks, placing nothing (%s)" % bl)
            await page.click('#a3d-rail .a3d-railbtn[data-tab="assets"]')
            await page.wait_for_timeout(300)
            tiles = await safe("""()=>Array.prototype.map.call(document.querySelectorAll('#a3d-leftpanel [data-a3dassets^="block:"]'),function(b){
                var m=b.querySelector('.a3d-asmeta');return {n:(b.querySelector('.a3d-asnm')||{}).textContent,m:m?m.textContent:''};})""") or []
            ck(sorted(x['n'] for x in tiles if x['m'].startswith('SketchUp, ')) == ['Chair', 'Desk', 'Pane'],
               "the Assets panel shows them as SketchUp blocks (%s)" % tiles)
            imp_tip = await safe("()=>{var b=document.querySelector('#a3d-leftpanel [data-a3dasact=\"import\"]');return b?b.getAttribute('title'):'';}") or ''
            ck('SketchUp' in imp_tip, "and its Import says it takes a SketchUp file's components (%r)" % imp_tip)
            await page.click('#a3d-leftpanel [data-a3dassearch]')
            await page.keyboard.type('site_kit')
            await page.wait_for_timeout(250)
            vis = await safe("""()=>Array.prototype.filter.call(document.querySelectorAll('#a3d-leftpanel [data-a3dassets^="block:"]'),
                function(e){return e.offsetParent!==null;}).length""")
            ck(vis == 3, "searching the library for the file's name finds its blocks (%s)" % vis)
            await page.keyboard.press('Escape')
            await page.click('#a3d-rail .a3d-railbtn[data-tab="properties"]') if await safe("()=>!!document.querySelector('#a3d-rail .a3d-railbtn[data-tab=\"properties\"]')") else None

            # ---------------------------------------------------------------------------------
            print("\n-- 9. properties")
            await fresh()
            await imp()
            objs = await skp_objs()

            async def props_of(n):
                o = by_name(objs, n)
                await safe("(id)=>window.__a3dSelectFor([id])", o['id'])
                return await props_html()
            h = await props_of('Chair B')
            ck('data-a3dpgrp="SketchUp"' in h and 'site_kit.skp, SketchUp 2017' in h and 'Chair (Chair B)' in h and '>Furniture<' in h and '>Oak<' in h,
               "Chair B's Properties say it is the Chair component on Furniture, in Oak, from site_kit.skp")
            h = await props_of('Group')
            ck('>Group<' in h and 'unnamed (Group#1)' in h and '>Walls<' in h and '>Brick<' in h, "the group says it is an unnamed group")
            h = await props_of('Tiles faces')
            ck('loose, in no group or component' in h and 'tiles.png, drawn in the colour SketchUp keeps with it' in h and '>Untagged<' in h,
               "the tiles name their texture's file, and say they are drawn in its colour")
            h = await props_of('Desk chair')
            ck('>Inside<' in h and '>Desk 1<' in h and 'Chair (Desk chair)' in h, "the chair in the desk says it is inside Desk 1")
            h = await props_of('Unpainted faces')
            ck('none (unpainted)' in h, "an unpainted face says so")
            h = await props_of('Pane 1')
            ck('35%, on a see-through layer' in h, "the pane says its opacity and where it went")
            await safe("()=>window.__a3dSelectFor([])")

            # ---------------------------------------------------------------------------------
            print("\n-- 10. kept with the project")
            await page.wait_for_timeout(700)
            await within(page.reload(), 'reload')
            await page.wait_for_timeout(2300)
            objs2 = await skp_objs()
            ck(len(objs2) == len(EXP['objects']) and all(by_name(objs2, e['name']) and by_name(objs2, e['name'])['skp']['file'] == 'site_kit.skp' for e in EXP['objects']),
               "after a reload every object is there with where it came from (%s)" % len(objs2))
            L2 = {l['name']: l for l in await layers()}
            ck('site_kit - Hidden stuff' in L2 and L2['site_kit - Hidden stuff'].get('visible') is False
               and L2.get(EXP['seeThrough']['layer'], {}).get('transparency') == 65,
               "and its layers as they were: the hidden tag off, the glass at 65%")
            ck(not errs, "no page errors (%s)" % errs[:3])

            # ---------------------------------------------------------------------------------
            print("\n-- 11. a tablet and a phone")
            for (w, hgt, nm) in ((820, 1180, 'tablet'), (390, 844, 'phone')):
                c2, p2, e2 = await open_page(w, hgt)
                await p2.set_input_files('#a3d-filein', files=[{'name': 'site_kit.skp', 'mimeType': 'application/octet-stream', 'buffer': SKP}])
                n = await wait_for("()=>window.__a3dSkpObjects().length", pg=p2)
                tr = await safe("()=>{var t=document.getElementById('a3d-toast');if(!t)return null;var r=t.getBoundingClientRect();return [r.left,r.right,window.innerWidth,t.textContent.length];}", pg=p2)
                ck(n == len(EXP['objects']) and tr and tr[0] >= 0 and tr[1] <= tr[2] and tr[3] > 40,
                   "on a %s (%dpx) the file opens and its message fits the screen (%s)" % (nm, w, tr))
                o2 = await skp_objs(pg=p2)
                await safe("(id)=>window.__a3dSelectFor([id])", by_name(o2, 'Chair B')['id'], pg=p2)
                h2 = await props_html(pg=p2)
                ck('data-a3dpgrp="SketchUp"' in h2 and 'Chair (Chair B)' in h2, "and its Properties tell where it came from")
                ck(not e2, "no page errors on the %s (%s)" % (nm, e2[:3]))
                await c2.close()
        except Stalled as s:
            ck(False, "the harness stalled at %s" % s)
        except Exception:
            traceback.print_exc()
            ck(False, "the suite ran to the end")
        await browser.close()
    print('\n%d/%d checks passed' % (CK.n - len(CK.bad), CK.n))
    print('RESULT: ' + ('PASS' if not CK.bad else 'FAIL'))
    return 0 if not CK.bad else 1


if __name__ == '__main__':
    sys.exit(asyncio.run(run()))
