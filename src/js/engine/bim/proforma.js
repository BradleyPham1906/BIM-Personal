

  /* ================= __acad3dV214: Costs and pro forma, the pure part =================
     docs/research/research-later-costs-proforma.md and docs/work-orders/v214/SPEC.md. Income lines, totals and NOI, the cost
     total, yield on cost, value by capitalisation, profit and margin. Each function is a work order, added below as it is
     built; none uses another file's names. */
function bimPfmLine(l) {
  var name = l.name || '';
  var qty = l.qty;
  var rate = l.rate;
  var periods = l.periods;
  if (!(periods > 0)) {
    periods = 1;
  }
  var gross = 0;
  if (qty !== undefined && qty !== null && rate !== undefined && rate !== null) {
    gross = qty * rate * periods;
  }
  var v = l.vacancy;
  if (!(v >= 0) || !(v < 1)) {
    v = 0;
  }
  return { name: name, gross: gross, effective: gross * (1 - v) };
}

function bimPfmTotals(lines, opex) {
  var gross = 0;
  var effective = 0;
  var i;
  for (i = 0; i < lines.length; i += 1) {
    var line = bimPfmLine(lines[i]);
    gross += line.gross;
    effective += line.effective;
  }
  var o = 0;
  if (opex > 0) {
    o = opex;
  }
  return { gross: gross, effective: effective, opex: o, noi: effective - o };
}

function bimPfmCost(items) {
  var total = 0;
  var i;
  for (i = 0; i < items.length; i += 1) {
    var a = items[i].amount;
    if (typeof a === 'number' && isFinite(a)) {
      total += a;
    }
  }
  return total;
}

function bimPfmMetrics(noi, cost, cap) {
  var yieldOnCost = null;
  if (cost > 0) {
    yieldOnCost = noi / cost;
  }
  var value = null;
  if (cap > 0) {
    value = noi / cap;
  }
  var profit = null;
  if (value !== null) {
    profit = value - cost;
  }
  var marginOnCost = null;
  if (profit !== null) {
    marginOnCost = profit / cost;
  }
  return { yieldOnCost: yieldOnCost, value: value, profit: profit, marginOnCost: marginOnCost };
}
