

  /* ================= __acad3dV175c: one paper space, the pure part =================
     docs/research/research-one-paper-space.md (the owner's D1 to D8, 2026-11-12) and docs/work-orders/v175c/SPEC.md.
     Every page of the set, a drawing sheet or a board, is a Layout: numbered in one series (A101, A102 ...), with a
     tab beside Model. This file holds the functions that need nothing of the page or the model: the next number,
     a number made good, a layout's label, the tabs' list, and the numbers used twice. Each is a work order in
     docs/work-orders/v175c/TASKS.md, added below as it is built. */
/* WO-01 bimLyNextNumber(numbers, prefix): the next layout number in a series */
function bimLyNextNumber(numbers, prefix) {
  var re, i, s, m, n, best;
  if (!(numbers instanceof Array)) {
    return prefix + '101';
  }
  re = new RegExp('^' + prefix + '(\\d+)$', 'i');
  best = 0;
  for (i = 0; i < numbers.length; i += 1) {
    s = numbers[i];
    if (typeof s !== 'string') {
      continue;
    }
    s = s.replace(/^\s+|\s+$/g, '');
    m = s.match(re);
    if (m) {
      n = parseInt(m[1], 10);
      if (n > best) {
        best = n;
      }
    }
  }
  if (best === 0) {
    return prefix + '101';
  }
  n = best + 1;
  if (n < 101) {
    n = 101;
  }
  return prefix + n;
}
/* WO-02 bimLyNumberValid(s): a layout number made good */
function bimLyNumberValid(s) {
  var t;
  if (typeof s !== 'string') {
    return '';
  }
  t = s.replace(/\s+/g, ' ').replace(/^\s+|\s+$/g, '');
  if (t === '' || !/^[A-Za-z0-9 ._-]+$/.test(t)) {
    return '';
  }
  return t.slice(0, 12);
}
/* WO-03 bimLyLabel(number, name): a layout's tab label */
function bimLyLabel(number, name) {
  var n, m;
  n = number === null || number === undefined ? '' : String(number);
  m = name === null || name === undefined ? '' : String(name);
  n = n.replace(/^\s+|\s+$/g, '');
  m = m.replace(/^\s+|\s+$/g, '');
  if (n !== '' && m !== '') {
    return n + ' - ' + m;
  }
  if (n !== '') {
    return n;
  }
  if (m !== '') {
    return m;
  }
  return 'Layout';
}
/* WO-04 bimLyTabs(entries, activeId): the layout tabs list */
function bimLyTabs(entries, activeId) {
  var out, i, e;
  if (!(entries instanceof Array)) {
    return [];
  }
  out = [];
  for (i = 0; i < entries.length; i += 1) {
    e = entries[i];
    out.push({id: e.id, t: e.t, label: bimLyLabel(e.num, e.name), on: e.id === activeId});
  }
  return out;
}
/* WO-05 bimLyDupNumbers(entries): numbers used by more than one layout */
function bimLyDupNumbers(entries) {
  var out, i, e, s, key, first, count, dupOrder, j, dupKey;
  if (!(entries instanceof Array)) {
    return [];
  }
  first = Object.create(null);
  count = Object.create(null);
  dupOrder = [];
  for (i = 0; i < entries.length; i += 1) {
    e = entries[i];
    if (e === null || e === undefined) {
      continue;
    }
    s = e.num;
    if (typeof s !== 'string') {
      continue;
    }
    s = s.replace(/^\s+|\s+$/g, '');
    if (s === '') {
      continue;
    }
    key = s.toLowerCase();
    if (count[key] === undefined) {
      first[key] = s;
      count[key] = 1;
    } else {
      count[key] += 1;
      if (count[key] === 2) {
        dupOrder.push(key);
      }
    }
  }
  out = [];
  for (j = 0; j < dupOrder.length; j += 1) {
    dupKey = dupOrder[j];
    out.push(first[dupKey]);
  }
  return out;
}
export { bimLyDupNumbers, bimLyLabel, bimLyNextNumber, bimLyNumberValid, bimLyTabs };
