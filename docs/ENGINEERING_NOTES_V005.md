# V005 — Left-side, over-rail assembly configuration

## Intent and coordinate system

The **4040 rail remains horizontal along world X**. The mount moves from V004's underside to the **left/outside +Y face** at `Y=+20 mm`. The machine interior and intended printer-bed view are toward **world −Y**. Up is **+Z**. The active captured rail slot is at `Z=+10 mm`.

This is **not** a mirrored STL redesign. V005 rigidly rotates every V004 assembled component (except the stationary 4040 rail) **+90° about the global X axis**, then specifies a documented articulated pose: base yaw **+30°**, elbow **−30°**, camera pitch **+12°**. Every V004 print model remains unchanged.

## CAD-only acceptance

- **26** positioned component/reference entries; all geometric solids valid.
- Plate left-side datum `Y=+20 mm`, flush with nominal rail face.
- Metal M5 T-nuts and positioning key recessed **0.65 mm** below the active rail face.
- No positive-volume collisions for rail vs plate, links, housing, bezel, or camera envelope in this pose.
- Nominal center ray points inward toward world `−Y` and crosses both rail faces **7.5 mm above the 4040 top**.
- Vision check uses a **single nominal lens-center ray**, not camera optical field-of-view or printer bed model.

## Regenerate and validate

`/src/build_v005.py`

```bash
python src/build_v005.py
python src/validate_v005.py
# Optional CAD-derived PNGs:
xvfb-run -a python src/render_v005.py
```

The generated STEP is `step/COMPLETE_4040_ESP32_CAM_MB_ASSEMBLY_V005.step`; machine-readable checks are `docs/validation_v005.json`. The committed CI workflow uploads this STEP as a workflow artifact.

## Physical acceptance still required

Measure the **actual** front-side 4040 rail location and slot form; confirm nearby frame parts and print-bed motion; use the actual ESP32-CAM-MB and USB cable envelope; validate line of sight with real optics and a field-of-view check; then test screw engagement, hand-wheel torque, vibration, cable flex, and thermal performance. V005 is an **engineering candidate**, not print-ready hardware certification.

The prior V004 sources, meshes, and published previews remain unchanged.
