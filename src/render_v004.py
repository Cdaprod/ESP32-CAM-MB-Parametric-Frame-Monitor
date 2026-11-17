#!/usr/bin/env python3
"""Render actual V004 BREP geometry into embedded documentation PNGs."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import render_assembly as renderer
import build_v004 as v

FONTP='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
FONTB='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

def annotate(where,title,subtitle):
    im=Image.open(where).convert('RGB')
    d=ImageDraw.Draw(im)
    d.rounded_rectangle((30,24,1470,145),radius=16,fill=(17,34,49))
    d.text((57,39),title,font=ImageFont.truetype(FONTB,30),fill=(250,251,253))
    d.text((57,101),subtitle,font=ImageFont.truetype(FONTP,17),fill=(197,218,233))
    d.rounded_rectangle((30,1081,1730,1142),radius=12,fill=(20,38,52))
    d.text((53,1099),'V004  ·  0.65 mm KEY RECESS  ·  METAL T-NUT CLAMP  ·  HORIZONTAL 4040  ·  CAD GEOMETRY',font=ImageFont.truetype(FONTP,18),fill=(233,239,246))
    im.save(where)

renderer.annotate=annotate

def main():
    root=v.ROOT/'previews';root.mkdir(exist_ok=True,parents=True)
    comps=v.components()
    renderer.camera_scene(comps,root/'v004_horizontal_assembly.png',
        'V004 ASSEMBLY  |  HORIZONTAL 4040 + CAMERA HOUSING',
        '3 tool-free adjustment knobs · 2 metal M5 T-nuts · bottom USB service loop',
        (190,-170,110),(0,12,-63))
    no_rail={name:0 for name,_,_,_ in comps if name=='4040_horizontal_reference'}
    renderer.camera_scene(comps,root/'v004_knobs_and_cable.png',
        'V004  |  THREE TOOL-FREE JOINTS + CABLE ROUTING',
        'Two 35mm arm links · hand wheels retain hex-head fasteners · cable saddles',
        (170,-150,15),(10,18,-96),opacity=no_rail)
    hide={name:0 for name,_,_,_ in comps if name.startswith(('4040_','M5_','V004_mount_plate','V004_first_arm','V004_second_arm'))}
    renderer.camera_scene(comps,root/'v004_camera_case.png',
        'V004  |  CLOSED-SIDE CAMERA SHELL + REMOVABLE BEZEL',
        'Side walls and top/bottom stops · camera optics and antenna openings',
        (165,-144,-40),(24,22,-122),opacity=hide)
    print('V004 rendered PNGs',[(p.name,p.stat().st_size) for p in root.glob('v004_*.png')])

if __name__=='__main__':main()
