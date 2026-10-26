# The specification tree

## Reading it

- `Product` nodes (blue-ish icon with two shapes) are assemblies. `Part` nodes contain
  `xy/yz/zx plane`, `PartBody`, extra `Body`, `Geometrical Set`, `Parameters`, `Relations`.
- Instance name shows as `PartNumber (InstanceName)`. The part number is the reference; the
  instance name is this placement. Two instances of the same bolt share one part number.
- Underlined node = active object. Double-click to activate, double-click the parent to leave.
- Red lightning on a node: needs update. Dimmed: hidden. Little chain or green brackets:
  linked or contextual. Red crossed: broken link or deactivated.
- A node with a small arrow-in-a-box icon: Visualization Mode (lightweight, not editable).

## Finding one thing in ten thousand nodes

**Edit > Search (Ctrl+F)** is the tool. Do not expand the tree by hand.

- Name field accepts wildcards: `*bracket*`. Case-insensitive by default.
- Type dropdown: Part, Product, Body, Sketch, Pad, Hole, Constraint, and so on.
- Scope: "In" the current product versus the whole document, "Look in" visible, hidden, or all.
- Click **Search** to populate the list, then **Select** to select results in the tree,
  or **Search and Select** to do both. Combine with Reframe On and Hide/Show.
- The **Favorites** tab remembers queries. The query string syntax (for example
  `Name=*bolt*,all` or `Type=Part,all`) is the same string the automation `Selection.Search`
  method takes, so a query you build here can go straight into a macro.

## Expand and collapse without crashing CATIA

- Expand one level: click the `+`. Expand all under a node: select it, View > Tree Expansion >
  Expand All Levels. On a large assembly this is slow and sometimes fatal. Prefer Search.
- Collapse everything: View > Tree Expansion > Collapse All.
- Tools > Options > General > Display > Tree Appearance controls font size and whether
  features are shown. Tree Manipulation controls expansion behavior and the scrollbar.

## Tree and viewer focus

- F3 hides or shows the tree. Shift+F3 switches mouse zoom/pan between tree and 3D.
- Clicking the tree's trunk line also switches focus. If the model stopped rotating,
  you are probably in tree mode.

## Properties

Right-click > Properties (Alt+Enter). Product tab holds part number, instance name,
revision, nomenclature, description, source (Made or Bought). Graphic tab holds color
and transparency. Mechanical tab (parts) holds material and mass once computed.

## Reorder and rename

Right-click a product > Edit > Reorder (or Reorder Children) to sort. Rename through
Properties. Check `company/conventions.md` before renaming anything: in managed environments
part numbers come from the PLM system, not from you.
