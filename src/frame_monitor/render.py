"""Render true CAD geometry rather than a synthetic illustration."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from . import vtk_renderer as renderer
from .assembly import components


def annotate(path,title,subtitle):
    im=Image.open(path).convert('RGB')
    draw=ImageDraw.Draw(im)
    font=renderer.font_path(False)
    bold=renderer.font_path(True)
    draw.rounded_rectangle((26,22,1720,143),radius=15,fill='#112838')
    draw.text((55,41),title,font=ImageFont.truetype(bold,28),fill='white')
    draw.text((55,103),subtitle,font=ImageFont.truetype(font,16),fill='#e2e9f0')
    draw.rounded_rectangle((26,1084,1730,1147),radius=11,fill='#162b3e')
    draw.text((55,1106),'V010 | HORIZONTAL 4040 | LEFT-SIDE MOUNT | FOUR COMPACT U-CLIPS | CAD REFERENCE ONLY',
              font=ImageFont.truetype(font,17),fill='white')
    im.save(path)


def render(root:Path):
    root=Path(root)
    target=root/'previews'
    target.mkdir(parents=True,exist_ok=True)
    renderer.annotate=annotate
    default=components()
    renderer.camera_scene(default,target/'v010_full_assembly.png',
        'V010 | UNIFIED FRAME-MONITOR ASSEMBLY',
        'Broad enclosure root, continuous wrist heel and gusseted pitch upright',
        (245,215,170),(22,65,19))
    renderer.camera_scene(default,target/'v010_cable_guides.png',
        'V010 | FOUR COMPACT OPEN U-CLIPS',
        'Alternating cable seats spaced 13 and 14 mm center-to-center',
        (162,230,124),(18,120,12),opacity={'4040_horizontal_reference':0})
    renderer.camera_scene(components(wrist=20),target/'v010_wrist_20_degrees.png',
        'V010 | INDEPENDENT WRIST YAW +20 DEGREES',
        'Wrist yaw preserved; cable follows the moving arm clips',
        (225,215,165),(20,72,19))

    # Isolated geometry-derived previews, not synthetic reference illustrations.
    from .geometry import first_arm,second_arm
    from . import parts as cad_parts,wrist as current_wrist
    from .primitives import cyl_y
    from .config import CONFIG as C
    arm1=first_arm()
    arm2=second_arm()
    c1=cyl_y(C.cable_diameter_mm/2,27,C.first_cable_x_mm,-47,C.first_cable_z_mm)
    c2=cyl_y(C.cable_diameter_mm/2,27,C.second_cable_x_mm,-82,C.second_cable_z_mm)
    renderer.camera_scene([('V010_first_arm',arm1,(.96,.51,.17),'printed'),
      ('USB_cable_reference',c1,(.07,.15,.24),'reference')],
      target/'v010_first_arm_isolated.png','V010 | FIRST ARM + U-CLIPS',
      'No long guide outriggers; cable beside moving arm',
      (78,-85,78),(-4,-34,15))
    renderer.camera_scene([('V010_second_arm',arm2,(.91,.54,.21),'printed'),
      ('USB_cable_reference',c2,(.07,.15,.24),'reference')],
      target/'v010_second_arm_isolated.png','V010 | SECOND ARM + U-CLIPS',
      'Maintains camera pitch axis; compact alternating retainers',
      (78,-115,78),(-4,-72,18))
    renderer.camera_scene([('V010_scalloped_thumbwheel',cad_parts.thumbwheel(),(.91,.65,.17),'printed')],
      target/'v010_thumbwheel.png','V010 | SCALLOPED HAND KNOB',
      'Original M4 captured nut and pivot datum retained',
      (45,-55,46),(0,0,3.5))
    renderer.camera_scene([('V010_relieved_camera_shell',current_wrist.shell(),(.13,.49,.61),'printed')],
      target/'v010_camera_shell.png','V010 | RELIEVED CAMERA SHELL',
      '14 mm leaf, deep rear-wall buttress and R1.5 root blend',
      (85,-190,90),(0,-105,25))
    renderer.camera_scene([('arm_1',arm1,(.95,.49,.19),'printed'),
      ('arm_2',arm2.translate((45,36,0)),(.91,.55,.24),'printed')],
      target/'v010_arm_pair.png','V010 | BOTH REVISED ARMS',
      'Rounded slots, continuous spine and four compact U-clips',
      (100,-115,80),(22,-48,13))

    # One inspection sheet follows the entire load path, with actual solids.
    import tempfile
    with tempfile.TemporaryDirectory() as temporary:
        panels=[('HOUSING ROOT',current_wrist.shell(),(85,-190,85),(4,-119,25)),
                ('WRIST HEEL',current_wrist.adapter(),(80,-170,55),(7,-111,-10)),
                ('PITCH UPRIGHT',arm2,(78,-115,78),(-4,-72,5)),
                ('EXTRUSION ROOT',cad_parts.reinforced_base_plate(),(65,-85,55),(0,-10,0))]
        sheet=Image.new('RGB',(1760,1180),'white')
        for i,(title,shape,eye,look) in enumerate(panels):
            path=Path(temporary)/f'{i}.png'
            renderer.camera_scene([(title,shape,(.91,.49,.2),'printed')],path,
                'V010 | '+title,'Solid load-path reinforcement; physical load testing required',eye,look)
            with Image.open(path) as panel:
                sheet.paste(panel.resize((880,590)),((i%2)*880,(i//2)*590))
        sheet.save(target/'v010_load_path.png')
