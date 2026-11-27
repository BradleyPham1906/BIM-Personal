

  /* ================= __acad3dV229: A split grammar for facades, the pure part =================
     docs/research/research-algorithmic-design.md and docs/work-orders/v229/SPEC.md. Rules kept as data: sizes resolved in a
     split (absolute, relative, floating), a repeat to the nearest count, the rules checked before anything runs, and the
     derivation of a rectangle into named leaves with their paths. Each function is a work order, added below as it is
     built; none uses another file's names. */
function bimSgSizes(len, sizes) {
  if (!sizes || sizes.length === 0) return [];
  var totalAbsRel = 0;
  var floats = [];
  for (var i = 0; i < sizes.length; i++) {
    var s = sizes[i];
    if (typeof s === 'number') {
      var v = s < 0 ? 0 : s;
      totalAbsRel += v;
    } else if (s && typeof s === 'object' && s.rel !== undefined) {
      var r = s.rel < 0 ? 0 : s.rel;
      totalAbsRel += r * len;
    } else if (s && typeof s === 'object' && s.fl !== undefined) {
      var f = s.fl < 0 ? 0 : s.fl;
      floats.push(f);
    }
  }
  var remaining = Math.max(0, len - totalAbsRel);
  var sumF = 0;
  for (var j = 0; j < floats.length; j++) sumF += floats[j];
  var result = [];
  for (var k = 0; k < sizes.length; k++) {
    var s = sizes[k];
    if (typeof s === 'number') {
      var v = s < 0 ? 0 : s;
      result.push(v);
    } else if (s && typeof s === 'object' && s.rel !== undefined) {
      var r = s.rel < 0 ? 0 : s.rel;
      result.push(r * len);
    } else if (s && typeof s === 'object' && s.fl !== undefined) {
      var f = s.fl < 0 ? 0 : s.fl;
      var val = sumF > 0 ? (f / sumF) * remaining : 0;
      result.push(val);
    }
  }
  return result;
}
function bimSgSplit(len, sizes) {
  var totalAbs=0,totalRel=0,floatVals=[],floatIndices=[];
  for(var i=0;i<sizes.length;i++){var s=sizes[i];if(typeof s==='number'){totalAbs+=s<0?0:s}else if(s&&typeof s==='object'&&s.rel!==undefined){totalRel+=(s.rel<0?0:s.rel)*len}else if(s&&typeof s==='object'&&s.fl!==undefined){floatIndices.push(i);floatVals.push(s.fl<0?0:s.fl)}}var sumF=0;for(var j=0;j<floatVals.length;j++)sumF+=floatVals[j];var remaining=Math.max(0,len-totalAbs-totalRel);var floatSizes=[];for(var j=0;j<floatVals.length;j++)floatSizes.push(sumF>0?(floatVals[j]/sumF)*remaining:0);var runningTotal=0,result=[];for(var i=0;i<sizes.length;i++){var s=sizes[i],size;if(typeof s==='number'){size=s<0?0:s;if(runningTotal+size>len)size=len-runningTotal}else if(s&&typeof s==='object'&&s.rel!==undefined){size=(s.rel<0?0:s.rel)*len;if(runningTotal+size>len)size=len-runningTotal}else if(s&&typeof s==='object'&&s.fl!==undefined){var fi=floatIndices.indexOf(i);size=fi!==-1?floatSizes[fi]:0}else size=0;if(size<0)size=0;if(size>0){result.push({i:i,at:runningTotal,size:size});runningTotal+=size}if(runningTotal>=len-1e-9)break}return result}
function bimSgRepeat(len, size) {
  if (len <= 0 || size <= 0) return { n: 0, size: 0 };
  var n = Math.max(1, Math.floor(len / size + 0.5 + 1e-9));
  return { n: n, size: len / n };
}
function bimSgValidate(rules, start) {
  var validOps = ['split', 'repeat', 'element'];
  var validAxes = ['x', 'y'];
  if (!rules[start]) { return { error: 'no start rule ' + start }; }
  var ruleNames = [];
  for (var n in rules) { ruleNames.push(n); }
  ruleNames.sort();
  for (var i = 0; i < ruleNames.length; i++) {
    var name = ruleNames[i];
    var rule = rules[name];
    if (!rule.op || validOps.indexOf(rule.op) === -1) { return { error: 'unknown op in ' + name }; }
    if (rule.op === 'split' || rule.op === 'repeat') {
      if (!rule.axis || validAxes.indexOf(rule.axis) === -1) { return { error: 'bad axis in ' + name }; }
    }
    if (rule.op === 'split') {
      if (!rule.parts || rule.parts.length === 0) { return { error: 'no parts in ' + name }; }
      for (var j = 0; j < rule.parts.length; j++) {
        var partRule = rule.parts[j][1];
        if (!rules[partRule]) { return { error: 'missing rule ' + partRule + ' in ' + name }; }
      }
    }
    if (rule.op === 'element') {
      if (!rule.kind || typeof rule.kind !== 'string' || rule.kind.length === 0) { return { error: 'no kind in ' + name }; }
    }
  }
  var refs = {};
  for (var i = 0; i < ruleNames.length; i++) {
    var r = rules[ruleNames[i]];
    if (r.op === 'split') { for (var j = 0; j < r.parts.length; j++) { var pn = r.parts[j][1]; if (!refs[pn]) refs[pn] = ruleNames[i]; } }
    if (r.op === 'repeat') { var rr = r.rule; if (!refs[rr]) refs[rr] = ruleNames[i]; }
  }
  var visiting = {};
  function walk(name) {
    if (visiting[name]) return { error: 'cycle at ' + name };
    visiting[name] = true;
    var rule = rules[name];
    if (rule.op === 'split') {
      for (var j = 0; j < rule.parts.length; j++) {
        var pr = rule.parts[j][1];
        var res = walk(pr);
        if (res.error) return res;
      }
    } else if (rule.op === 'repeat') {
      var rr = rule.rule;
      var res = walk(rr);
      if (res.error) return res;
    }
    delete visiting[name];
    return { ok: true };
  }
  for (var i = 0; i < ruleNames.length; i++) {
    var res = walk(ruleNames[i]);
    if (res.error) return res;
  }
  return { ok: true };
}
function bimSgDerive(rules, start, scope, params, limit) {
  limit = limit > 0 ? limit : 100000;
  scope = scope || { x: 0, y: 0, w: 0, h: 0 };
  if (scope.x === undefined) scope.x = 0;
  if (scope.y === undefined) scope.y = 0;
  var rulesCopy = {};
  for (var k in rules) { rulesCopy[k] = rules[k]; }
  var result = bimSgValidate(rules, start);
  if (result.error) return { error: result.error };
  function resolveSgSize(size, dim) {
    if (typeof size === 'number') { return size < 0 ? null : size; }
    if (typeof size === 'string') {
      var v = params[size];
      return v !== undefined && typeof v === 'number' && v >= 0 ? v : null;
    }
    if (size && typeof size === 'object') {
      if (size.rel !== undefined) {
        var r = size.rel;
        if (typeof r === 'string') r = params[r];
        if (typeof r !== 'number' || r < 0) return null;
        return r * dim;
      }
      if (size.fl !== undefined) {
        var f = size.fl;
        if (typeof f === 'string') f = params[f];
        if (typeof f !== 'number' || f < 0) return null;
        return { fl: f };
      }
    }
    return null;
  }
  var shapes = [], leaves = [], steps = 0;
  shapes.push({ rule: start, path: [[start, 0]], x: scope.x, y: scope.y, w: scope.w, h: scope.h });
  while (shapes.length > 0) {
    if (steps >= limit) { return { error: 'more than ' + limit + ' shapes' }; }
    var shape = shapes.shift(); steps++;
    var ruleName = shape.rule;
    var rule = rulesCopy[ruleName];
    if (!rule) continue;
    if (rule.op === 'element') {
      leaves.push({ rule: ruleName, kind: rule.kind, path: shape.path, x: shape.x, y: shape.y, w: shape.w, h: shape.h });
    } else if (rule.op === 'split') {
      var axis = rule.axis;
      var dim = axis === 'x' ? shape.w : shape.h;
      var resolvedSizes = [];
      var valid = true;
      for (var j = 0; j < rule.parts.length; j++) {
        var rsz = resolveSgSize(rule.parts[j][0], dim);
        if (rsz === null) { valid = false; break; }
        resolvedSizes.push(rsz);
      }
      if (!valid) { return { error: 'bad size in ' + ruleName }; }
      var parts = bimSgSplit(dim, resolvedSizes);
      var ruleCounts = {};
      for (var j = 0; j < parts.length; j++) {
        var part = parts[j];
        var partRule = rule.parts[part.i][1];
        var k = ruleCounts[partRule] || 0;
        ruleCounts[partRule] = k + 1;
        var childPath = shape.path.concat([[partRule, k]]);
        var childX, childY, childW, childH;
        if (axis === 'x') {
          childX = shape.x + part.at; childY = shape.y; childW = part.size; childH = shape.h;
        } else {
          childX = shape.x; childY = shape.y + part.at; childW = shape.w; childH = part.size;
        }
        shapes.push({ rule: partRule, path: childPath, x: childX, y: childY, w: childW, h: childH });
      }
    } else if (rule.op === 'repeat') {
      var rsz = resolveSgSize(rule.size, rule.axis === 'x' ? shape.w : shape.h);
      if (rsz === null || rsz <= 0) { return { error: 'bad size in ' + ruleName }; }
      var count = bimSgRepeat(rule.axis === 'x' ? shape.w : shape.h, rsz);
      if (count.n > 0 && rule.rule) {
        var childSize = count.size;
        for (var i = 0; i < count.n; i++) {
          var childPath = shape.path.concat([[rule.rule, i]]);
          var cX, cY, cW, cH;
          if (rule.axis === 'x') {
            cX = shape.x + i * childSize; cY = shape.y; cW = childSize; cH = shape.h;
          } else {
            cX = shape.x; cY = shape.y + i * childSize; cW = shape.w; cH = childSize;
          }
          shapes.push({ rule: rule.rule, path: childPath, x: cX, y: cY, w: cW, h: cH });
        }
      }
    }
  }
  return { leaves: leaves, steps: steps };
}
