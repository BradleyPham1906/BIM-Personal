// esbuild plugin: map "three" to the page's global BIMTHREE (the app's own pinned three.js)
export const threeGlobal = { name: "three-global", setup(b) {
  b.onResolve({ filter: /^three$/ }, () => ({ path: "three", namespace: "tg" }));
  b.onLoad({ filter: /.*/, namespace: "tg" }, () => ({ contents: "module.exports = window.BIMTHREE", loader: "js" }));
}};
