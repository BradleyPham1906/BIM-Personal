/* browser.mjs -- a stand-in for the browser, enough for the engine's top-level code to run in Node.
   Every page element is a stub that accepts what the engine does to it and draws nothing. */
function stub(name) {
  const fn = function () { return stub(name + '()'); };
  return new Proxy(fn, {
    get(t, k) {
      if (k === Symbol.toPrimitive) return () => '';
      if (k === Symbol.iterator) return function* () {};
      if (k === 'length') return 0;
      if (k === 'then') return undefined;
      if (!(k in t)) t[k] = stub(name + '.' + String(k));
      return t[k];
    },
    set(t, k, v) { t[k] = v; return true; },
    construct() { return stub('new ' + name); },
  });
}

function storage() {
  const m = new Map();
  return {
    getItem: (k) => (m.has(k) ? m.get(k) : null), setItem: (k, v) => { m.set(k, String(v)); },
    removeItem: (k) => { m.delete(k); }, clear: () => m.clear(), key: (i) => [...m.keys()][i] ?? null,
    get length() { return m.size; },
  };
}

export function installBrowser(g) {
  if (g.__a3dBrowserStub) return;
  g.__a3dBrowserStub = true;
  g.window = g;
  g.self = g;
  g.document = stub('document');
  g.localStorage = storage();
  g.sessionStorage = storage();
  if (!g.navigator || !g.navigator.userAgent) {
    try { Object.defineProperty(g, 'navigator', { value: { userAgent: 'node', platform: 'node', language: 'en' }, configurable: true }); } catch (e) {}
  }
  g.location = { href: 'http://localhost/', origin: 'http://localhost', protocol: 'http:', host: 'localhost', hash: '', search: '', pathname: '/' };
  g.addEventListener = () => {};
  g.removeEventListener = () => {};
  g.matchMedia = () => ({ matches: false, addEventListener() {}, addListener() {} });
  g.requestAnimationFrame = () => 0;
  g.cancelAnimationFrame = () => {};
  g.getComputedStyle = () => stub('style');
  g.devicePixelRatio = 1;
  g.innerWidth = 1280;
  g.innerHeight = 800;
  for (const n of ['HTMLElement', 'Element', 'Node', 'Image', 'MutationObserver', 'ResizeObserver',
    'IntersectionObserver', 'Worker', 'XMLHttpRequest', 'FileReader', 'DOMParser', 'XMLSerializer',
    'Path2D', 'indexedDB', 'OpenSkp', 'caches', 'BroadcastChannel']) {
    if (!(n in g)) g[n] = stub(n);
  }
}
