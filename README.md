# ESP32-CAM-MB · Parametric Frame Monitor

**V010 — Rounded-slot structural links, reinforced wrist, tactile knobs and relieved enclosure.**

Built by [Cdaprod](https://github.com/Cdaprod) with **Python + CadQuery**, real STEP/STL models, and actual geometry-derived renders.

**Current development release: V010 (CAD-only prototype; NOT print-qualified).** Real cable bending, snap-fit fatigue, 4040 rail fit, camera connector geometry, fastener preload, and full printer travel remain physically unverified.

**Print-readiness audit:** [12 prioritized, source-verified defects and acceptance gates](docs/PRINT_READINESS_AUDIT_V010.md) · [GitHub issue #5](https://github.com/Cdaprod/ESP32-CAM-MB-Parametric-Frame-Monitor/issues/5). **Do not install V010 on a moving printer** based only on CAD watertightness or screenshot appearance.

## Parametric 2020 / 4040 extrusion mounting brackets

**New feature — CAD engineering candidate, not an integrated V010 replacement.** The same one-piece gusseted bracket generator scales from one centered 2020 slot to two parallel 4040 slots at 20 mm pitch. M5 metal T-nuts provide clamp force; integral indexing tongues sit **between** screw stations, eliminating interference with the separate historical V5 key. An M4 camera-arm pivot retains the `Y = -17 mm` datum.

[**Open the offline interactive mounting-interface model selector**](viewer/mount_interface.html) · [Dimensional constraints, construction and installation](docs/MOUNTING_INTERFACE.md) · [Parametric CadQuery source](src/frame_monitor/mount_interface.py) · [Physical fit register](docs/MOUNTING_FIT_REGISTER.csv).

| Preset | Parallel slots | M5 screws | One-piece plate |
|---|---:|---:|---|
| 2020 single | 1 | 2 | 18 × 54 × 6 mm |
| 4040 dual | 2 | 4 | 38 × 54 × 6 mm |
| 4040 extended | 2 | 8 | 38 × 114 × 6 mm |

![Parametric 2020 bracket, two screws](previews/mount_2020_single_2xM5.png)

![Parametric 4040 bracket, dual slots and four screws](previews/mount_4040_dual_4xM5.png)

![Parametric extended 4040 bracket, eight screws](previews/mount_4040_dual_8xM5.png)

![Actual CAD rear face showing integral locating tongues](previews/mount_4040_tongue_detail.png)

Print-ready bracket exports are *not claimed*: physical slot fit, fastener preload, build orientation, bending strength and full printer motion still require validation. Actual STEP/STL variants are published in `step/MOUNT_*.step` and `stl/MOUNT_*.stl`. The `V010` assembly is preserved as-is until physical integration can be proved.

## Explore the latest assembly in 3D

[![Open the current interactive 3D assembly viewer](previews/v010_full_assembly.png)](viewer/index.html)

**[Open/download the current interactive offline HTML viewer](viewer/index.html)** · [Complete color-coded GLB](viewer/COMPLETE_ASSEMBLY.glb) · [Viewer version and checksums](viewer/release.json)

Orbit, zoom and toggle individual component groups in the standalone viewer. The viewer now retains the complete CAD tessellation rather than omitting triangles, and the cable reference is now a continuous, parameter-driven, pose-dependent tube with exact circular tangent arcs (physical cable bending remains unverified). Its HTML bundles the JavaScript, so after downloading you can open it on your phone or computer without an internet connection. GitHub README pages cannot execute embedded HTML or iframes; this linked preview opens the viewer file, which can be downloaded locally. The same viewer can also be hosted online through GitHub Pages when Pages is enabled.


**V010 structural revision:** The enclosure now uses a 14 mm-wide leaf and a rear-wall buttress with an R1.5 root blend, replacing a 5 mm tab with only 0.8 mm of housing overlap. The wrist has a broad spine, enlarged pitch ear and continuous underside heel; the pitch-arm upright has a full-width triangular heel. Paired ribs carry the extrusion bracket root, with clearance for the base wheel. Base and elbow wheel positions now clear the printed arms; their modeled bolts are M4×30 and M4×25 respectively. The reinforced pitch ear also uses M4×25, with a 2.85 mm nut-bearing floor.

**Cable insertion access:** Alternating clip centers are now 13 mm apart on the first arm and 14 mm on the second, leaving **8.5 mm and 9.5 mm clear between reinforced pads**. The routing groove and entry/exit anchors are revised to match. The nominal 3.0 mm throat still needs a physical cable-retention coupon.

![Reinforced housing, wrist, pitch upright and extrusion root from actual CAD](previews/v010_load_path.png)

Use the current [wrist STEP](step/V010_wrist_adapter.step) / [STL](stl/V010_wrist_adapter.stl) and [mount STEP](step/V010_mount_plate.step) / [STL](stl/V010_mount_plate.stl). Historical V004/V006 exports remain preserved. See [structural dimensions, checks and remaining acceptance gates](docs/ENGINEERING_NOTES_V010.md).

## Why V010 exists

**Visual correction:** The cable seats are now cut into directly reinforced arm sidewalls, inside the original 7.5 mm link thickness. The old suspended rings, long feet and vertical webs have been removed. The connected routing groove runs along each moving link; there is no remote cable-support arm. These are nominal snap-fit candidates, not physically qualified retainers.


The V008/V009 cable supports were essentially two long arms carrying the wire far away from the structural links. Those outriggers were never justified by the hardware. I wanted four small, alternating open U-clips following the link surfaces—not a longer version of the same mistake.

V010 retains the **35 mm pivot-center spacing**, horizontal 4040 rail, left-side mounting plate, metal M5 T-nuts, four hand-operated M4 adjustment joints and captive camera housing. It replaces the outboard ring-and-web guide with **two integral sidewall cable seats on each articulating link**. The clip entry sides alternate (-X, +Z, -X, +Z in each link's local geometry). The nominal 3.2 mm USB cable now follows the link bodies, with unconstrained transitions at the articulated joints.

![Both V010 printed arms from actual CAD](previews/v010_arm_pair.png)

### Isolated mechanical components

![First structural arm and two alternating U-clips](previews/v010_first_arm_isolated.png)

![Second structural arm and two alternating U-clips](previews/v010_second_arm_isolated.png)

![Scalloped M4 hand knob, retaining the original hex-nut interface](previews/v010_thumbwheel.png)

![Camera shell with shallow triangular reliefs](previews/v010_camera_shell.png)

![Assembled V010 cable routing and guides](previews/v010_cable_guides.png)

![Camera with independent wrist yaw at +20 degrees](previews/v010_wrist_20_degrees.png)

### CAD validation results

| Check | V010 CAD result |
|---|---:|
| Sampled base/elbow/pitch/wrist poses | **18 / 18 pass** |
| Distinct U-shaped, short retained clips | 4 |
| Long cable outrigger webs | 0 |
| Unique printed designs with single-volume watertight meshes | **8 / 8 pass** |
| Nominal cable diameter | 3.2 mm |
| Nominal U-seat internal diameter | 3.8 mm |
| Nominal radial cable/clip gap | 0.30 mm |
| Nominal clip entry throat | 3.0 mm |
| Minimum modeled cable/knob clearance | **3.650 mm** |
| Minimum modeled cable/rail clearance | **4.147 mm** |
| Requested cable-reference bend radius | **6.0 mm** (locally reduced as required) |
| Full continuous joint-envelope proof | **Not performed** |
| Real printed clip fatigue and cable bend | **Not verified** |

The 3.0 mm throat is narrower than the nominal 3.2 mm cable. Whether the printed plastic and actual cable jacket can tolerate repeated insertion **has not been established**. Cable routing uses one continuous round sweep over exact tangent arcs, but is still *reference geometry*, not a strain-controlled flexible cable simulation. Modeled bends can be tighter than the requested 6 mm; inspect the achieved radius in the validation JSON.

## Download the actual V010 models

| Item | STEP | Printable STL |
|---|---|---|
| Entire installed assembly | [V010 assembly](step/COMPLETE_4040_ESP32_CAM_MB_ASSEMBLY_V010.step) | — |
| First tapered arm | [STEP](step/V010_first_arm.step) | [STL](stl/V010_first_arm.stl) |
| Second tapered arm | [STEP](step/V010_second_arm.step) | [STL](stl/V010_second_arm.stl) |
| Scalloped hand knob (print four) | [STEP](step/V010_scalloped_thumbwheel.step) | [STL](stl/V010_scalloped_thumbwheel.stl) |
| Relieved camera shell | [STEP](step/V010_relieved_camera_shell.step) | [STL](stl/V010_relieved_camera_shell.stl) |

Use the existing **V004** alignment key and bezel, with the updated **V010 wrist adapter and mount plate**; historical exports are preserved. Use **V010's** camera shell, both arms and knob for new V010 assembly prints.

## OrcaSlicer project

[Download/open V010 printed parts in OrcaSlicer](orca/V010_printed_parts.3mf). The native project contains **11 independent objects**: one of each of the eight printed designs and four hand knobs total. Metal hardware, rail, board and cable references are excluded. Explicit part orientations place the enclosure and pitch/wrist load paths in the print plane; Orca grounds and arranges them on one Neptune 2 plate. The saved placement was checked for bed margins, grounding and nonoverlapping projected hulls with checked spacing.

Embedded settings: Neptune 2 0.4 mm nozzle, Panchroma PLA Matte, 0.20 mm layers, five walls, 40% infill, automatic normal supports, no brim. These are editable starting settings, not physical print qualification. The selected orientations do not establish tested layer strength or support removability; inspect supports and mating surfaces before printing.

Regenerate with `.venv/bin/python src/build_orca_project.py` using the installed OrcaSlicer and matching installed profiles. The script resolves inherited presets into temporary copies, preserves separate objects and BOM quantities, and checks the saved 3MF. No upload or printer operation occurs.

## One build command

`/src/build.py`

```bash
python -m pip install -r requirements.txt
python src/build.py build
python src/build.py validate
xvfb-run -a python src/build.py render  # also refreshes viewer/index.html and GLB
python src/build.py viewer               # refresh viewer only, from current models
python src/build.py mounts  # regenerate parametric 2020 and 4040 bracket family
# Rebuild V010 and mount interface from their current sources
xvfb-run -a python src/build.py all
```

- [Parametric dimensions](src/frame_monitor/config.py), [part geometry](src/frame_monitor/geometry.py), [kinematic cable path](src/frame_monitor/cable.py)
- [Machine-readable validation](docs/validation_v010.json), [assembly manifest](docs/manifest_v010.json), [engineering notes](docs/ENGINEERING_NOTES_V010.md), [BOM](docs/BOM.csv)
- [Design history](CHANGELOG.md) and [GitHub tracking issue #3](https://github.com/Cdaprod/ESP32-CAM-MB-Parametric-Frame-Monitor/issues/3)

### Still open for subsequent iterations

This revision also updates the grip surface of the thumbwheel and produces shallow pocket reliefs on the camera housing. The wrist, enclosure, pitch upright and extrusion mount now have continuous gusseted load paths. The cable still needs a physical strain-relief strategy at the ESP32-CAM-MB connector and proof of minimum cable bend radius around the joints.

![V009 historical geometry, showing the original dangling guide webs](previews/v009_full_assembly.png)

V009 remains archived for comparison; don't mistake its validated guide geometry for V010. **No claims of FEA, topology optimization, stronger links or print-tested cable retention are made.**

*An engineering project by [Cdaprod](https://github.com/Cdaprod): build it, measure it, improve it, and publish the real CAD.*