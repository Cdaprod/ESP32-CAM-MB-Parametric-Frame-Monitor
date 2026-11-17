"""Render true CAD geometry rather than a synthetic illustration."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from . import vtk_renderer as renderer
from .assembly import components


def annotate(path,title,subtitle):
    im=Image.open(path).convert('RGB')
    draw=ImageDraw.Draw(im)
    font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    draw.rounded_rectangle((26,22,1720,143),radius=15,fill='#112838')
    draw.text((55,41),title,font=ImageFont.truetype(bold,28),fill='white')
    draw.text((55,103),subtitle,font=ImageFont.truetype(font,16),fill='#e2e9f0')
    draw.rounded_rectangle((26,1084,1730,1147),radius=11,fill='#162b3e')
    draw.text((55,1106),'V008 | HORIZONTAL 4040 | LEFT-SIDE MOUNT | BOTH ARM GUIDES | CAD REFERENCE ONLY',
              font=ImageFont.truetype(font,17),fill='white')
    im.save(path)


def render(root:Path):
    root=Path(root)
    target=root/'previews'
    target.mkdir(parents=True,exist_ok=True)
    renderer.annotate=annotate
    default=components()
    renderer.camera_scene(default,target/'v008_full_assembly.png',
        'V008 | UNIFIED FRAME-MONITOR ASSEMBLY',
        'Both arm guides aligned to the nominal outboard USB cable',
        (245,215,170),(22,65,19))
    renderer.camera_scene(default,target/'v008_cable_guides.png',
        'V008 | FIRST AND SECOND ARM CABLE GUIDES',
        'Both guides now sit on the same 3.2mm cable route, clear of four hand knobs',
        (162,230,124),(18,120,12),opacity={'4040_horizontal_reference':0})
    renderer.camera_scene(components(wrist=20),target/'v008_wrist_20_degrees.png',
        'V008 | INDEPENDENT WRIST YAW +20 DEGREES',
        'Retains the V006 wrist and the corrected two-arm cable guide placement',
        (225,215,165),(20,72,19))
