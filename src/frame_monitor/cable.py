"""Continuous parametric cable reference with tangent circular arcs.

Geometry depends on the moving frames of all four joints. A drawn radius is
NOT a manufacturer-specified minimum bend radius or cable-flex validation.
"""
from __future__ import annotations
import math
import cadquery as cq
from . import parts as b4
from . import wrist
from .config import CONFIG as C


def route_nodes(wrist_angle=0):
    """(local XYZ, pose transform, purpose); no obsolete x=-27 anchors."""
    camera = lambda solid: wrist.pose_cam(solid, wrist_angle)
    intermediate = b4.pose_cam
    first, second = b4.pose_one, b4.pose_two
    fixed = lambda solid: solid
    ex, ey, ez = C.cable_exit_xyz_mm
    drop = ez-C.cable_exit_drop_mm
    xw, xj, xl = (C.cable_camera_outboard_x_mm,
                   C.cable_joint_outboard_x_mm,
                   C.cable_wrist_loop_outboard_x_mm)
    yw = wrist.S.wrist_y_mm
    yp, ye, yb = b4.P.camera_pivot_y, b4.P.elbow_pivot_y, b4.P.first_pivot_y
    x2,z2 = C.second_cable_x_mm,C.second_cable_z_mm
    x1,z1 = C.first_cable_x_mm,C.first_cable_z_mm
    zlow = C.cable_pitch_transition_z_mm
    return [
      ((ex,ey,ez),camera,"provisional connector exit"),
      ((ex,ey,drop),camera,"downward connector strain zone"),
      ((ex-8,ey-4,drop-5),camera,"under-shell arc"),
      ((xw+1,ey-15,drop-9),camera,"shell underside"),
      ((xw,yw,drop-10),camera,"wrist approach"),
      ((xw+1,yw-6,drop-16),camera,"wrist service loop A"),
      ((xl+1,yw-C.cable_wrist_loop_reach_mm-4,zlow-6),intermediate,"wrist service loop B"),
      ((xl-5,yw+7,zlow-3),intermediate,"wrist adapter"),
      ((xj,yw+30,zlow),intermediate,"pitch approach"),
      ((xj,yp-4,zlow+1),intermediate,"pitch slack"),
      ((xj,yp,C.cable_riser_lower_z_mm),second,"pitch return"),
      ((xj,yp,z2),second,"vertical riser"),
      ((x2,yp+7,z2),second,"second channel entry"),
      ((x2,C.second_clip_y_mm[1],z2),second,"second clip A"),
      ((x2,C.second_clip_y_mm[0],z2),second,"second clip B"),
      ((x2,ye-7,z2),second,"second channel exit"),
      ((xj,ye,z2),second,"elbow approach"),
      ((xj,ye+6,z1),first,"elbow return"),
      ((x1,ye+8,z1),first,"first channel entry"),
      ((x1,C.first_clip_y_mm[1],z1),first,"first clip A"),
      ((x1,C.first_clip_y_mm[0],z1),first,"first clip B"),
      ((x1,yb-7,z1),first,"first channel exit"),
      ((xj,yb,z1),first,"base transition"),
      ((xj,yb+7,z1),fixed,"fixed-frame approach"),
      ((xj,yb+13,z1+1.75),fixed,"fixed-frame endpoint")]


def path_points(wrist_angle=0):
    return [wrist._point(xyz,pose) for xyz,pose,_ in route_nodes(wrist_angle)]


def rounded_centerline(points):
    """Lines plus exact C1 tangent arcs with bounded tangent setback.

    For turn theta, setback=d=r*tan(theta/2); cap d against both adjacent
    legs to prevent neighbouring fillets overlapping. Reject hairpins or
    degenerate tube bends rather than drawing an impossible sharp cable.
    """
    pts=[p if isinstance(p,cq.Vector) else cq.Vector(*p) for p in points]
    if len(pts)<2 or C.cable_bend_radius_mm<=0:
        raise ValueError("Invalid cable anchors or radius")
    edges=[]
    bends=[]
    cursor=pts[0]
    for i in range(1,len(pts)-1):
        a=pts[i]-pts[i-1]
        b=pts[i+1]-pts[i]
        la,lb=a.Length,b.Length
        if min(la,lb)<1e-5: raise ValueError(f"Duplicate cable anchor {i}")
        a,b=a.normalized(),b.normalized()
        theta=math.acos(max(-1.0,min(1.0,a.dot(b))))
        if theta<1e-4: continue
        if theta>math.radians(170): raise ValueError(f"Hairpin at cable anchor {i}")
        tangent=math.tan(theta/2)
        r=min(C.cable_bend_radius_mm,
              C.cable_bend_cutback_fraction*min(la,lb)/tangent)
        if r<C.cable_reference_min_radius_mm:
            raise ValueError(f"Fillet radius {r:.3f} below reference guard at {i}")
        d=r*tangent
        entrance,exit=pts[i]-a*d,pts[i]+b*d
        center=pts[i]+(b-a).normalized()*r/math.cos(theta/2)
        mid=center+(pts[i]-center).normalized()*r
        if (entrance-cursor).Length>1e-6:
            edges.append(cq.Edge.makeLine(cursor,entrance))
        edges.append(cq.Edge.makeThreePointArc(entrance,mid,exit))
        bends.append({"anchor":i,"radius_mm":round(r,4),
                      "angle_deg":round(math.degrees(theta),2)})
        cursor=exit
    if (pts[-1]-cursor).Length>1e-6:
        edges.append(cq.Edge.makeLine(cursor,pts[-1]))
    wire=cq.Wire.assembleEdges(edges)
    if not wire.isValid(): raise ValueError("Invalid cable centerline")
    return wire,bends


def route_metrics(wrist_angle=0, *, base=None, elbow=None, pitch=None):
    """Measure the **same kinematic pose** used to construct cable geometry.

    The legacy transform functions use mutable b4.P. All overrides are
    temporary, so this function is safe to call after assembly.components()
    resets its own pose context.
    """
    names=("yaw_deg","elbow_deg","camera_pitch_deg")
    old=tuple(getattr(b4.P,key) for key in names)
    try:
        for key,value in zip(names,(base,elbow,pitch)):
            if value is not None:
                object.__setattr__(b4.P,key,value)
        wire,arcs=rounded_centerline(path_points(wrist_angle))
        return {"length_mm":round(wire.Length(),3),"arc_count":len(arcs),
                "minimum_drawn_radius_mm":min((a["radius_mm"] for a in arcs),default=None),
                "requested_drawn_radius_mm":C.cable_bend_radius_mm,
                "physical_cable_qualification":"UNVERIFIED"}
    finally:
        for key,value in zip(names,old):
            object.__setattr__(b4.P,key,value)


def cable_reference(wrist_angle=0):
    """Single circular-section BREP swept along articulated tangent arcs."""
    points=path_points(wrist_angle)
    wire,_=rounded_centerline(points)
    plane=cq.Plane(origin=points[0],normal=points[1]-points[0])
    shape=cq.Workplane(plane).circle(C.cable_diameter_mm/2).sweep(
        wire,isFrenet=False).val()
    if not shape.isValid() or len(shape.Solids())!=1:
        raise ValueError("Invalid smoothly swept cable")
    return shape
