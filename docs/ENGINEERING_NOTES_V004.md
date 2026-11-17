# V004 engineering change register — horizontal-frame camera monitor

**Status:** CAD-geometrically accepted, not physically qualified. **Supersedes:** V003 for the horizontal front-rail example. V001–V003 remain preserved.

| ID | User observation | V004 implemented geometry | CAD check | Physical acceptance needed |
|---|---|---|---|---|
| R01 | Tongue bottoming prevents clamp | Printed alignment key + metal T-nuts terminate **0.65 mm behind** the extrusion face; mounting plate back remains on nominal face | `key_recess_mm=0.65`; rail/key/plate interference zero | Validate face datum and physical 4040 fit; torque / anti-slide shake test |
| R02 | Previous mounting rail vertical | Entire 4040 profile and mount transformed so its 180 mm longitudinal axis is **horizontal**, global X | Assembly STEP orientation checked; no rail/plate interference | Confirm target front leg actually has modeled dual-slot 4040 face |
| R03 | Few angles, needs wrench | Two 35 mm articulated links; three M4 knobs, bolt-head hex pockets and captive nut traps | 27 geometric poses accepted: first joint -25..25°, elbow -30..30°, camera tilt 0..30° | Check joint friction and physical lock holding force; no negative pitch guarantee |
| R04 | Cradle exposes one side | Four-wall camera enclosure with integral left/right/top/bottom/rear, plus four-screw front bezel | Nominal envelope no intersection; all six axial escape directions blocked in modeled motion tests | Confirm real ESP32-CAM-MB width/depth, lens, header, antenna and USB connector |
| R05 | USB cable should route down arm | Bottom-centered cable opening, routed reference cable and two integrated cable saddles along arm | Cable reference included in assembly; camera enclosure retains bottom ledges outside USB slot | Confirm actual connector orientation, strain relief, flex, bend radius and thermal clearance |

## Fastening and interface details

- 4040 reference slot cavities are photo-derived, **two slots per face at ±10 mm**. Original source preserved in `reference/`.
- Mounting adapter: 2 × M5 nominal 8 mm socket bolts, fastener centers along horizontal rail ±15 mm; nut profile is geometry-only illustration of matching metal slider/T-nut. **Use actual metal 4040-compatible sliding T-nuts** with verified load capacity.
- Alignment key: 11 mm long at rail midspan, surface entirely recessed by 0.65 mm; it is **not tapped or load-bearing**. Metal T-nuts are modeled as 9 mm long each, non-overlapping the key.
- Hand knobs: three identical 12-sided 23 mm nominal diameter printable wheels with metal hex-head bolt captured in top pocket. Captive M4 hex nuts in the receiving parts allow tool-free adjustment after assembly. Verify actual screw lengths/nut traps and washers before use.
- Camera bezel: four M2.5 nominal screws; optical port Ø12.8 mm, top antenna viewing slot 22 × 6 mm, bottom USB slot 11 × 14 mm (nominal path, not connector-certified).
- Shell: 36 mm outer width, 24 mm depth, 51 mm height; 3 mm side/rear walls, 4 mm top/bottom. Internal volume sized for **provisional** 27 × 40 × 17 mm envelope.
- Parametric example angles: yaw +18°, elbow -15°, pitch +12°. Positive pitch angles tested 0 to 30°; negative pitch causes a known housing/support clash and is **outside accepted range**.

## Important unfinished fit/strength requirements

1. The screw-to-nut interface uses nominal, threadless solid envelopes; it **does not prove proper M5 engagement** or nut retention under torque.
2. Key clearance must be measured on your actual extrusion. The nominal 0.65 mm face recess is deliberate; larger face offsets may be unsafe, and no compression fit has been tested.
3. The three-position arms may move under sustained printer vibration unless a real friction washer/locking interface is used. V004 depicts the fastening concept, not a measured torque specification.
4. The case includes a routed reference cable. Its smooth geometry illustrates intended layout, not a tested electrical connector, cable gauge or bend radius.
5. Print in appropriate orientation, avoid unsupported internal bridges, and confirm toolhead, bed, wiring and power-supply clearance at full printer travel.

## Reproduce and verify

```bash
python -m pip install cadquery shapely trimesh numpy matplotlib vtk pillow
python src/build_v004.py
python src/validate_v004.py
xvfb-run -a python src/render_v004.py  # Linux, for screenshots
```

See `docs/validation_v004.json` for programmatic results and `docs/manifest_v004.json` for the exact parameter/specification register.
