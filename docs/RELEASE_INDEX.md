# Releases and current model — V008

**Current development release: V008.** [Project README](../README.md) · [Machine-readable release](CURRENT_RELEASE.json)

| Revision | Mechanical milestone | Canonical source |
|---|---|---|
| V001 | Initial frame mount and open cradle | [v001_mount.py](../src/v001_mount.py) |
| V002 | Recovered 4040 section and captured T-slot | [build_assembly.py](../src/build_assembly.py) · [Original ZIP](../reference/V002_original_preserved.zip) |
| V003 | Positive bolted cradle retention | [build_v003.py](../src/build_v003.py) |
| V004 | 0.65 mm recessed key, metal T-nuts, knobs, full enclosure | [build_v004.py](../src/build_v004.py) |
| V005 | Left-side horizontal mounting aimed back over rail | [build_v005.py](../src/build_v005.py) |
| V006 | Fourth independent camera wrist yaw, outboard cable reference | [build_v006.py](../src/build_v006.py) |
| V007 | Unreleased two-arm guide source candidate; not a verified release | [build_v007.py](../src/build_v007.py) |
| **V008** | **Independent unified CAD package; two aligned cable guides with 13-pose regression** | [build.py](../src/build.py) and [frame_monitor](../src/frame_monitor/) |

### Current V008 deliverables

- [Complete assembled STEP](../step/COMPLETE_4040_ESP32_CAM_MB_ASSEMBLY_V008.step)
- [New first arm STL](../stl/V008_first_arm.stl) and [second arm STL](../stl/V008_second_arm.stl)
- [Three real-geometry PNG previews](../previews/v008_full_assembly.png) · [Guides](../previews/v008_cable_guides.png) · [Wrist rotation](../previews/v008_wrist_20_degrees.png)
- [BOM](BOM.csv), [physical fit register](PHYSICAL_FIT_REGISTER_V008.csv), [assembly manifest](manifest_v008.json), [CAD report](validation_v008.json)
- [Engineering details](ENGINEERING_NOTES_V008.md), [validation limits](VALIDATION_SCOPE.md)

The unversioned BOM is a byte-for-byte copy of `BOM_V008.csv`. Historical STEP/STL/Python/PNG artifacts are preserved and explicitly version-labeled. The offline viewer under `viewer/` is **V003 only**, not V008.

**CAD only:** 13/13 selected joint poses pass. Minimum cable-to-knob gap 7.132 mm, cable-to-4040 gap 3.802 mm; both guide bores provide modeled 0.30 mm radial cable clearance. Actual fit, bend, sag and fatigue remain unverified.
