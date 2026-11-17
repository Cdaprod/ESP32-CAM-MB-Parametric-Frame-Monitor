"""Gate source, models, rendered PNGs, mesh validity and V009 cable clearances."""
import json
from pathlib import Path
import trimesh
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
REQUIRED=[
 'src/build.py','src/frame_monitor/config.py','src/frame_monitor/geometry.py',
 'src/frame_monitor/cable.py','src/frame_monitor/assembly.py',
 'src/frame_monitor/validate.py','src/frame_monitor/export.py',
 'src/frame_monitor/render.py','src/frame_monitor/primitives.py',
 'src/frame_monitor/rail.py','src/frame_monitor/parts.py',
 'src/frame_monitor/wrist.py','src/frame_monitor/vtk_renderer.py',
 'step/COMPLETE_4040_ESP32_CAM_MB_ASSEMBLY_V009.step',
 'step/V009_first_arm.step','step/V009_second_arm.step',
 'stl/V009_first_arm.stl','stl/V009_second_arm.stl',
 'docs/manifest_v009.json','docs/validation_v009.json',
 'previews/v009_full_assembly.png','previews/v009_cable_guides.png',
 'previews/v009_wrist_20_degrees.png',
]
for relative in REQUIRED:
    path=ROOT/relative
    assert path.is_file() and path.stat().st_size>100,relative
report=json.loads((ROOT/'docs/validation_v009.json').read_text())
s=report['summary']
assert s['revision']=='V009' and s['status']=='PASS CAD-only'
assert s['sampled_poses']==len(report['poses'])==13
assert s['component_entries']==30 and s['arm_guides_aligned']==2
assert s['watertight_new_stls']==2
assert s['min_cable_to_knob_mm']>=2 and s['min_cable_to_rail_mm']>=1.5
for pose in report['poses']:
    assert all(.24<=g<=.5 for g in pose['cable_to_guide_mm'].values()),pose
    assert max(pose['unintended_cable_guide_overlap_mm3'].values())<.01,pose
for relative in ('stl/V009_first_arm.stl','stl/V009_second_arm.stl'):
    mesh=trimesh.load(ROOT/relative,force='mesh')
    assert mesh.is_watertight and mesh.is_volume and mesh.body_count==1,relative
for relative in REQUIRED:
    if relative.endswith('.png'):
        with Image.open(ROOT/relative) as im:
            assert im.size[0]>=1200 and im.size[1]>=800
            im.verify()
from frame_monitor.assembly import components
assert len(components())==30
print('PASS: 13 poses; two aligned arm guides; two watertight STLs; 3 PNGs; STEP')
