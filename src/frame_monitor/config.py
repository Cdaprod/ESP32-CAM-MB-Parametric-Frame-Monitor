"""Single-source millimeter specification for the current CAD release."""
from dataclasses import dataclass

@dataclass(frozen=True)
class MonitorConfig:
    release: str = "V010"
    cable_diameter_mm: float = 3.2
    clip_bore_mm: float = 3.8
    clip_outer_radius_mm: float = 3.55
    clip_width_mm: float = 3.6
    clip_throat_mm: float = 3.0
    first_cable_x_mm: float = -9.5
    first_cable_z_mm: float = 10.25
    second_cable_x_mm: float = -9.5
    second_cable_z_mm: float = 17.75
    first_clip_y_mm: tuple = (-32.5,-37.7)
    second_clip_y_mm: tuple = (-66.0,-72.0)
    # All cable-routing dimensions are nominal, not measured jacket properties.
    cable_exit_xyz_mm: tuple = (0.0, -104.0, 1.0)
    cable_exit_drop_mm: float = 10.0
    cable_camera_outboard_x_mm: float = -22.0
    cable_joint_outboard_x_mm: float = -20.0
    cable_wrist_loop_outboard_x_mm: float = -30.0
    cable_wrist_loop_reach_mm: float = 10.0
    cable_pitch_transition_z_mm: float = -24.0
    cable_riser_lower_z_mm: float = -20.0
    cable_bend_radius_mm: float = 6.0
    cable_bend_cutback_fraction: float = 0.42
    cable_reference_min_radius_mm: float = 1.6
    cable_to_knob_min_mm: float = 1.0
    cable_to_rail_min_mm: float = 1.2
    sampled_poses: tuple = (
        (30,-30,12,0),(20,-30,12,-20),(20,-30,12,20),
        (40,-30,12,-20),(40,-30,12,20),
        (30,-40,12,-20),(30,-40,12,20),
        (30,-20,12,-20),(30,-20,12,20),
        (30,-30,0,-20),(30,-30,0,20),
        (30,-30,25,-20),(30,-30,25,20),
        (20,-20,0,-20),(40,-40,25,20),(20,-40,25,-20),
        (40,-20,0,20),(30,-20,25,0),
    )

CONFIG=MonitorConfig()
