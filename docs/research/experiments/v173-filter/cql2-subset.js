/* V173 research sketch, not the app's code.
   A recursive-descent parser and three-valued evaluator for a CQL2 Text subset:
   Basic CQL2 (= <> < <= > >=, AND OR NOT, IS [NOT] NULL, TRUE/FALSE literals)
   + Advanced Comparison Operators ([NOT] LIKE, [NOT] BETWEEN, [NOT] IN)
   + CASEI(...) from Case-insensitive Comparison (lower-case fold, not full Unicode folding).
   ES5 only: no eval, no new Function, no RegExp built from user text. */
'use strict';

/* ---------- tokenizer ---------- */
var KEYWORDS = { AND: 1, OR: 1, NOT: 1, IS: 1, NULL: 1, LIKE: 1, BETWEEN: 1, IN: 1, TRUE: 1, FALSE: 1, CASEI: 1 };

function FilterError(msg, pos) { this.message = msg + (pos >= 0 ? ' (at character ' + (pos + 1) + ')' : ''); this.pos = pos; }
FilterError.prototype = new Error();

function isIdStart(c) { return /[A-Za-z_:À-ɏͰ-ϿЀ-ӿ]/.test(c); }
function isIdPart(c) { return isIdStart(c) || /[0-9.]/.test(c); }

function tokenize(src) {
  var t = [], i = 0, n = src.length, c, s, j, buf;
  if (n > 4000) throw new FilterError('The filter is longer than 4000 characters', -1);
  while (i < n) {
    c = src.charAt(i);
    if (/\s/.test(c)) { i++; continue; }
    s = i;
    if (c === "'") {                        /* string: '' or \' escapes a quote (CQL2 req 21) */
      buf = ''; i++;
      for (;;) {
        if (i >= n) throw new FilterError('A text value is not closed with a quote', s);
        c = src.charAt(i);
        if (c === "'" && src.charAt(i + 1) === "'") { buf += "'"; i += 2; continue; }
        if (c === '\\' && i + 1 < n) {
          j = src.charAt(i + 1);
          buf += j === 'n' ? '\n' : j === 't' ? '\t' : j === 'r' ? '\r' : j; i += 2; continue;
        }
        if (c === "'") { i++; break; }
        buf += c; i++;
      }
      t.push({ k: 'str', v: buf, p: s }); continue;
    }
    if (c === '"') {                        /* quoted identifier: "" escapes a quote; spaces allowed (beyond the BNF, as cql2-rs) */
      buf = ''; i++;
      for (;;) {
        if (i >= n) throw new FilterError('A field name is not closed with a double quote', s);
        c = src.charAt(i);
        if (c === '"' && src.charAt(i + 1) === '"') { buf += '"'; i += 2; continue; }
        if (c === '"') { i++; break; }
        buf += c; i++;
      }
      if (!buf) throw new FilterError('An empty field name', s);
      t.push({ k: 'id', v: buf, p: s, q: 1 }); continue;
    }
    if (/[0-9]/.test(c) || ((c === '-' || c === '+' || c === '.') && /[0-9.]/.test(src.charAt(i + 1)))) {
      j = /^[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?/.exec(src.slice(i));
      if (!j) throw new FilterError('A number is not written correctly', s);
      i += j[0].length;
      if (i < n && isIdPart(src.charAt(i))) throw new FilterError('A number runs into a name', s);
      t.push({ k: 'num', v: parseFloat(j[0]), p: s }); continue;
    }
    if (isIdStart(c)) {
      j = i; while (j < n && isIdPart(src.charAt(j))) j++;
      buf = src.slice(i, j); i = j;
      if (KEYWORDS.hasOwnProperty(buf.toUpperCase())) t.push({ k: 'kw', v: buf.toUpperCase(), p: s });
      else t.push({ k: 'id', v: buf, p: s });
      continue;
    }
    j = src.substr(i, 2);
    if (j === '<>' || j === '<=' || j === '>=' || j === '!=') { t.push({ k: 'op', v: j === '!=' ? '<>' : j, p: s }); i += 2; continue; }
    if ('=<>(),'.indexOf(c) >= 0) { t.push({ k: c === '(' || c === ')' || c === ',' ? c : 'op', v: c, p: s }); i++; continue; }
    throw new FilterError('Unexpected character ' + JSON.stringify(c), s);
  }
  t.push({ k: 'end', p: n });
  return t;
}

/* ---------- parser: OR < AND < NOT < predicate (CQL2 booleanExpression) ---------- */
function parse(src) {
  var toks = tokenize(String(src)), i = 0, depth = 0;
  function peek() { return toks[i]; }
  function isKw(v) { return toks[i].k === 'kw' && toks[i].v === v; }
  function eat(k, v) {
    var x = toks[i];
    if (x.k !== k || (v !== undefined && x.v !== v)) throw new FilterError('Expected ' + (v || k) + ' but found ' + describe(x), x.p);
    i++; return x;
  }
  function describe(x) { return x.k === 'end' ? 'the end' : x.k === 'str' ? "'" + x.v + "'" : String(x.v || x.k); }
  function enter() { if (++depth > 64) throw new FilterError('The filter nests more than 64 levels', toks[i].p); }
  function orExpr() {
    enter(); var a = [andExpr()];
    while (isKw('OR')) { i++; a.push(andExpr()); }
    depth--; return a.length === 1 ? a[0] : { op: 'or', args: a };
  }
  function andExpr() {
    var a = [notExpr()];
    while (isKw('AND')) { i++; a.push(notExpr()); }
    return a.length === 1 ? a[0] : { op: 'and', args: a };
  }
  function notExpr() {
    if (isKw('NOT')) { i++; enter(); var x = notExpr(); depth--; return { op: 'not', args: [x] }; }
    return primary();
  }
  function primary() {
    var x = peek();
    if (x.k === '(') { i++; var e = orExpr(); eat(')'); return e; }
    if (isKw('TRUE') || isKw('FALSE')) {
      /* a bare boolean is a whole predicate only when no comparison follows */
      var nx = toks[i + 1];
      if (!(nx.k === 'op' || (nx.k === 'kw' && /^(IS|LIKE|BETWEEN|IN|NOT)$/.test(nx.v)))) { i++; return { lit: x.v === 'TRUE' }; }
    }
    return predicate();
  }
  function operand() {
    var x = peek();
    if (x.k === 'id') { i++; return { prop: x.v }; }
    if (x.k === 'str') { i++; return { lit: x.v }; }
    if (x.k === 'num') { i++; return { lit: x.v }; }
    if (isKw('TRUE') || isKw('FALSE')) { i++; return { lit: x.v === 'TRUE' }; }
    if (isKw('NULL')) { i++; return { lit: null }; }
    if (isKw('CASEI')) { i++; eat('('); var a = operand(); eat(')'); return { op: 'casei', args: [a] }; }
    throw new FilterError('Expected a field, a value or CASEI(...) but found ' + describe(x), x.p);
  }
  function predicate() {
    var l = operand(), neg = false, x, lo, hi, list;
    x = peek();
    if (x.k === 'op') { i++; return { op: x.v, args: [l, operand()] }; }
    if (isKw('IS')) { i++; if (isKw('NOT')) { i++; neg = true; } eat('kw', 'NULL'); x = { op: 'isNull', args: [l] }; return neg ? { op: 'not', args: [x] } : x; }
    if (isKw('NOT')) { i++; neg = true; }
    if (isKw('LIKE')) { i++; x = { op: 'like', args: [l, operand()] }; }
    else if (isKw('BETWEEN')) { i++; lo = operand(); eat('kw', 'AND'); hi = operand(); x = { op: 'between', args: [l, lo, hi] }; }
    else if (isKw('IN')) {
      i++; eat('('); list = [operand()];
      while (peek().k === ',') { i++; list.push(operand()); }
      eat(')'); x = { op: 'in', args: [l, list] };
    }
    else throw new FilterError('Expected a comparison (=, <>, <, >, LIKE, BETWEEN, IN, IS NULL) after ' + describe(toks[i - 1]), peek().p);
    return neg ? { op: 'not', args: [x] } : x;
  }
  var tree = orExpr();
  if (peek().k !== 'end') throw new FilterError('Unexpected ' + describe(peek()), peek().p);
  return tree;
}

/* ---------- evaluator: three-valued (true / false / null) ---------- */
var OWN = Object.prototype.hasOwnProperty;
var NUMERIC = /^\s*[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?\s*$/;

function value(node, props, opts) {
  if (OWN.call(node, 'lit')) return node.lit;
  if (OWN.call(node, 'prop')) {
    if (!props || !OWN.call(props, node.prop)) return null;   /* missing field reads as NULL (CQL2 req 2B) */
    var v = props[node.prop];
    return v === undefined ? null : v;
  }
  if (node.op === 'casei') { var s = value(node.args[0], props, opts); return s === null ? null : String(s).toLowerCase(); }
  return truth(node, props, opts);
}
/* coerce for comparison: number vs numeric string compares as numbers when opts.coerce */
function pair(a, b, opts) {
  if (typeof a === typeof b) return [a, b];
  if (opts.coerce) {
    if (typeof a === 'number' && typeof b === 'string' && NUMERIC.test(b)) return [a, parseFloat(b)];
    if (typeof b === 'number' && typeof a === 'string' && NUMERIC.test(a)) return [parseFloat(a), b];
  }
  return null;   /* incompatible types: CQL2 permission 2 lets us answer FALSE or error; we answer NULL (excluded) */
}
function cmp(op, a, b, opts) {
  if (a === null || b === null) return null;
  var p = pair(a, b, opts);
  if (!p) return op === '<>' ? true : (op === '=' ? false : null);
  a = p[0]; b = p[1];
  if (typeof a === 'number' && (isNaN(a) || isNaN(b))) return null;
  switch (op) {
    case '=': return a === b; case '<>': return a !== b;
    case '<': return a < b; case '<=': return a <= b;
    case '>': return a > b; case '>=': return a >= b;
  }
  throw new FilterError('Unknown operator ' + op, -1);
}
/* LIKE without RegExp: iterative wildcard match, % any run, _ one char, \ escapes; O(n*m) worst case */
function like(s, pat) {
  var si = 0, pi = 0, starP = -1, starS = 0, c, lit;
  var P = [], k;
  for (k = 0; k < pat.length; k++) {          /* pre-split the pattern into {w:'%'|'_'} or {c:char} */
    c = pat.charAt(k);
    if (c === '\\' && k + 1 < pat.length) { P.push({ c: pat.charAt(++k) }); }
    else if (c === '%') { if (!(P.length && P[P.length - 1].w === '%')) P.push({ w: '%' }); }
    else if (c === '_') P.push({ w: '_' });
    else P.push({ c: c });
  }
  while (si < s.length) {
    lit = P[pi];
    if (lit && (lit.w === '_' || (lit.c !== undefined && lit.c === s.charAt(si)))) { si++; pi++; }
    else if (lit && lit.w === '%') { starP = pi++; starS = si; }
    else if (starP >= 0) { pi = starP + 1; si = ++starS; }
    else return false;
  }
  while (pi < P.length && P[pi].w === '%') pi++;
  return pi === P.length;
}
function truth(node, props, opts) {
  var a, b, i, r, anyNull;
  if (OWN.call(node, 'lit')) return node.lit === null ? null : !!node.lit;
  switch (node.op) {
    case 'and':
      anyNull = false;
      for (i = 0; i < node.args.length; i++) { r = truth(node.args[i], props, opts); if (r === false) return false; if (r === null) anyNull = true; }
      return anyNull ? null : true;
    case 'or':
      anyNull = false;
      for (i = 0; i < node.args.length; i++) { r = truth(node.args[i], props, opts); if (r === true) return true; if (r === null) anyNull = true; }
      return anyNull ? null : false;
    case 'not': r = truth(node.args[0], props, opts); return r === null ? null : !r;
    case 'isNull': return value(node.args[0], props, opts) === null;
    case 'like':
      a = value(node.args[0], props, opts); b = value(node.args[1], props, opts);
      if (a === null || b === null) return null;
      return like(String(a), String(b));
    case 'between':
      a = value(node.args[0], props, opts);
      r = [cmp('>=', a, value(node.args[1], props, opts), opts), cmp('<=', a, value(node.args[2], props, opts), opts)];
      return truth({ op: 'and', args: [{ lit: r[0] }, { lit: r[1] }] }, props, opts);
    case 'in':
      a = value(node.args[0], props, opts); if (a === null) return null;
      anyNull = false;
      for (i = 0; i < node.args[1].length; i++) {
        r = cmp('=', a, value(node.args[1][i], props, opts), opts);
        if (r === true) return true; if (r === null) anyNull = true;
      }
      return anyNull ? null : false;
    case '=': case '<>': case '<': case '<=': case '>': case '>=':
      return cmp(node.op, value(node.args[0], props, opts), value(node.args[1], props, opts), opts);
    case 'casei': throw new FilterError('CASEI(...) is a value, not a condition', -1);
  }
  throw new FilterError('Unknown operator ' + node.op, -1);
}
/* a feature passes only when the filter is TRUE (CQL2 6.2: FALSE or NULL excludes it) */
function test(tree, props, opts) { return truth(tree, props, opts || { coerce: true }) === true; }

/* ---------- printer: tree back to CQL2 text (round trip) ---------- */
var PLAIN_ID = /^[A-Za-z_:][A-Za-z0-9_:.]*$/;
function printOperand(n) {
  if (OWN.call(n, 'prop')) return PLAIN_ID.test(n.prop) && !KEYWORDS.hasOwnProperty(n.prop.toUpperCase()) ? n.prop : '"' + n.prop.replace(/"/g, '""') + '"';
  if (OWN.call(n, 'lit')) {
    if (n.lit === null) return 'NULL';
    if (typeof n.lit === 'string') return "'" + n.lit.replace(/'/g, "''") + "'";
    if (typeof n.lit === 'boolean') return n.lit ? 'TRUE' : 'FALSE';
    return String(n.lit);
  }
  if (n.op === 'casei') return 'CASEI(' + printOperand(n.args[0]) + ')';
  return '(' + print(n) + ')';
}
var LEVEL = { or: 1, and: 2, not: 3 };
function print(n, parent) {
  var s, lv = LEVEL[n.op] || 4;
  if (OWN.call(n, 'lit')) return n.lit ? 'TRUE' : 'FALSE';
  switch (n.op) {
    case 'or': case 'and': s = n.args.map(function (a) { return print(a, lv); }).join(' ' + n.op.toUpperCase() + ' '); break;
    case 'not':
      var x = n.args[0];
      if (x.op === 'isNull') s = printOperand(x.args[0]) + ' IS NOT NULL';
      else if (x.op === 'like') s = printOperand(x.args[0]) + ' NOT LIKE ' + printOperand(x.args[1]);
      else if (x.op === 'in') s = printOperand(x.args[0]) + ' NOT IN (' + x.args[1].map(printOperand).join(', ') + ')';
      else if (x.op === 'between') s = printOperand(x.args[0]) + ' NOT BETWEEN ' + printOperand(x.args[1]) + ' AND ' + printOperand(x.args[2]);
      else s = 'NOT ' + print(x, 3);
      break;
    case 'isNull': s = printOperand(n.args[0]) + ' IS NULL'; break;
    case 'like': s = printOperand(n.args[0]) + ' LIKE ' + printOperand(n.args[1]); break;
    case 'in': s = printOperand(n.args[0]) + ' IN (' + n.args[1].map(printOperand).join(', ') + ')'; break;
    case 'between': s = printOperand(n.args[0]) + ' BETWEEN ' + printOperand(n.args[1]) + ' AND ' + printOperand(n.args[2]); break;
    default: s = printOperand(n.args[0]) + ' ' + n.op + ' ' + printOperand(n.args[1]);
  }
  return parent && lv < parent ? '(' + s + ')' : s;
}

module.exports = { parse: parse, test: test, truth: truth, print: print, like: like, FilterError: FilterError };
