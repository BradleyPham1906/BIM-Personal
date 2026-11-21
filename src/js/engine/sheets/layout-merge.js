

  /* ================= __acad3dV175c: One paper space, steps 2 and 3: one editor, one print, the pure part =================
     docs/research/research-one-paper-space.md and docs/work-orders/v175c/SPEC-step2.md. Steps 2 and 3: a sheet viewport
     as the one viewport object and back, a sheet as a layout, the drawing sheet's Draw menu, the vector print's page and
     outlines. Each function is a work order in TASKS-step2.md, added below as it is built; none uses another file's names. */

  /* WO-11: a sheet viewport as the one viewport object (the board's map frame) */
  function bimLmVpToFrame(vp) {
    var fit = vp.scaleMode === 'fit';
    return { t: 'map', id: vp.id, x: vp.x, y: vp.y, w: vp.w, h: vp.h, src: vp.kind + ':' + vp.refId,
      den: fit ? null : vp.scaleDenom, fit: fit, px: 0, py: 0, label: vp.label || '' };
  }

  /* WO-12: the inverse */
  function bimLmFrameToVp(fr) {
    var src = String(fr.src || '');
    var at = src.indexOf(':');
    var pos = typeof fr.den === 'number' && fr.den > 0;
    return { id: fr.id, kind: at >= 0 ? src.substring(0, at) : src, refId: at >= 0 ? src.substring(at + 1) : '',
      label: fr.label || '', x: fr.x, y: fr.y, w: fr.w, h: fr.h,
      scaleMode: (fr.fit || !pos) ? 'fit' : 'fixed', scaleDenom: pos ? fr.den : 100 };
  }

  /* WO-13: a sheet as a layout: its title block, then a frame per viewport */
  function bimLmSheetToLayout(sh) {
    var objs = [{ t: 'tblock', id: 'tb-' + sh.id, x: 0, y: 0, w: sh.w, h: sh.h }];
    var vps = sh.viewports || [];
    var i;
    for (i = 0; i < vps.length; i += 1) { objs.push(bimLmVpToFrame(vps[i])); }
    return { id: sh.id, num: sh.number || '', name: sh.name || '', w: sh.w, h: sh.h, drawing: true, objs: objs };
  }

  /* WO-14: the Draw menu; a drawing sheet leaves out live values, figures and charts */
  function bimLmDrawMenu(items, drawing) {
    var out = [];
    var i, k;
    for (i = 0; i < items.length; i += 1) {
      k = items[i].kind;
      if (!(drawing && (k === 'live' || k === 'figure' || k === 'chart'))) { out.push(items[i]); }
    }
    return out;
  }

  /* WO-15: a number for print: three decimals, '0' for any rounded zero */
  function bimLmN(v) {
    var n = Math.round(v * 1000) / 1000;
    return n === 0 ? '0' : String(n);
  }

  /* WO-16: the vector print's page, in millimetres */
  function bimLmSvgOpen(w, h) {
    var W = bimLmN(w);
    var H = bimLmN(h);
    return '<svg xmlns="http://www.w3.org/2000/svg" width="' + W + 'mm" height="' + H + 'mm" viewBox="0 0 ' + W + ' ' + H + '">';
  }

  /* WO-17: an outline on the print */
  function bimLmSvgRect(o, stroke, width) {
    return '<rect x="' + bimLmN(o.x) + '" y="' + bimLmN(o.y) + '" width="' + bimLmN(o.w) + '" height="' + bimLmN(o.h) +
      '" fill="none" stroke="' + (stroke || '#000000') + '" stroke-width="' + bimLmN(width == null ? 0.25 : width) + '"/>';
  }
export { bimLmDrawMenu, bimLmFrameToVp, bimLmN, bimLmSheetToLayout };
