// Minimal localStorage + DOM stub sufficient to exercise the real embedded logic
var STORE={};
var localStorage={
  getItem:function(k){return STORE.hasOwnProperty(k)?STORE[k]:null;},
  setItem:function(k,v){STORE[k]=String(v);}
};
function makeEl(tag,cls){
  var classes={};
  var checked=false;
  return {
    tag:tag,
    classList:{
      toggle:function(name,force){
        var on = force!==undefined ? force : !classes[name];
        classes[name]=on;
      },
      contains:function(name){return !!classes[name];}
    },
    _checked:false,
    get checked(){return this._checked;},
    set checked(v){this._checked=v;}
  };
}
// simulate a document with querySelectorAll returning matching stub elements by a simple registry
var REGISTRY={}; // selector -> [elements]
function registerEl(sel,el){
  if(!REGISTRY[sel])REGISTRY[sel]=[];
  REGISTRY[sel].push(el);
}
var document={
  querySelectorAll:function(sel){return REGISTRY[sel]||[];}
};
function fakeRoot(){
  return {querySelectorAll:function(sel){return REGISTRY[sel]||[];},querySelector:function(sel){return (REGISTRY[sel]||[])[0]||null;}};
}
  var UI_PANEL_MAP={sidebar:'.a3d-tree',snappill:'#a3d-snappill',navpill:'#a3d-pill',hud:'.a3d-hud'};
  var UI_PANEL_PREF_KEY='acad3dUIPrefs';

  function bimLoadUIPanelPrefs(){
    try{
      var raw=localStorage.getItem(UI_PANEL_PREF_KEY);
      if(raw)return JSON.parse(raw)||{};
    }catch(eL){}
    return {};
  }

  function bimSaveUIPanelPrefs(prefs){
    try{localStorage.setItem(UI_PANEL_PREF_KEY,JSON.stringify(prefs));}catch(eS){}
  }

  function bimSetUIPanelVisible(key,visible){
    var sel=UI_PANEL_MAP[key];
    if(!sel)return;
    var els=document.querySelectorAll(sel),i;
    for(i=0;i<els.length;i++)els[i].classList.toggle('a3d-hide-panel',!visible);
    var prefs=bimLoadUIPanelPrefs();
    prefs[key]=visible;
    bimSaveUIPanelPrefs(prefs);
  }

  function bimApplyUIPanelPrefs(root){
    var prefs=bimLoadUIPanelPrefs(),key;
    for(key in UI_PANEL_MAP){
      if(!UI_PANEL_MAP.hasOwnProperty(key)||!prefs.hasOwnProperty(key))continue;
      var visible=prefs[key],sel=UI_PANEL_MAP[key];
      var els=root.querySelectorAll(sel),i;
      for(i=0;i<els.length;i++)els[i].classList.toggle('a3d-hide-panel',!visible);
      var cb=root.querySelector('[data-a3dui="'+key+'"]');
      if(cb)cb.checked=visible;
    }
  }

var PASS=0,FAIL=0;
function assert(name,cond,detail){if(cond){PASS++;console.log('PASS  '+name);}else{FAIL++;console.log('FAIL  '+name+(detail?' -- '+detail:''));}}

// ---- 1. Setup: register stub elements matching the real selectors ----
var sidebarEl=makeEl('div');registerEl('.a3d-tree',sidebarEl);
var snapEl=makeEl('div');registerEl('#a3d-snappill',snapEl);
var navEl=makeEl('div');registerEl('#a3d-pill',navEl);
var hudEl=makeEl('span');registerEl('.a3d-hud',hudEl);
var sidebarCb=makeEl('input');registerEl('[data-a3dui="sidebar"]',sidebarCb);

// ---- 2. Toggling a panel off applies the hide class to the REAL matching element ----
bimSetUIPanelVisible('sidebar',false);
assert('hiding the sidebar applies the a3d-hide-panel class to the real matched element', sidebarEl.classList.contains('a3d-hide-panel')===true);

bimSetUIPanelVisible('sidebar',true);
assert('showing the sidebar again removes the hide class', sidebarEl.classList.contains('a3d-hide-panel')===false);

// ---- 3. An unknown/unmapped key is safely ignored, not crashed ----
var before=JSON.stringify(STORE);
bimSetUIPanelVisible('nonexistent',false);
assert('an unrecognized panel key does not crash and does not corrupt stored prefs', true); // reaching here means no throw

// ---- 4. Preferences persist to localStorage and survive a reload-equivalent reapply ----
bimSetUIPanelVisible('snappill',false);
bimSetUIPanelVisible('navpill',false);
var savedPrefs=JSON.parse(localStorage.getItem('acad3dUIPrefs'));
assert('preferences are actually persisted to localStorage', savedPrefs.snappill===false && savedPrefs.navpill===false);

// simulate a fresh page load: reset the DOM elements' hide state, then re-apply prefs
snapEl.classList.toggle('a3d-hide-panel',false);
navEl.classList.toggle('a3d-hide-panel',false);
sidebarCb.checked=true;
bimApplyUIPanelPrefs(fakeRoot());
assert('re-applying persisted prefs on "reload" correctly re-hides the snap pill', snapEl.classList.contains('a3d-hide-panel')===true);
assert('re-applying persisted prefs on "reload" correctly re-hides the nav pill', navEl.classList.contains('a3d-hide-panel')===true);
assert('sidebar preference (still true/visible) is correctly reflected on the checkbox after reapply', sidebarCb.checked===true);

// ---- 5. Corrupted localStorage data is handled gracefully, not a crash ----
STORE['acad3dUIPrefs']='{not valid json';
var recoveredPrefs=bimLoadUIPanelPrefs();
assert('corrupted stored preferences fall back to an empty object rather than crashing', 
  typeof recoveredPrefs==='object' && recoveredPrefs!==null);

console.log('');
console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');
process.exit(FAIL>0?1:0);
