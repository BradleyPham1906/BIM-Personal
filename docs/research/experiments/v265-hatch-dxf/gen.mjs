import { loadEngine } from '../../../../tests/unit/helpers/engine.mjs';
import fs from 'node:fs';
const E = loadEngine();
const out = {};
for (const name of ['diagonal', 'diagonal-reverse', 'cross', 'brick', 'concrete', 'steel', 'dots', 'horizontal', 'vertical']) {
  const def = E.bimPatternDef(name);
  for (const ang of [0, 30]) {
    const W = def.mm * (def.w || 1) * 0.1, H = def.mm * 0.1;
    out[name + '@' + ang] = { W, H, ang, lines: def.lines || [], dots: def.dots || [], fam: E.dxfPatternLines(def, W, H, ang) };
  }
}
fs.writeFileSync(process.argv[2], JSON.stringify(out));
