"""Verify current V009 documentation, real preview images and release artifacts."""
from pathlib import Path
import csv, json, re, struct, zipfile

ROOT=Path(__file__).resolve().parents[1]
def path_for(relative, allow_directory=False):
    target=(ROOT/relative).resolve()
    assert target.is_relative_to(ROOT.resolve()),relative
    assert target.exists(),relative
    if not allow_directory: assert target.is_file() and target.stat().st_size>0,relative
    return target

assert path_for("VERSION").read_text().strip()=="V009"
release=json.loads(path_for("docs/CURRENT_RELEASE.json").read_text())
assert release["release"]=="V009" and release["is_current"]
readme=path_for("README.md").read_text()
assert "Current CAD development release: V009" in readme[:700]
assert "previews/v009_full_assembly.png" in readme[:1100]
assert "V008" in readme and "7.132 mm" in readme and "3.802 mm" in readme

for field in ("source","validator","renderer","assembly_step","bom","bom_snapshot",
              "fit_register","manifest","validation","notes","legacy_viewer"):
    path_for(release[field])
for field in ("new_printed","reused_printed","previews"):
    for value in release[field]: path_for(value)

for document in ("README.md","CHANGELOG.md","docs/README.md","docs/RELEASE_INDEX.md",
                 "docs/VALIDATION_SCOPE.md"):
    content=path_for(document).read_text()
    for link in re.findall(r'\[[^]]+\]\(([^)]+)\)',content):
        if link.startswith(("http://","https://","mailto:","#")): continue
        relative=link.split("#")[0].split("?")[0]
        if relative: path_for(str(Path(document).parent/relative),allow_directory=True)

for preview in release["previews"]:
    raw=path_for(preview).read_bytes()
    assert raw[:8]==b"\x89PNG\r\n\x1a\n",preview
    width,height=struct.unpack(">II",raw[16:24])
    assert width>=1200 and height>=800,preview

assert path_for("docs/BOM.csv").read_bytes()==path_for("docs/BOM_V009.csv").read_bytes()
with path_for("docs/BOM.csv").open(newline="") as handle:
    rows=list(csv.DictReader(handle))
assert rows and all(r["revision"]=="V009" for r in rows)
assert sum("V009 NEW"==r["origin"] for r in rows)>=2

manifest=json.loads(path_for("docs/manifest_v009.json").read_text())
report=json.loads(path_for("docs/validation_v009.json").read_text())
summary=report["summary"]
assert manifest["revision"]==summary["revision"]=="V009"
assert manifest["component_count"]==len(manifest["components"])==30
assert summary["status"]=="PASS CAD-only"
assert summary["sampled_poses"]==len(report["poses"])==13
assert summary["arm_guides_aligned"]==2 and summary["watertight_new_stls"]==2

for historical in ("previews/v008_full_assembly.png","docs/validation_v008.json",
                   "viewer/OPEN_V003_OFFLINE.html"):
    path_for(historical)
with zipfile.ZipFile(path_for("reference/V002_original_preserved.zip")) as archive:
    assert archive.testzip() is None
print("PASS: canonical V009 README, real PNGs, BOM, current JSON, CAD outputs and history")
