#!/usr/bin/env python3
"""V005 actual-BREP CAD previews. Install vtk, pillow; run with xvfb-run on Linux."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import build_v005 as v
import render_assembly as renderer

def annotate(path,title,subtitle):
    image=Image.open(path).convert("RGB")
    draw=ImageDraw.Draw(image)
    font="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    bold="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    draw.rounded_rectangle((27,22,1580,149),radius=16,fill="#102537")
    draw.text((55,42),title,font=ImageFont.truetype(bold,29),fill="white")
    draw.text((55,104),subtitle,font=ImageFont.truetype(font,17),fill="#d4e6f6")
    draw.rounded_rectangle((30,1083,1730,1145),radius=12,fill="#162c3e")
    draw.text((55,1101),"V005  |  LEFT FACE Y=+20  |  HORIZONTAL X RAIL  |  AIMING TOWARD -Y  |  ACTUAL CAD GEOMETRY",
              font=ImageFont.truetype(font,17),fill="white")
    image.save(path)

renderer.annotate=annotate

def main():
    previews=v.ROOT/"previews"
    previews.mkdir(parents=True,exist_ok=True)
    parts=v.components()
    renderer.camera_scene(parts,previews/"v005_left_side_over_rail.png",
        "V005  |  LEFT-SIDE OVER-RAIL ESP32-CAM-MB",
        "Horizontal 4040 | left-side clamp | camera looks inward above rail toward printer bed",
        (250,230,210),(15,49,20))
    renderer.camera_scene(parts,previews/"v005_back_over_rail.png",
        "V005  |  VIEW ALONG THE CAMERA SIGHTLINE",
        "Side mount on Y=+20 | lens ray travels toward -Y above the rail",
        (175,-190,115),(35,45,21))
    renderer.camera_scene(parts,previews/"v005_arm_and_cable.png",
        "V005  |  ARTICULATION AND USB CABLE PATH",
        "Three hand-operated pivots | bottom USB exit | flexible cable reference",
        (180,260,120),(15,90,25),opacity={"4040_horizontal_reference":0})

if __name__ == "__main__":
    main()
