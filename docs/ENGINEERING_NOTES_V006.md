# V006 — Additional camera wrist pivot and protected cable route

**Status:** CAD-only geometric demonstrator. Physical installation remains unverified.

## Requirement-driven changes

1. Keep the V005 horizontal left-side 4040 mounting configuration and the original V004 base/elbow/pitch joints.
2. Insert a **fourth independent M4 wrist yaw pivot** between the distal arm's pitch lug and the camera shell, retaining tool-free adjustment.
3. Replace the camera shell with a model carrying the lower wrist leaf. The existing enclosure outline, antenna aperture, USB opening and four-screw bezel remain compatible with V004 envelope geometry.
4. Route the nominal **3.2 mm USB cable** out of the bottom opening, rearward underneath the shell, then laterally away from the adjustment wheels and along the outboard side of the links.
5. Model bolt, printed knob, and captive nut in the wrist assembly. Keep existing pitch-wheel captive nut and bore.

## Wrist joint constraints

- Distal pitch joint axis: local X at `(0,-87,-12)` mm.
- Newly introduced yaw pivot: local Z at `(7.5,-136,0)` mm.
- Printed adapter leaf: `Z = -10 .. -4` mm.
- Printed shell leaf: `Z = -3.5 .. +2.3` mm; separated by a modeled axial gap of 0.5 mm.
- Wrist bolt: nominal M4, with a fourth 23 mm diameter hand wheel and captive hex nut.
- Default wrist yaw = 0°; sampled `-20°` and `+20°` relative poses tested.

## Cable routing and clearance

The USB route is a **polyline of swept 3.2 mm cylinders** attached to moving-link reference points, not a flexible finite-element cable. The cable begins at the shell's underside USB aperture. The first route leaves beneath the camera, moves toward its rear and across to an outboard `X = -27 mm` path, then follows the moving wrist and arm sections.

Validation uses precise CadQuery solid-to-solid **minimum surface distance**, separately for each of the four hand knobs, the camera shell, wrist adapter, arm, and 4040 rail. The geometric acceptance thresholds are `>=2.0 mm` cable-to-knob and `>=1.5 mm` cable-to-other-tested-rigid-parts.

The 13 poses explicitly test base yaw from 20° to 40°, elbow angle from -40° to -20°, camera pitch from 0° to 25°, and wrist yaw from -20° to +20° in selected combinations. **Not an exhaustive 4D joint-space proof.**

| CAD check | Observed result |
|---|---:|
| Selected articulated poses | 13 / 13 pass |
| Smallest cable-to-thumbwheel surface clearance | 7.132 mm |
| Smallest cable-to-4040 extrusion surface clearance | 3.802 mm |
| New wrist adapter STL | Watertight / single volume |
| New full-sidewall camera shell STL | Watertight / single volume |
| Unwanted solid intersections in tested mating pairs | 0 mm³ |

## Build and verify

```bash
python -m pip install 'cadquery>=2.4,<3' 'shapely>=2,<3' 'numpy>=1.26,<3' 'trimesh>=4,<5'
python src/build_v006.py
python src/validate_v006.py
```

Renders use VTK and Pillow under Xvfb on headless Linux:

```bash
python -m pip install vtk pillow
xvfb-run -a python src/render_v006.py
```

## Physical checks still required

- Check *actual* ESP32-CAM-MB USB port direction, connector boot dimensions and clearance to shell bottom.
- Route real cable with a manufacturer-approved minimum dynamic bend radius; provide strain relief at the board and sufficient service loop at both moving joints.
- Verify actual frame mounting face, bed travel, nozzle, cable clips, belts, and Z/Y kinematics with the machine moving across its full envelope.
- Verify wrist clamp torque, captive-nut pocket print fit, heat/UV durability, and resistance to vibration.
- Print a small wrist interface coupon and test the joint movement/retention before committing to full assembly.

Earlier V004/V005 geometry/source remains in the repository without modification. Only two printable shapes are new here: wrist adapter and the shell with the wrist leaf. V004's bezel, base, two arm links and 4040 key are reused.