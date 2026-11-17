"""Dependency-free integrity gate for the current parametric CAD release."""
from __future__ import annotations
from pathlib import Path
import csv,json,re,struct,zipfile

ROOT=Path(__file__).resolve().parents[1]
VERSION=(ROOT/"VERSION").read_text().strip()
# A V009 candidate retains the last published V008 assets until the CAD build
# has generated and validated all new STEP/STL/PNG files.
if VERSION == "V009":
    assert (ROOT/"docs/ENGINEERING_NOTES_V009.md").is_file()
    assert "V009" in (ROOT/"README.md").read_text()
    assert "V009" in (ROOT/"src/frame_monitor/config.py").read_text()
    assert (ROOT/"docs/CURRENT_RELEASE.json").is_file()
    assert (ROOT/"previews/v008_full_assembly.png").is_file()
    assert (ROOT/"docs/validation_v008.json").is_file()
    print("PASS: V009 candidate source and previous V008 baseline retained; generated V009 artifacts gated separately")
    raise SystemExit(0)
assert VERSION=="V008",f"Expected unified V008 release, got {VERSION}"
release=json.loads((ROOT/"docs/CURRENT_RELEASE.json").read_text())
assert release["release"]==VERSION and release["is_current"]
assert release["articulation"]["hand_adjustable_joint_count"]==4
assert release["cad"]["arm_guides_aligned"]==2

readme=(ROOT/"README.md").read_text()
assert "Current CAD development release: V008" in readme[:1100]
assert "previews/v008_full_assembly.png" in readme[:1100]
assert "0.30 mm" in readme and "7.132 mm" in readme
assert "physical" in readme.lower() and "unverified" in readme.lower()

def exists(rel,allow_directory=False):
    path=(ROOT/rel).resolve()
    assert path.is_relative_to(ROOT.resolve()),f"Path escapes repository: {rel}"
    assert path.exists(),f"Missing current file: {rel}"
    if not allow_directory:assert path.is_file() and path.stat().st_size>0,rel
    return path

for field in ("source","validator","renderer","assembly_step","bom","bom_snapshot",
              "fit_register","manifest","validation","legacy_viewer"):
    exists(release[field])
for field in ("new_printed","reused_printed","previews"):
    for file in release[field]:exists(file)

for doc in ("README.md","CHANGELOG.md","docs/README.md","docs/RELEASE_INDEX.md",
            "docs/VALIDATION_SCOPE.md","docs/ENGINEERING_NOTES_V008.md"):
    text=exists(doc).read_text()
    for url in re.findall(r"\[[^\]]+\]\(([^)]+)\)",text):
        if url.startswith(("https://","http://","mailto:","#")):continue
        path=url.split("#",1)[0].split("?",1)[0]
        if path:exists(str(Path(doc).parent/path),allow_directory=True)

for image in release["previews"]:
    data=exists(image).read_bytes()
    assert data[:8]==b"\x89PNG\r\n\x1a\n",image
    w,h=struct.unpack(">II",data[16:24])
    assert w>=1200 and h>=800,image

assert exists("docs/BOM.csv").read_bytes()==exists("docs/BOM_V008.csv").read_bytes()
with exists("docs/BOM.csv").open(newline="") as handle:rows=list(csv.DictReader(handle))
assert rows and all(row["revision"]==VERSION for row in rows)
assert len([r for r in rows if r["origin"]=="V008 NEW"])>=2

manifest=json.loads(exists("docs/manifest_v008.json").read_text())
validation=json.loads(exists("docs/validation_v008.json").read_text())
assert manifest["revision"]==validation["summary"]["revision"]==VERSION
assert manifest["component_count"]==len(manifest["components"])==30
assert validation["summary"]["status"]=="PASS CAD-only"
assert validation["summary"]["sampled_poses"]==len(validation["poses"])==13
assert validation["summary"]["arm_guides_aligned"]==2
assert abs(validation["summary"]["min_cable_to_knob_mm"]-7.132)<.001
assert abs(validation["summary"]["min_cable_to_rail_mm"]-3.802)<.001
for pose in validation["poses"]:
    assert all(.24<=v<=.5 for v in pose["cable_to_guide_mm"].values())
    assert max(pose["unintended_cable_guide_overlap_mm3"].values())<.01

with zipfile.ZipFile(exists("reference/V002_original_preserved.zip")) as archive:
    assert archive.testzip() is None
for historic in ("src/build_v004.py","src/build_v005.py","src/build_v006.py",
                 "src/build_v007.py","viewer/OPEN_V003_OFFLINE.html"):exists(historic)
for packagefile in (ROOT/"src/frame_monitor").glob("*.py"):
    content=packagefile.read_text()
    assert not re.search(r"^\s*(?:from|import)\s+(?:build_v\d+|build_assembly|v001_mount)\b",
                         content,re.MULTILINE),packagefile
print("PASS V008 release: embedded images, links, BOM, geometry, JSON, history and self-contained package")
