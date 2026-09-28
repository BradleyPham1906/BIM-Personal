#!/usr/bin/env python3
"""bim_phase126_section_profiles_browser_tests.py -- V126: the section-profile library.

PIPELINE, Track B item 2. A column or beam type may carry a profile -- rect, circle, hss, pipe, ibeam,
channel -- whose properties are computed from its nominal dimensions, whose solid is the profile
swept along the member, and which the frame analysis reads. Every number is checked against a closed
form written here, or a published table with its stated error -- never against the app's own answer.

  1. PROPERTIES: A, Iz, Iy, J and a channel's centroid against the textbook formulas; bad profiles
     refused by name.
  2. THE CATALOGUE: W12x26 and W14x90 against the AISC manual within the fillets' share; every steel
     type is Steel, every type's width and depth is its section's extent.
  3. THE SOLID: a swept profile's volume is its area times its length (a round, its 32-gon); a beam
     hangs from its level with its web upright; a column's section turns with it.
  4. THE ANALYSIS: a W column cantilever sways PL^3/3EI with E = 210 GPa and the section's own I; a
     rectangle is unchanged from V125.
  5. PROPERTIES PANEL: the Type list grouped by material; a type change rebuilds the solid and changes
     the analysis, one undo; the Structural page shows the section's numbers; Edit Type's size is
     locked; a width edit on a profiled column is refused.
  6. ASSETS: a folded Sections group; a section dropped on a column, clicked onto the selection,
     refused on the wrong kind.
  7. KEPT: a copy keeps its section; a project stored before V126 gains the steel types once and
     keeps its own; a steel type it removed is not put back.

The harness never waits without a bound (V123).
"""
import asyncio, json, math, pathlib, sys, tempfile, traceback
from playwright.async_api import async_playwright

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
IN = 0.0254


class Stalled(Exception):
    pass


async def within(aw, what):
    try:
        return await asyncio.wait_for(aw, STALL)
    except asyncio.TimeoutError:
        raise Stalled(what)


def rel(a, b, tol=1e-12):
    if a is None or b is None:
        return False
    return abs(a - b) <= tol * max(1e-30, abs(b))


def saint_venant_J(hy, hz):
    a, b = max(hy, hz), min(hy, hz)
    return a * b ** 3 * (1 / 3 - 0.21 * (b / a) * (1 - (b / a) ** 4 / 12))


def props(p):
    """the textbook, written out here independently of the app"""
    s = p['shape']
    if s == 'rect':
        b, d = p['b'], p['d']
        return {'A': b * d, 'Iz': b * d ** 3 / 12, 'Iy': d * b ** 3 / 12, 'J': saint_venant_J(d, b), 'zc': 0}
    if s == 'circle':
        D = p['D']
        return {'A': math.pi * D ** 2 / 4, 'Iz': math.pi * D ** 4 / 64, 'Iy': math.pi * D ** 4 / 64, 'J': math.pi * D ** 4 / 32, 'zc': 0}
    if s == 'pipe':
        D, t = p['D'], p['t']
        d = D - 2 * t
        I = math.pi * (D ** 4 - d ** 4) / 64
        return {'A': math.pi * (D ** 2 - d ** 2) / 4, 'Iz': I, 'Iy': I, 'J': 2 * I, 'zc': 0}
    if s == 'hss':
        B, H, t = p['B'], p['H'], p['t']
        b, h = B - 2 * t, H - 2 * t
        return {'A': B * H - b * h, 'Iz': (B * H ** 3 - b * h ** 3) / 12, 'Iy': (H * B ** 3 - h * b ** 3) / 12,
                'J': 4 * ((B - t) * (H - t)) ** 2 * t / (2 * ((B - t) + (H - t))), 'zc': 0}
    d, bf, tf, tw = p['d'], p['bf'], p['tf'], p['tw']
    hw = d - 2 * tf
    A = 2 * bf * tf + hw * tw
    Iz = (bf * d ** 3 - (bf - tw) * hw ** 3) / 12
    J = (2 * bf * tf ** 3 + hw * tw ** 3) / 3
    if s == 'ibeam':
        return {'A': A, 'Iz': Iz, 'Iy': (2 * tf * bf ** 3 + hw * tw ** 3) / 12, 'J': J, 'zc': 0}
    # a channel, its back at z = 0: first moments of the two flanges and the web
    zc = (2 * bf * tf * bf / 2 + hw * tw * tw / 2) / A
    Iy = 2 * (tf * bf ** 3 / 12 + bf * tf * (bf / 2 - zc) ** 2) + (hw * tw ** 3 / 12 + hw * tw * (tw / 2 - zc) ** 2)
    return {'A': A, 'Iz': Iz, 'Iy': Iy, 'J': J, 'zc': zc}


SHAPES = {
    'rect': {'shape': 'rect', 'b': 0.3, 'd': 0.55},
    'circle': {'shape': 'circle', 'D': 0.45},
    'pipe': {'shape': 'pipe', 'D': 8.625 * IN, 't': 0.322 * IN},
    'hss': {'shape': 'hss', 'B': 0.2, 'H': 0.3, 't': 0.012},
    'ibeam': {'shape': 'ibeam', 'd': 16.0 * IN, 'bf': 7.0 * IN, 'tf': 0.505 * IN, 'tw': 0.305 * IN},
    'channel': {'shape': 'channel', 'd': 10.0 * IN, 'bf': 2.6 * IN, 'tf': 0.436 * IN, 'tw': 0.24 * IN},
}


async def run():
    ck = CK
    tmp = pathlib.Path(tempfile.mkdtemp(prefix='v126_'))
    blank = tmp / 'blank.html'
    blank.write_text('<!doctype html><title>seed</title>')
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 1600, 'height': 950})
        page = await ctx.new_page()

        def guard(obj, names):
            for nm in names:
                def make(f, nm):
                    async def g(*a, **k):
                        return await within(f(*a, **k), '%s %s' % (nm, str(a[:1])[:40]))
                    return g
                setattr(obj, nm, make(getattr(obj, nm), nm))
        guard(page.keyboard, ('type', 'press', 'down', 'up'))
        guard(page.mouse, ('move', 'down', 'up', 'click', 'dblclick'))
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))
        await page.goto('file://' + str(HTML))
        await page.wait_for_timeout(2300)

        async def safe(js, arg=None):
            try:
                return await within(page.evaluate(js, arg) if arg is not None else page.evaluate(js),
                                    'evaluate ' + js[:60].replace('\n', ' '))
            except Stalled:
                raise
            except Exception as e:
                print('      (evaluate failed: %s)' % str(e)[:200])
                return None

        has = await safe("()=>!!window.__acad3dV126")
        ck(bool(has), "__acad3dV126 marker is present")
        if not has:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.bad), ck.n))
            await browser.close()
            return 1

        async def blur():
            await safe("()=>{if(document.activeElement&&document.activeElement.blur)document.activeElement.blur();}")
            await page.wait_for_timeout(60)

        async def toast():
            return await safe("()=>{var t=document.getElementById('a3d-toast');return t?t.textContent:'';}") or ''

        async def tab(name):
            await page.click('#a3d-rail .a3d-railbtn[data-tab="%s"]' % name)
            await page.wait_for_timeout(250)

        async def centre_of(sel):
            return await safe("""(s)=>{var e=document.querySelector(s);if(!e)return null;
              e.scrollIntoView({block:'center'});var r=e.getBoundingClientRect();
              if(r.width<2||r.height<2)return null;return [r.left+r.width/2,r.top+r.height/2];}""", sel)

        async def drag(frm, to, steps=14):
            if not frm or not to:
                print('      (no drag: an end is missing -- %s -> %s)' % (frm, to))
                return
            await page.mouse.move(frm[0], frm[1])
            await page.mouse.down()
            for i in range(1, steps + 1):
                await page.mouse.move(frm[0] + (to[0] - frm[0]) * i / steps, frm[1] + (to[1] - frm[1]) * i / steps)
            await page.mouse.up()
            await page.wait_for_timeout(350)

        async def scene(js):
            """a fresh model: levels 0 and 1 (3 m), empty undo, the display off, self-weight off"""
            return await safe("""()=>{window.__a3dTestSetObjs([]);
              var lv=window.__a3dLevels();if(lv.length<2)window.__a3dAddLevel();
              window.__a3dSetLevel(window.__a3dLevels()[0].id);
              window.__a3dStructSettings({show:false,selfWeight:false,combo:'D',diagram:'M',deflected:true,res:null});
              window.__a3dTestClearUndo();window.__a3dSelectFor([]);
              var up=function(){window.__a3dSetLevel(window.__a3dLevels()[1].id);};
              var down=function(){window.__a3dSetLevel(window.__a3dLevels()[0].id);};
              return (""" + js + """)();}""")

        async def set_type(oid, tid):
            """through the Properties Type list, as a person would"""
            return await safe("""(a)=>{window.__a3dSelectFor([a[0]]);window.__a3dRefreshProps();
              var s=document.querySelector('[data-propf="objtype"]');if(!s)return 'no Type list';
              s.value=a[1];if(s.value!==a[1])return 'no such option';
              s.dispatchEvent(new Event('change',{bubbles:true}));return true;}""", [oid, tid])

        def snap(o):
            return safe("(id)=>window.__a3dObjSnapshot(id)", o)

        async def bounds(oid):
            return await safe("""(id)=>{var o=window.__a3dObjSnapshot(id);if(!o)return null;var mn=[1e9,1e9,1e9],mx=[-1e9,-1e9,-1e9];
              o.mesh.v.forEach(function(q){for(var k=0;k<3;k++){mn[k]=Math.min(mn[k],q[k]);mx[k]=Math.max(mx[k],q[k]);}});return [mn,mx];}""", oid)

        try:
            # ---------------------------------------------------------------------------------
            print("\n-- 1. section properties against the textbook")
            for nm, p in SHAPES.items():
                got = await safe("(p)=>window.__a3dProfileProps(p)", p)
                want = props(p)
                ok = got and all(rel(got[k], want[k]) for k in ('A', 'Iz', 'Iy', 'J'))
                ck(ok, "%s: A, Iz, Iy and J to 1e-12 (%s)" % (nm, got and {k: '%.6e' % got[k] for k in ('A', 'Iz', 'Iy', 'J')}))
            got = await safe("(p)=>window.__a3dProfileProps(p)", SHAPES['channel'])
            ck(got and rel(got['zc'], props(SHAPES['channel'])['zc']),
               "a channel's centroid sits %.2f mm off its back, as its flanges and web put it" % (props(SHAPES['channel'])['zc'] * 1000))
            loops = await safe("(p)=>window.__a3dProfileLoops(p)", SHAPES['channel'])
            zs = loops and [q[1] for q in loops['outer']]
            ck(zs and rel(min(zs), -props(SHAPES['channel'])['zc']) and rel(max(zs) - min(zs), SHAPES['channel']['bf']),
               "and its outline is placed with that centroid on the member's line")
            loops = await safe("(p)=>window.__a3dProfileLoops(p)", SHAPES['hss'])
            ck(loops and loops['inner'] and len(loops['inner']) == len(loops['outer']) == 4,
               "a hollow section has an outline and a hole")
            bad = await safe("""()=>[window.__a3dProfileProblem({shape:'hss',B:0.2,H:0.2,t:0.1}),
              window.__a3dProfileProblem({shape:'pipe',D:0.1,t:0.05}),window.__a3dProfileProblem({shape:'ibeam',d:0.3,bf:0.1,tf:0.16,tw:0.01}),
              window.__a3dProfileProblem({shape:'angle',d:1}),window.__a3dProfileProblem({shape:'rect',b:0.3,d:-1}),
              window.__a3dProfileProblem({shape:'rect',b:0.3,d:0.5})]""")
            ck(bad and all(bad[:5]) and bad[5] is None,
               "an HSS whose walls meet, a pipe that is solid, flanges deeper than the section, an angle and a negative depth are each refused by name (%s)" % bad)

            # ---------------------------------------------------------------------------------
            print("\n-- 2. the catalogue")
            T = await safe("()=>window.__a3dSectionTypes()") or []
            ck(len([t for t in T if t['cat'] == 'beam']) == 16 and len([t for t in T if t['cat'] == 'column']) == 12,
               "sixteen beam sections and twelve column sections (%d)" % len(T))
            ck(T and all(t['material'] == ('Concrete' if t['shape'] == 'circle' else 'Steel') for t in T),
               "every steel section is Steel, every round column Concrete")
            w12 = await safe("()=>window.__a3dProfileProps(window.__a3dTypeParams('beam','bt-w12x26').profile)")
            ck(w12 and 0 < (7.65 - w12['A'] / IN ** 2) / 7.65 < 0.04 and 0 < (204 - w12['Iz'] / IN ** 4) / 204 < 0.04,
               "W12x26 against the AISC manual: A %.2f in^2 (7.65) and Ix %.0f in^4 (204), under by the fillets' share only"
               % ((w12 or {}).get('A', 0) / IN ** 2, (w12 or {}).get('Iz', 0) / IN ** 4))
            w14 = await safe("()=>window.__a3dProfileProps(window.__a3dTypeParams('column','ct-w14x90').profile)")
            ck(w14 and 0 < (26.5 - w14['A'] / IN ** 2) / 26.5 < 0.04 and 0 < (999 - w14['Iz'] / IN ** 4) / 999 < 0.04,
               "W14x90: A %.2f in^2 (26.5) and Ix %.0f in^4 (999)" % ((w14 or {}).get('A', 0) / IN ** 2, (w14 or {}).get('Iz', 0) / IN ** 4))
            ext = await safe("""()=>window.__a3dSectionTypes().map(function(t){var p=window.__a3dTypeParams(t.cat,t.id);
              var L=window.__a3dProfileLoops(p.profile).outer,y=L.map(q=>q[0]),z=L.map(q=>q[1]);
              var dy=Math.max.apply(null,y)-Math.min.apply(null,y),dz=Math.max.apply(null,z)-Math.min.apply(null,z);
              return t.cat==='column'?[p.width,dy,p.depth,dz]:[p.width,dz,p.depth,dy];})""")
            ck(ext and all(abs(a - b) < 1e-12 and abs(c - d) < 1e-12 for a, b, c, d in ext),
               "every section type's width and depth are its section's extent, so schedules and picking read it")

            # ---------------------------------------------------------------------------------
            print("\n-- 3. the solid")
            for nm, p in SHAPES.items():
                v = await safe("(p)=>window.__a3dSweepVolume(p,2.5)", p)
                A = props(p)['A']
                if nm in ('circle', 'pipe'):
                    n = 32
                    f = n * math.sin(2 * math.pi / n) / (2 * math.pi)
                    ck(v and rel(v, A * 2.5 * f, 1e-9) and 0.993 < v / (A * 2.5) < 1,
                       "%s: the swept solid is its 32-gon, %.2f%% under the true round, closed and facing out" % (nm, 100 * (1 - v / (A * 2.5))) if v else nm)
                else:
                    ck(v and rel(v, A * 2.5, 1e-9), "%s: the swept solid's volume is A x L exactly, closed and facing out (%s)" % (nm, v))
            r = await scene("""function(){up();var b=window.__a3dBeam([0,0],[5,0],0.3,0.5),c=window.__a3dBeam([0,0],[0,4],0.3,0.5);down();
              var k=window.__a3dColumnAt([8,0],0,0.4,0.4,3);return {b:b,c:c,k:k};}""")
            ck(await set_type(r['b'], 'bt-w16x40') is True and await set_type(r['c'], 'bt-c10x15') is True
               and await set_type(r['k'], 'ct-w12x65') is True, "a beam, a second beam and a column take steel types from the Type list")
            bb = await bounds(r['b'])
            W16 = SHAPES['ibeam']
            ck(bb and rel(bb[1][1], 3, 1e-9) and rel(bb[1][1] - bb[0][1], W16['d'], 1e-9) and rel(bb[1][2] - bb[0][2], W16['bf'], 1e-9),
               "the W16x40 along X hangs from its level by its top, 16 in deep and 7 in across: its web upright (%s)" % bb)
            vol = await safe("(id)=>window.__a3dMeshVolume(id)", r['b'])
            ck(vol and rel(vol, props(W16)['A'] * 5, 1e-9), "and its solid holds exactly A x L of steel (%s m^3)" % vol)
            inner = await safe("""(a)=>{var o=window.__a3dObjSnapshot(a[0]);var zs={};o.mesh.v.forEach(function(q){
              if(Math.abs(q[0])<1e-9&&Math.abs(q[1]-a[1])<1e-9)zs[Math.abs(q[2]).toFixed(9)]=1;});return Object.keys(zs).map(Number).sort();}""", [r['b'], 3 - W16['tf']])
            ck(inner and len(inner) == 2 and rel(inner[0], W16['tw'] / 2, 1e-6) and rel(inner[1], W16['bf'] / 2, 1e-6),
               "under its top flange the W steps in to its web, %.1f mm thick: an I, not a box (%s)" % (W16['tw'] * 1000, inner))
            cb = await bounds(r['c'])
            C = SHAPES['channel']
            ck(cb and rel(cb[1][0] - cb[0][0], C['bf'], 1e-9) and rel(cb[1][1] - cb[0][1], C['d'], 1e-9),
               "the channel along Z is 2.6 in across and 10 in deep (%s)" % cb)
            kb = await bounds(r['k'])
            W12 = {'shape': 'ibeam', 'd': 12.1 * IN, 'bf': 12.0 * IN, 'tf': 0.605 * IN, 'tw': 0.390 * IN}
            ck(kb and rel(kb[1][1] - kb[0][1], 3, 1e-9) and rel(kb[1][0] - kb[0][0], W12['d'], 1e-9) and rel(kb[1][2] - kb[0][2], W12['bf'], 1e-9),
               "the W12x65 column runs its full 3 m, 12.1 in along X and 12.0 in along Z (%s)" % kb)
            await safe("(id)=>{window.__a3dSelectFor([id]);window.__a3dRefreshProps();}", r['k'])
            snap0 = await snap(r['k'])
            turned = await safe("""(id)=>{var o=window.__a3dObjSnapshot(id);window.__a3dSelectFor([id]);window.__a3dRefreshProps();
              var f=document.querySelector('[data-propf="crot"]');if(!f)return 'no rotation field';
              f.value='90';f.dispatchEvent(new Event('change',{bubbles:true}));return true;}""", r['k'])
            k2 = await snap(r['k'])
            kb2 = await bounds(r['k'])
            ck(turned is True and k2 and k2['bim'].get('section', {}).get('shape') == 'ibeam' and kb2
               and rel(kb2[1][0] - kb2[0][0], snap0['bim']['depth'], 1e-6) and rel(kb2[1][2] - kb2[0][2], snap0['bim']['width'], 1e-6),
               "turned 90 degrees in Properties, the column turns its I: 12.0 in along X, 12.1 in along Z (%s, %s)" % (turned, kb2))
            kv = await safe("(id)=>window.__a3dMeshVolume(id)", r['k'])
            ck(kv and rel(kv, props(W12)['A'] * 3, 1e-9), "and is still an I, not a box of its size (%s m^3)" % kv)

            # ---------------------------------------------------------------------------------
            print("\n-- 4. the analysis reads the section")
            r = await scene("""function(){var c=window.__a3dColumnAt([0,0],0,0.4,0.4,3),d=window.__a3dColumnAt([5,0],0,0.4,0.3,3);return {c:c,d:d};}""")
            await set_type(r['c'], 'ct-w10x49')
            await safe("""(id)=>{window.__a3dSelectFor([id]);window.__a3dStructEditFor(id,{loads:[{lc:'D',kind:'lateral',v:10,dir:'x'}]});window.__a3dSelectFor([]);}""", r['c'])
            m = await safe("()=>window.__a3dStructModel()")
            s = await safe("()=>window.__a3dStructSolve('D',false)")
            W10 = {'shape': 'ibeam', 'd': 10.0 * IN, 'bf': 10.0 * IN, 'tf': 0.560 * IN, 'tw': 0.340 * IN}
            pw = props(W10)
            ec = m and [e for e in m['els'] if e['member'] == r['c']]
            ck(ec and rel(ec[0]['A'], pw['A'], 1e-12) and rel(ec[0]['Iz'], pw['Iz'], 1e-12) and rel(ec[0]['J'], pw['J'], 1e-12)
               and rel(ec[0]['E'], 210e6, 1e-12),
               "the W10x49 column is analysed with its own A, I and J, and Steel's 210 GPa")
            if s and not s.get('error'):
                tip = [d for d, n in zip(s['disp'], m['nodes']) if n['p'][1] > 2.9 and abs(n['p'][0]) < 1e-9]
                want = 10 * 27 / (3 * 210e6 * pw['Iz'])
                ck(tip and rel(tip[0][0], want, 1e-6),
                   "a 3 m W10x49 cantilever under 10 kN sways PL^3/3EI = %.3f mm (%s)" % (want * 1000, tip and '%.3f' % (tip[0][0] * 1000)))
            else:
                ck(False, "the W column solves (%s)" % s)
            ed = m and [e for e in m['els'] if e['member'] == r['d']]
            ck(ed and rel(ed[0]['A'], 0.12) and rel(ed[0]['Iz'], 0.3 * 0.4 ** 3 / 12) and rel(ed[0]['J'], saint_venant_J(0.4, 0.3))
               and rel(ed[0]['E'], 32e6), "a column with no section is V125's rectangle, unchanged")
            sw = await safe("(id)=>window.__a3dMemberSection(id)", r['c'])
            ck(sw and sw['section']['shape'] == 'ibeam' and rel(sw['props']['A'], pw['A']),
               "the member's section, read the one way everything reads it")

            # ---------------------------------------------------------------------------------
            print("\n-- 5. Properties")
            r = await scene("""function(){up();var b=window.__a3dBeam([0,0],[6,0],0.3,0.5);down();
              var c=window.__a3dColumnAt([0,0],0,0.4,0.4,3),d=window.__a3dColumnAt([6,0],0,0.4,0.4,3);return {b:b,c:c,d:d};}""")
            groups = await safe("""(id)=>{window.__a3dSelectFor([id]);window.__a3dRefreshProps();var s=document.querySelector('[data-propf="objtype"]');
              return s?Array.prototype.map.call(s.querySelectorAll('optgroup'),g=>g.label):null;}""", r['b'])
            ck(groups and 'Steel' in groups and 'Concrete' in groups, "the Type list is grouped by material (%s)" % groups)
            m0 = await safe("()=>window.__a3dStructModel()")
            f0 = (await snap(r['b']))['mesh']['f']
            await safe("()=>window.__a3dTestClearUndo()")
            ck(await set_type(r['b'], 'bt-w16x40') is True, "the beam is made a W16x40 in the Type list")
            b1 = await snap(r['b'])
            m1 = await safe("()=>window.__a3dStructModel()")
            A0 = [e['A'] for e in m0['els'] if e['member'] == r['b']]
            A1 = [e['A'] for e in m1['els'] if e['member'] == r['b']]
            ck(b1['bim'].get('section', {}).get('shape') == 'ibeam' and len(b1['mesh']['f']) != len(f0) and A1 and rel(A1[0], props(W16)['A']),
               "its solid is rebuilt as an I, and the frame's model takes the W's area (%s -> %s)" % (A0, A1))
            txt = await safe("""()=>{var b=document.querySelector('.a3d-pgrp[data-a3dpgrp="Structural"]');if(!b)return null;
              var body=b.nextElementSibling;return body?body.textContent:'(folded)';}""")
            want_A = '%.2f' % (props(W16)['A'] * 1e4)
            ck(txt and 'W16x40' in txt and ('Area (cm²)' + want_A.rstrip('0').rstrip('.')) in txt and 'fillets not modelled' in txt,
               "the Structural page shows the section, its area (%s cm^2), and that fillets are not modelled" % want_A)
            kgm = props(W16)['A'] * 7900
            ck(txt and ('%.1f (Steel)' % kgm).replace('.0 (', ' (') in txt, "and its mass, %.1f kg/m of Steel" % kgm)
            await safe("()=>window.__a3dUndo()")
            b2 = await snap(r['b'])
            m2 = await safe("()=>window.__a3dStructModel()")
            A2 = [e['A'] for e in m2['els'] if e['member'] == r['b']]
            ck(not b2['bim'].get('section') and len(b2['mesh']['f']) == len(f0) and A2 and rel(A2[0], A0[0]),
               "one Undo takes the beam back to its rectangle, in the model and the analysis")
            # a profiled type back to a rectangle
            await set_type(r['b'], 'bt-w16x40')
            ck(await set_type(r['b'], 'bt-400x700') is True, "the W16x40 is made a 400 x 700 concrete beam again")
            b3 = await snap(r['b'])
            bv = await safe("(id)=>window.__a3dMeshVolume(id)", r['b'])
            ck(not b3['bim'].get('section') and rel(bv, 0.4 * 0.7 * 6, 1e-9),
               "and it leaves its section behind: a solid 0.4 x 0.7 x 6 m (%s m^3)" % bv)
            # a profiled column's size is its section's
            await set_type(r['c'], 'ct-hss8x8')
            c0 = await snap(r['c'])
            res = await safe("(id)=>window.__a3dRebuildColumn(id,0.5,0.5)", r['c'])
            c1 = await snap(r['c'])
            ck(res is False and rel(c1['bim']['width'], c0['bim']['width']) and 'set by its section' in await toast(),
               "a new width for an HSS column is refused, and says to choose another type")
            hres = await safe("(id)=>window.__a3dRebuildColumn(id,undefined,undefined,4)", r['c'])
            cb = await bounds(r['c'])
            hv = await safe("(id)=>window.__a3dMeshVolume(id)", r['c'])
            HSS8 = {'shape': 'hss', 'B': 8 * IN, 'H': 8 * IN, 't': 0.465 * IN}
            ck(hres is not False and cb and rel(cb[1][1] - cb[0][1], 4, 1e-9) and rel(hv, props(HSS8)['A'] * 4, 1e-9),
               "but its height changes, and it stays a tube: A x 4 m of steel (%s m^3)" % hv)
            dlg = await safe("""(id)=>{window.__a3dSelectFor([id]);window.__a3dRefreshProps();var b=document.querySelector('[data-propf="edittype"]');if(!b)return null;b.click();
              var ins=document.querySelectorAll('.a3d-dlg [data-typep]');var out={n:ins.length,dis:Array.prototype.every.call(ins,i=>i.disabled),
              txt:(document.querySelector('.a3d-dlg')||{}).textContent||''};var x=document.querySelector('.a3d-dlg [data-a3dlg="cancel"]');if(x)x.click();return out;}""", r['c'])
            ck(dlg and dlg['n'] >= 2 and dlg['dis'] and 'Rectangular hollow' in dlg['txt'],
               "Edit Type shows the section and locks its width and depth (%s)" % (dlg and {k: dlg[k] for k in ('n', 'dis')}))
            dlg = await safe("""(id)=>{window.__a3dSelectFor([id]);window.__a3dRefreshProps();var b=document.querySelector('[data-propf="edittype"]');b.click();
              var ins=document.querySelectorAll('.a3d-dlg [data-typep]');var out=Array.prototype.some.call(ins,i=>i.disabled);
              var x=document.querySelector('.a3d-dlg [data-a3dlg="cancel"]');if(x)x.click();return out;}""", r['d'])
            ck(dlg is False, "a rectangular column's type stays editable")

            # ---------------------------------------------------------------------------------
            print("\n-- 6. Assets: Sections")
            r = await scene("""function(){var c=window.__a3dColumnAt([0,0],0,0.6,0.6,3),d=window.__a3dColumnAt([3,0],0,0.4,0.4,3);
              up();var b=window.__a3dBeam([0,4],[6,4],0.3,0.5);down();
              window.__a3dSelectFor([c]);window.__a3dZoomToSelection();window.__a3dSelectFor([]);return {c:c,d:d,b:b};}""")
            await page.wait_for_timeout(400)
            await tab('browser')
            await tab('assets')
            ck(await safe("()=>window.__a3dAssetsUI().closed.sections===true"), "the Sections group starts folded, like Materials")
            await page.click('#a3d-leftpanel [data-a3dassetgrp="sections"]')
            await page.wait_for_timeout(200)
            rows = await safe("()=>document.querySelectorAll('#a3d-leftpanel [data-a3dassets^=\"section:\"]').length")
            ck(rows == 28, "unfolded, it lists the project's 28 sections (%s)" % rows)
            meta = await safe("()=>{var e=document.querySelector('#a3d-leftpanel [data-a3dassets=\"section:beam/bt-w16x40\"]');return e?e.textContent:null;}")
            ck(meta and 'Steel beam' in meta and ('%.1f kg/m' % (props(W16)['A'] * 7900)) in meta, "a row names its material, kind and mass per metre (%s)" % meta)
            rc = await safe("()=>window.__a3dCanvasRect()")
            on = await safe("()=>window.__a3dProject([0,1.5,0])")
            tgt = [round(rc['left'] + on['x']), round(rc['top'] + on['y'])] if on and rc else None
            await safe("()=>window.__a3dTestClearUndo()")
            src = await centre_of('#a3d-leftpanel [data-a3dassets="section:column/ct-pipe8"]')
            await drag(src, tgt)
            s1 = await snap(r['c'])
            ck(s1 and s1['bim'].get('typeId') == 'ct-pipe8' and s1['bim'].get('section', {}).get('shape') == 'pipe',
               "Pipe 8 dropped on the column makes it a pipe (%s)" % (s1 and s1['bim'].get('typeId')))
            await safe("()=>window.__a3dUndo()")
            ck(not (await snap(r['c']))['bim'].get('section'), "and one Undo takes it back")
            src = await centre_of('#a3d-leftpanel [data-a3dassets="section:beam/bt-w8x31"]')
            await drag(src, tgt)
            ck(not (await snap(r['c']))['bim'].get('section') and 'beam section' in await toast(),
               "a beam section dropped on a column is refused, and says it is a beam section (%s)" % await toast())
            await safe("(a)=>window.__a3dSelectFor(a)", [r['c'], r['d'], r['b']])
            await page.wait_for_timeout(150)
            await page.click('#a3d-leftpanel [data-a3dassets="section:column/ct-r500"]')
            await page.wait_for_timeout(300)
            sc, sd, sb = await snap(r['c']), await snap(r['d']), await snap(r['b'])
            ck(sc['bim'].get('typeId') == 'ct-r500' and sd['bim'].get('typeId') == 'ct-r500' and not sb['bim'].get('section'),
               "clicked, Round 500 goes on both selected columns and not on the selected beam")
            ck('2 columns are now Round 500mm' in await toast(), "and says so (%s)" % await toast())
            await safe("()=>window.__a3dSelectFor([])")
            await page.click('#a3d-leftpanel [data-a3dassets="section:beam/bt-ipe300"]')
            await page.wait_for_timeout(300)
            ck('Select a beam' in await toast(), "clicked with nothing selected, it says what to select (%s)" % await toast())
            await safe("()=>{var i=document.querySelector('#a3d-leftpanel [data-a3dassearch]');i.value='hollow';i.dispatchEvent(new Event('input',{bubbles:true}));}")
            await page.wait_for_timeout(300)
            n_ipe = await safe("()=>document.querySelectorAll('#a3d-leftpanel [data-a3dassets^=\"section:\"]').length")
            ck(n_ipe == 3, "searching the library for 'hollow' finds the three HSS sections, by their shape (%s)" % n_ipe)
            await safe("()=>{var i=document.querySelector('#a3d-leftpanel [data-a3dassearch]');i.value='';i.dispatchEvent(new Event('input',{bubbles:true}));}")

            # ---------------------------------------------------------------------------------
            print("\n-- 7. kept")
            r = await scene("""function(){var c=window.__a3dColumnAt([0,0],0,0.4,0.4,3);return {c:c};}""")
            await set_type(r['c'], 'ct-w12x65')
            await safe("(id)=>window.__a3dSelectFor([id])", r['c'])
            await blur()
            await page.keyboard.press('Control+d')
            await page.wait_for_timeout(400)
            cp = await safe("()=>window.__a3dState().sel")
            cps = cp and await snap(cp)
            cpv = cp and await safe("(id)=>window.__a3dMeshVolume(id)", cp)
            W12 = {'shape': 'ibeam', 'd': 12.1 * IN, 'bf': 12.0 * IN, 'tf': 0.605 * IN, 'tw': 0.390 * IN}
            ck(cp and cp != r['c'] and cps['bim'].get('section', {}).get('shape') == 'ibeam' and cps['bim'].get('typeId') == 'ct-w12x65'
               and rel(cpv, props(W12)['A'] * 3, 1e-9), "a copy keeps its W12x65 section and its solid")
            await page.wait_for_timeout(700)
            rec = await safe("()=>localStorage.getItem('acad3dV1')")
            ck(bool(rec), "the project is stored")
            if rec:
                R = json.loads(rec)
                for cat in ('column', 'beam'):
                    R['types'][cat] = [t for t in R['types'][cat] if not (t.get('params') or {}).get('profile')]
                R['types']['column'].append({'id': 'ct-mine', 'name': 'My 450 square', 'params': {'width': 0.45, 'depth': 0.45, 'material': 'Concrete'}})
                R['types'].pop('__v126', None)
                R['objs'] = []
                await page.goto('file://' + str(blank))
                await page.evaluate("(r)=>localStorage.setItem('acad3dV1',r)", json.dumps(R))
                await page.goto('file://' + str(HTML))
                await page.wait_for_timeout(2300)
                T2 = await safe("()=>window.__a3dSectionTypes()") or []
                mine = await safe("()=>window.__a3dTypeParams('column','ct-mine')")
                ck(len(T2) == 28 and mine and mine.get('width') == 0.45,
                   "a project stored before V126 gains the 28 sections and keeps its own type (%d, %s)" % (len(T2), mine))
                # an edit stores the project, and with it the record that it has had its sections
                await safe("()=>window.__a3dColumnAt([0,0],0,0.4,0.4,3)")
                await page.wait_for_timeout(900)
                rec2 = json.loads(await safe("()=>localStorage.getItem('acad3dV1')") or '{}')
                if rec2.get('types'):
                    rec2['types']['column'] = [t for t in rec2['types']['column'] if t['id'] != 'ct-w8x31']
                    await page.goto('file://' + str(blank))
                    await page.evaluate("(r)=>localStorage.setItem('acad3dV1',r)", json.dumps(rec2))
                    await page.goto('file://' + str(HTML))
                    await page.wait_for_timeout(2300)
                    T3 = await safe("()=>window.__a3dSectionTypes().map(t=>t.id)") or []
                    ck(rec2['types'].get('__v126') and len(T3) == 27 and 'ct-w8x31' not in T3,
                       "and a section it later removed is not put back (%d)" % len(T3))
                else:
                    ck(False, "the reloaded project is stored")
            ck(not errs, "no page errors (%s)" % errs[:3])
        except Stalled as e:
            ck(False, "the suite ran to the end (stalled at %s)" % e)
        except Exception as e:
            traceback.print_exc()
            ck(False, "the suite ran to the end (stopped by %s: %s)" % (type(e).__name__, str(e)[:160]))

        print("")
        await browser.close()
    print("%d/%d checks passed" % (ck.n - len(ck.bad), ck.n))
    if ck.bad:
        for b in ck.bad:
            print("  FAILED: " + b)
        print("RESULT: FAIL")
        return 1
    print("RESULT: PASS")
    return 0


if __name__ == '__main__':
    sys.exit(asyncio.run(run()))
