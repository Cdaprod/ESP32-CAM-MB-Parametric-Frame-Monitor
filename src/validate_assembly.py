#!/usr/bin/env python3
"""Geometric validation for 4040 parametric monitor V002. Mechanical strength not tested."""
import json
from pathlib import Path
import sys
import trimesh
from build_assembly import *

def validate():
    comps=assemble_components();d={n:solid for n,solid,_,_ in comps}
    report={'summary':{},'parts':{},'clearance_checks':{},'articulation':[],'limitations':[]}
    assert len(comps)==18
    for n,shape,_,kind in comps:
        assert shape.isValid(),n
        report['parts'][n]={'brep_valid':True,'volume_mm3':round(shape.Volume(),3)}
    for file in sorted((ROOT/'stl').glob('*.stl')):
        mesh=trimesh.load(file,force='mesh')
        assert mesh.is_volume and mesh.is_watertight and mesh.body_count==1,file.name
        report['parts'][file.stem]['stl_watertight']=True
        report['parts'][file.stem]['stl_body_count']=mesh.body_count
        v=d[file.stem].Volume()
        assert abs(mesh.volume/v-1)<.003,(file.stem,mesh.volume,v)
        report['parts'][file.stem]['mesh_volume_delta_pct']=round((mesh.volume/v-1)*100,4)
    def check(a,b,limit=.01):
        vol=d[a].intersect(d[b]).Volume();assert vol<limit,(a,b,vol)
        report['clearance_checks'][f'{a} vs {b}']=round(vol,5)
    check('4040_reference_extrusion','V5_profile_matched_key_M5_pilots')
    check('4040_reference_extrusion','V001_mount_base_4040_slot_10')
    check('V001_mount_base_4040_slot_10','V001_60mm_yaw_arm')
    check('V001_60mm_yaw_arm','V001_camera_tilt_cradle')
    check('V001_camera_tilt_cradle','ESP32_CAM_MB_nominal_envelope')
    for name in ('M5x8_socket_screw_1','M5x8_socket_screw_2'):
        check('4040_reference_extrusion',name)
        key_eng=d['V5_profile_matched_key_M5_pilots'].intersect(d[name]).Volume()
        # This intersection reflects nominal M5 shaft against 4.2 mm plastic tap pilot.
        assert key_eng>1.0
        report['clearance_checks'][f'{name} vs key pilot (intentional tap engagement mm3)']=round(key_eng,3)
    # Articulation at nine yaw/pitch pairs using V002 corrected hinge & board positions.
    for yaw in (-30,0,30):
      for pitch in (-15,0,15):
        arm=v002_swivel_arm(V).rotate((0,-17,0),(0,-17,1),yaw)
        cradle=(v002_camera_cradle(V).rotate((0,-77,0),(1,-77,0),pitch)
                  .rotate((0,-17,0),(0,-17,1),yaw))
        board=(board_envelope_v002(V).rotate((0,-77,0),(1,-77,0),pitch)
               .rotate((0,-17,0),(0,-17,1),yaw))
        base=rail_base(V)
        vals=[base.intersect(arm).Volume(),arm.intersect(cradle).Volume(),cradle.intersect(board).Volume()]
        assert all(v<.01 for v in vals),(yaw,pitch,vals)
        report['articulation'].append({'yaw_deg':yaw,'pitch_deg':pitch,'max_printed_part_or_camera_intersection_mm3':round(max(vals),5)})
    report['summary']={'assembly_components':len(comps),'printable_stls_checked':len(list((ROOT/'stl').glob('*.stl'))),
        'poses_tested':len(report['articulation']),'status':'PASS - geometric checks only'}
    report['limitations']=[
      'Recovered 4040 photo-derived profile is not manufacturer-verified.',
      'M5 holes in printed key are 4.2mm nominal tap pilots; modelled screw shanks intentionally interfere with pilots (no helical threads).',
      'Thread load strength of plastic key not certified; for operational service prefer metal T-nuts or a tested metal captive fastener.',
      'Simplified ESP32-CAM-MB envelope, no exact USB-port or component clearances.',
      'A frame-specific machine clearance / moving bed travel sweep has not been performed.',
      'Screw heads/nut hexes/washer bodies are simplified reference representations, not fastener supplier STEP models.',
    ]
    outfile=ROOT/'docs'/'validation.json'
    outfile.write_text(json.dumps(report,indent=2))
    print(json.dumps(report['summary'],indent=2))
if __name__=='__main__':validate()
