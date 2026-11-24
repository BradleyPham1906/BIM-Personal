// as-webaudio.js: measures, in Playwright's Chromium, (1) the AudioContext's state when made without a user gesture,
// under Chromium's default autoplay policy and with a click first; (2) how fast an OfflineAudioContext renders a
// procedural soundscape (white noise through a band-pass filter: rain or wind) with N sources, each through a
// PannerNode with panningModel 'HRTF' or 'equalpower' and the inverse distance model, as the realtime factor (seconds
// of audio per second of wall time). Only the browser's own Web Audio is used; no third-party code.
// Usage: node as-webaudio.js
'use strict';
const { chromium } = require('playwright');
(async () => {
  const out = { };
  for (const flags of [[], ['--autoplay-policy=user-gesture-required']]) {
    const browser = await chromium.launch({ args: flags });
    const page = await browser.newPage();
    await page.setContent('<button id=b>start</button>');
    const r = await page.evaluate(async () => {
      const a = new AudioContext(); const s0 = a.state;
      let pol = (navigator.getAutoplayPolicy ? navigator.getAutoplayPolicy('audiocontext') : 'n/a');
      return { stateBefore: s0, policy: pol, sampleRate: a.sampleRate, baseLatency: a.baseLatency };
    });
    await page.click('#b');
    r.stateAfterClickNewContext = await page.evaluate(async () => { const a = new AudioContext(); await new Promise(z => setTimeout(z, 50)); return a.state; });
    out[flags.length ? 'flag user-gesture-required' : 'default launch'] = r;
    if (!flags.length) {
      out.version = browser.version();
      out.render = await page.evaluate(async () => {
        const res = [];
        for (const model of ['equalpower', 'HRTF']) for (const N of [1, 8, 32, 64]) {
          const secs = 10, sr = 48000, ctx = new OfflineAudioContext(2, secs * sr, sr);
          const buf = ctx.createBuffer(1, sr * 2, sr), d = buf.getChannelData(0); let seed = 1;
          for (let i = 0; i < d.length; i++) { seed = (seed * 1103515245 + 12345) & 0x7fffffff; d[i] = seed / 0x3fffffff - 1; }
          for (let k = 0; k < N; k++) {
            const src = ctx.createBufferSource(); src.buffer = buf; src.loop = true;
            const f = ctx.createBiquadFilter(); f.type = 'bandpass'; f.frequency.value = 400 + 300 * k; f.Q.value = 0.7;
            const p = ctx.createPanner(); p.panningModel = model; p.distanceModel = 'inverse'; p.refDistance = 1; p.rolloffFactor = 1;
            p.positionX.setValueAtTime(-20 + k, 0); p.positionX.linearRampToValueAtTime(20 - k, secs); p.positionZ.value = -5 - k;
            src.connect(f).connect(p).connect(ctx.destination); src.start(k * 0.01);
          }
          const t0 = performance.now(); await ctx.startRendering(); const ms = performance.now() - t0;
          res.push({ model, sources: N, renderMs: Math.round(ms), realtimeFactor: +(secs * 1000 / ms).toFixed(1) });
        }
        return res;
      });
      // the inverse model's gain at 1, 2, 4, 8, 16 m (refDistance 1, rolloff 1), read back from the browser
      out.inverseGain = await page.evaluate(async () => {
        const g = [];
        for (const d of [1, 2, 4, 8, 16]) {
          const ctx = new OfflineAudioContext(2, 4800, 48000), c = ctx.createConstantSource(), p = ctx.createPanner();
          p.panningModel = 'equalpower'; p.distanceModel = 'inverse'; p.refDistance = 1; p.rolloffFactor = 1; p.positionZ.value = -d;
          c.connect(p).connect(ctx.destination); c.start();
          const b = await ctx.startRendering(), L = b.getChannelData(0)[4000], R = b.getChannelData(1)[4000];
          g.push({ m: d, gain: +Math.sqrt(L * L + R * R).toFixed(4), dB: +(20 * Math.log10(Math.sqrt(L * L + R * R))).toFixed(2) });
        }
        return g;
      });
    }
    await browser.close();
  }
  console.log(JSON.stringify(out, null, 1));
})();
