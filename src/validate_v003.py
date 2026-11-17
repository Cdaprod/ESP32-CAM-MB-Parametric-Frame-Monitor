#!/usr/bin/env python3
"""V003 CAD checks. Inversion captured in six axial directions; no physical load claim."""
from __future__ import annotations
import json
import trimesh
from pathlib import Path
from dataclasses import asdict
from build_v003 import *


def run():
    allparts=assemble_components_v003()
    names={n:solid for n,solid,_,_ in allparts}
    assert len(allparts)==23
    report={'revision':'V003','test_kind':'Geometric BREP+STL, no physical testing',
            'component_count':len(allparts),'parts':{},'resting_collisions':{},
            'directions_blocked':{},'articulation':[],'hardware_fit':{},'limits':[]}
    for n,s,col,kind in allparts:
        assert s.isValid() and len(s.Solids())==1,(n,'BREP invalid')
        report['parts'][n]={'valid':True,'volume_mm3':round(s.Volume(),4),'type':kind}
    local_cradle,local_cap=new_parts_local()
    board=upstream.board_envelope_v002(V)
    arm=upstream.v002_swivel_arm(V)
    base=upstream.rail_base(V)
    for name,sa,sb in [('cradle_vs_board',local_cradle,board),
                       ('cap_vs_board',local_cap,board),
                       ('cradle_vs_cap',local_cradle,local_cap),
                       ('cradle_vs_arm',local_cradle,arm)]:
        iv=sa.intersect(sb).Volume()
        assert iv<0.005,(name,iv)
        report['resting_collisions'][name+'_mm3']=round(iv,5)
    # Explicit positive-volume obstacles against escape of the nominal board
    # envelope in each of the six principal translational directions.
    movements={'+Z (upside-down escape)':(0,0,3),'-Z (normal gravity)':(0,0,-4),
               '+Y (toward lens)':(0,2,0),'-Y (toward back panel)':(0,-2,0),
               '+X (right)':(2,0,0),'-X (left)':(-2,0,0)}
    for label,delta in movements.items():
        b=board.translate(delta)
        cradle_hit=local_cradle.intersect(b).Volume()
        retainer_hit=local_cap.intersect(b).Volume()
        assert max(cradle_hit,retainer_hit)>30,(label,cradle_hit,retainer_hit)
        report['directions_blocked'][label]={'tested_displacement_mm':max(abs(x) for x in delta),
             'cradle_blocking_volume_mm3':round(cradle_hit,3),
             'retainer_blocking_volume_mm3':round(retainer_hit,3)}
    # Mechanical anchoring: inserts and screws have clearance only in their
    # appropriate through holes; the nominal screws engage nominal insert bores.
    for side in (-1,1):
        x=side*C.insert_x
        ins=insert_envelope().translate((x,C.insert_y,C.insert_top_z-C.insert_length))
        screw=cap_screw().translate((x,C.insert_y,C.cap_z_base+C.cap_thickness))
        for label,p,q in [('insert_vs_cradle',ins,local_cradle),
                          ('insert_vs_cap',ins,local_cap),
                          ('screw_vs_cradle',screw,local_cradle),
                          ('screw_vs_cap',screw,local_cap),
                          ('screw_vs_insert',screw,ins)]:
            vol=p.intersect(q).Volume()
            if label=='insert_vs_cradle':
                # Heat-set insert OD intentionally exceeds printed pilot ID.
                # Softened polymer must flow around the selected real insert.
                assert 2.0 < vol < 15.0,(side,label,vol)
            else:
                assert vol<0.005,(side,label,vol)
            report['hardware_fit'][f'{side}_{label}_mm3']=round(vol,5)
    # Rotation of camera + cap about the pitch joint and yaw joint, comparing
    # against the unchanged arm/base and nominal board to validate working poses.
    for yaw in (-30,0,30):
        for pitch in (-15,0,15):
            def cam_pose(part):
                return part.rotate((0,-77,0),(1,-77,0),pitch).rotate((0,-17,0),(0,-17,1),yaw)
            cr=cam_pose(local_cradle); ca=cam_pose(local_cap); bo=cam_pose(board)
            ar=arm.rotate((0,-17,0),(0,-17,1),yaw)
            vals=[cr.intersect(bo).Volume(),ca.intersect(bo).Volume(),
                  cr.intersect(ca).Volume(),ar.intersect(cr).Volume(),base.intersect(ar).Volume()]
            assert max(vals)<.005,(yaw,pitch,vals)
            report['articulation'].append({'yaw_deg':yaw,'pitch_deg':pitch,
                  'max_unwanted_intersection_mm3':round(max(vals),6)})
    # Exhaustive print-parts watertight check on the five actual V003 print parts.
    printable=['V001_mount_base_4040_slot_10','V001_60mm_yaw_arm',
               'V5_profile_matched_key_M5_pilots','V003_anti_inversion_cradle',
               'V003_bolted_top_retainer']
    from build_v003 import upstream as u
    srcdict={'V001_mount_base_4040_slot_10':u.install(u.rail_base(V)),
           'V001_60mm_yaw_arm':u.install(u.pose_arm(u.v002_swivel_arm(V))),
           'V5_profile_matched_key_M5_pilots':u.original_key_with_m5_pilots(),
           'V003_anti_inversion_cradle':local_cradle,
           'V003_bolted_top_retainer':local_cap}
    for n in printable:
        path=ROOT/'stl'/f'{n}.stl';assert path.exists(),path
        mesh=trimesh.load(path,force='mesh')
        assert mesh.is_watertight and mesh.is_volume and mesh.body_count==1,n
        target=srcdict[n].Volume()
        delta=abs(mesh.volume/target-1)*100
        assert delta<.3,(n,delta)
        report['parts'][n]['watertight_stl']=True
        report['parts'][n]['volume_delta_percent']=round(delta,4)
    report['summary']={'status':'PASS - geometry only','BREP_solids':23,
        'printable_STLs_watertight':len(printable),
        'articulation_poses_passed':len(report['articulation']),
        'escape_axes_blocked':len(report['directions_blocked']),
        'board_to_top_retainer_gap_mm':C.nominal_camera_top_clearance}
    report['limits']=[
      'Board 27 x 40 x 16 mm envelope and exact components/connectors remain provisional.',
      'M2.5 heat-set inserts are schematic cylinders with intentional pilot interference; verify manufacturer hole/insert thermal spec before print.',
      'Simulated obstruction in six cardinal axes is not proof against all possible rotation paths or physical vibration.',
      '4040 slot source is recovered photo-derived geometry, not certified extrusion manufacturer STEP.',
      'M5x8 into printed undercut key remains demonstrator only; use qualified metal T-nut for actual printer mounting.',
      'No real load, drop, torque, vibration, thermal, or machine-travel tests performed.'
    ]
    (ROOT/'docs'/'validation_v003.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report['summary'],indent=2))
    return report
if __name__=='__main__':run()
