/* V173 research: run the CQL2-subset sketch over edge cases. node run.js */
'use strict';
var F = require('./cql2-subset.js');
var pass = 0, fail = 0, rows = [];
function check(name, got, want) {
  var ok = JSON.stringify(got) === JSON.stringify(want);
  ok ? pass++ : fail++;
  rows.push((ok ? 'ok   ' : 'FAIL ') + name + (ok ? '' : '  got ' + JSON.stringify(got) + ' want ' + JSON.stringify(want)));
}
function t(expr, props, opts) { return F.test(F.parse(expr), props, opts); }
function tri(expr, props, opts) { return F.truth(F.parse(expr), props, opts || { coerce: true }); }
function err(expr) { try { F.parse(expr); return 'parsed'; } catch (e) { return e instanceof F.FilterError ? 'error' : 'CRASH ' + e; } }

var p = { NAME: "O'Brien", ZONE: 'R2', POP: 1500, POP_S: '1500', AREA: '10', H: null, 'Land use': 'Residential', and: 'kw', Code: 'A_1', Pct: '10%' };

/* quotes */
check("'' escape", t("NAME = 'O''Brien'", p), true);
check("\\' escape", t("NAME = 'O\\'Brien'", p), true);
check('unclosed string is an error', err("NAME = 'O"), 'error');
check('quoted field with space', t('"Land use" = \'Residential\'', p), true);
check('unquoted field with space is an error', err("Land use = 'x'"), 'error');
check('keyword as field needs quotes', t('"and" = \'kw\'', p), true);
check('bare keyword as field is an error', err("and = 'kw'"), 'error');
/* nulls: three-valued */
check('missing field = 1 is NULL', tri('NOPE = 1', p), null);
check('null field = 1 is NULL', tri('H = 1', p), null);
check('null field <> 1 is NULL (not true)', tri('H <> 1', p), null);
check('NOT (H = 1) stays NULL, excluded', t('NOT (H = 1)', p), false);
check('H IS NULL', t('H IS NULL', p), true);
check('missing IS NULL', t('NOPE IS NULL', p), true);
check('POP IS NOT NULL', t('POP IS NOT NULL', p), true);
check('NULL OR TRUE = TRUE', tri('H = 1 OR POP = 1500', p), true);
check('NULL AND FALSE = FALSE', tri('H = 1 AND POP = 1', p), false);
check('NULL AND TRUE = NULL', tri('H = 1 AND POP = 1500', p), null);
check('x IN (..., NULL) not found is NULL', tri("ZONE IN ('R1', NULL)", p), null);
check('NOT IN with a NULL item excludes all (SQL trap)', t("ZONE NOT IN ('R1', NULL)", p), false);
/* precedence NOT > AND > OR */
check('a OR b AND c = a OR (b AND c)', JSON.stringify(F.parse('A = 1 OR B = 2 AND C = 3')) === JSON.stringify(F.parse('A = 1 OR (B = 2 AND C = 3)')), true);
check('NOT binds tighter than AND', JSON.stringify(F.parse('NOT A = 1 AND B = 2')) === JSON.stringify(F.parse('(NOT A = 1) AND B = 2')), true);
check('precedence result', t("ZONE = 'X' OR POP = 1500 AND AREA = '10'", p), true);
check('grouping changes result', t("(ZONE = 'X' OR POP = 1500) AND AREA = '99'", p), false);
/* IN lists */
check('IN strings', t("ZONE IN ('R1','R2','R3')", p), true);
check('NOT IN strings', t("ZONE NOT IN ('R1','R3')", p), true);
check('IN numbers', t('POP IN (1, 1500)', p), true);
check('empty IN list is an error', err('ZONE IN ()'), 'error');
/* BETWEEN */
check('BETWEEN inclusive low', t('POP BETWEEN 1500 AND 2000', p), true);
check('BETWEEN inclusive high', t('POP BETWEEN 1000 AND 1500', p), true);
check('NOT BETWEEN', t('POP NOT BETWEEN 1 AND 10', p), true);
check('BETWEEN AND chained with AND', t("POP BETWEEN 1 AND 2000 AND ZONE = 'R2'", p), true);
/* LIKE */
check("LIKE prefix %", t("ZONE LIKE 'R%'", p), true);
check("LIKE single _", t("ZONE LIKE 'R_'", p), true);
check("LIKE _ needs exactly one", t("ZONE LIKE 'R__'", p), false);
check("LIKE is case sensitive", t("ZONE LIKE 'r%'", p), false);
check("CASEI makes it insensitive", t("CASEI(ZONE) LIKE CASEI('r%')", p), true);
check("LIKE escaped underscore literal", t("Code LIKE 'A\\_1'", p), true);
check("LIKE escaped underscore does not match other char", t("Code LIKE 'A\\_1'", { Code: 'AX1' }), false);
check("LIKE escaped percent", t("Pct LIKE '%\\%'", p), true);
check("LIKE on a number field compares its text", t("POP LIKE '15%'", p), true);
check("LIKE %%% collapses", t("ZONE LIKE '%%%2'", p), true);
/* numeric strings (ArcGIS-sourced GeoJSON) */
check("number field = '1500' with coercion", t("POP = '1500'", p), true);
check("string field '1500' = 1500 with coercion", t('POP_S = 1500', p), true);
check("string field '10' > 9 numeric, not text", t('AREA > 9', p), true);
check("same without coercion is NULL (excluded)", tri('AREA > 9', p, { coerce: false }), null);
check("text compare '10' > '9' is false (lexicographic)", t("AREA > '9'", p), false);
check("non-numeric string vs number stays incomparable", tri('ZONE > 1', p), null);
check("'1e3' counts as numeric", t('X = 1000', { X: '1e3' }), true);
check("' 12 ' with spaces counts as numeric", t('X = 12', { X: ' 12 ' }), true);
check("'' is not numeric", tri('X = 0', { X: '' }), false);
/* booleans */
check('boolean field = TRUE', t('B = TRUE', { B: true }), true);
check('bare TRUE filter', t('TRUE', {}), true);
check('keywords case-insensitive', t("zone = 'R2' and pop >= 1000", { zone: 'R2', pop: 1001 }), true);
/* safety */
check('prototype name is not a field', tri('constructor IS NULL', {}), true);
check('__proto__ is not a field', tri('"__proto__" IS NULL', {}), true);
check('toString = 1 is NULL', tri('toString = 1', {}), null);
check('JS code is a syntax error', err("NAME = ''); alert(1); ('"), 'error');
check('function call syntax is an error', err('alert(1)'), 'error');
var deep = ''; for (var d = 0; d < 200; d++) deep += '('; deep += 'A = 1'; for (d = 0; d < 200; d++) deep += ')';
check('200 nested parentheses is a clean error', err(deep), 'error');
var deepNot = ''; for (d = 0; d < 5000; d++) deepNot += 'NOT '; deepNot += 'A = 1';
check('NOT x5000 is a clean error, not a stack overflow', err(deepNot), 'error');
check('trailing junk is an error', err('A = 1 B'), 'error');
check('!= accepted as <>', t("ZONE != 'R1'", p), true);

/* round trip: print(parse(x)) parses to the same tree */
var RT = ["NAME = 'O''Brien'", '"Land use" = \'Residential\' AND POP > 10', 'A = 1 OR B = 2 AND C = 3',
  '(A = 1 OR B = 2) AND C = 3', "NOT (A = 1 OR B = 2)", "Z NOT IN ('a', 'b')", 'H IS NOT NULL', "CASEI(N) LIKE CASEI('a%')",
  'P NOT BETWEEN 1 AND 2', '"and" = 1', 'NOT NOT A = 1'];
RT.forEach(function (s) {
  var a = F.parse(s), txt = F.print(a), b = F.parse(txt);
  check('round trip ' + s + '  ->  ' + txt, JSON.stringify(a) === JSON.stringify(b), true);
});

/* LIKE speed: our matcher vs a RegExp built from the pattern on a pathological case */
var long = new Array(20001).join('a');
var pat = '%a%a%a%a%a%a%a%b';
var t0 = Date.now(); var r1 = F.like(long, pat); var ms1 = Date.now() - t0;
rows.push('info LIKE matcher, 20000 chars, pattern ' + pat + ': ' + r1 + ' in ' + ms1 + ' ms');
var re = new RegExp('^' + pat.replace(/%/g, '.*') + '$');
[20, 40, 60, 80].forEach(function (n) {
  var str = new Array(n + 1).join('a');
  var t1 = Date.now(); var r2 = re.test(str);
  rows.push('info RegExp ' + re + ' on ' + n + ' chars: ' + r2 + ' in ' + (Date.now() - t1) + ' ms');
});

/* parse + evaluate speed: 10000 features */
var feats = []; for (var k = 0; k < 10000; k++) feats.push({ ZONE: k % 3 ? 'R2' : 'C1', POP: String(k), NAME: 'n' + k });
var tree = F.parse("ZONE IN ('R1','R2') AND POP BETWEEN 100 AND 5000 AND NAME LIKE 'n1%'");
t0 = Date.now(); var hits = 0; for (k = 0; k < feats.length; k++) if (F.test(tree, feats[k])) hits++;
rows.push('info 10000 features evaluated in ' + (Date.now() - t0) + ' ms, ' + hits + ' pass');

console.log(rows.join('\n'));
console.log('\n' + pass + ' passed, ' + fail + ' failed');
var fs = require('fs');
var src = fs.readFileSync(__dirname + '/cql2-subset.js', 'utf8');
console.log('sketch size: ' + src.length + ' bytes, ' + src.split('\n').length + ' lines');
