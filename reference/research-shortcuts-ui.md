# Research: a shortcuts panel you can find your way around, and a dock that says what it is (V129)

The owner, looking at the V128 shortcut sheet and the tool dock: "lets clean up these shortcuts
stuff on the UI/UX becauase it kinda hard to navigate and things not very clear. can you research
how a good design for that would look like for easy to nav and use?" A mockup was shown on a
design canvas, and the owner answered: "oh i like that thats actually what i want."

The points below come from search summaries of the pages listed under Sources; the vendors' help
pages could not all be opened from the build environment.

## What was wrong

**The shortcut sheet** was a narrow popover beside the rail:
- All eight groups were in one column, so finding Snaps meant scrolling past Views and Drawing.
- The keys sat right after each label, at a different place on every row, instead of in a column
  to scan down.
- The grammar of a typed point (x,y, @x,y, d<a) was listed as if it were three shortcuts, inside
  Drawing.

**The dock** showed icons only:
- A tool's name appeared only in a native `title`, after a long browser delay and never on
  keyboard focus.
- The groups had no names.
- Each group's overflow was a bare triangle.
- Search was a magnifier with no label.

## What the mature tools do

1. **Figma** (Keyboard shortcuts panel):
   - It opens as a large panel over the canvas, with tabs by area across its top.
   - Keys are shown as key caps in a right-hand column.
   - `Ctrl+Shift+?` opens it.
2. **Google Docs** (`Ctrl+/`):
   - A centred dialog with a search box at the top and categories down the left.
   - The label is on the left, the keys on the right.
3. **Linear** (`?`):
   - A searchable help panel of every shortcut, grouped.
   - The key opens it from anywhere that is not a text field.
4. **Fusion and Revit:**
   - Every group on the toolbar is named under its tools: Create, Modify, Build, Annotate.
   - A group's overflow is a labelled drop-down.
   - The tooltip gives the tool's name, what it does and its shortcut, and a longer pause shows
     more.
5. **Tooltips** (Setproduct, LogRocket, the mgifford accessibility notes, MDN's `tooltip` role):
   - Show after a short delay on hover (300 to 500 ms), so a pointer passing over does not flash
     them.
   - Show at once on keyboard focus.
   - Hide on Escape, on leaving and on a press.
   - Never cover the thing described.
   - The element is `role=tooltip`, referenced by the control's `aria-describedby`. The control
     keeps its own accessible name.
   - A native `title` shown as well gives a second, plainer tooltip, so it goes.

## What V129 takes

- **The panel** opens centred over the drawing on `?` or SHORTCUTS.
  - A search at the top, categories with counts on the left, and one list.
  - Each row has the label on the left, the command to type next to it, and the keys in a
    right-aligned column.
  - Choosing a category shows only it and starts at the top. The search stays inside the chosen
    category.
- **Typing points** becomes its own page, after Drawing, with a note saying when it applies.
- **The dock:**
  - a name under every tool, and a name under every group;
  - "More" in place of the bare triangle;
  - search as a labelled pill showing its keys;
  - tooltips per the rules above;
  - an Appearance choice between tool names and icons only, remembered per browser.

  With names on, the dock was kept compact so the drawing loses as little room as possible: 143 px
  tall against 119 px before.

## Not taken, yet

- Rebinding keys from the panel (Revit, VS Code).
- Fusion's longer, illustrated second-stage tooltip.
- Pinning a group open on the dock.

## Sources

- [Figma: use Figma products with a keyboard](https://help.figma.com/hc/en-us/articles/360040328653-Use-Figma-products-with-a-keyboard)
- [Figma: the actions menu](https://help.figma.com/hc/en-us/articles/23570416033943-Use-the-actions-menu-in-Figma-Design)
- [Google Docs: keyboard shortcuts](https://support.google.com/docs/answer/179738)
- [Linear: keyboard shortcuts help](https://linear.app/changelog/2021-03-25-keyboard-shortcuts-help)
- [Fusion: the user interface](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/UserInterface_UM.htm)
- [Fusion: the S key](https://www.autodesk.com/products/fusion-360/blog/quick-tip-the-s-key/)
- [Revit: the ribbon](https://help.autodesk.com/cloudhelp/2016/ENU/Revit-GetStarted/files/GUID-3D5D02DD-0984-492E-9B65-9BA49876F14D.htm)
- [Setproduct: tooltip UI design](https://www.setproduct.com/blog/tooltip-ui-design)
- [LogRocket: designing better tooltips](https://blog.logrocket.com/ux-design/designing-better-tooltips-improved-ux/)
- [mgifford: tooltip accessibility best practices](https://github.com/mgifford/ACCESSIBILITY.md/blob/main/examples/TOOLTIP_ACCESSIBILITY_BEST_PRACTICES.md)
- [MDN: tooltip role](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Roles/tooltip_role)
