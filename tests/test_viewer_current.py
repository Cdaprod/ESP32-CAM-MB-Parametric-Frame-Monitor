"""Fail if current offline viewer, release, STEP or preview PNGs diverge."""
from pathlib import Path
import hashlib,json,re,struct
ROOT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
release=json.loads((ROOT/"docs/CURRENT_RELEASE.json").read_text())
meta=json.loads((ROOT/"viewer/release.json").read_text())
version=(ROOT/"VERSION").read_text().strip()
html_path=ROOT/"viewer/index.html"
glb_path=ROOT/"viewer/COMPLETE_ASSEMBLY.glb"
html=html_path.read_text()
glb=glb_path.read_bytes()
assert version==release["release"]==meta["release"]
assert meta["canonical_viewer"]==release["viewer"]=="viewer/index.html"
assert meta["viewer_glb"]==release["viewer_glb"]=="viewer/COMPLETE_ASSEMBLY.glb"
assert release["viewer_manifest"]=="viewer/release.json"
assert meta["fully_offline"] and meta["standalone_html"]
assert meta["part_count"]==len(meta["component_names"])==30
assert meta["plotly_mesh_policy"]=="all_faces", "Viewer must not drop triangles"
assert len(meta["plotly_face_counts"])==30
assert set(meta["plotly_face_counts"])==set(meta["component_names"])
assert all(n>0 for n in meta["plotly_face_counts"].values())
assert meta["reference_cable_default_hidden"] is False
assert meta["reference_cable_route"]["arc_count"]>=8
source=(ROOT/"src/frame_monitor/viewer.py").read_text()
assert "f[::stride]" not in source, "Face-stride sampling visually corrupts solid surfaces"
assert html_path.stat().st_size>3000000
assert f'<meta name="frame-monitor-release" content="{version}">' in html
assert "Plotly.newPlot" in html
assert not re.search(r'<script[^>]+src=["\x27]https?://',html,re.I)
assert sha(html_path)==meta["html_sha256"]
assert glb[:4]==b"glTF" and struct.unpack("<I",glb[8:12])[0]==len(glb)
assert sha(glb_path)==meta["glb_sha256"]
assert sha(ROOT/meta["assembly_step"])==meta["assembly_step_sha256"]
assert set(meta["previews_sha256"])==set(release["previews"])
for p, expected in meta["previews_sha256"].items():
    assert sha(ROOT/p)==expected,f"Viewer is stale vs {p}"
readme=(ROOT/"README.md").read_text()
assert readme.index("## Explore the latest assembly in 3D")<readme.index("## Why V010 exists")
for p in ("viewer/index.html","viewer/COMPLETE_ASSEMBLY.glb","viewer/release.json"):
    assert f"]({p})" in readme
print(f"PASS current {version} offline viewer, GLB, 30 components, STEP and 8 preview images")

assert 'aria-label="Component visibility"' in html
assert html.count('class="group-toggle"')==4
assert 'id="reset-view"' in html
