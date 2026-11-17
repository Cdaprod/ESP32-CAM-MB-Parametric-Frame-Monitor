"""Single-source millimeter specification for the current CAD release."""
from dataclasses import dataclass

@dataclass(frozen=True)
class MonitorConfig:
    release: str = "V009"
    cable_diameter_mm: float = 3.2
    cable_outboard_x_mm: float = -27.0
    guide_bore_diameter_mm: float = 3.8
    guide_first_y_mm: float = -32.0
    guide_first_z_mm: float = 19.0
    guide_second_y_mm: float = -69.2
    guide_second_z_mm: float = 27.0
    guide_axial_length_mm: float = 3.5
    cable_to_knob_min_mm: float = 2.0
    cable_to_rail_min_mm: float = 1.5
    guide_centerline_tolerance_mm: float = 0.15
    sampled_poses: tuple = (
        (30,-30,12,0),(20,-30,12,-20),(20,-30,12,20),
        (40,-30,12,-20),(40,-30,12,20),
        (30,-40,12,-20),(30,-40,12,20),
        (30,-20,12,-20),(30,-20,12,20),
        (30,-30,0,-20),(30,-30,0,20),
        (30,-30,25,-20),(30,-30,25,20),
    )

CONFIG=MonitorConfig()
