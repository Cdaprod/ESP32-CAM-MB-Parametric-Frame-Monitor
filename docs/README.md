# Documentation — current V009 CAD release

[Main README with the real V009 previews](../README.md) · [Full V009 assembly STEP](../step/COMPLETE_4040_ESP32_CAM_MB_ASSEMBLY_V009.step)

| Current V009 artifact | Purpose |
|---|---|
| [CURRENT_RELEASE.json](CURRENT_RELEASE.json) | Machine-readable authoritative current version and model paths |
| [ENGINEERING_NOTES_V009.md](ENGINEERING_NOTES_V009.md) | Tapered arm geometry and preserved cable-guide coordinates |
| [BOM.csv](BOM.csv) / [BOM_V009.csv](BOM_V009.csv) | Current hardware and printable arm parts |
| [PHYSICAL_FIT_REGISTER_V009.csv](PHYSICAL_FIT_REGISTER_V009.csv) | Physical measurements and structural testing pending |
| [manifest_v009.json](manifest_v009.json) | Thirty positioned assembly and reference components |
| [validation_v009.json](validation_v009.json) | Thirteen poses, clearance report and watertight STLs |
| [VALIDATION_SCOPE.md](VALIDATION_SCOPE.md) | What CAD tests do and do not establish |
| [RELEASE_INDEX.md](RELEASE_INDEX.md) | Revision lineage |

**Actual V009 CAD renders:** [Full assembly](../previews/v009_full_assembly.png) · [Cable guide and arms](../previews/v009_cable_guides.png) · [20° wrist](../previews/v009_wrist_20_degrees.png)

Build: `python src/build.py build` · Validate: `python src/build.py validate` · Render: `xvfb-run -a python src/build.py render`.

V008 remains the historical reference, but V009 is the current checked assembly. Nothing is physically load-rated or verified against the full printer travel envelope.
