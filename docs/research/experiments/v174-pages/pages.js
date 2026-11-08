/* V174 experiment e01: the ISO 216 A and B series computed from their rule, compared with the table
   ISO 216:2007 publishes (Tables 1 and 2, read in ISO's preview, 2026-11-08); and the inch series
   (ASME Y14.1 ANSI A-E, Architectural A-E1) converted to millimetres, compared with QGIS's page
   registry (qgspagesizeregistry.cpp, master, read as text) and with the app's SHEET_SIZES.
   Our own code, ES5, no dependencies. Run: node pages.js */
'use strict';

/* the published tables, [short, long] in mm */
var ISO_A = [[841,1189],[594,841],[420,594],[297,420],[210,297],[148,210],[105,148],[74,105],[52,74],[37,52],[26,37]];
var ISO_B = [[1000,1414],[707,1000],[500,707],[353,500],[250,353],[176,250],[125,176],[88,125],[62,88],[44,62],[31,44]];

/* exact sizes in metres: A_n has area 2^-n m^2 and sides in ratio sqrt 2 */
function exactA(n) { return [Math.pow(2, -0.25 - n / 2), Math.pow(2, 0.25 - n / 2)]; }
/* B_n is the geometric mean of A_n and A_(n-1): area 2^(0.5-n) */
function exactB(n) { return [Math.pow(2, -n / 2), Math.pow(2, 0.5 - n / 2)]; }

/* rule R1: round each exact size to the nearest millimetre */
function r1(ex) { return [Math.round(ex[0] * 1000), Math.round(ex[1] * 1000)]; }
/* rule R2: round the base size, then halve the long side of the rounded size before, rounding down */
function r2series(base, n) {
  var out = [[base[0], base[1]]], i;
  for (i = 1; i <= n; i++) { var p = out[i - 1]; out.push([Math.floor(p[1] / 2), p[0]]); }
  return out;
}
/* rule R3: as R2 but rounding the half to the nearest (half up) */
function r3series(base, n) {
  var out = [[base[0], base[1]]], i;
  for (i = 1; i <= n; i++) { var p = out[i - 1]; out.push([Math.round(p[1] / 2), p[0]]); }
  return out;
}

function compare(name, table, rows) {
  var bad = [], i;
  for (i = 0; i < table.length; i++) {
    if (rows[i][0] !== table[i][0] || rows[i][1] !== table[i][1]) bad.push(name.charAt(0) + i + ' ' + rows[i].join('x') + ' (table ' + table[i].join('x') + ')');
  }
  return bad;
}

function iso() {
  var A1 = [], B1 = [], n;
  for (n = 0; n <= 10; n++) { A1.push(r1(exactA(n))); B1.push(r1(exactB(n))); }
  var A0r = r1(exactA(0)), B0r = r1(exactB(0));
  var res = {
    'A, R1 round each exact size': compare('A', ISO_A, A1),
    'A, R2 halve the rounded size, floor': compare('A', ISO_A, r2series(A0r, 10)),
    'A, R3 halve the rounded size, round': compare('A', ISO_A, r3series(A0r, 10)),
    'B, R1 round each exact size': compare('B', ISO_B, B1),
    'B, R2 halve the rounded size, floor': compare('B', ISO_B, r2series(B0r, 10)),
    'B, R3 halve the rounded size, round': compare('B', ISO_B, r3series(B0r, 10))
  };
  var k;
  console.log('ISO 216, rules against the published table (mismatches listed):');
  for (k in res) console.log('  ' + k + ': ' + (res[k].length ? res[k].length + ' wrong: ' + res[k].join('; ') : 'all 11 match'));
  console.log('  exact A0 = ' + (exactA(0)[0] * 1000).toFixed(3) + ' x ' + (exactA(0)[1] * 1000).toFixed(3) + ' mm, area ' + (exactA(0)[0] * exactA(0)[1]).toFixed(9) + ' m2');
  console.log('  exact B0 = ' + (exactB(0)[0] * 1000).toFixed(3) + ' x ' + (exactB(0)[1] * 1000).toFixed(3) + ' mm');
  console.log('  table vs exact, worst error (mm): ' + worst(ISO_A, exactA) + ' (A), ' + worst(ISO_B, exactB) + ' (B)');
  console.log('  table ratio long/short, A0..A10: ' + ISO_A.map(function (s) { return (s[1] / s[0]).toFixed(4); }).join(' '));
}
function worst(table, ex) {
  var w = 0, i;
  for (i = 0; i < table.length; i++) { var e = ex(i); w = Math.max(w, Math.abs(table[i][0] - e[0] * 1000), Math.abs(table[i][1] - e[1] * 1000)); }
  return w.toFixed(3);
}

/* inch sizes, [short, long] in inches */
var INCH = {
  'ANSI A': [8.5, 11], 'ANSI B': [11, 17], 'ANSI C': [17, 22], 'ANSI D': [22, 34], 'ANSI E': [34, 44],
  'Arch A': [9, 12], 'Arch B': [12, 18], 'Arch C': [18, 24], 'Arch D': [24, 36], 'Arch E1': [30, 42], 'Arch E': [36, 48],
  'Arch E2': [26, 38], 'Arch E3': [27, 39]
};
/* QGIS master, qgspagesizeregistry.cpp, [w, h] mm portrait */
var QGIS = {
  'ANSI A': [215.9, 279.4], 'ANSI B': [279.4, 431.8], 'ANSI C': [431.8, 558.8], 'ANSI D': [558.8, 863.6], 'ANSI E': [863.6, 1117.6],
  'Arch A': [228.6, 304.8], 'Arch B': [304.8, 457.2], 'Arch C': [457.2, 609.6], 'Arch D': [609.6, 914.4], 'Arch E': [914.4, 1219.2],
  'Arch E1': [762, 1066.8], 'Arch E2': [660, 965], 'Arch E3': [686, 991]
};
/* the app, src/js/engine/sheets/sheets.js lines 34-49 */
var APP = { 'ANSI-A': [215.9, 279.4, 'ANSI A'], 'ANSI-B': [279.4, 431.8, 'ANSI B'], 'ANSI-D': [609.6, 914.4, 'ANSI D'] };

function inch() {
  var k, mm, q;
  console.log('\nInch series in mm (exact = in x 25.4) against QGIS:');
  for (k in INCH) {
    mm = [Math.round(INCH[k][0] * 25.4 * 1000) / 1000, Math.round(INCH[k][1] * 25.4 * 1000) / 1000];
    q = QGIS[k];
    var d = Math.max(Math.abs(mm[0] - q[0]), Math.abs(mm[1] - q[1]));
    console.log('  ' + k + ': ' + INCH[k].join('x') + ' in = ' + mm.join(' x ') + ' mm; QGIS ' + q.join(' x ') + (d > 1e-9 ? '  DIFFERS by ' + d.toFixed(2) + ' mm' : '  same') + '; ratio ' + (INCH[k][1] / INCH[k][0]).toFixed(4));
  }
  console.log('\nHalving: each size is two of the size below (long side of n-1 = 2 x short side of n):');
  ['ANSI', 'Arch'].forEach(function (s) {
    var L = s === 'ANSI' ? ['A', 'B', 'C', 'D', 'E'] : ['A', 'B', 'C', 'D', 'E'], i, line = [];
    for (i = 1; i < L.length; i++) {
      var lo = INCH[s + ' ' + L[i - 1]], hi = INCH[s + ' ' + L[i]];
      line.push(L[i - 1] + '->' + L[i] + ': ' + (hi[0] === lo[1] && hi[1] === 2 * lo[0] ? 'yes' : 'no'));
    }
    console.log('  ' + s + ': ' + line.join(', '));
  });
  console.log('\nThe app\'s sizes against their names:');
  for (k in APP) {
    var nm = APP[k][2], ex = INCH[nm];
    var ok = Math.abs(APP[k][0] - ex[0] * 25.4) < 1e-6 && Math.abs(APP[k][1] - ex[1] * 25.4) < 1e-6;
    var who = '';
    if (!ok) { var j; for (j in INCH) if (Math.abs(APP[k][0] - INCH[j][0] * 25.4) < 1e-6 && Math.abs(APP[k][1] - INCH[j][1] * 25.4) < 1e-6) who = j; }
    console.log('  ' + k + ' (' + APP[k][0] + ' x ' + APP[k][1] + ' mm, labelled ' + nm + '): ' + (ok ? 'matches ' + nm : 'does NOT match ' + nm + ' (' + ex.join('x') + ' in); it is ' + (who || 'no standard size')));
  }
}

iso();
inch();
