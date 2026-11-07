#!/usr/bin/env node
/* engine_modules.cjs -- keeps the engine's import and export lines true.

     node tools/engine_modules.cjs           rewrite every engine file's imports and exports
     node tools/engine_modules.cjs --check   exit 1 when any file's imports or exports are wrong

   Every file in src/js/engine/ (but _begin.js and _end.js) is an ES module:

     import { a, b } from '../core/state.js';      what it uses from other files
     ...its code...
     export { c, d };                              what other files use from it

   The build (tools/build_app.py) drops those lines and joins the files, in src/index.html's order,
   into the engine's one function, exactly as before. So the app runs the same code; the lines say
   which file needs which, and let Node load a file on its own (tests/unit/).

   How: the files are joined (without their import/export lines) and parsed as one script with
   TypeScript's parser; every name declared at the top of the engine's function is traced to the
   file that declares it and to every file that uses it. A file imports exactly the names it uses
   from other files and exports exactly the names other files use.

   A name assigned in another file than its own (x = 1 from elsewhere) cannot be written through an
   import: the declaring file exports a setter (setX) and the other files call it. --check reports
   any such write.

   Needs TypeScript (a development tool, not part of the app): a local or global install. */
'use strict';
var fs = require('fs'), path = require('path'), cp = require('child_process');

function loadTs() {
  try { return require('typescript'); } catch (e) {}
  try { return require(path.join(cp.execSync('npm root -g').toString().trim(), 'typescript')); } catch (e) {}
  console.error('engine_modules: TypeScript is needed (npm install -g typescript)');
  process.exit(2);
}
var ts = loadTs();

var ROOT = path.resolve(__dirname, '..');
var SRC = path.join(ROOT, 'src');
var ENGINE = path.join(SRC, 'js', 'engine');
var WIDTH = 110;

/* The same patterns tools/build_app.py strips. */
var HEAD = /^(?:import \{[^}]*\} from '[^']+';\n)+\n/;
var TAIL = /\nexport \{[^}]*\};\n$/;

function engineFiles() {
  var html = fs.readFileSync(path.join(SRC, 'index.html'), 'utf8');
  var out = [], re = /<!-- @include js\/engine\/(\S+) -->/g, m;
  while ((m = re.exec(html))) out.push(m[1]);
  return out;
}

function strip(t) { return t.replace(HEAD, '').replace(TAIL, '\n'); }

function analyse(files) {
  var text = '', starts = [];
  files.forEach(function (f) {
    var raw = fs.readFileSync(path.join(ENGINE, f), 'utf8');
    starts.push([text.length, f]);
    text += (f === '_begin.js' || f === '_end.js') ? raw : strip(raw);
  });
  function fileAt(pos) {
    var lo = 0, hi = starts.length - 1;
    while (lo < hi) { var mid = (lo + hi + 1) >> 1; if (starts[mid][0] <= pos) lo = mid; else hi = mid - 1; }
    return starts[lo][1];
  }
  var name = '/engine.js';
  var sf = ts.createSourceFile(name, text, ts.ScriptTarget.ES5, true, ts.ScriptKind.JS);
  var host = ts.createCompilerHost({ allowJs: true });
  var get = host.getSourceFile;
  host.getSourceFile = function (n) { return n === name ? sf : get.apply(host, arguments); };
  var prog = ts.createProgram([name], { allowJs: true, noLib: true, noResolve: true }, host);
  var ch = prog.getTypeChecker();
  var tryBlock = null;
  (function find(n) { if (tryBlock) return; if (ts.isTryStatement(n)) { tryBlock = n.tryBlock; return; } ts.forEachChild(n, find); })(sf);
  if (!tryBlock) throw new Error('the engine has no try block');

  var top = new Map();   // symbol -> {name, file}
  tryBlock.statements.forEach(function (st) {
    var f = fileAt(st.getStart());
    function add(id) { var s = ch.getSymbolAtLocation(id); if (s && !top.has(s)) top.set(s, { name: id.text, file: f }); }
    if (ts.isFunctionDeclaration(st) && st.name) add(st.name);
    else if (ts.isVariableStatement(st)) st.declarationList.declarations.forEach(function (d) { if (ts.isIdentifier(d.name)) add(d.name); });
  });
  var A = ts.SyntaxKind;
  function isWrite(id) {
    var p = id.parent;
    if (ts.isBinaryExpression(p) && p.left === id && p.operatorToken.kind >= A.FirstAssignment && p.operatorToken.kind <= A.LastAssignment) return true;
    if ((ts.isPrefixUnaryExpression(p) || ts.isPostfixUnaryExpression(p)) && (p.operator === A.PlusPlusToken || p.operator === A.MinusMinusToken)) return true;
    return false;
  }
  var uses = {}, writes = [];   // uses[file][fromFile] = Set(names)
  files.forEach(function (f) { uses[f] = {}; });
  (function walk(n) {
    if (ts.isIdentifier(n)) {
      var s = ch.getSymbolAtLocation(n), t = s && top.get(s);
      if (t) {
        var f = fileAt(n.getStart());
        if (f !== t.file) {
          (uses[f][t.file] = uses[f][t.file] || new Set()).add(t.name);
          if (isWrite(n)) writes.push(f + ': ' + t.name + ' (declared in ' + t.file + ')');
        }
      }
    }
    ts.forEachChild(n, walk);
  })(tryBlock);
  var exportsOf = {};
  files.forEach(function (f) { exportsOf[f] = new Set(); });
  files.forEach(function (f) { Object.keys(uses[f]).forEach(function (g) { uses[f][g].forEach(function (x) { exportsOf[g].add(x); }); }); });
  return { uses: uses, exportsOf: exportsOf, writes: writes };
}

function rel(from, to) {
  var r = path.posix.relative(path.posix.dirname(from), to);
  return r.charAt(0) === '.' ? r : './' + r;
}
function sorted(set) { return Array.from(set).sort(function (a, b) { return a < b ? -1 : a > b ? 1 : 0; }); }
function wrap(names, indent) {
  var lines = [], cur = indent;
  names.forEach(function (n, i) {
    var piece = n + (i < names.length - 1 ? ',' : '');
    if (cur.length > indent.length && cur.length + 1 + piece.length > WIDTH) { lines.push(cur); cur = indent; }
    cur += (cur.length > indent.length ? ' ' : '') + piece;
  });
  lines.push(cur);
  return lines.join('\n');
}
function statement(kw, names, tail) {
  var one = kw + ' { ' + names.join(', ') + ' }' + tail;
  if (one.length <= WIDTH) return one + '\n';
  return kw + ' {\n' + wrap(names, '  ') + '\n}' + tail + '\n';
}

function render(f, a, order) {
  var head = '';
  order.forEach(function (g) {
    var s = a.uses[f][g];
    if (s && s.size) head += statement('import', sorted(s), " from '" + rel(f, g) + "';");
  });
  if (head) head += '\n';
  var ex = sorted(a.exportsOf[f]);
  var tail = ex.length ? '\n' + statement('export', ex, ';') : '';
  var body = strip(fs.readFileSync(path.join(ENGINE, f), 'utf8'));
  return head + (tail ? body.slice(0, -1) + tail : body);
}

function main(argv) {
  var check = argv.indexOf('--check') >= 0;
  var files = engineFiles();
  var a = analyse(files);
  var modules = files.filter(function (f) { return f !== '_begin.js' && f !== '_end.js'; });
  var wrong = [];
  modules.forEach(function (f) {
    var want = render(f, a, files);
    var p = path.join(ENGINE, f);
    if (fs.readFileSync(p, 'utf8') !== want) {
      if (check) wrong.push(f); else fs.writeFileSync(p, want);
    }
  });
  if (a.writes.length) {
    console.log('assigned outside the file that declares it (export a setter and call it):');
    a.writes.forEach(function (w) { console.log('  ' + w); });
  }
  if (check) {
    if (wrong.length) {
      console.log('imports or exports out of date in ' + wrong.length + ' file(s): ' + wrong.slice(0, 10).join(', ') +
        (wrong.length > 10 ? ', ...' : '') + '\nrun: node tools/engine_modules.cjs');
    }
    if (wrong.length || a.writes.length) return 1;
    console.log('engine modules: ' + modules.length + ' files, imports and exports correct');
    return 0;
  }
  console.log('engine modules: ' + modules.length + ' files written');
  return 0;
}

process.exit(main(process.argv.slice(2)));
