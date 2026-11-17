#!/usr/bin/env python3
"""VTK renders from the exact V006 positioned CadQuery solids, not synthetic art."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import build_v006 as v
import render_assembly as renderer

def annotate(path,title,subtitle):
    im=Image.open(path).convert('RGB')
    draw=ImageDraw.Draw(im)
    font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    draw.rounded_rectangle((28,22,1720,143),radius=15,fill='#112838')
    draw.text((55,42),title,font=ImageFont.truetype(bold,29),fill='white')
    draw.text((55,105),subtitle,font=ImageFont.truetype(font,17),fill='#dce9ef')
    draw.rounded_rectangle((30,1083,1730,1145),radius=11,fill='#182e41')
    draw.text((55,1103),'V006 | 4040 LEFT-SIDE OVER-RAIL | FOUR HAND-ADJUSTABLE JOINTS | REFERENCE 3.2mm USB CABLE',
              font=ImageFont.truetype(font,17),fill='#f1f5f9')
    im.save(path)

renderer.annotate=annotate

def render():
    target=v.ROOT/'previews'
    target.mkdir(parents=True,exist_ok=True)
    parts=v.components()
    renderer.camera_scene(parts,target/'v006_wrist_full_assembly.png',
        'V006 | EXTRA CAMERA WRIST PIVOT',
        'Horizontal left-side 4040 mount / four hand knobs / bottom USB outlet',
        (245,215,170),(22,65,19))
    renderer.camera_scene(parts,target/'v006_wrist_and_cable_detail.png',
        'V006 | WRIST AND USB CABLE CLEARANCE',
        'Flexible cable runs behind the shell then outside the hand-knob sweep',
        (162,230,124),(18,120,12),
        opacity={'4040_horizontal_reference':0})
    rotated=v.components(wrist=20)
    renderer.camera_scene(rotated,target/'v006_wrist_rotated_20deg.png',
        'V006 | INDEPENDENT WRIST YAW +20 DEGREES',
        'Wrist re-aiming leaves shoulder, elbow and pitch adjustment unchanged',
        (225,215,165),(20,72,19))
    print('Generated three actual CAD-derived V006 PNGs')

if __name__=='__main__':render()
