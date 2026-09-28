#!/usr/bin/env python3
"""bim_phase118_panel_focus_browser_tests.py -- V118: a panel keeps the focus through its own rebuild,
and an open dialog owns the keyboard.

  1. THE PANEL IS STILL THE MARKUP. Properties is no longer replaced wholesale; the live panel is
     brought into line with the new markup. So the result is checked against a panel built from
     nothing, after moving between every kind of Properties -- walls of two types, a room, its tag, a
     column, a grid, the model with nothing selected -- markup AND every field's value, which the
     markup does not carry. A rejected edit shows the model's value again. The helper's own contract
     is driven on a panel of its own: what stays keeps its identity, focus and caret; what disappears
     above the focused field does not move it; a true reorder does, and the focus comes back.
  2. PROPERTIES KEEPS THE FOCUS. On V117 each of these dropped the focus to the page, where the next
     key is the model's: ArrowDown twice on the wall's Type dropdown steps the type twice and the
     wall does not move (V117 moved it a metre); ArrowUp twice on the wall's Height field raises it
     twice; a Tab from field to field in Model Properties lands on the next field; a click from one
     room field into another lands there, with the first field's edit kept.
  3. THE CLASS: the dock's Discipline dropdown keeps the focus through the dock's rebuild, and the
     selected object stays put.
  4. AN OPEN DIALOG OWNS THE KEYBOARD. With the focus off its fields, the nudge keys, Undo and Delete
     do not touch the model behind it (V117 moved the column and undid it); Escape still closes it and
     the function keys still set drawing aids; closed, the same keys work again.
  5. No page errors.
"""
import asyncio, pathlib, sys
from playwright.async_api import async_playwright

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'

SNAP_PANEL = """(host)=>{var p=document.querySelector(host);if(!p)return null;
  var c=p.querySelectorAll('input,select,textarea'),v=[],i;
  for(i=0;i<c.length;i++)v.push(c[i].type==='checkbox'||c[i].type==='radio'?String(c[i].checked):
    (c[i].tagName==='SELECT'?c[i].selectedIndex+':'+c[i].value:String(c[i].value)));
  return p.innerHTML+'||'+v.join('|');}"""


class Checks:
    def __init__(self):
        self.n, self.bad = 0, []

    def __call__(self, cond, msg):
        self.n += 1
        if not cond:
            self.bad.append(msg)
        print(('ok    ' if cond else 'FAIL  ') + msg)


async def main():
    ck = Checks()
    ck('__acad3dV118' in HTML.read_text(encoding='utf-8'), 'the V118 marker is present')
    if not ck.bad:
        try:
            await drive(ck)
        except Exception as e:
            ck(False, 'the suite ran to the end (stopped by %s: %s)' % (type(e).__name__, str(e).splitlines()[0][:160]))
    print('\n%d/%d checks passed' % (ck.n - len(ck.bad), ck.n))
    print('RESULT: ' + ('PASS' if not ck.bad else 'FAIL'))
    sys.exit(1 if ck.bad else 0)


async def drive(ck):
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 1600, 'height': 950})
        page = await ctx.new_page()
        page.set_default_timeout(6000)
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)[:160]))
        page.on('dialog', lambda d: asyncio.ensure_future(d.dismiss()))
        ev = page.evaluate

        async def safe(js, arg=None):
            try:
                return await (ev(js, arg) if arg is not None else ev(js))
            except Exception as e:
                print('      (evaluate failed: %s)' % str(e)[:160])
                return None

        async def press(key, ms=200):
            await page.keyboard.press(key)
            await page.wait_for_timeout(ms)

        async def blur():
            await safe("()=>{if(document.activeElement&&document.activeElement.blur)document.activeElement.blur();}")

        async def focused():
            return await safe("()=>{var a=document.activeElement;if(!a||a===document.body)return null;"
                              "return a.getAttribute('data-propf')||a.getAttribute('data-propmodel')||a.getAttribute('data-roomf')||a.id||a.tagName;}")

        async def obj(i):
            return (await safe("(i)=>window.__a3dObjSnapshot(i)", i)) or {}

        async def select(i):
            await safe("(i)=>{window.__a3dSelectFor(i?[i]:[]);window.__a3dRefreshProps();}", i)
            await page.wait_for_timeout(120)

        async def focus_field(sel):
            return await safe("(q)=>{var e=document.querySelector(q);if(!e)return false;e.focus();return document.activeElement===e;}", sel)

        await page.goto('file://' + str(HTML))
        try:
            await page.wait_for_function("()=>!!window.__a3dColumnAt&&!!window.__a3dCreateRoomAt&&!!document.querySelector('#a3d-propsbody')", timeout=20000)
        except Exception as e:
            print('      (the workspace did not come up: %s)' % str(e)[:100])
        await page.wait_for_timeout(500)
        await page.mouse.click(800, 450)
        await safe("""()=>{window.__a3dFlat(true);window.__a3dTestSetObjs([]);
            [[[0,0],[12,0]],[[12,0],[12,8]],[[12,8],[0,8]],[[0,8],[0,0]]].forEach(function(s){window.__a3dWall(s,0.3,null,'center',false);});}""")
        room = await safe("()=>window.__a3dCreateRoomAt([4,4],0)")
        col = await safe("()=>window.__a3dColumnAt([20,0],0,0.4,0.4,3)")
        wall = await safe("()=>window.__a3dWall([[0,20],[6,20]],0.3,3,'center',false)")
        grid = await safe("()=>window.__a3dAddGrid([-5,-5],[-5,15])")
        wall2 = await safe("()=>window.__a3dWall([[0,24],[6,24]],0.3,3,'center',false)")
        await safe("""(w)=>{window.__a3dSelectFor([w]);window.__a3dRefreshProps();
            var s=document.querySelector('#a3d-propsbody select[data-propf="walltype"]');
            s.value=s.options[s.options.length-1].value;s.dispatchEvent(new Event('change',{bubbles:true}));}""", wall2)
        await safe("()=>window.__a3dTagAllRooms()")
        tag = await safe("()=>{var t=window.__a3dState().objs.filter(function(o){return o.t==='roomtag';})[0];return t?t.id:null;}")

        # -------------------------------------------------------------------------------------------
        print('\n-- 1. the panel is still the markup')
        same = []
        for kind, target in (('wall', wall), ('wall of another type', wall2), ('room', room), ('column', col), ('grid', grid),
                             ('nothing', None), ('wall', wall), ('room tag', tag), ('room', room)):
            if kind == 'grid':
                await safe("(g)=>{window.__a3dSelectFor([]);window.__a3dSelectGrid(g);window.__a3dRefreshProps();}", grid)
            else:
                await safe("()=>{window.__a3dSelectGrid&&window.__a3dSelectGrid(null);}")
                await select(target)
            a = await safe(SNAP_PANEL, '#a3d-propsbody')
            await safe("()=>{document.getElementById('a3d-propsbody').innerHTML='';window.__a3dRefreshProps();}")
            b = await safe(SNAP_PANEL, '#a3d-propsbody')
            same.append((kind, a is not None and a == b and len(a) > 200))
        ck(all(s for _, s in same) and wall2 and tag, 'moving between walls of two types, a room, its tag, a column, a grid and the '
           'model, the panel equals one built from nothing -- markup and every field\'s value (%s)' % [k for k, s in same if not s])

        con = await safe("""()=>{var h=document.createElement('div');h.id='v118host';document.body.appendChild(h);
            var R=window.__a3dRenderInto,out={},b;
            function row(k,v){return '<div class="row"><label>'+k+'</label><input data-k="'+k+'" value="'+v+'"></div>';}
            R(h,'<p>note</p>'+row('x',0)+row('a',1)+row('b','hello'));
            b=h.querySelector('[data-k="b"]');b.__v118=1;b.focus();b.setSelectionRange(2,2);
            var mo=new MutationObserver(function(){});mo.observe(h,{childList:true,subtree:true});
            function movedB(){var rs=mo.takeRecords(),i,j,n;for(i=0;i<rs.length;i++)for(j=0;j<rs[i].removedNodes.length;j++){
              n=rs[i].removedNodes[j];if(n===b||(n.nodeType===1&&n.contains(b)))return true;}return false;}
            function at(){return [document.activeElement===b,b.selectionStart];}
            R(h,'<p>note</p>'+row('x',0)+row('a',9)+row('b','hello'));
            out.kept=[h.querySelector('[data-k="b"]')===b,h.querySelector('[data-k="a"]').value,movedB()].concat(at());
            R(h,row('x',0)+row('a',9)+row('b','hello'));
            out.noteGone=[movedB()].concat(at());
            R(h,row('a',9)+row('b','hello'));
            out.rowGone=[movedB()].concat(at());
            R(h,row('b','hello')+row('a',9));
            out.reorder=[movedB(),h.firstElementChild.contains(b)].concat(at());
            R(h,row('b','world')+row('a',9));
            out.value=[b.value,document.activeElement===b];
            b.setSelectionRange(3,3);
            R(h,'<div class="row"><span data-hint="1">new</span><label>b</label><input data-k="b" value="world"></div>'+row('a',9));
            var nb=h.querySelector('[data-k="b"]');
            out.rebuilt=[nb!==b,document.activeElement===nb,nb.selectionStart];
            mo.disconnect();h.parentNode.removeChild(h);
            return out;}""")
        con = con or {}
        ck(con.get('kept') == [True, '9', False, True, 2],
           'a re-render keeps an element that is still there -- the same element, focused, caret in place -- while a '
           'neighbour takes its new value (%s)' % con.get('kept'))
        ck(con.get('noteGone') == [False, True, 2] and con.get('rowGone') == [False, True, 2],
           'a note, then a whole row, disappearing above the focused field does not move it (%s %s)'
           % (con.get('noteGone'), con.get('rowGone')))
        ck(con.get('reorder') == [True, True, True, 2],
           'a true reorder moves it, and the focus and the caret come back to it (%s)' % con.get('reorder'))
        ck(con.get('value') == ['world', True], 'and the focused field shows the value the markup gives it (%s)' % con.get('value'))
        ck(con.get('rebuilt') == [True, True, 3],
           'a field whose row is rebuilt around it is found again by what it is, with the focus and the caret (%s)'
           % con.get('rebuilt'))

        await safe("()=>{window.__a3dSelectGrid&&window.__a3dSelectGrid(null);}")
        await select(tag)
        rname = (await obj(room)).get('name')
        await focus_field('#a3d-propsbody input[data-roomf="name"]')
        await page.keyboard.press('Control+a')
        await page.keyboard.press('Delete')
        await press('Enter', 250)
        tn = await safe("()=>{var i=document.querySelector('#a3d-propsbody input[data-roomf=\"name\"]');return i?i.value:null;}")
        ck(rname and tn == rname and (await obj(room)).get('name') == rname,
           'clearing the room name on its tag is refused, and the field shows the name again (%r)' % tn)
        await blur()

        await select(wall2)
        t0 = ((await obj(wall2)).get('bim') or {}).get('typeId')
        await safe("()=>{var c=document.querySelector('#a3d-propsbody input[data-propf=\"locked\"]');c.checked=true;c.dispatchEvent(new Event('change',{bubbles:true}));}")
        await page.wait_for_timeout(150)
        await focus_field('#a3d-propsbody select[data-propf="walltype"]')
        await press('ArrowUp', 250)
        dd = await safe("()=>{var s=document.querySelector('#a3d-propsbody select[data-propf=\"walltype\"]');return s?[s.value,document.activeElement===s]:null;}")
        ck(t0 and dd == [t0, True] and ((await obj(wall2)).get('bim') or {}).get('typeId') == t0 and (await obj(wall2)).get('locked'),
           'a Type change refused on a pinned wall leaves the dropdown showing the wall\'s type, still focused (V117 showed the '
           'refused one) (%s)' % (dd,))
        await safe("()=>{var c=document.querySelector('#a3d-propsbody input[data-propf=\"locked\"]');c.checked=false;c.dispatchEvent(new Event('change',{bubbles:true}));}")
        await blur()

        await select(wall)
        h0 = (await obj(wall)).get('bim', {}).get('height')
        await focus_field('#a3d-propsbody input[data-propf="height"]')
        await page.keyboard.press('Control+a')
        await page.keyboard.type('abc')
        await press('Enter', 250)
        shown = await safe("()=>{var i=document.querySelector('#a3d-propsbody input[data-propf=\"height\"]');return i?[i.value,i.defaultValue]:null;}")
        ck(shown and shown[0] == shown[1] and shown[0] not in ('', 'abc') and (await obj(wall)).get('bim', {}).get('height') == h0,
           'a rejected edit shows the model\'s value again, and the model is untouched (%s)' % (shown,))
        await blur()

        # -------------------------------------------------------------------------------------------
        print('\n-- 2. Properties keeps the focus through its own rebuild')

        async def wall_state():
            o = await obj(wall)
            return [o.get('pos'), (o.get('bim') or {}).get('typeId'), (o.get('bim') or {}).get('height')]

        await select(wall)
        opts = await safe("()=>{var s=document.querySelector('#a3d-propsbody select[data-propf=\"walltype\"]');"
                          "return s?[s.selectedIndex,Array.prototype.map.call(s.options,function(o){return o.value;})]:null;}")
        s0 = await wall_state()
        await focus_field('#a3d-propsbody select[data-propf="walltype"]')
        await press('ArrowDown')
        s1, f1 = await wall_state(), await focused()
        await press('ArrowDown')
        s2, f2 = await wall_state(), await focused()
        want = opts[1][opts[0] + 1:opts[0] + 3] if opts else None
        ck(want and len(want) == 2 and [s1[1], s2[1]] == want and s2[0] == s0[0] and f1 == f2 == 'walltype',
           'ArrowDown twice on the Type dropdown steps the type twice, the dropdown keeps the focus, and the wall does '
           'not move (%s -> %s -> %s)' % (s0[:2], s1[:2], s2[:2]))

        await focus_field('#a3d-propsbody input[data-propf="height"]')
        await press('ArrowUp')
        s3, f3 = await wall_state(), await focused()
        await press('ArrowUp')
        s4, f4 = await wall_state(), await focused()
        ck(s2[2] is not None and s3[2] is not None and s4[2] is not None and s4[2] > s3[2] > s2[2] and s4[0] == s2[0]
           and f3 == f4 == 'height',
           'ArrowUp twice on the Height field raises the wall twice and keeps the field (%s -> %s -> %s)' % (s2[2], s3[2], s4[2]))
        await blur()

        await select(None)
        await page.click('#a3d-propsbody [data-propmodel="project"]')
        await page.keyboard.press('Control+a')
        await page.keyboard.type('Tower')
        await press('Tab')
        fa = await focused()
        await page.keyboard.type('Client Co')
        await press('Tab')
        fb = await focused()
        tb = (await safe("()=>window.__a3dTitleBlockGet()")) or {}
        ck(fa == 'client' and fb == 'truenorth' and tb.get('project') == 'Tower' and tb.get('client') == 'Client Co',
           'a Tab in Model Properties lands on the next field each time, and both edits are the model\'s (%s, %s, %s)'
           % (fa, fb, {k: tb.get(k) for k in ('project', 'client')}))
        await blur()

        await select(room)
        await page.click('#a3d-propsbody input[data-roomf="dept"]')
        await page.keyboard.press('Control+a')
        await page.keyboard.type('Admin')
        await page.click('#a3d-propsbody input[data-roomf="comments"]')
        await page.wait_for_timeout(200)
        fc = await focused()
        await page.keyboard.type('North light')
        await press('Enter', 250)
        r = await obj(room)
        ck(fc == 'comments' and r.get('dept') == 'Admin' and r.get('comments') == 'North light',
           'a click from one room field into another lands there, with the first field\'s edit kept (%s, %r, %r)'
           % (fc, r.get('dept'), r.get('comments')))
        await blur()

        # -------------------------------------------------------------------------------------------
        print('\n-- 3. the class: the dock keeps the focus through its own rebuild')
        await select(col)
        c0 = (await obj(col)).get('pos')
        d0 = await safe("()=>window.__a3dDiscipline()")
        okf = await focus_field('#a3d-discsel')
        await press('ArrowDown', 300)
        d1, f5 = await safe("()=>window.__a3dDiscipline()"), await focused()
        await press('ArrowUp', 300)
        d2, f6 = await safe("()=>window.__a3dDiscipline()"), await focused()
        ck(okf and d1 != d0 and d2 == d0 and f5 == f6 == 'a3d-discsel' and (await obj(col)).get('pos') == c0,
           'the dock\'s Discipline dropdown steps down and back up with the focus kept, and the column stays put (%s %s %s)'
           % (d0, d1, d2))
        await blur()

        # -------------------------------------------------------------------------------------------
        print('\n-- 4. an open dialog owns the keyboard')
        await select(col)
        n0 = len((await safe("()=>window.__a3dState().objs")) or [])
        await safe("()=>window.__a3dOpenDlg('box')")
        hd = await safe("()=>{var d=document.querySelector('.a3d-dlg .a3d-dlghd');if(!d)return null;var r=d.getBoundingClientRect();return [r.x+r.width/2,r.y+r.height/2];}")
        if hd:
            await page.mouse.click(hd[0], hd[1])
            await page.wait_for_timeout(100)
        ae = await safe("()=>document.activeElement.tagName")
        for k in ('ArrowDown', 'PageUp', 'Control+z', 'Delete'):
            await press(k, 150)
        n1 = len((await safe("()=>window.__a3dState().objs")) or [])
        ck(hd and ae == 'BODY' and (await obj(col)).get('pos') == c0 and n1 == n0 and await safe("()=>!!document.querySelector('.a3d-dlg')"),
           'with a dialog open and the focus off its fields, the nudge keys, Undo and Delete leave the model alone (V117 moved '
           'the column and undid it) (%s)' % ae)
        o0 = ((await safe("()=>window.__a3dSnapState()")) or {}).get('ortho')
        await press('F8', 150)
        o1 = ((await safe("()=>window.__a3dSnapState()")) or {}).get('ortho')
        await press('F8', 150)
        ck(o0 is not None and o1 == (not o0), 'the function keys still set drawing aids with the dialog open (ortho %s -> %s)' % (o0, o1))
        await press('Escape', 200)
        gone = await safe("()=>!document.querySelector('.a3d-dlg')")
        await select(col)
        await blur()
        await press('ArrowDown', 200)
        c1 = (await obj(col)).get('pos')
        ck(gone and c1 != c0, 'Escape still closes the dialog, and then the same ArrowDown moves the column (%s -> %s)' % (c0, c1))

        await select(col)
        await blur()
        await page.keyboard.press('Control+k')
        await page.wait_for_timeout(300)
        await page.keyboard.type('ARRAYRECT')
        await page.wait_for_timeout(150)
        await press('Enter', 400)
        hd2 = await safe("()=>{var d=document.querySelector('.a3d-dlg .a3d-dlghd');if(!d)return null;var r=d.getBoundingClientRect();return [r.x+r.width/2,r.y+r.height/2];}")
        if hd2:
            await page.mouse.click(hd2[0], hd2[1])
            await page.wait_for_timeout(100)
        m0 = len((await safe("()=>window.__a3dState().objs")) or [])
        await press('Control+z', 200)
        m1 = len((await safe("()=>window.__a3dState().objs")) or [])
        await safe("()=>{var b=document.querySelector('.a3d-dlg [data-a3dlg=\"ok\"]');if(b)b.click();}")
        await page.wait_for_timeout(300)
        m2 = len((await safe("()=>window.__a3dState().objs")) or [])
        ck(hd2 and m1 == m0 and m2 > m0,
           'Ctrl+Z behind the Linear Array dialog undoes nothing, and its OK then arrays the column (%s -> %s -> %s)' % (m0, m1, m2))

        # -------------------------------------------------------------------------------------------
        print('\n-- 5. errors')
        ck(errs == [], 'no page errors (%s)' % errs[:3])
        await browser.close()


asyncio.run(main())
