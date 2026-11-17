"""Geometric regression: articulated cable, no x=-27 legacy guides."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from frame_monitor import parts
from frame_monitor.cable import route_nodes,path_points,rounded_centerline,cable_reference,route_metrics
from frame_monitor.config import CONFIG as C
old=(parts.P.yaw_deg,parts.P.elbow_deg,parts.P.camera_pitch_deg)
try:
    for angles in ((30,-30,12,0),(20,-40,25,-20),(40,-20,0,20)):
        for key,angle in zip(("yaw_deg","elbow_deg","camera_pitch_deg"),angles[:3]):
            object.__setattr__(parts.P,key,angle)
        nodes=route_nodes(angles[3])
        assert len(nodes)==25
        assert all(abs(xyz[0]+27)>1e-9 for xyz,frame,label in nodes)
        line,arcs=rounded_centerline(path_points(angles[3]))
        assert line.isValid() and len(arcs)>=8
        assert min(a["radius_mm"] for a in arcs)>=C.cable_reference_min_radius_mm
        assert any(e.geomType()=="CIRCLE" for e in line.Edges())
        tube=cable_reference(angles[3])
        assert tube.isValid() and len(tube.Solids())==1
        print("PASS",angles,route_metrics(angles[3]))
finally:
    for key,value in zip(("yaw_deg","elbow_deg","camera_pitch_deg"),old):
        object.__setattr__(parts.P,key,value)
