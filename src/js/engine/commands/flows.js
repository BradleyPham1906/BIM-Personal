

  /* ================= __acad3dV215: Flows and an app SDK, the pure part =================
     docs/research/research-notion-flows-sdk.md and docs/work-orders/v215/SPEC.md. Node graphs (order, refusal, evaluation)
     and the app bridge's checks (origin, command, arguments) and read-only snapshots. Each function is a work order, added
     below as it is built; none uses another file's names. */

function bimFlowOrder(nodes) {
  var names = [];
  var k;
  for (k in nodes) {
    if (Object.prototype.hasOwnProperty.call(nodes, k)) {
      names.push(k);
    }
  }
  names.sort();
  var i;
  for (i = 0; i < names.length; i += 1) {
    var n = names[i];
    var node = nodes[n];
    var ins = node.in;
    if (!ins) {
      ins = [];
    }
    var j;
    var seen = {};
    for (j = 0; j < ins.length; j += 1) {
      var iname = ins[j];
      if (seen[iname]) {
        return { error: 'duplicate input edge: ' + n };
      }
      seen[iname] = true;
      if (!(iname in nodes)) {
        return { error: 'missing node: ' + n };
      }
    }
  }
  var indeg = {};
  var dependents = {};
  var m;
  for (m = 0; m < names.length; m += 1) {
    var nm = names[m];
    indeg[nm] = 0;
    dependents[nm] = [];
  }
  for (m = 0; m < names.length; m += 1) {
    var nm2 = names[m];
    var ins2 = nodes[nm2].in;
    if (!ins2) {
      ins2 = [];
    }
    for (j = 0; j < ins2.length; j += 1) {
      indeg[nm2] += 1;
      dependents[ins2[j]].push(nm2);
    }
  }
  var queue = [];
  for (m = 0; m < names.length; m += 1) {
    if (indeg[names[m]] === 0) {
      queue.push(names[m]);
    }
  }
  queue.sort();
  var order = [];
  while (queue.length > 0) {
    var cur = queue.shift();
    order.push(cur);
    var deps = dependents[cur];
    deps.sort();
    var d;
    for (d = 0; d < deps.length; d += 1) {
      var dep = deps[d];
      indeg[dep] -= 1;
      if (indeg[dep] === 0) {
        queue.push(dep);
      }
    }
    queue.sort();
  }
  if (order.length !== names.length) {
    return { error: 'cycle' };
  }
  return { order: order };
}

function bimFlowEval(nodes) {
  var check = bimFlowOrder(nodes);
  if (check.error) {
    return check;
  }
  var order = check.order;
  var values = {};
  var i;
  for (i = 0; i < order.length; i += 1) {
    var name = order[i];
    var node = nodes[name];
    var op = node.op;
    var ins = node.in;
    if (!ins) {
      ins = [];
    }
    var j;
    var inputVals = [];
    for (j = 0; j < ins.length; j += 1) {
      inputVals.push(values[ins[j]]);
    }
    var hasNull = false;
    for (j = 0; j < inputVals.length; j += 1) {
      if (inputVals[j] === null || inputVals[j] === undefined) {
        hasNull = true;
        break;
      }
    }
    if (hasNull) {
      values[name] = null;
    } else if (op === 'value') {
      var v = node.value;
      values[name] = typeof v === 'number' ? v : null;
    } else if (op === 'sum') {
      var s = 0;
      for (j = 0; j < inputVals.length; j += 1) {
        s += inputVals[j];
      }
      values[name] = s;
    } else if (op === 'double') {
      values[name] = 2 * inputVals[0];
    } else if (op === 'mul') {
      var p = 1;
      for (j = 0; j < inputVals.length; j += 1) {
        p *= inputVals[j];
      }
      values[name] = p;
    } else {
      return { error: 'unsupported op: ' + name };
    }
  }
  return { values: values };
}

function bimSdkCheck(msg, allowed, origin, origins) {
  var o;
  for (o = 0; o < origins.length; o += 1) {
    if (origins[o] === origin) {
      break;
    }
  }
  if (o === origins.length) {
    return { ok: false, why: 'origin not allowed' };
  }
  if (msg === null || typeof msg !== 'object' || typeof msg.cmd !== 'string') {
    return { ok: false, why: 'not a command message' };
  }
  if (!Object.prototype.hasOwnProperty.call(allowed, msg.cmd)) {
    return { ok: false, why: 'unknown command ' + msg.cmd };
  }
  if (msg.args !== undefined && msg.args !== null) {
    if (typeof msg.args !== 'object' || Array.isArray(msg.args) || msg.args === null) {
      return { ok: false, why: 'args must be an object' };
    }
  }
  return { ok: true };
}

function bimSdkSnapshot(state, fields) {
  var result = {};
  var i;
  for (i = 0; i < fields.length; i += 1) {
    var f = fields[i];
    if (Object.prototype.hasOwnProperty.call(state, f)) {
      result[f] = JSON.parse(JSON.stringify(state[f]));
    }
  }
  return result;
}
