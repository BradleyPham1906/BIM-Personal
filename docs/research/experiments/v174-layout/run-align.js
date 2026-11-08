/* V174 research experiment: align, distribute and tidy up on sample boxes. Run: node run-align.js */
var A = require('./align.js');
function show(t, r) { console.log(t + ': ' + JSON.stringify(r)); }
var row = [{ x: 0, y: 10, w: 40, h: 20 }, { x: 70, y: 0, w: 30, h: 50 }, { x: 150, y: 25, w: 50, h: 10 }, { x: 260, y: 5, w: 40, h: 30 }];
show('align top, to selection', A.alAlign(row, 'top', 'selection'));
show('align vcenter, to selection (bounds 0..50, centre 25)', A.alAlign(row, 'vcenter', 'selection').map(function (p) { return p.y; }));
show('align bottom, to key object #2 (bottom 35)', A.alAlign(row, 'bottom', 'key', 2).map(function (p) { return p.y; }));
show('one box, to selection -> to parent (0,0,400,300), right', A.alAlign([{ x: 10, y: 10, w: 40, h: 20 }], 'right', 'selection', null, { x: 0, y: 0, w: 400, h: 300 }));
var d1 = A.alDistribute(row, 'x', 'centres'); show('distribute centres x, step ' + d1.step, d1.pos.map(function (p) { return p.x; }));
var d2 = A.alDistribute(row, 'x', 'gaps-centre'); show('distribute equal gaps x, step ' + d2.step, d2.pos.map(function (p) { return p.x; }));
show('two boxes: distribute changes nothing', A.alDistribute(row.slice(0, 2), 'x', 'gaps-edge'));
/* a wide box whose centre is not the last: the two readings of "outermost stay" part */
var wide = [{ x: 0, y: 0, w: 40, h: 20 }, { x: 60, y: 0, w: 300, h: 20 }, { x: 250, y: 30, w: 40, h: 20 }];
var w1 = A.alDistribute(wide, 'x', 'gaps-centre'), w2 = A.alDistribute(wide, 'x', 'gaps-edge');
show('wide box, gaps-centre (Inkscape), step ' + w1.step, w1.pos.map(function (p) { return p.x; }));
show('wide box, gaps-edge (our Figma reading), step ' + w2.step, w2.pos.map(function (p) { return p.x; }));
/* overlapping boxes: more box than room */
var ov = [{ x: 0, y: 0, w: 100, h: 20 }, { x: 50, y: 0, w: 100, h: 20 }, { x: 120, y: 0, w: 100, h: 20 }];
var o1 = A.alDistribute(ov, 'x', 'gaps-edge'); show('overlapping, equal gaps, step ' + o1.step, o1.pos.map(function (p) { return p.x; }));
/* rotated: a 100 x 20 box at 90 degrees is 20 x 100 by its bounds; at 45 degrees 84.85 x 84.85 */
show('aabb rot 90', A.alAabb({ x: 0, y: 0, w: 100, h: 20, rot: 90 }));
show('aabb rot 45', A.alAabb({ x: 0, y: 0, w: 100, h: 20, rot: 45 }));
show('align left, a rotated 45 box with a plain one', A.alAlign([{ x: 0, y: 0, w: 100, h: 20, rot: 45 }, { x: 30, y: 60, w: 50, h: 20 }], 'left', 'selection'));
/* tidy up: gaps 20, 20, 19, 35 -> mode 20 */
var t = [{ x: 0, y: 0, w: 50, h: 20 }, { x: 70, y: 0, w: 50, h: 20 }, { x: 140, y: 0, w: 50, h: 20 }, { x: 209, y: 0, w: 50, h: 20 }, { x: 294, y: 0, w: 50, h: 20 }];
var td = A.alTidy1(t, 'x'); show('tidy up x, mode gap ' + td.gap, td.pos.map(function (p) { return p.x; }));
/* board units: 12 columns; three figures 4 wide on a 12-wide board, distribute gaps -> 0 */
var bd = [{ x: 0, y: 0, w: 4, h: 3 }, { x: 4.5, y: 0, w: 4, h: 3 }, { x: 8, y: 0, w: 4, h: 3 }];
var bd1 = A.alDistribute(bd, 'x', 'gaps-edge'); show('board units, 3 x 4 columns, step ' + bd1.step, bd1.pos.map(function (p) { return p.x; }));
