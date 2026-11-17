# Engineering documentation — V006 current release

[Project README](../README.md) · [Full assembly STEP](../step/COMPLETE_4040_ESP32_CAM_MB_ASSEMBLY_V006.step) · [Design history](../CHANGELOG.md)

| Current V006 record | What it provides |
|---|---|
| [CURRENT_RELEASE.json](CURRENT_RELEASE.json) | Canonical release and artifact pointers |
| [ENGINEERING_NOTES_V006.md](ENGINEERING_NOTES_V006.md) | Wrist geometry and outboard USB cable design assumptions |
| [BOM.csv](BOM.csv) / [BOM_V006.csv](BOM_V006.csv) | Latest hardware list (identical copies) |
| [PHYSICAL_FIT_REGISTER_V006.csv](PHYSICAL_FIT_REGISTER_V006.csv) | Caliper measurements and qualification tasks still required |
| [manifest_v006.json](manifest_v006.json) | 30 named positioned assembly/reference entries |
| [validation_v006.json](validation_v006.json) | Thirteen sampled poses and their cable surface gaps |
| [VALIDATION_SCOPE.md](VALIDATION_SCOPE.md) | Explicit CAD-only limitations and acceptance gates |
| [RELEASE_INDEX.md](RELEASE_INDEX.md) | Current revision versus historical file conventions |

V006 has **four hand-wheel joints**, **two new printable CAD shapes** and **13 sampled successful poses**. The nominal minimum cable-to-thumbwheel gap is **7.132 mm**, and cable-to-rail gap is **3.802 mm**. These measurements do not qualify real printer motion, cable bend, torque, board stack dimensions, or vibration.

Older documents with explicit V003–V005 names remain immutable historical design records; the unversioned BOM and root README must refer to V006.

Rebuild: `make build && make validate`. Integrity tests: `make docs`. Render on headless Linux: `xvfb-run -a python src/render_v006.py`.
