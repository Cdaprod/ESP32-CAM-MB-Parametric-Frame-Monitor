#!/usr/bin/env python3
"""V005 — left-side over-rail camera mount for a horizontal 4040 extrusion.

Reuses V004 solids/hardware unchanged. Coordinates (mm):
  rail longitudinal X, extrusion cross-section Y/Z +/-20;
  world +Y is LEFT/OUTSIDE of machine, -Y is inward toward the print bed;
  world +Z is up; assembly mounted flush to Y=+20 rail face.
  Active undercut slot is at Z=+10, one of the two genuine 4040 slots.
  Camera optical axis crosses toward -Y with a >7mm rail-top clearance.

This is a *CAD layout demonstrator*, not a measured machine installation.
"""
from __future__ import annotations
import json
from pathlib import Path
from dataclasses import asdict,dataclass
import cadquery as cq
import build_v004 as base

ROOT=Path(__file__).resolve().parents[1]

@dataclass(frozen=True)
class Pose:
    side_rotation_deg:float=90.0  # V004 bottom mount (-Z) -> V005 left face (+Y)
    yaw_deg:float=30.0
    elbow_deg:float=-30.0
    camera_pitch_deg:float=12.0
    rail_top_z:float=20.0
    rail_left_face_y:float=20.0
    nominal_raycast_clearance_min_mm:float=5.0
    aiming_depth_y_mm:float=-100.0

P=Pose()

def left_side(s):
    """The *extrusion stays horizontal and unrotated*; installed components roll around X."""
    return s.rotate((0,0,0),(1,0,0),P.side_rotation_deg)

def components():
    old=(base.P.yaw_deg,base.P.elbow_deg,base.P.camera_pitch_deg)
    try:
        object.__setattr__(base.P,'yaw_deg',P.yaw_deg)
        object.__setattr__(base.P,'elbow_deg',P.elbow_deg)
        object.__setattr__(base.P,'camera_pitch_deg',P.camera_pitch_deg)
        originals=base.components()
    finally:
        for key,val in zip(('yaw_deg','elbow_deg','camera_pitch_deg'),old):
            object.__setattr__(base.P,key,val)
    return [(name,solid if name=='4040_horizontal_reference' else left_side(solid),rgb,kind)
            for name,solid,rgb,kind in originals]

def aim_geometry():
    """Two local points a millimetre apart along the modeled lens forward (+Y) axis."""
    old=(base.P.yaw_deg,base.P.elbow_deg,base.P.camera_pitch_deg)
    try:
        object.__setattr__(base.P,'yaw_deg',P.yaw_deg)
        object.__setattr__(base.P,'elbow_deg',P.elbow_deg)
        object.__setattr__(base.P,'camera_pitch_deg',P.camera_pitch_deg)
        def point(t):
            v=cq.Vertex.makeVertex(*t)
            return left_side(base.horizontal(base.b.install(base.pose_cam(v)))).Center()
        front=point((0,-95,29)); toward=point((0,-94,29))
    finally:
        for key,val in zip(('yaw_deg','elbow_deg','camera_pitch_deg'),old):
            object.__setattr__(base.P,key,val)
    direction=toward-front
    assert direction.y < -0.75, 'camera is not aimed into the bed (-Y)'
    def at_y(y):
        k=(y-front.y)/direction.y
        return front+direction.multiply(k)
    rail_entry=at_y(20)
    rail_exit=at_y(-20)
    bed=at_y(P.aiming_depth_y_mm)
    return {'lens_xyz_mm':list(front.toTuple()),'aim_vector':list(direction.toTuple()),
            'rail_left_face_y_20_xyz_mm':list(rail_entry.toTuple()),
            'rail_right_face_y_minus20_xyz_mm':list(rail_exit.toTuple()),
            'target_y_minus100_xyz_mm':list(bed.toTuple()),
            'clearance_above_rail_at_near_face_mm':rail_entry.z-P.rail_top_z,
            'clearance_above_rail_at_far_face_mm':rail_exit.z-P.rail_top_z}

def build():
    (ROOT/'step').mkdir(parents=True,exist_ok=True)
    (ROOT/'docs').mkdir(parents=True,exist_ok=True)
    pieces=components()
    assembly=cq.Assembly(name='ESP32_CAM_MB_LEFT_SIDE_OVER_RAIL_V005')
    for name,shape,rgb,kind in pieces:
        assert shape.isValid(), f'invalid part: {name}'
        assembly.add(shape,name=name,color=cq.Color(*rgb))
    out=ROOT/'step'/'COMPLETE_4040_ESP32_CAM_MB_ASSEMBLY_V005.step'
    assembly.save(str(out),exportType='STEP')
    aim=aim_geometry()
    document={'revision':'V005','inherits':'V004, all 7 printable geometry exports unchanged',
              'pose':asdict(P),'convention':'+Y = LEFT/OUTSIDE; -Y = BED/INBOARD; +Z = UP',
              'rail_axis':'X (horizontal)','mount_face':'+Y face at Y=20 mm','active_slot':'Z=+10 mm',
              'aim':aim,'component_count':len(pieces),
              'limitations':['Physical printer face availability and travel envelope not verified',
                             'Camera, rail profile and USB connector remain nominal',
                             'Aiming ray only represents nominal lens center; field of view is not optically simulated',
                             'No tightening torque, vibration, thermal, or actual line-of-sight measurements']}
    (ROOT/'docs'/'manifest_v005.json').write_text(json.dumps(document,indent=2))
    print('V005 assembly',len(pieces),'components;',out.stat().st_size,'bytes; clearance',round(aim['clearance_above_rail_at_near_face_mm'],2),'mm')
    return pieces

if __name__=='__main__':build()
