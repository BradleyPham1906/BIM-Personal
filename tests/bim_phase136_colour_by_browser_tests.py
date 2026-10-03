#!/usr/bin/env python3
"""bim_phase136_colour_by_browser_tests.py -- V136: the colour-by-property lens, and legends.

Giraffe's lenses and GeoLibre's legends (the owner's screenshots): the model coloured by usage,
level, type, layer, material, height or any property, with a legend; a data layer coloured by one
of its attributes, at an opacity.

  1. OFF UNTIL ASKED: Colour by in the View group, no colour changed, no legend.
  2. CATEGORIES: usage (the usage's own colours), level (in level order), type, layer, material;
     no value is grey; the legend lists each with its count.
  3. NUMBERS: height in six steps from the lowest to the highest; a property, by name or number.
  4. WHERE IT SHOWS: the 3D faces (pixels), the 2D faces over Presentation's fill; the legend below
     the room legend; not on paper.
  5. KEPT: one undo step; saved with the project and back after a reload.
  6. DATA LAYERS: coloured by an attribute (categories, numbers), an unknown one refused, an
     opacity; their legend; the panel.
  7. THE COMMAND.

The harness never waits without a bound (V123).
"""
import asyncio, io, json, math, pathlib, sys, traceback
from playwright.async_api import async_playwright
from PIL import Image

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'


class Checks:
    def __init__(self):
        self.n, self.bad = 0, []

    def __call__(self, cond, msg):
        self.n += 1
        if not cond:
            self.bad.append(msg)
        print(('  ok    ' if cond else '  FAIL  ') + msg)


CK = Checks()
STALL = 60


class Stalled(Exception):
    pass


async def within(aw, what):
    try:
        return await asyncio.wait_for(aw, STALL)
    except asyncio.TimeoutError:
        raise Stalled(what)


WA, WE2 = 6378137.0, 0.00669437999014
LAT0, LON0 = 39.9656683, -75.1687892
RAMP = ['#ffffb2', '#fed976', '#feb24c', '#fd8d3c', '#f03b20', '#bd0026']
SCHEME = ['#8dd3c7', '#ffffb3', '#bebada', '#fb8072', '#80b1d3', '#fdb462']
NONE = '#6b7480'


def m2g(x, z):
    s = math.sin(math.radians(LAT0))
    w = 1 - WE2 * s * s
    M, Nr = WA * (1 - WE2) / w ** 1.5, WA / math.sqrt(w)
    return [LON0 + math.degrees(x / (Nr * math.cos(math.radians(LAT0)))), LAT0 + math.degrees(-z / M)]


def sq(x0, z0, w, d):
    return [[m2g(*q) for q in [(x0, z0), (x0 + w, z0), (x0 + w, z0 + d), (x0, z0 + d), (x0, z0)]]]


def zones():
    return {'type': 'FeatureCollection', 'features': [
        {'type': 'Feature', 'properties': {'ZONE': 'CMX-3', 'AREA': 100}, 'geometry': {'type': 'Polygon', 'coordinates': sq(-100, -100, 60, 60)}},
        {'type': 'Feature', 'properties': {'ZONE': 'RSA-5', 'AREA': 400}, 'geometry': {'type': 'Polygon', 'coordinates': sq(-30, -100, 60, 60)}},
        {'type': 'Feature', 'properties': {'ZONE': 'CMX-3', 'AREA': 700}, 'geometry': {'type': 'Polygon', 'coordinates': sq(40, -100, 60, 60)}},
        {'type': 'Feature', 'properties': {'AREA': 250}, 'geometry': {'type': 'Polygon', 'coordinates': sq(-100, 40, 60, 60)}}]}


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def shaded_like(px, col, tol=0.12):
    """a lit face is its colour times one light factor: the three channels' ratios agree"""
    c = rgb(col)
    ks = [px[i] / c[i] for i in range(3) if c[i] > 30]
    return len(ks) >= 2 and max(ks) - min(ks) <= tol and 0.25 <= sum(ks) / len(ks) <= 1.5


async def run():
    ck = CK
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 1600, 'height': 950})
        page = await ctx.new_page()
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))

        async def gis(route):
            await route.fulfill(status=200, body=json.dumps(zones()), headers={'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'})
        await ctx.route('https://data.example.org/**', gis)

        await within(page.goto('file://' + str(HTML)), 'goto')
        await page.wait_for_timeout(2300)

        async def safe(js, arg=None):
            try:
                return await within(page.evaluate(js, arg) if arg is not None else page.evaluate(js), 'evaluate ' + js[:50])
            except Stalled:
                raise
            except Exception as e:
                print('      (evaluate failed: %s)' % str(e)[:200])
                return None

        has = await safe("()=>!!window.__acad3dV136")
        ck(bool(has), "__acad3dV136 marker is present")
        if not has:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.bad), ck.n))
            await browser.close()
            return 1

        async def toast():
            return await safe("()=>{var t=document.getElementById('a3d-toast');return t?t.textContent:'';}") or ''

        async def nosel():
            await safe("()=>{window.__a3dSelectFor([]);window.__a3dRefreshProps();}")
            await page.wait_for_timeout(60)

        async def props_html():
            return await safe("()=>document.getElementById('a3d-propsbody').innerHTML") or ''

        async def set_field(sel, val):
            ok = await safe("""(a)=>{var e=document.querySelector('#a3d-propsbody '+a[0]);if(!e)return false;
              if(e.type==='checkbox')e.checked=!!a[1];else e.value=a[1];e.dispatchEvent(new Event('change',{bubbles:true}));return true;}""", [sel, val])
            await page.wait_for_timeout(150)
            return ok

        async def lens(by=None, prop=None):
            if by is None:
                return await safe("()=>window.__a3dLens()")
            return await safe("(a)=>window.__a3dLens(a[0],a[1])", [by, prop])

        async def col(i):
            return await safe("(i)=>window.__a3dLensCol(i)", i)

        async def legend():
            await safe("()=>window.__a3dTestPaint()")
            return await safe("()=>window.__a3dLensLegend()")

        async def oset(i, k, v):
            return await safe("(a)=>window.__a3dTestObjSet(a[0],a[1],a[2])", [i, k, v])

        try:
            # ---------------------------------------------------------------------------------
            print("\n-- 1. off until asked")
            await safe("()=>{window.__a3dTestSetObjs([]);window.__a3dSelectFor([]);}")
            ids = []
            for L, W, H in ((4, 4, 3), (4, 4, 8), (4, 4, 15), (4, 4, 6)):
                ids.append(await safe("(a)=>window.__a3dAdd('box',{Length:a[0],Width:a[1],Height:a[2]}).id", [L, W, H]))
            A, B, C, D = ids
            ck(all(ids), "four boxes, 3, 8, 15 and 6 units tall")
            ck(await lens() == {'by': '', 'prop': ''}, "the lens is off")
            await nosel()
            h = await props_html()
            ck('data-proplens="by"' in h and h.count('<option', h.index('data-proplens="by"'), h.index('</select>', h.index('data-proplens="by"'))) == 8,
               "Colour by in the View group: Off and seven ways")
            ck(h.index('data-a3dpgrp="View"') < h.index('data-proplens="by"') < h.index('data-propmodel="present"'), "above Appearance")
            ck(await col(A) is None and await legend() is None, "no colour changed, no legend")

            # ---------------------------------------------------------------------------------
            print("\n-- 2. categories")
            await safe("(a)=>window.__a3dUsageAssign([a[0]],'use-res')", [A])
            await safe("(a)=>window.__a3dUsageAssign([a[0]],'use-ret')", [B])
            await safe("(a)=>window.__a3dUsageAssign([a[0]],'use-res')", [D])
            await safe("()=>window.__a3dMapSet('opacity',70)")   # the step before, so the lens's undo is its own
            r = await lens('usage')
            ck(r == {'by': 'usage', 'prop': ''}, "by usage")
            ck(await col(A) == '#e8a33d' and await col(B) == '#d6584e' and await col(D) == '#e8a33d', "each in its usage's own colour")
            ck(await col(C) == NONE, "one with no usage is grey")
            lg = await legend()
            b0 = (lg or {}).get('blocks', [{}])[0]
            ck(b0.get('title') == 'Coloured by usage' and [(x['name'], x['n'], x['col']) for x in b0.get('rows', [])] ==
               [('Residential', 2, '#e8a33d'), ('Retail', 1, '#d6584e'), ('no value', 1, NONE)], "the legend: each usage, its count, and no value (%s)" % b0.get('rows'))
            ck('2 entr' not in await toast() and 'Coloured by usage: 3 entries' in await toast(), "and says so")
            # level, in level order
            await safe("()=>{window.__a3dAddLevel();window.__a3dAddLevel();}")
            await nosel()
            lvids = await safe("()=>Array.prototype.map.call(document.querySelectorAll('#a3d-propsbody [data-propmodel=\"level\"] option'),function(o){return o.value;})") or []
            ck(len(lvids) >= 3, "three levels (%d)" % len(lvids))
            for i_, lid in ((A, lvids[2]), (B, lvids[0]), (C, lvids[1]), (D, lvids[0])):
                await oset(i_, 'level', lid)
            for lid, nm in ((lvids[0], 'Ground'), (lvids[1], 'Mezzanine'), (lvids[2], 'Attic')):   # names out of alphabetical order
                await safe("(a)=>window.__a3dTestLevelName(a[0],a[1])", [lid, nm])
            await lens('level')
            ck(await col(B) == SCHEME[0] and await col(D) == SCHEME[0] and await col(C) == SCHEME[1] and await col(A) == SCHEME[2],
               "by level: in level order, not name order")
            lg = await legend()
            ck([(x['name'], x['n']) for x in lg['blocks'][0]['rows']] == [('Ground', 2), ('Mezzanine', 1), ('Attic', 1)] and lg['blocks'][0]['title'] == 'Coloured by level',
               "the legend in level order: two on the ground")
            await lens('type')
            ck(len({await col(x) for x in ids}) == 1 and (await legend())['blocks'][0]['rows'][0]['name'] == 'Box', "by type: all boxes, one colour, named")
            cy = await safe("()=>window.__a3dAdd('cyl',{Radius:1,Height:2}).id")
            ck((await safe("(i)=>window.__a3dLensValue(i)", cy) or {}).get('name') == 'Cylinder', "a type is named as the app names it: Cylinder")
            await safe("()=>window.__a3dUndo()")
            await page.wait_for_timeout(100)
            ly = await safe("()=>{var l=window.__a3dAddLayer('Massing');return l&&l.id;}")
            await oset(B, 'layer', ly)
            await lens('layer')
            names = [x['name'] for x in (await legend())['blocks'][0]['rows']]
            ck('Massing' in names and len(names) == 2 and await col(B) != await col(A), "by layer: B on Massing apart (%s)" % names)
            await oset(A, 'materialName', 'Concrete')
            await oset(C, 'materialName', 'Brick')
            await lens('material')
            ck(await col(C) == SCHEME[0] and await col(A) == SCHEME[1] and await col(B) == NONE, "by material: in name order, none grey")

            # ---------------------------------------------------------------------------------
            print("\n-- 3. numbers")
            await lens('height')
            vals = [(await safe("(i)=>window.__a3dLensValue(i)", x) or {}).get('num') for x in ids]
            ck(vals == [1.05, 2.8, 5.25, 2.1], "each box's height in metres (%s)" % vals)
            ck(await col(A) == RAMP[0] and await col(C) == RAMP[5] and await col(B) == RAMP[2] and await col(D) == RAMP[1],
               "six steps from the lowest to the highest: the shortest lightest, the tallest darkest, the others between")
            lg = await legend()
            rows = lg['blocks'][0]['rows']
            ck(lg['blocks'][0]['title'] == 'Coloured by height (m)' and len(rows) == 4 and [x['n'] for x in rows] == [1, 1, 1, 1] and
               [x['col'] for x in rows] == [RAMP[0], RAMP[1], RAMP[2], RAMP[5]] and rows[0]['name'].startswith('1.1 to ') and rows[-1]['name'].endswith(' to 5.3'),
               "the legend: the steps that hold one, each its range (%s)" % [x['name'] for x in rows])
            await oset(A, 'context', {'kind': 'buildings', 'height': 21.5, 'tags': {'building': 'house', 'building:levels': '7'}})
            await oset(B, 'geo', {'source': 'x.geojson', 'props': {'building': 'retail', 'OWNER': 'City'}})
            await oset(C, 'context', {'kind': 'buildings', 'height': 15, 'tags': {'building': 'house', 'building:levels': '5'}})
            await safe("()=>window.__a3dTestPaint()")
            ck((await safe("(i)=>window.__a3dLensValue(i)", A) or {}).get('num') == 21.5, "a context building's height is its recorded one")
            keys = await safe("()=>window.__a3dLensPropKeys()") or []
            ck(keys[:5] == ['building', 'building:levels', 'height', 'kind', 'OWNER'], "the properties objects carry, the most common first, then by name (%s)" % keys[:5])
            await lens('prop', 'building')
            ck(await col(B) == SCHEME[1] and await col(A) == SCHEME[0] and await col(C) == SCHEME[0] and await col(D) == NONE, "by a property's words: house, retail")
            await lens('prop', 'building:levels')
            ck(await col(A) == RAMP[5] and await col(C) == RAMP[0] and await col(B) == NONE, "by a property's numbers: the ramp")
            ck((await legend())['blocks'][0]['title'] == 'Coloured by building:levels', "titled by the property")
            await lens('prop', '')
            ck(await col(A) is None and await legend() is None, "Property with none picked colours nothing")
            await nosel()
            h = await props_html()
            ck('data-proplens="prop"' in h and '<option value="building">' in h, "and offers the properties to pick")

            # ---------------------------------------------------------------------------------
            print("\n-- 4. where it shows")
            await lens('height')
            await safe("()=>window.__a3dSetView('top')")
            await page.wait_for_timeout(300)
            boxes = [[-6, 0, -6], [0, 0, -6], [6, 0, -6], [-6, 0, 0]]   # add3d's grid
            cA = await col(A)
            ck(cA == RAMP[5], "the context building's 21.5 m is now the tallest")
            await safe("()=>window.__a3dCamSet({tx:0,tz:-3,dist:40})")
            await safe("()=>window.__a3dTestPaint()")
            await page.wait_for_timeout(200)
            img = Image.open(io.BytesIO(await page.screenshot())).convert('RGB')

            async def at(p):
                return await safe("(p)=>{var r=document.getElementById('a3d-canvas').getBoundingClientRect(),q=window.__a3dProject([p[0],p[1],p[2]]);return [r.left+q.x,r.top+q.y];}", p)
            sC = await at([boxes[0][0] + 0.35, 1.05, boxes[0][2] + 0.35])   # off the face's edge lines
            pxC = img.getpixel((int(sC[0]), int(sC[1])))
            ck(shaded_like(pxC, RAMP[5]), "3D: the tallest's roof is drawn in the darkest step (%s)" % (pxC,))
            await lens('')
            await safe("()=>window.__a3dTestPaint()")
            await page.wait_for_timeout(150)
            img2 = Image.open(io.BytesIO(await page.screenshot())).convert('RGB')
            pxC2 = img2.getpixel((int(sC[0]), int(sC[1])))
            ck(not shaded_like(pxC2, RAMP[5]) and shaded_like(pxC2, '#7f9db8'), "and back in its own colour with the lens off (%s)" % (pxC2,))
            await lens('height')
            await safe("()=>window.__a3dSetPresentMode(true)")
            await safe("()=>window.__a3dTestPaint()")
            dsA = await safe("(i)=>window.__a3dLastDrawStyle(i)", A)
            ck(dsA and dsA['fill'] == RAMP[5], "2D (Presentation): the face's fill is the lens's, over Presentation's (%s)" % (dsA or {}).get('fill'))
            await lens('')
            await safe("()=>window.__a3dTestPaint()")
            dsA = await safe("(i)=>window.__a3dLastDrawStyle(i)", A)
            ck(dsA and dsA['fill'] != RAMP[5], "and its own with the lens off")
            await lens('usage')
            await safe("()=>window.__a3dTestPaint()")
            f0 = (await safe("(i)=>window.__a3dLastDrawStyle(i)", D) or {}).get('fill')
            await safe("(a)=>window.__a3dUsageAssign([a[0]],'use-off')", [D])
            await safe("()=>window.__a3dTestPaint()")
            f1 = (await safe("(i)=>window.__a3dLastDrawStyle(i)", D) or {}).get('fill')
            ck(f0 == '#e8a33d' and f1 == '#4e8fd6', "worked out afresh each paint: a usage changed shows at once (%s -> %s)" % (f0, f1))
            await safe("()=>window.__a3dUndo()")
            await safe("()=>window.__a3dSetPresentMode(false)")
            await lens('usage')
            await safe("()=>window.__a3dTestPaint()")
            lg = await safe("()=>window.__a3dLensLegend()")
            ck(lg and lg['box'][0] > 0 and lg['box'][1] > 0, "the legend is drawn (%s)" % (lg or {}).get('box'))
            cap = await safe("()=>window.__a3dTestLegendOnPaper()")
            ck(cap is None, "not on paper")

            # ---------------------------------------------------------------------------------
            print("\n-- 5. kept")
            await safe("()=>window.__a3dMapSet('opacity',60)")
            await lens('height')
            await safe("()=>window.__a3dUndo()")
            await page.wait_for_timeout(100)
            ck((await lens())['by'] == 'usage' and (await safe("()=>window.__a3dMapSettings()"))['opacity'] == 0.6, "one undo step, its own")
            await safe("()=>window.__a3dRedo()")
            await page.wait_for_timeout(100)
            ck((await lens())['by'] == 'height' and await col(A) == RAMP[5], "and a redo")
            await page.wait_for_timeout(700)
            await within(page.reload(), 'reload')
            await page.wait_for_timeout(2300)
            await safe("()=>window.__a3dTestPaint()")
            ck((await lens())['by'] == 'height' and await col(A) == RAMP[5], "saved with the project, back after a reload")

            # ---------------------------------------------------------------------------------
            print("\n-- 6. data layers")
            await nosel()
            await set_field('[data-propmodel="sunlat"]', repr(LAT0))
            await set_field('[data-propmodel="sunlon"]', repr(LON0))
            await safe("()=>window.__a3dSetTrueNorth(0)")
            await lens('')
            r = await safe("()=>window.__a3dDataAdd('https://data.example.org/zoning.geojson','Zoning','#3366ff',null)") or {}
            zid = r.get('id')
            ck((r.get('result') or {}).get('count') == 4, "a zoning layer of four districts")
            ck(await safe("(i)=>window.__a3dDataAttrKeys(i)", zid) == ['AREA', 'ZONE'], "its attributes, by name")
            await nosel()
            h = await props_html()
            ck('data-propdata="by:' + zid + '"' in h and 'data-propdata="opacity:' + zid + '"' in h, "each layer: Colour by and Opacity")
            await safe("()=>window.__a3dMapSet('opacity',50)")
            await set_field('[data-propdata="by:' + zid + '"]', 'ZONE')
            L = (await safe("()=>window.__a3dDataLayers()") or [{}])[0]
            ck(L.get('by') == 'ZONE', "coloured by ZONE")
            fc = [await safe("(a)=>window.__a3dDataFeatCol(a[0],a[1])", [zid, i]) for i in range(4)]
            ck(fc == [SCHEME[0], SCHEME[1], SCHEME[0], NONE], "the same district one colour, none grey (%s)" % fc)
            lg = await legend()
            b = [x for x in (lg or {}).get('blocks', []) if x['title'] == 'Zoning: ZONE']
            ck(b and [(x['name'], x['n']) for x in b[0]['rows']] == [('CMX-3', 2), ('RSA-5', 1), ('no value', 1)], "its legend")
            await safe("()=>window.__a3dUndo()")
            await page.wait_for_timeout(100)
            ck(not (await safe("()=>window.__a3dDataLayers()") or [{}])[0].get('by') and (await safe("()=>window.__a3dMapSettings()"))['opacity'] == 0.5,
               "an undo step of its own")
            await safe("()=>window.__a3dRedo()")
            ok = await safe("(i)=>window.__a3dDataSet(i,'by','AREA')", zid)
            fc = [await safe("(a)=>window.__a3dDataFeatCol(a[0],a[1])", [zid, i]) for i in range(4)]
            ck(ok and fc == [RAMP[0], RAMP[3], RAMP[5], RAMP[1]], "by a number: the ramp (%s)" % fc)
            ok = await safe("(i)=>window.__a3dDataSet(i,'by','NOPE')", zid)
            ck(ok is False and 'no attribute NOPE' in await toast(), "an attribute it does not have is refused")
            # opacity: the fill, at half
            await safe("()=>window.__a3dSetView('top')")
            await page.wait_for_timeout(300)
            await safe("()=>window.__a3dCamSet({tx:0,tz:0,dist:260})")
            await safe("()=>window.__a3dTestObjSet&&window.__a3dTestSetObjs([])")
            await safe("()=>window.__a3dMapSet('style','off')")

            async def px_at(x, z):
                await safe("()=>window.__a3dTestPaint()")
                await page.wait_for_timeout(150)
                im = Image.open(io.BytesIO(await page.screenshot())).convert('RGB')
                s = await safe("(p)=>{var r=document.getElementById('a3d-canvas').getBoundingClientRect(),q=window.__a3dProject([p[0],0,p[1]]);return [r.left+q.x,r.top+q.y];}", [x, z])
                return im.getpixel((int(s[0]), int(s[1])))
            bg = await px_at(0, 20)
            await safe("(i)=>window.__a3dDataSet(i,'by','ZONE')", zid)
            pz = await px_at(-70, -90)
            wz = tuple(bg[i] + (rgb(SCHEME[0])[i] - bg[i]) * 0.5 for i in range(3))
            ck(all(abs(pz[i] - wz[i]) <= 8 for i in range(3)), "on the plan: a district filled in its value's colour, more strongly (%s, %s)" % (pz, wz))
            await safe("(i)=>window.__a3dDataSet(i,'by','')", zid)
            p1 = await px_at(-70, -90)
            ok = await safe("(i)=>window.__a3dDataSet(i,'opacity','40')", zid)
            L = (await safe("()=>window.__a3dDataLayers()") or [{}])[0]
            p2 = await px_at(-70, -90)
            want1 = tuple(bg[i] + (rgb('#3366ff')[i] - bg[i]) * 0.16 for i in range(3))
            want2 = tuple(bg[i] + (rgb('#3366ff')[i] - bg[i]) * 0.16 * 0.4 for i in range(3))
            ck(ok and L.get('opacity') == 0.4, "Opacity 40 (%) kept as 0.4")
            ck(all(abs(p1[i] - want1[i]) <= 8 for i in range(3)) and all(abs(p2[i] - want2[i]) <= 8 for i in range(3)) and p1 != p2,
               "the fill fades with it (%s -> %s)" % (p1, p2))
            ok = await safe("(i)=>window.__a3dDataSet(i,'opacity','abc')", zid)
            ck(ok is False and 'percentage' in await toast(), "an opacity that is not a number is refused")
            await safe("(i)=>window.__a3dDataSet(i,'opacity',5)", zid)
            ck((await safe("()=>window.__a3dDataLayers()") or [{}])[0].get('opacity') == 0.1, "and kept to 10 to 100")

            # ---------------------------------------------------------------------------------
            print("\n-- 7. the command")
            await safe("()=>window.__a3dRunCmd('colourby')")
            await page.wait_for_timeout(150)
            foc = await safe("()=>document.activeElement&&document.activeElement.getAttribute('data-proplens')")
            ck(foc == 'by' and 'Colour by is in the View group' in await toast(), "COLOURBY opens the View group at Colour by")
            await set_field('[data-proplens="by"]', 'prop')
            ck((await lens())['by'] == 'prop', "picked in the panel")
            ck(not errs, "no page errors (%s)" % errs[:2])
        except Stalled as e:
            ck(False, 'stalled: %s' % e)
        except Exception:
            traceback.print_exc()
            ck(False, 'the harness crashed')
        await browser.close()
    print("\n%d/%d checks passed\nRESULT: %s" % (ck.n - len(ck.bad), ck.n, 'PASS' if not ck.bad else 'FAIL'))
    return 0 if not ck.bad else 1


if __name__ == '__main__':
    sys.exit(asyncio.run(run()))
