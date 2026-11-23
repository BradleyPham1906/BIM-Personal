/* ================= __acad3dV204: The Parametric Design Foundation, sketch to Pad to Pocket, the pure part =================
     docs/research/research-parametric-history.md and docs/work-orders/v204/SPEC.md. Feature records: dependency order with
     cycle refusal, what a change reaches, safe expressions, and the rebuild of sketch, Pad and Pocket keeping the last
     valid result. Each function is a work order, added below as it is built; none uses another file's names. */
function bimPfOrder(fs) {
  var order = [], visited = {}, inStack = {}, cycle = [];
  var fm = {}, idList = [];
  if (Array.isArray(fs)) {
    for (var i = 0; i < fs.length; i++) {
      if (fs[i] && fs[i].id) { fm[fs[i].id] = fs[i]; idList.push(fs[i].id); }
    }
  } else { idList = Object.keys(fs); fm = fs; }
  function visit(id, path) {
    if (cycle.length) { inStack[id] = false; return; }
    if (inStack[id]) { cycle = path.concat([id]); inStack[id] = false; return; }
    if (visited[id]) { inStack[id] = false; return; }
    inStack[id] = true;
    var f = fm[id];
    if (!f) { visited[id] = true; inStack[id] = false; return; }
    var r = f.refs || [];
    for (var j = 0; j < r.length; j++) { visit(r[j], path.concat([id])); if (cycle.length) { inStack[id] = false; return; } }
    inStack[id] = visited[id] = true; order.push(id); inStack[id] = false; }
  for (var i = 0; i < idList.length; i++) { visit(idList[i], []); if (cycle.length) return { error: 'cycle', ids: cycle }; }
  return { order: order }; }
function bimPfDownstream(fs, id) {
  var fm = {};
  if (Array.isArray(fs)) for (var i = 0; i < fs.length; i++) if (fs[i] && fs[i].id && fs[i].refs) fm[fs[i].id] = fs[i];
  else { var kl = Object.keys(fs); for (var i = 0; i < kl.length; i++) if (fs[kl[i]] && fs[kl[i]].refs) fm[kl[i]] = fs[kl[i]]; }
  var ds = [];
  function H(fid, idF) { if (fid === idF) return true; var r = fm[fid] ? fm[fid].refs || [] : []; for (var i = 0; i < r.length; i++) if (H(r[i], idF)) return true; return false; }
  var fids = Object.keys(fm);
  for (var i = 0; i < fids.length; i++) { var fj = fids[i]; if (fj !== id && H(fj, id)) ds.push(fj); }
  if (ds.length > 0) { var order = bimPfOrder(fs).order; var r = []; for (var i = 0; i < order.length; i++) if (ds.indexOf(order[i]) >= 0) r.push(order[i]); return r; }
  return [];
}
function bimPfExpr(s, params) { return { value: 0 }; }
function bimPfRebuild(fs, params, last) { return { order: [], results: {} }; }
