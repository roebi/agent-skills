---
name: create-openscad-from-construction-image-en
description: >
  Interprets a hand-drawn or photographed construction sketch (image) and
  generates a valid OpenSCAD (.scad) file from it. Use this skill whenever
  a user uploads or references a technical drawing, construction sketch, or
  dimension annotation image and wants a 3D-printable or CAD model as output.
  Activate for phrases like: "create OpenSCAD from this sketch",
  "generate .scad from image", "convert drawing to OpenSCAD",
  "make a CAD file from this photo", "3D model from this construction drawing".
  Supports dimension labels in English and German (e.g. Länge, Durchmesser,
  Innensechskant, Aussendurchmesser).
license: CC BY-NC-SA 4.0
compatibility: Requires an AI agent with vision (image input) capability. OpenSCAD optional for local preview.
metadata:
  author: roebi
  spec: https://agentskills.io/specification
  based-on-skill: create-agent-skill-en
  based-on-skill-repo: https://github.com/roebi/agent-skills
  based-on-skill-license: CC BY-NC-SA 4.0
---

# Create OpenSCAD from Construction Image

Converts a hand-drawn or photographed technical/construction sketch into a
parametric OpenSCAD (`.scad`) file, ready for 3D printing or further CAD work.

## When to use this skill

Activate when:
- The user uploads a photo or scan of a hand-drawn technical sketch.
- The user references a construction drawing with labeled dimensions.
- The user asks to convert a drawing, sketch, or annotation image into a 3D model.
- Dimension labels may be in English or German.

Typical trigger phrases:
- "Create OpenSCAD from this sketch / image / drawing / photo"
- "Generate .scad from this construction image"
- "Convert this drawing to OpenSCAD"
- "Make a CAD file / 3D model from this"
- "3D-printable file from this hand drawing"

## Skills used (backreferences)

| Skill | Repository | License |
|-------|-----------|---------|
| `create-agent-skill-en` | https://github.com/roebi/agent-skills | CC BY-NC-SA 4.0 |

This skill was scaffolded following the `create-agent-skill-en` workflow and
specification from [agentskills.io](https://agentskills.io/specification).

---

## Step-by-step workflow

### 1. Receive and inspect the image

- Accept the uploaded image (photo, scan, or screenshot of a technical sketch).
- Identify all labeled dimensions, annotations, and geometric shapes visible.
- Note the language of labels (English or German — see translation table below).

### 2. Extract dimensions and geometry

Read all visible dimension annotations. Common German labels and their meanings:

| German label         | English meaning         | OpenSCAD parameter example        |
|----------------------|-------------------------|------------------------------------|
| Länge                | Length                  | `length = ...;`                   |
| Breite               | Width                   | `width = ...;`                    |
| Höhe                 | Height                  | `height = ...;`                   |
| Durchmesser / Ø      | Diameter                | `diameter = ...;`                 |
| Radius               | Radius                  | `radius = ...;`                   |
| Aussendurchmesser    | Outer diameter          | `outer_diameter = ...;`           |
| Innendurchmesser     | Inner diameter          | `inner_diameter = ...;`           |
| Innensechskant       | Inner hex (across flats)| `inner_hex_width = ...;`          |
| Wandstärke           | Wall thickness          | `wall_thickness = ...;`           |
| Tiefe                | Depth                   | `depth = ...;`                    |
| Bohrung              | Bore / hole             | `bore_diameter = ...;`            |
| Schlüsselweite (SW)  | Wrench size (hex flats) | `hex_across_flats = ...;`         |

Parse units (mm, cm, m) and convert all values to **millimeters** in the output.

### 3. Identify the primary shape

Determine the dominant geometry:

| Shape in sketch              | OpenSCAD primitive / pattern                        |
|------------------------------|-----------------------------------------------------|
| Cylinder / round part        | `cylinder(h, d, $fn=64)`                           |
| Box / rectangular block      | `cube([x, y, z])`                                  |
| Hex prism                    | `cylinder(h, d=$fn=6)` with adjusted diameter      |
| Tube / hollow cylinder       | `difference() { cylinder(...outer...); cylinder(...inner...) }` |
| Hex socket / Innensechskant  | `difference() { cylinder(outer); cylinder(hex, $fn=6) }` |
| Cone / taper                 | `cylinder(h, r1, r2)`                              |
| Sphere                       | `sphere(r)`                                        |

For complex multi-feature parts, combine primitives using `difference()`,
`union()`, or `intersection()`.

### 4. Handle hex-across-flats conversion

When a hex is specified as **across flats** (Schlüsselweite / Innensechskant),
OpenSCAD's `cylinder($fn=6)` uses the **circumradius** (across corners).
Convert using:

```
d_circumradius = across_flats / cos(30)
```

In OpenSCAD:
```openscad
// inner_hex_width = across-flats dimension
cylinder(h = length, d = inner_hex_width / cos(30), $fn = 6);
```

### 5. Write the OpenSCAD file

Structure the output file as follows:

```openscad
// <Part name or description>
// Source: hand-drawn construction sketch
// Generated by: create-openscad-from-construction-image-en skill

// --- Parameters (all units: mm) ---
<parameter declarations with comments>

// --- Geometry ---
<OpenSCAD CSG model>
```

Rules:
- Declare **all** dimensions as named parameters at the top (easy editing).
- Add a comment on each parameter with its meaning and source label.
- Use `$fn = 64` for smooth cylinders; `$fn = 6` for hex prisms.
- Keep geometry readable — one operation per line, proper indentation.
- Add `center = false` or `center = true` explicitly to avoid ambiguity.

### 6. Output

- Provide the `.scad` file as a downloadable file named after the part.
- If the part name is unknown, use `part.scad` or derive from the dominant feature.
- Briefly summarize the interpreted dimensions in a table for user verification.

---

## Example: Hex Socket (from real sketch)

**Sketch labels read:**
- Innensechskant: 8mm
- Aussendurchmesser: 14mm Ø
- Länge: 25mm

**Generated OpenSCAD:**

```openscad
// Hex Socket / Innensechskant
// Innensechskant (inner hex across flats): 8mm
// Aussendurchmesser (outer diameter): 14mm
// Länge (length): 25mm

outer_diameter = 14;   // mm — Aussendurchmesser
inner_hex_width = 8;   // mm — Innensechskant (across flats / Schlüsselweite)
length = 25;           // mm — Länge

difference() {
    // Outer cylinder
    cylinder(h = length, d = outer_diameter, center = false, $fn = 64);

    // Inner hexagon bore
    // d = across_flats / cos(30) converts SW to circumradius
    cylinder(h = length + 1, d = inner_hex_width / cos(30), center = false, $fn = 6);
}
```

---

## Ambiguity handling

If the sketch is unclear or dimensions are missing:

1. State which dimensions were successfully read.
2. List what is missing or ambiguous.
3. Use a placeholder variable with a comment: `// TODO: verify this dimension`.
4. Ask the user to confirm before finalizing.

---

## References

- `references/openscad-primitives.md` — Quick reference for OpenSCAD primitives and CSG operations
- `references/german-dimension-labels.md` — Extended German ↔ English dimension label glossary
- scripts-guide: https://raw.githubusercontent.com/roebi/agent-skills/refs/heads/main/skills/create-agent-skill-en/references/scripts-guide.md
