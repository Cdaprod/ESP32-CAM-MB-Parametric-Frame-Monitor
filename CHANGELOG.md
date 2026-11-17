# ESP32-CAM-MB Parametric Frame Monitor — design history

**Current development release: V006.** Historical revision files remain intact.

## V006 — Additional wrist pivot and outboard USB path

- Adds a fourth independent M4 thumbwheel joint: camera wrist yaw (base, elbow and camera pitch are retained).
- Adds a printed wrist adapter and revised full-sidewall camera shell; reuses six unique V004 printable geometries.
- Moves the nominal Ø3.2 mm USB cable beneath/behind the camera and outboard of knobs.
- 30 assembly/reference entries; 13 sampled poses pass; nominal minimum cable-to-knob 7.132 mm; cable-to-rail 3.802 mm.
- Two new watertight printable STLs, assembled STEP, three geometry-derived PNGs and JSON reports.
- **CAD-only:** real USB connector, bend radius, dynamic slack, printer travel, physical slot, and clamp torque unverified.

[Source](src/build_v006.py) · [Current BOM](docs/BOM.csv) · [Detailed notes](docs/ENGINEERING_NOTES_V006.md).

## V005 — Left-side mounting orientation

Horizontally mounted 4040 with the camera on the outside left face looking back over the rail. [Source](src/build_v005.py).

## V004 — Revised rail clamp and fully captured case

Recessed key, metal T-nuts, three adjustable hand wheels, full camera sidewalls and bottom USB exit. [Source](src/build_v004.py) · [historical BOM](docs/BOM_V004.csv).

## V003 — Inversion-resistant cradle

Removable bolted retainer and reinforced side features. [Source](src/build_v003.py) · [historical STEP](step/COMPLETE_4040_ESP32_CAM_MB_ASSEMBLY_V003.step).

## V002 — 4040 frame assembly and screws

Recovered undercut key and dual-slot 4040 section, complete camera arm and screw demonstrator. [Original preserved ZIP](reference/V002_original_preserved.zip).

## V001 — Initial proof of concept

Python-generated camera board cradle, arm and mounting plate. [Source](src/v001_mount.py).

The [V003 offline viewer](viewer/OPEN_V003_OFFLINE.html) and older geometry artifacts are intentionally historic; do not mistake them for the latest V006 configuration.
