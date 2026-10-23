/* Offline tests: no package installation required. Optional acorn validates ES5. */
var assert = require('assert'), fs = require('fs'), path = require('path');
var file = path.resolve(__dirname, '../../vendor/openbridge/icons.es5.js');
var api = require(file), checks = 0;
function check(ok) { assert.ok(ok); checks += 1; }
check(api.names().length === 17);
check(api.source('home') === fs.readFileSync(path.resolve(__dirname, '../../vendor/openbridge/icons/home.svg'), 'utf8'));
check(api.source('__proto__') === '');
check(api.svg('unknown') === '');
check(api.svg('__proto__') === '');
check(api.svg('constructor') === '');
check(api.svg('home').indexOf('aria-hidden="true"') >= 0);
check(api.svg('home', 'Home').indexOf('role="img"') >= 0);
check(api.svg('home', '<img src=x onerror="alert(1)">').indexOf('<img') < 0);
check(api.svg('home', '" onload="evil').indexOf('aria-label="&quot; onload=&quot;evil"') >= 0);
var n = api.names(); n.pop();check(api.names().length === 17);
api.names().forEach(function (name) { check(api.svg(name).indexOf('<svg ') === 0); });
try { require('acorn').parse(fs.readFileSync(file, 'utf8'), {ecmaVersion:5});checks += 1;console.log('ES5 syntax parsed with acorn'); }
catch (e) { if (e.code !== 'MODULE_NOT_FOUND') { throw e; } console.log('ES5 parser unavailable; syntax parser check skipped'); }
console.log(checks + ' adapter checks passed');
