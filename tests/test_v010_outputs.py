"""V010 CAD release integrity: 18 poses, four solids, eight real renders."""
from pathlib import Path
import json,struct,csv
import trimesh

ROOT=Path(__file__).resolve().parents[1]
def required(name):
    p=ROOT/name
    assert p.is_file() and p.stat().st_size>0,name
    return p

assert required('VERSION').read_text().strip()=='V010'
release=json.loads(required('docs/CURRENT_RELEASE.json').read_text())
assert release['release']=='V010' and release['is_current']
manifest=json.loads(required('docs/manifest_v010.json').read_text())
report=json.loads(required('docs/validation_v010.json').read_text())
s=report['summary']
assert manifest['revision']==s['revision']=='V010'
assert manifest['component_count']==len(manifest['components'])==30
assert s['status']=='PASS CAD-only' and s['sampled_poses']==len(report['poses'])==18
assert s['integrated_alternating_open_clips']==4 and s['long_outriggers']==0
assert s['watertight_new_stls']==4
assert s['watertight_print_designs']==len(report['printable_meshes'])==8
assert s['min_cable_to_knob_mm']>=1.0, 'Cable clearance regressed under new embedded-channel routing'
assert s['min_cable_to_knob_mm']>=1.0 and s['min_cable_to_rail_mm']>3.0
assert report['clip_openings_in_order']==['-X','+Z','-X','+Z']
assert required(release['assembly_step']).stat().st_size>100_000
for stl in release['new_stls']:
    mesh=trimesh.load(required(stl),force='mesh')
    assert mesh.is_watertight and mesh.is_volume and mesh.body_count==1,stl
    required(stl.replace('stl/','step/').replace('.stl','.step'))
readme=required('README.md').read_text()
assert len(release['previews'])==8
for image in release['previews']:
    b=required(image).read_bytes()
    assert f']({image})' in readme,image
    assert b[:8]==b'\x89PNG\r\n\x1a\n',image
    w,h=struct.unpack('>II',b[16:24])
    assert w>=1200 and h>=800,image
assert required('docs/BOM.csv').read_bytes()==required('docs/BOM_V010.csv').read_bytes()
with required('docs/BOM.csv').open(newline='') as f:rows=list(csv.DictReader(f))
assert rows and all(row['revision']=='V010' for row in rows)
required('previews/v009_full_assembly.png')
print('PASS V010: four watertight STLs, 18 pose checks, eight embedded real PNGs, STEP, BOM')
