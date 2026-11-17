# V009 — Tapered triangulated articulated arms

## Geometry
V009 replaces BOTH V008 flat link cores with a tapered, braced 2.5D profile. End width: 14 mm; midspan: 18 mm; pivot spacing: 35 mm; thickness: 7.5 mm. Two triangular lightening windows preserve perimeter rails and a diagonal rib. This is **topology-inspired**, not FEA-optimized, and is not rated for load or vibration.

## Invariants
4040 remains horizontal; mounting is on its left/outside face and camera points back across the rail. Base and elbow journal XY centers remain (0,-17) and (0,-52) mm. Camera pitch pivot remains (0,-87,-12) mm. The wrist yaw, camera shell, bezel, alignment key and four hand knobs are retained. Both USB guide centers remain (-27,-32,19) and (-27,-69.2,27) mm, using nominal Ø3.8 bores for the Ø3.2 cable.

## Checks
CadQuery locally produced valid BREP geometry, one solid for each redesigned link; both test STL meshes were watertight, positive-volume, one-body meshes. The full original 13-pose validation and assembled interference checks must be performed by CI before release qualification. Local arm checks do not prove joint clearance, nozzle travel, adequate strength, cable bend radius or mating hardware fit. Actual ESP32/USB connector fit, printer motion, tightening torque, fatigue and thermal performance remain unverified.

## Build
Run `xvfb-run -a python src/build.py all` on a CAD-capable Linux host after installing `requirements.txt`. Expected results: `stl/V009_first_arm.stl`, `stl/V009_second_arm.stl`, matching STEP files, complete V009 STEP assembly, `docs/validation_v009.json` and `previews/v009_*.png`.

## Next engineering checks
Measure relative camera payload; test wrist and knob-to-link collisions at extremes; compare V008/V009 link deflection under the same cantilever load; verify minimum 3.2-mm USB cable service-loop bend radius from the actual cable datasheet.
