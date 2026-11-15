# V228 spec: Generated elements: a stable key, re-run in place, hand overrides

Notion: Algorithmic Design (research; proposed V228 to V232). Research: `docs/research/research-algorithmic-design.md` and the notes in `docs/research/research-algorithmic-design/`. The owner's decisions, 2026-11-15: all thirteen as the research recommends (the owner: "Just do whats recommended"; overrule any here). Implementation target: local `main`. Written by Claude, 2026-11-15.

## 1. The decisions this spec follows

- An element a generator makes is keyed by how it was made (the generator and the path of rules and indexes), is updated in place when the generator runs again, and keeps its id (decisions 2 and 11; research 4.2).
- Indexes are semantic (storey 3, bay 2), never a position in a list (decision 3; Lipp et al. 2019, e03).
- A hand edit is stored beside the generator as (key, property, value) and re-applied on each run. One whose place is gone for now is kept dormant and returns when the place returns; one whose rule is gone is listed for the owner. Nothing is moved to the nearest position (decision 3; Lipp, Wonka, Wimmer 2008).
- Generated elements are real elements from the start: no preview, no bake (decision 11).

## 2. What it does for the user

Run a generator twice and the same walls and windows are still the same elements, with their ids, history and anything set on them by hand; change a count and the edits that no longer have a place are shown, not lost and not moved.

## 3. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/bim/generated-elements.js` | new, after `js/engine/bim/parametric.js` in `src/index.html` (header done) | 5 pure functions (part 5) | Cline, WO-01 to WO-05 |
| `docs/work-orders/v228/v228.test.mjs` | new | their tests | Claude (done) |
| the app's own files | changed | wiring, the interface, saving and undo | Claude, WO-06, WO-07 |

## 4. Data

A key: `gen|Rule:index/Rule:index/...`. An item of a run: {key, kind, props, ...}. An existing element: {id, key} (read by Claude's wiring from the element's `bim.gen`). An override: {key, prop, value}.

## 5. Functions, `src/js/engine/bim/generated-elements.js`

ES5. Every function is pure: it never changes what it is given and uses no name from another file.

- **WO-01 `bimGelKey(gen, path)`**: gen a non-empty string without `|`, `/` or `:` (else {error: 'bad generator id'}); path a non-empty array (else {error: 'empty path'}) of [rule, index]: rule a non-empty string without those characters (else {error: 'bad rule name at I'}, I the position); index a whole number of 0 or more, or a non-empty string without those characters (else {error: 'bad index at I'}). {key: gen + '|' + the parts 'rule:index' joined by '/'}. The first fault met, in path order, is the one returned.
- **WO-02 `bimGelShape(key)`**: the key as a string with every index made only of digits replaced by `*`: 'g1|Facade:front/Floor:3/Bay:2' gives 'g1|Facade:front/Floor:*/Bay:*'. A key without `|` is returned unchanged (as a string). A part without `:` is left as it is.
- **WO-03 `bimGelReconcile(existing, derived)`**: existing [{id, key}] (the elements a generator made before), derived [{key, ...}] (this run's items). Two derived items with one key: {error: 'duplicate key K'}. Else {update: [{id, item}] in derived order for items whose key an existing element carries (the first existing element with that key), create: [the other derived items, in order], remove: [ids]}: first the later existing elements that repeat a key already seen, in existing order, then the existing elements whose key no derived item has, in existing order. Neither argument is changed.
- **WO-04 `bimGelOverrides(overrides, keys)`**: overrides [{key, prop, value}], keys [the keys of this run]. Each override, in order, goes to one list: apply when its key is in keys; dormant when it is not but bimGelShape of its key equals bimGelShape of some key in keys (its place is gone for now, as when 10 bays become 8); listed otherwise (its rule is gone). {apply, dormant, listed}, holding the same override objects.
- **WO-05 `bimGelApply(item, overrides)`**: a copy of item (its own keys copied; props a new object with item.props's own keys, {} when it has none) with, for each override in order whose key is item.key, props[prop] = value; and ov, the names of the properties so set, each once, in the order first met.

## 6. Order of the work

WO-01 to WO-05 in order (a later one may use an earlier one, as its task says). Then Claude: **WO-06** the generator record in `A3D.site.generators` ({id, kind, params, rules, overrides}), the `bim.gen` field {g, k} on elements, a batch maker (one undo step, one repaint, one save: the audit's hazards list), re-run by reconciliation, the dormant and listed overrides in the generator's Properties form with its rules as text beside it (decision 13); the opening cutter's cost measured in the browser check (research part 9); **WO-07** the records.

## 7. Not in this phase

The grammar that produces the items (V229); the model-wide graph (V230); exploration (V231); the node canvas (V232); detaching an element from its generator beyond a plain "detach" command.
