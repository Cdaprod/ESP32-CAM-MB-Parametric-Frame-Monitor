"""Parametric metal-T-nut extrusion bracket; all dimensions in millimetres.

Local axes: X across rail face, Y normal into extrusion (+Y), Z along rail.
The plate occupies -thickness <= Y <= 0; integral locating ribs enter Y > 0.
Old loose V5 key must not be used with this integrated-tongue family.
Physical clearance/print strength are not qualified.
"""
from dataclasses import dataclass, asdict, replace
from math import sqrt
import cadquery as cq

@dataclass(frozen=True)
class MountSpec:
    extrusion_size_mm: int = 40
    channel_count: int = 2
    selected_4040_slot: int = 1
    longitudinal_screws_per_slot: int = 2
    screw_pitch_mm: float = 30.0
    axial_end_margin_mm: float = 12.0
    transverse_edge_margin_mm: float = 9.0
    plate_thickness_mm: float = 6.0
    corner_radius_mm: float = 1.5
    screw_clearance_diameter_mm: float = 5.4
    counterbore_diameter_mm: float = 9.0
    counterbore_depth_mm: float = 3.0
    nominal_tnut_length_mm: float = 9.0
    tnut_axial_clearance_mm: float = 2.0
    tongue_mode: str = 'mouth' # mouth, slide_in_t_head, none
    tongue_projection_mm: float = 1.0
    slot_mouth_mm: float = 6.2
    slot_lip_depth_mm: float = 1.5
    slot_head_width_mm: float = 10.5
    slot_head_flat_end_mm: float = 3.5
    slot_inner_flat_mm: float = 5.0
    slot_depth_mm: float = 6.8
    fit_clearance_mm: float = .18
    bridge_reach_mm: float = 11.5
    bridge_width_mm: float = 17.0
    bridge_height_mm: float = 12.0
    pivot_y_mm: float = -17.0
    pivot_outer_radius_mm: float = 9.0
    pivot_hole_diameter_mm: float = 4.3
    captive_nut_across_flats_mm: float = 7.2
    captive_nut_depth_mm: float = 3.2
    structural_gusset_width_mm: float = 2.4

    @property
    def slot_centers_mm(self):
        if self.extrusion_size_mm==20 or self.channel_count==1: return (0.0,)
        return (-10.0,10.0)
    @property
    def reference_rail_shift_mm(self):
        return -10*self.selected_4040_slot if self.extrusion_size_mm==40 and self.channel_count==1 else 0.0
    @property
    def plate_width_mm(self):
        return max(self.slot_centers_mm)-min(self.slot_centers_mm)+2*self.transverse_edge_margin_mm
    @property
    def plate_length_mm(self):
        return (self.longitudinal_screws_per_slot-1)*self.screw_pitch_mm+2*self.axial_end_margin_mm
    @property
    def stations_mm(self):
        n=self.longitudinal_screws_per_slot
        return tuple((i-(n-1)/2)*self.screw_pitch_mm for i in range(n))
    @property
    def hole_centers_mm(self):
        return tuple((x,z) for x in self.slot_centers_mm for z in self.stations_mm)
    @property
    def tongue_intervals_mm(self):
        guard=self.nominal_tnut_length_mm/2+self.tnut_axial_clearance_mm
        return tuple((a+guard,b-guard) for a,b in zip(self.stations_mm,self.stations_mm[1:]))

    def validate(self):
        if self.extrusion_size_mm not in (20,40): raise ValueError('Only 2020 or 4040')
        if self.channel_count not in (1,2) or (self.extrusion_size_mm==20 and self.channel_count!=1):
            raise ValueError('Invalid parallel slot count')
        if self.selected_4040_slot not in (-1,1): raise ValueError('Invalid selected slot')
        if not 2 <= self.longitudinal_screws_per_slot <=8: raise ValueError('Screws/channel: 2..8')
        if self.screw_pitch_mm <= self.nominal_tnut_length_mm+2*self.tnut_axial_clearance_mm+4:
            raise ValueError('Screw pitch leaves no room for tongue')
        if self.tongue_mode not in ('mouth','slide_in_t_head','none'): raise ValueError('Invalid tongue mode')
        if not 0<self.fit_clearance_mm<.8: raise ValueError('Invalid clearance')
        if not 0<self.tongue_projection_mm<self.slot_lip_depth_mm: raise ValueError('Tongue reaches undercut')
        if self.counterbore_depth_mm >= self.plate_thickness_mm or self.plate_thickness_mm<4:
            raise ValueError('Insufficient screw counterbore floor')
        if self.counterbore_diameter_mm >= 2*self.transverse_edge_margin_mm:
            raise ValueError('Screw head too close to plate edge')
        if self.bridge_width_mm>=self.plate_width_mm: raise ValueError('Bridge too wide')
        return self

def block(x,y,z,dx,dy,dz):
    return cq.Solid.makeBox(dx,dy,dz,cq.Vector(x,y,z))

def slot_outline(s):
    """Photo-derived V5 female cavity; (depth into face, across slot)."""
    return [(0,-s.slot_mouth_mm/2),(s.slot_lip_depth_mm,-s.slot_mouth_mm/2),
        (s.slot_lip_depth_mm,-s.slot_head_width_mm/2),
        (s.slot_head_flat_end_mm,-s.slot_head_width_mm/2),
        (s.slot_depth_mm,-s.slot_inner_flat_mm/2),
        (s.slot_depth_mm,s.slot_inner_flat_mm/2),
        (s.slot_head_flat_end_mm,s.slot_head_width_mm/2),
        (s.slot_lip_depth_mm,s.slot_head_width_mm/2),
        (s.slot_lip_depth_mm,s.slot_mouth_mm/2),(0,s.slot_mouth_mm/2)]

def _offset_profile(s,x,stem=False):
    from shapely.geometry import Polygon,box as polybox
    from shapely.ops import unary_union
    profile=Polygon(slot_outline(s)).buffer(-s.fit_clearance_mm,join_style=2)
    if stem:
        w=(s.slot_mouth_mm-2*s.fit_clearance_mm)/2
        profile=unary_union((profile,polybox(-.15,-w,s.slot_lip_depth_mm+.35,w)))
    if not profile.is_valid or profile.geom_type!='Polygon':
        raise ValueError('Invalid T-head profile')
    return [(x+v,u) for u,v in list(profile.exterior.coords)[:-1]]

def tongue_segment(s,x,z0,z1):
    length=z1-z0
    if length<3: raise ValueError('Tongue too short')
    width=s.slot_mouth_mm-2*s.fit_clearance_mm
    if s.tongue_mode=='mouth':
        return block(x-width/2,-.15,z0,width,s.tongue_projection_mm+.15,length)
    if s.tongue_mode=='slide_in_t_head':
        # Must enter from extrusion end: larger than slot mouth by design.
        return cq.Workplane('XY').polyline(_offset_profile(s,x,True)).close().extrude(length).translate((0,0,z0)).val()
    raise ValueError('Tongue disabled')

def bracket(s):
    s.validate()
    w,l=s.plate_width_mm,s.plate_length_mm
    plate=block(-w/2,-s.plate_thickness_mm,-l/2,w,s.plate_thickness_mm,l)
    if s.corner_radius_mm:
        plate=cq.Workplane(obj=plate).edges('|Y').fillet(s.corner_radius_mm).val()
    bridge=block(-s.bridge_width_mm/2,-s.plate_thickness_mm-s.bridge_reach_mm,
        -s.bridge_height_mm/2,s.bridge_width_mm,s.bridge_reach_mm+1,s.bridge_height_mm)
    pivot=cq.Solid.makeCylinder(s.pivot_outer_radius_mm,s.bridge_height_mm,
        cq.Vector(0,s.pivot_y_mm,-s.bridge_height_mm/2))
    shape=plate.fuse(bridge,pivot).clean()
    for sign in (-1,1):
        x0=sign*(s.bridge_width_mm-s.structural_gusset_width_mm)/2
        outline=[(-s.plate_thickness_mm+.4,-s.bridge_height_mm/2-5),
          (-s.bridge_reach_mm-s.plate_thickness_mm+2,-s.bridge_height_mm/2),
          (-s.bridge_reach_mm-s.plate_thickness_mm+2,s.bridge_height_mm/2),
          (-s.plate_thickness_mm+.4,s.bridge_height_mm/2+5)]
        gus=cq.Workplane('YZ').polyline(outline).close().extrude(s.structural_gusset_width_mm).val()
        shape=shape.fuse(gus.translate((x0-s.structural_gusset_width_mm/2,0,0))).clean()
    if s.tongue_mode!='none':
        for x in s.slot_centers_mm:
            for z0,z1 in s.tongue_intervals_mm:
                shape=shape.fuse(tongue_segment(s,x,z0,z1))
        shape=shape.clean()
    for x,z in s.hole_centers_mm:
        bore=cq.Solid.makeCylinder(s.screw_clearance_diameter_mm/2,s.plate_thickness_mm+2,
             cq.Vector(x,-s.plate_thickness_mm-1,z),cq.Vector(0,1,0))
        cbore=cq.Solid.makeCylinder(s.counterbore_diameter_mm/2,s.counterbore_depth_mm+.01,
             cq.Vector(x,-s.plate_thickness_mm-.005,z),cq.Vector(0,1,0))
        shape=shape.cut(bore).cut(cbore)
    hole=cq.Solid.makeCylinder(s.pivot_hole_diameter_mm/2,s.bridge_height_mm+2,
        cq.Vector(0,s.pivot_y_mm,-s.bridge_height_mm/2-1))
    shape=shape.cut(hole)
    pocket=(cq.Workplane('XY').polygon(6,2*s.captive_nut_across_flats_mm/sqrt(3))
        .extrude(s.captive_nut_depth_mm).val()
        .translate((0,s.pivot_y_mm,-s.bridge_height_mm/2-.01)))
    shape=shape.cut(pocket).clean()
    if not shape.isValid() or len(shape.Solids())!=1:
        raise ValueError('Invalid or disconnected mounting bracket')
    return shape

def reference_extrusion(s,length=None):
    """Schematic 2020/4040 section with exact recovered V5 *face* slot voids."""
    s.validate()
    length=length or max(100.0,s.plate_length_mm+30)
    rail=block(-s.extrusion_size_mm/2,0,-length/2,
               s.extrusion_size_mm,s.extrusion_size_mm,length)
    rows=(0,) if s.extrusion_size_mm==20 else (-10,10)
    for x0 in rows:
        outline=[(x0+v,u) for u,v in slot_outline(s)]
        cut=cq.Workplane('XY').polyline(outline).close().extrude(length+2).val()
        rail=rail.cut(cut.translate((0,0,-length/2-1)))
    core=cq.Solid.makeCylinder(2.25,length+2,cq.Vector(0,s.extrusion_size_mm/2,-length/2-1))
    return rail.cut(core).clean().translate((s.reference_rail_shift_mm,0,0))

def tnut_reference(s):
    """Metal nut envelopes match the V5 undercut; never overlap tongue intervals."""
    result=[]
    for x,z in s.hole_centers_mm:
        shape=(cq.Workplane('XY').polyline(_offset_profile(s,x)).close()
            .extrude(s.nominal_tnut_length_mm)
            .translate((0,0,z-s.nominal_tnut_length_mm/2)).val())
        hole=cq.Solid.makeCylinder(2.5,s.slot_depth_mm+2,cq.Vector(x,-1,z),cq.Vector(0,1,0))
        result.append(shape.cut(hole).clean())
    return result

def screw_reference(s):
    out=[]
    for x,z in s.hole_centers_mm:
        sh=cq.Solid.makeCylinder(2.5,s.plate_thickness_mm+3.5,
               cq.Vector(x,-s.plate_thickness_mm+.5,z),cq.Vector(0,1,0))
        head=cq.Solid.makeCylinder(s.counterbore_diameter_mm/2-.25,2.8,
               cq.Vector(x,-s.plate_thickness_mm,z),cq.Vector(0,1,0))
        out.append(sh.fuse(head).clean())
    return out

def feature_manifest(s):
    return {'parameters':asdict(s),'plate_width_mm':s.plate_width_mm,
       'plate_length_mm':s.plate_length_mm,'slot_centers_mm':s.slot_centers_mm,
       'screw_stations_mm':s.stations_mm,'hole_centers_xz_mm':s.hole_centers_mm,
       'tongue_intervals_z_mm':s.tongue_intervals_mm if s.tongue_mode!='none' else (),
       'screw_count':len(s.hole_centers_mm),
       'assembly_rule':'Remove old V5 loose key; metal M5 T-nuts carry clamp force',
       'installation_rule':'End-slide only for T-head' if s.tongue_mode=='slide_in_t_head' else 'Face install, shallow tongue',
       'physical_fit':'UNVERIFIED'}

PRESETS={
    '2020_single_2xM5':MountSpec(extrusion_size_mm=20,channel_count=1),
    '4040_dual_4xM5':MountSpec(extrusion_size_mm=40,channel_count=2),
    '4040_dual_8xM5':MountSpec(extrusion_size_mm=40,channel_count=2,longitudinal_screws_per_slot=4),
    '4040_single_2xM5':MountSpec(extrusion_size_mm=40,channel_count=1),
}
