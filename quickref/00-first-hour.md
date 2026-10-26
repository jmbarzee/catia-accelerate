# First hour in CATIA V5

## What you are looking at

- **Spec tree** (left): the structure of the document. Products contain parts. Parts contain
  bodies. Bodies contain features. Everything you do appears here.
- **3D viewer** (center): the geometry. Clicking geometry highlights its tree node and vice versa.
- **Compass** (top right): drag it onto a part to move that part. Drag it back to the axis
  icon at bottom right to reset.
- **Workbench icon** (top right, below the compass): tells you which toolset is loaded.
  Click it to switch. The toolbars change per workbench. This is the number one source of
  "where did the button go" confusion.
- **Toolbars** (right and bottom): dockable. If one vanishes, View > Toolbars.
- **Status bar** (bottom): CATIA tells you what it wants you to click next. Read it.

## Three document types

| Extension | What it is | Workbench you usually want |
|---|---|---|
| `.CATProduct` | An assembly. References parts and sub-products, holds constraints. | Assembly Design |
| `.CATPart` | A single part with its feature history. | Part Design, Generative Shape Design |
| `.CATDrawing` | 2D drawing generated from a part or product. | Drafting |

## The five actions you will do constantly

1. **Fit everything in view:** the Fit All In icon (bottom toolbar) or View > Fit All In.
2. **Find a part by name:** Edit > Search (Ctrl+F), see [02-spec-tree](02-spec-tree.md).
3. **Hide what is in the way:** select it, then Hide/Show icon or right-click > Hide/Show.
   Swap Visible Space (icon next to it) shows everything hidden.
4. **Undo:** Ctrl+Z. CATIA undo stacks are deep but reset on save in some releases.
5. **Cancel the current command:** Esc. If the status bar still asks for input, Esc again.

## Things that bite new users

- **Double-clicking in the tree enters edit mode** on that object. In an assembly, double-click
  a part and you are now editing that part, not the assembly. Double-click the top product
  to come back. The active object is underlined and highlighted in blue.
- **The compass can move parts** if you drag it onto one. If something shifted, Ctrl+Z.
- **Update** (Ctrl+U, or the lightning-bolt icon): geometry shows red when it needs updating
  after a change. Nothing is wrong until you update and it stays red.
- **Save** vs **Save Management**: in an assembly, File > Save Management shows every modified
  document. Plain Save on a product may not save modified parts the way you expect.
  Check with `company/plm-workflow.md` before saving anything in a managed environment.
- **Visualization Mode** is why some parts cannot be edited. See
  [03-large-assemblies](03-large-assemblies.md).

## Next

[01-navigation](01-navigation.md), then [03-large-assemblies](03-large-assemblies.md).
