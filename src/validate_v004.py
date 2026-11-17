#!/usr/bin/env python3
"""V004 geometric acceptance. Does not certify physical fit, torque, vibration or cable bend radius."""
import json,itertools
from pathlib import Path
import trimesh
import build_v004 as v

def run():
    root=v.ROOT
    local,assembled=v.build()
    report={'revision':'V004','scope':'CAD-only geometric checks; physical testing outstanding',
            'key_recess_mm':round(20-v.alignment_key().BoundingBox().xmax,4),
            'metal_tnut_recess_mm':round(20-v.steel_tnut(15).BoundingBox().xmax,4),
            'stls':{},'collision_clearance_mm3':{},'retention_axes':{},'articulation':[]}
    assert abs(report['key_recess_mm']-v.P.face_key_recess)<.001
    assert abs(report['metal_tnut_recess_mm']-v.P.face_key_recess)<.001
    solids={name:s for name,s,_,_ in assembled}
    for a,b in [('4040_horizontal_reference','V004_recessed_alignment_key'),
                ('4040_horizontal_reference','M5_metal_tnut_left'),
                ('4040_horizontal_reference','M5_metal_tnut_right'),
                ('4040_horizontal_reference','V004_mount_plate'),
                ('V004_mount_plate','V004_first_arm'),
                ('V004_first_arm','V004_second_arm'),
                ('V004_second_arm','V004_full_sidewall_camera_shell'),
                ('V004_full_sidewall_camera_shell','V004_removable_camera_bezel'),
                ('V004_full_sidewall_camera_shell','ESP32_CAM_MB_provisional_envelope'),
                ('V004_removable_camera_bezel','ESP32_CAM_MB_provisional_envelope'),
                ('M4_thumbwheel_camera_tilt','V004_full_sidewall_camera_shell')]:
        vol=solids[a].intersect(solids[b]).Volume()
        assert vol<.01,(a,b,vol)
        report['collision_clearance_mm3'][f'{a} | {b}']=round(vol,5)
    # The enclosure physically blocks x+/- and z+/- with top/bottom walls.
    # Front bezel blocks Y+; rear shell blocks Y-. This is NOT drop testing.
    shell=v.camera_shell();bezel=v.camera_bezel();board=v.board_envelope()
    for key,delta in {'+X':(5,0,0),'-X':(-5,0,0),'+Y':(0,8,0),'-Y':(0,-5,0),'+Z':(0,0,5),'-Z':(0,0,-5)}.items():
        moved=board.translate(delta)
        iv=shell.intersect(moved).Volume()+bezel.intersect(moved).Volume()
        report['retention_axes'][key]=round(iv,2)
        assert iv>5,(key,iv)
    for n,sh in local.items():
        path=root/'stl'/f'{n}.stl'
        mesh=trimesh.load(path,force='mesh')
        assert mesh.is_watertight and mesh.is_volume and mesh.body_count==1,(n,'mesh invalid')
        delta=abs(mesh.volume/sh.Volume()-1)*100
        assert delta<0.5,(n,delta)
        report['stls'][n]={'watertight':True,'single_body':True,'volume_error_percent':round(delta,4)}
    # Negative pitch is prohibited because the housing hits arm two; do not
    # advertise unrestricted +/- travel. Verified sample range: 0..30 degrees.
    for yaw,elbow,pitch in itertools.product((-25,0,25),(-30,0,30),(0,15,30)):
        object.__setattr__(v.P,'yaw_deg',yaw)
        object.__setattr__(v.P,'elbow_deg',elbow)
        object.__setattr__(v.P,'camera_pitch_deg',pitch)
        a=v.pose_one(v.arm_one());aa=v.pose_two(v.arm_two());
        shell=v.pose_cam(v.camera_shell());bez=v.pose_cam(v.camera_bezel());board=v.pose_cam(v.board_envelope())
        collisions=[a.intersect(aa).Volume(),aa.intersect(shell).Volume(),
                    a.intersect(shell).Volume(),shell.intersect(bez).Volume(),
                    shell.intersect(board).Volume(),bez.intersect(board).Volume()]
        assert max(collisions)<.01,(yaw,elbow,pitch,collisions)
        report['articulation'].append({'base_deg':yaw,'elbow_deg':elbow,'pitch_deg':pitch,
                                       'max_interference_mm3':round(max(collisions),4)})
    report['summary']={'status':'PASS CAD-only','components':len(assembled),
                       'printable_models':len(local),'tested_poses':len(report['articulation']),
                       'blocked_translation_directions':6}
    report['known_limits']=['Provisional camera stack and non-certified 4040 profile',
                            'Cable route is schematic; real USB connector fit and bend radius untested',
                            'Camera pitch range currently 0..30deg only; negative tilt hits support',
                            'Metal hardware depicted without real threads; captive hex pockets need fit tests',
                            'No physical torque/vibration/thermal/travel/load validation']
    path=root/'docs'/'validation_v004.json'
    path.write_text(json.dumps(report,indent=2))
    print(json.dumps(report['summary'],indent=2))
    return report
if __name__=='__main__':run()
