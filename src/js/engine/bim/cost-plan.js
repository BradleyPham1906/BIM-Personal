

  /* ================= __acad3dV222: 4D/5D construction planning, CP0 to CP3: quantities, cost lines, allocation, the pure part =================
     docs/research/research-4d-5d-cp0-cp3.md and docs/work-orders/v222/SPEC.md. A slab's net volume, a cost line, an
     allocation that never exceeds 100%, planned cost by bucket. Each function is a work order, added below as it is built;
     none uses another file's names. */
function bimCpSlabNet(w, l, t, holes) {
  var i, net = w * l * t;
  for (i = 0; i < holes.length; i += 1) {
    var h = holes[i].t > 0 ? (holes[i].t > t ? t : holes[i].t) : t;
    net = net - holes[i].w * holes[i].l * h;
  }
  if (net < 0) net = 0;
  return net;
}

function bimCpLine(q, P) {
  var waste = P.waste !== undefined && P.waste >= 0 ? P.waste : 0;
  var order = q * (1 + waste);
  var material = order * P.matRate;
  var hours = q * P.hoursPer;
  var labour = hours * P.labRate;
  var total = material + labour;
  return { order: order, material: material, hours: hours, labour: labour, total: total };
}

function bimCpAllocate(amount, splits) {
  var i, total = 0;
  for (i = 0; i < splits.length; i += 1) {
    if (splits[i] < 0) return { error: 'invalid allocation' };
    total += splits[i];
  }
  if (total > 1 + 1e-12) return { error: 'invalid allocation' };
  var result = { assigned: [], unallocated: 0 };
  var remaining = amount;
  for (i = 0; i < splits.length; i += 1) {
    var share = splits[i];
    var assigned = amount * share;
    result.assigned.push(assigned);
    remaining -= assigned;
  }
  result.unallocated = remaining;
  return result;
}

function bimCpBuckets(items) {
  var i, day1 = 0, day2 = 0;
  for (i = 0; i < items.length; i += 1) {
    var split = items[i].split;
    if (split.day1 !== undefined) day1 += split.day1 * items[i].amount;
    if (split.day2 !== undefined) day2 += split.day2 * items[i].amount;
  }
  return { day1: day1, day2: day2 };
}
