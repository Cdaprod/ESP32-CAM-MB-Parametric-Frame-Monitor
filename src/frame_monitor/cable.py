"""V010 nominal four-joint cable path through four moving link-local U clips.

Reference only: not a flexible cable, force, strain or bend-radius simulation.
"""
import cadquery as cq
from . import parts as b4
from . import wrist as legacy
from .config import CONFIG

def path_points(wrist=0):
    x=CONFIG.first_cable_x_mm
    x2=CONFIG.second_cable_x_mm
    camera=lambda s:legacy.pose_camera(s,wrist) if hasattr(legacy,'pose_camera') else legacy.pose_cam(s,wrist)
    intermediate=legacy.pose_intermediate if hasattr(legacy,'pose_intermediate') else b4.pose_cam
    first=b4.pose_one
    second=b4.pose_two
    coords=[
      ((0,-104,1),camera),((0,-104,-1.5),camera),
      ((0,-120,-1.5),camera),((-27,-120,-1.5),camera),
      ((-27,-120,-28),camera),((-27,-136,-28),camera),
      ((-27,-140,-28),intermediate),((-27,-116,-28),intermediate),
      ((-27,-91,-27),intermediate),((-27,-89,-27),second),
      ((-27,-87,CONFIG.second_cable_z_mm),second),
      ((x2,-82,CONFIG.second_cable_z_mm),second),
      ((x2,-78,CONFIG.second_cable_z_mm),second),
      ((x2,CONFIG.second_clip_y_mm[1],CONFIG.second_cable_z_mm),second),
      ((x2,CONFIG.second_clip_y_mm[0],CONFIG.second_cable_z_mm),second),
      ((x2,-58,CONFIG.second_cable_z_mm),second),
      ((-27,-54,CONFIG.second_cable_z_mm),second),
      ((-27,-48,CONFIG.first_cable_z_mm),first),
      ((x,-44,CONFIG.first_cable_z_mm),first),
      ((x,CONFIG.first_clip_y_mm[1],CONFIG.first_cable_z_mm),first),
      ((x,CONFIG.first_clip_y_mm[0],CONFIG.first_cable_z_mm),first),
      ((x,-23,CONFIG.first_cable_z_mm),first),
      ((-27,-17,CONFIG.first_cable_z_mm),first),
      ((-27,-12,17),lambda s:s),((-27,-4,16),lambda s:s)
    ]
    return [legacy._point(point,pose) for point,pose in coords]

def cable_reference(wrist=0):
    points=path_points(wrist)
    radius=CONFIG.cable_diameter_mm/2
    segments=[]
    for start,end in zip(points,points[1:]):
        delta=end-start
        if delta.Length>1e-5:
            segments.append(cq.Solid.makeCylinder(radius,delta.Length,start,delta.normalized()))
    return cq.Compound.makeCompound(segments)
