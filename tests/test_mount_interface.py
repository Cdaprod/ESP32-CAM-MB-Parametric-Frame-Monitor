"""CAD gating for the parametric 2020 / 4040 mounting-interface family.

These tests prove nominal geometric consistency, not safe FDM loading or fit.
"""
import sys,json,struct
from pathlib import Path
from dataclasses import replace
import cadquery as cq
import trimesh
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from frame_monitor.mount_interface import (MountSpec,PRESETS,bracket,
    reference_extrusion,tnut_reference,feature_manifest)

variants={
 '2020_single_2xM5':(1,2,18,54),
 '4040_dual_4xM5':(2,4,38,54),
 '4040_dual_8xM5':(2,8,38,114),
 '4040_single_2xM5':(1,2,18,54)}
for name,(channels,count,width,length) in variants.items():
    s=PRESETS[name]
    assert s.channel_count==channels
    assert len(s.hole_centers_mm)==count
    assert s.plate_width_mm==width and s.plate_length_mm==length
    if channels==2:assert s.slot_centers_mm==(-10,10)
    for a,b in s.tongue_intervals_mm:
        assert b-a>3
        assert all(not a<=z<=b for z in s.stations_mm)
    plate=bracket(s);rail=reference_extrusion(s)
    assert plate.isValid() and len(plate.Solids())==1,name
    assert abs(plate.BoundingBox().xlen-width)<.05
    assert plate.intersect(rail).Volume()<.01,name
    for nut in tnut_reference(s):
        assert nut.intersect(rail).Volume()<.01,name
        assert nut.intersect(plate).Volume()<.01,name
    for x,z in s.hole_centers_mm:
        assert not plate.isInside(cq.Vector(x,-s.plate_thickness_mm/2,z),1e-4)
    assert feature_manifest(s)['screw_count']==count
    print('PASS geometry',name)

for mode in ('mouth','slide_in_t_head','none'):
    s=replace(PRESETS['4040_dual_4xM5'],tongue_mode=mode)
    assert bracket(s).intersect(reference_extrusion(s)).Volume()<.01
    print('PASS tongue mode',mode)
for s in (replace(MountSpec(),extrusion_size_mm=20,channel_count=2),
    replace(MountSpec(),longitudinal_screws_per_slot=1),
    replace(MountSpec(),screw_pitch_mm=12),
    replace(MountSpec(),tongue_projection_mm=2),
    replace(MountSpec(),fit_clearance_mm=-.1)):
    try: bracket(s)
    except ValueError: pass
    else:raise AssertionError('Invalid spec accepted: '+repr(s))

manifest=json.loads((ROOT/'docs'/'mount_interface_manifest.json').read_text())
metadata=json.loads((ROOT/'viewer'/'mount_interface_release.json').read_text())
assert set(manifest['variants'])==set(variants)-{'4040_single_2xM5'}
assert metadata['fully_offline']
assert len(manifest['previews'])==4
for name in manifest['variants']:
    step=ROOT/'step'/('MOUNT_'+name+'.step')
    stl=ROOT/'stl'/('MOUNT_'+name+'.stl')
    assert step.stat().st_size>15000 and stl.stat().st_size>1000
    mesh=trimesh.load_mesh(stl,force='mesh')
    assert mesh.is_watertight and mesh.is_volume and mesh.body_count==1
    assert abs(mesh.volume/bracket(PRESETS[name]).Volume()-1)<.006
readme=(ROOT/'README.md').read_text()
for path in manifest['previews']:
    image=ROOT/path
    content=image.read_bytes()
    assert content[:8]==b'\x89PNG\r\n\x1a\n'
    w,h=struct.unpack('>II',content[16:24])
    assert w>=1200 and h>=800
    assert f']({path})' in readme,path
html=(ROOT/'viewer'/'mount_interface.html').read_text()
assert 'Plotly.newPlot' in html
assert '<script src="https://cdn.' not in html
assert '4040_dual_8xM5' in html
print('PASS mount family: STEP, manifold STL, four real PNGs, offline viewer, README refs')
