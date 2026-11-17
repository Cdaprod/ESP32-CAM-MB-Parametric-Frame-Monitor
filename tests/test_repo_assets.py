"""Dependency-free repository release integrity check (current: V006).

Historical version-tagged artifacts are deliberately retained. Unversioned entry points
must always identify the active release and its generated outputs.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]

def require(path: str, minimum: int = 1) -> Path:
    p = (ROOT / path).resolve()
    assert p.is_relative_to(ROOT.resolve()), f"Path escapes repository: {path}"
    assert p.is_file(), f"Missing release file: {path}"
    assert p.stat().st_size >= minimum, f"Empty release file: {path}"
    return p

version = require("VERSION").read_text(encoding="utf-8").strip()
assert version == "V006", f"Expected V006, got {version!r}"
release = json.loads(require("docs/CURRENT_RELEASE.json").read_text(encoding="utf-8"))
assert release["release"] == version and release["is_current"] is True
assert release["articulation"]["hand_adjustable_joint_count"] == 4
assert release["articulation"]["independent_wrist_joint_count"] == 1

readme = require("README.md").read_text(encoding="utf-8")
assert "Current release: V006" in readme[:900]
assert "previews/v006_wrist_full_assembly.png" in readme[:1000]
assert "V003-only" in readme
assert "physical fit unverified" in readme.lower()
for value in ("7.132 mm", "3.802 mm", "13 of 13"):
    assert value in readme, value

for key in ("source", "validator", "renderer", "assembly_step", "bom",
            "bom_snapshot", "fit_register", "manifest", "validation", "legacy_viewer"):
    require(release[key])
for key in ("new_printed", "reused_printed", "previews"):
    for artifact in release[key]:
        require(artifact, 100)

for document in ("README.md", "CHANGELOG.md", "docs/README.md",
                 "docs/RELEASE_INDEX.md", "docs/VALIDATION_SCOPE.md"):
    content = require(document).read_text(encoding="utf-8")
    # Check every Markdown hyperlink and embedded image, ignoring external URLs.
    for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', content):
        if target.startswith(("https://", "http://", "mailto:", "#")):
            continue
        local = target.split("#", 1)[0].split("?", 1)[0]
        if local:
            require(str(Path(document).parent / local))

for relative in release["previews"]:
    assert require(relative, 1000).read_bytes()[:8] == b"\x89PNG\r\n\x1a\n", relative

assert require("docs/BOM.csv").read_bytes() == require("docs/BOM_V006.csv").read_bytes(), \
    "Current and versioned V006 BOMs diverge"
with require("docs/BOM.csv").open(newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))
assert rows and all(row["revision"] == version for row in rows)
wheels = [row for row in rows if "thumbwheel" in row["item"].lower()]
assert len(wheels) == 1 and wheels[0]["quantity"] == "4"

manifest = json.loads(require("docs/manifest_v006.json").read_text(encoding="utf-8"))
report = json.loads(require("docs/validation_v006.json").read_text(encoding="utf-8"))
summary = report["summary"]
assert manifest["revision"] == summary["revision"] == version
assert manifest["component_count"] == len(manifest["components"]) == 30
assert summary["result"] == "PASS CAD-only"
assert summary["tested_poses"] == len(report["poses"]) == 13
assert summary["thumbwheel_count"] == 4
assert abs(summary["min_cable_to_knob_mm"] - 7.132) <= 0.001
assert abs(summary["min_cable_to_rail_mm"] - 3.802) <= 0.001

with zipfile.ZipFile(require("reference/V002_original_preserved.zip", 1000)) as archive:
    assert archive.testzip() is None, "V002 original archive CRC mismatch"
for path in ("src/v001_mount.py","src/build_assembly.py","src/build_v003.py",
             "src/build_v004.py","src/build_v005.py",
             "step/COMPLETE_4040_ESP32_CAM_MB_ASSEMBLY_V003.step",
             "step/COMPLETE_4040_ESP32_CAM_MB_ASSEMBLY_V004.step"):
    require(path)

print("PASS: current V006 README, links, images, STEP/STLs, CSV, JSON, history")
