# V006 CAD validation scope and acceptance boundaries

This revision passes **13 sampled configurations** of a four-joint camera mount on a nominal photo-derived 4040 extrusion. It does not cover all combinations of joint angles or physical printer operation.

| Verified by the published CAD test | Outcome |
|---|---|
| Positioned assembly/reference entries | 30 |
| Hand-wheel joints | 4: base, elbow, pitch, wrist |
| Sampled joint configurations | 13/13 pass |
| Nominal Ø3.2 mm USB cable versus thumbwheels | Minimum 7.132 mm surface clearance |
| Nominal USB cable versus 4040 reference | Minimum 3.802 mm surface clearance |
| New V006 print meshes | Two watertight single-volume STLs |

**Not yet verified:** actual 4040 slot and metal T-nut compatibility; M5 clamp engagement, fastening torque and vibration; ESP32-CAM-MB exact board, pins, port and connector boot; actual USB cable bend radius, slack, snagging, strain relief, dynamic sag and wear; real printer build plate, belt, nozzle and axis travel; thermal and fatigue behavior.

A physical pass requires filling in [PHYSICAL_FIT_REGISTER_V006.csv](PHYSICAL_FIT_REGISTER_V006.csv), validating all moving-machine clearances, and updating parametric assumptions based on caliper measurements.

[Detailed V006 notes](ENGINEERING_NOTES_V006.md) · [Measured CAD results](validation_v006.json) · [Docs index](README.md).
