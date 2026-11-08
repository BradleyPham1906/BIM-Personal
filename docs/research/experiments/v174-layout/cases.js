/* V174 research experiment: the auto layout test cases, built from the edges of Figma's documented rules.
   cmp: 'yes' where Figma's rule and CSS flexbox should give the same boxes; 'no' with the reason where
   they should not (the comparison still runs, to show the difference). */
function box(w, h, o) { var r = { w: w, h: h, sizeW: 'fixed', sizeH: 'fixed' }, k; for (k in (o || {})) r[k] = o[k]; return r; }
function frame(o, kids) { var r = { dir: 'row', gap: 0, pad: 0, alignMain: 'start', alignCross: 'start', sizeW: 'fixed', sizeH: 'fixed', w: 300, h: 100, children: kids }, k; for (k in o) r[k] = o[k]; return r; }
var C = [];
function add(name, cmp, F, why) { C.push({ name: name, cmp: cmp, F: F, why: why || '' }); }

add('row fixed, gap 10, pad 8', 'yes', frame({ gap: 10, pad: 8 }, [box(50, 30), box(60, 40), box(70, 20)]));
add('column fixed, gap 12', 'yes', frame({ dir: 'column', gap: 12, w: 120, h: 300 }, [box(50, 30), box(60, 40), box(70, 20)]));
add('align center/center', 'yes', frame({ gap: 10, alignMain: 'center', alignCross: 'center' }, [box(50, 30), box(60, 40)]));
add('align end/end', 'yes', frame({ gap: 10, alignMain: 'end', alignCross: 'end', pad: [4, 6, 8, 10] }, [box(50, 30), box(60, 40)]));
add('hug both, pad 10', 'yes', frame({ sizeW: 'hug', sizeH: 'hug', gap: 5, pad: 10 }, [box(40, 20), box(30, 35)]));
add('hug: Figma 40px text + 10px pads = 60', 'yes', frame({ sizeW: 'hug', sizeH: 'hug', pad: [0, 10, 0, 10] }, [box(40, 16)]));
add('two fill share equally', 'yes', frame({ gap: 10 }, [box(0, 30, { sizeW: 'fill' }), box(0, 30, { sizeW: 'fill' })]));
add('fill beside fixed', 'yes', frame({ gap: 10, pad: 10 }, [box(80, 30), box(0, 30, { sizeW: 'fill' }), box(40, 30)]));
add('fill with min widths, room for both', 'yes', frame({ gap: 0 }, [box(0, 30, { sizeW: 'fill', minW: 100 }), box(0, 30, { sizeW: 'fill' })]));
add('fill with min widths, min binds', 'yes', frame({ gap: 0 }, [box(0, 30, { sizeW: 'fill', minW: 200 }), box(0, 30, { sizeW: 'fill' })]));
add('fill with max, cascade (spec loop)', 'yes', frame({ gap: 0 }, [box(0, 30, { sizeW: 'fill', maxW: 50 }), box(0, 30, { sizeW: 'fill', maxW: 110 }), box(0, 30, { sizeW: 'fill' })]));
add('fill with max, order reversed (Yoga differs)', 'yes', frame({ gap: 0 }, [box(0, 30, { sizeW: 'fill' }), box(0, 30, { sizeW: 'fill', maxW: 110 }), box(0, 30, { sizeW: 'fill', maxW: 50 })]));
add('fill with min > max (min wins)', 'yes', frame({ gap: 0 }, [box(0, 30, { sizeW: 'fill', minW: 120, maxW: 80 }), box(0, 30, { sizeW: 'fill' })]));
add('fill when fixed overflow', 'yes', frame({ gap: 10, w: 200 }, [box(150, 30), box(0, 30, { sizeW: 'fill' }), box(100, 30)]));
add('fill cross stretch', 'yes', frame({ gap: 10, pad: 10 }, [box(50, 30), box(60, 0, { sizeH: 'fill' })]));
add('fill cross stretch with max', 'yes', frame({ gap: 10, alignCross: 'center' }, [box(50, 30), box(60, 0, { sizeH: 'fill', maxH: 40 })]));
add('hidden child leaves the flow', 'yes', frame({ gap: 10 }, [box(50, 30), box(60, 40, { hidden: true }), box(70, 20)]));
add('absolute child leaves the flow', 'yes', frame({ gap: 10, pad: 10 }, [box(50, 30), box(20, 20, { absolute: true, x: 270, y: -10 }), box(70, 20)]));
add('zero children, hug', 'yes', frame({ sizeW: 'hug', sizeH: 'hug', pad: [3, 4, 5, 6] }, []));
add('zero children, fixed smaller than padding', 'yes', frame({ w: 10, h: 10, pad: 20 }, []), 'Figma: a frame is never smaller than its padding; CSS border-box lets the box be the padding (40) too, so both give 40: kept as a check');
add('auto gap between', 'yes', frame({ gap: 'auto', auto: 'between' }, [box(50, 30), box(60, 30), box(70, 30)]));
add('auto gap evenly', 'yes', frame({ gap: 'auto', auto: 'evenly' }, [box(50, 30), box(60, 30), box(70, 30)]));
add('auto gap around', 'yes', frame({ gap: 'auto', auto: 'around' }, [box(50, 30), box(60, 30), box(70, 30)]));
add('auto gap, one child sits at start', 'yes', frame({ gap: 'auto', auto: 'between' }, [box(50, 30)]));
add('auto gap between, overflow: flush, no negative gap', 'yes', frame({ gap: 'auto', auto: 'between', w: 150 }, [box(60, 30), box(60, 30), box(60, 30)]));
add('auto gap around, overflow', 'yes', frame({ gap: 'auto', auto: 'around', w: 150 }, [box(60, 30), box(60, 30), box(60, 30)]), 'CSS falls back to safe center, which on overflow is start (probe-overflow.js); Figma says only that the gap stops at 0');
add('numeric gap, center, overflow', 'yes', frame({ gap: 10, alignMain: 'center', w: 150 }, [box(60, 30), box(60, 30), box(60, 30)]));
add('wrap row, gap 10/20', 'yes', frame({ wrap: true, gap: 10, crossGap: 20, h: 200 }, [box(100, 30), box(100, 40), box(100, 30), box(100, 50)]));
add('wrap with a long child', 'yes', frame({ wrap: true, gap: 10, crossGap: 10, h: 300 }, [box(50, 30), box(400, 40), box(50, 30)]));
add('wrap exact fit stays on line', 'yes', frame({ wrap: true, gap: 0, h: 200 }, [box(100, 30), box(100, 30), box(100, 30), box(100, 30)]));
add('wrap, hidden child does not take a slot', 'yes', frame({ wrap: true, gap: 10, crossGap: 10, h: 200 }, [box(140, 30), box(140, 30, { hidden: true }), box(140, 30), box(140, 30)]));
add('wrap fill children with min width', 'yes', frame({ wrap: true, gap: 10, crossGap: 10, h: 200 }, [box(0, 30, { sizeW: 'fill', minW: 120 }), box(0, 30, { sizeW: 'fill', minW: 120 }), box(0, 30, { sizeW: 'fill', minW: 120 })]));
add('wrap fill without min stays one line', 'yes', frame({ wrap: true, gap: 10, crossGap: 10, h: 200 }, [box(0, 30, { sizeW: 'fill' }), box(0, 30, { sizeW: 'fill' }), box(0, 30, { sizeW: 'fill' }), box(0, 30, { sizeW: 'fill' })]));
add('wrap, tracks centred', 'yes', frame({ wrap: true, gap: 10, crossGap: 10, alignCross: 'center', h: 200 }, [box(140, 30), box(140, 50), box(140, 30)]));
add('wrap, tracks spread (between)', 'yes', frame({ wrap: true, gap: 10, crossGap: 10, alignContent: 'between', h: 200 }, [box(140, 30), box(140, 50), box(140, 30)]));
add('wrap column', 'yes', frame({ dir: 'column', wrap: true, gap: 10, crossGap: 10, w: 300, h: 100 }, [box(50, 40), box(60, 40), box(70, 40)]));
add('hug frame with a fill child becomes fixed', 'no', frame({ sizeW: 'hug', w: 300, gap: 10 }, [box(50, 30), box(0, 30, { sizeW: 'fill' })]), 'Figma: the frame turns Fixed and the Fill child takes the rest; CSS max-content: the Fill child is 0 wide');
add('hug cross with a stretch child', 'no', frame({ sizeH: 'hug', h: 100, gap: 10 }, [box(50, 30), box(60, 0, { sizeH: 'fill' })]), 'Figma: the frame turns Fixed (100); CSS: the line is the tallest other child (30)');
add('hug with min width larger than content', 'yes', frame({ sizeW: 'hug', sizeH: 'hug', minW: 200, gap: 10, alignMain: 'center' }, [box(50, 30), box(60, 30)]));
add('negative gap, last on top', 'yes', frame({ gap: -20, sizeW: 'hug' }, [box(60, 30), box(60, 30), box(60, 30)]), 'CSS gap cannot be negative; the page uses a negative margin instead');
add('nested hug frame', 'yes', frame({ gap: 10 }, [box(50, 30), frame({ sizeW: 'hug', sizeH: 'hug', dir: 'column', gap: 4, pad: 6 }, [box(20, 10), box(30, 10)])]));
module.exports = C;
