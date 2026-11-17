# Release index — current V010

**Current: V010 — directly integrated arm-sidewall cable passages.** [Current README](../README.md) · [Full STEP assembly](../step/COMPLETE_4040_ESP32_CAM_MB_ASSEMBLY_V010.step) · [Engineering notes](ENGINEERING_NOTES_V010.md)

| Revision | Engineering milestone |
|---|---|
| V001 | Initial camera mount and articulated arm |
| V002 | Recovered dual-slot 4040 extrusion and captured T-slot |
| V003 | Bolted retainer prevents upside-down release |
| V004 | Recessed key, metal M5 T-nuts, handwheel pivots, captive enclosure |
| V005 | Left-side orientation on horizontal rail, camera facing toward bed |
| V006 | Independent wrist joint and nominal cable route |
| V007 | Early dual-guide source candidate, not a complete released build |
| V008 | Unified Python generator and attempted two-arm guide correction |
| V009 | Tapered open-web arms, but long guide supports remain |
| **V010** | **Four cable seats cut directly into the arm sidewalls, two per arm, plus scalloped knobs and relieved camera shell** |

## Current interactive 3D viewer

[Standalone offline HTML viewer](../viewer/index.html) · [Current GLB](../viewer/COMPLETE_ASSEMBLY.glb) · [Integrity metadata](../viewer/release.json). Stable URLs are updated whenever the CAD preview pipeline runs. The V003 viewer is a preserved historical artifact.

## V010 source and export paths

[Unified build entry](../src/build.py) · [Parametric config](../src/frame_monitor/config.py) · [Assembly STEP](../step/COMPLETE_4040_ESP32_CAM_MB_ASSEMBLY_V010.step)

[First printable arm](../stl/V010_first_arm.stl) · [Second printable arm](../stl/V010_second_arm.stl) · [Scalloped thumbwheel](../stl/V010_scalloped_thumbwheel.stl) · [Relieved camera shell](../stl/V010_relieved_camera_shell.stl)

![Actual V010 arm-pair geometry](../previews/v010_arm_pair.png)

![Actual V010 assembled geometry](../previews/v010_full_assembly.png)

[Validation report](validation_v010.json) · [Hardware BOM](BOM.csv) · [Physical measurements](PHYSICAL_FIT_REGISTER_V010.csv)

The historical files retain their original version names. The V003 offline viewer is historical, and neither V008 nor V009 is the current arm design. CAD-only verification: 18 sampled poses, 1.650 mm minimum nominal cable-to-knob clearance, 3.802 mm to rail. Physical cable bending, print fatigue and machine clearances are unqualified.
