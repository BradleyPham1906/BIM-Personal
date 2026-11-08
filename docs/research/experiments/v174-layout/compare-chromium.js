/* V174 research experiment: our light auto layout (autolayout.js) against Chromium's flexbox.
   Each case is drawn as real CSS (display:flex) in a headless Chromium page, its boxes read back with
   getBoundingClientRect, and compared with ours to 0.01 px. Run: node compare-chromium.js
   (needs the playwright package and its Chromium; nothing is installed by this script). */
var lal = require('./autolayout.js');
var cases = require('./cases.js');
var chromium = require('playwright').chromium;

/* a frame as CSS: the mapping from Figma's terms to flexbox */
function css(F, isChild, parentRow) {
  var row = F.dir !== 'column', P = F.pad, s = [];
  if (typeof P === 'number') P = [P, P, P, P];
  P = P || [0, 0, 0, 0];
  s.push('display:flex', 'box-sizing:border-box', 'flex-direction:' + (row ? 'row' : 'column'),
    'flex-wrap:' + (F.wrap ? 'wrap' : 'nowrap'), 'padding:' + P.join('px ') + 'px');
  var mainGap = F.gap === 'auto' ? 0 : Math.max(0, F.gap || 0), crossGap = typeof F.crossGap === 'number' ? F.crossGap : mainGap;
  s.push((row ? 'column-gap:' : 'row-gap:') + mainGap + 'px', (row ? 'row-gap:' : 'column-gap:') + crossGap + 'px');
  var jc = F.gap === 'auto' ? ({ between: 'space-between', evenly: 'space-evenly', around: 'space-around' })[F.auto || 'between'] :
    ({ start: 'flex-start', center: 'center', end: 'flex-end' })[F.alignMain || 'start'];
  s.push('justify-content:' + jc);
  var ai = ({ start: 'flex-start', center: 'center', end: 'flex-end' })[F.alignCross || 'start'];
  s.push('align-items:' + ai);
  if (F.wrap) s.push('align-content:' + (F.alignContent === 'between' ? 'space-between' : ai));
  s.push('width:' + (F.sizeW === 'hug' ? 'max-content' : F.w + 'px'));
  s.push('height:' + (F.sizeH === 'hug' ? 'auto' : F.h + 'px'));
  if (typeof F.minW === 'number') s.push('min-width:' + F.minW + 'px');
  if (typeof F.maxW === 'number') s.push('max-width:' + F.maxW + 'px');
  if (typeof F.minH === 'number') s.push('min-height:' + F.minH + 'px');
  if (typeof F.maxH === 'number') s.push('max-height:' + F.maxH + 'px');
  if (!isChild) s.push('position:absolute', 'left:0', 'top:0');
  return s;
}
function childCss(c, row, first, negGap) {
  var s = c.children ? css(c, true, row) : ['box-sizing:border-box'];
  var M = row ? 'width' : 'height', Cc = row ? 'height' : 'width', sM = row ? c.sizeW : c.sizeH, sC = row ? c.sizeH : c.sizeW;
  var mnM = row ? c.minW : c.minH, mxM = row ? c.maxW : c.maxH, mnC = row ? c.minH : c.minW, mxC = row ? c.maxH : c.maxW;
  if (c.hidden) s.push('display:none');
  if (c.absolute) { s.push('position:absolute', 'left:' + c.x + 'px', 'top:' + c.y + 'px', 'width:' + c.w + 'px', 'height:' + c.h + 'px'); return s.join(';'); }
  if (sM === 'fill') s.push('flex:1 1 0px', M + ':auto');
  else { s.push('flex:0 0 auto'); if (sM !== 'hug') s.push(M + ':' + (row ? c.w : c.h) + 'px'); }
  s.push('min-' + M + ':' + (typeof mnM === 'number' ? mnM : 0) + 'px');
  if (typeof mxM === 'number') s.push('max-' + M + ':' + mxM + 'px');
  if (sC === 'fill') s.push('align-self:stretch', Cc + ':auto');
  else if (sC !== 'hug') s.push(Cc + ':' + (row ? c.h : c.w) + 'px');
  s.push('min-' + Cc + ':' + (typeof mnC === 'number' ? mnC : 0) + 'px');
  if (typeof mxC === 'number') s.push('max-' + Cc + ':' + mxC + 'px');
  if (!first && negGap < 0) s.push('margin-' + (row ? 'left' : 'top') + ':' + negGap + 'px');
  return s.join(';');
}
function html(F) {
  var row = F.dir !== 'column', h = '<div id="f" style="' + css(F, false).join(';') + '">', i, first = true;
  var neg = typeof F.gap === 'number' && F.gap < 0 ? F.gap : 0;
  for (i = 0; i < F.children.length; i++) {
    var c = F.children[i], inner = '';
    if (c.children) for (var j = 0; j < c.children.length; j++) inner += '<div style="' + childCss(c.children[j], c.dir !== 'column', j === 0, 0) + '"></div>';
    h += '<div class="k" style="' + childCss(c, row, first, neg) + '">' + inner + '</div>';
    if (!c.hidden && !c.absolute) first = false;
  }
  return h + '</div>';
}
function close(a, b) { return Math.abs(a - b) < 0.01; }
function run() {
  var t0 = Date.now(), b, page, version;
  return chromium.launch().then(function (br) { b = br; version = b.version(); return b.newPage(); }).then(function (p) {
    page = p;
    return page.setContent('<!doctype html><html><body style="margin:0"><div id="host" style="position:relative"></div></body></html>');
  }).then(function () {
    var chain = Promise.resolve(), rows = [];
    cases.forEach(function (K) {
      chain = chain.then(function () {
        return page.evaluate(function (h) {
          var host = document.getElementById('host');
          host.innerHTML = h;
          var f = document.getElementById('f'), fr = f.getBoundingClientRect(), out = { w: fr.width, h: fr.height, kids: [] };
          var ks = f.querySelectorAll(':scope > .k');
          for (var i = 0; i < ks.length; i++) {
            var r = ks[i].getBoundingClientRect();
            out.kids.push(getComputedStyle(ks[i]).display === 'none' ? null : { x: r.left - fr.left, y: r.top - fr.top, w: r.width, h: r.height });
          }
          return out;
        }, html(K.F)).then(function (cr) {
          var ours = lal.lalLayout(K.F), agree = close(ours.w, cr.w) && close(ours.h, cr.h), diffs = [];
          if (!agree) diffs.push('frame ours ' + ours.w + 'x' + ours.h + ' css ' + cr.w + 'x' + cr.h);
          ours.kids.forEach(function (o, i) {
            var c = cr.kids[i];
            if (!o && !c) return;
            if (!o || !c || !close(o.x, c.x) || !close(o.y, c.y) || !close(o.w, c.w) || !close(o.h, c.h)) {
              agree = false;
              diffs.push('#' + i + ' ours ' + JSON.stringify(o) + ' css ' + JSON.stringify(c));
            }
          });
          rows.push({ name: K.name, cmp: K.cmp, agree: agree, diffs: diffs, ours: ours, css: cr, why: K.why, lines: ours.lines, hugToFixed: ours.hugToFixed });
        });
      });
    });
    return chain.then(function () { return rows; });
  }).then(function (rows) {
    var exp = rows.filter(function (r) { return r.cmp === 'yes'; }), ok = exp.filter(function (r) { return r.agree; });
    var no = rows.filter(function (r) { return r.cmp === 'no'; });
    console.log('Chromium ' + version + ', ' + rows.length + ' cases, ' + (Date.now() - t0) + ' ms');
    rows.forEach(function (r) {
      console.log((r.agree ? 'AGREE  ' : 'DIFFER ') + '[' + r.cmp + '] ' + r.name + (r.hugToFixed.length ? ' (hug->fixed ' + r.hugToFixed.join(',') + ')' : '') + ' lines=' + r.lines);
      r.diffs.forEach(function (d) { console.log('        ' + d); });
      if (r.why) console.log('        note: ' + r.why);
    });
    console.log('Expected to agree: ' + ok.length + ' of ' + exp.length + ' agree. Expected to differ: ' +
      no.filter(function (r) { return !r.agree; }).length + ' of ' + no.length + ' differ.');
    return b.close();
  }).catch(function (e) { console.error(e); if (b) b.close(); process.exit(1); });
}
run();
