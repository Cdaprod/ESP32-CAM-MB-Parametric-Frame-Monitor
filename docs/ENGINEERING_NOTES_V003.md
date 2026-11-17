# ESP32-CAM-MB | PARAMETRIC FRAME MONITOR — 4040 FULL ASSEMBLY V003

**V003 is a new version, not a replacement of V002.** The **exact original V002 ZIP** is preserved byte-for-byte in `reference/V002_original_preserved.zip` (SHA-256 recorded in `docs/provenance.json`). The entire recovered 4040 rail, V5 undercut key, 60 mm arm, base plate, yaw/pitch screw hardware and V002 kinematics are unchanged. This revision **replaces only the open-topped camera cradle and adds a removable positive-retention bridge and its four metal fastener components.**

> **Prototype / fit test only.** The ESP32-CAM-MB assembled board envelope is a provisional 27 x 40 mm board with provisional 16 mm stacked depth. The original 4040 source is photo-derived and has not been dimensionally confirmed against the actual printer. Heat-set-insert size is an illustrative nominal, not a specified commercial component. Geometric capture does not equal structural/vibration qualification. Use metal T-nuts rather than the demonstrator's tapped-plastic M5 rail key when mounting to operating machinery.

## 1. Finished 4040 frame assembly — 23 components

![23-positioned-component assembled CAD geometry with the V003 bolted top retainer](previews/assembled_oblique.png)

- 4040 reference extrusion: 40 x 40 x 180 mm, two face slots centered at ±10 mm (recovered, photo-derived geometry).
- Original V5 undercut sliding key (parametric), original M5 screw pair and single-slot mount plate.
- Original corrected V002 60 mm swivel/tilt arm, M4 yaw/pitch bolts, washers and locknuts.
- New V003 cradle with upper insert towers, stronger forward lips and a **two-screw removable U-shaped upper retaining bridge**.
- Model of nominal camera/MB stack with lens, plus two brass insert envelopes and two M2.5 bolts.

The assembled STEP is pre-positioned and retains **23 independently named BREP solids**. Printable CAD parts are delivered as individual STEP and **watertight STL** files. A portable GLB and an offline HTML viewer are also supplied.

## 2. How the anti-inversion cradle works

![V003 cradle attached to camera arm with the positive-retention top bridge](previews/captured_camera_closeup.png)

![Side-by-side geometry-derived V002 open cradle and V003 retained cradle](previews/v002_vs_v003_comparison.png)

V002's cradle held the nominal camera laterally and front-to-back, but the open upper end allowed upward extraction. For an upside-down printer/camera orientation, gravity could therefore drive the board out along **local +Z**. V003 preserves the existing bottom stops and rear wall and introduces these changes:

1. **Printed continuous U-shaped retainer** sits above the board. The underside is at local `Z = 49.25 mm` and the nominal PCB ends at `Z = 48.00 mm`, yielding **1.25 mm top gap**.
2. **Two new integrated towers** on the outer side walls extend from `Z = 38.20` to `49.25 mm`. Their lateral outer boundary reaches `X = ±22.55 mm` in the cradle-local coordinate frame. They are part of the cradle body (not loose parts).
3. **M2.5×8 screws** secure the retainer in threaded inserts. The two socket heads are accessible from above; this is intentionally *not* a snap-fit dependent on printed plastic flexure.
4. **Front guide lips are widened from 1.1 mm to 2.2 mm**. They constrain forward removal without blocking the central lens in the nominal assembly.
5. The middle front of the upper bridge is open, minimizing obstruction near the board antenna; the bridge is connected by a **rear strip** and retains both outer upper corners.

![Camera front lens and antenna clearance with top retainer installed](previews/camera_front_and_retainer.png)

### Assembly sequence

![Exploded print of top retaining bar, threaded inserts and M2.5 cap screws](previews/exploded_retainer.png)

1. Print the V003 cradle and the V003 top bridge. Orient the bridge's **large underside surface against the build plate**. Print the cradle on its broad back or other supported face according to slicer analysis; inspect the pitch ear overhang and insert towers before slicing.
2. Test the printed fit against the **actual** ESP32-CAM and MB/USB programmer stack before heating inserts. Check cable exit, antenna clearance, lens clearance, PCB component protrusions, and the upper-board height.
3. Select actual **M2.5 heat-set inserts**, measure their OD/depth, and adjust `CaptureSpec` if they differ from the illustrative **OD3.7 × L4.0 mm** geometry. Install into both tower seats. The modeled pilot is **Ø3.45 mm** versus nominal **Ø3.70 mm** insert OD, intentionally representing a **0.25 mm diametral heat-set interference**. The cavity does not reproduce manufacturer-specific knurl geometry; confirm the real insert and vendor-recommended bore before print.
4. Slide the camera stack into the cradle from the open top, with optics toward front, until it rests at the bottom stops. The camera board should not be squeezed by the side walls.
5. Place the U-bridge over the upper corners, align both Ø2.9 mm clearance bores, install two **M2.5×8 screws**, and tighten by the insert maker's guidance. Do not overtighten and fracture the printed towers.
6. Apply gentle manual inversion *off the printer* and verify no board movement or flex. Add independent cable strain relief/tether before moving the printer.

### Inverted visual demonstration

![Camera cradle rotated upside down with the nominal board blocked by its retaining bridge](previews/upside_down_retention.png)

The inset board is intentionally a *model envelope*: do not confuse this image with a physical drop or torque test.

## 3. Parametric register (millimeters)

| Feature | V002 | V003 | Notes |
|---|---:|---:|---|
| PCB width × length | 27 × 40 | 27 × 40 | Provisional nominal board, unchanged |
| Stack depth | 16 | 16 | Provisional nominal MB assembled depth, unchanged |
| Top retention | Open | Captive bridge | Board must be inserted with bridge removed |
| Retaining lip width | 1.10 | **2.20** | Front lateral restraint increased |
| Printed upper mounting bosses | None | **2** | Reinforced integral side towers |
| Retainer cap top/bottom (local Z) | N/A | **52.25 / 49.25** | 3.00 mm cap thickness |
| Nominal PCB upper face (local Z) | 48.00 | 48.00 | Gap to cap = 1.25 mm |
| Retainer outside width | N/A | **45.1** | ±22.55 mm, local X |
| M2.5 retainer hole centers | N/A | **X±18.30, Y−86.5** | Local coordinate positions |
| Retainer through holes | N/A | **Ø2.9** | M2.5 screw clearance |
| Brass insert seats | N/A | **2 × Ø3.45** | Nominal 4.35-mm-deep heat-set pilot |
| Nominal threaded inserts | N/A | **2 × M2.5** | OD3.7 × L4.0; supplier dimensions must be checked |
| Retainer fasteners | N/A | **2 × M2.5×8** | Simplified CAD screw envelopes |
| Base mounting fasteners | 2 × M5×8 | Unchanged | Plastic key demonstration only |
| Articulation fasteners | 2 × M4×25 | Unchanged | Yaw and pitch pivots |
| Arm reach | 60 | 60 | Unchanged |

## 4. Geometric checks

Source of evidence: `docs/validation_v003.json` and `src/validate_v003.py`.

| Check | Result |
|---|---|
| Full positioned STEP component count | **23 valid single BREP solids** |
| Printable CAD parts | **5 valid, watertight STL solids** |
| Unwanted resting intersections between cradle, cap and PCB envelope | **0 mm³** |
| Intersections of inserted nominal M2.5 bolts with cap/towers/inserts | **0 mm³** (insert-to-pilot thermal embedding is intentionally interfering) |
| Test rotations (yaw -30°, 0°, +30° × pitch -15°, 0°, +15°) | **9 / 9 passed** |
| Board escape displacement along local ±X, ±Y, ±Z | **6 / 6 blocked in CAD** |
| Retainer to nominal board axial gap | **1.25 mm** |

**Method:** Each escape check translates the nominal board in one of the six cardinal directions by 2–4 mm and asserts a positive-volume clash with the cradle or bolted bridge. Each brass insert intentionally intersects its undersized printed heat-set pilot by approximately 5.62 mm³ in the nominal CAD; the insert’s central threaded passage remains clear of its M2.5 screw. This establishes local geometric obstruction, **not** a comprehensive multi-axis escape-path proof, dynamic vibration test, stress simulation, grip-force guarantee, or confirmation that a different-size real PCB fits.

**Risk register:** actual board thickness, header protrusions, antenna position, USB-cable connector and strain relief, heat-set insert type, bridge print direction and layer adhesion, actual fastener tightening torque, and rail/gantry travel envelope remain unverified. For final hardware use, dimension from calipers and replace the photo-derived extrusion reference with the actual fitted rail section.

## 5. Files

| File | Function |
|---|---|
| `step/COMPLETE_4040_ESP32_CAM_MB_ASSEMBLY_V003.step` | **FULL 23-piece correctly positioned CAD assembly** |
| `step/V003_anti_inversion_cradle.step` | New printed cradle only, original assembly-local coordinates |
| `step/V003_bolted_top_retainer.step` | New removable bolted bridge only |
| `stl/V003_anti_inversion_cradle.stl` | **Printable cradle geometry** |
| `stl/V003_bolted_top_retainer.stl` | **Printable bridge geometry** |
| `stl/V001_*.stl`, `stl/V5_*.stl` | Three original base, arm and key print parts, unchanged |
| `viewer/COMPLETE_ASSEMBLY_V003.glb` | Colored complete V003 assembly |
| `viewer/OPEN_V003_OFFLINE.html` | **Self-contained browser viewer** (embedded JS, no CDN) |
| `src/build_v003.py` | V003 design, subpart geometry and full assembly exporter |
| `src/validate_v003.py` | Assertions for watertight STLs, 6-direction blocking and 9 joint poses |
| `src/render_v003.py` | Model-derived VTK renders, including exploded and inverted states |
| `src/export_viewer_v003.py` | Offline viewer and glTF model export |
| `src/build_assembly.py` | Unchanged V002 upstream geometry used by V003 |
| `src/v001_mount.py` | Unchanged V001 initial Python geometry and parameters |
| `reference/*.scad` | Recovered original V5 T-slot/extrusion sources |
| `reference/V002_original_preserved.zip` | **Exact byte-for-byte V002 ZIP archive** |
| `docs/BOM.csv` | V003 revised BOM |
| `docs/assembly_manifest_v003.json` | Numeric parameter register and independent assembly solids |
| `docs/validation_v003.json` | Test outputs and explicit limitations |
| `docs/provenance.json` | SHA-256 and preservation verification |
| `previews/*.png` | Actual geometry-derived previews shown throughout README |

### Regenerate (Python 3.11+)

`/src/`:

```bash
python -m pip install cadquery shapely trimesh numpy matplotlib vtk plotly pillow
python src/build_v003.py
python src/validate_v003.py
python src/export_viewer_v003.py
# On Linux with no display:
xvfb-run -a python src/render_v003.py
# On desktop macOS without xvfb-run:
python src/render_v003.py
```

Only run `build_v003.py` to regenerate the V003 assembly. `build_assembly.py` and `v001_mount.py` are retained as upstream history. Modify `CaptureSpec` in `build_v003.py` for board/retainer fit and selected inserts. For an accurate non-default camera PCB, also modify the original `Spec`/reference envelope in upstream and then retest all constraints.

> **Version policy:** V002 stays unchanged; V003 is the first bolted, mechanically captive-cradle revision. Do not overwrite the original V002 ZIP. The **complete**, editable STEP and both changed printable STL files are included, not just a concept illustration.
