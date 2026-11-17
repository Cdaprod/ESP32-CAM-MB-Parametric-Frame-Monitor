# Version and artifact index

**Current release: V006.** [Overview](../README.md) · [release JSON](CURRENT_RELEASE.json).

| Revision | Mechanical change | Source |
|---|---|---|
| V001 | First camera mount | [v001_mount.py](../src/v001_mount.py) |
| V002 | Recovered 4040 and T-slot | [build_assembly.py](../src/build_assembly.py) · [archived ZIP](../reference/V002_original_preserved.zip) |
| V003 | Bolted positive cradle retention | [build_v003.py](../src/build_v003.py) |
| V004 | Metal T-nut clamp, recessed key, full sidewalls and three hand wheels | [build_v004.py](../src/build_v004.py) |
| V005 | Left-side horizontal 4040 over-rail orientation | [build_v005.py](../src/build_v005.py) |
| **V006** | **Fourth wrist pivot, revised shell and outboard USB routing** | [build_v006.py](../src/build_v006.py) |

### Current V006 build

- [Complete assembly STEP](../step/COMPLETE_4040_ESP32_CAM_MB_ASSEMBLY_V006.step)
- [Wrist adapter STL](../stl/V006_wrist_adapter.stl) and [revised shell STL](../stl/V006_camera_shell.stl)
- Six reusable V004 print designs, including the four instances of [thumbwheel STL](../stl/V004_M4_thumbwheel.stl)
- [Full assembly render](../previews/v006_wrist_full_assembly.png), [cable clearance](../previews/v006_wrist_and_cable_detail.png), [rotated wrist](../previews/v006_wrist_rotated_20deg.png)
- [Assembly manifest](manifest_v006.json), [13-pose report](validation_v006.json), [current BOM](BOM.csv), [fit register](PHYSICAL_FIT_REGISTER_V006.csv)

Previous STEP/STL/PNG/JSON files are **historical records**, not out-of-date current outputs. The unversioned [BOM.csv](BOM.csv) must match [BOM_V006.csv](BOM_V006.csv). The [V003 offline viewer](../viewer/OPEN_V003_OFFLINE.html) is **V003-only**.

The CAD validation does **not** prove continuous motion clearance, USB bend radius, hardware torque or physical printer travel. See [scope](VALIDATION_SCOPE.md).
