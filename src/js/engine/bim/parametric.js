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
function bimPfExpr(s, params) {
  var i = 0, sLen = s.length;
  var hadParenAfterName = false;
  function skipSpaces() { while (i < sLen && s[i] <= ' ') i++; }
  function parseNum() {
    skipSpaces();
    if (i >= sLen) return { error: 'end' };
    var start = i;
    if (s[i] === '.') { i++; while (i < sLen && s[i] >= '0' && s[i] <= '9') i++; }
    else { while (i < sLen && s[i] >= '0' && s[i] <= '9') i++; }
    var numStr = s.substring(start, i);
    if (numStr.length === 0 || numStr === '.') return { error: 'end' };
    skipSpaces();
    return { value: parseFloat(numStr) };
  }
  function parseAtom() {
    skipSpaces();
    if (i >= sLen) return { error: 'end' };
    var c = s[i];
    if (c === '(') {
      i++; skipSpaces();
      var r = parseSum();
      skipSpaces();
      if (i >= sLen || s[i] !== ')') return { error: 'expected )' };
      i++; return r;
    }
    if (c === '-' || c === '+') {
      i++; skipSpaces();
      var a = parseAtom();
      if (a.error) return a;
      return { value: c === '-' ? -a.value : a.value };
    }
    if (c >= '0' && c <= '9' || c === '.') return parseNum();
    // name - read identifier
    var start = i;
    while (i < sLen && (s[i] >= 'a' && s[i] <= 'z' || s[i] >= 'A' && s[i] <= 'Z' || s[i] >= '0' && s[i] <= '9' || s[i] === '_')) i++;
    var name = s.substring(start, i);
    skipSpaces();
    // Check if next non-space char is ( - if so, error
    if (i < sLen && s[i] === '(') { hadParenAfterName = true; return { error: 'unexpected (' }; }
    if (!params || !(name in params)) return { error: 'unknown name ' + name };
    return { value: params[name] };
  }
  function parseProd() {
    var left = parseAtom();
    if (left.error) return left;
    while (true) {
      skipSpaces();
      if (i >= sLen) break;
      var op = s[i];
      if (op !== '*' && op !== '/') break;
      i++;
      var right = parseAtom();
      if (right.error) return right;
      if (op === '/') {
        if (right.value === 0) return { error: 'division by zero' };
        left.value = left.value / right.value;
      } else {
        left.value = left.value * right.value;
      }
    }
    return left;
  }
  function parseSum() {
    var left = parseProd();
    if (left.error) return left;
    while (true) {
      skipSpaces();
      if (i >= sLen) break;
      var op = s[i];
      if (op !== '+' && op !== '-') break;
      i++;
      var right = parseProd();
      if (right.error) return right;
      if (op === '-') left.value = left.value - right.value;
      else left.value = left.value + right.value;
    }
    return left;
  }
  var r = parseSum();
  skipSpaces();
  if (hadParenAfterName) return { error: 'unexpected (' };
  if (!r.error && i < sLen) return { error: 'unexpected (' + s[i] + ')' };
  return r;
}
function bimPfRebuild(fs, params, last) {
  // Build feature reference map
  var fm = {};
  if (Array.isArray(fs)) {
    for (var i = 0; i < fs.length; i++) {
      if (fs[i] && fs[i].id) fm[fs[i].id] = fs[i];
    }
  } else {
    var idList = Object.keys(fs);
    for (var i = 0; i < idList.length; i++) {
      if (fs[idList[i]]) fm[idList[i]] = fs[idList[i]];
    }
  }
  // Get ordered features
  var orderResult = bimPfOrder(fs);
  if (orderResult.error) return { error: 'cycle', ids: orderResult.ids };
  var order = orderResult.order;
  // Compute volumes/areas for each feature
  var volumes = {};
  for (var i = 0; i < order.length; i++) {
    var fid = order[i];
    var feature = fm[fid];
    if (!feature) continue;
    var inputs = feature.inputs || {};
    var kind = feature.kind;
    function getParam(name) {
      if (params && name in params) return params[name];
      return parseFloat(name);
    }
    if (kind === 'sketch') {
      // Sketch uses 'w' and 'l' property keys
      var w = getParam(inputs.w);
      var l = getParam(inputs.l);
      if (isNaN(w) || isNaN(l) || w <= 0 || l <= 0) {
        volumes[fid] = { status: 'failed', why: 'the sketch needs a positive width and length', kept: null };
      } else {
        var area = w * l;
        volumes[fid] = { status: 'ok', why: null, kept: { width: w, length: l, area: area }, volume: area };
      }
    } else if (kind === 'pad') {
      var refId = feature.refs ? feature.refs[0] : null;
      var refVol = volumes[refId];
      if (!refVol || refVol.status !== 'ok' || !refVol.kept) {
        volumes[fid] = { status: 'failed', why: 'its sketch or depth is not valid', kept: null };
      } else {
        var depth = getParam(inputs.depth);
        if (isNaN(depth) || depth <= 0) {
          volumes[fid] = { status: 'failed', why: 'its sketch or depth is not valid', kept: null };
        } else {
          var padArea = refVol.kept.area;
          var padVolume = padArea * depth;
          volumes[fid] = { status: 'ok', why: null, kept: { depth: depth, area: padArea, volume: padVolume, width: refVol.kept.width, length: refVol.kept.length }, volume: padVolume };
        }
      }
    } else if (kind === 'pocket') {
      var padRef = feature.refs ? feature.refs[0] : null;
      var padVol = volumes[padRef];
      if (!padVol || padVol.status !== 'ok' || !padVol.kept) {
        volumes[fid] = { status: 'failed', why: 'its pad is not valid', kept: null };
      } else {
        // Use the pocket's own depth input
        var d = getParam(inputs.depth);
        var w = getParam(inputs.w);
        var l = getParam(inputs.l);
        if (isNaN(w) || isNaN(l) || isNaN(d) || w <= 0 || l <= 0 || d <= 0) {
          volumes[fid] = { status: 'failed', why: 'the pocket does not fit in its pad', kept: null };
        } else if (w > padVol.kept.width || l > padVol.kept.length) {
          volumes[fid] = { status: 'failed', why: 'the pocket does not fit in its pad', kept: null };
        } else {
          var pocketVolume = padVol.kept.volume - w * l * d;
          volumes[fid] = { status: 'ok', why: null, kept: { volume: pocketVolume }, volume: pocketVolume };
        }
      }
    }
  }
  // Build results in order
  var results = {};
  var kept = {};
  for (var i = 0; i < order.length; i++) {
    var fid = order[i];
    var vol = volumes[fid];
    if (!vol) {
      results[fid] = { status: 'failed', why: 'unknown feature' };
      continue;
    }
    results[fid] = vol;
    if (vol.kept) {
      kept[fid] = vol.kept;
    }
  }
  // Handle last valid result for failed features
  if (last) {
    for (var i = 0; i < order.length; i++) {
      var fid = order[i];
      var vol = volumes[fid];
      if (vol && vol.status === 'failed' && last[fid] && last[fid].status === 'ok' && last[fid].kept) {
        results[fid].kept = last[fid].kept;
      }
    }
  }
  return { order: order, results: results };
}
