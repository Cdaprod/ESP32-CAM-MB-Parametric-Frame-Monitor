"""Dependency-free canonical V010 repository integrity test.

Checks actual embedded previews, all local links in release-facing documentation,
source-of-truth CAD metrics and active export paths. Does not claim physical safety.
"""
from pathlib import Path
import csv
import json
import re
import struct

ROOT = Path(__file__).resolve().parents[1]
def must_exist(relative, *, directory=False):
    path = (ROOT / relative).resolve()
    assert path.is_relative_to(ROOT.resolve()), f"Escapes repository: {relative}"
    assert path.is_dir() if directory else path.is_file() and path.stat().st_size > 0, f"Missing artifact: {relative}"
    return path

release = json.loads(must_exist("docs/CURRENT_RELEASE.json").read_text())
report = json.loads(must_exist("docs/validation_v010.json").read_text())
manifest = json.loads(must_exist("docs/manifest_v010.json").read_text())
summary = report["summary"]
assert must_exist("VERSION").read_text().strip() == release["release"] == "V010"
assert release["is_current"]
assert summary["revision"] == manifest["revision"] == release["release"]
assert summary["status"] == "PASS CAD-only"
assert summary["sampled_poses"] == len(report["poses"]) == 18
assert summary["integrated_alternating_open_clips"] == 4
assert summary["long_outriggers"] == 0
assert summary["watertight_new_stls"] == len(release["new_stls"]) == 5
assert manifest["component_count"] == len(manifest["components"]) == 30
assert abs(summary["min_cable_to_knob_mm"] - 1.887) < 0.001
assert abs(summary["min_cable_to_rail_mm"] - 4.147) < 0.001

for name in ("source", "config", "assembly_step", "manifest", "validation",
             "bom", "engineering_notes"):
    must_exist(release[name])
for name in release["new_stls"]:
    must_exist(name)
    must_exist(name.replace("stl/", "step/").replace(".stl", ".step"))

readme = must_exist("README.md").read_text()
assert "**Current development release: V010" in readme
assert "1.887 mm" in readme and "4.147 mm" in readme

DOCS = [
    "README.md", "docs/README.md", "docs/RELEASE_INDEX.md",
    "docs/VALIDATION_SCOPE.md", "docs/ENGINEERING_NOTES_V010.md",
    "CHANGELOG.md",
]
for doc in DOCS:
    content = must_exist(doc).read_text()
    for link in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', content):
        if link.startswith(("https://", "http://", "mailto:", "#")):
            continue
        path_part = link.split("#", 1)[0].split("?", 1)[0]
        if path_part:
            target = (Path(doc).parent / path_part).as_posix()
            target_path = ROOT / target
            must_exist(target, directory=target_path.is_dir())

for image_path in release["previews"]:
    raw = must_exist(image_path).read_bytes()
    assert raw[:8] == b"\x89PNG\r\n\x1a\n", image_path
    width, height = struct.unpack(">II", raw[16:24])
    assert width >= 1200 and height >= 800, (image_path, width, height)
    assert f"]({image_path})" in readme, image_path

assert len(release["previews"]) == 8
assert must_exist("docs/BOM.csv").read_bytes() == must_exist("docs/BOM_V010.csv").read_bytes()
with must_exist("docs/BOM.csv").open(newline="") as f:
    bom = list(csv.DictReader(f))
assert bom and all(row["revision"] == "V010" for row in bom)

# These engineering pages must use the exact current minimums, not stale candidate values.
for doc in ("docs/README.md", "docs/VALIDATION_SCOPE.md", "docs/ENGINEERING_NOTES_V010.md"):
    text = must_exist(doc).read_text()
    assert "1.887 mm" in text and "4.147 mm" in text, doc
    assert "3.909 mm" not in text, doc
assert must_exist("previews/v009_full_assembly.png").is_file()
print("PASS: V010 README/docs image links, canonical JSON, actual PNGs, STEP/STLs and metrics")
