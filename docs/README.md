# Documentation index — V008

[Project README](../README.md) · [V008 complete STEP](../step/COMPLETE_4040_ESP32_CAM_MB_ASSEMBLY_V008.step)

| Current file | What it covers |
|---|---|
| [CURRENT_RELEASE.json](CURRENT_RELEASE.json) | Machine-readable authoritative release and artifact paths |
| [ENGINEERING_NOTES_V008.md](ENGINEERING_NOTES_V008.md) | Both new through-guides, shared cable route and geometry constraints |
| [BOM.csv](BOM.csv) / [BOM_V008.csv](BOM_V008.csv) | Current hardware and printable parts |
| [PHYSICAL_FIT_REGISTER_V008.csv](PHYSICAL_FIT_REGISTER_V008.csv) | Measurements required on actual hardware |
| [manifest_v008.json](manifest_v008.json) | 30 assembled components and reference envelopes |
| [validation_v008.json](validation_v008.json) | 13 sampled poses, cable-to-guide, knob and rail clearances |
| [VALIDATION_SCOPE.md](VALIDATION_SCOPE.md) | What CAD tests do not establish |
| [RELEASE_INDEX.md](RELEASE_INDEX.md) | Earlier revisions versus current build |

Build via `python src/build.py build`; validate via `python src/build.py validate`; geometry renders via `xvfb-run -a python src/build.py render` on headless Linux. [GitHub workflow](../.github/workflows/v008-cad.yml).

Previous versioned documents are retained as historical design records, not actively maintained V008 documentation.
