# V008 — synchronized cable guides and unified CAD build

**Status:** CAD-validated prototype. No physical printer/cable qualification.

## Root cause and change

The V006 USB cable centerline was routed outboard at local X = -27 mm, while both inherited V004 cable management saddles were at X = 0. The nominal cable therefore missed both guide openings. The V007 source candidate addressed the issue without generating a qualified release. V008 places both arm guides using the *same parametric coordinate system as the cable*, and moves active CAD source into one standalone Python package.

## Dimensional constraints

| Parameter | Design value (mm) |
|---|---:|
| Nominal cable diameter | 3.2 |
| Printed guide through-bore diameter | 3.8 |
| Bore-to-cable nominal radial clearance | 0.30 |
| Guide axial length on each arm | 3.5 |
| Guide external square section | 7.6 × 7.6 |
| First guide (local X,Y,Z) | -27, -32, 19 |
| Second guide (local X,Y,Z) | -27, -69.2, 27 |
| Elbow cable transfer lateral offset | +4.0 X |
| 4040 printed key recessed face | 0.65 |

The guide support is part of each arm; no additional loose cable-clip parts are required. The arm pivots, M4 bolt bores and captive nut geometry are retained. The V006 wrist adapter, enclosure and four hand-knob hardware references are unchanged.

## Validation

One active CLI `python src/build.py` builds, validates and renders from `src/frame_monitor/`. The package does **not import the historical versioned build scripts**. It generates the complete STEP assembly, both individual arm STEP/STLs, the assembly manifest, 13-pose report and actual geometry-derived PNG images.

The 13 sampled configurations check four thumbwheel and stationary rail minimum surface distances, plus surface clearance and Boolean overlap against **both new arm-guide bores**. Cable-to-guide gap must lie in **0.24–0.50 mm** and unintended intersection remain below **0.01 mm³**. Both new STL meshes must be watertight, single-volume and within 0.5% of the BREP volume.

Measured modeled results: **13/13 poses passed**, **0.30 mm** cable-to-guide gap for both arms, **7.132 mm** minimum cable-to-knob gap, **3.802 mm** minimum cable-to-rail gap, **2/2 watertight new STLs**.

## Physical qualification remaining

Measure actual USB cable and connector boots, test each guide with a physical cable and printed coupon, inspect guide-web strength and print direction, check dynamic cable bend/strain relief, verify actual 4040 slot and compatible metal M5 T-nuts, test all printer travel and vibration/thermal operation.

V001–V007 original sources, models and preview assets remain for revision provenance. V008 is the canonical current development output after passing CI.
