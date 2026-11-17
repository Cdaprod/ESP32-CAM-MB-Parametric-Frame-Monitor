"""Current route: one nominal 3.2mm cable reference across four moving joints.

Service loops and dynamic strain relief require real measurements and testing.
"""
import cadquery as cq
from . import parts as b4
from . import wrist as legacy
from .config import CONFIG

FIRST_ARM_ELBOW_ENTRY_OFFSET_X_MM=4.0


def path_points(wrist=0):
    x=CONFIG.cable_outboard_x_mm
    camera=(lambda s:legacy.pose_camera(s,wrist)) if hasattr(legacy,'pose_camera') else (lambda s:legacy.pose_cam(s,wrist))
    intermediate=legacy.pose_intermediate if hasattr(legacy,'pose_intermediate') else b4.pose_cam
    first=b4.pose_one
    second=b4.pose_two
    coords=[
      ((0,-104,1),camera),((0,-104,-1.5),camera),
      ((0,-120,-1.5),camera),((x,-120,-1.5),camera),
      ((x,-120,-28),camera),((x,-136,-28),camera),
      ((x,-140,-28),intermediate),((x,-116,-28),intermediate),
      ((x,-91,-27),intermediate),((x,-89,-27),second),
      ((x,-75,27),second),
      ((x,CONFIG.guide_second_y_mm,CONFIG.guide_second_z_mm),second),
      ((x,-56,27),second),
      ((x+FIRST_ARM_ELBOW_ENTRY_OFFSET_X_MM,-48,27),first),
      ((x,-35,19),first),
      ((x,CONFIG.guide_first_y_mm,CONFIG.guide_first_z_mm),first),
      ((x,-23,19),first),((x,-12,17),lambda s:s),((x,-4,16),lambda s:s)
    ]
    return [legacy._point(location,pose) for location,pose in coords]


def cable_reference(wrist=0):
    points=path_points(wrist)
    radius=CONFIG.cable_diameter_mm/2
    segments=[]
    for start,end in zip(points,points[1:]):
        delta=end-start
        if delta.Length>1e-5:
            segments.append(cq.Solid.makeCylinder(radius,delta.Length,start,delta.normalized()))
    return cq.Compound.makeCompound(segments)
