# Part basics (Part Design and Sketcher)

Start > Mechanical Design > Part Design. New part: File > New > Part.

## The loop

1. Select a plane (`xy`, `yz`, `zx` in the tree, or any planar face) and click **Sketch**.
2. In the Sketcher, draw with Profile, Rectangle, Circle, Line. Press Esc to end a tool.
3. **Constrain** the sketch: Constraint icon for dimensions, double-click a value to edit.
   Green sketch = fully constrained. White = under-constrained. Purple = over-constrained.
4. **Exit Workbench** (icon top right, the one with the door).
5. Apply a feature: **Pad** (extrude), **Pocket** (cut), **Shaft** (revolve),
   **Groove** (revolve cut), **Hole**, **Rib**, **Slot**.
6. Dress up: **Fillet**, **Chamfer**, **Draft**, **Shell**, **Thickness**.
7. Transform: **Mirror**, **Pattern** (rectangular, circular, user), **Translate**, **Scale**.

Double-click any feature in the tree to edit its parameters. Double-click a sketch to
re-enter the Sketcher.

## Bodies and booleans

- `PartBody` is the main body. Insert > Body adds more. Right-click a body > Define In
  Work Object to make features go into it.
- Insert > Boolean Operations: Add, Remove, Intersect, Union Trim. The classic pattern is
  "build the tool in a separate body, Remove it from PartBody".

## Parameters and formulas

- Tools > **Formula** (the `f(x)` icon). Create user parameters: Length, Angle, Real, String,
  Boolean. Reference them in any dimension by right-clicking the value field > Edit Formula.
- Tools > Options > Infrastructure > Part Infrastructure > Display > check **Parameters** and
  **Relations** so they show in the tree.
- A **Design Table** (also in the Formula dialog) drives parameters from an Excel sheet.
- The automation API reaches these through `Part.Parameters` and `Part.Relations`.
  See [docs-index/automation-object-model.md](../docs-index/automation-object-model.md).

## Publications

Tools > **Publication**. Publishing a face, plane, or axis gives it a stable name that other
parts and assemblies can reference. Companies that do skeleton-based design require them.
Check `company/conventions.md`.

## Surfaces

Generative Shape Design (Start > Shape) is a separate workbench for surfaces and wireframe.
Its results live in Geometrical Sets, not bodies. Close Surface or Thick Surface in Part
Design turns a surface into a solid.

## Material and mass

Apply Material icon (bottom toolbar) opens the material library. Then Measure Inertia
reports mass. Properties > Mechanical shows the material.

## Common errors

- **"Update error" with a red feature**: the sketch lost a reference, or a fillet radius is
  too large for the geometry. Double-click the red feature; CATIA highlights what failed.
- **Sketch turns purple**: over-constrained. Delete the last constraint you added.
- **Pad has nothing to pad**: the sketch profile is open or self-intersecting.
  Sketcher > Tools > Sketch Analysis shows the gap.
