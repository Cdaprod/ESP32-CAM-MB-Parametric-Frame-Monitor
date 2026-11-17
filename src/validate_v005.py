#!/usr/bin/env python3
"""V005 CAD-only verification: left-side mount and over-rail sightline."""
from __future__ import annotations
import json
import build_v005 as v

def validate():
    parts = v.components()
    d = {n:s for n,s,_,_ in parts}
    assert len(parts) == 26 and len(d) == len(parts)
    assert all(s.isValid() for _,s,_,_ in parts)
    rail = d["4040_horizontal_reference"]
    targets = ["V004_mount_plate","V004_first_arm","V004_second_arm",
               "V004_full_sidewall_camera_shell","V004_removable_camera_bezel",
               "ESP32_CAM_MB_provisional_envelope"]
    rail_interference = {}
    for n in targets:
        volume = rail.intersect(d[n]).Volume()
        assert volume < 0.01, (n,volume)
        rail_interference[n] = round(volume,5)
    pairs = [("V004_mount_plate","V004_first_arm"),
             ("V004_first_arm","V004_second_arm"),
             ("V004_second_arm","V004_full_sidewall_camera_shell"),
             ("V004_full_sidewall_camera_shell","V004_removable_camera_bezel"),
             ("V004_full_sidewall_camera_shell","ESP32_CAM_MB_provisional_envelope"),
             ("V004_removable_camera_bezel","ESP32_CAM_MB_provisional_envelope")]
    part_interference = {}
    for a,b in pairs:
        volume = d[a].intersect(d[b]).Volume()
        assert volume < 0.01, (a,b,volume)
        part_interference[a + " / " + b] = round(volume,5)
    mount = d["V004_mount_plate"].BoundingBox()
    assert abs(mount.ymin-20.0) < 1e-4
    assert abs(rail.BoundingBox().xlen-180.0) < 1e-4
    for n in ("V004_recessed_alignment_key","M5_metal_tnut_left","M5_metal_tnut_right"):
        assert abs(d[n].BoundingBox().ymax-19.35)<0.01, n
    ray = v.aim_geometry()
    assert ray["clearance_above_rail_at_near_face_mm"] > v.P.nominal_raycast_clearance_min_mm
    assert ray["clearance_above_rail_at_far_face_mm"] > v.P.nominal_raycast_clearance_min_mm
    assert ray["target_y_minus100_xyz_mm"][1] < 0.0
    report = {"revision":"V005","status":"PASS CAD-only",
              "component_count":len(parts),"printable_geometry_changes":0,
              "rail_interference_mm3":rail_interference,
              "part_pair_interference_mm3":part_interference,
              "optical_ray":ray,"physical_fit":"NOT VERIFIED"}
    path = v.ROOT/"docs"/"validation_v005.json"
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,indent=2))
    print(json.dumps({"status":report["status"],"components":len(parts),
                      "rail_top_clearance_mm":round(ray["clearance_above_rail_at_near_face_mm"],3)},indent=2))
    return report

if __name__ == "__main__":
    validate()
