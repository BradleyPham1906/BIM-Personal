"""falsify_phase135.py -- break the V135 build one way at a time, keeping the marker.

Each variant takes back one thing V135 does, and the V135 suite must fail on every one of them.
Variant names are lower case: the runner reads no other (V126)."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # ---- 135a: which portal
    'no_guess': [("    if(ad.length<3)return '';\n    function has(w)", "    return '';\n    function has(w)")],
    'guess_state_first': [("    return best||stHost;", "    return stHost||best;")],
    'not_remembered': [("    try{var pr=bimLoadUIPanelPrefs()||{};pr.dataPortal=host||'';bimSaveUIPanelPrefs(pr);}catch(eS){}\n", "")],
    'remembered_over_address': [("      A3D_FIND.portal=bimFindGuess()||(bimFindPortal(pr.dataPortal)?pr.dataPortal:'');",
                                 "      A3D_FIND.portal=(bimFindPortal(pr.dataPortal)?pr.dataPortal:'')||bimFindGuess();")],
    'unknown_portal_taken': [("    if(host&&!bimFindPortal(host))return false;\n    A3D_FIND.portal=host||'';", "    A3D_FIND.portal=host||'';")],
    # ---- 135a: the Hub search
    'lucene_kept': [("    return String(q==null?'':q).replace(/[\"\\\\\\/(){}\\[\\]\\^~:!?+]|&&|\\|\\|/g,' ').replace(/\\b(?:AND|OR|NOT)\\b/gi,' ')",
                     "    return String(q==null?'':q).replace(/\\b(?:AND|OR|NOT)\\b/gi,' ')")],
    'geojson_type_dropped': [("  var BIM_FIND_TYPES=['Feature Service','Map Service','GeoJson'];", "  var BIM_FIND_TYPES=['Feature Service','Map Service'];")],
    'groups_unchecked': [("if(/^[0-9a-f]{32}$/i.test(o.groups[i]))gr.push('group:'+o.groups[i]);", "gr.push('group:'+o.groups[i]);")],
    'org_with_groups': [("      (!gr.length&&o.org&&/^[0-9A-Za-z]{16}$/.test(o.org)?", "      (o.org&&/^[0-9A-Za-z]{16}$/.test(o.org)?")],
    'org_unchecked': [("      (!gr.length&&o.org&&/^[0-9A-Za-z]{16}$/.test(o.org)?", "      (!gr.length&&o.org?")],
    'private_items': [("+' AND access:public';", "+'';")],
    'no_title_sort': [("'&sortField='+(text?'relevance':'title')", "'&sortField='+(text?'relevance':'relevance')")],
    'groups_v2_ignored': [("    if(Array.isArray(f))for(i=0;i<f.length;i++){p=f[i]&&f[i].predicates;", "    if(false)for(i=0;i<f.length;i++){p=f[i]&&f[i].predicates;")],
    'groups_any_ignored': [("      if(v&&typeof v==='object'){add(v.any);add(v.all);}", "      if(v&&typeof v==='object'){add(v.all);}")],
    'groups_v1_ignored': [("    if(!out.length&&js&&js.catalog)add(js.catalog.groups);\n", "")],
    'groups_not_cached': [("    if(A3D_FIND.groups[site])return Promise.resolve(A3D_FIND.groups[site]);\n", "")],
    'site_failure_fails': [("return g;},function(){return [];});   /* the organisation is the fallback */", "return g;});   /* the organisation is the fallback */")],
    'never_near': [("    a=A3D_FIND.near?bimCtxArea():null;", "    a=null;")],
    'always_near': [("    a=A3D_FIND.near?bimCtxArea():null;", "    a=bimCtxArea();")],
    'bad_items_kept': [("    if(!it||!/^[0-9a-f]{32}$/i.test(String(it.id||'')))return null;", "    if(!it)return null;")],
    'more_restarts': [("    start=more?A3D_FIND.next:1;", "    start=1;")],
    'more_replaces': [("      A3D_FIND.res=A3D_FIND.res.concat(r.items);", "      A3D_FIND.res=r.items;")],
    'busy_not_refused': [("    if(A3D_FIND.busy){a3dToast('A search is already on its way');return null;}\n", "")],
    'no_portal_searched': [("    if(!P){a3dToast('Pick a portal to search: a city, county, state or federal agency');return null;}",
                            "    if(!P)P={name:'all',host:'',site:'',org:'',socrata:false};")],
    'failure_unnamed': [("      A3D_FIND.err=e&&e.said?host+' said: '+e.said:bimCtxErr(host,e);A3D_FIND.said='';", "      A3D_FIND.err='The search failed';A3D_FIND.said='';")],
    'error_envelope_ignored': [("        if(js.error)throw {said:String(js.error.message||'an error').slice(0,160)};\n        if(!Array.isArray(js.results))throw {bad:true};\n        for(i=0;i<js.results.length;i++){it=bimHubItem",
                                "        if(!Array.isArray(js.results))throw {bad:true};\n        for(i=0;i<js.results.length;i++){it=bimHubItem")],
    # ---- 135a: Socrata
    'socrata_not_scoped': [("    return 'https://api.us.socrata.com/api/catalog/v1?search_context='+encodeURIComponent(dom)+'&domains='",
                            "    return 'https://api.us.socrata.com/api/catalog/v1?search_context=&domains='")],
    'socrata_other_domains': [("    if(!en.metadata||en.metadata.domain!==dom)return null;\n", "")],
    'socrata_tables_kept': [("    if(i>=ty.length)return null;\n", "")],
    'socrata_geom_unchecked': [("    if(!/^[A-Za-z_][A-Za-z0-9_]*$/.test(geom))geom='';\n", "")],
    'socrata_one_batch': [("          if(got.length<BIM_FIND_NUM&&b<5)return batch();", "          if(false)return batch();")],
    'socrata_whole_dataset': [("        '$limit='+BIM_DATA_MAX;\n    }\n    return L.url;", "        '$limit=50000';\n    }\n    return L.url;")],
    'socrata_box_order': [("'within_box('+L.geom+','+a.n.toFixed(7)+','+a.w.toFixed(7)+','+a.s.toFixed(7)+','+a.e.toFixed(7)+')'",
                           "'within_box('+L.geom+','+a.s.toFixed(7)+','+a.w.toFixed(7)+','+a.n.toFixed(7)+','+a.e.toFixed(7)+')'")],
    'socrata_not_a_kind': [("    if(/^https?:\\/\\/[^\\/]+\\/resource\\/[a-z0-9]{4}-[a-z0-9]{4}\\.geojson(\\?.*)?$/i.test(u))return {kind:'socrata'};   /* __acad3dV135 */\n", "")],
    'socrata_geom_not_kept': [("    if(extra&&/^[A-Za-z_][A-Za-z0-9_]*$/.test(extra.geom||''))lyr.geom=extra.geom;", "")],
    # ---- 135a: adding
    'service_first_layer_only': [("      if(ls.length===1)return bimDataAdd(u+'/'+ls[0].id,it.title,null,cr);", "      if(ls.length>=1)return bimDataAdd(u+'/'+ls[0].id,it.title,null,cr);")],
    'group_layers_offered': [("&&!l.subLayerIds&&(!l.type||/feature layer/i.test(l.type)))", "&&(!l.type||/layer/i.test(l.type)))")],
    'geojson_item_as_service': [("    if(it.type==='GeoJson')return Promise.resolve(bimDataAdd(bimFindItemData(it.id),it.title,null,cr));\n", "")],
    'no_portal_credit': [("    if(it.src==='socrata')return Promise.resolve(bimDataAdd(it.data,it.title,null,cr,{geom:it.geom}));\n    if(it.type==='GeoJson')return Promise.resolve(bimDataAdd(bimFindItemData(it.id),it.title,null,cr));",
                          "    if(it.src==='socrata')return Promise.resolve(bimDataAdd(it.data,it.title,null,null,{geom:it.geom}));\n    if(it.type==='GeoJson')return Promise.resolve(bimDataAdd(bimFindItemData(it.id),it.title,null,null));")],
    'no_address_asked': [("    if(!/^https:\\/\\/\\S+\\/(FeatureServer|MapServer)$/i.test(u)){a3dToast(it.title+' has no ArcGIS layer address to read');return Promise.resolve(null);}\n", "")],
    'layer_failure_unnamed': [("      var msg=e&&e.said?host+' said: '+e.said:bimCtxErr(host,e);\n      a3dToast(it.title+': '+msg);", "      var msg='failed';\n      a3dToast(msg);")],
    # ---- 135b
    'no_find_panel': [("    r+=bimFindHtml();   /* __acad3dV135 */\n", "")],
    'no_credit': [("    r+=bimPropText('Portals',BIM_FIND_CREDIT);\n", "")],
    'added_not_said': [("        (ad?'<span class=\"a3d-fdk\">added</span>':'<button", "        (false?'<span class=\"a3d-fdk\">added</span>':'<button")],
    'no_more_button': [("    if(A3D_FIND.next&&!A3D_FIND.busy)r+=bimPropRow('','<button type=\"button\" class=\"a3d-pedit\" data-propfindact=\"more\">More results</button>');\n", "")],
    'search_not_disabled': [("data-propfindact=\"search\"'+(A3D_FIND.busy?' disabled':'')+'>Search", "data-propfindact=\"search\">Search")],
    'portal_select_ignored': [("    if(k==='portal'){bimFindSetPortal(f.value);refreshProps();return true;}", "    if(k==='portal'){return true;}")],
    'pick_not_wired': [("      if(ly)bimFindAdd(ix,ly);", "      if(false)bimFindAdd(ix,ly);")],
    'search_on_typing': [("    if(k==='q'){A3D_FIND.q=String(f.value||'').slice(0,120);return true;}", "    if(k==='q'){bimFindSearch(f.value);return true;}")],
    'no_command': [("    finddata:function(){bimFindCommand();},                      /* __acad3dV135 */\n", "")],
    'unsafe_link': [("target=\"_blank\" rel=\"noopener noreferrer\" title=", "target=\"_blank\" title=")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV135' in txt
out.write_text(txt, encoding='utf-8')
