// V270: an IGES 5.3 file of a box, written from the specification's fixed-column layout (Start, Global, Directory,
// Parameter, Terminate sections, 80 columns), as six untrimmed bilinear rational B-spline surfaces (entity 128).
// Our own test file: no third-party drawing is committed. Usage: node gen_iges_cube.mjs W D H > box.igs (metres).
const [W, D, H] = process.argv.slice(2).map(Number);
export function igesBox(w, d, h) {
  const P = (x, y, z) => [x, y, z];
  // each face's four corners, (u0 v0), (u1 v0), (u0 v1), (u1 v1), the first index fastest, as entity 128 orders them
  const faces = [
    [P(0, 0, 0), P(0, d, 0), P(w, 0, 0), P(w, d, 0)],
    [P(0, 0, h), P(w, 0, h), P(0, d, h), P(w, d, h)],
    [P(0, 0, 0), P(w, 0, 0), P(0, 0, h), P(w, 0, h)],
    [P(0, d, 0), P(0, d, h), P(w, d, 0), P(w, d, h)],
    [P(0, 0, 0), P(0, 0, h), P(0, d, 0), P(0, d, h)],
    [P(w, 0, 0), P(w, d, 0), P(w, 0, h), P(w, d, h)]];
  const pad = (s, n) => String(s).padStart(n, ' ');
  const num = (v) => (Number.isInteger(v) ? v.toFixed(1) : String(v));
  const S = ['Box written by BIM-Personal docs/research/experiments/v270-iges'];
  const hs = (s) => s.length + 'H' + s;
  const G = [hs(','), hs(';'), hs('box'), hs('box.igs'), hs('BIM-Personal'), hs('V270'), '32', '38', '6', '308', '15', hs('box'),
    '1.0', '6', hs('M'), '1', '1.0', hs('20261122.000000'), '1.0E-6', '100.0', hs('BIM-Personal'), hs('BIM-Personal'), '11', '0'].join(',') + ';';
  // a record split at its delimiters, never inside a parameter
  const lines = (text, width) => { const out = []; let cur = ''; const toks = text.match(/(\d+H[^]*?|[^,;]*)[,;]/g);
    let i = 0, rest = text; const parts = [];
    while (rest.length) { const h = /^(\d+)H/.exec(rest); let len;
      if (h) len = h[0].length + +h[1] + 1; else len = rest.search(/[,;]/) + 1;
      parts.push(rest.slice(0, len)); rest = rest.slice(len); }
    parts.forEach((t) => { if ((cur + t).length > width) { out.push(cur); cur = ''; } cur += t; });
    if (cur) out.push(cur); return out; };
  const Dl = [], Pl = [];
  faces.forEach((F, k) => {
    const de = 2 * k + 1;
    const params = ['128', '1', '1', '1', '1', '0', '0', '1', '0', '0', '0.0', '0.0', '1.0', '1.0', '0.0', '0.0', '1.0', '1.0',
      '1.0', '1.0', '1.0', '1.0', ...F.flat().map(num), '0.0', '1.0', '0.0', '1.0'];
    // the record split at delimiters into lines of at most 64 columns
    const recs = []; let cur = '';
    params.forEach((p, i) => { const tok = p + (i === params.length - 1 ? ';' : ','); if ((cur + tok).length > 64) { recs.push(cur); cur = ''; } cur += tok; });
    if (cur) recs.push(cur);
    const pStart = Pl.length + 1;
    recs.forEach((r) => Pl.push(r.padEnd(64, ' ') + pad(de, 8) + 'P' + pad(Pl.length + 1, 7)));
    Dl.push(pad(128, 8) + pad(pStart, 8) + pad(0, 8) + pad(0, 8) + pad(0, 8) + pad(0, 8) + pad(0, 8) + pad(0, 8) + '00000000' + 'D' + pad(de, 7));
    Dl.push(pad(128, 8) + pad(0, 8) + pad(0, 8) + pad(recs.length, 8) + pad(0, 8) + pad('', 8) + pad('', 8) + pad('FACE', 8) + pad(k, 8) + 'D' + pad(de + 1, 7));
  });
  const out = [];
  S.forEach((s, i) => out.push(s.padEnd(72, ' ') + 'S' + pad(i + 1, 7)));
  lines(G, 72).forEach((g, i) => out.push(g.padEnd(72, ' ') + 'G' + pad(i + 1, 7)));
  out.push(...Dl, ...Pl);
  out.push(('S' + pad(S.length, 7) + 'G' + pad(lines(G, 72).length, 7) + 'D' + pad(Dl.length, 7) + 'P' + pad(Pl.length, 7)).padEnd(72, ' ') + 'T' + pad(1, 7));
  return out.join('\n') + '\n';
}
if (W > 0 && D > 0 && H > 0) process.stdout.write(igesBox(W, D, H));
