# V175 Presentation P2: live elements (research, 2026-11-08)

Under `docs/research/research-protocol.md` ("Research as a scientist does it"). Levels: **P** read in the primary
source, **S** a dependable secondary source with the gap said, **U** a search summary or an unchecked single copy, kept
out of the code. Written from the working notes in `docs/research/research-presentation-live/`.

(Draft: parts 1 and 2 written before the searches; the rest follows from the working notes.)

## 2. The question and the hypotheses

**The question.** How should a board's objects stay connected to the model and its analyses, so that a plan, a
schedule, a chart, a number or a line of text on a board is always what the model says, and how should an edit made
on the board itself be kept, marked and undone, in an ES5, zero-dependency app with one layer system?

A good answer must decide: what kinds of object can be live; when each is brought up to date (always, on a change, on
demand); how an out-of-date or missing source is shown; what an override is (the whole object, or one property) and
how Reset works; the syntax of a field in text; how numbers are formatted; and what is saved.

**The hypotheses**, each one evidence could prove wrong:

- **H1.** The professional tools named by the owner (Archicad, LayOut) bring a linked drawing up to date
  automatically, by default, without a command.
- **H2.** Archicad's and LayOut's text fields (autotext, auto-text) update by themselves whenever their source
  changes; neither can be edited in place without breaking the link.
- **H3.** LayOut's override is per property (camera, style, scale), not the whole viewport, and Reset brings back
  only the overridden properties.
- **H4.** Every surveyed tool marks a stale linked item visibly on the page or in a list.
- **H5.** Figma and Penpot keep overrides per property (Penpot: per attribute group), and their Reset is per
  property and for all.
- **H6.** The app's revision counter (`A3D_REV`, moved by `saveSoon`) catches every change a live object depends on.
- **H7.** Drawing every live object from its source on every board draw costs under 16 ms for a board of 80 objects
  of which 20 are live, so no cache beyond the existing ones is needed.
- **H8.** Analyses (sun hours, solar, cut and fill) are too slow to rerun on every model change, so a live object bound
  to one must show its kept value and say when it is out of date (Archicad's Manual update).
- **H9.** A field syntax exists in a surveyed tool that is typed easily on a phone, needs no escaping in ordinary
  prose, and is never evaluated as code.
- **H10.** Storing the binding and the overrides, never the resolved value, keeps undo's 50 snapshots small: under
  2 KB more for a board of 20 live objects.
