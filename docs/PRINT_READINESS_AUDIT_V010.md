# V010 — print-readiness and visualization audit (2026-11-17)

**Scope:** Four user-provided iPhone screenshots of `viewer/index.html`, examined against the current GitHub `main` CadQuery implementation. **Status: CAD prototype only; NOT print-qualified or safe to install on a working printer.** This document records the defects. The tracked engineering checklist and acceptance criteria live in [issue #5](https://github.com/Cdaprod/ESP32-CAM-MB-Parametric-Frame-Monitor/issues/5).

## 1. Separate display failures from solid failures

The yellow handwheels and teal camera enclosure appear hollow, triangulated or missing surfaces in the offline HTML. The cause is directly visible in the former `src/frame_monitor/viewer.py`: faces were skipped at a fixed stride (`f[::stride]`). This *cannot* preserve a closed triangulation. It is not proof that the underlying STEP geometry is broken. The immediate source fix retains **all** tessellated triangles in the Plotly HTML, as already done for GLB. The reference cable is hidden by default until the route is corrected, but remains available through the legend.

**Regression gate:** the latest `viewer/index.html`, `COMPLETE_ASSEMBLY.glb`, release manifest, geometry-derived preview PNGs and README links must be generated from the same V010 source in CI. Check mobile performance and fit separately; correctness comes before decimation optimization.

## 2. Cable reference is mechanically misleading

`src/frame_monitor/cable.py` still includes multiple hardcoded `x=-27` waypoints inherited from legacy outboard support geometry, while the V010 clip channel axes use `x=-9.5`. It connects points with straight capped cylinders, leaving hard corners and no bend-radius enforcement. This matches the zigzagging and hanging black cable seen in the screenshots. **A hidden cable in the viewer is not a corrected routing.**

Replace with per-moving-link attachment frames, measured cable and boot envelope, continuous radius-constrained centerline, joint service slack, end termination and strain relief. Sweep the entire permitted four-axis envelope and report minimum bend radius and nearest-part clearance. The nominal 3.2 mm cable is only an assumption.

## 3. Structural arm and wrist concerns

`src/frame_monitor/geometry.py::_skeletal_link` removes two long triangular openings from each 35 mm pivot-to-pivot arm. Very narrow residual diagonal webs, unsupported transitions and local notches can concentrate bending and torsional stress. The existing 0.7–1.0 mm cosmetic fillets do not establish minimum load-bearing sections or printed-layer strength.

`second_arm` also includes a 12 × 8 × 31 mm vertical riser joined to the arm, and `src/frame_monitor/wrist.py::adapter` retains a narrow approximately 49 mm bridge with 4.35 × 8 mm cross-section. Confirm the critical orientations and reinforce these junctions with integrated ribs/gussets or a redesigned mechanical connection. Do not simply thicken every surface: preserve link kinematics, 35 mm pivot datums, camera mounting envelope, access and full printer clearance.

Test load directions **relative to FDM build Z** (layer interfaces). Publish actual slice paths, section maps, unsupported overhangs, root radii and mechanical assumptions before claiming a link is print-ready.

## 4. Clip geometry is unproven

The four U-shaped cutouts are modeled in rectangular pads; the nominal 3.2 mm jacket must pass a **2.65 mm throat** into a **3.8 mm seat**. No compliant root length, strain, jacket measurement, insertion cycle, fatigue, snap force or thermal creep is currently tested. Rounded leads and a flexible cantilever/living-hinge geometry must be chosen based on material and print orientation; build small clip-only coupons first.

## 5. CAD acceptance is not print acceptance

`src/frame_monitor/validate.py` checks BREP validity, single-body watertightness and volume consistency for **four new** V010 STL outputs, plus 18 pose samples and cable/reference clearances. The assembled print BOM contains **eight distinct printed designs**: V004 key, V004 mounting plate, V010 first and second arms, shared M4 wheel, V006 wrist adapter, V010 shell, V006 bezel. Four identical wheels do not create four unique printable designs.

Before calling a release a print candidate: validate *all eight* current print-source files; verify minimum cross-section and wall after cuts, surface normals and mesh integrity, CAD clearance/contact, specific OrcaSlicer preview, print orientation, material, layer height, line width and perimeter count; check actual 4040 and nut clamping; check complete unpowered printer travel, heat, vibration, fastener preload and cable bending. Then perform physical fitting and functional testing. Physical qualification cannot be established by software alone.

## Release decision

**V010 stays archived as the latest CAD-only prototype**, even if its viewer displays correctly. The next release can only be called a **print candidate** after geometry, slicing and actual hardware dimensions are verified. Call it physically qualified only after documented test coupons, arm and wrist load testing, clip cycling, clamping checks and full-travel inspection.

See [source geometry](../src/frame_monitor/geometry.py), [wrist](../src/frame_monitor/wrist.py), [cable](../src/frame_monitor/cable.py), [viewer](../src/frame_monitor/viewer.py), [validation](../src/frame_monitor/validate.py), [current measurements](PHYSICAL_FIT_REGISTER_V010.csv) and [issue #5](https://github.com/Cdaprod/ESP32-CAM-MB-Parametric-Frame-Monitor/issues/5).
