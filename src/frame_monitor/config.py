"""Single-source millimeter specification for the current CAD release."""
from dataclasses import dataclass

@dataclass(frozen=True)
class MonitorConfig:
    release: str = "V010"
    cable_diameter_mm: float = 3.2
    clip_bore_mm: float = 3.8
    clip_outer_radius_mm: float = 3.55
    clip_width_mm: float = 3.6
    clip_throat_mm: float = 2.65
    first_cable_x_mm: float = -9.5
    first_cable_z_mm: float = 10.25
    second_cable_x_mm: float = -9.5
    second_cable_z_mm: float = 17.75
    first_clip_y_mm: tuple = (-32.5,-37.7)
    second_clip_y_mm: tuple = (-66.0,-72.0)
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
